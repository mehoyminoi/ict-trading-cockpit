from datetime import datetime

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.environment_progression import (
    EnvironmentEligibilityStatus,
    derive_operator_progression_status,
    evaluate_environment_eligibility,
    progression_eligibility_to_dict,
)
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, current_new_york_time
from ict_cockpit.analysis.trading_session_run import (
    RunEnvironment,
    default_purpose_for_environment,
)
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget
from ict_cockpit.progression import ProgressionAttainment
from ict_cockpit.trade_plan import CompetencyDefinition, TradePlanDefinition


class ProcessRunLauncherWidget(QWidget):
    """Small doorway into the shared TDA -> Watch -> Review runtime.

    The launcher chooses provenance only. It does not create a Lab-specific
    process definition; Replay, Historical Backtest, Forward Test, and Live all
    execute the same runtime owned by the active Trade Plan.
    """

    def __init__(
        self,
        trading_day_shell: TradingDayShellWidget,
        *,
        trade_plan_revision: str,
        competencies: tuple[CompetencyDefinition, ...] = (),
        trade_plan: TradePlanDefinition | None = None,
        competency_assessment_repository=None,
        competency_evidence_repository=None,
        competency_evidence_maturity_repository=None,
        progression_certification_repository=None,
        progression_attainment_repository=None,
        on_launched=None,
        on_review_progression=None,
    ) -> None:
        super().__init__()
        self.trading_day_shell = trading_day_shell
        self.trade_plan_revision = trade_plan_revision.strip()
        self.competencies = tuple(competencies)
        self.trade_plan = trade_plan
        self.competency_assessment_repository = competency_assessment_repository
        self.competency_evidence_repository = competency_evidence_repository
        self.competency_evidence_maturity_repository = (
            competency_evidence_maturity_repository
        )
        self.progression_certification_repository = (
            progression_certification_repository
        )
        self.progression_attainment_repository = progression_attainment_repository
        self.competency_checkboxes: dict[str, QCheckBox] = {}
        self.on_launched = on_launched
        self.on_review_progression = on_review_progression
        self._progression_status = None

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(10, 8, 10, 8)
        frame_layout.setSpacing(6)

        heading = QLabel("New Process Run")
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        frame_layout.addWidget(heading)

        description = QLabel(
            "Use the same Trade Plan and operating process in Live, Replay, Historical Backtest, or Forward Test. "
            "Only the run environment changes; TDA, Watch, authorization, and Review remain the same."
        )
        description.setWordWrap(True)
        frame_layout.addWidget(description)

        environment_row = QHBoxLayout()
        environment_row.addWidget(QLabel("Environment"))
        self.environment_combo = QComboBox()
        for environment in (
            RunEnvironment.REPLAY,
            RunEnvironment.HISTORICAL_BACKTEST,
            RunEnvironment.FORWARD_TEST,
            RunEnvironment.LIVE,
        ):
            self.environment_combo.addItem(environment.value, environment.value)
        environment_row.addWidget(self.environment_combo, 1)
        frame_layout.addLayout(environment_row)

        self.purpose_label = QLabel()
        self.purpose_label.setWordWrap(True)
        frame_layout.addWidget(self.purpose_label)

        self.eligibility_label = QLabel()
        self.eligibility_label.setWordWrap(True)
        self.eligibility_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.eligibility_label.setContentsMargins(8, 6, 8, 6)
        frame_layout.addWidget(self.eligibility_label)

        self.progression_guidance_label = QLabel()
        self.progression_guidance_label.setWordWrap(True)
        frame_layout.addWidget(self.progression_guidance_label)

        self.requirement_details_button = QPushButton("Show requirement details")
        self.requirement_details_button.setCheckable(True)
        self.requirement_details_button.setVisible(False)
        frame_layout.addWidget(self.requirement_details_button)

        self.requirement_details_label = QLabel()
        self.requirement_details_label.setWordWrap(True)
        self.requirement_details_label.setVisible(False)
        self.requirement_details_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.requirement_details_label.setContentsMargins(8, 6, 8, 6)
        frame_layout.addWidget(self.requirement_details_label)
        self.requirement_details_button.toggled.connect(
            self.requirement_details_label.setVisible
        )
        self.requirement_details_button.toggled.connect(
            lambda checked: self.requirement_details_button.setText(
                "Hide requirement details"
                if checked
                else "Show requirement details"
            )
        )

        guardrail_actions = QHBoxLayout()
        self.stage_lower_button = QPushButton("Stage recommended lower environment")
        self.stage_lower_button.setVisible(False)
        self.stage_lower_button.clicked.connect(
            self.stage_recommended_lower_environment
        )
        guardrail_actions.addWidget(self.stage_lower_button)

        self.review_progression_button = QPushButton("Review Progression")
        self.review_progression_button.setVisible(False)
        self.review_progression_button.clicked.connect(
            self._request_progression_review
        )
        guardrail_actions.addWidget(self.review_progression_button)
        frame_layout.addLayout(guardrail_actions)

        market_time_row = QHBoxLayout()
        self.market_time_label = QLabel("Replay market time · New York")
        self.market_time_edit = QDateTimeEdit()
        self.market_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.market_time_edit.setCalendarPopup(True)
        now_ny = current_new_york_time()
        self.market_time_edit.setDateTime(
            QDateTime.fromString(
                now_ny.strftime("%Y-%m-%d %H:%M"),
                "yyyy-MM-dd HH:mm",
            )
        )
        market_time_row.addWidget(self.market_time_label)
        market_time_row.addWidget(self.market_time_edit, 1)
        frame_layout.addLayout(market_time_row)
        self.environment_combo.currentTextChanged.connect(
            lambda _text: self._sync_environment_ui()
        )

        self.study_frame = QFrame()
        self.study_frame.setFrameShape(QFrame.Shape.StyledPanel)
        study_layout = QVBoxLayout(self.study_frame)
        study_layout.setContentsMargins(8, 6, 8, 6)
        study_layout.setSpacing(4)

        self.study_heading = QLabel("Run Intent")
        self.study_heading.setStyleSheet("font-weight: 600;")
        study_layout.addWidget(self.study_heading)

        self.study_question_input = QLineEdit()
        self.study_question_input.setPlaceholderText(
            "Focus / question — what are you trying to learn, rehearse, or validate?"
        )
        study_layout.addWidget(self.study_question_input)

        self.study_hypothesis_input = QLineEdit()
        self.study_hypothesis_input.setPlaceholderText(
            "Hypothesis (optional) — what do you expect to find?"
        )
        study_layout.addWidget(self.study_hypothesis_input)

        self.study_scope_input = QLineEdit()
        self.study_scope_input.setPlaceholderText(
            "Scope (optional) — setup, session, dates, conditions, or practice focus"
        )
        study_layout.addWidget(self.study_scope_input)

        self.competency_frame = QFrame()
        self.competency_frame.setFrameShape(QFrame.Shape.StyledPanel)
        competency_layout = QVBoxLayout(self.competency_frame)
        competency_layout.setContentsMargins(7, 5, 7, 5)
        competency_layout.setSpacing(2)
        competency_heading = QLabel("Competency focus (optional)")
        competency_heading.setStyleSheet("font-weight: 600;")
        competency_layout.addWidget(competency_heading)
        competency_note = QLabel(
            "Tag the plan-owned mechanic(s) this run is deliberately training. "
            "This is evidence provenance, not a proficiency score."
        )
        competency_note.setWordWrap(True)
        competency_layout.addWidget(competency_note)
        for competency in self.competencies:
            checkbox = QCheckBox(
                f"{competency.name} · {competency.category}"
            )
            checkbox.setToolTip(competency.description)
            self.competency_checkboxes[competency.id] = checkbox
            competency_layout.addWidget(checkbox)
        if not self.competencies:
            competency_layout.addWidget(
                QLabel("No competencies are defined in this Trade Plan revision.")
            )
        study_layout.addWidget(self.competency_frame)

        study_note = QLabel(
            "Historical Backtest requires a focused study question. "
            "Replay and Forward Test may carry optional intent without becoming Lab work."
        )
        study_note.setWordWrap(True)
        study_layout.addWidget(study_note)
        frame_layout.addWidget(self.study_frame)

        plan_row = QHBoxLayout()
        plan_row.addWidget(QLabel("Trade Plan"))
        self.trade_plan_label = QLabel(self.trade_plan_revision or "Not identified")
        self.trade_plan_label.setStyleSheet("font-weight: 600;")
        plan_row.addWidget(self.trade_plan_label, 1)
        frame_layout.addLayout(plan_row)

        available_playbooks = [item for item in trading_day_shell.playbooks if item.available]
        models_row = QHBoxLayout()
        models_row.addWidget(QLabel("Reference models"))
        self.models_label = QLabel(
            f"{len(available_playbooks)} available from Trade Plan · selected during TDA"
        )
        self.models_label.setWordWrap(True)
        models_row.addWidget(self.models_label, 1)
        frame_layout.addLayout(models_row)

        model_guidance = QLabel(
            "Reference models are not auto-selected for Replay or Backtest runs. "
            "During Premarket Thesis, use Models in Play to mark whichever models the analysis says may apply. "
            "Selecting none is valid and leaves the technician/day-specific path available."
        )
        model_guidance.setWordWrap(True)
        model_guidance.setFrameShape(QFrame.Shape.StyledPanel)
        model_guidance.setContentsMargins(8, 6, 8, 6)
        frame_layout.addWidget(model_guidance)

        self.begin_button = QPushButton("Begin Process Run")
        self.begin_button.clicked.connect(self.begin_process_run)
        frame_layout.addWidget(self.begin_button)

        self.status_label = QLabel(
            "No separate Lab workflow is created; this opens the normal Process runtime with study provenance attached."
        )
        self.status_label.setWordWrap(True)
        frame_layout.addWidget(self.status_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(frame)
        self._sync_environment_ui()

    def _sync_environment_ui(self) -> None:
        environment = self.selected_environment
        historical = environment in {
            RunEnvironment.REPLAY,
            RunEnvironment.HISTORICAL_BACKTEST,
        }
        self.market_time_label.setVisible(historical)
        self.market_time_edit.setVisible(historical)

        intent_visible = environment is not RunEnvironment.LIVE
        self.study_frame.setVisible(intent_visible)
        self.competency_frame.setVisible(intent_visible)
        self.study_heading.setText(
            "Study Intent"
            if environment is RunEnvironment.HISTORICAL_BACKTEST
            else "Run Intent"
        )

        purpose = default_purpose_for_environment(environment)
        self.purpose_label.setText(
            f"Default purpose · {purpose.value}"
        )

        progression_status = self._derive_selected_progression_status()
        self._progression_status = progression_status
        eligibility = progression_status.eligibility
        boundary_text = (
            progression_status.boundary.value
            if progression_status.boundary is not None
            else "Foundation / no boundary required"
        )
        blocked_names = []
        if (
            eligibility.progression is not None
            and eligibility.status is EnvironmentEligibilityStatus.BLOCKED
        ):
            blocked_names = [
                item.requirement_name
                for item in eligibility.progression.requirement_results
                if item.status.value != "Satisfied"
            ]
        blocker_summary = (
            "\nBlocked by · " + ", ".join(blocked_names)
            if blocked_names
            else ""
        )
        self.eligibility_label.setText(
            f"Progression eligibility · {eligibility.status.value.upper()}\n"
            f"Boundary · {boundary_text}\n"
            f"{eligibility.detail}{blocker_summary}"
        )
        self.progression_guidance_label.setText(
            f"Next · {progression_status.action_guidance}"
            if progression_status.action_guidance
            else ""
        )

        requirement_lines = []
        if (
            eligibility.progression is not None
            and eligibility.progression.requirement_results
        ):
            for item in eligibility.progression.requirement_results:
                reason = (
                    f" · {item.reason.value}"
                    if item.reason is not None
                    else ""
                )
                requirement_lines.append(
                    f"{item.status.value.upper()}{reason}: "
                    f"{item.requirement_name} — {item.detail}"
                )
        self.requirement_details_label.setText("\n".join(requirement_lines))
        has_details = bool(requirement_lines)
        self.requirement_details_button.setVisible(has_details)
        if not has_details:
            self.requirement_details_button.setChecked(False)
            self.requirement_details_label.setVisible(False)

        blocked = eligibility.status is EnvironmentEligibilityStatus.BLOCKED
        self.stage_lower_button.setVisible(
            blocked and progression_status.recommended_environment is not None
        )
        self.review_progression_button.setVisible(
            blocked and bool(progression_status.navigation_target)
        )

    def _derive_selected_progression_status(self):
        return derive_operator_progression_status(
            self.selected_environment,
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
            progression_attainment_repository=(
                self.progression_attainment_repository
            ),
        )

    def stage_recommended_lower_environment(self) -> bool:
        """Stage the normal lower rung without starting or mutating history."""

        status = self._derive_selected_progression_status()
        lower = status.recommended_environment
        if (
            status.eligibility.status
            is not EnvironmentEligibilityStatus.BLOCKED
            or lower is None
        ):
            self.status_label.setText(
                "No blocked upward transition has a lower environment to stage."
            )
            return False

        self.environment_combo.setCurrentText(lower.value)
        self.status_label.setText(
            f"Staged {lower.value}. Review the preserved run intent, then "
            "explicitly click Begin Process Run when ready. No progression, "
            "regression, or attainment record was created."
        )
        return True

    def _request_progression_review(self) -> None:
        if self.on_review_progression is None:
            self.status_label.setText(
                "Progression review navigation is unavailable in this context."
            )
            return
        self.on_review_progression()

    def _evaluate_selected_environment(self):
        return evaluate_environment_eligibility(
            self.selected_environment,
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

    def _selected_historical_market_time(self) -> datetime:
        value = self.market_time_edit.dateTime()
        date_value = value.date()
        time_value = value.time()
        return datetime(
            date_value.year(),
            date_value.month(),
            date_value.day(),
            time_value.hour(),
            time_value.minute(),
            tzinfo=MARKET_TIMEZONE,
        )

    @property
    def selected_environment(self) -> RunEnvironment:
        return RunEnvironment(self.environment_combo.currentData())

    def prepare_targeted_study(self, competency_id: str) -> bool:
        competency_id = competency_id.strip()
        checkbox = self.competency_checkboxes.get(competency_id)
        if checkbox is None:
            self.status_label.setText(
                "The selected competency is not defined in this Trade Plan revision."
            )
            return False

        self.environment_combo.setCurrentText(
            RunEnvironment.HISTORICAL_BACKTEST.value
        )
        for item in self.competency_checkboxes.values():
            item.setChecked(False)
        checkbox.setChecked(True)
        competency = next(
            (
                item
                for item in self.competencies
                if item.id == competency_id
            ),
            None,
        )
        label = competency.name if competency is not None else competency_id
        question = self.study_question_input.text().strip()
        if question:
            self.status_label.setText(
                f"Targeted Study prepared for {label}. "
                "Study question is set; click Begin Process Run to start."
            )
            self.begin_button.setFocus()
        else:
            self.status_label.setText(
                f"Targeted Study prepared for {label}. "
                "Define the study question, then click Begin Process Run."
            )
            self.study_question_input.setFocus()
        return True

    def begin_process_run(self) -> bool:
        shell = self.trading_day_shell
        if shell.active_trading_run is not None:
            self.status_label.setText(
                "An active Process Run already exists. Conclude it before starting another environment."
            )
            return False

        environment = self.selected_environment
        eligibility = self._evaluate_selected_environment()
        if not eligibility.can_launch:
            self.status_label.setText(
                f"Cannot start {environment.value}: {eligibility.detail} "
                f"Use the recommended lower environment or satisfy the "
                f"configured Trade Plan requirements."
            )
            return False

        shell.run_environment = environment
        shell.run_purpose = default_purpose_for_environment(environment)

        question = self.study_question_input.text().strip()
        if (
            environment is RunEnvironment.HISTORICAL_BACKTEST
            and not question
        ):
            self.status_label.setText(
                "Add a focused study question before starting Historical Backtest."
            )
            return False

        if environment in {
            RunEnvironment.REPLAY,
            RunEnvironment.HISTORICAL_BACKTEST,
        }:
            shell.run_market_timestamp = self._selected_historical_market_time()
        else:
            shell.run_market_timestamp = None

        hypothesis = self.study_hypothesis_input.text().strip()
        scope = self.study_scope_input.text().strip()
        selected_focus = []
        if environment is not RunEnvironment.LIVE:
            for competency in self.competencies:
                checkbox = self.competency_checkboxes.get(competency.id)
                if checkbox is not None and checkbox.isChecked():
                    selected_focus.append(competency.to_dict())

        if (
            environment is not RunEnvironment.LIVE
            and (question or hypothesis or scope or selected_focus)
        ):
            shell.run_study_context = {
                "question": question,
                "hypothesis": hypothesis,
                "scope": scope,
                "competency_focus": selected_focus,
            }
        else:
            shell.run_study_context = {}
        shell.start_new_trading_day()

        run = shell.active_trading_run
        if run is None:
            self.status_label.setText("The Process Run could not be started.")
            return False

        attainment_note = ""
        if (
            self.progression_attainment_repository is not None
            and eligibility.progression is not None
            and eligibility.progression.status
                is EnvironmentEligibilityStatus.AVAILABLE
            and eligibility.progression.policy_id
        ):
            attainment = ProgressionAttainment(
                trade_plan_id=eligibility.progression.trade_plan_id,
                trade_plan_revision=eligibility.progression.trade_plan_revision,
                boundary=eligibility.progression.boundary,
                policy_id=eligibility.progression.policy_id,
                eligibility_snapshot=progression_eligibility_to_dict(
                    eligibility.progression
                ),
                attained_environment=environment.value,
                note=f"Boundary crossed by starting Process Run {run.id}.",
            )
            saved = self.progression_attainment_repository.record_if_absent(
                attainment
            )
            if saved.id == attainment.id:
                attainment_note = (
                    f" Progression attainment recorded for "
                    f"{eligibility.progression.boundary.value}."
                )

        available_count = len([item for item in shell.playbooks if item.available])
        self.status_label.setText(
            f"Started {environment.value} · {run.purpose.value} · {run.run_label} · Trade Plan "
            f"{run.trade_plan_revision or self.trade_plan_revision}. "
            f"{available_count} reference model(s) are available; none are auto-selected. "
            f"Market time source: {run.market_time_context.get('source', 'Not configured')}. "
            + (
                f"Study: {run.study_context.question}. "
                if run.study_context is not None
                else ""
            )
            + "Choose Models in Play during Premarket Thesis if the TDA says they apply."
            + attainment_note
        )
        if self.on_launched is not None:
            self.on_launched()
        return True
