"""Higher occurrence boundaries and honest, scoped read projections."""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import json

import pytest

from ict_cockpit.analysis.amdx import (
    Anchor, InterpretationHistory, Profile, Role, XSubtype, intraday_cycles, payload,
)
from ict_cockpit.analysis.amdx_context import (
    HIGHER_LEVELS, PositionState, TEMPORAL_REVISION, project_stack,
    resolve_higher_cycles, resolve_stack_cycles,
)
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, raw_qt_quarters_for


def ny(text):
    return datetime.fromisoformat(text).replace(tzinfo=MARKET_TIMEZONE)


REFERENCE = ny("2026-10-08T09:15")


def contexts(moment):
    return {c.cycle.layer: c for c in resolve_higher_cycles(moment)}


@pytest.mark.parametrize("text", [
    "2011-01-01T00:00", "2015-01-01T00:00", "2023-01-01T00:00",
    "2026-12-31T17:59", "2026-12-31T18:00", "2027-01-01T00:00",
    "2026-03-08T17:59", "2026-03-08T18:00", "2026-11-01T17:59",
    "2026-11-01T18:00", "2026-09-28T09:15", "2026-10-01T09:15",
    "2026-10-04T18:00", "2026-06-29T09:15", "2026-07-01T09:15",
    "2026-10-08T17:59", "2026-10-08T18:00", "2026-10-09T17:59",
    "2026-10-10T09:15", "2026-10-11T17:59", "2026-10-11T18:00",
])
def test_occurrences_match_existing_raw_positions_with_half_open_bounds(text):
    moment = ny(text)
    resolved = resolve_higher_cycles(moment)
    raw = raw_qt_quarters_for(moment)
    assert tuple(c.cycle.layer for c in resolved) == HIGHER_LEVELS
    assert resolve_higher_cycles(moment.astimezone(timezone.utc)) == resolved
    for c in resolved:
        assert c.position == raw[c.cycle.layer]
        assert c.temporal_revision == TEMPORAL_REVISION
        assert len({q.id for q in c.cycle.quarters}) == 4
        assert c.cycle.quarter_at(c.cycle.quarters[-1].end) is None
        if c.active_quarter:
            assert c.cycle.quarter_at(moment) == c.active_quarter
            assert c.state is PositionState.ACTIVE
        else:
            assert c.cycle.quarter_at(moment) is None
        for a, b in zip(c.cycle.quarters, c.cycle.quarters[1:]):
            assert a.end == b.start


def test_year_end_uses_calendar_midnight_separately_from_futures_rollover():
    evening = contexts(ny("2026-12-31T19:00"))
    midnight = contexts(ny("2027-01-01T00:00"))
    assert evening["cycle_16y"].cycle.quarters[0].start == ny("2011-01-01T00:00")
    assert evening["cycle_16y"].position == evening["year"].position == "Q4"
    assert midnight["cycle_16y"].cycle.quarters[0].start == ny("2027-01-01T00:00")
    assert midnight["cycle_16y"].position == midnight["year"].position == "Q1"
    assert evening["month"].cycle == midnight["month"].cycle
    assert evening["month"].cycle.id.endswith(":month:2027-01")
    assert evening["month"].state is PositionState.UNASSIGNED


def test_monthly_full_weeks_and_cross_month_week_relationship_are_stable():
    sept = contexts(ny("2026-09-28T09:15"))
    oct = contexts(ny("2026-10-01T09:15"))
    assert sept["month"].cycle.quarters[3].end == ny("2026-10-04T18:00")
    assert sept["week"].cycle == oct["week"].cycle
    assert oct["week"].cycle.parent_quarter_id == sept["month"].cycle.quarters[3].id
    assert oct["month"].state is PositionState.UNASSIGNED
    assert oct["month"].active_quarter is None
    assert oct["month"].cycle.quarters[0].start == ny("2026-10-04T18:00")
    assert oct["week"].cycle.parent_quarter_id not in {q.id for q in oct["month"].cycle.quarters}
    assert oct["month"].cycle.parent_quarter_id == ""


def test_fifth_week_and_friday_are_orientation_states_without_q5_anchors():
    c = contexts(ny("2026-06-29T09:15"))
    assert c["month"].state is PositionState.DISTORTION
    assert c["month"].position == "Distortion"
    assert c["month"].active_quarter is None
    assert c["week"].cycle.parent_quarter_id == ""
    friday = contexts(ny("2026-10-09T09:15"))["week"]
    assert friday.state is PositionState.DISTORTION
    assert friday.position == "" and friday.active_quarter is None
    assert len(friday.cycle.quarters) == 4
    assert friday.cycle.quarters[-1].label.startswith("Thursday")
    assert len(resolve_stack_cycles(ny("2026-10-09T09:15"))) == 7


