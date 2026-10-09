from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4


class DevelopmentDirection(str, Enum):
    STUDY = "Study"
    REHEARSAL = "Rehearsal"
    VALIDATION = "Validation"
    MONITOR = "Monitor / Gather Evidence"
    NO_ACTIVE_FOCUS = "No Active Focus"


class CompetencyState(str, Enum):
    NOT_ASSESSED = "Not Assessed"
    UNDER_STUDY = "Under Study"
    REHEARSAL_NEEDED = "Rehearsal Needed"
    VALIDATION_NEEDED = "Validation Needed"
    PROFICIENT = "Proficient"


@dataclass
class CompetencyAssessment:
    trade_plan_id: str
    trade_plan_revision: str
    competency_id: str
    state: CompetencyState = CompetencyState.NOT_ASSESSED
    note: str = ""
    source: str = "Manual"
    updated_at: str = ""

    def __post_init__(self) -> None:
        self.trade_plan_id = self.trade_plan_id.strip()
        self.trade_plan_revision = self.trade_plan_revision.strip()
        self.competency_id = self.competency_id.strip()
        self.note = self.note.strip()
        self.source = self.source.strip() or "Manual"
        if isinstance(self.state, str):
            self.state = CompetencyState(self.state)
        if not self.trade_plan_id:
            raise ValueError("trade plan id cannot be empty")
        if not self.trade_plan_revision:
            raise ValueError("trade plan revision cannot be empty")
        if not self.competency_id:
            raise ValueError("competency id cannot be empty")
        if not self.updated_at:
            self.updated_at = datetime.now().astimezone().isoformat(
                timespec="seconds"
            )

    def set_state(
        self,
        state: CompetencyState | str,
        *,
        note: str = "",
        source: str = "Manual",
    ) -> None:
        self.state = CompetencyState(state)
        self.note = note.strip()
        self.source = source.strip() or "Manual"
        self.updated_at = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

@dataclass
class CompetencyEvidence:
    """One human-legible evidence record tied to a plan-owned competency."""

    trade_plan_id: str
    trade_plan_revision: str
    competency_id: str
    competency_name: str
    competency_category: str
    trading_run_id: str
    run_environment: str
    run_purpose: str
    study_outcome: str
    note: str = ""
    study_question: str = ""
    study_hypothesis: str = ""
    study_scope: str = ""
    market_time_context: dict = None
    qt_context: dict = None
    source: str = "Study Review"
    recorded_at: str = ""
    id: str = ""

    def __post_init__(self) -> None:
        self.trade_plan_id = self.trade_plan_id.strip()
        self.trade_plan_revision = self.trade_plan_revision.strip()
        self.competency_id = self.competency_id.strip()
        self.competency_name = self.competency_name.strip() or self.competency_id
        self.competency_category = self.competency_category.strip()
        self.trading_run_id = self.trading_run_id.strip()
        self.run_environment = self.run_environment.strip()
        self.run_purpose = self.run_purpose.strip()
        self.study_outcome = self.study_outcome.strip()
        self.note = self.note.strip()
        self.study_question = self.study_question.strip()
        self.study_hypothesis = self.study_hypothesis.strip()
        self.study_scope = self.study_scope.strip()
        self.market_time_context = dict(self.market_time_context or {})
        self.qt_context = dict(self.qt_context or {})
        self.source = self.source.strip() or "Study Review"
        self.recorded_at = self.recorded_at.strip()
        self.id = self.id.strip() or str(uuid4())

        if not self.trade_plan_id:
            raise ValueError("trade plan id cannot be empty")
        if not self.trade_plan_revision:
            raise ValueError("trade plan revision cannot be empty")
        if not self.competency_id:
            raise ValueError("competency id cannot be empty")
        if not self.trading_run_id:
            raise ValueError("trading run id cannot be empty")
        if not self.run_environment:
            raise ValueError("run environment cannot be empty")
        if not self.run_purpose:
            raise ValueError("run purpose cannot be empty")
        if not self.study_outcome:
            raise ValueError("study outcome cannot be empty")
        if not self.recorded_at:
            self.recorded_at = datetime.now().astimezone().isoformat(
                timespec="seconds"
            )



@dataclass
class CompetencyDevelopmentDirection:
    """Current human-reviewed development direction for one competency."""

    trade_plan_id: str
    trade_plan_revision: str
    competency_id: str
    direction: DevelopmentDirection = DevelopmentDirection.NO_ACTIVE_FOCUS
    note: str = ""
    supporting_evidence_ids: list[str] = None
    source: str = "Review / Development"
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        self.trade_plan_id = self.trade_plan_id.strip()
        self.trade_plan_revision = self.trade_plan_revision.strip()
        self.competency_id = self.competency_id.strip()
        if isinstance(self.direction, str):
            self.direction = DevelopmentDirection(self.direction)
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
        if not self.competency_id:
            raise ValueError("competency id cannot be empty")
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now



@dataclass
class CompetencyCrossRunObservation:
    """Current human-authored cross-run observation for one competency."""

    trade_plan_id: str
    trade_plan_revision: str
    competency_id: str
    observation: str = ""
    supporting_evidence_ids: list[str] = None
    source: str = "Review / Development"
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        self.trade_plan_id = self.trade_plan_id.strip()
        self.trade_plan_revision = self.trade_plan_revision.strip()
        self.competency_id = self.competency_id.strip()
        self.observation = self.observation.strip()
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
        if not self.competency_id:
            raise ValueError("competency id cannot be empty")
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
