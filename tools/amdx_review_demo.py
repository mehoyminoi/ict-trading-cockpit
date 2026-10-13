"""Synthetic later-Review pairings; no database, UI, feeds or trading policy."""
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ict_cockpit.analysis.amdx import Anchor, InterpretationHistory, Role, intraday_cycles
from ict_cockpit.analysis.amdx_review import ReviewHistory
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE


def worked_examples():
    reference = datetime(2026, 10, 8, 9, 15, tzinfo=MARKET_TIMEZONE)
    day, _ = intraday_cycles(reference)
    source = InterpretationHistory()
    cases = (
        ("E1", "Expected", Role.D, day.quarters[0].start - timedelta(minutes=1)),
        ("E2", "Expected", Role.M, reference),
        ("O1", "Observed", Role.M, day.quarters[-1].end),
    )
    for i, (id, channel, role, market_reference) in enumerate(cases):
        args = dict(claim_id=id, run_id="synthetic-review-run", branch_id="working",
                    channel=channel, cycle=day, quarter_id=day.quarters[2].id,
                    anchor=Anchor(f"anchor-{id}", day.quarters[2].id, role, "synthetic-technician"),
                    recorded_at=reference + timedelta(minutes=i), market_reference=market_reference)
        source = source.revise_working(**args) if id == "E2" else source.accept(**args)
    review = ReviewHistory(source)
    for i, (id, expected, head) in enumerate((("P1", "E1", None), ("P2", "E2", "P1"))):
        review = review.record(comparison_id=id, expected_claim_id=expected,
                               observed_claim_id="O1", expected_head_id=head,
                               recorded_at=reference + timedelta(minutes=10 + i),
                               market_reference=day.quarters[-1].end)
    assert ReviewHistory.from_payload(json.loads(json.dumps(review.to_payload()))) == review
    return review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the versioned synthetic archive")
    args = parser.parse_args()
    review = worked_examples()
    if args.json:
        print(json.dumps(review.to_payload(), indent=2))
        return
    print("Synthetic later-Review examples — no Watch display or baseline default.")
    for pair in review.comparisons:
        summary = review.summarize(pair.id)
        expected = review.claim(pair.expected_claim_id)
        observed = review.claim(pair.observed_claim_id)
        print(f"{pair.id}: {expected.id} {expected.inference.candidates[0].value} / "
              f"{observed.id} {observed.inference.candidates[0].value}: "
              f"{summary.order_relation}; {summary.subtype_relation}.")
        print(f"  Market-reference timing: {summary.expected_timing} / {summary.observed_timing}.")
    print("P1 remains retained after P2 selects an alternate basis; O1 is unchanged.")
    print("Mixed legacy/working claims and comparison archive round-trip: PASS.")
    print("These are supplied Replay references, not evidence of a live forecast or price classification.")


if __name__ == "__main__":
    main()
