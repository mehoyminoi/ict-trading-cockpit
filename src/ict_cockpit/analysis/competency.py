from dataclasses import dataclass
from datetime import datetime
from enum import Enum


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
