"""Durable higher-context adapter over the existing AMDX transactions.

No migration, legacy conversion, live clock or UI policy. Callers own process
permissions; targets retain the inspected run/channel/cycle/reference/heads.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import json

from ict_cockpit.analysis.amdx import Anchor, Cycle, Role, XSubtype, aware, require_id, timestamp
from ict_cockpit.analysis.amdx_context import (
    HIGHER_LEVELS, StackProjection, project_stack, resolve_higher_cycles,
)
from ict_cockpit.analysis.amdx_review import Comparison
from ict_cockpit.analysis.market_time import as_new_york
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate, WorkingRevisionResult
from ict_cockpit.database.amdx_review_repository import ObservedRevisionResult


@dataclass(frozen=True)
class ContextSnapshot:
    projection: StackProjection
    comparison_heads: tuple[Comparison, ...]
    reference_source: str


@dataclass(frozen=True)
class HigherEditTarget:
    run_id: str
    channel: str
    cycle: Cycle
    quarter_id: str
    market_reference: datetime
    expected_head_id: str | None
    expected_comparison_head_id: str | None
    reference_source: str
    branch_id: str = "working"


class AMDXContextRepository:
    def __init__(self, amdx):
        self.amdx = amdx
        self.connection = amdx.connection

    def _run_fields(self, run_id):
        require_id(run_id)
        row = self.connection.execute("""
            SELECT market_context_snapshot_json, qt_context_json,
                   review_observed_qt_context_json FROM trading_session_run WHERE id=?
        """, (run_id,)).fetchone()
        if row is None:
            raise ValueError("Higher context requires an existing saved trading run")
        fields = tuple(json.loads(value or "{}") for value in row)
        if any(not isinstance(value, dict) for value in fields):
            raise ValueError("Saved run context must contain object payloads")
        return fields

    @staticmethod
    def _saved_reference(snapshot):
        value = snapshot.get("reference_market_time")
        if value is None or value == "":
            raise ValueError("Higher observed context requires a saved run-start timestamp; "
                             "a legacy day label alone is insufficient")
        try:
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Expected a timestamp")
            return as_new_york(timestamp(value))
        except (ValueError, TypeError, AttributeError) as error:
            raise ValueError("Saved run-start reference is invalid for higher observed context") from error

    def load_stack(self, run_id: str, *, channel: str = "Expected",
                   reference: datetime | None = None, branch_id: str = "working") -> ContextSnapshot:
        if channel not in ("Expected", "Observed"):
            raise ValueError("Channel must be Expected or Observed")
        with self.amdx.review._snapshot():
            stored, expected_legacy, observed_legacy = self._run_fields(run_id)
            if channel == "Observed":
                if reference is not None:
                    raise ValueError("Higher observed reference comes from the saved run, not a caller clock")
                reference = self._saved_reference(stored)
                source, legacy = "Saved run-start reference", observed_legacy
            else:
                reference = as_new_york(aware(reference))
                source, legacy = "Explicit reference", expected_legacy
            review = self.amdx.review.get_history(run_id)
            projection = project_stack(run_id=run_id, channel=channel, branch_id=branch_id,
                reference=reference, history=review.interpretations, legacy_context=legacy)
            heads = tuple(head for row in projection.cycles
                          if (head := review.head(run_id, branch_id, row.context.cycle.id)) is not None)
            return ContextSnapshot(projection, heads, source)

    @staticmethod
    def prepare_target(snapshot: ContextSnapshot, level: str,
                       position: int | None = None) -> HigherEditTarget:
        view = snapshot.projection
        if level not in HIGHER_LEVELS or view.branch_id != "working":
            raise ValueError("Higher entry requires an identified higher level in the working branch")
        row = next(item for item in view.cycles if item.context.cycle.layer == level)
        if position is None:
            quarter = row.context.active_quarter
            if quarter is None:
                raise ValueError("No active higher quarter; explicitly select Q1–Q4 to inspect/edit this quartet")
        else:
            if type(position) is not int or position not in (1, 2, 3, 4):
                raise ValueError("Quarter position must be 1 through 4")
            quarter = row.context.cycle.quarters[position - 1]
        pair = next((p for p in snapshot.comparison_heads if p.cycle_id == row.context.cycle.id), None)
        return HigherEditTarget(view.run_id, view.channel, row.context.cycle, quarter.id,
            view.reference, row.claim.id if row.claim else None,
            pair.id if pair and view.channel == "Observed" else None, snapshot.reference_source)

    @staticmethod
    def _validate_target(target, *, canonical=True):
        require_id(target.run_id)
        if target.channel not in ("Expected", "Observed") or target.branch_id != "working":
            raise ValueError("Higher entry requires the Expected/Observed working scope")
        expected_source = "Saved run-start reference" if target.channel == "Observed" else "Explicit reference"
        if target.reference_source != expected_source:
            raise ValueError("Higher target has inconsistent reference provenance")
        aware(target.market_reference)
        if target.cycle.layer not in HIGHER_LEVELS:
            raise ValueError("Higher entry requires a higher-cycle target")
        if canonical:
            context = next((c for c in resolve_higher_cycles(target.market_reference)
                            if c.cycle.layer == target.cycle.layer), None)
            if context is None or target.cycle != context.cycle:
                raise ValueError("Higher target disagrees with its versioned temporal identity")
        if target.quarter_id not in {q.id for q in target.cycle.quarters}:
            raise ValueError("Higher target is outside its quartet")
        if target.channel == "Expected" and target.expected_comparison_head_id is not None:
            raise ValueError("Working entry has no comparison head")

    def revise(self, target: HigherEditTarget, *, claim_id: str, recorded_at: datetime,
               role: Role | None = None, anchor_id: str | None = None,
               source_ref: str = "", subtype: XSubtype | None = None, note: str = "",
               comparison_id: str | None = None, clear_applicability: bool = False
               ) -> WorkingRevisionResult | ObservedRevisionResult:
        self._validate_target(target, canonical=False)
        require_id(claim_id)
        aware(recorded_at)
        if role is None:
            if anchor_id is not None or subtype is not None or source_ref or note:
                raise ValueError("A clear action cannot also carry anchor content")
            anchor = None
        else:
            anchor = Anchor(anchor_id, target.quarter_id, role, source_ref, subtype, note=note)
        if target.channel == "Observed":
            require_id(comparison_id)
        elif comparison_id is not None:
            raise ValueError("Working entry does not reserve an observed comparison identity")
        arguments = dict(claim_id=claim_id, run_id=target.run_id, branch_id=target.branch_id,
            cycle=target.cycle, quarter_id=target.quarter_id, anchor=anchor,
            recorded_at=recorded_at, market_reference=target.market_reference,
            clear_applicability=clear_applicability)
        with self.amdx._transaction():
            table = "amdx_observed_command" if target.channel == "Observed" else "amdx_working_command"
            retry = self.connection.execute(f"SELECT 1 FROM {table} WHERE id=?", (claim_id,)).fetchone() is not None
            # Recorded retries use their immutable request/payload, including
            # temporal definitions no longer selected by the current resolver.
            self._validate_target(target, canonical=not retry)
            if target.channel == "Observed":
                # An exact committed retry replays its original receipt/basis;
                # only a new request is checked against current provenance.
                if not retry:
                    current = self._saved_reference(self._run_fields(target.run_id)[0])
                    # Same-zone datetime equality ignores the repeated-hour
                    # fold. Compare actual instants, including their offsets.
                    if current.astimezone(timezone.utc) != target.market_reference.astimezone(timezone.utc):
                        raise StaleAMDXUpdate("Saved run-start reference changed; reload higher context before entry")
                return self.amdx.review._revise_observed_locked(**arguments,
                    comparison_id=comparison_id, expected_observed_head_id=target.expected_head_id,
                    expected_comparison_head_id=target.expected_comparison_head_id)
            return self.amdx._revise_working_locked(**arguments, channel="Expected",
                expected_head_id=target.expected_head_id)
