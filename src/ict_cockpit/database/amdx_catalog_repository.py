"""Asset-scoped catalog commands reusing the shared versioned quartet engine."""
from dataclasses import dataclass
from datetime import datetime
import json

from ict_cockpit.analysis.amdx import (
    Anchor, Cycle, InterpretationHistory, Role, canonical_timestamp,
    claim_payload, cycle_from_payload, payload, require_id, timestamp,
)
from ict_cockpit.analysis.amdx_catalog import CATALOG_POLICY, CaptureBasis, Catalog
from ict_cockpit.analysis.amdx_master import MasterCalendar, master_owner_payload, read_master_owner
from ict_cockpit.analysis.amdx_context import project_stack, resolve_stack_cycles
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate, WorkingRevisionResult, _json


@dataclass(frozen=True)
class CatalogTarget:
    catalog_id: str
    instrument: str
    channel: str
    cycle: Cycle
    quarter_id: str
    market_reference: datetime
    expected_head_id: str | None


def _apply(history, request, catalog):
    if set(request) != {"target", "anchor", "recorded_at", "capture", "clear_applicability", "id"}:
        raise ValueError("Unsupported catalog request fields")
    target = dict(request["target"])
    if set(target) != set(CatalogTarget.__dataclass_fields__):
        raise ValueError("Unsupported catalog target fields")
    target["cycle"] = cycle_from_payload(target["cycle"])
    target["market_reference"] = timestamp(target["market_reference"])
    target = CatalogTarget(**target)
    AMDXCatalogRepository._validate_target(target, catalog, canonical=False)
    capture = dict(request["capture"])
    if set(capture) != set(CaptureBasis.__dataclass_fields__):
        raise ValueError("Unsupported catalog capture provenance fields")
    if capture.get("information_available_at") is not None:
        capture["information_available_at"] = timestamp(capture["information_available_at"])
    capture = CaptureBasis(**capture)
    recorded_at = timestamp(request["recorded_at"])
    capture.validate_recording(recorded_at)
    previous = _head(history, catalog, target.channel, target.cycle.id)
    if (previous.id if previous else None) != target.expected_head_id:
        raise StaleAMDXUpdate("Catalog quartet changed; reload its scoped head before entry")
    arguments = dict(claim_id=request["id"], run_id=catalog.owner_id, branch_id="working",
        channel=target.channel, cycle=target.cycle, quarter_id=target.quarter_id,
        anchor=Anchor(**request["anchor"]) if request["anchor"] is not None else None,
        recorded_at=recorded_at, market_reference=target.market_reference,
        clear_applicability=request["clear_applicability"])
    action = history.revise_working if target.channel == "Expected" else history.revise_observed
    updated = action(**arguments)
    changed = len(updated.claims) != len(history.claims)
    return updated, WorkingRevisionResult(updated.claims[-1] if changed else previous, changed)


def _head(history, catalog, channel, cycle_id):
    return next((c for c in reversed(history.claims) if
        (c.run_id, c.channel, c.cycle.id) == (catalog.owner_id, channel, cycle_id)), None)


def _replay(catalog, commands):
    history, results = InterpretationHistory(), {}
    for command in commands:
        if set(command) != {"version", "policy", "request", "result"} or (
            type(command["version"]) is not int or command["version"] != 1 or command["policy"] != CATALOG_POLICY
        ):
            raise ValueError("Unsupported catalog command envelope")
        request = command["request"]
        if type(command["result"].get("changed")) is not bool:
            raise ValueError("Catalog change status must be an explicit boolean")
        require_id(request["id"])
        if request["id"] in results:
            raise ValueError("Catalog command identity is repeated")
        history, result = _apply(history, request, catalog)
        if command["result"] != _result_payload(result):
            raise ValueError("Catalog result disagrees with its immutable request/replay")
        results[request["id"]] = result
    return history, results


def _result_payload(result):
    return {"changed": result.changed, "claim": claim_payload(result.claim) if result.claim else None}


