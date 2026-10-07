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
    calendar_quarter: str
    calendar_quarter_month_index: int
    calendar_month_phase: str
    raw_quarters: dict[str, str] = field(default_factory=dict)
    raw_quarter_layers: tuple[dict, ...] = field(default_factory=tuple)
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
            "calendar_quarter": self.calendar_quarter,
            "calendar_quarter_month_index": self.calendar_quarter_month_index,
            "calendar_month_phase": self.calendar_month_phase,
            "raw_quarters": dict(self.raw_quarters),
            "raw_quarter_layers": [dict(item) for item in self.raw_quarter_layers],
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


def calendar_quarter_for(moment: datetime) -> str:
    local = as_new_york(moment)
    return f"Q{((local.month - 1) // 3) + 1}"


def calendar_quarter_month_index_for(moment: datetime) -> int:
    local = as_new_york(moment)
    return ((local.month - 1) % 3) + 1


def calendar_month_phase_for(moment: datetime) -> str:
    """Return the mentorship-group monthly PO3 role inside a calendar quarter."""

    index = calendar_quarter_month_index_for(moment)
    return {1: "A", 2: "M", 3: "D"}[index]


def cycle_16y_quarter_for(moment: datetime) -> str:
    """Return the active 4-year quarter inside the anchored 16-year cycle."""

    local = as_new_york(moment)
    quarter = ((local.year - 2011) % 16) // 4 + 1
    return f"Q{quarter}"


def quadrennial_year_quarter_for(moment: datetime) -> str:
    """Return the active year quarter inside its four-year block."""

    local = as_new_york(moment)
    quarter = ((local.year - 2011) % 4) + 1
    return f"Q{quarter}"


