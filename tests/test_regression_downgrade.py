from dataclasses import replace

from PySide6.QtWidgets import QApplication, QLabel

from ict_cockpit.analysis.competency import (
    CompetencyAssessment,
    CompetencyState,
)
from ict_cockpit.analysis.environment_progression import (
    EnvironmentEligibilityStatus,
    ProgressionStandingStatus,
    derive_progression_standing,
    evaluate_environment_eligibility,
    progression_eligibility_to_dict,
)
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.progression_attainment_repository import (
    ProgressionAttainmentRepository,
)
from ict_cockpit.database.progression_regression_review_repository import (
    ProgressionRegressionReviewRepository,
)
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget
from ict_cockpit.progression import (
    ProgressionAttainment,
    ProgressionBoundary,
    ProgressionRegressionReview,
    RegressionReviewClassification,
)
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


class AssessmentRepo:
    def __init__(self, item=None):
        self.item = item

    def get(self, _plan_id, _competency_id):
        return self.item


def configured_plan(*, revision: str = "Alpha 0.7"):
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
    return replace(base, revision=revision, progression_policies=(policy,))


def assessment(plan, state: CompetencyState):
    return CompetencyAssessment(
        trade_plan_id=plan.id,
        trade_plan_revision=plan.revision,
        competency_id="draw-on-liquidity",
        state=state,
    )


def available_result(plan):
    result = evaluate_environment_eligibility(
        RunEnvironment.FORWARD_TEST,
        trade_plan=plan,
        competency_assessment_repository=AssessmentRepo(
            assessment(plan, CompetencyState.PROFICIENT)
        ),
    )
    assert result.progression is not None
    assert result.status is EnvironmentEligibilityStatus.AVAILABLE
    return result.progression


def attainment_from_result(plan, result, *, id="attainment-1"):
    return ProgressionAttainment(
        id=id,
        trade_plan_id=plan.id,
        trade_plan_revision=plan.revision,
        boundary=result.boundary,
        policy_id=result.policy_id,
        eligibility_snapshot=progression_eligibility_to_dict(result),
        attained_environment=RunEnvironment.FORWARD_TEST.value,
        attained_at="2026-10-09T12:00:00-06:00",
    )


