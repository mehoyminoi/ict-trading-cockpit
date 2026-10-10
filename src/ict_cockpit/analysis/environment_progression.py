from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ict_cockpit.analysis.trading_session_run import (
    RunEnvironment,
    RunPurpose,
    default_purpose_for_environment,
)
from ict_cockpit.progression import ProgressionBoundary
from ict_cockpit.trade_plan import (
    ProgressionRequirementKind,
    ProgressionRequirementOperator,
    TradePlanDefinition,
)


class EnvironmentEligibilityStatus(str, Enum):
    AVAILABLE = "Available"
    NOT_CONFIGURED = "Not Configured"
    BLOCKED = "Blocked"


class ProgressionRequirementStatus(str, Enum):
    SATISFIED = "Satisfied"
    NOT_SATISFIED = "Not Satisfied"
    UNKNOWN = "Unknown / Cannot Evaluate"


class ProgressionRequirementReason(str, Enum):
    REQUIREMENT_NOT_SATISFIED = "Requirement Not Satisfied"
    INSUFFICIENT_EVIDENCE = "Insufficient Evidence"
    CANNOT_EVALUATE = "Cannot Evaluate"
    HUMAN_CERTIFICATION_REQUIRED = "Human Certification Required"


class ProgressionStandingStatus(str, Enum):
    NOT_ATTAINED = "Not Yet Attained"
    AVAILABLE_NOT_ATTAINED = "Available · Not Yet Attained"
    ATTAINED_AVAILABLE = "Attained · Currently Available"
    ELIGIBILITY_LOSS_DETECTED = "Eligibility Loss Detected"
    REVALIDATION_REQUIRED = "Revalidation Required"
    HISTORICAL_ATTAINMENT = "Historical Attainment · Current Policy Not Configured"


@dataclass(frozen=True)
class ProgressionRequirementResult:
    requirement_id: str
    requirement_name: str
    requirement_kind: str
    competency_id: str
    status: ProgressionRequirementStatus
    detail: str
    expected_values: tuple[str, ...] = field(default_factory=tuple)
    observed_value: str = ""
    reason: ProgressionRequirementReason | None = None
    source_provenance: str = ""


