from datetime import datetime

import pytest
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.amdx import Role, XSubtype
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_session_run import (
    RunEnvironment,
    default_purpose_for_environment,
)
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
    connection = open_application_database(tmp_path / "quiet-watch.db")
    window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    shell = window.trade_plan_widget.trading_day_shell_widget
    shell.run_environment = RunEnvironment.REPLAY
    shell.run_purpose = default_purpose_for_environment(shell.run_environment)
    shell.run_market_timestamp = REFERENCE
    assert shell.start_trading_run(), shell.summary_label.text()
    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    shell._update_view()
    window.trade_plan_widget.focus_runtime()
    window.resize(1344, 756)
    window.show()
    QApplication.processEvents()
    yield window, shell, connection
    dispose(window)
    connection.close()


def command_count(connection):
    return connection.execute(
        "SELECT COUNT(*) FROM amdx_catalog_command"
    ).fetchone()[0]


def test_watch_uses_four_region_composition_and_hides_full_editor(cockpit):
    _window, shell, _connection = cockpit
    composition = shell.runtime.watch_quiet_composition

    assert shell.runtime.mode_stack.currentWidget() is composition
    assert composition.orientation.isVisible()
    assert composition.operating_scroll.isVisible()
    assert composition.amdx_now.isVisible()
    assert composition.safety.isVisible()
    assert shell.runtime.amdx_context_widget.isHidden()
    assert "Watch · NYAM" in composition.orientation.position_label.text()
    assert "09:15 ET" in composition.orientation.market_time_label.text()
    assert "P&L intentionally absent" == composition.safety.no_pnl_label.text()


def test_amdx_now_invokes_same_immediate_command_and_updates_source(cockpit):
    _window, shell, connection = cockpit
    composition = shell.runtime.watch_quiet_composition
    source = shell.runtime.amdx_context_widget
    before = command_count(connection)

    assert composition.amdx_now.projection.quarter_position == 3
    QTest.mouseClick(
        composition.amdx_now.role_buttons[Role.D],
        Qt.MouseButton.LeftButton,
    )
    QApplication.processEvents()

    assert command_count(connection) == before + 1
    assert "D" in source.table.item(1, 2).text()
    assert composition.amdx_now.table.item(1, 2).text() == source.table.item(1, 2).text()
    assert "no Watch history/comparison" in composition.amdx_now.status_label.text()


def test_x_subtype_remains_one_action_when_the_selected_quarter_allows_x(cockpit):
    _window, shell, connection = cockpit
    composition = shell.runtime.watch_quiet_composition
    source = shell.runtime.amdx_context_widget
    source.select_quarter(1, 3)
    QApplication.processEvents()
    before = command_count(connection)

    assert composition.amdx_now.x_buttons[XSubtype.REVERSAL].isVisible()
    QTest.mouseClick(
        composition.amdx_now.x_buttons[XSubtype.REVERSAL],
        Qt.MouseButton.LeftButton,
    )
    QApplication.processEvents()

    assert command_count(connection) == before + 1
    assert "X(R)" in source.table.item(1, 3).text()
    assert "X(R)" in composition.amdx_now.table.item(1, 3).text()


def test_safety_strip_never_substitutes_safe_broker_facts(cockpit):
    _window, shell, _connection = cockpit
    composition = shell.runtime.watch_quiet_composition
    run = shell.active_trading_run

    assert composition.safety.cells["broker"][1].text() == "Adapter not connected"
    assert "Unavailable is not treated as safe" in composition.safety.cells["broker"][2].text()
    assert composition.safety.cells["position"][1].text() == "Unavailable"
    assert composition.safety.cells["orders"][1].text() == "Nothing staged by Cockpit"

    run.set_authorization_gate("trading-day-permitted", "Blocked")
    composition.load_context(run)
    assert composition.safety.cells["authorization"][1].text() == "No candidate active"
    assert "blocked" in composition.safety.cells["authorization"][2].text()
    assert "attention required" in composition.safety.summary_label.text()


def test_stale_compact_decision_keeps_error_through_refresh_without_replay(cockpit):
    _window, shell, connection = cockpit
    source = shell.runtime.amdx_context_widget
    compact = shell.runtime.watch_quiet_composition.amdx_now
    old_projection = compact.projection
    source.select_quarter(1, 3)
    compact.projection = old_projection
    before = command_count(connection)
    compact._choose(Role.D)
    assert "target changed" in compact.status_label.text()
    compact.refresh_projection(source.decision_projection())
    assert "target changed" in compact.status_label.text()
    assert command_count(connection) == before
    compact._select_quarter(1, 3)
    compact._choose(Role.X, XSubtype.REVERSAL)
    assert command_count(connection) == before + 1
    assert "target changed" not in compact.status_label.text()


def test_inactive_decision_cannot_restart_cancelled_gesture(cockpit):
    _window, shell, connection = cockpit
    source = shell.runtime.amdx_context_widget
    projection = source.decision_projection()
    before = command_count(connection)
    source.set_active(False)
    assert not source.choose_decision(projection.token, Role.D)
    assert source._gesture_cancelled
    assert command_count(connection) == before


def test_named_monitor_profile_moves_one_orientation_rail_and_persists(cockpit):
    _window, shell, connection = cockpit
    composition = shell.runtime.watch_quiet_composition
    shell.amdx_decision_dock.set_display_profile("tv-below")
    QApplication.processEvents()

    assert composition.profile == "tv-below"
    assert "below" in composition.orientation.chart_hint_label.text()
    index = composition.grid.indexOf(composition.orientation)
    row, column, row_span, column_span = composition.grid.getItemPosition(index)
    assert (row, column, row_span, column_span) == (2, 0, 1, 2)

    restored = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    try:
        restored_composition = (
            restored.trade_plan_widget.trading_day_shell_widget.runtime.watch_quiet_composition
        )
        assert restored_composition.profile == "tv-below"
    finally:
        dispose(restored)
