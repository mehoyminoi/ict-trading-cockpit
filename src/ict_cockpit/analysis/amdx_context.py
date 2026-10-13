"""Pure cycle orientation and scoped interpretation projection.

No storage, legacy conversion, wall-clock fallback or phase classification.
Calendar and futures-day conventions intentionally remain distinct.
"""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum

from ict_cockpit.analysis.amdx import (
    Claim, Cycle, Inference, InterpretationHistory, Quarter, aware, infer_profile,
    intraday_cycles, require_id,
)
from ict_cockpit.analysis.market_time import (
    MARKET_TIMEZONE, as_new_york, futures_trading_day_for, market_is_open,
    raw_qt_quarters_for,
)


TEMPORAL_REVISION = "qt-higher-ny-v1"
HIGHER_LEVELS = ("cycle_16y", "quadrennial", "year", "month", "week")


class PositionState(str, Enum):
    ACTIVE = "Active"
    DISTORTION = "Distortion"
    UNASSIGNED = "Unassigned"
    CLOSED = "Closed"


@dataclass(frozen=True)
class CycleContext:
    cycle: Cycle
    position: str
    state: PositionState
    reference_basis: str
    temporal_revision: str
    prior_q4_id: str | None

    @property
    def active_quarter(self) -> Quarter | None:
        return next((q for q in self.cycle.quarters
                     if self.position == f"Q{q.position}"), None)


@dataclass(frozen=True)
class ProjectedCycle:
    context: CycleContext
    claim: Claim | None
    inference: Inference


@dataclass(frozen=True)
class LegacyValue:
    key: str
    value: str
    provenance: str = "Legacy/derived flat context; not a cycle anchor"


@dataclass(frozen=True)
class StackProjection:
    run_id: str
    channel: str
    branch_id: str
    reference: datetime
    market_open: bool
    cycles: tuple[ProjectedCycle, ...]
    legacy_values: tuple[LegacyValue, ...]


def _identity(level: str, key: str) -> str:
    return f"{TEMPORAL_REVISION}:{level}:{key}"


def _quartet(level, key, boundaries, labels, *, parent=""):
    identity = _identity(level, key)
    return Cycle(identity, level, tuple(
        Quarter(f"{identity}:Q{i + 1}", i + 1, label, boundaries[i], boundaries[i + 1])
        for i, label in enumerate(labels)
    ), parent)


def _midnight(year, month=1):
    return datetime(year, month, 1, tzinfo=MARKET_TIMEZONE)


def _futures_start(trading_date):
    return datetime.combine(trading_date - timedelta(days=1), time(18), MARKET_TIMEZONE)


def _first_monday(month_date):
    first = month_date.replace(day=1)
    return first + timedelta(days=(-first.weekday()) % 7)


def _previous_month(month_date):
    return (month_date.replace(day=1) - timedelta(days=1)).replace(day=1)


