"""Seed one clearly synthetic question/criterion in an isolated Study workspace."""
import argparse
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import QApplication
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.analysis.amdx_rules import Condition, Definition, QuartetScope


def open_demo(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / 'study-criterion-v0.txt'
    fresh = not any(directory.iterdir())
    if not fresh and (not marker.exists() or marker.read_text() != 'Synthetic criterion Study v0'
                      or not (directory / 'demo.db').exists()):
        raise ValueError('Use a new empty directory or this criterion trial directory')
    os.environ['XDG_DATA_HOME'] = str(directory / 'xdg')
    connection = open_application_database(directory / 'demo.db')
    try:
        window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
        pane = window.amdx_catalog_widget
        window.tabs.setCurrentWidget(pane)
        if fresh:
            window.integrated_study_task.question.setText('Synthetic study: does a London close-inside observation satisfy this candidate for Asia A?')
            pane.date_input.setDate(QDate(2026, 10, 8))
            pane.time_input.setTime(QTime(9, 15))
            definition = Definition('synthetic-study-close-inside', 'trial-v1', window.trade_plan.revision,
                'Candidate', 'day', 1, 'Assigned Role', 'A', 0,
                (Condition(QuartetScope(2), 'synthetic-close-inside', 'eq', True),),
                'SYNTHETIC: London close-inside supports Asia A (workflow test only)')
            window.trading_session_run_repository.amdx.definitions.save_candidate(definition)
            row = next(i for i, item in enumerate(pane.projection.cycles) if item.context.cycle.layer == 'day')
            pane.table.setCurrentCell(row, 1)
            marker.write_text('Synthetic criterion Study v0')
        window.setWindowTitle('Synthetic criterion Study · no real price data or adopted trading rule')
        return connection, window
    except Exception:
        connection.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path(tempfile.gettempdir()) / 'ict-study-criterion-v0')
    args = parser.parse_args()
    app = QApplication.instance() or QApplication(sys.argv)
    connection, window = open_demo(args.data_dir)
    window.show()
    try:
        return app.exec()
    finally:
        connection.close()


if __name__ == '__main__':
    raise SystemExit(main())
