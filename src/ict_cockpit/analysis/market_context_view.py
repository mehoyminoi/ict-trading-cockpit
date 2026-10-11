"""Read-only presentation of stored context; never queries or evaluates policy."""

from dataclasses import dataclass
from datetime import datetime

from ict_cockpit.analysis.market_context_event import (
    MarketContextEvent,
    MarketContextEventCategory,
    MarketContextEventStatus,
    MarketContextSnapshot,
    MarketContextSnapshotStatus,
    MarketContextTimingPrecision,
    parse_event_datetime,
)
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.quarter_theory import (
    qt_context_summary,
    raw_quarter_provenance_tooltip,
    raw_quarter_stack_summary,
)
from ict_cockpit.analysis.trading_session_run import TradingRun


SCHEDULE_CATEGORIES = frozenset({
    MarketContextEventCategory.HOLIDAY,
    MarketContextEventCategory.EARLY_CLOSE,
    MarketContextEventCategory.MARKET_SCHEDULE,
})


@dataclass(frozen=True)
class MarketContextView:
    availability: str
    temporal: str
    events: str
    detail: str


def _aware_time(value: str) -> datetime | None:
    try:
        moment = parse_event_datetime(value)
    except (ValueError, TypeError):
        return None
    return moment if moment.utcoffset() is not None else None


def _timestamp(value: str) -> str:
    moment = _aware_time(value)
    if moment is None:
        return value or "Not recorded"
    local = moment.astimezone(MARKET_TIMEZONE)
    return f"{local:%Y-%m-%d %H:%M:%S %Z} ({local:%z})"


def _event_caption(event: MarketContextEvent) -> str:
    local = event.scheduled_datetime.astimezone(MARKET_TIMEZONE)
    if event.timing_precision is not MarketContextTimingPrecision.EXACT:
        return f"{event.title} [timing {event.timing_precision.value}; {event.status.value}]"
    return (
        f"{event.title} {local:%H:%M} ET "
        f"[{event.impact.value}; {event.status.value}]"
    )