@dataclass(frozen=True)
class ProgressionEligibilityResult:
    trade_plan_id: str
    trade_plan_revision: str
    boundary: ProgressionBoundary
    status: EnvironmentEligibilityStatus
    detail: str
    policy_id: str = ""
    requirement_results: tuple[ProgressionRequirementResult, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class ProgressionStanding:
    boundary: ProgressionBoundary
    status: ProgressionStandingStatus
    detail: str
    current_eligibility: ProgressionEligibilityResult
    prior_attainment: Any = None
    review_required: bool = False


@dataclass(frozen=True)
class EnvironmentEligibility:
    environment: RunEnvironment
    purpose: RunPurpose
    status: EnvironmentEligibilityStatus
    detail: str
    recommended_environment: RunEnvironment | None = None
    progression: ProgressionEligibilityResult | None = None

    @property
    def can_launch(self) -> bool:
        """A configured BLOCKED result prevents upward launch."""

        return self.status is not EnvironmentEligibilityStatus.BLOCKED


_ENVIRONMENT_BOUNDARY = {
    RunEnvironment.REPLAY: ProgressionBoundary.STUDY_TO_REHEARSAL,
    RunEnvironment.FORWARD_TEST: ProgressionBoundary.REHEARSAL_TO_VALIDATION,
    RunEnvironment.LIVE: ProgressionBoundary.VALIDATION_TO_EXECUTION,
}

_RECOMMENDED_LOWER = {
    RunEnvironment.REPLAY: RunEnvironment.HISTORICAL_BACKTEST,
    RunEnvironment.FORWARD_TEST: RunEnvironment.REPLAY,
    RunEnvironment.LIVE: RunEnvironment.FORWARD_TEST,
}


def progression_boundary_for_environment(
    environment: RunEnvironment | str,
) -> ProgressionBoundary | None:
    environment = RunEnvironment(environment)
    return _ENVIRONMENT_BOUNDARY.get(environment)


def environment_for_progression_boundary(
    boundary: ProgressionBoundary | str,
) -> RunEnvironment:
    boundary = ProgressionBoundary(boundary)
    for environment, candidate in _ENVIRONMENT_BOUNDARY.items():
        if candidate is boundary:
            return environment
    raise ValueError(f"no environment mapping for boundary: {boundary.value}")


def _compare_expected(
    observed: str,
    operator: ProgressionRequirementOperator,
    expected_values: tuple[str, ...],
) -> bool:
    if operator is ProgressionRequirementOperator.IS:
        return observed == expected_values[0]
    if operator is ProgressionRequirementOperator.IS_ONE_OF:
        return observed in expected_values
    raise ValueError(f"unsupported comparison operator: {operator.value}")


def _unknown_result(requirement, detail: str, *, provenance: str = ""):
    return ProgressionRequirementResult(
        requirement_id=requirement.id,
        requirement_name=requirement.name,
        requirement_kind=requirement.requirement_kind.value,
        competency_id=requirement.competency_id,
        status=ProgressionRequirementStatus.UNKNOWN,
        reason=ProgressionRequirementReason.CANNOT_EVALUATE,
        detail=detail,
        expected_values=requirement.expected_values,
        source_provenance=provenance,
    )


def _evaluate_requirement(
    *,
    trade_plan: TradePlanDefinition,
    boundary: ProgressionBoundary,
    requirement,
    competency_assessment_repository: Any = None,
    competency_evidence_repository: Any = None,
    competency_evidence_maturity_repository: Any = None,
    progression_certification_repository: Any = None,
) -> ProgressionRequirementResult:
    kind = requirement.requirement_kind

    if kind is ProgressionRequirementKind.COMPETENCY_STATE:
        if competency_assessment_repository is None:
            return _unknown_result(
                requirement,
                "Competency State source is unavailable.",
            )
        assessment = competency_assessment_repository.get(
            trade_plan.id,
            requirement.competency_id,
        )
        if assessment is None:
            return ProgressionRequirementResult(
                requirement_id=requirement.id,
                requirement_name=requirement.name,
                requirement_kind=kind.value,
                competency_id=requirement.competency_id,
                status=ProgressionRequirementStatus.NOT_SATISFIED,
                reason=ProgressionRequirementReason.INSUFFICIENT_EVIDENCE,
                detail="No competency assessment is recorded.",
                expected_values=requirement.expected_values,
                observed_value="Not assessed",
                source_provenance="CompetencyAssessment",
            )
        observed = assessment.state.value
        passed = _compare_expected(
            observed,
            requirement.operator,
            requirement.expected_values,
        )
        return ProgressionRequirementResult(
            requirement_id=requirement.id,
            requirement_name=requirement.name,
            requirement_kind=kind.value,
            competency_id=requirement.competency_id,
            status=(
                ProgressionRequirementStatus.SATISFIED
                if passed
                else ProgressionRequirementStatus.NOT_SATISFIED
            ),
            reason=(
                None
                if passed
                else ProgressionRequirementReason.REQUIREMENT_NOT_SATISFIED
            ),
            detail=(
                f"Competency State is {observed}."
                if passed
                else f"Competency State is {observed}; policy expectation is not met."
            ),
            expected_values=requirement.expected_values,
            observed_value=observed,
            source_provenance=(
                f"CompetencyAssessment · stored plan revision "
                f"{assessment.trade_plan_revision}"
            ),
        )

    if kind is ProgressionRequirementKind.EVIDENCE_MATURITY_STATE:
        if competency_evidence_maturity_repository is None:
            return _unknown_result(
                requirement,
                "Evidence Maturity source is unavailable.",
            )
        profile = competency_evidence_maturity_repository.get(
            trade_plan.id,
            requirement.competency_id,
            boundary.value,
        )
        if profile is None:
            return ProgressionRequirementResult(
                requirement_id=requirement.id,
                requirement_name=requirement.name,
                requirement_kind=kind.value,
                competency_id=requirement.competency_id,
                status=ProgressionRequirementStatus.NOT_SATISFIED,
                reason=ProgressionRequirementReason.INSUFFICIENT_EVIDENCE,
                detail="No Evidence Maturity profile is recorded for this boundary.",
                expected_values=requirement.expected_values,
                observed_value="No profile",
                source_provenance="CompetencyEvidenceMaturityProfile",
            )
        if profile.trade_plan_revision != trade_plan.revision:
            return ProgressionRequirementResult(
                requirement_id=requirement.id,
                requirement_name=requirement.name,
                requirement_kind=kind.value,
                competency_id=requirement.competency_id,
                status=ProgressionRequirementStatus.UNKNOWN,
                reason=ProgressionRequirementReason.CANNOT_EVALUATE,
                detail=(
                    "Evidence Maturity was last reviewed under Trade Plan "
                    f"{profile.trade_plan_revision}; current-plan review is required "
                    f"for {trade_plan.revision}."
                ),
                expected_values=requirement.expected_values,
                observed_value=profile.maturity_state.value,
                source_provenance=(
                    f"CompetencyEvidenceMaturityProfile · "
                    f"{profile.trade_plan_revision}"
                ),
            )
        observed = profile.maturity_state.value
        passed = _compare_expected(
            observed,
            requirement.operator,
            requirement.expected_values,
        )
        return ProgressionRequirementResult(
            requirement_id=requirement.id,
            requirement_name=requirement.name,
            requirement_kind=kind.value,
            competency_id=requirement.competency_id,
            status=(
                ProgressionRequirementStatus.SATISFIED
                if passed
                else ProgressionRequirementStatus.NOT_SATISFIED
            ),
            reason=(
                None
                if passed
                else ProgressionRequirementReason.REQUIREMENT_NOT_SATISFIED
            ),
            detail=(
                f"Evidence Maturity is {observed}."
                if passed
                else f"Evidence Maturity is {observed}; policy expectation is not met."
            ),
            expected_values=requirement.expected_values,
            observed_value=observed,
            source_provenance=(
                f"CompetencyEvidenceMaturityProfile · {trade_plan.revision}"
            ),
        )

    if kind is ProgressionRequirementKind.EVIDENCE_PURPOSE_PRESENT:
        if competency_evidence_repository is None:
            return _unknown_result(
                requirement,
                "Competency evidence source is unavailable.",
            )
        purpose = requirement.expected_values[0]
        evidence = competency_evidence_repository.list_for_competency(
            trade_plan.id,
            requirement.competency_id,
        )
        qualifying = [
            item
            for item in evidence
            if item.trade_plan_revision == trade_plan.revision
            and item.run_purpose == purpose
        ]
        if qualifying:
            run_count = len({item.trading_run_id for item in qualifying})
            return ProgressionRequirementResult(
                requirement_id=requirement.id,
                requirement_name=requirement.name,
                requirement_kind=kind.value,
                competency_id=requirement.competency_id,
                status=ProgressionRequirementStatus.SATISFIED,
                detail=(
                    f"{len(qualifying)} current-plan {purpose} evidence record(s) "
                    f"across {run_count} run(s) are present."
                ),
                expected_values=requirement.expected_values,
                observed_value=f"{len(qualifying)} record(s)",
                source_provenance=(
                    f"CompetencyEvidence · Trade Plan {trade_plan.revision}"
                ),
            )
        return ProgressionRequirementResult(
            requirement_id=requirement.id,
            requirement_name=requirement.name,
            requirement_kind=kind.value,
            competency_id=requirement.competency_id,
            status=ProgressionRequirementStatus.NOT_SATISFIED,
            reason=ProgressionRequirementReason.INSUFFICIENT_EVIDENCE,
            detail=(
                f"No reviewed {purpose} evidence is recorded for this competency "
                f"under Trade Plan {trade_plan.revision}."
            ),
            expected_values=requirement.expected_values,
            observed_value="0 record(s)",
            source_provenance=(
                f"CompetencyEvidence · Trade Plan {trade_plan.revision}"
            ),
        )

    if kind is ProgressionRequirementKind.HUMAN_CERTIFICATION:
        if progression_certification_repository is None:
            return _unknown_result(
                requirement,
                "Human Certification source is unavailable.",
            )
        certification = progression_certification_repository.get(
            trade_plan.id,
            trade_plan.revision,
            boundary,
            requirement.id,
        )
        if certification is None or not certification.confirmed:
            return ProgressionRequirementResult(
                requirement_id=requirement.id,
                requirement_name=requirement.name,
                requirement_kind=kind.value,
                competency_id=requirement.competency_id,
                status=ProgressionRequirementStatus.NOT_SATISFIED,
                reason=ProgressionRequirementReason.HUMAN_CERTIFICATION_REQUIRED,
                detail="Required human certification has not been confirmed.",
                expected_values=requirement.expected_values,
                observed_value="Not confirmed",
                source_provenance=(
                    f"ProgressionCertification · Trade Plan {trade_plan.revision}"
                ),
            )
        return ProgressionRequirementResult(
            requirement_id=requirement.id,
            requirement_name=requirement.name,
            requirement_kind=kind.value,
            competency_id=requirement.competency_id,
            status=ProgressionRequirementStatus.SATISFIED,
            detail="Required human certification is confirmed.",
            expected_values=requirement.expected_values,
            observed_value="Confirmed",
            source_provenance=(
                f"ProgressionCertification · Trade Plan {trade_plan.revision}"
            ),
        )

    return _unknown_result(
        requirement,
        f"Requirement kind {kind.value} is not supported by this evaluator.",
    )


def evaluate_progression_boundary(
    *,
    trade_plan: TradePlanDefinition,
    boundary: ProgressionBoundary | str,
    competency_assessment_repository: Any = None,
    competency_evidence_repository: Any = None,
    competency_evidence_maturity_repository: Any = None,
    progression_certification_repository: Any = None,
) -> ProgressionEligibilityResult:
    boundary = ProgressionBoundary(boundary)
    policy = trade_plan.progression_policy_by_boundary(boundary)

    if policy is None:
        return ProgressionEligibilityResult(
            trade_plan_id=trade_plan.id,
            trade_plan_revision=trade_plan.revision,
            boundary=boundary,
            status=EnvironmentEligibilityStatus.NOT_CONFIGURED,
            detail=(
                "No Trade Plan progression policy is published for this boundary. "
                "Readiness is unknown, not proven."
            ),
        )

    results = tuple(
        _evaluate_requirement(
            trade_plan=trade_plan,
            boundary=boundary,
            requirement=requirement,
            competency_assessment_repository=competency_assessment_repository,
            competency_evidence_repository=competency_evidence_repository,
            competency_evidence_maturity_repository=(
                competency_evidence_maturity_repository
            ),
            progression_certification_repository=(
                progression_certification_repository
            ),
        )
        for requirement in policy.requirements
    )

    blocked = [
        item
        for item in results
        if item.status is not ProgressionRequirementStatus.SATISFIED
    ]
    if not blocked:
        status = EnvironmentEligibilityStatus.AVAILABLE
        detail = (
            f"All {len(results)} configured progression requirement(s) are satisfied."
        )
    else:
        status = EnvironmentEligibilityStatus.BLOCKED
        unsatisfied = sum(
            item.status is ProgressionRequirementStatus.NOT_SATISFIED
            for item in blocked
        )
        unknown = sum(
            item.status is ProgressionRequirementStatus.UNKNOWN
            for item in blocked
        )
        parts = []
        if unsatisfied:
            parts.append(f"{unsatisfied} not satisfied")
        if unknown:
            parts.append(f"{unknown} cannot evaluate")
        detail = (
            "Configured progression policy is blocked: "
            + ", ".join(parts)
            + "."
        )

    return ProgressionEligibilityResult(
        trade_plan_id=trade_plan.id,
        trade_plan_revision=trade_plan.revision,
        policy_id=policy.id,
        boundary=boundary,
        status=status,
        detail=detail,
        requirement_results=results,
    )


def evaluate_environment_eligibility(
    environment: RunEnvironment | str,
    *,
    trade_plan: TradePlanDefinition | None = None,
    competency_assessment_repository: Any = None,
    competency_evidence_repository: Any = None,
    competency_evidence_maturity_repository: Any = None,
    progression_certification_repository: Any = None,
) -> EnvironmentEligibility:
    environment = RunEnvironment(environment)
    purpose = default_purpose_for_environment(environment)

    if environment is RunEnvironment.HISTORICAL_BACKTEST:
        return EnvironmentEligibility(
            environment=environment,
            purpose=purpose,
            status=EnvironmentEligibilityStatus.AVAILABLE,
            detail=(
                "Foundation study environment is available for focused concept "
                "practice and evidence collection."
            ),
        )

    boundary = _ENVIRONMENT_BOUNDARY[environment]
    recommended = _RECOMMENDED_LOWER[environment]

    if trade_plan is None:
        return EnvironmentEligibility(
            environment=environment,
            purpose=purpose,
            status=EnvironmentEligibilityStatus.NOT_CONFIGURED,
            detail=(
                "No Trade Plan progression criteria are published for this "
                "environment yet. Readiness is therefore unknown, not proven."
            ),
            recommended_environment=recommended,
        )

    progression = evaluate_progression_boundary(
        trade_plan=trade_plan,
        boundary=boundary,
        competency_assessment_repository=competency_assessment_repository,
        competency_evidence_repository=competency_evidence_repository,
        competency_evidence_maturity_repository=(
            competency_evidence_maturity_repository
        ),
        progression_certification_repository=progression_certification_repository,
    )
    return EnvironmentEligibility(
        environment=environment,
        purpose=purpose,
        status=progression.status,
        detail=progression.detail,
        recommended_environment=recommended,
        progression=progression,
    )



def progression_eligibility_to_dict(
    result: ProgressionEligibilityResult,
) -> dict:
    """Serialize a derived C3 result for immutable historical provenance."""

    return {
        "trade_plan_id": result.trade_plan_id,
        "trade_plan_revision": result.trade_plan_revision,
        "policy_id": result.policy_id,
        "boundary": result.boundary.value,
        "status": result.status.value,
        "detail": result.detail,
        "requirement_results": [
            {
                "requirement_id": item.requirement_id,
                "requirement_name": item.requirement_name,
                "requirement_kind": item.requirement_kind,
                "competency_id": item.competency_id,
                "status": item.status.value,
                "reason": item.reason.value if item.reason is not None else "",
                "detail": item.detail,
                "expected_values": list(item.expected_values),
                "observed_value": item.observed_value,
                "source_provenance": item.source_provenance,
            }
            for item in result.requirement_results
        ],
    }


def derive_progression_standing(
    *,
    trade_plan: TradePlanDefinition,
    eligibility: ProgressionEligibilityResult,
    progression_attainment_repository: Any = None,
) -> ProgressionStanding:
    """Compare current eligibility with immutable historical attainment.

    This comparison may identify eligibility loss or revalidation work, but it
    never infers competency regression.
    """

    if progression_attainment_repository is None:
        return ProgressionStanding(
            boundary=eligibility.boundary,
            status=(
                ProgressionStandingStatus.AVAILABLE_NOT_ATTAINED
                if eligibility.status is EnvironmentEligibilityStatus.AVAILABLE
                else ProgressionStandingStatus.NOT_ATTAINED
            ),
            detail="Progression attainment history is unavailable.",
            current_eligibility=eligibility,
        )

    prior = progression_attainment_repository.latest_for_boundary(
        trade_plan.id,
        eligibility.boundary,
    )

    if prior is None:
        status = (
            ProgressionStandingStatus.AVAILABLE_NOT_ATTAINED
            if eligibility.status is EnvironmentEligibilityStatus.AVAILABLE
            else ProgressionStandingStatus.NOT_ATTAINED
        )
        detail = (
            "This boundary is available but has not yet been deliberately crossed."
            if status is ProgressionStandingStatus.AVAILABLE_NOT_ATTAINED
            else "No historical attainment is recorded for this boundary."
        )
        return ProgressionStanding(
            boundary=eligibility.boundary,
            status=status,
            detail=detail,
            current_eligibility=eligibility,
        )

    if eligibility.status is EnvironmentEligibilityStatus.NOT_CONFIGURED:
        return ProgressionStanding(
            boundary=eligibility.boundary,
            status=ProgressionStandingStatus.HISTORICAL_ATTAINMENT,
            detail=(
                f"Historical attainment exists under Trade Plan "
                f"{prior.trade_plan_revision}, while the current boundary has "
                "no configured progression policy."
            ),
            current_eligibility=eligibility,
            prior_attainment=prior,
        )

    same_governing_context = (
        prior.trade_plan_revision == trade_plan.revision
        and prior.policy_id == eligibility.policy_id
    )

    if eligibility.status is EnvironmentEligibilityStatus.AVAILABLE:
        if same_governing_context:
            return ProgressionStanding(
                boundary=eligibility.boundary,
                status=ProgressionStandingStatus.ATTAINED_AVAILABLE,
                detail=(
                    "This boundary was previously attained under the current "
                    "Trade Plan policy and is currently available."
                ),
                current_eligibility=eligibility,
                prior_attainment=prior,
            )
        return ProgressionStanding(
            boundary=eligibility.boundary,
            status=ProgressionStandingStatus.AVAILABLE_NOT_ATTAINED,
            detail=(
                f"A historical attainment exists under Trade Plan "
                f"{prior.trade_plan_revision}, but the current revision/policy "
                "has not yet been deliberately attained."
            ),
            current_eligibility=eligibility,
            prior_attainment=prior,
        )

    if same_governing_context:
        return ProgressionStanding(
            boundary=eligibility.boundary,
            status=ProgressionStandingStatus.ELIGIBILITY_LOSS_DETECTED,
            detail=(
                "This boundary was previously attained under the same Trade Plan "
                "policy, but current eligibility is now BLOCKED. This is an "
                "eligibility-loss condition, not an automatic competency-regression "
                "conclusion."
            ),
            current_eligibility=eligibility,
            prior_attainment=prior,
            review_required=True,
        )

    return ProgressionStanding(
        boundary=eligibility.boundary,
        status=ProgressionStandingStatus.REVALIDATION_REQUIRED,
        detail=(
            f"Historical attainment exists under Trade Plan "
            f"{prior.trade_plan_revision}, but the current Trade Plan "
            f"{trade_plan.revision} does not currently satisfy this boundary. "
            "Fresh contextual validation/review is required; prior competency "
            "knowledge is not erased."
        ),
        current_eligibility=eligibility,
        prior_attainment=prior,
        review_required=True,
    )
