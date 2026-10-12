"""Check E7's normal application against a database created by accepted E6 code.

The first launch archives the pinned E6 source from local Git and runs its normal
repositories/UI in a separate offscreen process. Later launches only restore the
same working database. No operator history or production database is used.
"""
import argparse
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tarfile
import tempfile


E6_COMMIT = "42e3b346245de17e61a062e29fa6cd082d2527bf"
ROOT = Path(__file__).resolve().parents[1]


def prepare_sandbox(directory):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / "e6-origin.json"
    database = directory / "demo.db"
    if manifest.exists():
        evidence = json.loads(manifest.read_text(encoding="utf-8"))
        if evidence["source_commit"] != E6_COMMIT or not database.exists():
            raise ValueError("Incomplete or different compatibility sandbox; use a new directory.")
        return evidence
    if any(directory.iterdir()):
        raise ValueError("First launch requires an empty directory; existing files are never replaced.")
    # All archive entries come from this project's pinned Git source, not an
    # uploaded archive. Only src/ is required to execute the earlier application.
    archive = subprocess.run(
        ["git", "archive", E6_COMMIT, "src"], cwd=ROOT,
        check=True, capture_output=True,
    ).stdout
    with tempfile.TemporaryDirectory(prefix="ict-e6-source-") as source:
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            # Newer Python supports an explicit extraction policy; retain
            # compatibility with 3.10 installations before that backport.
            options = {"filter": "data"} if hasattr(tarfile, "data_filter") else {}
            bundle.extractall(source, **options)
        env = dict(os.environ, PYTHONPATH=str(Path(source) / "src"), QT_QPA_PLATFORM="offscreen")
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "seed_e6_compatibility.py"),
             str(directory), str(Path(source) / "src"), E6_COMMIT],
            cwd=source, env=env, check=True,
        )
    return json.loads(manifest.read_text(encoding="utf-8"))


def open_window(directory, evidence):
    sys.path.insert(0, str(ROOT / "src"))
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel
    from ict_cockpit.database.connection import create_connection
    from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
    from ict_cockpit.database.tda_repository import TDARepository
    from ict_cockpit.database.study_find_repository import StudyFindRepository
    from ict_cockpit.gui.main_window import MainWindow

    conn = create_connection(Path(directory) / "demo.db")
    try:
        initialize_schema(conn)
        window = MainWindow(TDARepository(conn), StudyFindRepository(conn))
        run = window.trade_plan_widget.trading_day_shell_widget.active_trading_run
        if run is None or run.id != evidence["run_id"]:
            raise ValueError("Original E6 run is no longer active. Use a new empty sandbox to repeat the check.")
        if run.market_context_snapshot != evidence["market_context_snapshot"]:
            raise ValueError("Restored context differs from the original E6 snapshot.")
        label = QLabel(
            f"E6 compatibility sandbox · synthetic data · original v37 → current v{CURRENT_SCHEMA_VERSION} / Alpha 0.7\n"
            f"Original run: {evidence['run_id']} · original capture: {evidence['capture_id']}"
        )
        label.setTextFormat(Qt.TextFormat.PlainText)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setWordWrap(True)
        window.statusBar().addPermanentWidget(label, 1)
        window.setWindowTitle("E6 → E7 compatibility — separate database / synthetic records")
        return conn, window
    except Exception:
        conn.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True,
                        help="Empty directory on first launch; same directory for restart")
    args = parser.parse_args()
    directory = args.data_dir.resolve()
    try:
        evidence = prepare_sandbox(directory)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Compatibility sandbox unavailable: {exc}\n"
                    "Run from a Git checkout containing the accepted E6 commit; git fetch origin if needed.\n")
    print(f"Database: {directory / 'demo.db'}", flush=True)
    print(f"Created by accepted E6 commit: {evidence['source_commit']}", flush=True)
    print(f"Original run: {evidence['run_id']}", flush=True)
    print(f"Original capture: {evidence['capture_id']}", flush=True)
    print("Restart: " + shlex.join([
        "python", "tools/e6_compatibility_demo.py", "--data-dir", str(directory)
    ]), flush=True)
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv[:1])
    conn, window = open_window(directory, evidence)
    window.show()
    try:
        return app.exec()
    finally:
        for timer in window.findChildren(QTimer):
            timer.stop()
        window.close()
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
