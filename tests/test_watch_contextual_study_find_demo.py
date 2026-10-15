from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from tools.watch_contextual_study_find_demo import KIND, open_demo


def dispose(connection, window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    QApplication.processEvents()
    connection.close()


def test_retained_demo_restores_watch_draft_and_display_profile(tmp_path):
    directory = tmp_path / "trial"
    connection, window = open_demo(directory)
    window.show()
    QApplication.processEvents()
    shell = window.trade_plan_widget.trading_day_shell_widget
    try:
        assert shell.runtime.current_mode.id == "live-watch"
        dock = window.contextual_study_find_dock
        dock.open_for(shell.study_find_button, shell._study_find_capture_basis())
        dock.pattern_input.setText("Retained pattern")
        dock.observation_input.setPlainText("Retained observation")
        draft_id = window.study_find_widget.current_study_find_id
        run_id = shell.active_trading_run.id
        dock.dismiss()
        shell.amdx_decision_dock.set_display_profile("tv-below")
    finally:
        dispose(connection, window)

    connection, window = open_demo(directory)
    window.show()
    QApplication.processEvents()
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        dock = window.contextual_study_find_dock
        assert shell.active_trading_run.id == run_id
        assert window.study_find_widget.current_study_find_id == draft_id
        assert window.study_find_widget.pattern_input.text() == "Retained pattern"
        assert dock.display_profile == "tv-below"
        assert (directory / "watch-contextual-study-find-fixture.json").read_text().find(KIND) >= 0
    finally:
        dispose(connection, window)
