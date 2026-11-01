from datetime import datetime

import pytest
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.amdx import Role, XSubtype
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
def cockpit(tmp_path):
    connection = open_application_database(tmp_path / "decision-dock.db")
    window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
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
    yield window, shell, connection
    dispose(window)
    connection.close()


def command_count(connection):
    return connection.execute("SELECT COUNT(*) FROM amdx_catalog_command").fetchone()[0]


def enter_watch(shell):
    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    shell._update_view()
    QApplication.processEvents()
    assert shell.runtime.current_mode.id == "live-watch"


def test_reference_is_watch_only_and_truthful_about_missing_published_definition(cockpit):
    _window, shell, _connection = cockpit
    assert shell.plan_reference_frame.isHidden()
    enter_watch(shell)
    assert shell.plan_reference_frame.isVisible()

    QTest.mouseClick(shell.plan_reference_button, Qt.MouseButton.LeftButton)
    dock = shell.amdx_decision_dock
    assert dock.isVisible()
    assert "Alpha 0.7" in dock.provenance_label.text()
    assert "No published AMDX definition" in dock.reference_label.text()
    assert dock.target_label.text() == shell.runtime.amdx_context_widget.target_label.text()
    assert dock.projection.token == shell.runtime.amdx_context_widget.decision_projection().token
    dock.hide()  # outside-click popup dismissal follows the same return path
    QApplication.processEvents()
    assert shell.plan_reference_button.hasFocus()


def test_single_key_shortcut_does_not_steal_text_entry(cockpit):
    _window, shell, _connection = cockpit
    enter_watch(shell)
    field = shell.runtime.live_watch_widget.observation_input
    field.setFocus()
    QApplication.processEvents()
    QTest.keyClick(field, Qt.Key.Key_P)
    QApplication.processEvents()
    assert field.text() == "p"
    assert not shell.amdx_decision_dock.isVisible()


def test_dock_uses_same_command_updates_main_projection_and_returns_focus(cockpit):
    _window, shell, connection = cockpit
    enter_watch(shell)
    pane = shell.runtime.amdx_context_widget
    pane.select_quarter(1, 3)
    before = command_count(connection)

    shell.amdx_decision_dock.open_for(shell.plan_reference_button)
    QApplication.processEvents()
    dock = shell.amdx_decision_dock
    assert dock.x_buttons[XSubtype.REVERSAL].isVisible()
    QTest.mouseClick(dock.x_buttons[XSubtype.REVERSAL], Qt.MouseButton.LeftButton)
    QApplication.processEvents()

    assert not dock.isVisible()
    assert shell.plan_reference_button.hasFocus()
    assert command_count(connection) == before + 1
    assert "X(R)" in pane.table.item(1, 3).text()
    assert pane.table.item(1, 4).text() == "AMDX"


def test_illegal_or_changed_projection_cannot_record(cockpit):
    _window, shell, connection = cockpit
    enter_watch(shell)
    pane = shell.runtime.amdx_context_widget
    projection = pane.decision_projection()
    before = command_count(connection)

    assert projection.quarter_position == 3
    assert Role.A not in projection.legal_roles
    assert pane.choose_decision(projection.token, Role.A) is False
    assert command_count(connection) == before

    pane.select_quarter(1, 3)
    assert pane.choose_decision(projection.token, Role.D) is False
    assert "target changed" in pane.status_label.text()
    assert command_count(connection) == before


def test_failed_or_mode_changed_support_stays_truthful_and_never_replays(cockpit):
    _window, shell, connection = cockpit
    enter_watch(shell)
    pane = shell.runtime.amdx_context_widget
    dock = shell.amdx_decision_dock
    dock.open_for(shell.plan_reference_button)
    before = command_count(connection)

    pane._read_error = True
    pane.status_label.setText("Shared context unavailable · synthetic read failure · use Reload AMDX")
    pane._render()
    QApplication.processEvents()
    QTest.mouseClick(dock.role_buttons[Role.D], Qt.MouseButton.LeftButton)
    assert dock.isVisible()
    assert "unavailable" in dock.status_label.text().lower()
    assert command_count(connection) == before

    pane._read_error = False
    assert shell.runtime.apply_transition("live-return-analysis")
    shell._update_view()
    QApplication.processEvents()
    assert not dock.isVisible()
    assert shell.plan_reference_frame.isHidden()
    assert command_count(connection) == before


def test_display_profile_is_constrained_and_remembered_per_workspace(cockpit):
    _window, shell, connection = cockpit
    dock = shell.amdx_decision_dock
    dock.set_display_profile("tv-below")
    assert dock.display_profile == "tv-below"
    with pytest.raises(ValueError):
        dock.set_display_profile("floating-anywhere")

    restored = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    try:
        restored_shell = restored.trade_plan_widget.trading_day_shell_widget
        assert restored_shell.amdx_decision_dock.display_profile == "tv-below"
    finally:
        dispose(restored)