def read_catalog_archive(value):
    """Validate a self-contained archive, including original no-op provenance."""
    if set(value) != {"version", "policy", "catalog", "commands"} or (
        type(value["version"]) is not int or value["version"] not in (1, 2) or value["policy"] != CATALOG_POLICY
    ):
        raise ValueError("Unsupported catalog archive envelope")
    if value["version"] == 1:
        if set(value["catalog"]) != set(Catalog.__dataclass_fields__):
            raise ValueError("Unsupported catalog identity fields")
        catalog = Catalog(**value["catalog"])
    else:
        catalog = read_master_owner(value["catalog"])
    history, _ = _replay(catalog, value["commands"])
    return catalog, history


class AMDXCatalogRepository:
    def __init__(self, amdx):
        self.amdx = amdx
        self.connection = amdx.connection

    def create(self, catalog: Catalog):
        if not isinstance(catalog, Catalog):
            raise ValueError("Master owners require the canonical master creation action")
        encoded = _json(payload(catalog))
        with self.amdx._transaction():
            existing = self.connection.execute("SELECT payload_json FROM amdx_catalog WHERE id=?", (catalog.id,)).fetchone()
            if existing is not None:
                if existing[0] != encoded:
                    raise ValueError("Catalog identity cannot be reused with another instrument/definition")
                return catalog
            self.connection.execute("INSERT INTO amdx_catalog(id,instrument,payload_json) VALUES (?,?,?)",
                                    (catalog.id, catalog.instrument, encoded))
        return catalog

    def get(self, catalog_id):
        require_id(catalog_id)
        row = self.connection.execute("SELECT instrument,payload_json FROM amdx_catalog WHERE id=?", (catalog_id,)).fetchone()
        if row is None:
            raise ValueError("Catalog does not exist")
        value = json.loads(row[1])
        if set(value) == set(Catalog.__dataclass_fields__):
            catalog = Catalog(**value)
        else:
            catalog = read_master_owner(value)
        if (catalog.id, catalog.instrument) != (catalog_id, row[0]):
            raise ValueError("Catalog payload disagrees with stored ownership")
        return catalog

    def list_catalogs(self, *, instrument=None):
        rows = self.connection.execute("SELECT id FROM amdx_catalog WHERE (? IS NULL OR instrument=?) ORDER BY rowid",
                                       (instrument, instrument)).fetchall()
        # Preserve the old collection chooser's contract. Normal master access
        # uses amdx.master and never adds a fabricated Backtest/ForwardTest purpose.
        return tuple(c for r in rows if isinstance(c := self.get(r[0]), Catalog))

    def _commands(self, catalog):
        rows = self.connection.execute("SELECT id,cycle_id,channel,payload_json FROM amdx_catalog_command WHERE catalog_id=? ORDER BY sequence",
                                       (catalog.id,)).fetchall()
        commands = []
        for id, cycle, channel, encoded in rows:
            command = json.loads(encoded)
            request = command["request"]
            if (request["id"], request["target"]["cycle"]["id"], request["target"]["channel"]) != (id, cycle, channel):
                raise ValueError("Catalog command disagrees with stored ownership")
            registered = self.connection.execute("SELECT payload_json FROM amdx_cycle_identity WHERE id=?", (cycle,)).fetchone()
            if registered is None or registered[0] != _json(request["target"]["cycle"]):
                raise ValueError("Catalog cycle disagrees with the immutable registry")
            commands.append(command)
        return commands

    def history(self, catalog_id):
        with self.amdx.review._snapshot():
            catalog = self.get(catalog_id)
            return _replay(catalog, self._commands(catalog))[0]

    def current_heads(self, catalog_id, *, channel=None, level=None):
        """Enumerate this collection's stored occurrences without a date cutoff."""
        if channel is not None and channel not in ("Expected", "Observed"):
            raise ValueError("Channel must be Expected or Observed")
        with self.amdx.review._snapshot():
            history = self.history(catalog_id)
            heads = {}
            for claim in history.claims:
                heads[claim.channel, claim.cycle.id] = claim
            return tuple(c for c in heads.values() if
                         (channel is None or c.channel == channel) and
                         (level is None or c.cycle.layer == level))

    def load_stack(self, catalog_id, *, reference, channel="Observed"):
        with self.amdx.review._snapshot():
            catalog = self.get(catalog_id)
            history = _replay(catalog, self._commands(catalog))[0]
            return project_stack(run_id=catalog.owner_id, reference=reference,
                                 history=history, channel=channel)

    def prepare_target(self, catalog_id, *, reference, level, position=None, channel="Observed"):
        with self.amdx.review._snapshot():
            catalog = self.get(catalog_id)
            view = self.load_stack(catalog_id, reference=reference, channel=channel)
            row = next((r for r in view.cycles if r.context.cycle.layer == level), None)
            if row is None:
                raise ValueError("Select an identified AMDX level")
            if position is None:
                quarter = row.context.active_quarter
                if quarter is None:
                    raise ValueError("No active quarter; explicitly select Q1–Q4")
            else:
                if type(position) is not int or position not in (1, 2, 3, 4):
                    raise ValueError("Quarter position must be 1 through 4")
                quarter = row.context.cycle.quarters[position - 1]
            return CatalogTarget(catalog.id, catalog.instrument, channel, row.context.cycle,
                quarter.id, canonical_timestamp(view.reference), row.claim.id if row.claim else None)

    @staticmethod
    def _validate_target(target, catalog, *, canonical):
        if (target.catalog_id, target.instrument) != (catalog.id, catalog.instrument):
            raise ValueError("Catalog target has different collection/instrument ownership")
        if target.channel not in ("Expected", "Observed"):
            raise ValueError("Channel must be Expected or Observed")
        canonical_timestamp(target.market_reference)
        if target.quarter_id not in {q.id for q in target.cycle.quarters}:
            raise ValueError("Catalog target is outside its quartet")
        if canonical and target.cycle not in tuple(c.cycle for c in resolve_stack_cycles(target.market_reference)):
            raise ValueError("Catalog target disagrees with canonical temporal identity")

    def revise(self, target, *, command_id, recorded_at, role=None, anchor_id=None,
               source_ref="", subtype=None, note="", capture=CaptureBasis(), clear_applicability=False):
        require_id(command_id)
        recorded_at = canonical_timestamp(recorded_at)
        capture.validate_recording(recorded_at)
        if role is None:
            if anchor_id is not None or source_ref or subtype is not None or note:
                raise ValueError("Clear cannot also carry anchor content")
            anchor = None
        else:
            anchor = Anchor(anchor_id, target.quarter_id, Role(role), source_ref, subtype, note=note)
        request = dict(id=command_id, target=payload(target), anchor=payload(anchor),
            recorded_at=recorded_at.isoformat(), capture=payload(capture), clear_applicability=clear_applicability)
        with self.amdx._transaction():
            catalog = self.get(target.catalog_id)
            commands = self._commands(catalog)
            history, results = _replay(catalog, commands)
            existing = self.connection.execute("SELECT catalog_id,payload_json FROM amdx_catalog_command WHERE id=?", (command_id,)).fetchone()
            self._validate_target(target, catalog, canonical=existing is None)
            if existing is not None:
                old = json.loads(existing[1])
                if existing[0] != catalog.id or _json(old["request"]) != _json(request):
                    raise ValueError("Catalog command identity cannot be overwritten or reused")
                return results[command_id]
            _, result = _apply(history, request, catalog)
            self.amdx._store_cycle(target.cycle)
            command = dict(version=1, policy=CATALOG_POLICY, request=request, result=_result_payload(result))
            self.connection.execute("INSERT INTO amdx_catalog_command(id,catalog_id,cycle_id,channel,payload_json) VALUES (?,?,?,?,?)",
                (command_id, catalog.id, target.cycle.id, target.channel, _json(command)))
            return result

    def export_archive(self, catalog_id):
        with self.amdx.review._snapshot():
            catalog = self.get(catalog_id)
            commands = self._commands(catalog)
            _replay(catalog, commands)
            is_master = isinstance(catalog, MasterCalendar)
            return dict(version=2 if is_master else 1, policy=CATALOG_POLICY,
                        catalog=master_owner_payload(catalog) if is_master else payload(catalog), commands=commands)
