"""Retained normal-window observed AMDX Review trial; synthetic Replay only."""
import argparse
from pathlib import Path
import sys
import tempfile

from amdx_entry_demo import open_demo
from PySide6.QtWidgets import QApplication


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(tempfile.gettempdir()) / "ict-amdx-observed-v1")
    args = parser.parse_args()
    app = QApplication.instance() or QApplication(sys.argv)
    connection, window = open_demo(args.data_dir, review=True)
    window.resize(1280, 720)
    window.show()
    try:
        return app.exec()
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
