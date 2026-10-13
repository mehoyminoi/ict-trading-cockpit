"""Bounded higher Review orientation, independent of phase interpretation.

Portable validation uses retained cycle boundaries; only new preparation calls
current temporal rules. A scope proof declares retrospective selection, never
information availability.
"""
from datetime import datetime, time, timedelta, timezone

from ict_cockpit.analysis.amdx import canonical_timestamp, cycle_from_payload, payload, timestamp
from ict_cockpit.analysis import amdx_context
from ict_cockpit.analysis.amdx_context import CycleContext, HIGHER_LEVELS, PositionState, TEMPORAL_REVISION
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, futures_trading_day_for

POLICY = "amdx-higher-review-day-v1"


def _instant(value):
    return canonical_timestamp(value).astimezone(timezone.utc)


def day_bounds(original):
    day = futures_trading_day_for(original)
    start = datetime.combine(day - timedelta(days=1), time(18), MARKET_TIMEZONE)
    end = datetime.combine(day, time(18), MARKET_TIMEZONE)
    return day, start, end


def _points(original):
    day, start, end = day_bounds(original)
    return (("Original launch", original), ("Reviewed day start", start),
            ("Calendar midnight", datetime.combine(day, time(), MARKET_TIMEZONE)))


def _fingerprint(contexts):
    return tuple((c["cycle"]["id"], c["position"], c["state"]) for c in contexts)


def orientations(original):
    seen, result = set(), []
    for source, reference in _points(original):
        contexts = payload(amdx_context.resolve_higher_cycles(reference))
        fingerprint = _fingerprint(contexts)
        if fingerprint not in seen:
            seen.add(fingerprint)
            result.append(dict(source=source, reference=reference.isoformat(), contexts=contexts))
    return result


def make_scope(binding, launch, selected_reference):
    original = timestamp(launch["projection"]["reference"])
    selected = canonical_timestamp(selected_reference).astimezone(MARKET_TIMEZONE)
    candidates = orientations(original)
    chosen = next((c for c in candidates if _instant(timestamp(c["reference"])) == _instant(selected)), None)
    if chosen is None:
        raise ValueError("Select an available higher context within the original reviewed day")
    day, start, end = day_bounds(original)
    return dict(version=1, policy=POLICY, temporal_revision=TEMPORAL_REVISION,
        run_id=binding["run_id"], instrument=binding["instrument"], master_binding_id=binding["master_binding_id"],
        original_reference=launch["projection"]["reference"], selected_reference=selected.isoformat(),
        reviewed_day=day.isoformat(), window_start=start.isoformat(), window_end=end.isoformat(),
        timezone="America/New_York", source=chosen["source"], candidates=candidates,
        original_contexts=[r["context"] for r in launch["projection"]["cycles"][:5]],
        selected_contexts=chosen["contexts"])


def _validate_contexts(contexts, reference):
    if not isinstance(contexts, list) or len(contexts) != 5:
        raise ValueError("Scope proof requires all five higher contexts")
    for level, content in zip(HIGHER_LEVELS, contexts):
        if set(content) != set(CycleContext.__dataclass_fields__):
            raise ValueError("Unsupported scope context fields")
        cycle = cycle_from_payload(content["cycle"])
        state = PositionState(content["state"])
        if cycle.layer != level or content["temporal_revision"] != TEMPORAL_REVISION:
            raise ValueError("Scope proof has inconsistent higher layer/revision")
        if state is PositionState.ACTIVE:
            quarter = cycle.quarter_at(reference)
            if quarter is None or content["position"] != f"Q{quarter.position}":
                raise ValueError("Scope proof position differs from retained boundaries")
        elif (level, content["position"], state.value) not in (
            ("month", "Distortion", "Distortion"), ("month", "", "Unassigned"),
            ("week", "", "Distortion"), ("week", "", "Closed")):
            raise ValueError("Unsupported inactive scope position")
        if content["reference_basis"] != ("New York calendar" if level in HIGHER_LEVELS[:3] else "New York futures day"):
            raise ValueError("Scope proof reference convention differs")
        if content["prior_q4_id"] is not None and not isinstance(content["prior_q4_id"], str):
            raise ValueError("Invalid scope prior-quarter identity")


def validate_scope(proof, binding, launch, reference, contexts):
    """Check retained proof without reclassifying through today's resolver."""
    fields = {"version", "policy", "temporal_revision", "run_id", "instrument", "master_binding_id",
        "original_reference", "selected_reference", "reviewed_day", "window_start", "window_end",
        "timezone", "source", "candidates", "original_contexts", "selected_contexts"}
    if not isinstance(proof, dict) or set(proof) != fields or type(proof["version"]) is not int or (
        proof["version"], proof["policy"], proof["temporal_revision"], proof["timezone"]
    ) != (1, POLICY, TEMPORAL_REVISION, "America/New_York"):
        raise ValueError("Unsupported higher Review scope proof")
    if (proof["run_id"], proof["instrument"], proof["master_binding_id"], proof["original_reference"], proof["original_contexts"]) != (
        binding["run_id"], binding["instrument"], binding["master_binding_id"], launch["projection"]["reference"],
        [r["context"] for r in launch["projection"]["cycles"][:5]]):
        raise ValueError("Scope proof differs from original run launch")
    original = timestamp(proof["original_reference"])
    selected = timestamp(proof["selected_reference"])
    day, start, end = day_bounds(original)
    if (proof["reviewed_day"], proof["window_start"], proof["window_end"]) != (day.isoformat(), start.isoformat(), end.isoformat()) or not (
        _instant(start) <= _instant(selected) < _instant(end)
    ) or _instant(selected) != _instant(reference):
        raise ValueError("Scope proof is outside its original reviewed day")
    candidates = proof["candidates"]
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 3:
        raise ValueError("Invalid scope candidates")
    allowed = dict(_points(original))
    seen, sources = set(), []
    chosen = None
    for candidate in candidates:
        if set(candidate) != {"source", "reference", "contexts"} or candidate["source"] not in allowed:
            raise ValueError("Invalid scope candidate fields")
        moment = timestamp(candidate["reference"])
        if candidate["reference"] != allowed[candidate["source"]].isoformat():
            raise ValueError("Scope candidate differs from its declared reference")
        _validate_contexts(candidate["contexts"], moment)
        fingerprint = _fingerprint(candidate["contexts"])
        if fingerprint in seen:
            raise ValueError("Duplicate higher scope orientation")
        seen.add(fingerprint)
        sources.append(candidate["source"])
        if _instant(moment) == _instant(selected):
            chosen = candidate
    if candidates[0]["contexts"] != proof["original_contexts"]:
        raise ValueError("Original scope orientation differs from retained launch")
    if sources != sorted(sources, key=list(allowed).index) or sources[0] != "Original launch":
        raise ValueError("Scope proof must retain original orientation first")
    if chosen is None or (proof["source"], proof["selected_contexts"]) != (chosen["source"], chosen["contexts"]) or contexts != chosen["contexts"]:
        raise ValueError("Scope proof differs from selected retained projection")
