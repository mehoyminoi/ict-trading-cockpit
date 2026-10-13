"""Structural and archival behavior; synthetic examples are not trading rules."""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import json

import pytest

from ict_cockpit.analysis.amdx import (
    Anchor, Cycle, InterpretationHistory, Profile, Quarter, Role, XSubtype,
    infer_profile, intraday_cycles,
)
from ict_cockpit.analysis.amdx_rules import (
    Condition, Definition, Evaluation, Fact, Operator, OutputKind, evaluate,
)
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, build_market_time_context


REFERENCE = datetime(2026, 10, 8, 9, 15, tzinfo=MARKET_TIMEZONE)


def cycles():
    return intraday_cycles(REFERENCE)


def anchor(cycle, position, role, *, id="anchor", subtype=None):
    return Anchor(id, cycle.quarters[position - 1].id, role, "synthetic-technician", subtype)


def accept(history, cycle, position, role, *, revision="1", branch="working", channel="Expected", run="run"):
    return history.accept(
        claim_id=f"claim-{revision}", run_id=run, branch_id=branch, channel=channel,
        cycle=cycle, quarter_id=cycle.quarters[position - 1].id,
        anchor=anchor(cycle, position, role, id=f"anchor-{revision}") if role is not None else None,
        recorded_at=REFERENCE + timedelta(minutes=int(revision)), market_reference=REFERENCE,
    )


@pytest.mark.parametrize("moment", [
    datetime(2026, 3, 9, 0, tzinfo=MARKET_TIMEZONE),
    datetime(2026, 11, 2, 6, tzinfo=MARKET_TIMEZONE),
    REFERENCE,
    datetime(2026, 10, 8, 18, tzinfo=MARKET_TIMEZONE),
])
def test_intraday_identity_and_clock_agree_with_accepted_runtime(moment):
    day, session = intraday_cycles(moment)
    context = build_market_time_context(moment).to_dict()
    assert day.id == f"day:{context['futures_trading_day']}"
    assert day.quarter_at(moment).label == context["session"]
    assert f"Q{day.quarter_at(moment).position}" == context["daily_quarter"]
    assert f"Q{session.quarter_at(moment).position}" == context["session_quarter"]
    assert session.parent_quarter_id == day.quarter_at(moment).id
    assert intraday_cycles(moment.astimezone(timezone.utc)) == (day, session)
    assert day.quarter_at(day.quarters[-1].end) is None
    assert session.quarter_at(session.quarters[1].start).position == 2


def test_no_active_quartet_on_closed_weekend_or_naive_reference():
    assert intraday_cycles(datetime(2026, 10, 10, 9, tzinfo=MARKET_TIMEZONE)) == ()
    with pytest.raises(ValueError, match="aware"):
        intraday_cycles(datetime(2026, 10, 8, 9))


@pytest.mark.parametrize("position,role,expected", [
    (1, Role.A, Profile.AMDX), (2, Role.M, Profile.AMDX),
    (3, Role.D, Profile.AMDX), (4, Role.X, Profile.AMDX),
    (1, Role.X, Profile.XAMD), (2, Role.A, Profile.XAMD),
    (3, Role.M, Profile.XAMD), (4, Role.D, Profile.XAMD),
])
def test_single_anchor_constrains_whole_quartet(position, role, expected):
    day, _ = cycles()
    result = infer_profile(day, (anchor(day, position, role),))
    assert result.candidates == (expected,)
    assert result.state == "Resolved"
    assert "".join(r.role.value for r in result.roles) == expected.value
    assert result.roles[position - 1].origin == "Technician"
    assert all(r.origin == "Implied" for i, r in enumerate(result.roles) if i != position - 1)
    assert next(r for r in result.roles if r.role is Role.X).subtype is None