@pytest.mark.parametrize("text", ["2026-10-10T09:15", "2026-10-11T17:59"])
def test_closed_weekends_retain_higher_inspection_without_intraday_targets(text):
    projection = project_stack(run_id="r", reference=ny(text), history=InterpretationHistory())
    assert not projection.market_open
    assert len(projection.cycles) == 5
    assert projection.cycles[-1].context.state is PositionState.CLOSED
    assert projection.cycles[-1].context.active_quarter is None
    assert all(c.claim is None and c.inference.state == "Unresolved" for c in projection.cycles)


@pytest.mark.parametrize("before,after,hours", [
    ("2026-03-01T18:00", "2026-03-08T18:00", 167),
    ("2026-10-25T18:00", "2026-11-01T18:00", 169),
])
def test_month_week_bounds_preserve_new_york_wall_clock_across_dst(before, after, hours):
    c = contexts(ny(before))["month"]
    q = c.active_quarter
    assert q.start == ny(before) and q.end == ny(after)
    elapsed = q.end.astimezone(timezone.utc) - q.start.astimezone(timezone.utc)
    assert elapsed == timedelta(hours=hours)


def test_parent_links_are_complete_temporal_relationships_and_prior_q4_is_only_identity():
    c = contexts(REFERENCE)
    for child, parent in ((c["quadrennial"], c["cycle_16y"]), (c["year"], c["quadrennial"]),
                          (c["week"], c["month"])):
        q = next(q for q in parent.cycle.quarters if q.id == child.cycle.parent_quarter_id)
        assert q.start <= child.cycle.quarters[0].start
        assert child.cycle.quarters[-1].end <= q.end
    assert c["month"].prior_q4_id.endswith(":month:2026-09:Q4")
    assert c["week"].prior_q4_id.endswith(":week:2026-09-28:Q4")
    assert c["year"].prior_q4_id.endswith(":year:2025:Q4")


def test_intraday_identifiers_and_parent_content_remain_byte_equivalent():
    cycles = resolve_stack_cycles(REFERENCE)
    assert tuple(c.cycle for c in cycles[-2:]) == intraday_cycles(REFERENCE)
    assert all(c.temporal_revision == "" for c in cycles[-2:])


def revise(history, cycle, *, revision, run="r", channel="Expected", position=3, role=Role.M,
           subtype=None):
    method = history.revise_working if channel == "Expected" else history.revise_observed
    return method(claim_id=revision, run_id=run, channel=channel, branch_id="working",
        cycle=cycle, quarter_id=cycle.quarters[position - 1].id,
        anchor=Anchor("a-" + revision, cycle.quarters[position - 1].id, role,
                      "synthetic", subtype), recorded_at=REFERENCE, market_reference=REFERENCE)


def test_projection_filters_run_channel_branch_and_preserves_exact_claim_provenance():
    cycle = contexts(REFERENCE)["year"].cycle
    history = revise(InterpretationHistory(), cycle, revision="r-exp", role=Role.D)
    history = revise(history, cycle, revision="other-run", run="other", role=Role.M)
    history = revise(history, cycle, revision="r-obs", channel="Observed", role=Role.M)
    history = history.accept(claim_id="alternative", run_id="r", channel="Expected",
        branch_id="alternative", cycle=cycle, quarter_id=cycle.quarters[0].id,
        anchor=Anchor("alternative-a", cycle.quarters[0].id, Role.X, "synthetic"),
        recorded_at=REFERENCE, market_reference=REFERENCE)
    before = json.dumps(payload(history), sort_keys=True)
    expected = project_stack(run_id="r", reference=REFERENCE, history=history)
    observed = project_stack(run_id="r", reference=REFERENCE, history=history, channel="Observed")
    alternate = project_stack(run_id="r", reference=REFERENCE, history=history, branch_id="alternative")
    assert expected.cycles[2].claim.id == "r-exp"
    assert observed.cycles[2].claim.id == "r-obs"
    assert alternate.cycles[2].claim.id == "alternative"
    assert expected.cycles[2].claim is history.claims[0]
    assert expected.cycles[2].inference.candidates == (Profile.AMDX,)
    assert observed.cycles[2].inference.candidates == (Profile.XAMD,)
    assert json.dumps(payload(history), sort_keys=True) == before
    assert all(row.claim is None for i, row in enumerate(expected.cycles) if i != 2)


