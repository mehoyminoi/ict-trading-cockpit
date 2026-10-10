"""Pure context evaluation: no provider access, wall clock, or run mutation."""
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from enum import Enum
from zoneinfo import ZoneInfo

from ict_cockpit.context_rules import (
    ContextConditionKind, ContextEffect, ContextEventWindow, normalize_context_rules,
)
from ict_cockpit.analysis.market_context_event import (
    MarketContextEventStatus as EventStatus, MarketContextImpact, MarketContextSnapshot,
    MarketContextSnapshotStatus, futures_day_event_window, parse_event_datetime,
)


class ContextMatch(str, Enum):
    MATCHED = "Matched"
    NOT_MATCHED = "Not Matched"
    UNKNOWN = "Unknown"
    NOT_APPLICABLE = "Not Applicable"


@dataclass(frozen=True)
class ContextRuleResult:
    rule_id: str
    name: str
    state: ContextMatch
    effect: ContextEffect | None
    reasons: tuple[str, ...]
    event_ids: tuple[str, ...] = ()

    @property
    def blocks_new_entry(self):
        return self.effect in {ContextEffect.BLOCK_NEW_ENTRY, ContextEffect.STAND_DOWN_DAY}


NY = ZoneInfo("America/New_York")


def _aware(value):
    try:
        result = parse_event_datetime(value)
        return result if result.tzinfo is not None else None
    except (ValueError, TypeError):
        return None


def _condition(condition, market, snapshot):
    now = _aware(market.get("captured_at", ""))
    if now is None:
        return ContextMatch.UNKNOWN, "Explicit market timestamp is missing or invalid.", ()
    now = now.astimezone(NY)
    if condition.kind is ContextConditionKind.MARKET_CLOCK:
        matches = (not condition.weekdays or now.weekday() in condition.weekdays) and (
            not condition.after_time or now.time().replace(tzinfo=None) > time.fromisoformat(condition.after_time)
        )
        return (ContextMatch.MATCHED if matches else ContextMatch.NOT_MATCHED), f"NY market clock: {now.isoformat()} (strictly after cutoff).", ()
    if condition.event_window is ContextEventWindow.FUTURES_DAY:
        try:
            start, end = futures_day_event_window(market.get("futures_trading_day", ""), timezone=NY)
        except (ValueError, TypeError):
            return ContextMatch.UNKNOWN, "Futures trading day is missing or invalid.", ()
        if not start <= now <= end:
            return ContextMatch.UNKNOWN, "Market timestamp and futures trading day disagree.", ()
    else:
        monday = now.date() - timedelta(days=now.weekday())
        start = datetime.combine(monday, time(), NY)
        end = start + timedelta(days=7) - timedelta(microseconds=1)
    if snapshot.status is not MarketContextSnapshotStatus.AVAILABLE:
        return ContextMatch.UNKNOWN, f"Event snapshot is {snapshot.status.value}.", ()
    query_start, query_end = _aware(snapshot.query_start), _aware(snapshot.query_end)
    if query_start is None or query_end is None or query_end < query_start:
        return ContextMatch.UNKNOWN, "Snapshot coverage bounds are missing or invalid.", ()
    matches, uncertain = [], []
    for event in snapshot.events:
        stamp = event.scheduled_datetime
        if not start <= stamp <= end or not query_start <= stamp <= query_end:
            continue
        if event.status in {EventStatus.CANCELLED, EventStatus.POSTPONED}:
            continue
        if condition.category and event.category is not condition.category:
            continue
        if condition.event_types and event.normalized_event_type and event.normalized_event_type not in condition.event_types:
            continue
        if condition.impacts and event.impact is not MarketContextImpact.UNKNOWN and event.impact not in condition.impacts:
            continue
        if condition.affected_markets and event.affected_markets and not set(condition.affected_markets).intersection(event.affected_markets):
            continue
        unknown = (
            event.status in {EventStatus.UNKNOWN, EventStatus.TENTATIVE}
            or (condition.event_types and not event.normalized_event_type)
            or (condition.impacts and event.impact is MarketContextImpact.UNKNOWN)
            or (condition.affected_markets and not event.affected_markets)
        )
        (uncertain if unknown else matches).append(event.id)
    if matches:
        return ContextMatch.MATCHED, "Matching normalized event facts are recorded.", tuple(matches)
    if uncertain:
        return ContextMatch.UNKNOWN, "Potential matching events have unknown selectors or status.", tuple(uncertain)
    if query_start > start or query_end < end:
        return ContextMatch.UNKNOWN, f"Snapshot does not cover the complete {condition.event_window.value.lower()}.", ()
    return ContextMatch.NOT_MATCHED, "Complete snapshot window contains no matching event facts.", ()


def evaluate_context_rules(rules, *, environment, market_time_context, market_context_snapshot):
    results = []
    snapshot = MarketContextSnapshot.from_dict(market_context_snapshot)
    for rule in normalize_context_rules(rules):
        if environment not in rule.environments:
            results.append(ContextRuleResult(rule.id, rule.name, ContextMatch.NOT_APPLICABLE, None,
                                             (f"Rule does not apply in {environment}.",)))
            continue
        terms = [_condition(x, market_time_context, snapshot) for x in rule.conditions]
        states = [x[0] for x in terms]
        # A false conjunct resolves the rule even when another conjunct is unknown.
        state = (ContextMatch.NOT_MATCHED if ContextMatch.NOT_MATCHED in states else
                 ContextMatch.UNKNOWN if ContextMatch.UNKNOWN in states else ContextMatch.MATCHED)
        effect = rule.effect if state is ContextMatch.MATCHED else rule.unknown_effect if state is ContextMatch.UNKNOWN else None
        results.append(ContextRuleResult(rule.id, rule.name, state, effect,
                                         tuple(x[1] for x in terms), tuple(dict.fromkeys(i for x in terms for i in x[2]))))
    return tuple(results)
