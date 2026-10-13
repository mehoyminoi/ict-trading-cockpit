"""Insert-only Review pairings with owned, atomic observation/pair actions."""
from contextlib import contextmanager
from datetime import datetime
import json

from ict_cockpit.analysis.amdx import Anchor, Cycle, LEGACY_POLICY, payload, require_id
from ict_cockpit.analysis.amdx_review import Comparison, PAIRING_POLICY, ReviewHistory
from ict_cockpit.database.amdx_repository import _json


def _request(operation: str, arguments: dict) -> dict:
    return {"version": 1, "operation": operation, "arguments": payload(arguments)}


class AMDXReviewRepository:
    def __init__(self, amdx):
        self.amdx = amdx
        self.connection = amdx.connection

    @contextmanager
    def _snapshot(self):
        # Multiple reads must see the same claim/pair/receipt snapshot. Existing
        # caller or writer transactions retain their own commit boundary.
        owned = not self.connection.in_transaction
        if owned:
            self.connection.execute("BEGIN")
        try:
            yield
            if owned:
                self.connection.commit()
        except BaseException:
            if owned:
                self.connection.rollback()
            raise

    def require_free_identity(self, id: str) -> None:
        """Claims/working commands cannot reuse an existing Review identity."""
        require_id(id)
        if self.connection.execute("SELECT 1 FROM amdx_comparison WHERE id = ?", (id,)).fetchone():
            raise ValueError("A Review identity cannot be reused for another action")

    def get_history(self, run_id: str) -> ReviewHistory:
        with self._snapshot():
            return self._get_history(run_id)

    def _get_history(self, run_id: str) -> ReviewHistory:
        source = self.amdx.get_history(run_id)
        rows = self.connection.execute("""
            SELECT id, branch_id, cycle_id, expected_claim_id, observed_claim_id,
                   parent_comparison_id, payload_json
            FROM amdx_comparison WHERE run_id = ? ORDER BY sequence
        """, (run_id,)).fetchall()
        items = []
        for id, branch, cycle, expected, observed, parent, encoded in rows:
            envelope = json.loads(encoded)
            if set(envelope) != {"version", "comparison"} or type(envelope["version"]) is not int or envelope["version"] != 1:
                raise ValueError("Unsupported stored Review comparison version")
            item = envelope["comparison"]
            if (item["id"], item["run_id"], item["branch_id"], item["cycle_id"],
                item["expected_claim_id"], item["observed_claim_id"], item["previous_comparison_id"]) != (
                id, run_id, branch, cycle, expected, observed, parent
            ):
                raise ValueError("Review payload disagrees with stored ownership/basis")
            items.append(item)
        review = ReviewHistory.from_payload({"version": 1, "policy": PAIRING_POLICY,
                                           "interpretations": source.to_payload(), "comparisons": items})
        receipts = self.connection.execute("""
            SELECT id, operation, observed_claim_id, payload_json
            FROM amdx_review_command WHERE run_id = ?
        """, (run_id,)).fetchall()
        if {r[0] for r in receipts} != {p.id for p in review.comparisons}:
            raise ValueError("Review history has missing or unrelated command receipts")
        for pair in review.comparisons:
            receipt = next(r for r in receipts if r[0] == pair.id)
            if receipt[1] == "Pair":
                arguments = dict(run_id=run_id, comparison_id=pair.id,
                                 expected_claim_id=pair.expected_claim_id,
                                 observed_claim_id=pair.observed_claim_id,
                                 expected_head_id=pair.previous_comparison_id,
                                 recorded_at=pair.recorded_at, market_reference=pair.market_reference)
            elif receipt[1] == "ObserveAndPair":
                observed = review.claim(pair.observed_claim_id)
                if observed.action_policy != LEGACY_POLICY or (
                    observed.recorded_at, observed.market_reference
                ) != (pair.recorded_at, pair.market_reference):
                    raise ValueError("Atomic observation/pair receipt disagrees with its source action")
                observed_parent = self.connection.execute("SELECT parent_claim_id FROM amdx_claim WHERE id = ?",
                                                          (observed.id,)).fetchone()[0]
                anchor = next((a for a in observed.anchors if a.quarter_id == observed.action_quarter_id), None)
                arguments = dict(comparison_id=pair.id, expected_claim_id=pair.expected_claim_id,
                                 expected_comparison_head_id=pair.previous_comparison_id,
                                 claim_id=observed.id, run_id=run_id, branch_id=pair.branch_id,
                                 cycle=observed.cycle, quarter_id=observed.action_quarter_id,
                                 anchor=anchor, recorded_at=pair.recorded_at,
                                 market_reference=pair.market_reference, expected_observed_head_id=observed_parent)
            else:
                raise ValueError("Unsupported Review command operation")
            if receipt[2:] != (pair.observed_claim_id, _json(_request(receipt[1], arguments))):
                raise ValueError("Review comparison disagrees with its original command receipt")
        return review

    def get_comparison(self, comparison_id: str) -> Comparison | None:
        require_id(comparison_id)
        with self._snapshot():
            row = self.connection.execute("SELECT run_id FROM amdx_comparison WHERE id = ?", (comparison_id,)).fetchone()
            if row is None:
                return None
            return next(p for p in self._get_history(row[0]).comparisons if p.id == comparison_id)

    def _retry(self, review: ReviewHistory, id: str, operation: str, arguments: dict) -> Comparison | None:
        require_id(id)
        receipt = self.connection.execute("""
            SELECT run_id, operation, observed_claim_id, payload_json FROM amdx_review_command WHERE id = ?
        """, (id,)).fetchone()
        if receipt is not None:
            pair = next((p for p in review.comparisons if p.id == id), None)
            if pair is None or receipt != (
                arguments["run_id"], operation, pair.observed_claim_id, _json(_request(operation, arguments))
            ):
                raise ValueError("A Review command identity cannot be overwritten or reused")
            return pair
        if self.connection.execute("SELECT 1 FROM amdx_comparison WHERE id = ?", (id,)).fetchone() or any(
            self.connection.execute(f"SELECT 1 FROM {table} WHERE id = ?", (id,)).fetchone()
            for table in ("amdx_claim", "amdx_working_command")
        ):
            raise ValueError("A stored action identity cannot be reused for Review")
        return None

    def _insert(self, pair: Comparison, operation: str, arguments: dict) -> None:
        self.connection.execute("""
            INSERT INTO amdx_comparison
            (id, run_id, branch_id, cycle_id, expected_claim_id, observed_claim_id, parent_comparison_id, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair.id, pair.run_id, pair.branch_id, pair.cycle_id, pair.expected_claim_id,
              pair.observed_claim_id, pair.previous_comparison_id,
              _json({"version": 1, "comparison": payload(pair)})))
        self.connection.execute("""
            INSERT INTO amdx_review_command (id, run_id, operation, observed_claim_id, payload_json)
            VALUES (?, ?, ?, ?, ?)
        """, (pair.id, pair.run_id, operation, pair.observed_claim_id, _json(_request(operation, arguments))))

    def record_comparison(self, *, run_id: str, comparison_id: str,
                          expected_claim_id: str | None, observed_claim_id: str,
                          expected_head_id: str | None, recorded_at: datetime,
                          market_reference: datetime) -> Comparison:
        arguments = dict(run_id=run_id, comparison_id=comparison_id,
                         expected_claim_id=expected_claim_id, observed_claim_id=observed_claim_id,
                         expected_head_id=expected_head_id, recorded_at=recorded_at, market_reference=market_reference)
        with self.amdx._transaction():
            review = self.get_history(run_id)
            retry = self._retry(review, comparison_id, "Pair", arguments)
            if retry is not None:
                return retry
            updated = review.record(**{key: value for key, value in arguments.items() if key != "run_id"})
            pair = updated.comparisons[-1]
            self._insert(pair, "Pair", arguments)
            return pair

    def record_observation(self, *, comparison_id: str, expected_claim_id: str | None,
                           expected_comparison_head_id: str | None, claim_id: str,
                           run_id: str, branch_id: str, cycle: Cycle, quarter_id: str,
                           anchor: Anchor | None, recorded_at: datetime, market_reference: datetime,
                           expected_observed_head_id: str | None) -> Comparison:
        arguments = dict(comparison_id=comparison_id, expected_claim_id=expected_claim_id,
                         expected_comparison_head_id=expected_comparison_head_id, claim_id=claim_id,
                         run_id=run_id, branch_id=branch_id, cycle=cycle, quarter_id=quarter_id,
                         anchor=anchor, recorded_at=recorded_at, market_reference=market_reference,
                         expected_observed_head_id=expected_observed_head_id)
        with self.amdx._transaction():
            review = self.get_history(run_id)
            retry = self._retry(review, comparison_id, "ObserveAndPair", arguments)
            if retry is not None:
                return retry
            if comparison_id == claim_id or any(
                self.connection.execute(f"SELECT 1 FROM {table} WHERE id = ?", (claim_id,)).fetchone()
                for table in ("amdx_claim", "amdx_working_command", "amdx_comparison")
            ):
                raise ValueError("Atomic observed entry requires a new distinct claim identity")
            self.amdx._accept(claim_id=claim_id, run_id=run_id, branch_id=branch_id,
                              channel="Observed", cycle=cycle, quarter_id=quarter_id, anchor=anchor,
                              recorded_at=recorded_at, market_reference=market_reference,
                              expected_head_id=expected_observed_head_id)
            review = review.with_interpretations(self.amdx.get_history(run_id))
            updated = review.record(comparison_id=comparison_id, expected_claim_id=expected_claim_id,
                                    observed_claim_id=claim_id, expected_head_id=expected_comparison_head_id,
                                    recorded_at=recorded_at, market_reference=market_reference)
            pair = updated.comparisons[-1]
            self._insert(pair, "ObserveAndPair", arguments)
            return pair
