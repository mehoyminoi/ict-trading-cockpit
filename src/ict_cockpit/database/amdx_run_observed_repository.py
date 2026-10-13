"""One maintained Observed judgment with immutable per-run assessment receipts."""
from dataclasses import dataclass
from datetime import datetime
import json

from ict_cockpit.analysis.amdx import canonical_timestamp, payload, require_id, timestamp
from ict_cockpit.analysis.amdx_catalog import CaptureBasis
from ict_cockpit.analysis.amdx_context import HIGHER_LEVELS
from ict_cockpit.analysis.market_time import futures_trading_day_for
from ict_cockpit.database.amdx_master_repository import MasterTarget
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate, _json
from ict_cockpit.database.amdx_run_calendar_repository import _read_packet, _read_projection, _read_run_binding, _validate_launch_reference


POLICY = "amdx-run-observed-calendar-v1"


@dataclass(frozen=True)
class PreparedRunObservation:
    basis_json: str
    target: MasterTarget


@dataclass(frozen=True)
class RunObservationResult:
    id: str
    run_id: str
    recorded_at: datetime
    projection: object
    packet_json: str

    @property
    def packet(self):
        return json.loads(self.packet_json)

    @property
    def changed(self):
        return self.packet["result"]["calendar_command"]["result"]["changed"]

    @property
    def reason(self):
        return "Run assessment"


def _scope(binding, launch, context, target):
    original = _read_packet(launch)
    if original.reason != "Launch" or launch["binding"] != binding or original.operation_id != binding["launch_operation_id"]:
        raise ValueError("Observed assessment requires the original launch basis")
    if launch["run_context"] != binding["run_basis"] or original.recorded_at != timestamp(binding["bound_at"]):
        raise ValueError("Original launch packet differs from its bound raw basis/time")
    _validate_launch_reference(binding, original.projection.reference)
    if set(context) != set(binding["run_basis"]) or any(context[k] != binding["run_basis"][k] for k in
        ("id", "trading_day_id", "process_session_id", "run_environment", "run_purpose")):
        raise ValueError("Observed assessment has inconsistent run ownership")
    for key, content in context.items():
        if key.endswith("_json"):
            json.loads(content)
    timestamp(context["started_at"])
    saved = json.loads(context["market_context_snapshot_json"])
    initial = json.loads(binding["run_basis"]["market_context_snapshot_json"])
    if not isinstance(saved, dict) or saved.get("reference_market_time") != initial.get("reference_market_time"):
        raise StaleAMDXUpdate("Saved run-start provenance changed; reload Review")
    reference = timestamp(target["target"]["market_reference"])
    cycle = target["target"]["cycle"]
    if target["binding"]["id"] != binding["master_binding_id"] or (
        target["target"]["catalog_id"], target["target"]["instrument"], target["target"]["channel"]
    ) != (binding["catalog_id"], binding["instrument"], "Observed"):
        raise ValueError("Observed target has different instrument/binding/channel")
    if cycle["layer"] in HIGHER_LEVELS:
        if canonical_timestamp(reference) != canonical_timestamp(original.projection.reference):
            raise ValueError("Higher Review is limited to the original launch reference until bounded scope proof is implemented")
    elif cycle["layer"] in ("day", "session"):
        if futures_trading_day_for(reference) != futures_trading_day_for(original.projection.reference):
            raise ValueError("Observed assessment is outside its original reviewed trading day")
    else:
        raise ValueError("Unsupported Observed Review layer")