def test_schema_v33_adds_attainment_and_regression_review_storage(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    version = connection.execute("PRAGMA user_version").fetchone()[0]
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    assert version == CURRENT_SCHEMA_VERSION == 33
    assert "progression_attainment" in tables
    assert "progression_regression_review" in tables
    connection.close()


def test_attainment_is_recorded_once_as_immutable_history(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = ProgressionAttainmentRepository(connection)
    plan = configured_plan()
    result = available_result(plan)

    first = attainment_from_result(plan, result, id="first")
    second = attainment_from_result(plan, result, id="second")

    saved_first = repository.record_if_absent(first)
    saved_second = repository.record_if_absent(second)

    assert saved_first.id == "first"
    assert saved_second.id == "first"
    records = repository.list_for_plan(plan.id)
    assert len(records) == 1
    assert records[0].eligibility_snapshot["status"] == "Available"
    connection.close()


def test_never_attained_block_is_not_regression(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = ProgressionAttainmentRepository(connection)
    plan = configured_plan()

    blocked = evaluate_environment_eligibility(
        RunEnvironment.FORWARD_TEST,
        trade_plan=plan,
        competency_assessment_repository=AssessmentRepo(
            assessment(plan, CompetencyState.REHEARSAL_NEEDED)
        ),
    )
    standing = derive_progression_standing(
        trade_plan=plan,
        eligibility=blocked.progression,
        progression_attainment_repository=repository,
    )

    assert standing.status is ProgressionStandingStatus.NOT_ATTAINED
    assert standing.review_required is False
    connection.close()


def test_same_policy_attainment_then_block_detects_eligibility_loss(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = ProgressionAttainmentRepository(connection)
    plan = configured_plan()
    available = available_result(plan)
    repository.record_if_absent(attainment_from_result(plan, available))

    blocked = evaluate_environment_eligibility(
        RunEnvironment.FORWARD_TEST,
        trade_plan=plan,
        competency_assessment_repository=AssessmentRepo(
            assessment(plan, CompetencyState.REHEARSAL_NEEDED)
        ),
    )
    standing = derive_progression_standing(
        trade_plan=plan,
        eligibility=blocked.progression,
        progression_attainment_repository=repository,
    )

    assert (
        standing.status
        is ProgressionStandingStatus.ELIGIBILITY_LOSS_DETECTED
    )
    assert standing.review_required is True
    assert standing.prior_attainment is not None
    connection.close()


def test_new_plan_revision_block_is_revalidation_not_regression(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = ProgressionAttainmentRepository(connection)

    old_plan = configured_plan(revision="Alpha 0.7")
    old_available = available_result(old_plan)
    repository.record_if_absent(
        attainment_from_result(old_plan, old_available, id="old-attainment")
    )

    new_plan = configured_plan(revision="Alpha 0.8")
    blocked = evaluate_environment_eligibility(
        RunEnvironment.FORWARD_TEST,
        trade_plan=new_plan,
        competency_assessment_repository=AssessmentRepo(
            assessment(new_plan, CompetencyState.REHEARSAL_NEEDED)
        ),
    )
    standing = derive_progression_standing(
        trade_plan=new_plan,
        eligibility=blocked.progression,
        progression_attainment_repository=repository,
    )

    assert standing.status is ProgressionStandingStatus.REVALIDATION_REQUIRED
    assert "Alpha 0.7" in standing.detail
    assert standing.review_required is True
    connection.close()


def test_regression_review_round_trips_without_mutating_competency(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    attainment_repository = ProgressionAttainmentRepository(connection)
    review_repository = ProgressionRegressionReviewRepository(connection)
    plan = configured_plan()
    available = available_result(plan)
    attained = attainment_repository.record_if_absent(
        attainment_from_result(plan, available)
    )
    competency = assessment(plan, CompetencyState.PROFICIENT)
    before = competency.state

    blocked = evaluate_environment_eligibility(
        RunEnvironment.FORWARD_TEST,
        trade_plan=plan,
        competency_assessment_repository=AssessmentRepo(
            assessment(plan, CompetencyState.REHEARSAL_NEEDED)
        ),
    )
    review = ProgressionRegressionReview(
        trade_plan_id=plan.id,
        trade_plan_revision=plan.revision,
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        prior_attainment_id=attained.id,
        eligibility_snapshot=progression_eligibility_to_dict(
            blocked.progression
        ),
        classification=(
            RegressionReviewClassification.CONFIRMED_COMPETENCY_REGRESSION
        ),
        note="Human-reviewed skill regression.",
        supporting_evidence_ids=["evidence-1", "evidence-2"],
    )
    review_repository.save(review)

    loaded = review_repository.get(
        plan.id,
        plan.revision,
        review.boundary,
        attained.id,
    )

    assert loaded is not None
    assert (
        loaded.classification
        is RegressionReviewClassification.CONFIRMED_COMPETENCY_REGRESSION
    )
    assert loaded.supporting_evidence_ids == ["evidence-1", "evidence-2"]
    assert competency.state is before
    connection.close()


def test_launcher_records_attainment_only_when_available_boundary_is_crossed(
    tmp_path,
) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    attainment_repository = ProgressionAttainmentRepository(connection)
    plan = configured_plan()
    widget = TradePlanWidget(
        plan,
        competency_assessment_repository=AssessmentRepo(
            assessment(plan, CompetencyState.PROFICIENT)
        ),
        progression_attainment_repository=attainment_repository,
    )
    launcher = widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(RunEnvironment.FORWARD_TEST.value)

    assert attainment_repository.list_for_plan(plan.id) == []
    assert launcher.begin_process_run() is True

    records = attainment_repository.list_for_plan(plan.id)
    assert len(records) == 1
    assert (
        records[0].boundary
        is ProgressionBoundary.REHEARSAL_TO_VALIDATION
    )
    assert records[0].attained_environment == RunEnvironment.FORWARD_TEST.value
    connection.close()


def test_alpha_07_not_configured_launch_does_not_create_attainment(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = ProgressionAttainmentRepository(connection)
    plan = build_default_trade_plan()
    widget = TradePlanWidget(
        plan,
        progression_attainment_repository=repository,
    )
    launcher = widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(RunEnvironment.REPLAY.value)

    assert launcher.begin_process_run() is True
    assert repository.list_for_plan(plan.id) == []
    connection.close()


def test_review_development_distinguishes_attainment_from_current_block(
    tmp_path,
) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    attainment_repository = ProgressionAttainmentRepository(connection)
    review_repository = ProgressionRegressionReviewRepository(connection)
    plan = configured_plan()
    available = available_result(plan)
    attainment_repository.record_if_absent(
        attainment_from_result(plan, available)
    )

    widget = TradePlanWidget(
        plan,
        competency_assessment_repository=AssessmentRepo(
            assessment(plan, CompetencyState.REHEARSAL_NEEDED)
        ),
        progression_attainment_repository=attainment_repository,
        progression_regression_review_repository=review_repository,
    )
    labels = [item.text() for item in widget.findChildren(QLabel)]

    assert any("Eligibility Loss Detected" in text for text in labels)
    assert any("Historical attainment" in text for text in labels)
    assert any("Current eligibility · BLOCKED" in text for text in labels)
    connection.close()
