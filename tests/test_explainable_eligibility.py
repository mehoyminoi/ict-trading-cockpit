from dataclasses import replace

from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.competency import (
    CompetencyAssessment,
    CompetencyEvidence,
    CompetencyEvidenceMaturityProfile,
    CompetencyState,
    EvidenceMaturityState,
)
from ict_cockpit.analysis.environment_progression import (
    EnvironmentEligibilityStatus,
    ProgressionRequirementReason,
    ProgressionRequirementStatus,
    evaluate_environment_eligibility,
    evaluate_progression_boundary,
)
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.progression_certification_repository import (
    ProgressionCertificationRepository,
)
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget
from ict_cockpit.progression import (
    ProgressionBoundary,
    ProgressionCertification,
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


class MaturityRepo:
    def __init__(self, item=None):
        self.item = item

    def get(self, _plan_id, _competency_id, _boundary):
        return self.item


class EvidenceRepo:
    def __init__(self, items=()):
        self.items = list(items)

    def list_for_competency(self, _plan_id, _competency_id):
        return list(self.items)


class CertificationRepo:
    def __init__(self, item=None):
        self.item = item

    def get(self, _plan_id, _revision, _boundary, _requirement_id):
        return self.item


def requirement(
    requirement_id: str,
    kind: ProgressionRequirementKind,
    operator: ProgressionRequirementOperator,
    expected_values: tuple[str, ...],
    *,
    competency_id: str = "draw-on-liquidity",
):
    return ProgressionRequirementDefinition(
        id=requirement_id,
        name=requirement_id.replace("-", " ").title(),
        requirement_kind=kind,
        operator=operator,
        expected_values=expected_values,
        competency_id=(
            ""
            if kind is ProgressionRequirementKind.HUMAN_CERTIFICATION
            else competency_id
        ),
    )


def configured_plan(*requirements):
    base = build_default_trade_plan()
    policy = ProgressionPolicyDefinition(
        id="rehearsal-to-validation-test",
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        name="Rehearsal to Validation Test",
        requirements=tuple(requirements),
    )
    return replace(base, progression_policies=(policy,))


def test_schema_v32_adds_progression_certification_storage(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    version = connection.execute("PRAGMA user_version").fetchone()[0]
    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(progression_certification)"
        ).fetchall()
    }

    assert version == CURRENT_SCHEMA_VERSION == 33
    assert {
        "trade_plan_id",
        "trade_plan_revision",
        "progression_boundary",
        "requirement_id",
        "confirmed",
        "note",
        "confirmed_at",
        "updated_at",
    }.issubset(columns)
    connection.close()


def test_progression_certification_round_trips_by_revision_boundary_requirement(
    tmp_path,
) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = ProgressionCertificationRepository(connection)

    item = ProgressionCertification(
        trade_plan_id="ict-trade-plan-alpha",
        trade_plan_revision="Alpha 0.8",
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        requirement_id="progression-review",
        confirmed=True,
        note="Reviewed contradictions and current-plan context.",
    )
    repository.save(item)

    loaded = repository.get(
        item.trade_plan_id,
        item.trade_plan_revision,
        item.boundary,
        item.requirement_id,
    )

    assert loaded is not None
    assert loaded.confirmed is True
    assert loaded.note == item.note
    assert loaded.confirmed_at
    connection.close()


def test_all_satisfied_requirements_make_configured_boundary_available() -> None:
    plan = configured_plan(
        requirement(
            "state",
            ProgressionRequirementKind.COMPETENCY_STATE,
            ProgressionRequirementOperator.IS_ONE_OF,
            ("Validation Needed", "Proficient"),
        ),
        requirement(
            "maturity",
            ProgressionRequirementKind.EVIDENCE_MATURITY_STATE,
            ProgressionRequirementOperator.IS,
            ("Decision-Usable Evidence",),
        ),
        requirement(
            "rehearsal-evidence",
            ProgressionRequirementKind.EVIDENCE_PURPOSE_PRESENT,
            ProgressionRequirementOperator.EXISTS,
            ("Rehearsal",),
        ),
        requirement(
            "review-certification",
            ProgressionRequirementKind.HUMAN_CERTIFICATION,
            ProgressionRequirementOperator.IS,
            ("Confirmed",),
        ),
    )
    assessment = CompetencyAssessment(
        trade_plan_id=plan.id,
        trade_plan_revision="Alpha 0.7",
        competency_id="draw-on-liquidity",
        state=CompetencyState.PROFICIENT,
    )
    maturity = CompetencyEvidenceMaturityProfile(
        trade_plan_id=plan.id,
        trade_plan_revision=plan.revision,
        competency_id="draw-on-liquidity",
        progression_boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        maturity_state=EvidenceMaturityState.DECISION_USABLE,
    )
    evidence = CompetencyEvidence(
        trade_plan_id=plan.id,
        trade_plan_revision=plan.revision,
        competency_id="draw-on-liquidity",
        competency_name="Draw on liquidity / narrative",
        competency_category="TDA",
        trading_run_id="run-1",
        run_environment="Replay",
        run_purpose="Rehearsal",
        study_outcome="Practice Complete",
    )
    certification = ProgressionCertification(
        trade_plan_id=plan.id,
        trade_plan_revision=plan.revision,
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        requirement_id="review-certification",
        confirmed=True,
    )

    result = evaluate_progression_boundary(
        trade_plan=plan,
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        competency_assessment_repository=AssessmentRepo(assessment),
        competency_evidence_maturity_repository=MaturityRepo(maturity),
        competency_evidence_repository=EvidenceRepo((evidence,)),
        progression_certification_repository=CertificationRepo(certification),
    )

    assert result.status is EnvironmentEligibilityStatus.AVAILABLE
    assert all(
        item.status is ProgressionRequirementStatus.SATISFIED
        for item in result.requirement_results
    )