def test_unknown_not_applicable_and_x_subtype_are_distinct():
    day, _ = cycles()
    result = infer_profile(day, (anchor(day, 3, Role.UNKNOWN),))
    assert result.candidates == (Profile.AMDX, Profile.XAMD)
    assert all(r.role is Role.UNKNOWN for r in result.roles)
    assert infer_profile(day, (anchor(day, 3, Role.NOT_APPLICABLE),)).state == "Not Applicable"
    result = infer_profile(day, (anchor(day, 4, Role.X, subtype=XSubtype.REVERSAL),))
    assert result.roles[3].subtype is XSubtype.REVERSAL
    with pytest.raises(ValueError, match="Only X"):
        anchor(day, 3, Role.D, subtype=XSubtype.REVERSAL)


def test_conflicts_unsupported_position_and_subtype_disagreement_remain_visible():
    day, _ = cycles()
    conflicting = (anchor(day, 1, Role.A, id="a1"), anchor(day, 2, Role.A, id="a2"))
    assert infer_profile(day, conflicting).state == "Conflict"
    assert infer_profile(day, (anchor(day, 2, Role.X),)).candidates == ()
    result = infer_profile(day, (
        anchor(day, 4, Role.X, id="c", subtype=XSubtype.CONTINUATION),
        anchor(day, 4, Role.X, id="r", subtype=XSubtype.REVERSAL),
    ))
    assert result.state == "Conflict" and result.roles == ()


def test_parent_child_quartets_are_independent_and_foreign_anchor_is_rejected():
    day, session = cycles()
    assert infer_profile(day, (anchor(day, 3, Role.D),)).candidates == (Profile.AMDX,)
    assert infer_profile(session, (anchor(session, 3, Role.M),)).candidates == (Profile.XAMD,)
    with pytest.raises(ValueError, match="outside"):
        infer_profile(session, (anchor(day, 3, Role.D),))


def test_cycle_identity_requires_ordered_unique_contiguous_quarters():
    day, _ = cycles()
    with pytest.raises(ValueError, match="four ordered"):
        replace(day, quarters=day.quarters[:3])
    with pytest.raises(ValueError, match="unique"):
        replace(day, quarters=(replace(day.quarters[0], id=day.quarters[1].id),) + day.quarters[1:])
    with pytest.raises(ValueError, match="contiguous"):
        replace(day, quarters=(replace(day.quarters[0], end=day.quarters[0].end - timedelta(minutes=1)),) + day.quarters[1:])


def test_actions_preserve_revisions_and_clearing_does_not_resurrect_old_anchor(tmp_path):
    day, _ = cycles()
    history = accept(InterpretationHistory(), day, 3, Role.M)
    history = accept(history, day, 3, Role.D, revision="2")
    history = accept(history, day, 3, None, revision="3")
    assert [c.inference.candidates for c in history.claims] == [
        (Profile.XAMD,), (Profile.AMDX,), (Profile.AMDX, Profile.XAMD),
    ]
    assert history.claims[-1].anchors == ()
    archive = tmp_path / "synthetic-history.json"
    archive.write_text(json.dumps(history.to_payload()))
    restored = InterpretationHistory.from_payload(json.loads(archive.read_text()))
    assert restored == history
    assert len(accept(restored, day, 3, Role.D, revision="4").claims) == 4
    with pytest.raises(FrozenInstanceError):
        history.claims[0].channel = "Observed"
    detached = history.to_payload()
    detached["claims"][0]["anchors"][0]["role"] = "D"
    assert history.claims[0].anchors[0].role is Role.M
    with pytest.raises(ValueError, match="disagrees"):
        InterpretationHistory.from_payload(detached)


def test_scoped_actions_preserve_conflicts_and_isolate_runs_branches_channels_cycles():
    day, session = cycles()
    history = accept(InterpretationHistory(), day, 1, Role.A)
    history = accept(history, day, 2, Role.A, revision="2")
    assert history.claims[-1].inference.state == "Conflict"
    for i, kwargs in enumerate(({"branch": "alternative"}, {"channel": "Observed"}, {"run": "other"}), 3):
        history = accept(history, day, 3, Role.M, revision=str(i), **kwargs)
        assert history.claims[-1].inference.candidates == (Profile.XAMD,)
        assert len(history.claims[-1].anchors) == 1
    history = accept(history, session, 3, Role.M, revision="6")
    assert history.claims[-1].cycle.id == session.id
    assert history.claims[1].inference.state == "Conflict"
    assert InterpretationHistory.from_payload(history.to_payload()) == history


