from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class TradingDaySession:
    """Runtime state for moving through the trading-day process modes."""

    blueprint_revision: str
    mode_ids: list[str]
    current_mode_id: str
    completed_mode_ids: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    updated_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        self.blueprint_revision = self.blueprint_revision.strip()
        self.mode_ids = [mode_id.strip() for mode_id in self.mode_ids]
        self.current_mode_id = self.current_mode_id.strip()
        self.completed_mode_ids = [mode_id.strip() for mode_id in self.completed_mode_ids]

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

    def mark_current_complete(self) -> None:
        if self.current_mode_id not in self.completed_mode_ids:
            self.completed_mode_ids.append(self.current_mode_id)

    def move_next(self) -> bool:
        index = self.current_mode_index
        if index >= len(self.mode_ids) - 1:
            return False
        self.mark_current_complete()
        self.current_mode_id = self.mode_ids[index + 1]
        return True

    def move_previous(self) -> bool:
        index = self.current_mode_index
        if index == 0:
            return False
        self.current_mode_id = self.mode_ids[index - 1]
        return True
