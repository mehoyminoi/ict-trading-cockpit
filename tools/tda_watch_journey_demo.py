"""TDA-to-Watch journey using the real runtime in a separate synthetic Replay workspace."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLabel

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
KIND = "TDA Watch journey trial v0"


def open_demo(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / "tda-watch-journey-fixture.json"
    existing = manifest.exists()
    if not existing and any(directory.iterdir()):
        raise ValueError("Use an empty trial directory; existing files will not be replaced")
    metadata = json.loads(manifest.read_text()) if existing else None
    if existing and (
        metadata.get("kind") != KIND or not (directory / "demo.db").exists()
    ):
        raise ValueError(
            "The retained TDA-Watch fixture is incomplete or belongs to another trial"
        )

    os.environ["XDG_DATA_HOME"] = str(directory / "xdg")
    connection = open_application_database(directory / "demo.db")
    try:
        window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
        for timer in window.findChildren(QTimer):
            timer.stop()
        shell = window.trade_plan_widget.trading_day_shell_widget
        if not existing:
            shell.run_environment = RunEnvironment.REPLAY
            shell.run_purpose = default_purpose_for_environment(
                shell.run_environment
            )
            shell.run_market_timestamp = REFERENCE
            if not shell.start_trading_run():
                raise ValueError(shell.summary_label.text())
            metadata = {"kind": KIND, "run_id": shell.active_trading_run.id}
            manifest.write_text(json.dumps(metadata, indent=2))
        if (
            shell.active_trading_run is None
            or shell.active_trading_run.id != metadata["run_id"]
        ):
            raise ValueError(
                "This trial run was concluded. Use a new empty directory to repeat the trial"
            )
        if shell.runtime.current_mode.id not in ("tda", "live-watch"):
            raise ValueError("This trial has moved beyond TDA/Watch. Reuse it for inspection through the normal app, or choose a new empty trial directory.")
        # Do not fill stations, complete work, override incomplete TDA or move modes.
        # The operator follows the same runtime transition as ordinary use.

        window.tabs.setCurrentWidget(window.trade_plan_widget)
        window.trade_plan_widget.focus_runtime()
        if not existing:
            window.resize(1600, 900)
        window.setWindowTitle(
            "TDA → Watch journey · synthetic MNQ Replay · separate database"
        )
        notice = QLabel(
            "Synthetic MNQ Replay · 2026-10-09 09:15 NY · real TDA → Watch path · no broker · not the separate Guided TDA tab"
        )
        notice.setWordWrap(True)
        window.statusBar().addPermanentWidget(notice, 1)

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
        default=Path.home() / "ict-cockpit-trials" / "tda-watch-journey-v0",
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