def build_market_context_view(
    run: TradingRun,
    *,
    mode_id: str = "tda",
    market_time_context: dict | None = None,
) -> MarketContextView:
    """Project a snapshot using explicit market time, without a wall-clock fallback.

    Watch shows the next recorded time (all simultaneous events are accounted
    for) and schedule facts for the captured day. No event-duration, warning
    horizon, market-open override, or authorization meaning is inferred.
    """
    market = dict(
        run.market_time_context if market_time_context is None else market_time_context
    )
    snapshot = MarketContextSnapshot.from_dict(run.market_context_snapshot)
    records = sorted(snapshot.events, key=lambda item: (item.scheduled_datetime, item.id))
    schedule = [item for item in records if item.category in SCHEDULE_CATEGORIES]
    other = [item for item in records if item.category not in SCHEDULE_CATEGORIES]
    available = snapshot.status is MarketContextSnapshotStatus.AVAILABLE

    if available:
        availability = (
            f"Available · {len(other)} event(s), {len(schedule)} schedule fact(s) captured"
            if records else "Available · provider query completed with no matching events"
        )
        if not snapshot.coverage.complete:
            availability += " · source completeness unverified"
    else:
        availability = f"{snapshot.status.value} · event and schedule context unknown"
    availability += " · run-start snapshot"

    if market:
        temporal = (
            f"{market.get('session', 'Unknown')} · raw QT "
            f"{market.get('daily_quarter') or 'Unknown'} / "
            f"{market.get('session_quarter') or 'Unknown'}"
        )
        if mode_id == "tda":
            temporal += " · AMDX expectation: " + qt_context_summary(run.qt_context)
    else:
        temporal = "Market-time / raw QT context unknown"

    now = _aware_time(str(market.get("captured_at", "")))
    start = _aware_time(snapshot.query_start)
    end = _aware_time(snapshot.query_end)
    in_window = now is not None and start is not None and end is not None and start <= now <= end
    if not available:
        event_summary = "Event and schedule facts are unknown for this run."
    elif mode_id == "post-market":
        event_summary = "Stored event / schedule facts and provenance available in details."
    elif not in_window:
        event_summary = (
            "Market time is outside the captured event window; see stored details."
            if now is not None and start is not None and end is not None
            else "Event timing unknown; market time or snapshot bounds are not recorded."
        )
    else:
        upcoming = [
            item for item in other
            if item.scheduled_datetime >= now
            and item.timing_precision is MarketContextTimingPrecision.EXACT
            and item.status not in {
                MarketContextEventStatus.CANCELLED,
                MarketContextEventStatus.POSTPONED,
                MarketContextEventStatus.RELEASED,
            }
        ]
        if upcoming:
            next_event = upcoming[0]
            simultaneous = sum(
                item.scheduled_datetime == next_event.scheduled_datetime for item in upcoming
            )
            label = "At reference time" if next_event.scheduled_datetime == now else "Next recorded time"
            event_summary = f"{label}: {_event_caption(next_event)}"
            if simultaneous > 1:
                event_summary += f" (+{simultaneous - 1} at the same time; see details)"
        else:
            event_summary = "No verified upcoming exact event times in this snapshot."
        uncertain = [item for item in records if item.timing_precision is not MarketContextTimingPrecision.EXACT]
        if uncertain:
            event_summary += f" · {len(uncertain)} record(s) have uncertain timing; inspect source details."
        active_schedule = [item for item in schedule
                           if item.status is not MarketContextEventStatus.CANCELLED
                           and item.timing_precision is MarketContextTimingPrecision.EXACT
                           and start <= item.scheduled_datetime <= end]
        if active_schedule:
            event_summary += f" · Schedule fact: {_event_caption(active_schedule[0])}"
            if len(active_schedule) > 1:
                event_summary += f" (+{len(active_schedule) - 1}; see details)"
        elif any(item.timing_precision is not MarketContextTimingPrecision.EXACT for item in schedule):
            event_summary += " · Source schedule rows have uncertain day/time applicability; see details."
        else:
            event_summary += " · No non-cancelled schedule exceptions captured."

    detail = [
        f"Trading Run: {run.run_label} ({run.id})",
        f"Environment / purpose: {run.environment.value} / {run.purpose.value}",
        f"Trade Plan revision: {run.trade_plan_revision or 'Not recorded'}",
        "",
        "Market-time / QT facts (separate from event snapshot)",
        f"Market reference: {_timestamp(str(market.get('captured_at', '')))}",
        f"Market-time source: {market.get('source') or 'Not recorded'}",
        f"Futures trading day: {market.get('futures_trading_day') or 'Not recorded'}",
        f"Raw QT: {raw_quarter_stack_summary(market)}",
        raw_quarter_provenance_tooltip(market),
        f"AMDX expectation / TDA: {qt_context_summary(run.qt_context)}",
    ]
    if mode_id == "post-market":
        detail += [
            f"AMDX observed / Review: {qt_context_summary(run.review_observed_qt_context)}",
            f"QT Review note: {run.review_qt_context_note or 'Not recorded'}",
        ]
    detail += [
        "",
        "Event / schedule snapshot — stored at run start; not a refreshed feed",
        f"Availability: {snapshot.status.value}",
        f"Provider: {snapshot.provider or 'Not recorded'}",
        f"Query start: {_timestamp(snapshot.query_start)}",
        f"Query end: {_timestamp(snapshot.query_end)}",
        f"Snapshot market reference: {_timestamp(snapshot.reference_market_time)}",
        f"Snapshot market-time source: {snapshot.market_time_source or 'Not recorded'}",
        f"Snapshot captured at: {_timestamp(snapshot.captured_at)}",
        f"Snapshot detail: {snapshot.detail or 'Not recorded'}",
        f"Source completeness: {'Explicit complete claim' if snapshot.coverage.complete else 'Unknown / incomplete'}",
        f"Source coverage bounds: {snapshot.coverage.start or 'Not recorded'} → {snapshot.coverage.end or 'Not recorded'}",
        f"Source coverage basis: {snapshot.coverage.basis}",
        f"Source coverage scope: {snapshot.coverage.to_dict()}",
        "",
        "Event and schedule facts do not imply QT structural distortion or entry permission.",
    ]
    p = snapshot.source_provenance
    detail += [f"Source capture ID: {p.capture_id or 'Not recorded'}",
               f"SHA-256: {p.content_sha256 or 'Not recorded'}",
               f"Source reference: {p.source_reference or 'Not recorded'}",
               f"Source imported at: {_timestamp(p.imported_at)}",
               f"Declared source window: {p.declared_start or 'Not recorded'} → {p.declared_end or 'Not recorded'}",
               f"Timezone basis: {p.timezone_basis or 'Not recorded'}",
               f"Adapter / mapping revision: {p.adapter_revision or 'Not recorded'} / {p.mapping_revision or 'Not recorded'}",
               f"Source knowledge basis: {p.knowledge_basis}", *p.limitations]
    for item in records:
        detail += [
            "",
            f"{item.title} · {item.category.value} · {item.impact.value} · {item.status.value}",
            f"Source clock: {_timestamp(item.scheduled_at)} · original: {item.scheduled_at} · precision: {item.timing_precision.value}",
            f"Provider / source event: {item.provider} / {item.source_event_id or 'Not recorded'}",
            f"Event ID / type: {item.id} / {item.normalized_event_type or 'Not recorded'}",
            f"Identity basis: {item.identity_basis}",
            f"Native record: {item.native_record or 'Not recorded'}",
            f"Source timezone: {item.source_timezone or 'Not recorded'}",
            f"Native impact: {item.provider_native_impact or 'Not recorded'}",
            f"Affected markets: {', '.join(item.affected_markets) or 'Not recorded'}",
            f"Actual / forecast / previous: {item.actual or 'Not recorded'} / {item.forecast or 'Not recorded'} / {item.previous or 'Not recorded'}",
            f"Source updated at: {_timestamp(item.source_updated_at)}",
            f"Event captured at: {_timestamp(item.captured_at)}",
            f"Provenance reference: {item.provenance_reference or 'Not recorded'}",
        ]
    if not records:
        detail.append("No event records stored.")
    results = run.context_rule_results(market)
    detail += ["", "Trade Plan context rules — evaluated from stored rules and explicit market time"]
    if not results:
        detail.append("No declarative context rules recorded; existing manual Trade Plan gates remain in force.")
    for rule, result in zip(run.context_rule_snapshot, results):
        effect = result.effect.value if result.effect else "No effect"
        detail += [f"{result.name} [{result.rule_id}]: {result.state.value} / {effect}",
                   f"Rule rationale: {rule['rationale']}",
                   f"Applies in: {', '.join(rule['environments'])}",
                   f"Matched effect / unknown effect: {rule['effect']} / {rule['unknown_effect']}",
                   *result.reasons, f"Matching/potential event IDs: {', '.join(result.event_ids) or 'None'}"]
    active = [result for result in results if result.effect is not None]
    if active:
        event_summary += " · Plan context: " + "; ".join(
            f"{result.name}: {result.state.value} / {result.effect.value}" for result in active
        )
    return MarketContextView(availability, temporal, event_summary, "\n".join(detail))
