"""Later Review preserves selected profiles, not a hindsight-selected winner."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from ict_cockpit.analysis.amdx import (
    Anchor, InterpretationHistory, Role, XSubtype, intraday_cycles,
)
from ict_cockpit.analysis.amdx_review import ReviewHistory, StaleComparison
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE


REFERENCE = datetime(2026, 10, 8, 9, 15, tzinfo=MARKET_TIMEZONE)
DAY, SESSION = intraday_cycles(REFERENCE)


def add(history, name, role, *, channel="Expected", position=3, cycle=DAY,
        branch="working", run="run", reference=REFERENCE, subtype=None,
        working=False):
    args = dict(
        claim_id=name, run_id=run, branch_id=branch, channel=channel,
        cycle=cycle, quarter_id=cycle.quarters[position - 1].id,
        anchor=Anchor(f"anchor-{name}", cycle.quarters[position - 1].id, role,
                      "synthetic-technician", subtype) if role is not None else None,
        recorded_at=REFERENCE + timedelta(minutes=len(history.claims)),
        market_reference=reference,
    )
    return history.revise_working(**args) if working else history.accept(**args)


def fixture():
    history = add(InterpretationHistory(), "E1", Role.D, reference=DAY.quarters[0].start - timedelta(minutes=1))
    history = add(history, "E2", Role.M, working=True)
    return add(history, "O1", Role.M, channel="Observed", reference=DAY.quarters[-1].end)


def record(history, id="P1", expected="E1", observed="O1", head=None, minutes=10):
    return history.record(comparison_id=id, expected_claim_id=expected,
                          observed_claim_id=observed, expected_head_id=head,
                          recorded_at=REFERENCE + timedelta(minutes=minutes),
                          market_reference=DAY.quarters[-1].end)


def test_initial_and_adapted_expectations_can_be_compared_without_rewriting_observation():
    source = fixture()
    review = record(ReviewHistory(source))
    alternate = record(review, id="P2", expected="E2", head="P1", minutes=11)
    assert alternate.interpretations == source
    assert alternate.comparisons[0] == review.comparisons[0]
    assert alternate.summarize("P1").order_relation == "Different order"
    assert alternate.summarize("P2").order_relation == "Same order"
    assert alternate.summarize("P2").subtype_relation == "Both subtypes unresolved"
    assert alternate.summarize("P1").expected_timing == "Before cycle"
    assert alternate.summarize("P2").expected_timing == "During cycle"
    assert alternate.summarize("P1").observed_timing == "After cycle"
    assert record(alternate) is alternate  # Retry retains original predecessor.
    with pytest.raises(FrozenInstanceError):
        alternate.comparisons[0].expected_claim_id = "E2"


def test_later_expectation_does_not_retarget_existing_or_missing_baseline():
    source = add(InterpretationHistory(), "O1", Role.D, channel="Observed")
    review = record(ReviewHistory(source), expected=None)
    source = add(source, "E1", Role.D, reference=DAY.quarters[-1].end + timedelta(hours=1))
    extended = review.with_interpretations(source)
    assert extended.comparisons == review.comparisons
    assert extended.summarize("P1").order_relation == "No expected baseline"
    explicit_late = record(extended, id="P2", head="P1", minutes=11)
    assert explicit_late.summarize("P2").expected_timing == "After cycle"
    assert explicit_late.comparisons[0].expected_claim_id is None


@pytest.mark.parametrize("side,field,value", [
    ("expected", "run", "another-run"),
    ("observed", "run", "another-run"),
    ("expected", "branch", "alternative"),
    ("observed", "branch", "alternative"),
    ("expected", "cycle", SESSION),
    ("observed", "cycle", SESSION),
])
def test_unrelated_runs_branches_or_layers_cannot_be_paired(side, field, value):
    e_args = {field: value} if side == "expected" else {}
    o_args = {field: value} if side == "observed" else {}
    source = add(InterpretationHistory(), "E1", Role.D, **e_args)
    source = add(source, "O1", Role.D, channel="Observed", **o_args)
    with pytest.raises(ValueError, match="same run, branch and quartet"):
        record(ReviewHistory(source))


@pytest.mark.parametrize("expected,observed", [("O1", "O1"), ("E1", "E1"), ("missing", "O1")])
def test_channel_reversal_and_missing_bases_are_rejected(expected, observed):
    with pytest.raises(ValueError):
        record(ReviewHistory(fixture()), expected=expected, observed=observed)


def test_stale_repair_is_deliberate_and_identity_drift_is_rejected():
    original = record(ReviewHistory(fixture()))
    with pytest.raises(StaleComparison):
        record(original, id="P2", expected="E2")
    for change in ({"expected": "E2"}, {"head": "P1"}, {"minutes": 11}):
        with pytest.raises(ValueError, match="identity"):
            record(original, **change)
    with pytest.raises(ValueError, match="identity"):
        record(ReviewHistory(fixture()), id="E1")
    with pytest.raises(ValueError, match="before its source"):
        record(ReviewHistory(fixture()), minutes=0)
    with pytest.raises(ValueError, match="backward"):
        record(original, id="P2", head="P1", minutes=9)


@pytest.mark.parametrize("expected_role,observed_role", [
    (Role.UNKNOWN, Role.D), (Role.D, Role.UNKNOWN),
    (Role.NOT_APPLICABLE, Role.D), (Role.D, Role.NOT_APPLICABLE),
    (Role.A, Role.D),  # A at Q3 remains an inspectable original conflict.
])
def test_uncertainty_applicability_and_original_conflicts_are_not_forced_to_a_match(expected_role, observed_role):
    source = add(InterpretationHistory(), "E1", expected_role)
    source = add(source, "O1", observed_role, channel="Observed")
    review = record(ReviewHistory(source))
    assert review.summarize("P1").order_relation == "Not comparable"
    assert review.claim("E1").anchors[0].role == expected_role


@pytest.mark.parametrize("expected,observed,relation", [
    (None, XSubtype.REVERSAL, "Expected subtype unresolved"),
    (XSubtype.REVERSAL, None, "Observed subtype unresolved"),
    (XSubtype.REVERSAL, XSubtype.REVERSAL, "Same subtype"),
    (XSubtype.CONTINUATION, XSubtype.REVERSAL, "Different subtype"),
])
def test_order_agreement_does_not_claim_a_predicted_x_subtype(expected, observed, relation):
    source = add(InterpretationHistory(), "E1", Role.X, position=4, subtype=expected)
    source = add(source, "O1", Role.X, position=4, subtype=observed, channel="Observed")
    summary = record(ReviewHistory(source)).summarize("P1")
    assert (summary.order_relation, summary.subtype_relation) == ("Same order", relation)


def test_conditional_unknown_remains_in_retained_basis_even_when_order_is_resolved():
    source = add(InterpretationHistory(), "E1", Role.M, working=True)
    source = add(source, "E2", Role.UNKNOWN, position=1, working=True)
    source = add(source, "O1", Role.M, channel="Observed")
    review = record(ReviewHistory(source), expected="E2")
    assert review.summarize("P1").order_relation == "Same order"
    assert review.claim("E2").anchors[-1].role is Role.UNKNOWN
    assert review.claim("E2").inference.roles[0].role is Role.X
    assert review.summarize("P1").subtype_relation == "Both subtypes unresolved"


def test_comparison_heads_are_independent_for_parent_child_and_alternative_scopes():
    source = fixture()
    source = add(source, "session-O", Role.M, cycle=SESSION, channel="Observed")
    source = add(source, "alternative-O", Role.D, branch="alternative", channel="Observed")
    review = record(ReviewHistory(source))
    review = record(review, id="PS", expected=None, observed="session-O")
    review = record(review, id="PA", expected=None, observed="alternative-O")
    assert review.head("run", "working", DAY.id).id == "P1"
    assert review.head("run", "working", SESSION.id).id == "PS"
    assert review.head("run", "alternative", DAY.id).id == "PA"


@pytest.mark.parametrize("field,value", [
    ("expected_claim_id", "absent"), ("observed_claim_id", "E1"),
    ("run_id", "another-run"), ("previous_comparison_id", "absent"),
    ("policy", "future-policy"), ("recorded_at", "2026-01-01T00:00:00+00:00"),
    ("market_reference", "2026-10-08T09:15:00"),
])
def test_archive_rejects_inconsistent_pairing_basis_policy_or_time(field, value):
    archive = record(ReviewHistory(fixture())).to_payload()
    archive["comparisons"][0][field] = value
    with pytest.raises(ValueError):
        ReviewHistory.from_payload(archive)


def test_mixed_archive_survives_a_separate_process_and_does_not_expose_live_mutable_data():
    review = record(ReviewHistory(fixture()))
    archive = review.to_payload()
    detached = deepcopy(archive)
    detached["interpretations"]["claims"][0]["inference"]["state"] = "Unresolved"
    with pytest.raises(ValueError, match="inference"):
        ReviewHistory.from_payload(detached)
    assert ReviewHistory.from_payload(json.loads(json.dumps(archive))) == review
    code = ('import json,sys; from ict_cockpit.analysis.amdx_review import ReviewHistory; '
            'h=ReviewHistory.from_payload(json.load(sys.stdin)); '
            'print(h.summarize("P1").order_relation)')
    result = subprocess.run([sys.executable, "-c", code], input=json.dumps(archive),
                            capture_output=True, text=True, check=True,
                            env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")},
                            cwd=Path(__file__).resolve().parents[1])
    assert result.stdout.strip() == "Different order"
    assert review.to_payload() == archive


def test_source_history_cannot_be_removed_reordered_or_rewritten():
    review = record(ReviewHistory(fixture()))
    for source in (InterpretationHistory(), InterpretationHistory(review.interpretations.claims[::-1])):
        with pytest.raises(ValueError, match="replaced or removed"):
            review.with_interpretations(source)
    tampered = replace(review.interpretations.claims[0], market_reference=REFERENCE)
    source = InterpretationHistory((tampered,) + review.interpretations.claims[1:])
    with pytest.raises(ValueError, match="replaced or removed"):
        review.with_interpretations(source)


@pytest.mark.parametrize("key,value", [("version", 2), ("version", True), ("policy", "automatic-latest")])
def test_future_archive_envelopes_are_not_silently_adopted(key, value):
    archive = record(ReviewHistory(fixture())).to_payload()
    archive[key] = value
    with pytest.raises(ValueError, match="envelope"):
        ReviewHistory.from_payload(archive)


def test_duplicate_pair_extra_fields_and_bad_predecessor_are_rejected():
    review = record(ReviewHistory(fixture()))
    with pytest.raises(ValueError, match="identity"):
        ReviewHistory(review.interpretations, review.comparisons * 2)
    archive = review.to_payload()
    archive["comparisons"][0]["default"] = "first"
    with pytest.raises(ValueError, match="fields"):
        ReviewHistory.from_payload(archive)
    with pytest.raises(ValueError, match="predecessor"):
        ReviewHistory(review.interpretations, (replace(review.comparisons[0], previous_comparison_id="later"),))


def test_legacy_only_archive_preserves_original_claim_bytes_and_requires_explicit_baseline_argument():
    source = add(InterpretationHistory(), "E1", Role.D)
    source = add(source, "O1", Role.D, channel="Observed")
    original = source.to_payload()
    assert original["version"] == 1
    review = record(ReviewHistory(source))
    assert review.to_payload()["interpretations"] == original
    assert ReviewHistory.from_payload(review.to_payload()) == review
    with pytest.raises(TypeError):
        review.record(comparison_id="missing-explicit-choice", observed_claim_id="O1",
                      expected_head_id="P1", recorded_at=REFERENCE + timedelta(minutes=11),
                      market_reference=REFERENCE)


def test_worked_demo_uses_explicit_pairings_and_replays_without_database_or_ui():
    import runpy

    demo = runpy.run_path(str(Path(__file__).resolve().parents[1] / "tools" / "amdx_review_demo.py"))
    review = demo["worked_examples"]()
    assert review.summarize("P1").order_relation == "Different order"
    assert review.summarize("P2").order_relation == "Same order"
    assert [p.expected_claim_id for p in review.comparisons] == ["E1", "E2"]
