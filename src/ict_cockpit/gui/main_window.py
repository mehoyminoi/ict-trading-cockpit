import sqlite3
import json
from dataclasses import asdict
from pathlib import Path

from PySide6.QtCore import QByteArray, QSettings, QTimer, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QPushButton,
    QLabel,
    QScrollArea,
    QHBoxLayout,
    QMenu,
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
from ict_cockpit.gui.study_home_widget import StudyHomeWidget
from ict_cockpit.gui.integrated_study_task_widget import IntegratedStudyTaskWidget
from ict_cockpit.database.study_investigation_repository import StudyInvestigationRepository, describe_association
from ict_cockpit.gui.contextual_study_find_dock import ContextualStudyFindDock
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

        database_path = next(
            (row[2] for row in study_find_repository.connection.execute("PRAGMA database_list") if row[1] == "main"),
            "",
        )
        self.workspace_settings = (
            QSettings(
                str(Path(database_path).with_name(Path(database_path).name + ".workspace.ini")),
                QSettings.Format.IniFormat,
            )
            if database_path
            else None
        )

        self.setWindowTitle(window_title())
        # Give the cockpit enough initial working room on a desktop without
        # forcing maximized mode. The runtime remains scrollable on smaller displays.
        self.resize(1120, 760)

        self.trade_plan = build_default_trade_plan()
        self.context_capture_repository = ContextCaptureRepository(study_find_repository.connection)
        self.trade_plan_widget = TradePlanWidget(
            self.trade_plan,
            workspace_settings=self.workspace_settings,
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

        self.trade_plan_widget.tda_station_runner_widget.configure_workspace_settings(self.workspace_settings)
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
        self.integrated_study_task = IntegratedStudyTaskWidget(
            plan_id=self.trade_plan.id, revision=self.trade_plan.revision,
            settings=self.workspace_settings,
        )
        self.amdx_catalog_widget.layout().insertWidget(1, self.integrated_study_task)
        self.integrated_study_task.capture_requested.connect(self._open_investigation_capture)
        self.integrated_study_task.review_requested.connect(self._open_investigation_review)
        self.integrated_study_task.criteria_requested.connect(self._open_study_criteria)
        self.integrated_study_task.overview_requested.connect(self._open_investigation_overview)
        self.integrated_study_task.evaluation_requested.connect(self._open_criterion_study)
        self.investigation_return_buttons = []
        self.investigation_context_labels = []
        self.pending_investigation_context = None
        self.capture_context_defaults = None
        for destination in (self.study_find_widget, self.study_find_review_widget):
            button = QPushButton("Return to AMDX investigation")
            button.setToolTip("Return without saving, completing, or changing the current investigation.")
            button.hide()
            button.clicked.connect(lambda: self.tabs.setCurrentWidget(self.amdx_catalog_widget))
            context = QLabel()
            context.setWordWrap(True)
            context.hide()
            destination.layout().insertWidget(0, context)
            destination.layout().insertWidget(0, button)
            self.investigation_context_labels.append(context)
            self.investigation_return_buttons.append(button)
        self.tabs.addTab(self.amdx_catalog_widget, "AMDX Lab")
        self.investigation_repository = StudyInvestigationRepository(study_find_repository.connection)
        self.link_investigation_action = QAction("Link capture only (do not save content)", self)
        self.link_investigation_action.triggered.connect(self._link_investigation_capture)
        self.capture_association_label = QLabel()
        self.capture_association_label.setWordWrap(True)
        save_layout = self.study_find_widget.layout()
        save_index = save_layout.indexOf(self.study_find_widget.save_feedback)
        self.study_save_destination = QLabel()
        self.study_save_destination.setTextFormat(Qt.TextFormat.PlainText)
        self.study_save_destination.setWordWrap(True)
        save_layout.insertWidget(save_index, self.study_save_destination)
        save_layout.insertWidget(save_index + 1, self.capture_association_label)
        save_layout.removeWidget(self.study_find_widget.save_button)
        save_row = QHBoxLayout()
        self.save_to_investigation_button = QPushButton("Save to investigation")
        self.save_to_investigation_button.clicked.connect(self._save_to_investigation)
        save_row.addWidget(self.save_to_investigation_button)
        save_row.addWidget(self.study_find_widget.save_button)
        self.study_save_more = QPushButton("More…")
        save_menu = QMenu(self.study_save_more)
        save_menu.addAction(self.link_investigation_action)
        self.study_save_more.setMenu(save_menu)
        save_row.addWidget(self.study_save_more)
        save_layout.insertLayout(save_layout.indexOf(self.study_find_widget.save_feedback) + 1, save_row)
        self.study_find_widget.draft_changed.connect(lambda _draft: self._refresh_capture_association())
        self.study_find_widget.draft_changed.connect(lambda _draft: self._refresh_capture_context())
        self.capture_context_notice = QLabel()
        self.capture_context_notice.setWordWrap(True)
        self.study_find_widget.layout().insertWidget(3, self.capture_context_notice)
        self.keep_study_question_button = QPushButton("Keep question for later")
        self.keep_study_question_button.setToolTip("Save selected Notes or Observation directly; without a selection, write a question.")
        self.question_capture_feedback = QLabel()
        self.question_capture_feedback.setWordWrap(True)
        self.study_find_widget.layout().insertWidget(4, self.question_capture_feedback)
        self._question_selection_editor = None
        self._quick_question_pending = None
        for editor in (self.study_find_widget.notes_input, self.study_find_widget.observation_input):
            editor.selectionChanged.connect(lambda editor=editor: self._remember_question_selection(editor))
        self.keep_study_question_button.clicked.connect(lambda: self._open_study_questions(capture=True))
        self.study_find_widget.layout().insertWidget(4, self.keep_study_question_button)
        self.keep_study_finding_button = QPushButton("Keep finding…")
        self.keep_study_finding_button.setToolTip("Retain an insight or partial answer; selected Notes or Observation prefill the wording.")
        self.keep_study_finding_button.clicked.connect(lambda: self._open_study_findings(capture=True))
        self.study_find_widget.layout().insertWidget(5, self.keep_study_finding_button)
        self.discard_study_draft_button = QPushButton("Discard current draft…")
        self.discard_study_draft_button.clicked.connect(self._discard_study_draft)
        self.study_find_widget.layout().addWidget(self.discard_study_draft_button)

        self.study_questions_button = QPushButton("Study questions…")
        self.study_questions_button.clicked.connect(lambda: self._open_study_questions(capture=False))
        self.integrated_study_task.layout().addWidget(self.study_questions_button)
        self.study_findings_button = QPushButton("Study findings…")
        self.study_findings_button.clicked.connect(lambda: self._open_study_findings(capture=False))
        self.integrated_study_task.layout().addWidget(self.study_findings_button)
        definition = QLabel(
            f"Published AMDX criteria · Trade Plan {self.trade_plan.revision}: not configured. "
            "Quarter choices below enforce structural AMDX/XAMD legality; they do not classify price action."
        )
        definition.setWordWrap(True)
        self.amdx_catalog_widget.layout().insertWidget(2, definition)
        self.amdx_catalog_widget.set_active(False)
        self.tabs.currentChanged.connect(lambda _index: self.amdx_catalog_widget.set_active(
            self.tabs.currentWidget() is self.amdx_catalog_widget))
        self.workspace_scroll = QScrollArea()
        self.workspace_scroll.setWidgetResizable(True)
        self.workspace_scroll.setWidget(self.tabs)
        self.setCentralWidget(self.workspace_scroll)

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
        self.contextual_study_find_dock = ContextualStudyFindDock(
            self.study_find_widget,
            settings=self.workspace_settings,
        )
        shell.contextual_study_find_requested.connect(
            self._toggle_contextual_study_find
        )
        shell.contextual_study_find_dismiss_requested.connect(
            self._dismiss_contextual_study_find
        )
        self.contextual_study_find_dock.dismissed.connect(
            self.save_pending_study_find_draft
        )
        self.tabs.currentChanged.connect(
            lambda _index: self._sync_contextual_study_find_context()
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
        self.study_home_widget = StudyHomeWidget(self.trade_plan.competencies)
        self.tabs.addTab(self.study_home_widget, "Study")
        self.study_home_widget.study_requested.connect(self._stage_home_study)
        self.study_home_widget.resume_requested.connect(self._resume_home_run)
        self.study_home_widget.capture_requested.connect(
            lambda: self.tabs.setCurrentWidget(self.study_find_widget)
        )
        self.study_home_widget.calendar_requested.connect(
            lambda: self.tabs.setCurrentWidget(self.amdx_catalog_widget)
        )
        self.tabs.currentChanged.connect(lambda _index: self._refresh_study_home())
        self._refresh_study_save_destination()
        self._refresh_study_home()
        if shell.active_trading_run is None:
            self.tabs.setCurrentWidget(self.study_home_widget)
        self._restore_workspace_layout()
        self.study_find_review_widget.splitter.splitterMoved.connect(self._save_review_layout)

    def _remember_question_selection(self, editor):
        if editor.textCursor().hasSelection():
            self._question_selection_editor = editor
            self.question_capture_feedback.clear()

    def _study_capture_snapshot(self):
        widget = self.study_find_widget
        draft = widget.build_draft()
        editor = self._question_selection_editor
        selected = editor.textCursor().selectedText().replace("\u2029", "\n") if editor else ""
        source = dict(capture_id=draft.id,
                      state="Unfinished capture" if widget.save_button.isEnabled() else "Saved Study Find",
                      date=draft.observation_date.isoformat(), instrument=draft.instrument,
                      session=draft.session, pattern=draft.pattern_name,
                      observation=draft.observation, notes=draft.notes,
                      images=list(draft.image_paths),
                      association=self.investigation_repository.get(draft.id))
        return source, selected

    def _open_study_questions(self, *, capture=False):
        from ict_cockpit.database.study_question_repository import StudyQuestionRepository
        from ict_cockpit.gui.study_question_dialog import StudyQuestionDialog
        source = None
        selected = ""
        if capture:
            source, selected = self._study_capture_snapshot()
        repository = StudyQuestionRepository(self.study_find_repository.connection)
        if capture and selected.strip():
            from datetime import datetime, timezone
            from uuid import uuid4
            item = dict(version=1, id=str(uuid4()), plan_id=self.trade_plan.id,
                        plan_revision=self.trade_plan.revision, question=selected.strip(),
                        original_text=selected, source=source,
                        recorded_at=datetime.now(timezone.utc).isoformat())
            previous = self._quick_question_pending
            if previous is not None and all(previous[k] == item[k]
                    for k in item if k not in ('id', 'recorded_at')):
                item = previous
            self._quick_question_pending = item
            try:
                repository.save(item)
            except (ValueError, RuntimeError, sqlite3.Error) as error:
                self.question_capture_feedback.setText(f"Question not saved: {error}. Selection retained; try again.")
                return
            self.question_capture_feedback.setText("Question kept. Continue here; find it later in Study questions.")
            return
        dialog = StudyQuestionDialog(
            repository,
            plan_id=self.trade_plan.id, plan_revision=self.trade_plan.revision,
            source=source, original_text=selected, parent=self)
        dialog.exec()

    def _open_study_findings(self, *, capture=False):
        from ict_cockpit.database.study_finding_repository import StudyFindingRepository
        from ict_cockpit.gui.study_finding_dialog import StudyFindingDialog
        source, selected, destination = None, "", None
        try:
            if capture:
                source, selected = self._study_capture_snapshot()
                source["navigation_context"] = self.pending_investigation_context
                # A saved capture association wins over newer navigation context.
                destination = source.get("association") or self.pending_investigation_context
                if destination and not destination.get("question", "").strip():
                    destination = None
            dialog = StudyFindingDialog(
                StudyFindingRepository(self.study_find_repository.connection),
                plan_id=self.trade_plan.id, plan_revision=self.trade_plan.revision,
                source=source, original_text=selected, destination=destination, parent=self)
            dialog.exec()
        except (ValueError, sqlite3.Error) as error:
            self.question_capture_feedback.setText(f"Could not open findings: {error}. Your capture remains here.")

    def _open_investigation_overview(self):
        from ict_cockpit.gui.study_investigation_overview import StudyInvestigationOverview
        from ict_cockpit.database.study_criterion_repository import StudyCriterionRepository
        dialog = StudyInvestigationOverview(
            self.investigation_repository,
            StudyCriterionRepository(self.trading_session_run_repository.amdx),
            self.study_find_review_widget.repository,
            task_id=self.integrated_study_task.task_id, plan_id=self.trade_plan.id,
            question=self.integrated_study_task.question.text(), parent=self)
        dialog.exec()

    def _open_criterion_study(self):
        from ict_cockpit.gui.study_criterion_dialog import StudyCriterionDialog
        from ict_cockpit.database.study_criterion_repository import StudyCriterionRepository
        target = self.amdx_catalog_widget.target
        if target is None or self.amdx_catalog_widget._read_error:
            self.status_bar.showMessage("Select a quarter in the Study calendar first.", 8000)
            return
        dialog = StudyCriterionDialog(
            StudyCriterionRepository(self.trading_session_run_repository.amdx),
            task_id=self.integrated_study_task.task_id, plan_id=self.trade_plan.id,
            plan_revision=self.trade_plan.revision, question=self.integrated_study_task.question.text(),
            instrument=target.instrument, cycle=target.cycle, reference=target.market_reference, parent=self,
        )
        dialog.exec()

    def _open_study_criteria(self):
        from ict_cockpit.gui.amdx_criteria_dialog import AMDXCriteriaDialog
        target = self.amdx_catalog_widget.target
        if target is None or self.amdx_catalog_widget._read_error:
            self.status_bar.showMessage("Select a quarter in the Study calendar before opening criteria.", 8000)
            return
        dialog = AMDXCriteriaDialog(
            self.trading_session_run_repository.amdx.definitions,
            plan_revision=self.trade_plan.revision, cycle=target.cycle,
            instrument=target.instrument, reference=target.market_reference, parent=self,
        )
        dialog.exec()

    def _restore_workspace_layout(self):
        if self.workspace_settings is None:
            return
        geometry = self.workspace_settings.value("workspace-window/geometry-v1")
        if isinstance(geometry, QByteArray):
            self.restoreGeometry(geometry)
        divider = self.workspace_settings.value("study-review/splitter-v1")
        if isinstance(divider, QByteArray):
            self.study_find_review_widget.splitter.restoreState(divider)

    def _save_review_layout(self, *_args):
        if self.workspace_settings is not None:
            self.workspace_settings.setValue("study-review/splitter-v1", self.study_find_review_widget.splitter.saveState())
            self.workspace_settings.sync()

    def closeEvent(self, event):
        if self.workspace_settings is not None:
            self.workspace_settings.setValue("workspace-window/geometry-v1", self.saveGeometry())
            if self.study_find_review_widget.isVisible():
                self._save_review_layout()
            self.workspace_settings.sync()
        super().closeEvent(event)


    def _refresh_capture_association(self):
        self.capture_association_label.setText(describe_association(
            self.investigation_repository.get(self.study_find_widget.current_study_find_id)))
        self._refresh_study_save_destination()

    def _study_save_target(self):
        existing = self.investigation_repository.get(self.study_find_widget.current_study_find_id)
        target = existing or self.pending_investigation_context
        if target is None:
            return None
        keys = ('task_id', 'plan_id', 'plan_revision', 'question', 'instrument',
                'market_reference', 'interpretation')
        return {key: target[key] for key in keys}

    def _refresh_study_save_destination(self):
        source = self.study_find_widget
        try:
            existing = self.investigation_repository.get(source.current_study_find_id)
            target = self._study_save_target()
        except (ValueError, sqlite3.Error) as error:
            self.study_save_destination.setText(f"Destination unavailable: {error}")
            self.save_to_investigation_button.setEnabled(False)
            return
        if target:
            prefix = "Existing association (preserved)" if existing else "Save destination"
            self.study_save_destination.setText(
                f"{prefix}: {target['question'] or '(enter an investigation question first)'}\n"
                f"{target['instrument']} · {target['market_reference']} · {target['interpretation']}\n"
                "Save to investigation retains the content and association together. "
                "Plain Save Study Find adds no new association; an existing one remains.")
        else:
            self.study_save_destination.setText(
                "No investigation destination. Save Study Find keeps this capture independently. "
                "Open capture from an investigation to choose a destination.")
        self.save_to_investigation_button.setEnabled(bool(target and target['question'].strip())
            and source.save_button.isEnabled() and self.amdx_catalog_widget.run_scope is None)
        self.link_investigation_action.setEnabled(bool(target and target['question'].strip()))

    def _save_to_investigation(self):
        from datetime import datetime
        from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
        source = self.study_find_widget
        if not source.save_button.isEnabled():
            return
        try:
            if self.amdx_catalog_widget.run_scope is not None:
                raise ValueError("Return to the independent Study calendar before saving to an investigation")
            target = self._study_save_target()
            if target is None:
                raise ValueError("Open capture from an investigation first")
            captured = source.build_study_find()
            images = tuple(source.image_paths)
            reference = datetime.fromisoformat(target['market_reference'])
            if reference.tzinfo is None or reference.utcoffset() is None:
                raise ValueError("Historical reference requires a timezone")
            differences = []
            reference_date = reference.astimezone(MARKET_TIMEZONE).date()
            if captured.observation_date != reference_date:
                differences.append(f"Date: capture {captured.observation_date} / destination {reference_date}")
            if captured.instrument != target['instrument'].strip().upper():
                differences.append(f"Instrument: capture {captured.instrument} / destination {target['instrument']}")
            # Session is an inspected-quarter suggestion, not inferred from clock time.
            existing = self.investigation_repository.get(captured.id)
            defaults = self.capture_context_defaults or {}
            if not existing and defaults.get('session') and captured.session != defaults['session']:
                differences.append(f"Session: capture {captured.session} / inspected {defaults['session']}")
            if differences:
                answer = QMessageBox.question(self, "Check capture and destination",
                    "\n".join(differences) + f"\n\nInvestigation: {target['question']}\n"
                    "Save with these differences? The entered capture values will be retained.",
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Cancel)
                if answer != QMessageBox.StandardButton.Save:
                    source.save_feedback.setText("Not saved. Check the capture or destination; your input remains here.")
                    return
                if (captured != source.build_study_find() or images != tuple(source.image_paths)
                        or target != self._study_save_target()):
                    raise ValueError("Capture or destination changed while confirming; inspect it and try again")
            self._persist_study_find(captured, investigation=target)
        except (ValueError, RuntimeError, sqlite3.Error) as error:
            source.save_feedback.setText(f"Not saved: {error}. Your input remains here.")

    def _link_investigation_capture(self):
        pane = self.amdx_catalog_widget
        try:
            if pane.run_scope is not None:
                raise ValueError("Return to Study calendar before linking an independent investigation")
            draft = self.study_find_widget.build_draft()
            if draft.has_content() and self.study_find_widget.save_button.isEnabled():
                self.study_find_repository.save_draft(draft)
            context = self._study_save_target()
            if context is None:
                raise ValueError("Open Study Find from the investigation before linking")
            self.investigation_repository.link(
                self.study_find_widget.current_study_find_id, **context)
            self._refresh_capture_association()
        except (ValueError, sqlite3.Error) as exc:
            self.capture_association_label.setText(f"Link not saved: {exc}")

    def _show_investigation_context(self, index):
        pane = self.amdx_catalog_widget
        try:
            reference = pane.reference().isoformat()
        except ValueError:
            reference = "Invalid historical reference; correct it in the calendar"
        if index == 0:
            self.pending_investigation_context = dict(
                task_id=self.integrated_study_task.task_id,
                plan_id=self.trade_plan.id, plan_revision=self.trade_plan.revision,
                question=self.integrated_study_task.question.text(), instrument=pane.instrument,
                market_reference=reference, interpretation=pane.channel_selector.currentText(),
            )
        label = self.investigation_context_labels[index]
        label.setText(
            f"Investigation: {self.integrated_study_task.question.text() or 'No question entered'}\n"
            f"{pane.instrument} · {reference} · {pane.channel_selector.currentText()}\n"
            "Navigation context only; not a saved link to this capture or evidence."
        )
        label.show()
        self.investigation_return_buttons[index].show()

    def _refresh_capture_context(self):
        defaults = self.capture_context_defaults
        if not defaults:
            return
        draft = self.study_find_widget.build_draft()
        differences = []
        for name, actual, suggested in (
            ("date", draft.observation_date.isoformat(), defaults["observation_date"].isoformat()),
            ("instrument", draft.instrument, defaults["instrument"]),
            ("session", draft.session, defaults["session"]),
        ):
            if suggested and actual != suggested:
                differences.append(f"{name}: capture {actual or '(empty)'} / selected context {suggested}")
        self.capture_context_notice.setText(
            "Capture context differs — " + "; ".join(differences) +
            ". Your entry is preserved; check before saving or linking."
            if differences else
            "Capture matches the opening context. Date is the selected New York calendar date; "
            "session follows the inspected quarter where known. Fields remain editable.")

    def _capture_draft_fingerprint(self):
        return json.dumps(asdict(self.study_find_widget.build_draft()), sort_keys=True, default=str)

    def _remember_discard_seed(self):
        self._discard_seed = self._capture_draft_fingerprint()
        if self.workspace_settings is not None:
            self.workspace_settings.setValue("study-capture/discard-seed-v1", self._discard_seed)
            self.workspace_settings.sync()

    def _untouched_discard_seed(self):
        seed = getattr(self, "_discard_seed", None)
        if seed is None and self.workspace_settings is not None:
            seed = self.workspace_settings.value("study-capture/discard-seed-v1", "")
        return bool(seed) and seed == self._capture_draft_fingerprint()

    def _open_investigation_capture(self):
        from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
        pane = self.amdx_catalog_widget
        try:
            reference = pane.reference().astimezone(MARKET_TIMEZONE)
            if pane._read_error or pane.run_scope is not None:
                raise ValueError("Return to a valid independent Study calendar before opening capture.")
        except ValueError as error:
            self.status_bar.showMessage(str(error), 10000)
            return
        session = ""
        target = pane.target
        if target is not None and target.cycle.layer == "day":
            session = next(q.label for q in target.cycle.quarters if q.id == target.quarter_id)
        elif target is not None and target.cycle.layer == "session":
            session = next((q.label for row in pane.projection.cycles
                            if row.context.cycle.layer == "day"
                            for q in row.context.cycle.quarters
                            if q.id == target.cycle.parent_quarter_id), "")
        self.capture_context_defaults = dict(
            observation_date=reference.date(), instrument=pane.instrument, session=session)
        source = self.study_find_widget
        if not source.save_button.isEnabled():
            # Saved material remains in Review; never clear an unfinished draft.
            source._loading_draft = True
            try:
                source.reset_form()
            finally:
                source._loading_draft = False
        if source.save_button.isEnabled() and self._untouched_discard_seed():
            # Discard's carried context is still only a suggestion, not an authored draft.
            blocked = source.blockSignals(True)
            try:
                source.instrument_input.clear()
                source.session_input.clear()
                source.apply_context_defaults(**self.capture_context_defaults)
            finally:
                source.blockSignals(blocked)
            self._remember_discard_seed()
            source.emit_draft_changed()
        else:
            source.apply_context_defaults(**self.capture_context_defaults)
        self._show_investigation_context(0)
        self._refresh_capture_association()
        self._refresh_capture_context()
        self.tabs.setCurrentWidget(source)

    def _open_investigation_review(self):
        self._show_investigation_context(1)
        self.study_find_review_widget.refresh()
        self.tabs.setCurrentWidget(self.study_find_review_widget)

    def _refresh_study_home(self):
        if self.tabs.currentWidget() is not self.study_home_widget:
            return
        shell = self.trade_plan_widget.trading_day_shell_widget
        source = self.study_find_widget
        has_draft = bool(source.pattern_input.text().strip()
                         or source.observation_input.toPlainText().strip()
                         or source.notes_input.toPlainText().strip()
                         or self.study_find_repository.get_latest_draft())
        self.study_home_widget.refresh(
            run=shell.active_trading_run,
            mode_name=shell.runtime.current_mode.name,
            directions=self.competency_development_direction_repository.list_for_plan(self.trade_plan.id),
            revision=self.trade_plan.revision,
            has_draft=has_draft,
        )

    def _resume_home_run(self):
        self.tabs.setCurrentWidget(self.trade_plan_widget)
        self.trade_plan_widget.focus_runtime()

    def _stage_home_study(self, competency_id):
        plan = self.trade_plan_widget
        if plan.trading_day_shell_widget.active_trading_run is not None:
            self._refresh_study_home()
            return
        if not plan.process_run_launcher_widget.prepare_targeted_study(competency_id):
            return
        self.tabs.setCurrentWidget(plan)
        plan.section_list.setCurrentRow(plan._section_ids.index("review-development"))
        plan.competency_evidence_review_widget.select_work_area("practice")
        plan.process_run_launcher_widget.study_question_input.setFocus()

    def _toggle_contextual_study_find(self, basis) -> None:
        shell = self.trade_plan_widget.trading_day_shell_widget
        if (
            self.tabs.currentWidget() is not self.trade_plan_widget
            or shell.active_trading_run is None
            or shell.runtime.current_mode.id != "live-watch"
        ):
            return
        if self.contextual_study_find_dock.isVisible():
            self.contextual_study_find_dock.dismiss()
            return
        self.contextual_study_find_dock.open_for(
            shell.study_find_button,
            basis,
        )

    def _dismiss_contextual_study_find(self) -> None:
        if self.contextual_study_find_dock.isVisible():
            self.contextual_study_find_dock.dismiss()

    def _sync_contextual_study_find_context(self) -> None:
        if (
            self.tabs.currentWidget() is not self.trade_plan_widget
            and self.contextual_study_find_dock.isVisible()
        ):
            self.contextual_study_find_dock.dismiss()

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
        if scope.get("review_run_id") is not None:
            from ict_cockpit.gui.amdx_review_stack_dialog import AMDXReviewStackDialog
            shell = self.trade_plan_widget.trading_day_shell_widget
            run_id = scope["review_run_id"]
            def allowed():
                run = shell.active_trading_run
                return (run is not None and run.id == run_id and shell.runtime.current_mode.id == "post-market"
                    and self.tabs.currentWidget() is self.trade_plan_widget)
            if not allowed():
                return
            try:
                dialog = AMDXReviewStackDialog(self.trading_session_run_repository.amdx, run_id, self, allowed=allowed)
                def update_active(_index):
                    dialog.pane.set_active(allowed())
                self.tabs.currentChanged.connect(update_active)
                try:
                    dialog.exec()
                finally:
                    self.tabs.currentChanged.disconnect(update_active)
                    dialog.pane.set_active(False)
                    dialog.deleteLater()
                shell._refresh_market_time_display()
            except (ValueError, TypeError, sqlite3.Error, RuntimeError) as error:
                self.status_bar.showMessage(f"Higher Review unavailable: {error}", 6000)
            return
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

    def _discard_study_draft(self):
        source = self.study_find_widget
        if not source.save_button.isEnabled():
            source.save_feedback.setText("This Study Find is saved. Use Start New Study Find; saved records are not discarded here.")
            return
        identity = source.current_study_find_id
        answer = QMessageBox.question(
            self, "Discard current Study Find draft?",
            "Discard this unfinished capture's pattern, observation, notes and attachment list? "
            "Date, instrument and session will stay as starting context. Saved finds, queued questions "
            "and their source records will remain. This cannot be undone.",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)
        if answer != QMessageBox.StandardButton.Discard:
            return
        # The confirmation can process events; recheck identity/state before mutation.
        if source.current_study_find_id != identity or not source.save_button.isEnabled():
            source.save_feedback.setText("Draft changed while confirming. Nothing discarded; inspect it and try again.")
            return
        draft = source.build_draft()
        pending = self.pending_study_find_draft
        was_active = self.study_find_draft_save_timer.isActive()
        self.study_find_draft_save_timer.stop()
        try:
            if self.study_find_repository.get_by_id(identity) is not None:
                raise ValueError("This identity belongs to a saved Study Find")
            self.study_find_repository.delete_draft(identity)
        except (ValueError, sqlite3.Error) as error:
            self.pending_study_find_draft = pending
            if was_active:
                self.study_find_draft_save_timer.start()
            source.save_feedback.setText(f"Draft not discarded: {error}. Your input remains here.")
            return
        self.pending_study_find_draft = None
        blocked = source.blockSignals(True)
        source._loading_draft = True
        try:
            source.reset_form()
            source.apply_context_defaults(observation_date=draft.observation_date,
                                          instrument=draft.instrument, session=draft.session)
        finally:
            source._loading_draft = False
            source.blockSignals(blocked)
        self._remember_discard_seed()
        # Sync other projections once, only after the new identity is complete.
        source.emit_draft_changed()
        self._quick_question_pending = None
        self._question_selection_editor = None
        self.question_capture_feedback.clear()
        source.save_feedback.setText("Draft discarded. Fresh capture ready with the same date, instrument and session.")

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
        self._persist_study_find(study_find)

    def _persist_study_find(self, study_find, *, investigation=None) -> bool:
        timer_active = self.study_find_draft_save_timer.isActive()
        self.study_find_draft_save_timer.stop()
        try:
            self.study_find_repository.save_capture(
                study_find, self.study_find_widget.image_paths, investigation=investigation)
        except (ValueError, RuntimeError, sqlite3.Error) as error:
            if timer_active:
                self.study_find_draft_save_timer.start()
            self.study_find_widget.save_feedback.setText(f"Not saved: {error}. Your input remains here.")
            self.study_find_widget.submission_failed.emit(str(error))
            return False
        self.pending_study_find_draft = None
        self.study_find_widget.mark_saved()
        message = "Study Find saved to investigation." if investigation else "Study Find saved."
        self.study_find_widget.save_feedback.setText(message)
        self.status_bar.showMessage(message, 3000)
        self.contextual_study_find_dock.notify_saved(study_find.id)
        try:
            self._refresh_capture_association()
            self.study_find_review_widget.refresh()
        except (ValueError, sqlite3.Error) as error:
            self.study_find_widget.save_feedback.setText(f"{message} Review refresh failed: {error}. Reopen review to inspect.")
        return True

    def save_trade_record(self, trade) -> None:
        self.trade_draft_save_timer.stop()
        self.pending_trade_draft = None

        self.trade_record_repository.save(trade)
        for image_path in self.trade_summary_widget.image_paths:
            self.trade_record_repository.add_image(trade.id, image_path)

        self.trade_record_repository.delete_draft(trade.id)
        self.trade_summary_widget.mark_saved()
        self.status_bar.showMessage("Trade Summary saved", 3000)
