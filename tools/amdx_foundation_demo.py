"""Read-only synthetic AMDX worked examples; no app database or trading policy."""
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ict_cockpit.analysis.amdx import Anchor, InterpretationHistory, Role, intraday_cycles
from ict_cockpit.analysis.amdx_rules import (
    Condition, Definition, Evaluation, Fact, Operator, OutputKind, evaluate,
)
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE


def worked_examples():
    reference = datetime(2026, 10, 8, 9, 15, tzinfo=MARKET_TIMEZONE)
    day, _ = intraday_cycles(reference)
    history = InterpretationHistory()
    for i, role in enumerate((Role.M, Role.D), 1):
        history = history.accept(
            claim_id=f"synthetic-claim-{i}", run_id="synthetic-run", branch_id="working",
            channel="Expected", cycle=day, quarter_id=day.quarters[2].id,
            anchor=Anchor(f"synthetic-anchor-{i}", day.quarters[2].id, role, "synthetic-technician"),
            recorded_at=reference + timedelta(minutes=i), market_reference=reference,
        )
    facts = (
        Fact("synthetic-asia-feature", day.quarters[0].id, "x-like", True, "", reference, "synthetic-input"),
        Fact("synthetic-london-feature", day.quarters[1].id, "major-manipulation", True, "", reference, "synthetic-input"),
    )
    definitions = (
        Definition("synthetic-asia", "fixture-v1", "fixture-plan", "Candidate", "day", 1,
                   OutputKind.ASSIGNED_ROLE, Role.X, 10,
                   (Condition(day.quarters[0].id, "x-like", Operator.EQ, True),),
                   "Synthetic manually supplied feature; not a validated classifier."),
        Definition("synthetic-london", "fixture-v1", "fixture-plan", "Candidate", "day", 2,
                   OutputKind.ASSIGNED_ROLE, Role.M, 0,
                   (Condition(day.quarters[1].id, "major-manipulation", Operator.EQ, True),),
                   "Synthetic priority prefers London manipulation."),
    )
    evaluation = evaluate(evaluation_id="synthetic-evaluation", run_id="synthetic-run", cycle=day,
                          market_reference=reference, definitions=definitions, facts=facts)
    snapshot = json.loads(json.dumps({"history": history.to_payload(), "criteria": evaluation.to_payload()}))
    assert InterpretationHistory.from_payload(snapshot["history"]) == history
    assert Evaluation.from_payload(snapshot["criteria"]) == evaluation
    return history, evaluation, snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the versioned synthetic archive")
    args = parser.parse_args()
    history, evaluation, snapshot = worked_examples()
    if args.json:
        print(json.dumps(snapshot, indent=2))
        return
    print("Synthetic AMDX foundation examples — no database, feed, plan publication or orders.")
    for claim in history.claims:
        roles = " / ".join(r.role.value + ("(?)" if r.role is Role.X and r.subtype is None else "")
                           for r in claim.inference.roles)
        print(f"{claim.id}: Q3={claim.anchors[0].role.value} → {claim.inference.candidates[0].value}: {roles}")
    print("Both accepted revisions remain in history.")
    print(f"Criteria: {evaluation.resolution_policy}; governing rule: {', '.join(evaluation.governing_rule_ids)}")
    print(f"London Q2=M → {evaluation.profile().candidates[0].value}; opposing Asia Q1=X result remains in the trace.")
    print("Versioned history and evaluation JSON round-trip: PASS.")


if __name__ == "__main__":
    main()