def resolve_higher_cycles(reference: datetime) -> tuple[CycleContext, ...]:
    """Identify higher quartets using existing raw-position conventions.

    The selected monthly occurrence comes from the futures-day month. Its full
    Monday weeks are retained, including tails beyond that calendar month.
    Before its first Monday no active quarter is inferred from the prior month.
    Distortion/closed states preserve an inspectable quartet, without Q5 input.
    """
    local = as_new_york(aware(reference))
    trading_date = futures_trading_day_for(local)
    raw = raw_qt_quarters_for(local)
    cycle_year = local.year - ((local.year - 2011) % 16)
    block_year = local.year - ((local.year - 2011) % 4)
    month_date = trading_date.replace(day=1)
    monday = trading_date - timedelta(days=trading_date.weekday())
    month_monday = _first_monday(month_date)
    week_month = monday.replace(day=1)
    week_index = (monday - _first_monday(week_month)).days // 7 + 1
    # Derive this relationship from the week's own start, never the caller's
    # selected month. Its ID/content must remain stable across month rollover.
    week_parent = (f"{_identity('month', week_month.strftime('%Y-%m'))}:Q{week_index}"
                   if 1 <= week_index <= 4 else "")
    try:
        cycle16 = _quartet("cycle_16y", str(cycle_year),
            tuple(_midnight(cycle_year + 4 * i) for i in range(5)),
            tuple(f"{cycle_year + 4 * i}–{cycle_year + 4 * i + 3}" for i in range(4)))
        block = _quartet("quadrennial", str(block_year),
            tuple(_midnight(block_year + i) for i in range(5)),
            tuple(str(block_year + i) for i in range(4)),
            parent=f"{cycle16.id}:{raw['cycle_16y']}")
        year = _quartet("year", str(local.year),
            tuple(_midnight(local.year, 1 + 3 * i) for i in range(4))
            + (_midnight(local.year + 1),),
            ("Jan–Mar", "Apr–Jun", "Jul–Sep", "Oct–Dec"),
            parent=f"{block.id}:{raw['quadrennial']}")
        month = _quartet("month", month_date.strftime("%Y-%m"),
            tuple(_futures_start(month_monday + timedelta(days=7 * i)) for i in range(5)),
            tuple(f"Monday week {(month_monday + timedelta(days=7 * i)).isoformat()}"
                  for i in range(4)))
        week = _quartet("week", monday.isoformat(),
            tuple(_futures_start(monday + timedelta(days=i)) for i in range(5)),
            tuple((monday + timedelta(days=i)).strftime("%A %Y-%m-%d") for i in range(4)),
            parent=week_parent)
    except (ValueError, OverflowError) as error:
        raise ValueError("Higher cycle bounds exceed the supported datetime range") from error
    previous = (
        _identity("cycle_16y", str(cycle_year - 16)) if cycle_year > 16 else None,
        _identity("quadrennial", str(block_year - 4)) if block_year > 4 else None,
        _identity("year", str(local.year - 1)) if local.year > 1 else None,
        _identity("month", _previous_month(month_date).strftime("%Y-%m")),
        _identity("week", (monday - timedelta(days=7)).isoformat()),
    )
    contexts = []
    for cycle, prior in zip((cycle16, block, year, month, week), previous):
        position = raw[cycle.layer]
        if position.startswith("Q"):
            state = PositionState.ACTIVE
        elif cycle.layer == "month" and position == "Distortion":
            state = PositionState.DISTORTION
        elif cycle.layer == "week" and trading_date.weekday() == 4:
            state = PositionState.DISTORTION
        elif cycle.layer == "week":
            state = PositionState.CLOSED
        else:
            state = PositionState.UNASSIGNED
        # Keep the raw weekly Friday value empty; the explicit state explains
        # its distortion role without changing the existing factual API.
        contexts.append(CycleContext(cycle, position, state,
            "New York calendar" if cycle.layer in HIGHER_LEVELS[:3] else "New York futures day",
            TEMPORAL_REVISION, f"{prior}:Q4" if prior else None))
    return tuple(contexts)


def resolve_stack_cycles(reference: datetime) -> tuple[CycleContext, ...]:
    local = as_new_york(aware(reference))
    contexts = resolve_higher_cycles(local)
    intraday = tuple(CycleContext(cycle, f"Q{cycle.quarter_at(local).position}",
        PositionState.ACTIVE, "New York futures day", "", None)
        for cycle in intraday_cycles(local))
    return contexts + intraday


def project_stack(*, run_id: str, reference: datetime, history: InterpretationHistory,
                  channel: str = "Expected", branch_id: str = "working",
                  legacy_context: dict[str, str] | None = None) -> StackProjection:
    """Read only the requested run/channel/branch heads; never borrow another.

    Caller supplies a deliberate reference (preserved run reference for Review).
    Selected claims retain their recorded input/reference/revision provenance.
    Legacy values are carried separately, exactly as supplied, without defaults.
    """
    require_id(run_id)
    require_id(branch_id)
    if channel not in ("Expected", "Observed"):
        raise ValueError("Channel must be Expected or Observed")
    local = as_new_york(aware(reference))
    legacy = tuple(LegacyValue(key, value) for key, value in (legacy_context or {}).items())
    if any(not isinstance(v.key, str) or not isinstance(v.value, str) for v in legacy):
        raise ValueError("Legacy context keys and values must be strings")
    result = []
    for context in resolve_stack_cycles(local):
        cycle = context.cycle
        same_identity = tuple(c for c in history.claims if c.cycle.id == cycle.id)
        if any(c.cycle != cycle for c in same_identity):
            raise ValueError("Stable cycle identity disagrees with its temporal content")
        claim = next((c for c in reversed(same_identity)
                      if (c.run_id, c.channel, c.branch_id) == (run_id, channel, branch_id)), None)
        inference = infer_profile(cycle, claim.anchors + claim.applicability if claim else ())
        if claim is not None and inference != claim.inference:
            raise ValueError("Claim inference disagrees with its retained anchors")
        result.append(ProjectedCycle(context, claim, inference))
    return StackProjection(run_id, channel, branch_id, local, market_is_open(local),
                           tuple(result), legacy)