def test_missing_required_evidence_is_not_satisfied_not_unknown() -> None:
    req = requirement(
        "rehearsal-evidence",
        ProgressionRequirementKind.EVIDENCE_PURPOSE_PRESENT,
        ProgressionRequirementOperator.EXISTS,
        ("Rehearsal",),
    )
    plan = configured_plan(req)

    result = evaluate_progression_boundary(
        trade_plan=plan,
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        competency_evidence_repository=EvidenceRepo(),
    )

    item = result.requirement_results[0]
    assert result.status is EnvironmentEligibilityStatus.BLOCKED
    assert item.status is ProgressionRequirementStatus.NOT_SATISFIED
    assert item.reason is ProgressionRequirementReason.INSUFFICIENT_EVIDENCE


def test_old_revision_evidence_does_not_satisfy_current_plan_context() -> None:
    req = requirement(
        "rehearsal-evidence",
        ProgressionRequirementKind.EVIDENCE_PURPOSE_PRESENT,
        ProgressionRequirementOperator.EXISTS,
        ("Rehearsal",),
    )
    plan = configured_plan(req)
    old = CompetencyEvidence(
        trade_plan_id=plan.id,
        trade_plan_revision="Alpha 0.6",
        competency_id="draw-on-liquidity",
        competency_name="Draw on liquidity / narrative",
        competency_category="TDA",
        trading_run_id="old-run",
        run_environment="Replay",
        run_purpose="Rehearsal",
        study_outcome="Practice Complete",
    )

    result = evaluate_progression_boundary(
        trade_plan=plan,
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        competency_evidence_repository=EvidenceRepo((old,)),
    )

    item = result.requirement_results[0]
    assert item.status is ProgressionRequirementStatus.NOT_SATISFIED
    assert "Trade Plan Alpha 0.7" in item.detail


def test_old_revision_maturity_is_unknown_and_does_not_reset_competency() -> None:
    req = requirement(
        "maturity",
        ProgressionRequirementKind.EVIDENCE_MATURITY_STATE,
        ProgressionRequirementOperator.IS,
        ("Decision-Usable Evidence",),
    )
    plan = configured_plan(req)
    maturity = CompetencyEvidenceMaturityProfile(
        trade_plan_id=plan.id,
        trade_plan_revision="Alpha 0.6",
        competency_id="draw-on-liquidity",
        progression_boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        maturity_state=EvidenceMaturityState.DECISION_USABLE,
    )
    assessment = CompetencyAssessment(
        trade_plan_id=plan.id,
        trade_plan_revision="Alpha 0.6",
        competency_id="draw-on-liquidity",
        state=CompetencyState.PROFICIENT,
    )
    before = assessment.state

    result = evaluate_progression_boundary(
        trade_plan=plan,
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        competency_evidence_maturity_repository=MaturityRepo(maturity),
        competency_assessment_repository=AssessmentRepo(assessment),
    )

    item = result.requirement_results[0]
    assert item.status is ProgressionRequirementStatus.UNKNOWN
    assert item.reason is ProgressionRequirementReason.CANNOT_EVALUATE
    assert assessment.state is before


def test_missing_human_certification_blocks_with_specific_reason() -> None:
    req = requirement(
        "review-certification",
        ProgressionRequirementKind.HUMAN_CERTIFICATION,
        ProgressionRequirementOperator.IS,
        ("Confirmed",),
    )
    plan = configured_plan(req)

    result = evaluate_progression_boundary(
        trade_plan=plan,
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        progression_certification_repository=CertificationRepo(),
    )

    item = result.requirement_results[0]
    assert result.status is EnvironmentEligibilityStatus.BLOCKED
    assert item.status is ProgressionRequirementStatus.NOT_SATISFIED
    assert (
        item.reason
        is ProgressionRequirementReason.HUMAN_CERTIFICATION_REQUIRED
    )


def test_alpha_07_not_configured_remains_non_restrictive() -> None:
    plan = build_default_trade_plan()

    result = evaluate_environment_eligibility(
        RunEnvironment.LIVE,
        trade_plan=plan,
    )

    assert result.status is EnvironmentEligibilityStatus.NOT_CONFIGURED
    assert result.can_launch is True


def test_configured_blocked_policy_prevents_upward_launcher_transition() -> None:
    get_app()
    req = requirement(
        "state",
        ProgressionRequirementKind.COMPETENCY_STATE,
        ProgressionRequirementOperator.IS,
        ("Proficient",),
    )
    plan = configured_plan(req)
    assessment = CompetencyAssessment(
        trade_plan_id=plan.id,
        trade_plan_revision=plan.revision,
        competency_id="draw-on-liquidity",
        state=CompetencyState.REHEARSAL_NEEDED,
    )
    widget = TradePlanWidget(
        plan,
        competency_assessment_repository=AssessmentRepo(assessment),
    )
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(RunEnvironment.FORWARD_TEST.value)

    assert "BLOCKED" in launcher.eligibility_label.text()
    assert "State" in launcher.eligibility_label.text()
    assert launcher.begin_process_run() is False
    assert widget.trading_day_shell_widget.active_trading_run is None