def _read_command(value):
    if set(value) != {"version", "policy", "request", "result"} or type(value["version"]) is not int or (
        value["version"] != 1 or value["policy"] != POLICY
    ):
        raise ValueError("Unsupported run Observed envelope")
    request, result = value["request"], value["result"]
    if set(request) != {"id", "recorded_at", "basis", "target", "calendar_request"} or set(result) != {
        "master", "projection", "calendar_command"
    }:
        raise ValueError("Unsupported run Observed fields")
    if set(request["target"]) != {"binding", "target"}:
        raise ValueError("Unsupported run Observed target fields")
    basis = request["basis"]
    if set(basis) != {"binding", "run_context", "launch", "parent_id", "master", "projection"}:
        raise ValueError("Unsupported run assessment basis")
    binding = _read_run_binding(basis["binding"])
    _scope(binding, basis["launch"], basis["run_context"], request["target"])
    before_binding, before = _read_projection(basis["projection"], basis["master"], channel="Observed")
    after_binding, after = _read_projection(result["projection"], result["master"], channel="Observed")
    if before_binding != after_binding or payload(before_binding) != request["target"]["binding"] or (
        before.reference != after.reference or before.run_id != after.run_id or before.market_open != after.market_open
    ) or (before_binding.id, before_binding.instrument, before_binding.catalog_id) != (
        binding["master_binding_id"], binding["instrument"], binding["catalog_id"]
    ):
        raise ValueError("Observed assessment changed master/reference ownership")
    command = result["calendar_command"]
    expected = request["calendar_request"]
    if command["request"] != expected or (expected["id"], expected["recorded_at"], expected["target"]) != (
        request["id"], request["recorded_at"], request["target"]["target"]
    ):
        raise ValueError("Observed assessment differs from its original command")
    old_ledger, new_ledger = basis["master"]["ledger"], result["master"]["ledger"]
    if new_ledger != {**old_ledger, "commands": old_ledger["commands"] + [command]}:
        raise ValueError("Observed assessment must append exactly its calendar command")
    selected = expected["target"]["cycle"]["id"]
    selected_row = next((row for row in before.cycles if row.context.cycle.id == selected), None)
    if before.reference != timestamp(expected["target"]["market_reference"]) or selected_row is None or (
        payload(selected_row.context.cycle) != expected["target"]["cycle"]
    ) or any(
        a.context != b.context or (a.context.cycle.id != selected and a != b) for a, b in zip(before.cycles, after.cycles)
    ):
        raise ValueError("Observed assessment changed another retained layer")
    require_id(request["id"])
    if basis["parent_id"] is not None:
        require_id(basis["parent_id"])
    recorded = timestamp(request["recorded_at"])
    if recorded < timestamp(binding["bound_at"]):
        raise ValueError("Observed assessment cannot predate launch")
    return RunObservationResult(request["id"], binding["run_id"], recorded, after, _json(value))


def read_run_observed_archive(value):
    if set(value) != {"version", "policy", "run_id", "commands"} or type(value["version"]) is not int or value["version"] != 1 or value["policy"] != POLICY:
        raise ValueError("Unsupported run Observed archive")
    require_id(value["run_id"])
    results, known, parent, binding = [], set(), None, None
    for command in value["commands"]:
        result = _read_command(command)
        basis = command["request"]["basis"]
        if result.id in known or result.run_id != value["run_id"] or basis["parent_id"] != parent or (
            binding is not None and basis["binding"] != binding
        ) or (results and result.recorded_at < results[-1].recorded_at
        ):
            raise ValueError("Observed archive has inconsistent run/parent/identity")
        results.append(result)
        known.add(result.id)
        parent, binding = result.id, basis["binding"]
    return tuple(results)


