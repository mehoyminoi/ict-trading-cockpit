import pytest

from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from ict_cockpit.analysis.amdx import XSubtype
from PySide6.QtWidgets import QApplication

from tools.watch_quiet_composition_demo import KIND, open_demo


def dispose(connection, window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    QApplication.processEvents()
    connection.close()


@pytest.mark.parametrize("return_from_workspace", [False, True])
def test_operator_q4_entry_from_demo_and_after_workspace_return(tmp_path, return_from_workspace):
    connection, window = open_demo(tmp_path / "entry-trial")
    window.show()
    QApplication.processEvents()
    shell = window.trade_plan_widget.trading_day_shell_widget
    source = shell.runtime.amdx_context_widget
    compact = shell.runtime.watch_quiet_composition.amdx_now
    try:
        if return_from_workspace:
            window.tabs.setCurrentWidget(window.study_find_widget)
            window.tabs.setCurrentWidget(window.trade_plan_widget)
            QApplication.processEvents()
        rect = compact.table.visualItemRect(compact.table.item(1, 3))
        QTest.mouseClick(compact.table.viewport(), Qt.MouseButton.LeftButton, pos=rect.center())
        QApplication.processEvents()
        assert compact.projection.quarter_position == 4
        QTest.mouseClick(compact.x_buttons[XSubtype.REVERSAL], Qt.MouseButton.LeftButton)
        QApplication.processEvents()
        assert "X(R)" in compact.table.item(1, 3).text(), (
            source.status_label.text(), source._gesture_cancelled, source._surface_active
        )
    finally:
        dispose(connection, window)

    connection, window = open_demo(tmp_path / "entry-trial")
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        compact = shell.runtime.watch_quiet_composition.amdx_now
        assert "X(R)" in compact.table.item(1, 3).text()
        compact._select_quarter(1, 3)
        assert shell.amdx_decision_dock.source.decision_projection().current_subtype is XSubtype.REVERSAL
    finally:
        dispose(connection, window)


def test_retained_demo_restores_profile_gate_and_composition(tmp_path):
    directory = tmp_path / "trial"
    connection, window = open_demo(directory)
    window.show()
    QApplication.processEvents()
    shell = window.trade_plan_widget.trading_day_shell_widget
    try:
        run_id = shell.active_trading_run.id
        shell.amdx_decision_dock.set_display_profile("tv-below")
        shell._set_authorization_gate("trading-day-permitted", "Blocked")
        assert shell.runtime.watch_quiet_composition.profile == "tv-below"
        assert "attention required" in (
            shell.runtime.watch_quiet_composition.safety.summary_label.text()
        )
    finally:
        dispose(connection, window)

    connection, window = open_demo(directory)
    window.show()
    QApplication.processEvents()
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        composition = shell.runtime.watch_quiet_composition
        assert shell.active_trading_run.id == run_id
        assert composition.profile == "tv-below"
        assert composition.safety.cells["authorization"][1].text() == (
            "No candidate active"
        )
        assert "blocked" in composition.safety.cells["authorization"][2].text()
        assert KIND in (
            directory / "watch-quiet-composition-fixture.json"
        ).read_text()
    finally:
        dispose(connection, window)
