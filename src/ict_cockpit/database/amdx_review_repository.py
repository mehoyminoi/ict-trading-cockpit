"""Insert-only Review pairings with owned, atomic observation/pair actions."""
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import json

from ict_cockpit.analysis.amdx import (
    Anchor, Claim, Cycle, InterpretationHistory, LEGACY_POLICY, OBSERVED_POLICY,
    claim_payload, cycle_from_payload, payload, require_id, timestamp,
)
from ict_cockpit.analysis.amdx_review import Comparison, PAIRING_POLICY, ReviewHistory, StaleComparison
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate, _json


def _request(operation: str, arguments: dict) -> dict:
    return {"version": 1, "operation": operation, "arguments": payload(arguments)}


def _observed_request(arguments: dict) -> dict:
    return {"version": 1, "policy": OBSERVED_POLICY, "arguments": payload(arguments)}


OBSERVED_COLUMNS = ("id", "comparison_id", "run_id", "cycle_id", "parent_claim_id",
                    "parent_comparison_id", "result_claim_id", "result_comparison_id",
                    "changed", "basis_count", "comparison_count", "payload_json")


@dataclass(frozen=True)
class ObservedRevisionResult:
    claim: Claim | None
    comparison: Comparison | None
    changed: bool


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
        if self.connection.execute("SELECT 1 FROM amdx_observed_command WHERE id=? OR comparison_id=?", (id, id)).fetchone():
            raise ValueError("An observed action identity cannot be reused for another action")

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
        observed_commands = self.connection.execute(
            f"SELECT {','.join(OBSERVED_COLUMNS)} FROM amdx_observed_command WHERE run_id=? ORDER BY rowid",
            (run_id,),
        ).fetchall()
        new_pairs = {dict(zip(OBSERVED_COLUMNS, r))["result_comparison_id"] for r in observed_commands if dict(zip(OBSERVED_COLUMNS, r))["changed"]}
        if {r[0] for r in receipts} & new_pairs or {r[0] for r in receipts} | new_pairs != {p.id for p in review.comparisons}:
            raise ValueError("Review history has missing or unrelated command receipts")
        for pair in review.comparisons:
            if pair.id in new_pairs:
                continue
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
        for row in observed_commands:
            self._validate_observed_command(review, dict(zip(OBSERVED_COLUMNS, row)))
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
        self.require_free_identity(id)
        return None

    def _observed_command(self, id: str) -> dict | None:
        row = self.connection.execute(
            f"SELECT {','.join(OBSERVED_COLUMNS)} FROM amdx_observed_command WHERE id=?", (id,)
        ).fetchone()
        return dict(zip(OBSERVED_COLUMNS, row)) if row is not None else None

    def validate_observed_claim_receipt(self, claim: dict, parent: str | None, basis_count: int) -> None:
        command = self._observed_command(claim["id"])
        if command is None or (
            command["run_id"], command["cycle_id"], command["parent_claim_id"],
            command["result_claim_id"], command["result_comparison_id"], command["changed"], command["basis_count"]
        ) != (claim["run_id"], claim["cycle"]["id"], parent, claim["id"], command["comparison_id"], 1, basis_count):
            raise ValueError("Observed claim disagrees with its command receipt")
        args = dict(claim_id=claim["id"], comparison_id=command["comparison_id"],
                    run_id=claim["run_id"], branch_id=claim["branch_id"], cycle=claim["cycle"],
                    quarter_id=claim["action_quarter_id"], anchor=claim["action_anchor"],
                    recorded_at=claim["recorded_at"], market_reference=claim["market_reference"],
                    expected_observed_head_id=parent, expected_comparison_head_id=command["parent_comparison_id"],
                    clear_applicability=claim["action"] == "ClearApplicability")
        if command["payload_json"] != _json(_observed_request(args)):
            raise ValueError("Observed claim disagrees with its original request")
        expected = None
        if command["parent_comparison_id"] is not None:
            old = self.connection.execute("SELECT run_id,branch_id,cycle_id,expected_claim_id FROM amdx_comparison WHERE id=?",
                                          (command["parent_comparison_id"],)).fetchone()
            if old is None or old[:3] != (claim["run_id"], claim["branch_id"], claim["cycle"]["id"]):
                raise ValueError("Observed comparison predecessor has inconsistent scope")
            expected = old[3]
        pair = Comparison(command["comparison_id"], claim["run_id"], claim["branch_id"], claim["cycle"]["id"],
                          expected, claim["id"], command["parent_comparison_id"],
                          timestamp(claim["recorded_at"]), timestamp(claim["market_reference"]))
        stored = self.connection.execute("SELECT sequence,payload_json FROM amdx_comparison WHERE id=?",
                                         (pair.id,)).fetchone()
        if stored is None or stored[1] != _json({"version": 1, "comparison": payload(pair)}) or (
            self.connection.execute("SELECT COUNT(*) FROM amdx_comparison WHERE run_id=? AND sequence<?",
                                    (pair.run_id, stored[0])).fetchone()[0] != command["comparison_count"]
        ):
            raise ValueError("Observed claim disagrees with its retained comparison")

    def _validate_observed_command(self, review: ReviewHistory, command: dict) -> ObservedRevisionResult:
        envelope = json.loads(command["payload_json"])
        if set(envelope) != {"version", "policy", "arguments"} or type(envelope["version"]) is not int or (
            envelope["version"] != 1 or envelope["policy"] != OBSERVED_POLICY
        ):
            raise ValueError("Unsupported observed command envelope")
        arguments = envelope["arguments"]
        require_id(command["comparison_id"])
        if command["id"] == command["comparison_id"] or any(
            self.connection.execute(sql, params).fetchone()
            for sql, params in (
                ("SELECT 1 FROM amdx_claim WHERE id=?", (command["comparison_id"],)),
                ("SELECT 1 FROM amdx_comparison WHERE id=?", (command["id"],)),
                ("SELECT 1 FROM amdx_working_command WHERE id IN (?,?)", (command["id"],command["comparison_id"])),
                ("SELECT 1 FROM amdx_observed_command WHERE id!=? AND (id IN (?,?) OR comparison_id IN (?,?))",
                 (command["id"],command["id"],command["comparison_id"],command["id"],command["comparison_id"])),
            )
        ):
            raise ValueError("Observed command has a reused request identity")
        required = {"claim_id", "comparison_id", "run_id", "branch_id", "cycle", "quarter_id", "anchor",
                    "recorded_at", "market_reference", "expected_observed_head_id", "expected_comparison_head_id",
                    "clear_applicability"}
        if set(arguments) != required or (
            arguments["claim_id"], arguments["comparison_id"], arguments["run_id"], arguments["cycle"]["id"],
            arguments["expected_observed_head_id"], arguments["expected_comparison_head_id"]
        ) != (command["id"], command["comparison_id"], command["run_id"], command["cycle_id"],
              command["parent_claim_id"], command["parent_comparison_id"]):
            raise ValueError("Observed command disagrees with its original scope/heads")
        cycle = cycle_from_payload(arguments["cycle"])
        stored_cycle = self.connection.execute("SELECT payload_json FROM amdx_cycle_identity WHERE id=?",
                                               (cycle.id,)).fetchone()
        if stored_cycle is None or stored_cycle[0] != _json(payload(cycle)):
            raise ValueError("Observed command disagrees with its stable cycle identity")
        if type(command["basis_count"]) is not int or type(command["comparison_count"]) is not int or not (
            0 <= command["basis_count"] <= len(review.interpretations.claims)
                and 0 <= command["comparison_count"] <= len(review.comparisons)) or (
            command["changed"] and command["comparison_count"] == len(review.comparisons)
        ):
            raise ValueError("Observed command has an invalid source snapshot")
        source = InterpretationHistory(review.interpretations.claims[:command["basis_count"]])
        prefix = ReviewHistory(source, review.comparisons[:command["comparison_count"]])
        scope = command["run_id"], arguments["branch_id"], command["cycle_id"]
        previous = next((c for c in reversed(source.claims) if (c.run_id,c.branch_id,c.channel,c.cycle.id) == (*scope[:2], "Observed", scope[2])), None)
        old_pair = prefix.head(*scope)
        if (previous.id if previous else None, old_pair.id if old_pair else None) != (
            command["parent_claim_id"], command["parent_comparison_id"]
        ):
            raise ValueError("Observed command's inspected heads disagree with its snapshot")
        recorded = timestamp(arguments["recorded_at"])
        if old_pair and recorded < old_pair.recorded_at:
            raise ValueError("Observed action recording time precedes its comparison head")
        updated = source.revise_observed(
            claim_id=command["id"], run_id=command["run_id"], branch_id=arguments["branch_id"], channel="Observed",
            cycle=cycle, quarter_id=arguments["quarter_id"],
            anchor=Anchor(**arguments["anchor"]) if arguments["anchor"] is not None else None,
            recorded_at=recorded, market_reference=timestamp(arguments["market_reference"]),
            clear_applicability=arguments["clear_applicability"],
        )
        changed = len(updated.claims) != len(source.claims)
        if changed != bool(command["changed"]):
            raise ValueError("Observed command changed/no-op result disagrees with its basis")
        claim = review.claim(command["result_claim_id"]) if command["result_claim_id"] else None
        pair = next((p for p in review.comparisons if p.id == command["result_comparison_id"]), None)
        if changed:
            if (claim != updated.claims[-1] or command["result_claim_id"] != command["id"]
                or pair is None or pair.id != command["comparison_id"] or pair.observed_claim_id != claim.id
                or review.comparisons[command["comparison_count"]] != pair
                or pair.expected_claim_id != (old_pair.expected_claim_id if old_pair else None)):
                raise ValueError("Observed command has an inconsistent revised result")
        elif claim != previous or pair != old_pair or any(c.id == command["id"] for c in review.interpretations.claims) or any(p.id == command["comparison_id"] for p in review.comparisons):
            raise ValueError("Observed no-op has an inconsistent original result")
        return ObservedRevisionResult(claim, pair, changed)

    def _insert_pair(self, pair: Comparison) -> None:
        self.connection.execute("""
            INSERT INTO amdx_comparison
            (id, run_id, branch_id, cycle_id, expected_claim_id, observed_claim_id, parent_comparison_id, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair.id, pair.run_id, pair.branch_id, pair.cycle_id, pair.expected_claim_id,
              pair.observed_claim_id, pair.previous_comparison_id,
              _json({"version": 1, "comparison": payload(pair)})))

    def _insert(self, pair: Comparison, operation: str, arguments: dict) -> None:
        self._insert_pair(pair)
        self.connection.execute("""
            INSERT INTO amdx_review_command (id, run_id, operation, observed_claim_id, payload_json)
            VALUES (?, ?, ?, ?, ?)
        """, (pair.id, pair.run_id, operation, pair.observed_claim_id, _json(_request(operation, arguments))))

    def revise_observed(self, *, claim_id: str, comparison_id: str, run_id: str, branch_id: str,
                        cycle: Cycle, quarter_id: str, anchor: Anchor | None,
                        recorded_at: datetime, market_reference: datetime,
                        expected_observed_head_id: str | None, expected_comparison_head_id: str | None,
                        clear_applicability: bool = False) -> ObservedRevisionResult:
        """One accepted observed revision; preserve only a deliberately saved basis.

        A repeated explicit meaning reserves both request identities without
        adding a profile or pairing. Exact original retries return their result.
        """
        arguments = dict(claim_id=claim_id, comparison_id=comparison_id, run_id=run_id,
                         branch_id=branch_id, cycle=cycle, quarter_id=quarter_id, anchor=anchor,
                         recorded_at=recorded_at, market_reference=market_reference,
                         expected_observed_head_id=expected_observed_head_id,
                         expected_comparison_head_id=expected_comparison_head_id,
                         clear_applicability=clear_applicability)
        encoded = _json(_observed_request(arguments))
        with self.amdx._transaction():
            review = self.get_history(run_id)
            existing = self._observed_command(claim_id)
            if existing is not None:
                if existing["payload_json"] != encoded:
                    raise ValueError("An observed command identity cannot be overwritten or reused")
                return self._validate_observed_command(review, existing)
            for id in (claim_id, comparison_id):
                self.require_free_identity(id)
                if any(self.connection.execute(f"SELECT 1 FROM {table} WHERE id=?", (id,)).fetchone()
                       for table in ("amdx_claim", "amdx_working_command")):
                    raise ValueError("A stored identity cannot be reused for observed revision")
            if claim_id == comparison_id:
                raise ValueError("Observed command and comparison require distinct identities")
            previous = next((c for c in reversed(review.interpretations.claims) if (
                c.run_id,c.branch_id,c.channel,c.cycle.id
            ) == (run_id,branch_id,"Observed",cycle.id)), None)
            old_pair = review.head(run_id, branch_id, cycle.id)
            if (previous.id if previous else None) != expected_observed_head_id:
                raise StaleAMDXUpdate("Observed quartet changed; inspect its latest claim before revising")
            if (old_pair.id if old_pair else None) != expected_comparison_head_id:
                raise StaleComparison("Comparison selection changed; inspect it before revising the observation")
            if old_pair and recorded_at < old_pair.recorded_at:
                raise ValueError("Observed recording time cannot precede its comparison head")
            updated = review.interpretations.revise_observed(
                claim_id=claim_id, run_id=run_id, branch_id=branch_id, channel="Observed", cycle=cycle,
                quarter_id=quarter_id, anchor=anchor, recorded_at=recorded_at, market_reference=market_reference,
                clear_applicability=clear_applicability,
            )
            changed = len(updated.claims) != len(review.interpretations.claims)
            result_claim, result_pair = previous, old_pair
            self.amdx._store_cycle(cycle)
            if changed:
                result_claim = updated.claims[-1]
                extended = review.with_interpretations(updated).record(
                    comparison_id=comparison_id,
                    expected_claim_id=old_pair.expected_claim_id if old_pair else None,
                    observed_claim_id=result_claim.id, expected_head_id=expected_comparison_head_id,
                    recorded_at=recorded_at, market_reference=market_reference,
                )
                result_pair = extended.comparisons[-1]
                self.connection.execute("""
                    INSERT INTO amdx_claim(id,run_id,branch_id,channel,cycle_id,parent_claim_id,payload_json)
                    VALUES (?,?,?,?,?,?,?)
                """, (claim_id,run_id,branch_id,"Observed",cycle.id,expected_observed_head_id,
                      _json({"version": 3, "claim": claim_payload(result_claim)})))
                self._insert_pair(result_pair)
            self.connection.execute("""
                INSERT INTO amdx_observed_command
                (id,comparison_id,run_id,cycle_id,parent_claim_id,parent_comparison_id,
                 result_claim_id,result_comparison_id,changed,basis_count,comparison_count,payload_json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (claim_id,comparison_id,run_id,cycle.id,expected_observed_head_id,expected_comparison_head_id,
                  result_claim.id if result_claim else None, result_pair.id if result_pair else None,
                  int(changed),len(review.interpretations.claims),len(review.comparisons),encoded))
            return ObservedRevisionResult(result_claim, result_pair, changed)

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
