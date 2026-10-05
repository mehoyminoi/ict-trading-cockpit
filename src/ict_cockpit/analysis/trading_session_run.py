from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


SESSION_NAMES = ("Asia", "London", "NYAM", "NYPM")


class TradingSessionRunStatus(str, Enum):
    ACTIVE = "Active"
    CONCLUDED = "Concluded"


@dataclass
class TradingSessionRun:
    """One deliberate market-session operating run inside a Trading Day."""

    trading_day_id: str
    session_name: str
    process_session_id: str
    tda_station_session_id: str = ""
    status: TradingSessionRunStatus = TradingSessionRunStatus.ACTIVE
    outcome: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    started_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )
    concluded_at: str = ""
    updated_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        self.trading_day_id = self.trading_day_id.strip()
        self.session_name = self.session_name.strip()
        self.process_session_id = self.process_session_id.strip()
        self.tda_station_session_id = self.tda_station_session_id.strip()
        self.outcome = self.outcome.strip()
        self.concluded_at = self.concluded_at.strip()
        if isinstance(self.status, str):
            self.status = TradingSessionRunStatus(self.status)

        if not self.trading_day_id:
            raise ValueError("trading day id cannot be empty")
        if not self.session_name:
            raise ValueError("session name cannot be empty")
        if not self.process_session_id:
            raise ValueError("process session id cannot be empty")

    def conclude(self, outcome: str = "") -> None:
        """Conclude this run without implying that the Trading Day is complete."""
        if self.status is TradingSessionRunStatus.CONCLUDED:
            return
        self.outcome = outcome.strip()
        self.status = TradingSessionRunStatus.CONCLUDED
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        self.concluded_at = now
        self.updated_at = now
