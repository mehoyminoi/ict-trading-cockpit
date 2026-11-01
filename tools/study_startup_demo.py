"""Retained synthetic Study-first startup trial; never uses the regular database."""

import argparse
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QApplication
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


def open_demo(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / "study-startup-v0.txt"
    if any(directory.iterdir()) and not marker.exists():
        raise ValueError("Use an empty directory or this trial's existing directory")
    if marker.exists() and (marker.read_text() != "Study startup v0" or not (directory / "demo.db").exists()):
        raise ValueError("Incomplete Study startup trial; use a new empty directory")
    os.environ["XDG_DATA_HOME"] = str(directory / "xdg")
    connection = open_application_database(directory / "demo.db")
    try:
        window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
        marker.write_text("Study startup v0")
        window.setWindowTitle("Study-first startup · synthetic trial · separate database")
        return connection, window
    except Exception:
        connection.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(tempfile.gettempdir()) / "ict-study-startup-v0")
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
