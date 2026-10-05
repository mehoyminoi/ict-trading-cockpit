from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow, QStatusBar, QTabWidget

from ict_cockpit.app_info import window_title
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.study_find_review_widget import StudyFindReviewWidget
from ict_cockpit.gui.study_find_widget import StudyFindWidget
from ict_cockpit.gui.tda_workflow import TDAWorkflowWidget


class MainWindow(QMainWindow):
    def __init__(
        self,
        tda_repository: TDARepository,
        study_find_repository: StudyFindRepository,
    ) -> None:
        super().__init__()

        self.tda_repository = tda_repository
        self.study_find_repository = study_find_repository

        self.setWindowTitle(window_title())
        self.resize(800, 500)

        self.tda_workflow = TDAWorkflowWidget()
        self.study_find_widget = StudyFindWidget()
        self.study_find_review_widget = StudyFindReviewWidget(
            self.study_find_repository
        )

        self.tabs = QTabWidget()
        self.tabs.addTab(self.tda_workflow, "Guided TDA")
        self.tabs.addTab(self.study_find_widget, "Study Find")
        self.tabs.addTab(self.study_find_review_widget, "Study Review")
        self.setCentralWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.tda_workflow.tda_ready.connect(self.save_tda)
        self.study_find_widget.study_find_ready.connect(self.save_study_find)

        self.pending_tda_draft = None
        self.tda_draft_save_timer = QTimer(self)
        self.tda_draft_save_timer.setSingleShot(True)
        self.tda_draft_save_timer.setInterval(750)
        self.tda_draft_save_timer.timeout.connect(
            self.save_pending_tda_draft
        )
        self.tda_workflow.draft_changed.connect(
            self.schedule_tda_draft_save
        )

        self.pending_study_find_draft = None
        self.study_find_draft_save_timer = QTimer(self)
        self.study_find_draft_save_timer.setSingleShot(True)
        self.study_find_draft_save_timer.setInterval(750)
        self.study_find_draft_save_timer.timeout.connect(
            self.save_pending_study_find_draft
        )
        self.study_find_widget.draft_changed.connect(
            self.schedule_study_find_draft_save
        )

        self._restore_drafts()

    def _restore_drafts(self) -> None:
        latest_tda_draft = self.tda_repository.get_latest_draft()
        if latest_tda_draft is not None:
            self.tda_workflow.load_tda(latest_tda_draft)
            self.status_bar.showMessage(
                "Restored unfinished TDA draft",
                3000,
            )

        latest_study_find_draft = (
            self.study_find_repository.get_latest_draft()
        )
        if latest_study_find_draft is not None:
            self.study_find_widget.load_draft(latest_study_find_draft)
            self.status_bar.showMessage(
                "Restored unfinished Study Find draft",
                3000,
            )

    def save_tda(self, tda) -> None:
        self.tda_draft_save_timer.stop()
        self.pending_tda_draft = None

        self.tda_repository.save(tda)
        self.status_bar.showMessage(
            f"TDA saved — {tda.status.value}",
            5000,
        )
        self.tda_workflow.mark_saved()

    def schedule_tda_draft_save(self, tda) -> None:
        self.pending_tda_draft = tda
        self.tda_draft_save_timer.start()

    def save_pending_tda_draft(self) -> None:
        if self.pending_tda_draft is None:
            return

        self.tda_repository.save_draft(self.pending_tda_draft)
        self.pending_tda_draft = None
        self.status_bar.showMessage("TDA draft saved", 1500)

    # Backward-compatible names retained for existing callers/tests.
    def schedule_draft_save(self, tda) -> None:
        self.schedule_tda_draft_save(tda)

    def save_pending_draft(self) -> None:
        self.save_pending_tda_draft()

    def schedule_study_find_draft_save(self, draft) -> None:
        self.pending_study_find_draft = draft
        self.study_find_draft_save_timer.start()

    def save_pending_study_find_draft(self) -> None:
        draft = self.pending_study_find_draft
        if draft is None:
            return

        if draft.has_content():
            self.study_find_repository.save_draft(draft)
            self.status_bar.showMessage("Study Find draft saved", 1500)
        else:
            self.study_find_repository.delete_draft(draft.id)

        self.pending_study_find_draft = None

    def save_study_find(self, study_find) -> None:
        self.study_find_draft_save_timer.stop()
        self.pending_study_find_draft = None

        self.study_find_repository.save(study_find)

        for image_path in self.study_find_widget.image_paths:
            self.study_find_repository.add_image(
                study_find.id,
                image_path,
            )

        self.study_find_repository.delete_draft(study_find.id)
        self.study_find_widget.mark_saved()
        self.study_find_review_widget.refresh()
        self.status_bar.showMessage("Study Find saved", 3000)
