"""Normal-window AMDX entry sandbox, automatically retained for restart checks."""
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QLabel
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, build_market_time_context
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


def open_demo(directory, *, review=False):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / "amdx-entry-fixture.json"
    existing = manifest.exists()
    if not existing and any(directory.iterdir()):
        raise ValueError("Use an empty AMDX sandbox directory; existing files will not be replaced")
    metadata = json.loads(manifest.read_text()) if existing else None
    kind = "AMDX observed entry fixture v1" if review else "AMDX entry fixture v1"
    if metadata is not None and metadata.get("kind") != kind:
        raise ValueError("This directory is not an AMDX entry sandbox")
    if existing and not (directory / "demo.db").exists():
        raise ValueError("The saved sandbox database is missing; it will not be reseeded")
    connection = open_application_database(directory / "demo.db")
    try:
        window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
        shell = window.trade_plan_widget.trading_day_shell_widget
        if not existing:
            shell.run_environment = RunEnvironment.REPLAY
            shell.run_market_timestamp = datetime(2026, 10, 8, 9, 15, tzinfo=MARKET_TIMEZONE)
            if not shell.start_trading_run():
                raise ValueError("Unable to start the synthetic Replay run")
            if review:
                # Explicit synthetic override, through the normal process actions.
                # No trading rules, evidence or completed TDA are fabricated.
                if not shell.runtime.apply_transition("finish-tda", override_incomplete=True):
                    raise ValueError("Unable to advance synthetic TDA")
                if not shell.runtime.apply_transition("live-finish"):
                    raise ValueError("Unable to open synthetic Review")
            metadata = {"kind": kind, "run_id": shell.active_trading_run.id}
            manifest.write_text(json.dumps(metadata, indent=2))
        if shell.active_trading_run is None or shell.active_trading_run.id != metadata["run_id"]:
            raise ValueError("The saved fixture has been concluded; use a new empty directory for another run")
        window.trade_plan_widget.focus_runtime()
        if review and shell.runtime.current_mode.id != "post-market":
            raise ValueError("The retained observed fixture is not in Review; use a new empty directory")
        window.setWindowTitle("AMDX observed entry sandbox · synthetic Replay" if review else "AMDX entry sandbox · synthetic Replay · separate database")
        notice = QLabel(f"Synthetic {'Review (incomplete TDA overridden)' if review else 'AMDX entry'} sandbox · {directory / 'demo.db'} · restart with the same command")
        notice.setWordWrap(True)
        window.statusBar().addPermanentWidget(notice, 1)
        menu = window.menuBar().addMenu("Demo reference")
        advance = QAction("Advance by 90 minutes", window)
        def advance_reference():
            run = shell.active_trading_run
            if run is None:
                return
            reference = datetime.fromisoformat(run.market_time_context["captured_at"])
            run.market_time_context = build_market_time_context(reference + timedelta(minutes=90), source="Historical Reference").to_dict()
            window.save_trading_session_run(run)
            shell._refresh_market_time_display()
        advance.triggered.connect(advance_reference)
        menu.addAction(advance)
        window.amdx_demo_advance = advance
        if review:
            failure = QAction("Simulate observed write failure", window)
            failure.setCheckable(True)
            trigger = "amdx_demo_observed_failure"
            failure.setChecked(connection.execute("SELECT 1 FROM sqlite_master WHERE type='trigger' AND name=?", (trigger,)).fetchone() is not None)
            def set_failure(enabled):
                if enabled:
                    connection.execute(f"CREATE TRIGGER IF NOT EXISTS {trigger} BEFORE INSERT ON amdx_observed_command BEGIN SELECT RAISE(ABORT, 'synthetic observed write failure'); END")
                else:
                    connection.execute(f"DROP TRIGGER IF EXISTS {trigger}")
            failure.toggled.connect(set_failure)
            menu.addAction(failure)
            window.amdx_demo_failure = failure
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
    parser.add_argument("--data-dir", type=Path, default=Path(tempfile.gettempdir()) / "ict-amdx-entry")
    args = parser.parse_args()
    app = QApplication.instance() or QApplication(sys.argv)
    connection, window = open_demo(args.data_dir)
    window.resize(1100, 900)
    window.show()
    try:
        return app.exec()
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
