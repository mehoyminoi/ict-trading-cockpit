"""Retained native shared-calendar trial in its own synthetic database."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QLabel
from ict_cockpit.analysis.amdx import Role
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


REFERENCE = datetime(2026, 10, 9, 9, 15, tzinfo=MARKET_TIMEZONE)
HISTORICAL = datetime(1985, 8, 12, 9, 15, tzinfo=MARKET_TIMEZONE)
KIND = 'AMDX shared calendar native trial v0'


def open_demo(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / 'shared-fixture.json'
    existing = manifest.exists()
    if not existing and any(directory.iterdir()):
        raise ValueError('Use an empty trial directory; existing files will not be replaced')
    metadata = json.loads(manifest.read_text()) if existing else None
    if existing and (metadata.get('kind') != KIND or not (directory / 'demo.db').exists()):
        raise ValueError('The retained shared-calendar fixture is incomplete or belongs to another trial')
    connection = open_application_database(directory / 'demo.db')
    try:
        window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
        for timer in window.findChildren(QTimer):
            timer.stop()
        shell = window.trade_plan_widget.trading_day_shell_widget
        if not existing:
            target = shell.calendar_repository.master.prepare_target('MNQ', reference=REFERENCE, level='year', position=3)
            shell.calendar_repository.catalog.revise(target.target, command_id='synthetic-launch-year',
                recorded_at=datetime.now().astimezone(), role=Role.D, anchor_id='synthetic-launch-anchor',
                source_ref='Synthetic fixture: starting Yearly AMDX, not a market assessment')
            shell.run_environment = RunEnvironment.REPLAY
            shell.run_market_timestamp = REFERENCE
            if not shell.start_trading_run():
                raise ValueError(shell.summary_label.text())
            metadata = dict(kind=KIND, run_id=shell.active_trading_run.id)
            manifest.write_text(json.dumps(metadata, indent=2))
        if shell.active_trading_run is None or shell.active_trading_run.id != metadata['run_id']:
            raise ValueError('This trial run was concluded. Use a new empty directory to repeat the trial')
        window.trade_plan_widget.focus_runtime()
        window.resize(1344, 756)
        window.setWindowTitle('Shared AMDX calendar · synthetic MNQ Replay · separate database')
        notice = QLabel('Synthetic MNQ · 2026-10-09 09:15 NY · initial Yearly AMDX is fixture data · close/reopen retains edits')
        notice.setWordWrap(True)
        window.statusBar().addPermanentWidget(notice, 1)
        menu = window.menuBar().addMenu('Shared trial')
        window.shared_trial_actions = []
        def action(title, callback):
            item = QAction(title, window)
            item.triggered.connect(callback)
            menu.addAction(item)
            window.shared_trial_actions.append(item)
        def study(reference, channel):
            lab = window.amdx_catalog_widget
            lab.leave_run_scope()
            lab.channel_selector.setCurrentText(channel)
            lab.set_reference(reference.isoformat())
            lab.select_cell(2, 3)
            window.tabs.setCurrentWidget(lab)
        def watch():
            if shell.runtime.current_mode.id == 'tda':
                shell.runtime.apply_transition('finish-tda', override_incomplete=True)
            elif shell.runtime.current_mode.id == 'post-market':
                window.statusBar().showMessage('Review is the last checkpoint; use a new trial directory to repeat Watch', 6000)
                return
            window.tabs.setCurrentWidget(window.trade_plan_widget)
            window.trade_plan_widget.focus_runtime()
        def review():
            if shell.runtime.current_mode.id == 'tda':
                shell.runtime.apply_transition('finish-tda', override_incomplete=True)
            if shell.runtime.current_mode.id == 'live-watch':
                shell.runtime.apply_transition('live-finish')
            window.tabs.setCurrentWidget(window.trade_plan_widget)
            window.trade_plan_widget.focus_runtime()
        action('1 · Historical Lab · 1985 Yearly Q3 · Observed', lambda: study(HISTORICAL, 'Observed'))
        action('2 · Watch · synthetic incomplete-TDA override', watch)
        action('Inspect current Yearly working calendar', lambda: study(REFERENCE, 'Expected'))
        action('5 · Review · captured launch context', review)
        return connection, window
    except Exception:
        if 'window' in locals():
            for timer in window.findChildren(QTimer):
                timer.stop()
            window.close()
            window.deleteLater()
        connection.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path(tempfile.gettempdir()) / 'ict-amdx-shared-native-v0')
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
