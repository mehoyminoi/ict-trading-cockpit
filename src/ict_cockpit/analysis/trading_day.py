from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4

from ict_cockpit.analysis.trading_session_run import TradingRun, TradingRunStatus


class TradingDayLifecycleStatus(str, Enum):
    ACTIVE = "Active"
    COMPLETE = "Complete"


@dataclass
class TradingDay:
    """Top-level futures trading day that owns zero or more Trading Runs."""

    futures_day_label: str = ""
    status: TradingDayLifecycleStatus = TradingDayLifecycleStatus.ACTIVE
    # Persisted schema-v12 name retained for compatibility.
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

    @property
    def active_trading_run_id(self) -> str:
        return self.active_session_run_id

    @active_trading_run_id.setter
    def active_trading_run_id(self, value: str) -> None:
        self.active_session_run_id = value.strip()

    def activate_trading_run(self, trading_run: TradingRun) -> None:
        if self.status is TradingDayLifecycleStatus.COMPLETE:
            raise ValueError("completed trading day cannot start a trading run")
        if trading_run.trading_day_id != self.id:
            raise ValueError("trading run must belong to this trading day")
        if trading_run.status is not TradingRunStatus.ACTIVE:
            raise ValueError("only an active trading run can be activated")
        if self.active_trading_run_id and self.active_trading_run_id != trading_run.id:
            raise ValueError("trading day already has an active trading run")
        self.active_trading_run_id = trading_run.id
        self._touch()

    def conclude_trading_run(self, trading_run: TradingRun, outcome: str = "") -> None:
        if trading_run.trading_day_id != self.id:
            raise ValueError("trading run must belong to this trading day")
        if self.active_trading_run_id != trading_run.id:
            raise ValueError("trading run is not the active run for this trading day")
        trading_run.conclude(outcome)
        self.active_trading_run_id = ""
        self._touch()

    # Compatibility wrappers for schema-v12 callers/tests created during the
    # earlier market-session-specific iteration of this branch.
    def activate_session_run(self, session_run: TradingRun) -> None:
        self.activate_trading_run(session_run)

    def conclude_session_run(self, session_run: TradingRun, outcome: str = "") -> None:
        self.conclude_trading_run(session_run, outcome)

    def complete(self) -> None:
        if self.active_trading_run_id:
            raise ValueError("cannot complete trading day while a trading run is active")
        if self.status is TradingDayLifecycleStatus.COMPLETE:
            return
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        self.status = TradingDayLifecycleStatus.COMPLETE
        self.completed_at = now
        self.updated_at = now

    def _touch(self) -> None:
        self.updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