def test_reused_ids_changed_bounds_and_wrong_pinned_targets_are_rejected():
    day, _ = cycles()
    history = accept(InterpretationHistory(), day, 3, Role.D)
    with pytest.raises(ValueError, match="identity already"):
        accept(history, day, 3, Role.M)
    changed = replace(day, quarters=tuple(replace(q, start=q.start + timedelta(days=1), end=q.end + timedelta(days=1)) for q in day.quarters))
    with pytest.raises(ValueError, match="different bounds"):
        accept(history, changed, 3, Role.M, revision="2")
    with pytest.raises(ValueError, match="pinned target"):
        history.accept(claim_id="new", run_id="run", branch_id="working", channel="Expected",
                       cycle=day, quarter_id=day.quarters[0].id, anchor=anchor(day, 3, Role.D),
                       recorded_at=REFERENCE, market_reference=REFERENCE)


def test_payload_revision_and_transcript_tampering_fail_explicitly():
    day, _ = cycles()
    history = accept(accept(InterpretationHistory(), day, 3, Role.D), day, 1, Role.A, revision="2")
    for mutate in (
        lambda p: p.update(version=99),
        lambda p: p["claims"][0].update(structural_revision="future"),
        lambda p: p["claims"][1].update(action_quarter_id=day.quarters[2].id),
    ):
        p = history.to_payload()
        mutate(p)
        with pytest.raises(ValueError):
            InterpretationHistory.from_payload(p)


def rule(day, *, id="synthetic-close", role=Role.A, position=1, priority=0, kind=OutputKind.ASSIGNED_ROLE):
    return Definition(id, "candidate-v1", "synthetic-plan-v1", "Candidate", "day", position,
                      kind, role, priority, (Condition(day.quarters[1].id, "closed-inside", Operator.EQ, True),),
                      "Synthetic explicit feature, not an adopted London classifier.")


def fact(day, *, value=True, at=REFERENCE, id="synthetic-input", unit=""):
    return Fact(id, day.quarters[1].id, "closed-inside", value, unit, at, "synthetic-capture-v1")


def evaluation(day, definitions, facts, *, id="evaluation", reference=REFERENCE):
    return evaluate(evaluation_id=id, run_id="synthetic-run", cycle=day,
                    market_reference=reference, definitions=definitions, facts=facts)


def test_input_scope_and_classification_target_are_separate():
    day, _ = cycles()
    result = evaluation(day, (rule(day),), (fact(day),))
    assert result.results[0].fact_ids == ("synthetic-input",)
    assert result.results[0].target_quarter_id == day.quarters[0].id
    assert result.profile().candidates == (Profile.AMDX,)
    assert result.profile().roles[0].origin == "Rule"


def test_priority_retains_opposing_matches_and_local_behavior_does_not_assign_role():
    day, _ = cycles()
    definitions = (rule(day, role=Role.X, priority=10),
                   rule(day, id="synthetic-manipulation", role=Role.M, position=2),
                   rule(day, id="synthetic-local", role=Role.X, kind=OutputKind.LOCAL_BEHAVIOR))
    result = evaluation(day, definitions, (fact(day),))
    # Both proposals remain visible; declared global priority governs the profile.
    assert infer_profile(day, result.assigned_anchors()).state == "Conflict"
    assert result.profile().candidates == (Profile.AMDX,)
    assert result.governing_rule_ids == ("synthetic-manipulation",)
    assert result.resolution_policy == "Cycle Profile Priority"
    definitions = (rule(day, role=Role.X, priority=10),
                   rule(day, id="synthetic-preferred", role=Role.A), definitions[-1])
    result = evaluation(day, definitions, (fact(day),))
    assert all(r.state == "Matched" for r in result.results)
    assert result.resolutions[0].selected_rule_ids == ("synthetic-preferred",)
    assert result.resolutions[1].role is Role.X
    assert result.profile().candidates == (Profile.AMDX,)
    assert len(result.assigned_anchors()) == 1


