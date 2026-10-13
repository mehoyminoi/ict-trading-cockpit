"""Retained shared Observed Review trial in a separate synthetic database."""
import argparse
from datetime import timedelta
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication
from ict_cockpit.analysis.market_time import build_market_time_context
from tools.amdx_shared_calendar_demo import open_demo as open_shared_demo, REFERENCE


def open_demo(directory):
    connection, window = open_shared_demo(directory)
    shell = window.trade_plan_widget.trading_day_shell_widget
    if shell.runtime.current_mode.id == "tda":
        shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    if shell.runtime.current_mode.id == "live-watch":
        shell.runtime.apply_transition("live-finish")
    window.setWindowTitle("Maintained Observed Review · synthetic MNQ · separate database")
    for action in window.menuBar().actions():
        if action.text() == "Shared trial":
            window.menuBar().removeAction(action)
    menu = window.menuBar().addMenu("Review trial")
    window.review_trial_actions = []
    def add(title, callback):
        action = QAction(title, window)
        action.triggered.connect(callback)
        menu.addAction(action)
        window.review_trial_actions.append(action)
    def lab():
        pane = window.amdx_catalog_widget
        pane.leave_run_scope()
        pane.set_reference(REFERENCE.isoformat())
        pane.select_cell(6, 3)
        window.tabs.setCurrentWidget(pane)
    def return_review():
        window.tabs.setCurrentWidget(window.trade_plan_widget)
        window.trade_plan_widget.focus_runtime()
    def advance():
        run = shell.active_trading_run
        if run is not None:
            run.market_time_context = build_market_time_context(REFERENCE + timedelta(days=1), source="Historical Reference").to_dict()
            window.save_trading_session_run(run)
            shell._refresh_market_time_display()
    add("Lab · same NYAM 90-minute Observed quartet", lab)
    add("Return to Review", return_review)
    add("Advance display to next Trading Day", advance)
    return_review()
    return connection, window


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(tempfile.gettempdir()) / "ict-amdx-review-calendar-v0")
    args = parser.parse_args()
    app = QApplication.instance() or QApplication(sys.argv)
    connection, window = open_demo(args.data_dir)
    window.show()
    try:
        return app.exec()
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
