"""Transactional, insert-only AMDX history owned by existing saved runs."""
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3

from ict_cockpit.analysis.amdx import (
    Anchor, Claim, Cycle, InterpretationHistory, LEGACY_POLICY, OBSERVED_POLICY, WORKING_POLICY,
    aware, claim_payload, payload, require_id, timestamp,
)
from ict_cockpit.analysis.amdx_rules import Evaluation


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


class StaleAMDXUpdate(ValueError):
    """The scope changed after a caller inspected it; reload before revising."""


@dataclass(frozen=True)
class StoredEvaluation:
    evaluation: Evaluation
    recorded_at: datetime
    basis_claim_id: str | None


@dataclass(frozen=True)
class WorkingRevisionResult:
    claim: Claim | None
    changed: bool


def _working_request(*, clear_applicability=False, **arguments):
    return {"version": 1, **payload(arguments), "clear_applicability": clear_applicability}


class AMDXRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        from ict_cockpit.database.amdx_review_repository import AMDXReviewRepository
        self.review = AMDXReviewRepository(self)
        from ict_cockpit.database.amdx_context_repository import AMDXContextRepository
        self.context = AMDXContextRepository(self)
        from ict_cockpit.database.amdx_catalog_repository import AMDXCatalogRepository
        self.catalog = AMDXCatalogRepository(self)
        from ict_cockpit.database.amdx_master_repository import AMDXMasterRepository
        self.master = AMDXMasterRepository(self)

    @contextmanager
    def _transaction(self):
        # Own the commit boundary. Never commit or roll back unrelated caller work.
        if self.connection.in_transaction:
            raise RuntimeError("AMDX actions require a connection without a pending transaction")
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise

    def _require_run(self, run_id):
        require_id(run_id)
        if self.connection.execute("SELECT 1 FROM trading_session_run WHERE id = ?", (run_id,)).fetchone() is None:
            raise ValueError("AMDX history requires an existing saved trading run")

    def _store_cycle(self, cycle: Cycle):
        encoded = _json(payload(cycle))
        row = self.connection.execute("SELECT payload_json FROM amdx_cycle_identity WHERE id = ?", (cycle.id,)).fetchone()
        if row:
            if row[0] != encoded:
                raise ValueError("Stable cycle identity has different temporal content")
        else:
            self.connection.execute("INSERT INTO amdx_cycle_identity (id, payload_json) VALUES (?, ?)", (cycle.id, encoded))

    def get_history(self, run_id: str) -> InterpretationHistory:
        self._require_run(run_id)
        rows = self.connection.execute("""
            SELECT id, branch_id, channel, cycle_id, parent_claim_id, payload_json
            FROM amdx_claim WHERE run_id = ? ORDER BY sequence
        """, (run_id,)).fetchall()
        claims, heads = [], {}
        for id, branch, channel, cycle_id, parent, encoded in rows:
            item = json.loads(encoded)
            if item.get("version") not in (1, 2, 3):
                raise ValueError("Unsupported stored AMDX claim version")
            claim = item["claim"]
            if {1: LEGACY_POLICY, 2: WORKING_POLICY, 3: OBSERVED_POLICY}[item["version"]] != claim.get("action_policy", LEGACY_POLICY):
                raise ValueError("Claim envelope disagrees with its action policy")
            if (claim["id"], claim["run_id"], claim["branch_id"], claim["channel"], claim["cycle"]["id"]) != (
                id, run_id, branch, channel, cycle_id
            ):
                raise ValueError("AMDX claim payload disagrees with its stored ownership/scope")
            key = branch, channel, cycle_id
            if parent != heads.get(key):
                raise ValueError("AMDX scope has an inconsistent revision chain")
            cycle_row = self.connection.execute("SELECT payload_json FROM amdx_cycle_identity WHERE id = ?", (cycle_id,)).fetchone()
            if cycle_row is None or cycle_row[0] != _json(claim["cycle"]):
                raise ValueError("AMDX claim disagrees with its stable cycle identity")
            if item["version"] == 2:
                receipt = self.connection.execute("""
                    SELECT run_id, cycle_id, parent_claim_id, result_claim_id, changed, payload_json
                    FROM amdx_working_command WHERE id = ?
                """, (id,)).fetchone()
                request = _working_request(
                    claim_id=id, run_id=run_id, branch_id=branch, channel=channel,
                    cycle=claim["cycle"], quarter_id=claim["action_quarter_id"],
                    anchor=claim["action_anchor"], recorded_at=claim["recorded_at"],
                    market_reference=claim["market_reference"], expected_head_id=parent,
                    clear_applicability=claim["action"] == "ClearApplicability",
                )
                if receipt != (run_id, cycle_id, parent, id, 1, _json(request)):
                    raise ValueError("Working claim disagrees with its command receipt")
            elif item["version"] == 3:
                self.review.validate_observed_claim_receipt(claim, parent, len(claims))
            heads[key] = id
            claims.append(claim)
        return InterpretationHistory.from_payload({"version": 3, "claims": claims})

    def accept(self, *, claim_id: str, run_id: str, branch_id: str, channel: str,
               cycle: Cycle, quarter_id: str, anchor: Anchor | None,
               recorded_at: datetime, market_reference: datetime,
               expected_head_id: str | None) -> Claim:
        """Validate, append and commit one pinned accepted choice/clear atomically.

        expected_head_id is mandatory: None means this scope was inspected empty.
        Repeating an identical action ID is idempotent, including after later edits.
        """
        with self._transaction():
            return self._accept(
                claim_id=claim_id, run_id=run_id, branch_id=branch_id, channel=channel,
                cycle=cycle, quarter_id=quarter_id, anchor=anchor,
                recorded_at=recorded_at, market_reference=market_reference,
                expected_head_id=expected_head_id,
            )

    def _accept(self, *, claim_id: str, run_id: str, branch_id: str, channel: str,
                cycle: Cycle, quarter_id: str, anchor: Anchor | None,
                recorded_at: datetime, market_reference: datetime,
                expected_head_id: str | None) -> Claim:
        """Append inside an already-owned transaction, also used by Review."""
        if not self.connection.in_transaction:
            raise RuntimeError("An owned AMDX transaction is required")
        self.review.require_free_identity(claim_id)
        history = self.get_history(run_id)
        if self.connection.execute("SELECT 1 FROM amdx_working_command WHERE id = ?", (claim_id,)).fetchone():
            raise ValueError("A working command identity cannot be reused for legacy accumulation")
        existing = self.connection.execute("SELECT run_id, parent_claim_id FROM amdx_claim WHERE id = ?", (claim_id,)).fetchone()
        if existing:
            claim = next((c for c in history.claims if c.id == claim_id), None)
            action_anchor = next((a for a in claim.anchors if a.quarter_id == claim.action_quarter_id), None) if claim else None
            if claim is None or (
                claim.run_id, claim.branch_id, claim.channel, claim.cycle, claim.action_quarter_id,
                action_anchor, claim.recorded_at, claim.market_reference, existing[1]
            ) != (run_id, branch_id, channel, cycle, quarter_id, anchor, recorded_at, market_reference, expected_head_id):
                raise ValueError("A stored claim identity cannot be overwritten or reused")
            return claim
        previous = next((c for c in reversed(history.claims) if (
            c.branch_id, c.channel, c.cycle.id
        ) == (branch_id, channel, cycle.id)), None)
        if (previous.id if previous else None) != expected_head_id:
            raise StaleAMDXUpdate("AMDX scope changed; reload its latest claim before accepting this revision")
        updated = history.accept(
            claim_id=claim_id, run_id=run_id, branch_id=branch_id, channel=channel,
            cycle=cycle, quarter_id=quarter_id, anchor=anchor,
            recorded_at=recorded_at, market_reference=market_reference,
        )
        claim = updated.claims[-1]
        self._store_cycle(cycle)
        self.connection.execute("""
            INSERT INTO amdx_claim (id, run_id, branch_id, channel, cycle_id, parent_claim_id, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (claim.id, run_id, branch_id, channel, cycle.id, expected_head_id,
              _json({"version": 1, "claim": claim_payload(claim)})))
        return claim

    def revise_working(self, *, expected_head_id: str | None, clear_applicability: bool = False,
                       **arguments) -> WorkingRevisionResult:
        with self._transaction():
            return self._revise_working_locked(expected_head_id=expected_head_id,
                clear_applicability=clear_applicability, **arguments)

    def _revise_working_locked(self, *, expected_head_id: str | None, clear_applicability: bool = False,
                       **arguments) -> WorkingRevisionResult:
        """Shared action inside an already-owned transaction."""
        if not self.connection.in_transaction:
            raise RuntimeError("A working revision requires an owned transaction")
        request = _working_request(**arguments, expected_head_id=expected_head_id,
                                   clear_applicability=clear_applicability)
        self.review.require_free_identity(arguments["claim_id"])
        history = self.get_history(arguments["run_id"])
        receipt = self.connection.execute("""
            SELECT run_id, cycle_id, parent_claim_id, result_claim_id, changed, payload_json
            FROM amdx_working_command WHERE id = ?
        """, (arguments["claim_id"],)).fetchone()
        if receipt:
            if receipt[5] != _json(request) or receipt[:3] != (
                arguments["run_id"], arguments["cycle"].id, expected_head_id
            ):
                raise ValueError("A working command identity cannot be overwritten or reused")
            result = next((c for c in history.claims if c.id == receipt[3]), None)
            if (receipt[3] is not None and result is None) or (
                result and (result.branch_id, result.channel, result.cycle) != (
                    arguments["branch_id"], arguments["channel"], arguments["cycle"]
                )
            ) or (receipt[4] and (receipt[3] != arguments["claim_id"] or result.action_policy != WORKING_POLICY)) or (
                not receipt[4] and receipt[3] != expected_head_id
            ):
                raise ValueError("Working command receipt has an inconsistent result basis")
            basis_index = next((i for i, c in enumerate(history.claims) if c.id == expected_head_id), -1)
            basis = InterpretationHistory(history.claims[:basis_index + 1])
            replay = basis.revise_working(**arguments, clear_applicability=clear_applicability)
            if bool(len(replay.claims) != len(basis.claims)) != bool(receipt[4]) or (
                receipt[4] and replay.claims[-1] != result
            ):
                raise ValueError("Working command receipt disagrees with its action basis")
            return WorkingRevisionResult(result, bool(receipt[4]))
        if self.connection.execute("SELECT 1 FROM amdx_claim WHERE id = ?", (arguments["claim_id"],)).fetchone():
            raise ValueError("A stored claim identity cannot be reused for a working command")
        previous = next((c for c in reversed(history.claims) if (
            c.branch_id, c.channel, c.cycle.id
        ) == (arguments["branch_id"], arguments["channel"], arguments["cycle"].id)), None)
        if (previous.id if previous else None) != expected_head_id:
            raise StaleAMDXUpdate("AMDX scope changed; reload before revising its working quartet")
        updated = history.revise_working(**arguments, clear_applicability=clear_applicability)
        changed = len(updated.claims) != len(history.claims)
        result = updated.claims[-1] if changed else previous
        self._store_cycle(arguments["cycle"])
        if changed:
            self.connection.execute("""
                INSERT INTO amdx_claim (id, run_id, branch_id, channel, cycle_id, parent_claim_id, payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (result.id, result.run_id, result.branch_id, result.channel, result.cycle.id,
                  expected_head_id, _json({"version": 2, "claim": claim_payload(result)})))
        self.connection.execute("""
            INSERT INTO amdx_working_command
            (id, run_id, cycle_id, parent_claim_id, result_claim_id, changed, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (arguments["claim_id"], arguments["run_id"], arguments["cycle"].id,
              expected_head_id, result.id if result else None, int(changed), _json(request)))
        return WorkingRevisionResult(result, changed)


    def save_evaluation(self, evaluation: Evaluation, *, recorded_at: datetime,
                        basis_claim_id: str | None = None) -> StoredEvaluation:
        aware(recorded_at)
        # Reject fabricated/inconsistent result objects before storing them.
        evaluation = Evaluation.from_payload(evaluation.to_payload())
        encoded = _json(evaluation.to_payload())
        with self._transaction():
            self._require_run(evaluation.run_id)
            existing = self.get_evaluation(evaluation.id)
            stored = StoredEvaluation(evaluation, recorded_at, basis_claim_id)
            if existing:
                if existing != stored:
                    raise ValueError("A stored evaluation identity cannot be overwritten or reused")
                return existing
            if basis_claim_id is not None:
                require_id(basis_claim_id)
                basis = next((c for c in self.get_history(evaluation.run_id).claims if c.id == basis_claim_id), None)
                if basis is None or basis.cycle != evaluation.cycle:
                    raise ValueError("Evaluation basis must identify a claim in this run and quartet")
            self._store_cycle(evaluation.cycle)
            for definition in evaluation.definitions:
                key = (definition.plan_revision, definition.id, definition.revision, definition.publication)
                definition_json = _json(payload(definition))
                row = self.connection.execute("""
                    SELECT payload_json FROM amdx_definition_revision
                    WHERE plan_revision = ? AND rule_id = ? AND rule_revision = ? AND publication = ?
                """, key).fetchone()
                if row:
                    if row[0] != definition_json:
                        raise ValueError("A recorded definition revision has different content; use a new revision")
                else:
                    self.connection.execute("""
                        INSERT INTO amdx_definition_revision (plan_revision, rule_id, rule_revision, publication, payload_json)
                        VALUES (?, ?, ?, ?, ?)
                    """, key + (definition_json,))
            self.connection.execute("""
                INSERT INTO amdx_evaluation (id, run_id, cycle_id, recorded_at, basis_claim_id, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (evaluation.id, evaluation.run_id, evaluation.cycle.id, recorded_at.isoformat(), basis_claim_id, encoded))
            return stored

    def get_evaluation(self, evaluation_id: str) -> StoredEvaluation | None:
        row = self.connection.execute("""
            SELECT run_id, cycle_id, recorded_at, basis_claim_id, payload_json
            FROM amdx_evaluation WHERE id = ?
        """, (evaluation_id,)).fetchone()
        if row is None:
            return None
        evaluation = Evaluation.from_payload(json.loads(row[4]))
        self._require_run(evaluation.run_id)
        if (evaluation.id, evaluation.run_id, evaluation.cycle.id) != (evaluation_id, row[0], row[1]):
            raise ValueError("Evaluation payload disagrees with stored ownership/scope")
        cycle_row = self.connection.execute("SELECT payload_json FROM amdx_cycle_identity WHERE id = ?", (row[1],)).fetchone()
        if cycle_row is None or cycle_row[0] != _json(payload(evaluation.cycle)):
            raise ValueError("Evaluation disagrees with its stable cycle identity")
        if row[3] is not None:
            basis = self.connection.execute("SELECT run_id, cycle_id FROM amdx_claim WHERE id = ?", (row[3],)).fetchone()
            if basis != (evaluation.run_id, evaluation.cycle.id):
                raise ValueError("Stored evaluation basis has inconsistent run/quartet ownership")
        for definition in evaluation.definitions:
            key = (definition.plan_revision, definition.id, definition.revision, definition.publication)
            stored = self.connection.execute("""
                SELECT payload_json FROM amdx_definition_revision
                WHERE plan_revision = ? AND rule_id = ? AND rule_revision = ? AND publication = ?
            """, key).fetchone()
            if stored is None or stored[0] != _json(payload(definition)):
                raise ValueError("Evaluation disagrees with its recorded definition revision")
        return StoredEvaluation(evaluation, timestamp(row[2]), row[3])

    def get_evaluations(self, run_id: str) -> tuple[StoredEvaluation, ...]:
        self._require_run(run_id)
        rows = self.connection.execute("SELECT id FROM amdx_evaluation WHERE run_id = ? ORDER BY sequence", (run_id,)).fetchall()
        return tuple(self.get_evaluation(row[0]) for row in rows)
