from dataclasses import replace

import pytest
from PySide6.QtWidgets import QApplication, QLabel

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


def maturity_requirement(
    *,
    requirement_id: str = "draw-maturity",
    competency_id: str = "draw-on-liquidity",
) -> ProgressionRequirementDefinition:
    return ProgressionRequirementDefinition(
        id=requirement_id,
        name="Draw evidence is decision-usable",
        requirement_kind=ProgressionRequirementKind.EVIDENCE_MATURITY_STATE,
        operator=ProgressionRequirementOperator.IS,
        expected_values=("Decision-Usable Evidence",),
        competency_id=competency_id,
    )


def test_default_alpha_07_has_no_configured_progression_policy() -> None:
    plan = build_default_trade_plan()

    assert plan.revision == "Alpha 0.7"
    assert plan.progression_policies == ()
    assert plan.progression_policy_snapshot() == []
    assert plan.progression_policy_by_boundary(
        ProgressionBoundary.STUDY_TO_REHEARSAL
    ) is None


def test_progression_policy_round_trips_all_v0_requirement_kinds() -> None:
    requirements = (
        maturity_requirement(),
        ProgressionRequirementDefinition(
            id="draw-state",
            name="Draw competency state permits validation",
            requirement_kind=ProgressionRequirementKind.COMPETENCY_STATE,
            operator=ProgressionRequirementOperator.IS_ONE_OF,
            expected_values=("Validation Needed", "Proficient"),
            competency_id="draw-on-liquidity",
        ),
        ProgressionRequirementDefinition(
            id="draw-rehearsal-evidence",
            name="Rehearsal evidence exists",
            requirement_kind=ProgressionRequirementKind.EVIDENCE_PURPOSE_PRESENT,
            operator=ProgressionRequirementOperator.EXISTS,
            expected_values=("Rehearsal",),
            competency_id="draw-on-liquidity",
        ),
        ProgressionRequirementDefinition(
            id="progression-review",
            name="Progression review completed",
            requirement_kind=ProgressionRequirementKind.HUMAN_CERTIFICATION,
            operator=ProgressionRequirementOperator.IS,
            expected_values=("Confirmed",),
            description="Boundary/global certification.",
        ),
    )
    policy = ProgressionPolicyDefinition(
        id="rehearsal-to-validation",
        boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        name="Rehearsal to Validation",
        description="Synthetic policy used to verify the C2 substrate.",
        requirements=requirements,
    )

    restored = ProgressionPolicyDefinition.from_dict(policy.to_dict())

    assert restored == policy
    assert restored.requirements[0].competency_id == "draw-on-liquidity"
    assert restored.requirements[-1].competency_id == ""


def test_trade_plan_validates_progression_policy_competency_references() -> None:
    plan = build_default_trade_plan()
    policy = ProgressionPolicyDefinition(
        id="unknown-competency-policy",
        boundary=ProgressionBoundary.STUDY_TO_REHEARSAL,
        name="Unknown competency policy",
        requirements=(
            maturity_requirement(
                competency_id="competency-that-does-not-exist",
            ),
        ),
    )

    with pytest.raises(ValueError, match="unknown competency"):
        replace(plan, progression_policies=(policy,))


def test_trade_plan_allows_at_most_one_policy_per_boundary() -> None:
    plan = build_default_trade_plan()
    first = ProgressionPolicyDefinition(
        id="policy-a",
        boundary=ProgressionBoundary.STUDY_TO_REHEARSAL,
        name="Policy A",
        requirements=(maturity_requirement(requirement_id="a"),),
    )
    second = ProgressionPolicyDefinition(
        id="policy-b",
        boundary=ProgressionBoundary.STUDY_TO_REHEARSAL,
        name="Policy B",
        requirements=(maturity_requirement(requirement_id="b"),),
    )

    with pytest.raises(ValueError, match="at most one progression policy"):
        replace(plan, progression_policies=(first, second))


def test_empty_progression_policy_is_invalid() -> None:
    with pytest.raises(ValueError, match="at least one gating requirement"):
        ProgressionPolicyDefinition(
            id="empty",
            boundary=ProgressionBoundary.VALIDATION_TO_EXECUTION,
            name="Empty policy",
            requirements=(),
        )


def test_requirement_kind_operator_combinations_are_validated() -> None:
    with pytest.raises(ValueError, match="Evidence Purpose Present requires EXISTS"):
        ProgressionRequirementDefinition(
            id="bad-purpose",
            name="Bad purpose requirement",
            requirement_kind=ProgressionRequirementKind.EVIDENCE_PURPOSE_PRESENT,
            operator=ProgressionRequirementOperator.IS,
            expected_values=("Rehearsal",),
            competency_id="draw-on-liquidity",
        )

    with pytest.raises(ValueError, match="Human Certification expected value"):
        ProgressionRequirementDefinition(
            id="bad-certification",
            name="Bad certification",
            requirement_kind=ProgressionRequirementKind.HUMAN_CERTIFICATION,
            operator=ProgressionRequirementOperator.IS,
            expected_values=("Yes",),
        )


def test_rules_safety_renders_progression_policy_without_evaluating_it() -> None:
    get_app()
    base_plan = build_default_trade_plan()
    policy = ProgressionPolicyDefinition(
        id="study-to-rehearsal-demo",
        boundary=ProgressionBoundary.STUDY_TO_REHEARSAL,
        name="Study to Rehearsal demo",
        requirements=(maturity_requirement(),),
    )
    configured_plan = replace(base_plan, progression_policies=(policy,))

    widget = TradePlanWidget(configured_plan)
    widget.section_list.setCurrentRow(1)
    page = widget.stack.currentWidget()
    text = "\n".join(label.text() for label in page.findChildren(QLabel))

    assert "Progression Policy" in text
    assert "Study -> Rehearsal" in text
    assert "Draw evidence is decision-usable" in text
    assert "Eligibility evaluation is a separate layer" in text

    unconfigured_widget = TradePlanWidget(base_plan)
    unconfigured_widget.section_list.setCurrentRow(1)
    unconfigured_page = unconfigured_widget.stack.currentWidget()
    unconfigured_text = "\n".join(
        label.text() for label in unconfigured_page.findChildren(QLabel)
    )
    assert "NOT CONFIGURED" in unconfigured_text
    assert "No readiness rule is inferred" in unconfigured_text
