from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from tools.watch_decision_dock_demo import KIND, open_demo


def dispose(connection, window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    QApplication.processEvents()
    connection.close()


def test_retained_demo_opens_watch_and_restores_display_profile(tmp_path):
    directory = tmp_path / "trial"
    connection, window = open_demo(directory)
    window.show()
    QApplication.processEvents()
    shell = window.trade_plan_widget.trading_day_shell_widget
    try:
        assert shell.runtime.current_mode.id == "live-watch"
        assert shell.plan_reference_frame.isVisible()
        assert shell.amdx_decision_dock.reference_label.text().startswith(
            "No published AMDX definition"
        )
        shell.amdx_decision_dock.set_display_profile("tv-below")
        run_id = shell.active_trading_run.id
    finally:
        dispose(connection, window)

    connection, window = open_demo(directory)
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        assert shell.active_trading_run.id == run_id
        assert shell.amdx_decision_dock.display_profile == "tv-below"
        assert (directory / "watch-decision-dock-fixture.json").read_text().find(KIND) >= 0
    finally:
        dispose(connection, window)
