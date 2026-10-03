from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from ict_cockpit.app_info import window_title


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

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
