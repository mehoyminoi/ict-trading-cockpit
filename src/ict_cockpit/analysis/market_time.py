from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


MARKET_TIMEZONE_NAME = "America/New_York"
MARKET_TIMEZONE = ZoneInfo(MARKET_TIMEZONE_NAME)


@dataclass(frozen=True)
class TimedWindowContext:
    id: str
    name: str
    start_time: str
    end_time: str
    state: str
    minutes_until_start: int | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "state": self.state,
            "minutes_until_start": self.minutes_until_start,
        }


@dataclass(frozen=True)
class MarketTimeContext:
    """Factual New York market-time state.

    This layer intentionally stops at temporal facts. It does not infer AMDX/XAMD
    meaning; those interpretations belong to a Trade Plan or technician thesis.
    """

    captured_at: str
    timezone: str
    source: str
    futures_trading_day: str
    market_open: bool
    weekday: str
    session: str
    daily_quarter: str
    session_quarter: str
    timed_windows: tuple[TimedWindowContext, ...] = field(default_factory=tuple)
    active_window_ids: tuple[str, ...] = field(default_factory=tuple)
    next_window_id: str = ""

    def to_dict(self) -> dict:
        return {
            "captured_at": self.captured_at,
            "timezone": self.timezone,
            "source": self.source,
            "futures_trading_day": self.futures_trading_day,
            "market_open": self.market_open,
            "weekday": self.weekday,
            "session": self.session,
            "daily_quarter": self.daily_quarter,
            "session_quarter": self.session_quarter,
            "timed_windows": [item.to_dict() for item in self.timed_windows],
            "active_window_ids": list(self.active_window_ids),
            "next_window_id": self.next_window_id,
        }


_SESSION_BOUNDS = (
    ("Asia", 18 * 60, 24 * 60),
    ("London", 0, 6 * 60),
    ("NYAM", 6 * 60, 12 * 60),
    ("NYPM", 12 * 60, 18 * 60),
)

_DAILY_QUARTERS = {
    "Asia": "Q1",
    "London": "Q2",
    "NYAM": "Q3",
    "NYPM": "Q4",
}

_TIMED_WINDOWS = (
    ("london-silver-bullet", "London Silver Bullet", 3 * 60, 4 * 60),
    ("nyam-silver-bullet", "NYAM Silver Bullet", 10 * 60, 11 * 60),
    ("ny-lunch-silver-bullet", "NY Lunch Silver Bullet", 12 * 60, 13 * 60),
    ("nypm-silver-bullet", "NYPM Silver Bullet", 14 * 60, 15 * 60),
)


def as_new_york(moment: datetime) -> datetime:
    """Return an aware America/New_York datetime.

    Naive datetimes are interpreted as already being New York wall-clock time.
    This is useful for explicit Replay / Historical Backtest timestamps.
    """

    if moment.tzinfo is None:
        return moment.replace(tzinfo=MARKET_TIMEZONE)
    return moment.astimezone(MARKET_TIMEZONE)


def current_new_york_time() -> datetime:
    return datetime.now(tz=MARKET_TIMEZONE)


def futures_trading_day_for(moment: datetime) -> date:
    """Apply the cockpit's 18:00 New York futures-day boundary."""

    local = as_new_york(moment)
    rollover = local.date()
    if local.time() >= time(18, 0):
        rollover += timedelta(days=1)
    return rollover


def market_is_open(moment: datetime) -> bool:
    """Return the coarse futures-week availability used by the cockpit.

    Intraday maintenance gaps are intentionally outside v0. The operating
    process currently treats 18:00 ET as the direct NYPM -> Asia boundary.
    """

    local = as_new_york(moment)
    weekday = local.weekday()  # Monday=0, Sunday=6
    minute = local.hour * 60 + local.minute
    if weekday == 5:
        return False
    if weekday == 4 and minute >= 18 * 60:
        return False
    if weekday == 6 and minute < 18 * 60:
        return False
    return True


def session_for(moment: datetime) -> str:
    local = as_new_york(moment)
    if not market_is_open(local):
        return "Closed"
    minute = local.hour * 60 + local.minute
    for name, start, end in _SESSION_BOUNDS:
        if start <= minute < end:
            return name
    return "Closed"


def session_quarter_for(moment: datetime, session: str | None = None) -> str:
    local = as_new_york(moment)
    session = session or session_for(local)
    if session not in _DAILY_QUARTERS:
        return ""
    minute = local.hour * 60 + local.minute
    start = next(start for name, start, _end in _SESSION_BOUNDS if name == session)
    offset = minute - start
    quarter = max(1, min(4, offset // 90 + 1))
    return f"Q{quarter}"


def _window_contexts(moment: datetime) -> tuple[tuple[TimedWindowContext, ...], tuple[str, ...], str]:
    local = as_new_york(moment)
    current_minute = local.hour * 60 + local.minute
    windows: list[TimedWindowContext] = []
    active_ids: list[str] = []
    next_window_id = ""

    for window_id, name, start, end in _TIMED_WINDOWS:
        if start <= current_minute < end and market_is_open(local):
            state = "Active"
            minutes_until = 0
            active_ids.append(window_id)
        elif current_minute < start:
            state = "Upcoming"
            minutes_until = start - current_minute
            if not next_window_id and market_is_open(local):
                next_window_id = window_id
        else:
            state = "Closed"
            minutes_until = None

        windows.append(
            TimedWindowContext(
                id=window_id,
                name=name,
                start_time=f"{start // 60:02d}:{start % 60:02d}",
                end_time=f"{end // 60:02d}:{end % 60:02d}",
                state=state,
                minutes_until_start=minutes_until,
            )
        )

    return tuple(windows), tuple(active_ids), next_window_id


def build_market_time_context(
    moment: datetime | None = None,
    *,
    source: str = "Live Clock",
) -> MarketTimeContext:
    local = as_new_york(moment or current_new_york_time())
    session = session_for(local)
    windows, active_ids, next_window_id = _window_contexts(local)
    return MarketTimeContext(
        captured_at=local.isoformat(timespec="seconds"),
        timezone=MARKET_TIMEZONE_NAME,
        source=source.strip() or "Unknown",
        futures_trading_day=futures_trading_day_for(local).isoformat(),
        market_open=market_is_open(local),
        weekday=local.strftime("%A"),
        session=session,
        daily_quarter=_DAILY_QUARTERS.get(session, ""),
        session_quarter=session_quarter_for(local, session),
        timed_windows=windows,
        active_window_ids=active_ids,
        next_window_id=next_window_id,
    )
