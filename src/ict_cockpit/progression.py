from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4


class ProgressionBoundary(str, Enum):
    """Canonical upward learning/progression boundaries."""

    STUDY_TO_REHEARSAL = "Study -> Rehearsal"
    REHEARSAL_TO_VALIDATION = "Rehearsal -> Validation"
    VALIDATION_TO_EXECUTION = "Validation -> Execution"


@dataclass
class ProgressionCertification:
    """Human confirmation used only for one explicit progression requirement."""

    trade_plan_id: str
    trade_plan_revision: str
    boundary: ProgressionBoundary
    requirement_id: str
    confirmed: bool = False
    note: str = ""
    confirmed_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        self.trade_plan_id = self.trade_plan_id.strip()
        self.trade_plan_revision = self.trade_plan_revision.strip()
        self.requirement_id = self.requirement_id.strip()
        self.note = self.note.strip()
        if isinstance(self.boundary, str):
            self.boundary = ProgressionBoundary(self.boundary)
        if not self.trade_plan_id:
            raise ValueError("trade plan id cannot be empty")
        if not self.trade_plan_revision:
            raise ValueError("trade plan revision cannot be empty")
        if not self.requirement_id:
            raise ValueError("progression certification requirement id cannot be empty")
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        if self.confirmed and not self.confirmed_at:
            self.confirmed_at = now
        if not self.updated_at:
            self.updated_at = now


class RegressionReviewClassification(str, Enum):
    REVALIDATION_REQUIRED = "Revalidation Required"
    CONFIRMED_COMPETENCY_REGRESSION = "Confirmed Competency Regression"
    EVIDENCE_GOVERNANCE_REASSESSMENT = "Evidence / Governance Reassessment"
    CERTIFICATION_WITHDRAWN = "Certification Withdrawn"
    NEEDS_STUDY_UNRESOLVED = "Needs Study / Unresolved"


@dataclass(frozen=True)
class ProgressionAttainment:
    """Immutable history that one configured progression boundary was crossed."""

    trade_plan_id: str
    trade_plan_revision: str
    boundary: ProgressionBoundary
    policy_id: str
    eligibility_snapshot: dict
    attained_environment: str
    attained_at: str = ""
    source: str = "Process Run Launcher"
    note: str = ""
    id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "trade_plan_id", self.trade_plan_id.strip())
        object.__setattr__(
            self, "trade_plan_revision", self.trade_plan_revision.strip()
        )
        if isinstance(self.boundary, str):
            object.__setattr__(
                self, "boundary", ProgressionBoundary(self.boundary)
            )
        object.__setattr__(self, "policy_id", self.policy_id.strip())
        object.__setattr__(
            self, "attained_environment", self.attained_environment.strip()
        )
        object.__setattr__(self, "source", self.source.strip() or "Process Run Launcher")
        object.__setattr__(self, "note", self.note.strip())
        object.__setattr__(
            self, "eligibility_snapshot", dict(self.eligibility_snapshot or {})
        )
        if not self.trade_plan_id:
            raise ValueError("trade plan id cannot be empty")
        if not self.trade_plan_revision:
            raise ValueError("trade plan revision cannot be empty")
        if not self.policy_id:
            raise ValueError("progression attainment policy id cannot be empty")
        if not self.attained_environment:
            raise ValueError("attained environment cannot be empty")
        if not self.eligibility_snapshot:
            raise ValueError("eligibility snapshot cannot be empty")
        if not self.attained_at:
            object.__setattr__(
                self,
                "attained_at",
                datetime.now().astimezone().isoformat(timespec="seconds"),
            )
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))


@dataclass
class ProgressionRegressionReview:
    """Human interpretation of lost support for a previously attained boundary."""

    trade_plan_id: str
    trade_plan_revision: str
    boundary: ProgressionBoundary
    prior_attainment_id: str
    eligibility_snapshot: dict
    classification: RegressionReviewClassification
    note: str = ""
    supporting_evidence_ids: list[str] = None
    source: str = "Review / Development"
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        self.trade_plan_id = self.trade_plan_id.strip()
        self.trade_plan_revision = self.trade_plan_revision.strip()
        if isinstance(self.boundary, str):
            self.boundary = ProgressionBoundary(self.boundary)
        self.prior_attainment_id = self.prior_attainment_id.strip()
        self.eligibility_snapshot = dict(self.eligibility_snapshot or {})
        if isinstance(self.classification, str):
            self.classification = RegressionReviewClassification(
                self.classification
            )
        self.note = self.note.strip()
        self.supporting_evidence_ids = [
            str(item).strip()
            for item in (self.supporting_evidence_ids or [])
            if str(item).strip()
        ]
        self.source = self.source.strip() or "Review / Development"
        if not self.trade_plan_id:
            raise ValueError("trade plan id cannot be empty")
        if not self.trade_plan_revision:
            raise ValueError("trade plan revision cannot be empty")
        if not self.prior_attainment_id:
            raise ValueError("prior attainment id cannot be empty")
        if not self.eligibility_snapshot:
            raise ValueError("eligibility snapshot cannot be empty")
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
