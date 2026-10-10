from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

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
from ict_cockpit.database.progression_attainment_repository import (
    ProgressionAttainmentRepository,
)
from ict_cockpit.database.progression_certification_repository import (
    ProgressionCertificationRepository,
)
from ict_cockpit.database.progression_regression_review_repository import (
    ProgressionRegressionReviewRepository,
)
from ict_cockpit.analysis.environment_progression import (
    derive_progression_standing,
    environment_for_progression_boundary,
    evaluate_environment_eligibility,
    progression_eligibility_to_dict,
)
from ict_cockpit.gui.competency_evidence_review_widget import (
    CompetencyEvidenceReviewWidget,
)
from ict_cockpit.gui.process_blueprint_widget import ProcessBlueprintWidget
from ict_cockpit.gui.process_run_launcher_widget import ProcessRunLauncherWidget
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget
from ict_cockpit.progression import (
    ProgressionCertification,
    ProgressionRegressionReview,
    RegressionReviewClassification,
)
from ict_cockpit.trade_plan import (
    PlaybookDefinition,
    ProgressionRequirementKind,
    TradePlanDefinition,
    TradePlanSectionDefinition,
)


class TradePlanWidget(QWidget):
    """Alpha shell for the trading system and its executable process."""

    def __init__(
        self,
        trade_plan: TradePlanDefinition,
        competency_assessment_repository: CompetencyAssessmentRepository | None = None,
        competency_evidence_repository: CompetencyEvidenceRepository | None = None,
        competency_development_direction_repository:
            CompetencyDevelopmentDirectionRepository | None = None,
        competency_cross_run_observation_repository:
            CompetencyCrossRunObservationRepository | None = None,
        competency_evidence_maturity_repository:
            CompetencyEvidenceMaturityRepository | None = None,
        progression_certification_repository:
            ProgressionCertificationRepository | None = None,
        progression_attainment_repository:
            ProgressionAttainmentRepository | None = None,
        progression_regression_review_repository:
            ProgressionRegressionReviewRepository | None = None,
    ) -> None:
        super().__init__()
        self.trade_plan = trade_plan
        self.competency_assessment_repository = competency_assessment_repository
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
        self.progression_certification_repository = (
            progression_certification_repository
        )
        self.progression_attainment_repository = progression_attainment_repository
        self.progression_regression_review_repository = (
            progression_regression_review_repository
        )
        self.competency_evidence_review_widget = None
        self.review_development_layout = None
        self.progression_governance_widget = None

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
            trade_plan=trade_plan,
            competency_assessment_repository=(
                self.competency_assessment_repository
            ),
            competency_evidence_repository=self.competency_evidence_repository,
            competency_evidence_maturity_repository=(
                self.competency_evidence_maturity_repository
            ),
            progression_certification_repository=(
                self.progression_certification_repository
            ),
            progression_attainment_repository=(
                self.progression_attainment_repository
            ),
            on_launched=self.focus_runtime,
            on_review_progression=self.focus_progression_review,
        )

        self._section_ids: list[str] = []
        for section in trade_plan.sections:
            self._section_ids.append(section.id)
            self.section_list.addItem(QListWidgetItem(section.name))
            if section.id == "process":
                page = self.process_tabs
            elif section.id == "rules-safety":
                page = self._build_rules_safety_page(section)
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
        if self.selected_section_id == "review-development":
            if self.competency_evidence_review_widget is not None:
                self.competency_evidence_review_widget.refresh()
            self._refresh_progression_governance_panel()
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

    def focus_progression_review(self) -> None:
        """Navigate to the focused Review / Development progression surface."""

        try:
            review_row = self._section_ids.index("review-development")
        except ValueError:
            return
        self.section_list.setCurrentRow(review_row)
        if self.competency_evidence_review_widget is not None:
            self.competency_evidence_review_widget.select_work_area(
                "Progression"
            )

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

    def _build_rules_safety_page(
        self,
        section: TradePlanSectionDefinition,
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

        progression_heading = QLabel("Progression Policy")
        progression_heading.setStyleSheet("font-weight: 600;")
        layout.addWidget(progression_heading)

        progression_note = QLabel(
            "Progression Policy is authoritative, versioned Trade Plan data. "
            "It defines gating requirements for upward Study -> Rehearsal -> "
            "Validation -> Execution boundaries. Eligibility evaluation is a "
            "separate layer."
        )
        progression_note.setWordWrap(True)
        progression_note.setFrameShape(QFrame.Shape.StyledPanel)
        progression_note.setContentsMargins(8, 6, 8, 6)
        layout.addWidget(progression_note)

        if not self.trade_plan.progression_policies:
            empty = QLabel(
                f"Trade Plan {self.trade_plan.revision} · Progression Policy: "
                "NOT CONFIGURED. No readiness rule is inferred."
            )
            empty.setWordWrap(True)
            empty.setFrameShape(QFrame.Shape.StyledPanel)
            empty.setContentsMargins(8, 6, 8, 6)
            layout.addWidget(empty)
        else:
            for policy in self.trade_plan.progression_policies:
                card = QFrame()
                card.setFrameShape(QFrame.Shape.StyledPanel)
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(8, 6, 8, 6)
                title = QLabel(
                    f"{policy.name} · {policy.boundary.value}"
                )
                title.setStyleSheet("font-weight: 600;")
                card_layout.addWidget(title)
                if policy.description:
                    description = QLabel(policy.description)
                    description.setWordWrap(True)
                    card_layout.addWidget(description)
                for requirement in policy.requirements:
                    scope = (
                        requirement.competency_id
                        if requirement.competency_id
                        else "Boundary / global"
                    )
                    expected = ", ".join(requirement.expected_values)
                    line = QLabel(
                        f"• {requirement.name} · {scope} · "
                        f"{requirement.requirement_kind.value} "
                        f"{requirement.operator.value} {expected}"
                    )
                    line.setWordWrap(True)
                    card_layout.addWidget(line)
                    if (
                        requirement.requirement_kind
                        is ProgressionRequirementKind.HUMAN_CERTIFICATION
                        and self.progression_certification_repository is not None
                    ):
                        certification = (
                            self.progression_certification_repository.get(
                                self.trade_plan.id,
                                self.trade_plan.revision,
                                policy.boundary,
                                requirement.id,
                            )
                        )
                        certification_checkbox = QCheckBox(
                            "Human certification confirmed"
                        )
                        certification_checkbox.setChecked(
                            bool(
                                certification is not None
                                and certification.confirmed
                            )
                        )
                        certification_note = QLineEdit()
                        certification_note.setPlaceholderText(
                            "Certification note (optional)"
                        )
                        if certification is not None:
                            certification_note.setText(certification.note)
                        certification_status = QLabel()
                        certification_status.setWordWrap(True)
                        save_certification = QPushButton(
                            "Save Human Certification"
                        )
                        save_certification.clicked.connect(
                            lambda _checked=False,
                            boundary=policy.boundary,
                            requirement_id=requirement.id,
                            checkbox=certification_checkbox,
                            note_input=certification_note,
                            status_label=certification_status:
                                self._save_progression_certification(
                                    boundary,
                                    requirement_id,
                                    checkbox,
                                    note_input,
                                    status_label,
                                )
                        )
                        card_layout.addWidget(certification_checkbox)
                        card_layout.addWidget(certification_note)
                        card_layout.addWidget(save_certification)
                        card_layout.addWidget(certification_status)
                layout.addWidget(card)

        layout.addSpacing(8)
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

    def _save_progression_certification(
        self,
        boundary,
        requirement_id: str,
        checkbox: QCheckBox,
        note_input: QLineEdit,
        status_label: QLabel,
    ) -> None:
        if self.progression_certification_repository is None:
            status_label.setText("Certification persistence is unavailable.")
            return
        item = ProgressionCertification(
            trade_plan_id=self.trade_plan.id,
            trade_plan_revision=self.trade_plan.revision,
            boundary=boundary,
            requirement_id=requirement_id,
            confirmed=checkbox.isChecked(),
            note=note_input.text(),
        )
        self.progression_certification_repository.save(item)
        status_label.setText(
            "Certification saved for this exact Trade Plan revision and "
            "progression requirement."
        )
        self.process_run_launcher_widget._sync_environment_ui()
        self._refresh_progression_governance_panel()

    def _refresh_progression_governance_panel(self) -> None:
        if (
            not self.trade_plan.progression_policies
            or self.review_development_layout is None
            or self.progression_governance_widget is None
        ):
            return
        replacement = self._build_progression_governance_panel()
        self.competency_evidence_review_widget.set_progression_standing_widget(
            replacement
        )
        self.progression_governance_widget = replacement

    def _build_progression_governance_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 6, 8, 6)
        heading = QLabel("Progression Standing")
        heading.setStyleSheet("font-weight: 600;")
        layout.addWidget(heading)
        note = QLabel(
            "Historical attainment and current eligibility are shown separately. "
            "Eligibility loss never changes Competency State automatically."
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        for policy in self.trade_plan.progression_policies:
            environment = environment_for_progression_boundary(policy.boundary)
            eligibility = evaluate_environment_eligibility(
                environment,
                trade_plan=self.trade_plan,
                competency_assessment_repository=(
                    self.competency_assessment_repository
                ),
                competency_evidence_repository=self.competency_evidence_repository,
                competency_evidence_maturity_repository=(
                    self.competency_evidence_maturity_repository
                ),
                progression_certification_repository=(
                    self.progression_certification_repository
                ),
            )
            standing = derive_progression_standing(
                trade_plan=self.trade_plan,
                eligibility=eligibility.progression,
                progression_attainment_repository=(
                    self.progression_attainment_repository
                ),
            )
            card = QFrame()
            card.setFrameShape(QFrame.Shape.StyledPanel)
            card_layout = QVBoxLayout(card)
            title = QLabel(
                f"{policy.boundary.value} · {standing.status.value}"
            )
            title.setStyleSheet("font-weight: 600;")
            card_layout.addWidget(title)
            current = QLabel(
                f"Current eligibility · {eligibility.status.value.upper()} · "
                f"{eligibility.detail}"
            )
            current.setWordWrap(True)
            card_layout.addWidget(current)
            if standing.prior_attainment is not None:
                attained = QLabel(
                    f"Historical attainment · "
                    f"{standing.prior_attainment.trade_plan_revision} · "
                    f"{standing.prior_attainment.attained_at}"
                )
                attained.setWordWrap(True)
                card_layout.addWidget(attained)
            detail = QLabel(standing.detail)
            detail.setWordWrap(True)
            card_layout.addWidget(detail)

            if (
                standing.review_required
                and standing.prior_attainment is not None
                and self.progression_regression_review_repository is not None
            ):
                existing = self.progression_regression_review_repository.get(
                    self.trade_plan.id,
                    self.trade_plan.revision,
                    policy.boundary,
                    standing.prior_attainment.id,
                )
                classification = QComboBox()
                for item in RegressionReviewClassification:
                    classification.addItem(item.value, item.value)
                if existing is not None:
                    classification.setCurrentText(
                        existing.classification.value
                    )
                elif standing.status.value == "Revalidation Required":
                    classification.setCurrentText(
                        RegressionReviewClassification.REVALIDATION_REQUIRED.value
                    )

                review_note = QLineEdit()
                review_note.setPlaceholderText(
                    "Review note — what changed and what does it mean?"
                )
                if existing is not None:
                    review_note.setText(existing.note)

                evidence_ids = QLineEdit()
                evidence_ids.setPlaceholderText(
                    "Supporting evidence IDs (optional, comma-separated)"
                )
                if existing is not None:
                    evidence_ids.setText(
                        ", ".join(existing.supporting_evidence_ids)
                    )

                save_status = QLabel()
                save_status.setWordWrap(True)
                save_button = QPushButton("Save Regression / Revalidation Review")
                save_button.clicked.connect(
                    lambda _checked=False,
                    boundary=policy.boundary,
                    attainment=standing.prior_attainment,
                    eligibility_result=eligibility.progression,
                    classification_combo=classification,
                    note_input=review_note,
                    evidence_input=evidence_ids,
                    status_label=save_status:
                        self._save_progression_regression_review(
                            boundary,
                            attainment,
                            eligibility_result,
                            classification_combo,
                            note_input,
                            evidence_input,
                            status_label,
                        )
                )
                card_layout.addWidget(QLabel("Human review classification"))
                card_layout.addWidget(classification)
                card_layout.addWidget(review_note)
                card_layout.addWidget(evidence_ids)
                card_layout.addWidget(save_button)
                card_layout.addWidget(save_status)

            layout.addWidget(card)

        return panel

    def _save_progression_regression_review(
        self,
        boundary,
        attainment,
        eligibility_result,
        classification_combo: QComboBox,
        note_input: QLineEdit,
        evidence_input: QLineEdit,
        status_label: QLabel,
    ) -> None:
        if self.progression_regression_review_repository is None:
            status_label.setText("Regression review persistence is unavailable.")
            return
        supporting_ids = [
            item.strip()
            for item in evidence_input.text().split(",")
            if item.strip()
        ]
        item = ProgressionRegressionReview(
            trade_plan_id=self.trade_plan.id,
            trade_plan_revision=self.trade_plan.revision,
            boundary=boundary,
            prior_attainment_id=attainment.id,
            eligibility_snapshot=progression_eligibility_to_dict(
                eligibility_result
            ),
            classification=classification_combo.currentText(),
            note=note_input.text(),
            supporting_evidence_ids=supporting_ids,
        )
        self.progression_regression_review_repository.save(item)
        status_label.setText(
            "Review saved. Historical attainment is preserved; Competency State, "
            "Evidence Maturity, and Development Direction were not changed."
        )

    def _build_review_development_page(
        self, section: TradePlanSectionDefinition
    ) -> QWidget:
        self.setProperty("uiAnchor", "review.development")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        page = QWidget()
        layout = QVBoxLayout(page)
        self.review_development_layout = layout
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
            self.competency_evidence_review_widget.set_practice_launcher_widget(
                self.process_run_launcher_widget
            )
            if self.trade_plan.progression_policies:
                self.progression_governance_widget = (
                    self._build_progression_governance_panel()
                )
                self.competency_evidence_review_widget.set_progression_standing_widget(
                    self.progression_governance_widget
                )
            layout.addWidget(self.competency_evidence_review_widget)
        elif self.trade_plan.progression_policies:
            # Preserve progression-standing visibility for lightweight/synthetic
            # TradePlanWidget uses that do not wire a competency-evidence repository.
            # Normal application wiring places the same panel in the focused
            # Progression work area above.
            self.progression_governance_widget = (
                self._build_progression_governance_panel()
            )
            layout.addWidget(self.progression_governance_widget)

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
