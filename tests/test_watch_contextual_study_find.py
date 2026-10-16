from datetime import datetime
from pathlib import Path

import pytest
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


REFERENCE = datetime(2026, 10, 9, 9, 15, tzinfo=MARKET_TIMEZONE)


def dispose(window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    QApplication.processEvents()


@pytest.fixture
def cockpit(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    connection = open_application_database(tmp_path / "contextual-study-find.db")
    repository = StudyFindRepository(connection)
    window = MainWindow(TDARepository(connection), repository)
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    shell = window.trade_plan_widget.trading_day_shell_widget
    shell.run_environment = RunEnvironment.REPLAY
    shell.run_market_timestamp = REFERENCE
    assert shell.start_trading_run(), shell.summary_label.text()
    window.trade_plan_widget.focus_runtime()
    window.resize(1344, 756)
    window.show()
    QApplication.processEvents()
    yield window, shell, repository, connection
    dispose(window)
    connection.close()


def enter_watch(shell):
    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    shell._update_view()
    QApplication.processEvents()
    assert shell.runtime.current_mode.id == "live-watch"


def open_capture(shell):
    QTest.mouseClick(shell.study_find_button, Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    return shell.window().contextual_study_find_dock


def test_contextual_launcher_is_watch_only_and_seeds_supported_empty_fields(cockpit):
    window, shell, _repository, _connection = cockpit
    assert shell.study_find_button.isHidden()
    enter_watch(shell)
    assert shell.study_find_button.isVisible()

    dock = open_capture(shell)
    source = window.study_find_widget
    assert dock.isVisible()
    assert "2026-10-09 · MNQ · NYAM" in dock.persisted_basis_label.text()
    assert "Current Watch context only" in dock.context_only_label.text()
    assert "Working AMDX · NYAM 90m Q3" in dock.context_only_label.text()
    assert "not stored" in dock.context_only_label.text()
    assert source.date_input.date().toString("yyyy-MM-dd") == "2026-10-09"
    assert source.instrument_input.text() == "MNQ"
    assert source.session_input.text() == "NYAM"


def test_contextual_fields_are_the_existing_draft_and_dismissal_flushes(cockpit):
    window, shell, repository, _connection = cockpit
    enter_watch(shell)
    dock = open_capture(shell)
    draft_id = window.study_find_widget.current_study_find_id

    dock.pattern_input.setText("London high raid")
    dock.observation_input.setPlainText("Displacement followed the raid")
    dock.notes_input.setPlainText("Review the first FVG")
    dock.dismiss()
    QApplication.processEvents()

    saved = repository.get_latest_draft()
    assert saved is not None
    assert saved.id == draft_id
    assert saved.pattern_name == "London high raid"
    assert saved.observation == "Displacement followed the raid"
    assert window.study_find_widget.notes_input.toPlainText() == "Review the first FVG"
    assert shell.study_find_button.hasFocus()

    dock = open_capture(shell)
    assert "Resumed existing draft" in dock.draft_label.text()
    assert dock.observation_input.toPlainText() == "Displacement followed the raid"


def test_existing_draft_is_not_overwritten_by_current_watch_defaults(cockpit):
    window, shell, _repository, _connection = cockpit
    source = window.study_find_widget
    source.instrument_input.setText("NQ")
    source.session_input.setText("London")
    source.pattern_input.setText("Existing investigation")
    source.observation_input.setPlainText("Started before Watch")
    draft_id = source.current_study_find_id

    enter_watch(shell)
    dock = open_capture(shell)

    assert source.current_study_find_id == draft_id
    assert source.instrument_input.text() == "NQ"
    assert source.session_input.text() == "London"
    assert dock.pattern_input.text() == "Existing investigation"
    assert "current Watch defaults were not substituted" in dock.draft_label.text()


def test_clipboard_image_and_save_use_existing_repository_then_return(cockpit):
    window, shell, repository, connection = cockpit
    enter_watch(shell)
    before_mode = shell.runtime.current_mode.id
    before_run = shell.active_trading_run.id
    before_amdx = shell.runtime.amdx_context_widget.decision_projection().token
    before_commands = connection.execute(
        "SELECT COUNT(*) FROM amdx_catalog_command"
    ).fetchone()[0]
    dock = open_capture(shell)
    study_find_id = window.study_find_widget.current_study_find_id

    dock.pattern_input.setText("London high raid")
    dock.observation_input.setPlainText("Displacement arrived after the raid")
    image = QImage(36, 24, QImage.Format.Format_RGB32)
    image.fill(0x336699)
    QApplication.clipboard().setImage(image)
    assert dock.paste_chart()
    assert "1 managed chart image attached" == dock.attachment_label.text()

    assert dock.save_and_return()
    QApplication.processEvents()

    saved = repository.get_by_id(study_find_id)
    images = repository.get_images(study_find_id)
    assert saved is not None
    assert saved.observation == "Displacement arrived after the raid"
    assert len(images) == 1
    assert Path(images[0]).exists()
    assert repository.get_latest_draft() is None
    assert not dock.isVisible()
    assert shell.study_find_button.hasFocus()
    assert shell.runtime.current_mode.id == before_mode
    assert shell.active_trading_run.id == before_run
    assert shell.runtime.amdx_context_widget.decision_projection().token == before_amdx
    assert connection.execute(
        "SELECT COUNT(*) FROM amdx_catalog_command"
    ).fetchone()[0] == before_commands


def test_invalid_save_stays_open_and_leaving_watch_preserves_draft(cockpit):
    window, shell, repository, _connection = cockpit
    enter_watch(shell)
    dock = open_capture(shell)

    assert not dock.save_and_return()
    assert dock.isVisible()
    assert dock.status_label.text() == "Pattern is required before saving."
    dock.pattern_input.setText("Partial pattern")
    dock.observation_input.setPlainText("Unfinished observation")

    assert shell.runtime.apply_transition("live-return-analysis")
    shell._update_view()
    QApplication.processEvents()

    assert not dock.isVisible()
    saved = repository.get_latest_draft()
    assert saved is not None
    assert saved.id == window.study_find_widget.current_study_find_id
    assert saved.pattern_name == "Partial pattern"
    assert saved.observation == "Unfinished observation"
