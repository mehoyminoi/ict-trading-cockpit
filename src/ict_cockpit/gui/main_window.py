from PySide6.QtWidgets import QLabel, QMainWindow, QStatusBar, QTabWidget
from PySide6.QtCore import QTimer

from ict_cockpit.app_info import window_title
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.tda_workflow import TDAWorkflowWidget
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.gui.study_find_widget import StudyFindWidget


class MainWindow(QMainWindow):
    def __init__(
    self,
    tda_repository: TDARepository,
    study_find_repository: StudyFindRepository,
) -> None:
        super().__init__()

        self.tda_repository = tda_repository

        self.setWindowTitle(window_title())
        self.resize(800, 500)

        self.tda_workflow = TDAWorkflowWidget()


        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.tda_repository = tda_repository
        self.study_find_repository = study_find_repository

        self.tda_workflow = TDAWorkflowWidget()
        self.study_find_widget = StudyFindWidget()

        self.tda_workflow.tda_ready.connect(self.save_tda)

        self.study_find_widget.study_find_ready.connect(
                self.save_study_find
        )

        self.tabs = QTabWidget()
        self.tabs.addTab(self.tda_workflow, "Guided TDA")
        self.tabs.addTab(self.study_find_widget, "Study Find")

        latest_draft = self.tda_repository.get_latest_draft()

        if latest_draft is not None:
            self.tda_workflow.load_tda(latest_draft)

            self.status_bar.showMessage(
                "Restored unfinished TDA draft",
                3000,
            )

        self.setCentralWidget(self.tabs)
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

    def save_study_find(self, study_find) -> None:
        self.study_find_repository.save(study_find)

        for image_path in self.study_find_widget.image_paths:
            self.study_find_repository.add_image(
                study_find.id,
                image_path,
            )

        self.study_find_widget.mark_saved()

        self.status_bar.showMessage(
            "Study Find saved",
            3000,
        )