def test_projection_uses_latest_scoped_claim_with_explicit_x_and_entered_implied_meaning():
    c = contexts(REFERENCE)["month"].cycle
    h = revise(InterpretationHistory(), c, revision="first", position=4, role=Role.X,
               subtype=XSubtype.REVERSAL)
    h = revise(h, c, revision="second", position=4, role=Role.X, subtype=XSubtype.CONTINUATION)
    row = project_stack(run_id="r", reference=REFERENCE, history=h).cycles[3]
    assert row.claim.id == "second" and row.claim.anchors[0].subtype is XSubtype.CONTINUATION
    assert row.inference.roles[3].origin == "Technician"
    assert all(r.origin == "Implied" for r in row.inference.roles[:3])


@pytest.mark.parametrize("role,state", [(Role.UNKNOWN, "Unresolved"),
                                        (Role.NOT_APPLICABLE, "Not Applicable")])
def test_projection_preserves_explicit_uncertainty_and_quartet_applicability(role, state):
    c = contexts(REFERENCE)["week"].cycle
    h = revise(InterpretationHistory(), c, revision="judgment", role=role)
    row = project_stack(run_id="r", reference=REFERENCE, history=h).cycles[4]
    assert row.inference.state == state
    assert (row.claim.anchors + row.claim.applicability)[0].role is role


def test_legacy_context_is_separate_exact_input_without_invented_anchors_or_defaults():
    legacy = {"quarter": "D", "month": "A", "extra": "original value"}
    projection = project_stack(run_id="r", reference=REFERENCE, history=InterpretationHistory(),
                               legacy_context=legacy)
    assert {v.key: v.value for v in projection.legacy_values} == legacy
    assert all(c.claim is None and c.inference.state == "Unresolved" for c in projection.cycles)
    legacy["quarter"] = "M"
    assert projection.legacy_values[0].value == "D"
    with pytest.raises(FrozenInstanceError):
        projection.reference = REFERENCE + timedelta(days=1)


def test_cross_month_rollover_keeps_scoped_week_claim_and_leaves_new_month_unassigned():
    start, later = ny("2026-09-28T09:15"), ny("2026-10-01T09:15")
    week = contexts(start)["week"].cycle
    h = revise(InterpretationHistory(), week, revision="week-input")
    row = project_stack(run_id="r", reference=later, history=h).cycles[4]
    assert row.claim is h.claims[0]
    assert row.context.cycle == week
    assert row.context.position == "Q4"
    assert row.claim.market_reference == REFERENCE


def test_year_rollover_does_not_borrow_prior_cycle_or_another_runs_head():
    old = contexts(REFERENCE)["year"].cycle
    h = revise(InterpretationHistory(), old, revision="old")
    next_reference = ny("2027-01-05T09:15")
    new = contexts(next_reference)["year"].cycle
    h = revise(h, new, revision="other", run="other")
    row = project_stack(run_id="r", reference=next_reference, history=h).cycles[2]
    assert row.claim is None and row.inference.state == "Unresolved"
    assert row.context.prior_q4_id == old.quarters[3].id


@pytest.mark.parametrize("arguments", [
    {"run_id": ""}, {"branch_id": ""}, {"channel": "Working"},
    {"reference": datetime(2026, 10, 8)}, {"legacy_context": {"quarter": None}},
])
def test_projection_rejects_missing_scope_reference_or_malformed_legacy_input(arguments):
    defaults = dict(run_id="r", reference=REFERENCE, history=InterpretationHistory())
    defaults.update(arguments)
    with pytest.raises(ValueError):
        project_stack(**defaults)


def test_projection_rejects_inconsistent_cycle_identity_and_claim_inference():
    cycle = contexts(REFERENCE)["year"].cycle
    history = revise(InterpretationHistory(), cycle, revision="input")
    altered = replace(history.claims[0], cycle=replace(cycle, parent_quarter_id="invented"))
    with pytest.raises(ValueError, match="temporal content"):
        project_stack(run_id="r", reference=REFERENCE, history=InterpretationHistory((altered,)))
    altered = replace(history.claims[0], inference=replace(history.claims[0].inference, state="invented"))
    with pytest.raises(ValueError, match="retained anchors"):
        project_stack(run_id="r", reference=REFERENCE, history=InterpretationHistory((altered,)))


@pytest.mark.parametrize("text", ["0001-01-01T09:15", "9999-12-31T09:15"])
def test_unrepresentable_calendar_quartets_reject_instead_of_guessing(text):
    with pytest.raises(ValueError, match="supported datetime range"):
        resolve_higher_cycles(ny(text))
