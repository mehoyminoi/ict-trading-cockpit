"""Retained higher Observed Review trial in a separate synthetic database."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QLabel
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow

REFERENCE=datetime(2027,1,1,9,15,37,tzinfo=MARKET_TIMEZONE)
KIND='AMDX higher Review synthetic trial v1'


def open_demo(directory):
    directory=Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    manifest=directory/'higher-review-fixture.json'
    existing=manifest.exists()
    if not existing and any(directory.iterdir()):
        raise ValueError('Use a new empty trial directory; existing files will not be replaced')
    metadata=json.loads(manifest.read_text()) if existing else None
    if existing and (metadata.get('kind')!=KIND or not (directory/'demo.db').exists()):
        raise ValueError('This directory belongs to another trial or its fixture is incomplete')
    connection=open_application_database(directory/'demo.db')
    try:
        window=MainWindow(TDARepository(connection),StudyFindRepository(connection))
        for timer in window.findChildren(QTimer):timer.stop()
        shell=window.trade_plan_widget.trading_day_shell_widget
        if not existing:
            shell.run_environment=RunEnvironment.REPLAY
            shell.run_market_timestamp=REFERENCE
            if not shell.start_trading_run():raise ValueError(shell.summary_label.text())
            metadata=dict(kind=KIND,run_id=shell.active_trading_run.id)
            manifest.write_text(json.dumps(metadata,indent=2))
        if shell.active_trading_run is None or shell.active_trading_run.id!=metadata['run_id']:
            raise ValueError('This trial was concluded; use a new empty directory for another run')
        if shell.runtime.current_mode.id=='tda':shell.runtime.apply_transition('finish-tda',override_incomplete=True)
        if shell.runtime.current_mode.id=='live-watch':shell.runtime.apply_transition('live-finish')
        window.tabs.setCurrentWidget(window.trade_plan_widget)
        window.trade_plan_widget.focus_runtime()
        window.resize(1344,756)
        window.setWindowTitle('Higher Observed Review · synthetic MNQ · separate database')
        notice=QLabel('Synthetic future calendar boundary · 2027-01-01 09:15:37 NY · no market data/prediction · close/reopen retains edits')
        notice.setWordWrap(True)
        window.statusBar().addPermanentWidget(notice,1)
        menu=window.menuBar().addMenu('Higher Review trial')
        fault=QAction('Simulate assessment write failure',window)
        fault.setCheckable(True)
        # A retained database may still contain an injection after closing the trial.
        fault.setChecked(bool(connection.execute("SELECT 1 FROM sqlite_master WHERE name='demo_higher_failure'").fetchone()))
        def toggle(enabled):
            if enabled:
                connection.execute("CREATE TRIGGER IF NOT EXISTS demo_higher_failure BEFORE INSERT ON amdx_run_observed_command BEGIN SELECT RAISE(ABORT,'Synthetic higher assessment write failure'); END")
            else:
                connection.execute('DROP TRIGGER IF EXISTS demo_higher_failure')
        fault.toggled.connect(toggle)
        menu.addAction(fault)
        window.higher_failure_action=fault
        return connection,window
    except Exception:
        if 'window' in locals():
            for timer in window.findChildren(QTimer):timer.stop()
            window.close();window.deleteLater()
        connection.close()
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=Path(tempfile.gettempdir())/'ict-amdx-higher-review-v1')
    args=parser.parse_args()
    app=QApplication.instance() or QApplication(sys.argv)
    connection,window=open_demo(args.data_dir)
    window.show()
    try:return app.exec()
    finally:connection.close()


if __name__=='__main__':raise SystemExit(main())
