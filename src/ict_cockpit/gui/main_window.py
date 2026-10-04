from PySide6.QtWidgets import QLabel, QMainWindow, QStatusBar

from ict_cockpit.app_info import window_title
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.tda_workflow import TDAWorkflowWidget


class MainWindow(QMainWindow):
    def __init__(self, tda_repository: TDARepository) -> None:
        super().__init__()

        self.tda_repository = tda_repository

        self.setWindowTitle(window_title())
        self.resize(800, 500)

        self.tda_workflow = TDAWorkflowWidget()

        self.tda_workflow.tda_ready.connect(self.save_tda)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.setCentralWidget(self.tda_workflow)

    def save_tda(self, tda) -> None:
        self.tda_repository.save(tda)

        self.status_bar.showMessage(
            f"TDA saved — {tda.status.value}",
            5000,
        )