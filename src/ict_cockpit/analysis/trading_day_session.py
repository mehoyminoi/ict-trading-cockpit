from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class TradingDayStatus(str, Enum):
    ACTIVE = "Active"
    COMPLETE = "Complete"


class TransitionOutcome(str, Enum):
    ADVANCE = "Advance"
    RETURN_TO_ANALYSIS = "Return to Analysis"
    STAND_DOWN = "Stand Down / No Trade"
    COMPLETE_DAY = "Complete Trading Day"


@dataclass
class TradingDayTransition:
    """One intentional process transition recorded during a trading day."""

    from_mode_id: str
    to_mode_id: str | None
    outcome: TransitionOutcome
    reason: str = ""
    override_incomplete: bool = False
    created_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        self.from_mode_id = self.from_mode_id.strip()
        self.to_mode_id = self.to_mode_id.strip() if self.to_mode_id else None
        self.reason = self.reason.strip()
        if not self.from_mode_id:
            raise ValueError("transition source mode cannot be empty")


@dataclass
class TradingDaySession:
    """Runtime state for moving intentionally through trading-day process modes."""

    blueprint_revision: str
    mode_ids: list[str]
    current_mode_id: str
    completed_mode_ids: list[str] = field(default_factory=list)
    status: TradingDayStatus = TradingDayStatus.ACTIVE
    day_outcome: str = ""
    transitions: list[TradingDayTransition] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    updated_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        self.blueprint_revision = self.blueprint_revision.strip()
        self.mode_ids = [mode_id.strip() for mode_id in self.mode_ids]
        self.current_mode_id = self.current_mode_id.strip()
        self.completed_mode_ids = [mode_id.strip() for mode_id in self.completed_mode_ids]
        self.day_outcome = self.day_outcome.strip()
        if isinstance(self.status, str):
            self.status = TradingDayStatus(self.status)

        if not self.blueprint_revision:
            raise ValueError("blueprint revision cannot be empty")
        if not self.mode_ids or any(not mode_id for mode_id in self.mode_ids):
            raise ValueError("trading day session must contain mode ids")
        if len(self.mode_ids) != len(set(self.mode_ids)):
            raise ValueError("mode ids must be unique")
        if self.current_mode_id not in self.mode_ids:
            raise ValueError("current mode must exist in mode ids")
        if any(mode_id not in self.mode_ids for mode_id in self.completed_mode_ids):
            raise ValueError("completed modes must exist in mode ids")

    @property
    def current_mode_index(self) -> int:
        return self.mode_ids.index(self.current_mode_id)

    def mark_mode_complete(self, mode_id: str) -> None:
        if mode_id not in self.mode_ids:
            raise ValueError("mode must exist in trading day session")
        if mode_id not in self.completed_mode_ids:
            self.completed_mode_ids.append(mode_id)

    def mark_current_complete(self) -> None:
        self.mark_mode_complete(self.current_mode_id)

    def transition_to(
        self,
        target_mode_id: str,
        outcome: TransitionOutcome,
        *,
        reason: str = "",
        override_incomplete: bool = False,
        mark_source_complete: bool = True,
    ) -> None:
        if self.status is TradingDayStatus.COMPLETE:
            raise ValueError("completed trading day cannot transition")
        if target_mode_id not in self.mode_ids:
            raise ValueError("target mode must exist in trading day session")

        source_mode_id = self.current_mode_id
        if mark_source_complete:
            self.mark_mode_complete(source_mode_id)
        self.transitions.append(
            TradingDayTransition(
                from_mode_id=source_mode_id,
                to_mode_id=target_mode_id,
                outcome=outcome,
                reason=reason,
                override_incomplete=override_incomplete,
            )
        )
        self.current_mode_id = target_mode_id

    def advance(
        self,
        *,
        reason: str = "",
        override_incomplete: bool = False,
    ) -> bool:
        index = self.current_mode_index
        if index >= len(self.mode_ids) - 1:
            return False
        self.transition_to(
            self.mode_ids[index + 1],
            TransitionOutcome.ADVANCE,
            reason=reason,
            override_incomplete=override_incomplete,
        )
        return True

    def return_to_analysis(self, analysis_mode_id: str = "tda", *, reason: str = "") -> None:
        if analysis_mode_id not in self.mode_ids:
            raise ValueError("analysis mode must exist in trading day session")
        self.completed_mode_ids = [
            mode_id for mode_id in self.completed_mode_ids if mode_id != analysis_mode_id
        ]
        self.transition_to(
            analysis_mode_id,
            TransitionOutcome.RETURN_TO_ANALYSIS,
            reason=reason,
            mark_source_complete=False,
        )

    def stand_down(self, review_mode_id: str = "post-market", *, reason: str = "") -> None:
        if review_mode_id not in self.mode_ids:
            raise ValueError("review mode must exist in trading day session")
        self.day_outcome = TransitionOutcome.STAND_DOWN.value
        self.transition_to(
            review_mode_id,
            TransitionOutcome.STAND_DOWN,
            reason=reason,
        )

    def complete_day(self, *, reason: str = "") -> None:
        if self.status is TradingDayStatus.COMPLETE:
            return
        self.mark_current_complete()
        self.transitions.append(
            TradingDayTransition(
                from_mode_id=self.current_mode_id,
                to_mode_id=None,
                outcome=TransitionOutcome.COMPLETE_DAY,
                reason=reason,
            )
        )
        self.status = TradingDayStatus.COMPLETE
        if not self.day_outcome:
            self.day_outcome = "Trading Day Complete"

    # Backward-compatible helpers retained while callers migrate to explicit outcomes.
    def move_next(self) -> bool:
        return self.advance()

    def move_previous(self) -> bool:
        index = self.current_mode_index
        if index == 0:
            return False
        self.current_mode_id = self.mode_ids[index - 1]
        return True
