from dataclasses import replace

from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.competency import CompetencyAssessment, CompetencyState
from ict_cockpit.analysis.environment_progression import (
    EnvironmentEligibilityStatus,
    derive_operator_progression_status,
)
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.progression_attainment_repository import (
    ProgressionAttainmentRepository,
)
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget
from ict_cockpit.progression import ProgressionBoundary
from ict_cockpit.trade_plan import (
    ProgressionPolicyDefinition,
    ProgressionRequirementDefinition,
    ProgressionRequirementKind,
    ProgressionRequirementOperator,
)


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class MutableAssessmentRepo:
    def __init__(self, item=None):
        self.item = item

    def get(self, _plan_id, _competency_id):
        return self.item


class EmptyEvidenceRepo:
    def list_for_plan(self, _plan_id):
        return []

    def list_for_competency(self, _plan_id, _competency_id):
        return []


def configured_plan():
    base = build_default_trade_plan()
    requirement = ProgressionRequirementDefinition(
        id="draw-state",
        name="Draw State",
        requirement_kind=ProgressionRequirementKind.COMPETENCY_STATE,
        operator=ProgressionRequirementOperator.IS,
        expected_values=("Proficient",),
        competency_id="draw-on-liquidity",
    )
    policy = ProgressionPolicyDefinition(
        id="rehearsal-to-validation-test",
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        name="Rehearsal to Validation Test",
        requirements=(requirement,),
    )
    return replace(base, progression_policies=(policy,))


def assessment(plan, state):
    return CompetencyAssessment(
        trade_plan_id=plan.id,
        trade_plan_revision=plan.revision,
        competency_id="draw-on-liquidity",
        state=state,
    )


def test_c5_operator_status_is_derived_not_persisted(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    plan = configured_plan()
    repo = MutableAssessmentRepo(
        assessment(plan, CompetencyState.REHEARSAL_NEEDED)
    )

    status = derive_operator_progression_status(
        RunEnvironment.FORWARD_TEST,
        trade_plan=plan,
        competency_assessment_repository=repo,
    )

    assert status.boundary is ProgressionBoundary.REHEARSAL_TO_VALIDATION
    assert status.eligibility.status is EnvironmentEligibilityStatus.BLOCKED
    assert status.recommended_environment is RunEnvironment.REPLAY
    assert status.navigation_target == "review.progression"
    assert "requirements are not satisfied" in status.action_guidance.lower()
    assert CURRENT_SCHEMA_VERSION == 33
    connection.close()


def test_blocked_launcher_stages_lower_environment_without_start_or_history(
    tmp_path,
) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    plan = configured_plan()
    attainment_repo = ProgressionAttainmentRepository(connection)
    assessment_repo = MutableAssessmentRepo(
        assessment(plan, CompetencyState.REHEARSAL_NEEDED)
    )
    widget = TradePlanWidget(
        plan,
        competency_assessment_repository=assessment_repo,
        progression_attainment_repository=attainment_repo,
    )
    launcher = widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(RunEnvironment.FORWARD_TEST.value)
    launcher.study_question_input.setText("Preserve this rehearsal intent")
    launcher.competency_checkboxes["draw-on-liquidity"].setChecked(True)

    assert "BLOCKED" in launcher.eligibility_label.text()
    assert launcher.stage_lower_button.isVisible() is True
    assert launcher.stage_recommended_lower_environment() is True

    assert launcher.selected_environment is RunEnvironment.REPLAY
    assert launcher.study_question_input.text() == "Preserve this rehearsal intent"
    assert launcher.competency_checkboxes["draw-on-liquidity"].isChecked() is True
    assert widget.trading_day_shell_widget.active_trading_run is None
    assert attainment_repo.list_for_plan(plan.id) == []
    assert "No progression, regression, or attainment record was created" in (
        launcher.status_label.text()
    )
    connection.close()


def test_blocked_launcher_can_navigate_to_focused_progression_area(
    tmp_path,
) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    plan = configured_plan()
    widget = TradePlanWidget(
        plan,
        competency_assessment_repository=MutableAssessmentRepo(
            assessment(plan, CompetencyState.REHEARSAL_NEEDED)
        ),
        competency_evidence_repository=EmptyEvidenceRepo(),
    )
    launcher = widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(RunEnvironment.FORWARD_TEST.value)

    assert launcher.review_progression_button.isVisible() is True
    launcher.review_progression_button.click()

    assert widget.selected_section_id == "review-development"
    review = widget.competency_evidence_review_widget
    assert review is not None
    assert review.work_tabs.currentWidget() is review.progression_page
    connection.close()


def test_requirement_details_are_progressively_disclosed(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    plan = configured_plan()
    widget = TradePlanWidget(
        plan,
        competency_assessment_repository=MutableAssessmentRepo(
            assessment(plan, CompetencyState.REHEARSAL_NEEDED)
        ),
    )
    launcher = widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(RunEnvironment.FORWARD_TEST.value)

    assert "Blocked by · Draw State" in launcher.eligibility_label.text()
    assert launcher.requirement_details_button.isVisible() is True
    assert launcher.requirement_details_label.isVisible() is False

    launcher.requirement_details_button.click()
    assert launcher.requirement_details_label.isVisible() is True
    assert "Draw State" in launcher.requirement_details_label.text()
    assert "Requirement Not Satisfied" in launcher.requirement_details_label.text()
    connection.close()


def test_active_run_is_not_demoted_when_progression_state_later_blocks(
    tmp_path,
) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    plan = configured_plan()
    assessment_repo = MutableAssessmentRepo(
        assessment(plan, CompetencyState.PROFICIENT)
    )
    attainment_repo = ProgressionAttainmentRepository(connection)
    widget = TradePlanWidget(
        plan,
        competency_assessment_repository=assessment_repo,
        progression_attainment_repository=attainment_repo,
    )
    launcher = widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(RunEnvironment.FORWARD_TEST.value)

    assert launcher.begin_process_run() is True
    original_run = widget.trading_day_shell_widget.active_trading_run
    assert original_run is not None
    original_id = original_run.id

    assessment_repo.item = assessment(
        plan,
        CompetencyState.REHEARSAL_NEEDED,
    )
    launcher._sync_environment_ui()

    assert "BLOCKED" in launcher.eligibility_label.text()
    assert widget.trading_day_shell_widget.active_trading_run is not None
    assert widget.trading_day_shell_widget.active_trading_run.id == original_id
    assert widget.trading_day_shell_widget.run_environment is (
        RunEnvironment.FORWARD_TEST
    )
    assert len(attainment_repo.list_for_plan(plan.id)) == 1
    connection.close()


def test_alpha_07_remains_nonrestrictive_without_lower_rung_staging(
    tmp_path,
) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    plan = build_default_trade_plan()
    widget = TradePlanWidget(plan)
    launcher = widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(RunEnvironment.LIVE.value)

    assert "NOT CONFIGURED" in launcher.eligibility_label.text()
    assert launcher.stage_lower_button.isVisible() is False
    assert launcher.review_progression_button.isVisible() is False
    connection.close()
