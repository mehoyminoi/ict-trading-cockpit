from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from ict_cockpit.app_info import window_title
from ict_cockpit.database.tda_repository import TDARepository


class MainWindow(QMainWindow):
    def __init__(self, tda_repository: TDARepository) -> None:
        super().__init__()

        self.tda_repository = tda_repository

        self.setWindowTitle(window_title())
        self.resize(800, 500)

        title = QLabel("ICT Trading Cockpit")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        status = QLabel("Development environment working")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(status)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