def month_week_quarter_for(moment: datetime) -> str:
    """Return Q1-Q4 for full Monday-start weeks; fifth week is Distortion.

    Days before the first Monday of the futures trading-day month are left
    unassigned rather than inferred.
    """

    trading_date = futures_trading_day_for(moment)
    first_day = trading_date.replace(day=1)
    days_to_monday = (7 - first_day.weekday()) % 7
    first_monday = first_day + timedelta(days=days_to_monday)
    if trading_date < first_monday:
        return ""

    week_index = ((trading_date - first_monday).days // 7) + 1
    if 1 <= week_index <= 4:
        return f"Q{week_index}"
    return "Distortion"


def week_day_quarter_for(moment: datetime) -> str:
    """Return Mon-Thu Q1-Q4 using the futures trading-day date."""

    trading_date = futures_trading_day_for(moment)
    weekday = trading_date.weekday()
    if 0 <= weekday <= 3:
        return f"Q{weekday + 1}"
    return ""


def raw_qt_quarters_for(
    moment: datetime,
    *,
    session: str | None = None,
) -> dict[str, str]:
    """Return factual raw nested QT positions without AMDX interpretation."""

    local = as_new_york(moment)
    active_session = session or session_for(local)
    day_quarter = _DAILY_QUARTERS.get(active_session, "")
    session_quarter = session_quarter_for(local, active_session)
    return {
        "cycle_16y": cycle_16y_quarter_for(local),
        "quadrennial": quadrennial_year_quarter_for(local),
        "year": calendar_quarter_for(local),
        "month": month_week_quarter_for(local),
        "week": week_day_quarter_for(local),
        "day": day_quarter,
        "session": session_quarter,
    }


def _format_date_range(start: date, end: date) -> str:
    if start.year == end.year:
        if start.month == end.month:
            return f"{start.strftime('%b')} {start.day}–{end.day}, {start.year}"
        return f"{start.strftime('%b')} {start.day}–{end.strftime('%b')} {end.day}, {start.year}"
    return f"{start.isoformat()}–{end.isoformat()}"


def raw_qt_layer_contexts_for(
    moment: datetime,
    *,
    session: str | None = None,
) -> tuple[dict, ...]:
    """Describe what each raw QT quarter refers to and its effective interval."""

    local = as_new_york(moment)
    trading_date = futures_trading_day_for(local)
    active_session = session or session_for(local)
    raw = raw_qt_quarters_for(local, session=active_session)

    cycle_start_year = local.year - ((local.year - 2011) % 16)
    block_start_year = local.year - ((local.year - 2011) % 4)

    calendar_q = ((local.month - 1) // 3) + 1
    quarter_start_month = (calendar_q - 1) * 3 + 1
    quarter_start = date(local.year, quarter_start_month, 1)
    if calendar_q == 4:
        quarter_end = date(local.year, 12, 31)
    else:
        quarter_end = date(local.year, quarter_start_month + 3, 1) - timedelta(days=1)

    first_day = trading_date.replace(day=1)
    first_monday = first_day + timedelta(days=(7 - first_day.weekday()) % 7)
    month_value = raw.get("month", "")
    if month_value.startswith("Q"):
        month_week_index = int(month_value[1])
        month_child_start = first_monday + timedelta(days=7 * (month_week_index - 1))
        month_child_end = month_child_start + timedelta(days=6)
        month_child_label = f"Monday-week {_format_date_range(month_child_start, month_child_end)}"
    elif month_value == "Distortion":
        month_child_start = first_monday + timedelta(days=28)
        month_child_end = month_child_start + timedelta(days=6)
        month_child_label = f"Fifth Monday-week {_format_date_range(month_child_start, month_child_end)}"
    else:
        month_child_start = None
        month_child_end = None
        month_child_label = "Before first Monday-start week"

    week_start = trading_date - timedelta(days=trading_date.weekday())
    week_end = week_start + timedelta(days=4)

    trading_day_start = datetime.combine(
        trading_date - timedelta(days=1),
        time(18, 0),
        tzinfo=MARKET_TIMEZONE,
    )
    trading_day_end = datetime.combine(
        trading_date,
        time(18, 0),
        tzinfo=MARKET_TIMEZONE,
    )

    session_bounds = next(
        ((start, end) for name, start, end in _SESSION_BOUNDS if name == active_session),
        None,
    )
    session_start_dt = None
    session_end_dt = None
    macro_start_dt = None
    macro_end_dt = None
    if session_bounds is not None:
        start_minute, end_minute = session_bounds
        session_date = local.date()
        session_start_dt = datetime.combine(
            session_date,
            time(start_minute // 60, start_minute % 60),
            tzinfo=MARKET_TIMEZONE,
        )
        session_end_hour = 0 if end_minute == 24 * 60 else end_minute // 60
        session_end_date = session_date + (timedelta(days=1) if end_minute == 24 * 60 else timedelta())
        session_end_dt = datetime.combine(
            session_end_date,
            time(session_end_hour, end_minute % 60),
            tzinfo=MARKET_TIMEZONE,
        )
        session_q = raw.get("session", "")
        if session_q.startswith("Q"):
            macro_index = int(session_q[1]) - 1
            macro_start_dt = session_start_dt + timedelta(minutes=90 * macro_index)
            macro_end_dt = macro_start_dt + timedelta(minutes=90)

    def layer(
        level_id: str,
        short_label: str,
        parent_label: str,
        child_label: str,
        start_value,
        end_value,
    ) -> dict:
        return {
            "id": level_id,
            "short_label": short_label,
            "quarter": raw.get(level_id, ""),
            "parent_label": parent_label,
            "active_child_label": child_label,
            "effective_start": start_value.isoformat() if start_value is not None else "",
            "effective_end": end_value.isoformat() if end_value is not None else "",
            "source": "Derived",
        }

    return (
        layer(
            "cycle_16y",
            "16Y",
            f"16Y Cycle {cycle_start_year}–{cycle_start_year + 15}",
            f"4-year block {block_start_year}–{block_start_year + 3}",
            date(block_start_year, 1, 1),
            date(block_start_year + 3, 12, 31),
        ),
        layer(
            "quadrennial",
            "4Y",
            f"Quadrennial {block_start_year}–{block_start_year + 3}",
            f"Year {local.year}",
            date(local.year, 1, 1),
            date(local.year, 12, 31),
        ),
        layer(
            "year",
            "Year",
            f"Calendar Year {local.year}",
            f"{quarter_start.strftime('%b')}–{quarter_end.strftime('%b')}",
            quarter_start,
            quarter_end,
        ),
        layer(
            "month",
            "Month",
            local.strftime("%B %Y"),
            month_child_label,
            month_child_start,
            month_child_end,
        ),
        layer(
            "week",
            "Week",
            f"Trading Week {_format_date_range(week_start, week_end)}",
            f"{trading_date.strftime('%A')} {trading_date.isoformat()}",
            trading_day_start,
            trading_day_end,
        ),
        layer(
            "day",
            "Day",
            f"Trading Day {trading_date.isoformat()}",
            active_session or "Closed",
            session_start_dt,
            session_end_dt,
        ),
        layer(
            "session",
            "Session",
            (
                f"{active_session} Session "
                f"{session_start_dt.strftime('%H:%M')}–{session_end_dt.strftime('%H:%M')}"
                if session_start_dt is not None and session_end_dt is not None
                else "Session unavailable"
            ),
            (
                f"{macro_start_dt.strftime('%H:%M')}–{macro_end_dt.strftime('%H:%M')}"
                if macro_start_dt is not None and macro_end_dt is not None
                else "90m interval unavailable"
            ),
            macro_start_dt,
            macro_end_dt,
        ),
    )


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
    daily_quarter = _DAILY_QUARTERS.get(session, "")
    session_quarter = session_quarter_for(local, session)
    windows, active_ids, next_window_id = _window_contexts(local)
    return MarketTimeContext(
        captured_at=local.isoformat(timespec="seconds"),
        timezone=MARKET_TIMEZONE_NAME,
        source=source.strip() or "Unknown",
        futures_trading_day=futures_trading_day_for(local).isoformat(),
        market_open=market_is_open(local),
        weekday=local.strftime("%A"),
        session=session,
        daily_quarter=daily_quarter,
        session_quarter=session_quarter,
        calendar_quarter=calendar_quarter_for(local),
        calendar_quarter_month_index=calendar_quarter_month_index_for(local),
        calendar_month_phase=calendar_month_phase_for(local),
        raw_quarters=raw_qt_quarters_for(
            local,
            session=session,
        ),
        raw_quarter_layers=raw_qt_layer_contexts_for(
            local,
            session=session,
        ),
        timed_windows=windows,
        active_window_ids=active_ids,
        next_window_id=next_window_id,
    )


def timed_window_by_id(context: dict, window_id: str) -> dict:
    for item in list(context.get("timed_windows", []) or []):
        if str(item.get("id", "")) == window_id:
            return dict(item)
    return {}


def temporal_relevance_for(
    context: dict,
    window_ids: tuple[str, ...] | list[str],
) -> dict:
    """Summarize how a set of Trade Plan windows relates to the market clock.

    The result is descriptive; callers decide whether temporal state is advisory
    or an executable Trade Plan prerequisite.
    """

    ids = [str(item).strip() for item in window_ids if str(item).strip()]
    if not ids:
        return {
            "state": "Not Time-Bound",
            "window_id": "",
            "window_name": "",
            "minutes_until_start": None,
        }

    windows = [timed_window_by_id(context, window_id) for window_id in ids]
    windows = [item for item in windows if item]
    if not windows:
        return {
            "state": "Not Configured",
            "window_id": "",
            "window_name": "",
            "minutes_until_start": None,
        }

    active = next((item for item in windows if item.get("state") == "Active"), None)
    if active is not None:
        return {
            "state": "Active",
            "window_id": str(active.get("id", "")),
            "window_name": str(active.get("name", "")),
            "minutes_until_start": 0,
        }

    upcoming = [
        item
        for item in windows
        if item.get("state") == "Upcoming"
        and item.get("minutes_until_start") is not None
    ]
    if upcoming:
        next_item = min(upcoming, key=lambda item: int(item["minutes_until_start"]))
        return {
            "state": "Upcoming",
            "window_id": str(next_item.get("id", "")),
            "window_name": str(next_item.get("name", "")),
            "minutes_until_start": int(next_item["minutes_until_start"]),
        }

    return {
        "state": "Closed",
        "window_id": "",
        "window_name": "",
        "minutes_until_start": None,
    }
