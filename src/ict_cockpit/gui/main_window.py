from PySide6.QtWidgets import QLabel, QMainWindow, QStatusBar
from PySide6.QtCore import QTimer

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

        latest_draft = self.tda_repository.get_latest_draft()

        if latest_draft is not None:
            self.tda_workflow.load_tda(latest_draft)

            self.status_bar.showMessage(
                "Restored unfinished TDA draft",
                3000,
            )

        self.setCentralWidget(self.tda_workflow)
        self.pending_draft = None

        self.draft_save_timer = QTimer(self)
        self.draft_save_timer.setSingleShot(True)
        self.draft_save_timer.setInterval(750)

        self.draft_save_timer.timeout.connect(
            self.save_pending_draft
        )

        self.tda_workflow.draft_changed.connect(
            self.schedule_draft_save
)

    def save_tda(self, tda) -> None:
        self.draft_save_timer.stop()
        self.pending_draft = None   

        self.tda_repository.save(tda)

        self.status_bar.showMessage(
            f"TDA saved — {tda.status.value}",
            5000,
        )

        self.tda_workflow.mark_saved()

    def schedule_draft_save(self, tda) -> None:
        self.pending_draft = tda
        self.draft_save_timer.start()

    def save_pending_draft(self) -> None:
        if self.pending_draft is None:
            return

        self.tda_repository.save_draft(
            self.pending_draft
        )

        self.pending_draft = None

        self.status_bar.showMessage(
            "Draft saved",
            1500,
        )