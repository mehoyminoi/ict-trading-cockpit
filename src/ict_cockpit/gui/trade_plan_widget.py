from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
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
from ict_cockpit.gui.competency_evidence_review_widget import (
    CompetencyEvidenceReviewWidget,
)
from ict_cockpit.gui.process_blueprint_widget import ProcessBlueprintWidget
from ict_cockpit.gui.process_run_launcher_widget import ProcessRunLauncherWidget
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget
from ict_cockpit.trade_plan import (
    PlaybookDefinition,
    TradePlanDefinition,
    TradePlanSectionDefinition,
)


class TradePlanWidget(QWidget):
    """Alpha shell for the trading system and its executable process."""

    def __init__(
        self,
        trade_plan: TradePlanDefinition,
        competency_evidence_repository: CompetencyEvidenceRepository | None = None,
        competency_development_direction_repository:
            CompetencyDevelopmentDirectionRepository | None = None,
        competency_cross_run_observation_repository:
            CompetencyCrossRunObservationRepository | None = None,
        competency_evidence_maturity_repository:
            CompetencyEvidenceMaturityRepository | None = None,
    ) -> None:
        super().__init__()
        self.trade_plan = trade_plan
        self.competency_evidence_repository = competency_evidence_repository
        self.competency_development_direction_repository = (
            competency_development_direction_repository
        )
        self.competency_cross_run_observation_repository = (
            competency_cross_run_observation_repository
        )
        self.competency_evidence_maturity_repository = (
            competency_evidence_maturity_repository
        )
        self.competency_evidence_review_widget = None

        self.title_label = QLabel(f"{trade_plan.name} — {trade_plan.revision}")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")

        self.subtitle_label = QLabel(
            "Define the plan, execute the plan, observe the execution, learn from it, revise the plan."
        )
        self.subtitle_label.setWordWrap(True)

        self.operating_model_label = QLabel(
            "Foundation + Rules / Safety define the system. Playbooks define valid methods. "
            "Process operates the trading day. Review / Development improves the system and "
            "may be entered directly for Film Night, Lab, backtesting, or revision work."
        )
        self.operating_model_label.setWordWrap(True)
        self.operating_model_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.operating_model_label.setContentsMargins(10, 8, 10, 8)

        self.section_list = QListWidget()
        self.section_list.setMaximumWidth(220)

        self.stack = QStackedWidget()
        self.process_blueprint_widget = ProcessBlueprintWidget(
            trade_plan.process_blueprint
        )
        self.trading_day_shell_widget = TradingDayShellWidget(
            trade_plan.process_blueprint,
            live_watch_policy=trade_plan.live_watch_policy,
            playbooks=trade_plan.playbooks,
            authorization_gates=trade_plan.authorization_gates,
            trade_plan_revision=trade_plan.revision,
        )

        self.trading_day_runtime_widget = self.trading_day_shell_widget.runtime
        self.tda_station_runner_widget = (
            self.trading_day_runtime_widget.tda_station_runner_widget
        )

        self.process_tabs = QTabWidget()
        self.process_tabs.addTab(self.process_blueprint_widget, "Process Map")
        self.process_tabs.addTab(self.trading_day_shell_widget, "Run Trading Day")
        self.process_tabs.currentChanged.connect(self._process_tab_changed)

        self.process_run_launcher_widget = ProcessRunLauncherWidget(
            self.trading_day_shell_widget,
            trade_plan_revision=trade_plan.revision,
            competencies=trade_plan.competencies,
            on_launched=self.focus_runtime,
        )

        self._section_ids: list[str] = []
        for section in trade_plan.sections:
            self._section_ids.append(section.id)
            self.section_list.addItem(QListWidgetItem(section.name))
            if section.id == "process":
                page = self.process_tabs
            elif section.id == "playbooks":
                page = self._build_playbooks_page(section)
            elif section.id == "review-development":
                page = self._build_review_development_page(section)
            else:
                page = self._build_section_page(section)
            self.stack.addWidget(page)

        self.section_list.currentRowChanged.connect(self._section_changed)
        self.section_list.setCurrentRow(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(6)
        body.addWidget(self.section_list)
        body.addWidget(self.stack, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(5)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.operating_model_label)
        layout.addLayout(body)

    def _section_changed(self, row: int) -> None:
        self.stack.setCurrentIndex(row)
        if (
            self.selected_section_id == "review-development"
            and self.competency_evidence_review_widget is not None
        ):
            self.competency_evidence_review_widget.refresh()
        process_active = self.selected_section_id == "process"
        self.title_label.setVisible(not process_active)
        self.subtitle_label.setVisible(not process_active)
        self.operating_model_label.setVisible(not process_active)

    def _process_tab_changed(self, _index: int) -> None:
        if self.process_tabs.currentWidget() is self.trading_day_shell_widget:
            self.trading_day_shell_widget.ensure_primary_trading_run_started()

    def focus_runtime(self) -> None:
        try:
            process_row = self._section_ids.index("process")
        except ValueError:
            return
        self.section_list.setCurrentRow(process_row)
        self.process_tabs.setCurrentWidget(self.trading_day_shell_widget)

    def _prepare_targeted_study(self, competency_id: str) -> None:
        if self.process_run_launcher_widget.prepare_targeted_study(competency_id):
            self.process_run_launcher_widget.study_question_input.setFocus()

    def _build_section_page(self, section: TradePlanSectionDefinition) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        heading = QLabel(section.name)
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(heading)
        purpose = QLabel(section.purpose)
        purpose.setWordWrap(True)
        layout.addWidget(purpose)
        layout.addSpacing(12)
        topics_heading = QLabel("Current scope")
        topics_heading.setStyleSheet("font-weight: 600;")
        layout.addWidget(topics_heading)
        for topic in section.topics:
            label = QLabel(f"• {topic}")
            label.setWordWrap(True)
            layout.addWidget(label)
        layout.addStretch()
        return page

    def _build_review_development_page(
        self, section: TradePlanSectionDefinition
    ) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        heading = QLabel(section.name)
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(heading)

        purpose = QLabel(section.purpose)
        purpose.setWordWrap(True)
        layout.addWidget(purpose)

        competency_summary = QLabel(
            f"Competency catalog · {len(self.trade_plan.competencies)} "
            "plan-owned mechanic(s) available for targeted study."
        )
        competency_summary.setWordWrap(True)
        competency_summary.setFrameShape(QFrame.Shape.StyledPanel)
        competency_summary.setContentsMargins(8, 6, 8, 6)
        layout.addWidget(competency_summary)

        if self.competency_evidence_repository is not None:
            self.competency_evidence_review_widget = CompetencyEvidenceReviewWidget(
                self.trade_plan,
                self.competency_evidence_repository,
                self.competency_development_direction_repository,
                self.competency_cross_run_observation_repository,
                self.competency_evidence_maturity_repository,
            )
            self.competency_evidence_review_widget.study_competency_requested.connect(
                self._prepare_targeted_study
            )
            layout.addWidget(self.competency_evidence_review_widget)

        launcher_heading = QLabel("Lab / Replay")
        launcher_heading.setStyleSheet("font-weight: 600;")
        layout.addWidget(launcher_heading)
        layout.addWidget(self.process_run_launcher_widget)

        scope_heading = QLabel("Current scope")
        scope_heading.setStyleSheet("font-weight: 600;")
        layout.addWidget(scope_heading)
        for topic in section.topics:
            label = QLabel(f"• {topic}")
            label.setWordWrap(True)
            layout.addWidget(label)

        layout.addStretch()
        scroll.setWidget(page)
        return scroll

    def _build_playbooks_page(self, section: TradePlanSectionDefinition) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        heading = QLabel(section.name)
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(heading)
        purpose = QLabel(section.purpose)
        purpose.setWordWrap(True)
        layout.addWidget(purpose)
        note = QLabel(
            "Playbooks are authoritative Trade Plan data. The current alpha renders them read-only; future in-app editing will create a draft/new Trade Plan revision rather than mutate a published revision."
        )
        note.setWordWrap(True)
        note.setFrameShape(QFrame.Shape.StyledPanel)
        note.setContentsMargins(10, 8, 10, 8)
        layout.addWidget(note)
        for playbook in self.trade_plan.playbooks:
            layout.addWidget(self._build_playbook_card(playbook))
        if not self.trade_plan.playbooks:
            empty = QLabel("No structured Playbooks are defined in this Trade Plan revision.")
            empty.setWordWrap(True)
            layout.addWidget(empty)
        layout.addStretch()
        return page

    def _build_playbook_card(self, playbook: PlaybookDefinition) -> QFrame:
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        state = "Available" if playbook.available else "Locked"
        title = QLabel(f"{playbook.name} · {playbook.revision} · {state}")
        title.setStyleSheet("font-weight: 600;")
        layout.addWidget(title)
        if playbook.purpose:
            purpose = QLabel(playbook.purpose)
            purpose.setWordWrap(True)
            layout.addWidget(purpose)
        sessions = ", ".join(playbook.sessions) if playbook.sessions else "Not specified"
        session_label = QLabel(f"Sessions / windows: {sessions}")
        session_label.setWordWrap(True)
        layout.addWidget(session_label)
        summary = QLabel(
            f"{len(playbook.watch_point_templates)} inherited watch point(s) · "
            f"{len(playbook.entry_criteria)} entry criterion/criteria · "
            f"required threshold: {playbook.required_entry_count if playbook.required_entry_count is not None else 'Not configured'}"
        )
        summary.setWordWrap(True)
        layout.addWidget(summary)
        return card

    @property
    def selected_section_id(self) -> str:
        row = self.section_list.currentRow()
        if 0 <= row < len(self._section_ids):
            return self._section_ids[row]
        return ""

    @property
    def feedback_record_id(self) -> str:
        if self.selected_section_id == "process":
            if self.process_tabs.currentWidget() is self.trading_day_shell_widget:
                return self.trading_day_shell_widget.feedback_record_id
            station_id = self.process_blueprint_widget.selected_station_id
            if station_id:
                return station_id
        return self.selected_section_id
