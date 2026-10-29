"""Direct merged-main compatibility, including rollback at the final format barrier."""
from io import BytesIO
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tarfile

import pytest
from PySide6.QtCore import QTimer

from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow

MAIN = '6dd43c845940874000f46371965441dec262e77a'
ROOT = Path(__file__).resolve().parents[1]


def schema_rows(connection):
    return connection.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name').fetchall()


def dispose(window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()


@pytest.mark.parametrize('late_failure', [False, True])
def test_actual_main_v41_restores_legacy_review_and_final_migration_failure_rolls_back(tmp_path, late_failure):
    archived = tmp_path / 'actual-main'
    archived.mkdir()
    with tarfile.open(fileobj=BytesIO(subprocess.check_output(['git', 'archive', MAIN], cwd=ROOT))) as tar:
        tar.extractall(archived, filter='data')
    directory = tmp_path / 'retained-main'
    script = '''
import json,sys
from pathlib import Path
sys.path[:0]=[sys.argv[1]+'/src',sys.argv[1]+'/tools']
from PySide6.QtCore import QTimer,Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from amdx_entry_demo import open_demo
from ict_cockpit.analysis.amdx import Anchor,Role,intraday_cycles
app=QApplication([])
c,window=open_demo(Path(sys.argv[2]),review=True,date_case=True)
for timer in window.findChildren(QTimer):timer.stop()
shell=window.trade_plan_widget.trading_day_shell_widget
run=shell.active_trading_run
pane=shell.runtime.amdx_context_widget
reference=pane.reference
cycle=intraday_cycles(reference)[1]
quarter=cycle.quarters[2]
pane.repository.revise_working(claim_id='main-working',run_id=run.id,branch_id='working',channel='Expected',
    cycle=cycle,quarter_id=quarter.id,anchor=Anchor('main-anchor',quarter.id,Role.D,'synthetic main chart'),
    recorded_at=reference,market_reference=reference,expected_head_id=None)
pane.select_quarter(1,2)
QTest.mouseClick(pane.phase_buttons[Role.M],Qt.MouseButton.LeftButton)
assert pane.table.item(1,4).text()=='XAMD',pane.status_label.text()
run.qt_context={'year':'D','month':'A'}
run.review_observed_qt_context={'year':'M'}
run.review_takeaway='Preserved synthetic main review'
window.save_trading_session_run(run)
assert c.execute('PRAGMA user_version').fetchone()[0]==41
metadata=dict(run_id=run.id,reference=reference.isoformat(),history=pane.repository.get_history(run.id).to_payload(),
    review=pane.repository.review.get_history(run.id).to_payload())
window.close();window.deleteLater();c.close()
print(json.dumps(metadata))
'''
    written = subprocess.run([sys.executable, '-c', script, str(archived), str(directory)],
        cwd=archived, text=True, capture_output=True, check=True)
    metadata = json.loads(written.stdout)
    database = directory / 'demo.db'
    backup = tmp_path / 'original-main-v41.db'
    shutil.copyfile(database, backup)
    backup_bytes = backup.read_bytes()
    connection = create_connection(database)
    names = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    before = {name: connection.execute('SELECT * FROM '+name).fetchall() for name in names}
    original_schema = schema_rows(connection)
    original_run = connection.execute('SELECT * FROM trading_session_run WHERE id=?', (metadata['run_id'],)).fetchone()
    if late_failure:
        connection.set_authorizer(lambda action,a,b,*_: sqlite3.SQLITE_DENY
            if action==sqlite3.SQLITE_PRAGMA and a=='user_version' and b=='50' else sqlite3.SQLITE_OK)
        with pytest.raises(sqlite3.DatabaseError):
            initialize_schema(connection)
        connection.set_authorizer(None)
        assert connection.execute('PRAGMA user_version').fetchone()[0] == 41
        assert schema_rows(connection) == original_schema
        assert {name: connection.execute('SELECT * FROM '+name).fetchall() for name in names} == before
    initialize_schema(connection)
    assert connection.execute('PRAGMA user_version').fetchone()[0] == 50
    assert {name: connection.execute('SELECT * FROM '+name).fetchall() for name in names} == before
    for table in ('amdx_catalog','amdx_catalog_command','amdx_master_binding','amdx_run_binding',
                  'amdx_run_capture','amdx_run_calendar_command','amdx_run_observed_command'):
        assert not connection.execute('SELECT * FROM '+table).fetchall()
    owner = AMDXRepository(connection)
    assert owner.get_history(metadata['run_id']).to_payload() == metadata['history']
    assert owner.review.get_history(metadata['run_id']).to_payload() == metadata['review']
    with pytest.raises(ValueError, match='legacy ownership is unknown'):
        owner.run_calendar.get_binding(metadata['run_id'])
    previous = {}
    exec(compile((archived/'src/ict_cockpit/database/schema.py').read_text(), 'actual-main-schema', 'exec'), previous)
    with pytest.raises(RuntimeError, match='Unsupported database schema version: 50'):
        previous['initialize_schema'](connection)
    for _ in range(2):
        window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
        try:
            for timer in window.findChildren(QTimer):
                timer.stop()
            shell = window.trade_plan_widget.trading_day_shell_widget
            pane = shell.runtime.amdx_context_widget
            assert shell.active_trading_run.id == metadata['run_id']
            assert shell.runtime.current_mode.id == 'post-market'
            assert pane.reference.isoformat() == metadata['reference']
            assert pane.binding is None
            assert pane.review_stack_button.isHidden()
            assert pane.table.item(1,4).text() == 'XAMD'
            assert shell.active_trading_run.review_takeaway == 'Preserved synthetic main review'
            assert owner.get_history(metadata['run_id']).to_payload() == metadata['history']
            assert owner.review.get_history(metadata['run_id']).to_payload() == metadata['review']
            assert connection.execute('SELECT * FROM trading_session_run WHERE id=?', (metadata['run_id'],)).fetchone() == original_run
            assert not connection.execute('SELECT * FROM amdx_run_binding').fetchall()
            assert not connection.execute('SELECT * FROM amdx_catalog_command').fetchall()
        finally:
            dispose(window)
        connection.close()
        connection = create_connection(database)
        owner = AMDXRepository(connection)
    assert not connection.execute('PRAGMA foreign_key_check').fetchall()
    connection.close()
    assert backup.read_bytes() == backup_bytes
