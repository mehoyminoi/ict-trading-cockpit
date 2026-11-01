import json
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QTimer
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from ict_cockpit.existing_workspace import open_existing_workspace
from ict_cockpit.main import open_window
from ict_cockpit.media.workspace_paths import resolve_study_image
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from datetime import datetime
from tools.study_criterion_demo import open_demo


def close(connection, window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    QApplication.processEvents()
    connection.close()


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path / 'original-xdg'))
    root = tmp_path / 'Study with spaces'
    connection, window = open_demo(root)
    (root / 'xdg').mkdir(exist_ok=True)
    window._open_investigation_capture()
    capture = window.study_find_widget
    capture.pattern_input.setText('Retained example')
    capture.observation_input.setPlainText('Retain meaningful historical observation')
    image = root / 'xdg/chart.png'
    picture = QImage(16, 16, QImage.Format.Format_RGB32)
    picture.fill(0x446688)
    assert picture.save(str(image))
    capture.image_paths.append(str(image))
    assert capture.submit()
    window.resize(600, 500)
    close(connection, window)
    return root


def rows(root):
    with closing(sqlite3.connect(root / 'demo.db')) as c:
        return {name: c.execute(f'SELECT * FROM {name} ORDER BY 1').fetchall() for name in (
            'study_find', 'study_find_image', 'study_task_registry', 'study_investigation_capture',
            'study_review', 'amdx_definition_revision')}


def test_idle_launch_retains_material_geometry_and_does_not_seed_or_start(workspace):
    before = rows(workspace)
    marker = (workspace / 'study-criterion-v0.txt').read_bytes()
    for _ in range(2):
        connection, window = open_window(workspace)
        try:
            assert Path(connection.execute('PRAGMA database_list').fetchone()[2]) == workspace / 'demo.db'
            assert window.tabs.currentWidget() is window.study_home_widget
            assert window.trade_plan_widget.trading_day_shell_widget.active_trading_run is None
            assert connection.execute('SELECT count(*) FROM trading_session_run').fetchone()[0] == 0
            assert window.workspace_settings.fileName() == str(workspace / 'demo.db.workspace.ini')
            assert window.width() == 600 and window.height() == 500
            assert str(workspace) in window.windowTitle() and 'retained trial' in window.windowTitle()
            assert not QImage(resolve_study_image(str(workspace / 'xdg/chart.png'))).isNull()
            assert rows(workspace) == before
        finally:
            close(connection, window)
    assert (workspace / 'study-criterion-v0.txt').read_bytes() == marker


def test_active_replay_restores_existing_identity_without_calendar_override(workspace):
    connection, window = open_window(workspace)
    shell = window.trade_plan_widget.trading_day_shell_widget
    shell.run_environment = RunEnvironment.REPLAY
    shell.run_market_timestamp = datetime(2026, 10, 9, 9, 15, tzinfo=MARKET_TIMEZONE)
    assert shell.start_trading_run()
    run_id = shell.active_trading_run.id
    process_id = shell.runtime.session.id
    before = rows(workspace)
    close(connection, window)
    connection, window = open_window(workspace)
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        assert window.tabs.currentWidget() is window.trade_plan_widget
        assert shell.active_trading_run.id == run_id
        assert shell.runtime.session.id == process_id
        assert shell.active_trading_run.environment is RunEnvironment.REPLAY
        assert connection.execute('SELECT count(*) FROM trading_session_run').fetchone()[0] == 1
        window.tabs.setCurrentWidget(window.amdx_catalog_widget)
        window.tabs.setCurrentWidget(window.trade_plan_widget)
        assert shell.active_trading_run.id == run_id
        assert rows(workspace) == before
    finally:
        close(connection, window)


@pytest.mark.parametrize('problem', ['missing-db','missing-settings','missing-media','marker','manifest','old-schema','future-schema','tables','symlink-db'])
def test_invalid_workspace_refused_without_replacement_or_environment_change(workspace, monkeypatch, problem):
    if problem == 'missing-db': (workspace / 'demo.db').unlink()
    elif problem == 'missing-settings': (workspace / 'demo.db.workspace.ini').unlink()
    elif problem == 'missing-media': (workspace / 'xdg').rename(workspace / 'saved-media')
    elif problem == 'marker': (workspace / 'study-criterion-v0.txt').write_text('Other workspace')
    elif problem == 'manifest': (workspace / 'study-workspace-origin.json').write_text('{bad')
    elif problem in ('old-schema','future-schema','tables'):
        with closing(sqlite3.connect(workspace / 'demo.db')) as c:
            if problem == 'tables': c.execute('DROP TABLE study_review')
            else: c.execute('PRAGMA user_version='+('52' if problem=='old-schema' else '999'))
    else:
        (workspace / 'demo.db').rename(workspace / 'original.db')
        (workspace / 'demo.db').symlink_to(workspace / 'original.db')
    before={p.relative_to(workspace):p.read_bytes() for p in workspace.rglob('*') if p.is_file()}
    monkeypatch.setenv('XDG_DATA_HOME','/unchanged-for-rejected-launch')
    with pytest.raises((ValueError, sqlite3.Error)):
        open_existing_workspace(workspace)
    assert os.environ['XDG_DATA_HOME']=='/unchanged-for-rejected-launch'
    assert {p.relative_to(workspace):p.read_bytes() for p in workspace.rglob('*') if p.is_file()}==before


def test_missing_directory_and_cli_argument_do_not_create_workspace(tmp_path):
    target=tmp_path/'not-created'
    with pytest.raises(ValueError,match='does not exist'): open_existing_workspace(target)
    tool=Path(__file__).parents[1]/'tools/open_cockpit.py'
    for args in ([],['--workspace',str(target)]):
        result=subprocess.run([sys.executable,str(tool),*args],capture_output=True,text=True)
        assert result.returncode != 0
        assert 'workspace' in result.stderr.lower()
        assert not target.exists()


@pytest.mark.parametrize('version', [1, 2])
def test_restored_manifest_media_works_without_original_location(workspace, version):
    import shutil
    copy = workspace.parent / 'recovery'
    shutil.copytree(workspace, copy)
    manifest = {'version':version, 'original_root':str(workspace)}
    if version == 2:
        manifest['reference_roots']=[str(workspace), '/prior-study-location']
        manifest['previous_manifest']={'version':1,'original_root':'/prior-study-location'}
    (copy / 'study-workspace-origin.json').write_text(json.dumps(manifest))
    manifest_bytes=(copy / 'study-workspace-origin.json').read_bytes()
    before=rows(copy)
    workspace.rename(workspace.parent / 'retained-original')
    connection, window=open_window(copy)
    try:
        assert rows(copy)==before
        mapped=resolve_study_image(str(workspace / 'xdg/chart.png'))
        assert mapped==str(copy / 'xdg/chart.png')
        assert not QImage(mapped).isNull()
        assert (copy / 'study-workspace-origin.json').read_bytes()==manifest_bytes
    finally:
        close(connection, window)


def test_default_entry_remains_separate_and_keeps_study_first(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME',str(tmp_path / 'default-data'))
    connection, window=open_window()
    try:
        assert Path(connection.execute('PRAGMA database_list').fetchone()[2]) == tmp_path / 'default-data/ict-trading-cockpit/ict_cockpit.db'
        assert window.tabs.currentWidget() is window.study_home_widget
        assert window.trade_plan_widget.trading_day_shell_widget.active_trading_run is None
    finally:
        close(connection, window)
