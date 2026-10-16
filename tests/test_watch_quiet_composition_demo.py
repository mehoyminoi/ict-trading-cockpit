from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from tools.watch_quiet_composition_demo import KIND, open_demo


def dispose(connection, window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    QApplication.processEvents()
    connection.close()


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