def test_equal_priority_disagreement_remains_unresolved_and_ties_can_agree():
    day, _ = cycles()
    first = rule(day)
    second = rule(day, id="synthetic-outside", role=Role.X)
    result = evaluation(day, (first, second), (fact(day),))
    assert result.resolutions[0].state == "Conflict"
    assert result.assigned_anchors() == ()
    result = evaluation(day, (first, replace(second, role=Role.A)), (fact(day),))
    assert result.resolutions[0].selected_rule_ids == (first.id, second.id)


@pytest.mark.parametrize("facts", [(), (None,), ("future",), ("unit",), ("type",), ("competing",)])
def test_missing_asof_units_types_and_competing_captures_stay_unknown(facts):
    day, _ = cycles()
    label = facts[0] if facts else "missing"
    inputs = {
        "missing": (), None: (fact(day, at=None),),
        "future": (fact(day, at=REFERENCE + timedelta(seconds=1)),),
        "unit": (fact(day, unit="handles"),), "type": (fact(day, value=1),),
        "competing": (fact(day), fact(day, id="second")),
    }[label]
    result = evaluation(day, (rule(day),), inputs)
    assert result.results[0].state == "Unknown"
    assert result.resolutions[0].state == "Unknown"
    assert result.assigned_anchors() == ()


def test_unknown_at_higher_priority_prevents_final_lower_priority_winner():
    day, _ = cycles()
    known = rule(day, priority=10)
    unknown = replace(rule(day, id="unknown", role=Role.X), conditions=(Condition("prior-scope", "missing", Operator.EQ, True),))
    result = evaluation(day, (known, unknown), (fact(day),))
    assert result.resolutions[0].state == "Unknown"
    assert result.assigned_anchors() == ()
    result = evaluation(day, (known, replace(unknown, priority=20)), (fact(day),))
    assert result.resolutions[0].role is Role.A
    assert result.results[1].state == "Unknown"


def test_numeric_conditions_have_explicit_units_and_boundaries():
    day, _ = cycles()
    criterion = replace(rule(day), conditions=(Condition("range", "excursion", Operator.GT, 0, "handles"),))
    input = Fact("price", "range", "excursion", 0.0, "handles", REFERENCE, "synthetic-price")
    assert evaluation(day, (criterion,), (input,)).results[0].state == "Not Matched"
    assert evaluation(day, (replace(criterion, conditions=(replace(criterion.conditions[0], operator=Operator.GE),)),), (input,)).results[0].state == "Matched"
    with pytest.raises(ValueError, match="finite scalar"):
        replace(input, value=float("nan"))


def test_false_conjunction_and_layer_exclusion_are_distinct_from_unknown():
    day, session = cycles()
    criterion = replace(rule(day), conditions=rule(day).conditions + (Condition("missing", "input", Operator.EQ, True),))
    result = evaluation(day, (criterion,), (fact(day, value=False),))
    assert result.results[0].state == "Not Matched"
    assert result.resolutions[0].state == "No Match"
    assert evaluation(session, (criterion,), ()).results[0].state == "Not Applicable"


def test_archived_evaluation_replays_original_revision_without_later_inputs(tmp_path):
    day, _ = cycles()
    original = evaluation(day, (replace(rule(day), publication="Published"),), (fact(day),))
    changed_definition = replace(original.definitions[0], revision="published-v2", role=Role.X)
    changed = evaluation(day, (changed_definition,), original.facts, id="comparison")
    assert original.profile().candidates == (Profile.AMDX,)
    assert changed.profile().candidates == (Profile.XAMD,)
    archive = tmp_path / "synthetic-evaluation.json"
    archive.write_text(json.dumps(original.to_payload()))
    assert Evaluation.from_payload(json.loads(archive.read_text())) == original
    # A future fact can be retained for provenance but not used in an earlier prediction.
    future = evaluation(day, (rule(day),), (fact(day, at=REFERENCE + timedelta(hours=1)),))
    assert Evaluation.from_payload(future.to_payload()).results[0].state == "Unknown"
    tampered = original.to_payload()
    tampered["evaluation"]["definitions"][0]["role"] = "X"
    with pytest.raises(ValueError, match="disagrees"):
        Evaluation.from_payload(tampered)