class AMDXRunObservedRepository:
    def __init__(self, amdx):
        self.amdx, self.connection = amdx, amdx.connection

    def _head(self, run_id):
        row = self.connection.execute("SELECT id FROM amdx_run_observed_command WHERE run_id=? ORDER BY sequence DESC LIMIT 1", (run_id,)).fetchone()
        return row[0] if row else None

    def prepare(self, run_id, *, reference, level, position):
        with self.amdx.review._snapshot():
            binding = self.amdx.run_calendar.get_binding(run_id)
            context = self.amdx.run_calendar._run_context(run_id)
            launch = self.amdx.run_calendar.get_result(binding["launch_operation_id"]).capture.packet
            target = self.amdx.master.prepare_target(binding["instrument"], reference=reference,
                level=level, position=position, channel="Observed")
            _scope(binding, launch, context, payload(target))
            projection = self.amdx.master.load_stack(binding["instrument"], reference=reference, channel="Observed").projection
            basis = dict(binding=binding, run_context=context, launch=launch, parent_id=self._head(run_id),
                master=self.amdx.master.export_archive(binding["instrument"]), projection=payload(projection))
            return PreparedRunObservation(_json(basis), target)

    def revise(self, prepared, *, operation_id, recorded_at, role=None, anchor_id=None,
               source_ref="", subtype=None, note="", clear_applicability=False, capture=None):
        basis = json.loads(prepared.basis_json)
        recorded_at = canonical_timestamp(recorded_at)
        calendar_request = self.amdx.catalog._revision_request(prepared.target.target,
            command_id=operation_id, recorded_at=recorded_at, role=role, anchor_id=anchor_id,
            source_ref=source_ref, subtype=subtype, note=note, clear_applicability=clear_applicability,
            capture=capture or CaptureBasis(kind="HistoricalEntry"))
        request = dict(id=operation_id, recorded_at=recorded_at.isoformat(), basis=basis,
            target=payload(prepared.target), calendar_request=calendar_request)
        with self.amdx._transaction():
            saved = self.connection.execute("SELECT payload_json FROM amdx_run_observed_command WHERE id=?", (operation_id,)).fetchone()
            if saved:
                if json.loads(saved[0])["request"] != request:
                    raise ValueError("Run Observed identity cannot be reused with another request")
                return self.get_result(operation_id)
            self.amdx.run_calendar._reserve(dict(id=operation_id, capture_id=operation_id))
            binding = basis["binding"]
            _scope(binding, basis["launch"], basis["run_context"], request["target"])
            current = self.prepare(binding["run_id"], reference=prepared.target.target.market_reference,
                level=prepared.target.target.cycle.layer,
                position=next(q.position for q in prepared.target.target.cycle.quarters if q.id == prepared.target.target.quarter_id))
            if current != prepared:
                raise StaleAMDXUpdate("Inspected Observed calendar/run basis changed; use Reload AMDX")
            if basis["parent_id"] and recorded_at < self.get_result(basis["parent_id"]).recorded_at:
                raise ValueError("Assessment recording time cannot precede its parent")
            self.amdx.master.validate_target(prepared.target)
            self.amdx.catalog._revise_locked(prepared.target.target, calendar_request)
            master = self.amdx.master.export_archive(binding["instrument"])
            projection = self.amdx.master.load_stack(binding["instrument"],
                reference=prepared.target.target.market_reference, channel="Observed").projection
            result = dict(master=master, projection=payload(projection), calendar_command=master["ledger"]["commands"][-1])
            command = dict(version=1, policy=POLICY, request=request, result=result)
            receipt = _read_command(command)
            self.connection.execute("INSERT INTO amdx_run_observed_command(id,run_id,catalog_id,catalog_command_id,parent_id,payload_json) VALUES (?,?,?,?,?,?)",
                (operation_id, binding["run_id"], binding["catalog_id"], operation_id, basis["parent_id"], receipt.packet_json))
            return receipt

    def get_result(self, operation_id):
        with self.amdx.review._snapshot():
            row = self.connection.execute("SELECT run_id,catalog_id,catalog_command_id,parent_id,payload_json FROM amdx_run_observed_command WHERE id=?", (operation_id,)).fetchone()
            if row is None:
                raise ValueError("Run Observed operation does not exist")
            command = json.loads(row[4])
            result = _read_command(command)
            binding = command["request"]["basis"]["binding"]
            if (result.run_id, binding["catalog_id"], result.id, command["request"]["basis"]["parent_id"]) != row[:4] or result.id != operation_id:
                raise ValueError("Run Observed receipt disagrees with stored scope")
            original = self.connection.execute("SELECT catalog_id,payload_json FROM amdx_catalog_command WHERE id=?", (operation_id,)).fetchone()
            if original != (binding["catalog_id"], _json(command["result"]["calendar_command"])) or self.amdx.run_calendar.get_binding(result.run_id) != binding:
                raise ValueError("Run Observed receipt differs from original calendar command/binding")
            if self.amdx.run_calendar.get_result(binding["launch_operation_id"]).capture.packet != command["request"]["basis"]["launch"]:
                raise ValueError("Run assessment differs from its original launch packet")
            return result

    def export_archive(self, run_id):
        with self.amdx.review._snapshot():
            self.amdx.run_calendar.get_binding(run_id)
            rows = self.connection.execute("SELECT id,payload_json FROM amdx_run_observed_command WHERE run_id=? ORDER BY sequence", (run_id,)).fetchall()
            for id, _ in rows:
                self.get_result(id)
            archive = dict(version=1, policy=POLICY, run_id=run_id, commands=[json.loads(row[1]) for row in rows])
            read_run_observed_archive(archive)
            return archive

    def latest(self, run_id):
        with self.amdx.review._snapshot():
            self.amdx.run_calendar.get_binding(run_id)
            head = self._head(run_id)
            return self.get_result(head) if head else None
