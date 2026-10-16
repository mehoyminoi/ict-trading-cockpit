"""Retained native Watch contextual Study Find trial in a separate database."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QLabel

from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


REFERENCE = datetime(2026, 10, 9, 9, 15, tzinfo=MARKET_TIMEZONE)
KIND = "Watch contextual Study Find trial v0"


def open_demo(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / "watch-contextual-study-find-fixture.json"
    existing = manifest.exists()
    if not existing and any(directory.iterdir()):
        raise ValueError("Use an empty trial directory; existing files will not be replaced")
    metadata = json.loads(manifest.read_text()) if existing else None
    if existing and (metadata.get("kind") != KIND or not (directory / "demo.db").exists()):
        raise ValueError("The retained contextual Study Find fixture is incomplete or belongs to another trial")

    os.environ["XDG_DATA_HOME"] = str(directory / "xdg")
    connection = open_application_database(directory / "demo.db")
    try:
        window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
        for timer in window.findChildren(QTimer):
            timer.stop()
        shell = window.trade_plan_widget.trading_day_shell_widget
        if not existing:
            shell.run_environment = RunEnvironment.REPLAY
            shell.run_market_timestamp = REFERENCE
            if not shell.start_trading_run():
                raise ValueError(shell.summary_label.text())
            metadata = {"kind": KIND, "run_id": shell.active_trading_run.id}
            manifest.write_text(json.dumps(metadata, indent=2))
        if shell.active_trading_run is None or shell.active_trading_run.id != metadata["run_id"]:
            raise ValueError("This trial run was concluded. Use a new empty directory to repeat the trial")
        if shell.runtime.current_mode.id == "tda":
            shell.runtime.apply_transition("finish-tda", override_incomplete=True)
        if shell.runtime.current_mode.id != "live-watch":
            raise ValueError("The saved trial is past Watch. Use a new empty directory to repeat the trial")

        window.tabs.setCurrentWidget(window.trade_plan_widget)
        window.trade_plan_widget.focus_runtime()
        window.resize(1344, 756)
        window.setWindowTitle("Contextual Study Find · synthetic MNQ Replay · separate database")
        notice = QLabel(
            "Synthetic MNQ · 2026-10-09 09:15 NY · Study Find uses real draft/save/image paths · exact Watch run/time/AMDX association is display-only in v0"
        )
        notice.setWordWrap(True)
        window.statusBar().addPermanentWidget(notice, 1)

        menu = window.menuBar().addMenu("Workspace profile")
        window.contextual_study_find_trial_actions = []

        def add_action(title, callback):
            item = QAction(title, window)
            item.triggered.connect(callback)
            menu.addAction(item)
            window.contextual_study_find_trial_actions.append(item)

        add_action(
            "TradingView left · Cockpit right",
            lambda: shell.amdx_decision_dock.set_display_profile("tv-left"),
        )
        add_action(
            "Cockpit above · TradingView below",
            lambda: shell.amdx_decision_dock.set_display_profile("tv-below"),
        )
        return connection, window
    except Exception:
        if "window" in locals():
            for timer in window.findChildren(QTimer):
                timer.stop()
            window.close()
            window.deleteLater()
        connection.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "ict-watch-contextual-study-find-v0",
    )
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