def test_definition_validation_rejects_implicit_targets_priorities_and_duplicate_revisions():
    day, _ = cycles()
    for changes in ({"target_position": 0}, {"priority": True}, {"conditions": ()}, {"publication": ""}):
        with pytest.raises(ValueError):
            replace(rule(day), **changes)
    with pytest.raises(ValueError, match="separate evaluations"):
        evaluation(day, (rule(day), replace(rule(day), revision="v2")), ())
    with pytest.raises(ValueError, match="unique"):
        evaluation(day, (rule(day),), (fact(day), fact(day)))


def test_cycle_priority_preserves_manual_conflict_and_blocks_unknown_other_target():
    day, _ = cycles()
    london = rule(day, id="london", position=2, role=Role.M, priority=1)
    asia = rule(day, id="asia", position=1, role=Role.X, priority=2)
    result = evaluation(day, (london, asia), (fact(day),))
    assert result.profile().roles[0].role is Role.A
    manual = anchor(day, 1, Role.X, id="manual")
    assert infer_profile(day, (manual,) + result.assigned_anchors()).state == "Conflict"
    unknown = replace(asia, priority=0, conditions=(Condition("missing", "feature", Operator.EQ, True),))
    result = evaluation(day, (london, unknown), (fact(day),))
    assert result.governing_state == "Unknown"
    assert result.profile().state == "Unresolved"
    assert result.governing_rule_ids == ()
    # Unknown and matched results cannot acquire implicit priority from input ordering.
    reversed_result = evaluation(day, (unknown, london), (fact(day),))
    assert reversed_result.profile() == result.profile()


def test_same_priority_across_quarters_must_support_one_consistent_profile():
    day, _ = cycles()
    definitions = (rule(day, id="asia", role=Role.X), rule(day, id="london", position=2, role=Role.M))
    result = evaluation(day, definitions, (fact(day),))
    assert result.profile().state == "Conflict"
    assert result.governing_rule_ids == ("asia", "london")
    result = evaluation(day, (replace(definitions[0], role=Role.A), definitions[1]), (fact(day),))
    assert result.profile().candidates == (Profile.AMDX,)


def test_unresolved_x_and_explicit_subtype_are_compatible_but_c_and_r_conflict():
    day, _ = cycles()
    untyped = rule(day, role=Role.X)
    typed = replace(rule(day, id="typed", role=Role.X), subtype=XSubtype.CONTINUATION)
    result = evaluation(day, (untyped, typed), (fact(day),))
    assert result.resolutions[0].state == "Resolved"
    assert result.resolutions[0].subtype is XSubtype.CONTINUATION
    assert result.profile().roles[0].subtype is XSubtype.CONTINUATION
    result = evaluation(day, (typed, replace(typed, id="other", subtype=XSubtype.REVERSAL)), (fact(day),))
    assert result.resolutions[0].state == "Conflict"
    assert result.profile().state == "Conflict"


def test_synthetic_demo_is_read_only_and_its_archive_can_be_loaded():
    import subprocess
    from pathlib import Path
    import sys

    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, str(root / "tools/amdx_foundation_demo.py"), "--json"],
                            cwd=root, capture_output=True, text=True, check=True)
    value = json.loads(result.stdout)
    assert len(InterpretationHistory.from_payload(value["history"]).claims) == 2
    assert Evaluation.from_payload(value["criteria"]).profile().candidates == (Profile.AMDX,)
