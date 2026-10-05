from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4

from ict_cockpit.analysis.trading_session_run import TradingSessionRun, TradingSessionRunStatus


class TradingDayLifecycleStatus(str, Enum):
    ACTIVE = "Active"
    COMPLETE = "Complete"


@dataclass
class TradingDay:
    """Top-level futures trading day that owns zero or more Session Runs."""

    futures_day_label: str = ""
    status: TradingDayLifecycleStatus = TradingDayLifecycleStatus.ACTIVE
    active_session_run_id: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    started_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )
    completed_at: str = ""
    updated_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        self.futures_day_label = self.futures_day_label.strip()
        self.active_session_run_id = self.active_session_run_id.strip()
        self.completed_at = self.completed_at.strip()
        if isinstance(self.status, str):
            self.status = TradingDayLifecycleStatus(self.status)

    def activate_session_run(self, session_run: TradingSessionRun) -> None:
        if self.status is TradingDayLifecycleStatus.COMPLETE:
            raise ValueError("completed trading day cannot start a session run")
        if session_run.trading_day_id != self.id:
            raise ValueError("session run must belong to this trading day")
        if session_run.status is not TradingSessionRunStatus.ACTIVE:
            raise ValueError("only an active session run can be activated")
        if self.active_session_run_id and self.active_session_run_id != session_run.id:
            raise ValueError("trading day already has an active session run")
        self.active_session_run_id = session_run.id
        self._touch()

    def conclude_session_run(self, session_run: TradingSessionRun, outcome: str = "") -> None:
        if session_run.trading_day_id != self.id:
            raise ValueError("session run must belong to this trading day")
        if self.active_session_run_id != session_run.id:
            raise ValueError("session run is not the active run for this trading day")
        session_run.conclude(outcome)
        self.active_session_run_id = ""
        self._touch()

    def complete(self) -> None:
        if self.active_session_run_id:
            raise ValueError("cannot complete trading day while a session run is active")
        if self.status is TradingDayLifecycleStatus.COMPLETE:
            return
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        self.status = TradingDayLifecycleStatus.COMPLETE
        self.completed_at = now
        self.updated_at = now

    def _touch(self) -> None:
        self.updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
