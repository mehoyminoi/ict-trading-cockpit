import argparse
import os
from pathlib import Path
import sqlite3
import sys

from PySide6.QtWidgets import QApplication

from ict_cockpit.database.bootstrap import open_default_application_database
from ict_cockpit.database.feedback_repository import FeedbackRepository
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.database.trade_record_repository import TradeRecordRepository
from ict_cockpit.existing_workspace import open_existing_workspace
from ict_cockpit.gui.main_window import MainWindow


def open_window(workspace=None):
    """Use the shared application, retaining its normal startup routing."""
    previous_xdg = os.environ.get('XDG_DATA_HOME')
    if workspace is None:
        connection = open_default_application_database()
        root = None
    else:
        connection, root = open_existing_workspace(workspace)
    try:
        window = MainWindow(
            TDARepository(connection), StudyFindRepository(connection),
            FeedbackRepository(connection), TradeRecordRepository(connection),
        )
        if root is not None:
            window.setWindowTitle(f'{window.windowTitle()} · retained trial workspace · {root}')
        return connection, window
    except BaseException:
        connection.close()
        if workspace is not None:
            if previous_xdg is None:
                os.environ.pop('XDG_DATA_HOME', None)
            else:
                os.environ['XDG_DATA_HOME'] = previous_xdg
        raise


def main(argv=None, *, require_workspace=False) -> int:
    parser = argparse.ArgumentParser(description='Open Cockpit with normal Study-first / active-run restoration.')
    parser.add_argument('--workspace', type=Path, required=require_workspace,
                        help='Existing retained Study directory; never creates or migrates it')
    args = parser.parse_args(argv)
    app = QApplication.instance() or QApplication([sys.argv[0]])
    try:
        connection, window = open_window(args.workspace)
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.exit(1, f'Cockpit could not open: {error}\n')
    window.show()
    try:
        return app.exec()
    finally:
        connection.close()


if __name__ == '__main__':
    sys.exit(main())
