from dataclasses import dataclass
from datetime import datetime
from enum import Enum


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
