"""Retained, isolated TDA map/Focus trial; no Trading Run or regular database."""
import argparse
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.tda_station_session_repository import TDAStationSessionRepository
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.tda_station_runner_widget import TDAStationRunnerWidget


class TrialWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def closeEvent(self, event):
        self.runner._save_splitter()
        self.settings.setValue('window/geometry', self.saveGeometry())
        self.settings.sync()
        super().closeEvent(event)


def open_demo(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / 'tda-mapped-focus-v0.txt'
    if any(directory.iterdir()) and not marker.exists():
        raise ValueError('Use a new empty directory or this trial’s existing directory')
    if marker.exists() and (marker.read_text() != 'TDA mapped Focus v0' or not (directory/'demo.db').exists()):
        raise ValueError('Incomplete trial; use a new empty directory')
    connection = open_application_database(directory/'demo.db')
    try:
        repository = TDAStationSessionRepository(connection)
        runner = TDAStationRunnerWidget(build_default_process_blueprint())
        settings = QSettings(str(directory/'layout.ini'), QSettings.Format.IniFormat)
        runner.configure_workspace_settings(settings)
        saved = repository.get_latest()
        if saved is not None:
            runner.load_session(saved)
        runner.session_changed.connect(repository.save)
        window = TrialWindow(settings)
        window.runner = runner
        window.repository = repository
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(runner)
        window.setCentralWidget(scroll)
        window.resize(1440,810)
        geometry = settings.value('window/geometry')
        if geometry is not None:
            window.restoreGeometry(geometry)
        window.setWindowTitle('TDA mapped Focus · synthetic trial · no Trading Run')
        marker.write_text('TDA mapped Focus v0')
        return connection, window
    except Exception:
        connection.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=Path(tempfile.gettempdir())/'ict-tda-mapped-focus-v0')
    args=parser.parse_args()
    app=QApplication.instance() or QApplication(sys.argv)
    connection,window=open_demo(args.data_dir)
    window.show()
    try:
        return app.exec()
    finally:
        connection.close()

if __name__ == '__main__':
    raise SystemExit(main())
