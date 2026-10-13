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
from ict_cockpit.database.competency_assessment_repository import (
    CompetencyAssessmentRepository,
)
from ict_cockpit.database.competency_development_direction_repository import (
    CompetencyDevelopmentDirectionRepository,
)
from ict_cockpit.database.competency_cross_run_observation_repository import (
    CompetencyCrossRunObservationRepository,
)
from ict_cockpit.database.competency_evidence_repository import (
    CompetencyEvidenceRepository,
)
from ict_cockpit.database.competency_evidence_maturity_repository import (
    CompetencyEvidenceMaturityRepository,
)
from ict_cockpit.database.feedback_repository import FeedbackRepository
from ict_cockpit.database.progression_attainment_repository import (
    ProgressionAttainmentRepository,
)
from ict_cockpit.database.progression_certification_repository import (
    ProgressionCertificationRepository,
)
from ict_cockpit.database.progression_regression_review_repository import (
    ProgressionRegressionReviewRepository,
)
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.summary_template_repository import (
    SummaryTemplateRepository,
)
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.database.tda_station_session_repository import (
    TDAStationSessionRepository,
)
from ict_cockpit.database.trade_record_repository import TradeRecordRepository
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import (
    TradingDaySessionRepository,
)
from ict_cockpit.database.trading_session_run_repository import (
    TradingSessionRunRepository,
)
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.database.context_capture_repository import ContextCaptureRepository
from ict_cockpit.gui.feedback_dialog import FeedbackDialog
from ict_cockpit.gui.study_find_review_widget import StudyFindReviewWidget
from ict_cockpit.gui.study_find_widget import StudyFindWidget
from ict_cockpit.gui.amdx_master_lab_widget import AMDXMasterLabWidget
from ict_cockpit.gui.summary_template_workbench_widget import (
    SummaryTemplateWorkbenchWidget,
)
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
        self.tda_station_session_repository = TDAStationSessionRepository(
            study_find_repository.connection
        )
        self.trading_day_session_repository = TradingDaySessionRepository(
            study_find_repository.connection
        )
        self.trading_day_repository = TradingDayRepository(
            study_find_repository.connection
        )
        self.trading_session_run_repository = TradingSessionRunRepository(
            study_find_repository.connection
        )
        self.competency_assessment_repository = (
            CompetencyAssessmentRepository(
                study_find_repository.connection
            )
        )
        self.competency_evidence_repository = CompetencyEvidenceRepository(
            study_find_repository.connection
        )
        self.competency_evidence_maturity_repository = (
            CompetencyEvidenceMaturityRepository(
                study_find_repository.connection
            )
        )
        self.competency_development_direction_repository = (
            CompetencyDevelopmentDirectionRepository(
                study_find_repository.connection
            )
        )
        self.competency_cross_run_observation_repository = (
            CompetencyCrossRunObservationRepository(
                study_find_repository.connection
            )
        )
        self.progression_certification_repository = (
            ProgressionCertificationRepository(
                study_find_repository.connection
            )
        )
        self.progression_attainment_repository = (
            ProgressionAttainmentRepository(
                study_find_repository.connection
            )
        )
        self.progression_regression_review_repository = (
            ProgressionRegressionReviewRepository(
                study_find_repository.connection
            )
        )
        self.summary_template_repository = SummaryTemplateRepository(
            study_find_repository.connection
        )
        self.summary_template_repository.ensure_defaults()

        self.setWindowTitle(window_title())
        # Give the cockpit enough initial working room on a desktop without
        # forcing maximized mode. The runtime remains scrollable on smaller displays.
        self.resize(1120, 760)

        self.trade_plan = build_default_trade_plan()
        self.context_capture_repository = ContextCaptureRepository(study_find_repository.connection)
        self.trade_plan_widget = TradePlanWidget(
            self.trade_plan,
            context_capture_repository=self.context_capture_repository,
            competency_assessment_repository=(
                self.competency_assessment_repository
            ),
            competency_evidence_repository=self.competency_evidence_repository,
            competency_development_direction_repository=(
                self.competency_development_direction_repository
            ),
            competency_cross_run_observation_repository=(
                self.competency_cross_run_observation_repository
            ),
            competency_evidence_maturity_repository=(
                self.competency_evidence_maturity_repository
            ),
            progression_certification_repository=(
                self.progression_certification_repository
            ),
            progression_attainment_repository=(
                self.progression_attainment_repository
            ),
            progression_regression_review_repository=(
                self.progression_regression_review_repository
            ),
        )
        # Backward-compatible references retained while Process Map tests and
        # callers transition to the Trade Plan parent model.
        self.process_blueprint = self.trade_plan.process_blueprint
        self.process_blueprint_widget = (
            self.trade_plan_widget.process_blueprint_widget
        )

        self.tda_workflow = TDAWorkflowWidget()
        self.study_find_widget = StudyFindWidget(
            self.summary_template_repository
        )
        self.trade_summary_widget = TradeSummaryWidget(
            self.summary_template_repository
        )
        self.study_find_review_widget = StudyFindReviewWidget(
            self.study_find_repository
        )
        self.summary_template_workbench_widget = (
            SummaryTemplateWorkbenchWidget(
                self.summary_template_repository
            )
        )
        self.summary_template_workbench_widget.template_published.connect(
            self._summary_template_published
        )

        self.tabs = QTabWidget()
        self.tabs.addTab(self.trade_plan_widget, "Trade Plan")
        self.tabs.addTab(self.tda_workflow, "Guided TDA")
        self.tabs.addTab(self.study_find_widget, "Study Find")
        self.tabs.addTab(self.trade_summary_widget, "Trade Summary")
        self.tabs.addTab(self.study_find_review_widget, "Study Review")
        self.tabs.addTab(
            self.summary_template_workbench_widget,
            "Workbench",
        )
        self.amdx_catalog_widget = AMDXMasterLabWidget(self.trading_session_run_repository.amdx.master)
        self.tabs.addTab(self.amdx_catalog_widget, "AMDX Lab")
        self.amdx_catalog_widget.set_active(False)
        self.tabs.currentChanged.connect(lambda _index: self.amdx_catalog_widget.set_active(
            self.tabs.currentWidget() is self.amdx_catalog_widget))
        self.setCentralWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._configure_feedback_actions()

        self.tda_workflow.tda_ready.connect(self.save_tda)
        self.study_find_widget.study_find_ready.connect(self.save_study_find)
        self.trade_summary_widget.trade_ready.connect(self.save_trade_record)
        self.trade_plan_widget.tda_station_runner_widget.session_changed.connect(
            self.save_tda_station_session
        )
        self.trade_plan_widget.trading_day_runtime_widget.session_changed.connect(
            self.save_trading_day_session
        )
        shell = self.trade_plan_widget.trading_day_shell_widget
        shell.calendar_repository = self.trading_session_run_repository.amdx
        shell.calendar_launch_context = self._save_calendar_launch_context
        shell.runtime.amdx_context_widget.set_repository(self.trading_session_run_repository.amdx)
        shell.runtime.amdx_context_widget.open_stack.connect(self._open_amdx_stack)
        shell.runtime.amdx_context_widget.recorded.connect(lambda _result: self.amdx_catalog_widget.refresh())
        self.amdx_catalog_widget.recorded.connect(lambda _result: shell._refresh_market_time_display())
        self.tabs.currentChanged.connect(lambda _index: shell.runtime.amdx_context_widget.set_active(
            self.tabs.currentWidget() is self.trade_plan_widget))
        shell.runtime.qt_context_widget.set_intraday_read_only(True)
        shell.runtime.post_market_review_widget.set_coupled_intraday(True)
        shell.trading_day_changed.connect(self.save_trading_day)
        shell.session_run_changed.connect(self.save_trading_session_run)

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

    def _summary_template_published(self, _kind: str) -> None:
        self.study_find_widget.refresh_summary_template_label()
        self.trade_summary_widget.refresh_summary_template_label()
        self.status_bar.showMessage(
            "Summary template revision published",
            3000,
        )

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
        if current_widget is self.amdx_catalog_widget:
            return tab_name, self.amdx_catalog_widget.catalog.id if self.amdx_catalog_widget.catalog else ""

        if current_widget is self.trade_summary_widget:
            return tab_name, self.trade_summary_widget.current_trade_id

        if current_widget is self.study_find_review_widget:
            row = self.study_find_review_widget.study_list.currentRow()
            if 0 <= row < len(self.study_find_review_widget.study_finds):
                study_find = self.study_find_review_widget.study_finds[row]
                return tab_name, study_find.id

        if current_widget is self.summary_template_workbench_widget:
            template = self.summary_template_workbench_widget.active_template
            if template is not None:
                return tab_name, (
                    f"{template.template_id}@r{template.revision}"
                )

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

        active_day = self.trading_day_repository.get_latest_active()
        if active_day is not None:
            runs = self.trading_session_run_repository.get_for_day(active_day.id)
            active_run = next(
                (run for run in runs if run.id == active_day.active_session_run_id),
                None,
            )
            process_session = None
            tda_session = None
            if active_run is not None:
                process_session = self.trading_day_session_repository.get_by_id(
                    active_run.process_session_id
                )
                if active_run.tda_station_session_id:
                    tda_session = self.tda_station_session_repository.get_by_id(
                        active_run.tda_station_session_id
                    )
            self.trade_plan_widget.trading_day_shell_widget.load_state(
                active_day,
                runs,
                process_session=process_session,
                tda_session=tda_session,
            )
            # Data restoration is only half of persistence. Put the operator
            # back at the runtime surface that owns the restored state.
            self.tabs.setCurrentWidget(self.trade_plan_widget)
            self.trade_plan_widget.focus_runtime()
            self.status_bar.showMessage("Restored active Trading Day", 3000)
        else:
            # Compatibility fallback for databases created before Session Runs
            # became the owner of process/TDA runtime records.
            latest_station_session = self.tda_station_session_repository.get_latest()
            if latest_station_session is not None:
                self.trade_plan_widget.tda_station_runner_widget.load_session(
                    latest_station_session
                )

            latest_trading_day_session = self.trading_day_session_repository.get_latest()
            if latest_trading_day_session is not None:
                self.trade_plan_widget.trading_day_runtime_widget.load_session(
                    latest_trading_day_session
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

    def save_tda_station_session(self, session) -> None:
        self.tda_station_session_repository.save(session)
        self.status_bar.showMessage("TDA station progress saved", 1200)

    def save_trading_day_session(self, session) -> None:
        self.trading_day_session_repository.save(session)
        self.status_bar.showMessage("Session process saved", 1200)

    def save_trading_day(self, trading_day) -> None:
        self.trading_day_repository.save(trading_day)
        self.status_bar.showMessage("Trading Day saved", 1200)

    def save_trading_session_run(self, session_run) -> None:
        from ict_cockpit.database.trading_session_run_repository import RUN_COLUMNS
        values = self.trading_session_run_repository._values_for_run(session_run)
        stored = self.trading_session_run_repository.connection.execute(
            "SELECT " + ",".join(RUN_COLUMNS) + " FROM trading_session_run WHERE id=?", (session_run.id,)).fetchone()
        if stored is None or tuple(stored) != values:
            self.trading_session_run_repository.save(session_run)
        self.competency_evidence_repository.replace_from_study_review(
            trade_plan_id=self.trade_plan.id,
            trading_run=session_run,
        )
        self.status_bar.showMessage(
            f"{session_run.session_name} Trading Run saved",
            1200,
        )

    def _save_calendar_launch_context(self):
        shell = self.trade_plan_widget.trading_day_shell_widget
        self.trading_day_repository.save(shell.trading_day)
        self.trading_day_session_repository.save(shell.runtime.session)
        self.tda_station_session_repository.save(shell.runtime.tda_station_runner_widget.session)

    def _open_amdx_stack(self, scope):
        if scope.get("capture") is not None:
            from ict_cockpit.gui.amdx_captured_stack_dialog import AMDXCapturedStackDialog
            dialog = AMDXCapturedStackDialog(scope["capture"], self.trading_session_run_repository.amdx, self)
            dialog.exec()
            return
        pane = self.amdx_catalog_widget
        if scope["instrument"] != pane.instrument:
            self.status_bar.showMessage("The current native Lab is configured for MNQ; another instrument is not substituted.", 5000)
            return
        pane.run_scope = None
        pane.channel_selector.setCurrentText("Expected")
        pane.set_reference(scope["reference"])
        run = self.trade_plan_widget.trading_day_shell_widget.active_trading_run
        if run is not None and run.id == scope.get("run_id"):
            pane.inspect_run(run.id)
            pane.capture_selector.setCurrentIndex(int(run.environment.value in ("Live", "Forward Test")))
        self.tabs.setCurrentWidget(pane)

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
