from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QStatusBar,
    QTabWidget,
)

from ict_cockpit.app_info import APP_VERSION, window_title
from ict_cockpit.database.feedback_repository import FeedbackRepository
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.database.trade_record_repository import TradeRecordRepository
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.feedback_dialog import FeedbackDialog
from ict_cockpit.gui.study_find_review_widget import StudyFindReviewWidget
from ict_cockpit.gui.study_find_widget import StudyFindWidget
from ict_cockpit.gui.tda_workflow import TDAWorkflowWidget
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget
from ict_cockpit.gui.trade_summary_widget import TradeSummaryWidget


class MainWindow(QMainWindow):
    def __init__(
        self,
        tda_repository: TDARepository,
        study_find_repository: StudyFindRepository,
        feedback_repository: FeedbackRepository | None = None,
        trade_record_repository: TradeRecordRepository | None = None,
    ) -> None:
        super().__init__()

        self.tda_repository = tda_repository
        self.study_find_repository = study_find_repository
        self.feedback_repository = feedback_repository or FeedbackRepository(
            study_find_repository.connection
        )
        self.trade_record_repository = (
            trade_record_repository
            or TradeRecordRepository(study_find_repository.connection)
        )

        self.setWindowTitle(window_title())
        self.resize(900, 650)

        self.trade_plan = build_default_trade_plan()
        self.trade_plan_widget = TradePlanWidget(self.trade_plan)
        # Backward-compatible references retained while Process Map tests and
        # callers transition to the Trade Plan parent model.
        self.process_blueprint = self.trade_plan.process_blueprint
        self.process_blueprint_widget = (
            self.trade_plan_widget.process_blueprint_widget
        )

        self.tda_workflow = TDAWorkflowWidget()
        self.study_find_widget = StudyFindWidget()
        self.trade_summary_widget = TradeSummaryWidget()
        self.study_find_review_widget = StudyFindReviewWidget(
            self.study_find_repository
        )

        self.tabs = QTabWidget()
        self.tabs.addTab(self.trade_plan_widget, "Trade Plan")
        self.tabs.addTab(self.tda_workflow, "Guided TDA")
        self.tabs.addTab(self.study_find_widget, "Study Find")
        self.tabs.addTab(self.trade_summary_widget, "Trade Summary")
        self.tabs.addTab(self.study_find_review_widget, "Study Review")
        self.setCentralWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._configure_feedback_actions()

        self.tda_workflow.tda_ready.connect(self.save_tda)
        self.study_find_widget.study_find_ready.connect(self.save_study_find)
        self.trade_summary_widget.trade_ready.connect(self.save_trade_record)

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

        self.pending_trade_draft = None
        self.trade_draft_save_timer = QTimer(self)
        self.trade_draft_save_timer.setSingleShot(True)
        self.trade_draft_save_timer.setInterval(750)
        self.trade_draft_save_timer.timeout.connect(
            self.save_pending_trade_draft
        )
        self.trade_summary_widget.draft_changed.connect(
            self.schedule_trade_draft_save
        )

        self._restore_drafts()

    def _configure_feedback_actions(self) -> None:
        feedback_menu = self.menuBar().addMenu("Feedback")

        self.capture_feedback_action = QAction("Capture Feedback", self)
        self.capture_feedback_action.setShortcut(QKeySequence("Ctrl+Alt+F"))
        self.capture_feedback_action.triggered.connect(
            self.capture_feedback
        )
        self.addAction(self.capture_feedback_action)
        feedback_menu.addAction(self.capture_feedback_action)

        self.copy_feedback_digest_action = QAction(
            "Copy Feedback Digest",
            self,
        )
        self.copy_feedback_digest_action.triggered.connect(
            self.copy_feedback_digest
        )
        feedback_menu.addAction(self.copy_feedback_digest_action)

    def current_feedback_context(self) -> tuple[str, str]:
        current_widget = self.tabs.currentWidget()
        tab_name = self.tabs.tabText(self.tabs.currentIndex())

        if current_widget is self.trade_plan_widget:
            return tab_name, self.trade_plan_widget.feedback_record_id

        if current_widget is self.tda_workflow:
            return tab_name, self.tda_workflow.current_tda_id

        if current_widget is self.study_find_widget:
            return tab_name, self.study_find_widget.current_study_find_id

        if current_widget is self.trade_summary_widget:
            return tab_name, self.trade_summary_widget.current_trade_id

        if current_widget is self.study_find_review_widget:
            row = self.study_find_review_widget.study_list.currentRow()
            if 0 <= row < len(self.study_find_review_widget.study_finds):
                study_find = self.study_find_review_widget.study_finds[row]
                return tab_name, study_find.id

        return tab_name or "Unknown", ""

    def capture_feedback(self) -> None:
        context, record_id = self.current_feedback_context()
        dialog = FeedbackDialog(
            context=context,
            record_id=record_id,
            app_version=APP_VERSION,
            parent=self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.feedback_repository.save(dialog.build_entry())
        self.status_bar.showMessage("Feedback captured", 2000)

    def copy_feedback_digest(self) -> str:
        digest = self.feedback_repository.render_markdown_digest()
        QApplication.clipboard().setText(digest)
        self.status_bar.showMessage(
            "Feedback digest copied to clipboard",
            2500,
        )
        return digest

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

        latest_trade_draft = self.trade_record_repository.get_latest_draft()
        if latest_trade_draft is not None:
            self.trade_summary_widget.load_draft(latest_trade_draft)
            self.status_bar.showMessage(
                "Restored unfinished Trade Summary draft",
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

    def schedule_trade_draft_save(self, draft) -> None:
        self.pending_trade_draft = draft
        self.trade_draft_save_timer.start()

    def save_pending_trade_draft(self) -> None:
        draft = self.pending_trade_draft
        if draft is None:
            return

        if draft.has_content():
            self.trade_record_repository.save_draft(draft)
            self.status_bar.showMessage("Trade Summary draft saved", 1500)
        else:
            self.trade_record_repository.delete_draft(draft.id)

        self.pending_trade_draft = None

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

    def save_trade_record(self, trade) -> None:
        self.trade_draft_save_timer.stop()
        self.pending_trade_draft = None

        self.trade_record_repository.save(trade)
        for image_path in self.trade_summary_widget.image_paths:
            self.trade_record_repository.add_image(trade.id, image_path)

        self.trade_record_repository.delete_draft(trade.id)
        self.trade_summary_widget.mark_saved()
        self.status_bar.showMessage("Trade Summary saved", 3000)
