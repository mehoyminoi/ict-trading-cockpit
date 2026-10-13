"""Owned run launch/context/working-edit transactions with frozen AMDX basis.

Native consumers and retrospective legacy assignment remain separate slices.
Archives reconstruct retained temporal content without today's resolver.
"""
from dataclasses import dataclass
from datetime import datetime
import json

from ict_cockpit.analysis.amdx import (
    canonical_timestamp, cycle_from_payload, infer_profile, payload, require_id, timestamp,
)
from ict_cockpit.analysis.amdx_catalog import CaptureBasis
from ict_cockpit.analysis.amdx_context import (
    CycleContext, HIGHER_LEVELS, PositionState, ProjectedCycle, StackProjection, TEMPORAL_REVISION,
)
from ict_cockpit.database.amdx_catalog_repository import read_catalog_archive
from ict_cockpit.database.amdx_master_repository import MasterSnapshot, MasterTarget, read_master_archive
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate, WorkingRevisionResult, _json


RUN_CALENDAR_POLICY = "amdx-run-calendar-v1"


@dataclass(frozen=True)
class PreparedCalendarLaunch:
    run_values: tuple
    snapshot: MasterSnapshot


@dataclass(frozen=True)
class PreparedRunCapture:
    run_id: str
    binding_json: str
    run_context_json: str
    parent_capture_id: str
    snapshot: MasterSnapshot


@dataclass(frozen=True)
class CapturedRunContext:
    id: str
    run_id: str
    operation_id: str
    recorded_at: datetime
    reason: str
    projection: StackProjection
    packet_json: str

    @property
    def packet(self):
        return json.loads(self.packet_json)


@dataclass(frozen=True)
class RunCalendarResult:
    capture: CapturedRunContext
    calendar_result: WorkingRevisionResult | None = None


def _envelope(value, fields, versions=(1,)):
    if set(value) != set(fields) | {"version", "policy"} or (
        type(value["version"]) is not int or value["version"] not in versions or value["policy"] != RUN_CALENDAR_POLICY
    ):
        raise ValueError("Unsupported run calendar envelope")


def _read_run_binding(value):
    _envelope(value, {"run_id", "instrument", "master_binding_id", "catalog_id",
                      "launch_operation_id", "bound_at", "run_basis"})
    from ict_cockpit.analysis.amdx_master import require_instrument
    for key in ("run_id", "master_binding_id", "catalog_id", "launch_operation_id"):
        require_id(value[key])
    require_instrument(value["instrument"])
    timestamp(value["bound_at"])
    from ict_cockpit.database.trading_session_run_repository import RUN_COLUMNS
    if set(value["run_basis"]) != set(RUN_COLUMNS) or value["run_basis"]["id"] != value["run_id"]:
        raise ValueError("Run binding has inconsistent original run basis")
    if value["run_basis"]["status"] != "Active" or value["run_basis"]["concluded_at"]:
        raise ValueError("Run binding requires an original active launch")
    from ict_cockpit.analysis.trading_session_run import RunEnvironment, RunPurpose
    RunEnvironment(value["run_basis"]["run_environment"])
    RunPurpose(value["run_basis"]["run_purpose"])
    for key, content in value["run_basis"].items():
        if key.endswith("_json"):
            json.loads(content)
    timestamp(value["run_basis"]["started_at"])
    return value


def _validate_launch_reference(binding, reference):
    original = json.loads(binding["run_basis"]["market_context_snapshot_json"])
    if not isinstance(original, dict):
        raise ValueError("Saved run-start context must be an object")
    saved = original.get("reference_market_time")
    if saved is not None and saved != "":
        if not isinstance(saved, str) or canonical_timestamp(timestamp(saved)) != canonical_timestamp(reference):
            raise ValueError("Launch calendar reference differs from saved run-start context")


def _read_projection(value, master_archive, *, channel="Expected"):
    if set(value) != set(StackProjection.__dataclass_fields__):
        raise ValueError("Unsupported captured projection fields")
    master, owner, history = read_master_archive(master_archive)
    if channel not in ("Expected", "Observed") or (value["run_id"], value["channel"], value["branch_id"]) != (owner.owner_id, channel, "working"):
        raise ValueError("Run capture requires the maintained working interpretation")
    reference = timestamp(value["reference"])
    if type(value["market_open"]) is not bool or value["legacy_values"] != []:
        raise ValueError("Unsupported captured market/legacy state")
    levels = HIGHER_LEVELS + (("day", "session") if value["market_open"] else ())
    if tuple(r["context"]["cycle"]["layer"] for r in value["cycles"]) != levels:
        raise ValueError("Captured stack does not retain all identified layers")
    rows = []
    for item in value["cycles"]:
        if set(item) != {"context", "claim", "inference"}:
            raise ValueError("Unsupported captured row fields")
        fields = dict(item["context"])
        if set(fields) != set(CycleContext.__dataclass_fields__):
            raise ValueError("Unsupported captured cycle context")
        fields["cycle"] = cycle_from_payload(fields["cycle"])
        fields["state"] = PositionState(fields["state"])
        context = CycleContext(**fields)
        expected_revision = TEMPORAL_REVISION if context.cycle.layer in HIGHER_LEVELS else ""
        if context.temporal_revision != expected_revision:
            raise ValueError("Unsupported retained temporal revision")
        if context.state == PositionState.ACTIVE:
            active = context.cycle.quarter_at(reference)
            if active is None or context.position != f"Q{active.position}":
                raise ValueError("Captured active position disagrees with retained boundaries")
        elif context.state == PositionState.DISTORTION:
            if (context.cycle.layer, context.position) not in (("month", "Distortion"), ("week", "")):
                raise ValueError("Unsupported retained distortion position")
        elif (context.cycle.layer, context.position) != (
            "week" if context.state == PositionState.CLOSED else "month", ""
        ):
            raise ValueError("Unsupported retained inactive position")
        head = next((c for c in reversed(history.claims) if
                     (c.cycle.id, c.channel, c.branch_id) == (context.cycle.id, channel, "working")), None)
        if head is not None and head.cycle != context.cycle:
            raise ValueError("Captured cycle differs from its original claim")
        if item["claim"] != payload(head):
            raise ValueError("Captured head/absence disagrees with its retained ledger")
        inference = infer_profile(context.cycle, head.anchors + head.applicability if head else ())
        if item["inference"] != payload(inference):
            raise ValueError("Captured inference differs from retained anchors")
        rows.append(ProjectedCycle(context, head, inference))
    return master, StackProjection(owner.owner_id, channel, "working", reference,
                                   value["market_open"], tuple(rows), ())


def _read_packet(value):
    _envelope(value, {"id", "run_id", "operation_id", "recorded_at", "reason", "binding",
                      "run_context", "master", "projection", "unavailable_levels"})
    binding = _read_run_binding(value["binding"])
    master, projection = _read_projection(value["projection"], value["master"])
    if (value["run_id"], master.id, master.instrument, master.catalog_id) != (
        binding["run_id"], binding["master_binding_id"], binding["instrument"], binding["catalog_id"]
    ):
        raise ValueError("Captured run/master ownership disagrees")
    for key in ("id", "operation_id"):
        require_id(value[key])
    recorded = timestamp(value["recorded_at"])
    if recorded < timestamp(binding["bound_at"]):
        raise ValueError("Capture cannot predate its original launch binding")
    if value["reason"] not in ("Launch", "ContextUse", "CycleChange", "WorkingEdit"):
        raise ValueError("Unsupported run capture reason")
    original = binding["run_basis"]
    context = value["run_context"]
    if set(context) != set(original) or any(context[k] != original[k] for k in
        ("id", "trading_day_id", "process_session_id", "run_environment", "run_purpose")):
        raise ValueError("Capture has inconsistent run identity/environment")
    unavailable = [] if projection.market_open else [dict(level=level, reason="Closed") for level in ("day", "session")]
    if value["unavailable_levels"] != unavailable:
        raise ValueError("Captured unavailable layers disagree with market state")
    return CapturedRunContext(value["id"], value["run_id"], value["operation_id"], recorded,
                              value["reason"], projection, _json(value))


def _read_operation(command):
    _envelope(command, {"request", "result"}, versions=(1, 2))
    request = command["request"]
    fields = {"id", "capture_id", "run_id", "operation", "recorded_at", "reason",
              "parent_capture_id", "binding", "run_context", "snapshot", "master_target", "calendar_request"}
    if command["version"] == 2:
        fields.add("updated_run_context")
        if request.get("operation") != "Capture":
            raise ValueError("Run consumption requires a context-use operation")
    if set(request) != fields:
        raise ValueError("Unsupported run calendar request fields")
    original = request["binding"]["run_basis"]
    if set(request["run_context"]) != set(original) or any(
        request["run_context"][key] != original[key] for key in
        ("id", "trading_day_id", "process_session_id", "run_environment", "run_purpose")
    ):
        raise ValueError("Inspected run context has inconsistent ownership")
    if set(command["result"]) != {"capture"}:
        raise ValueError("Unsupported run calendar result fields")
    packet = command["result"]["capture"]
    capture = _read_packet(packet)
    if (capture.operation_id, capture.id, capture.run_id, packet["recorded_at"], capture.reason,
        packet["binding"], packet["run_context"]) != (
        request["id"], request["capture_id"], request["run_id"], request["recorded_at"], request["reason"],
        request["binding"], request.get("updated_run_context", request["run_context"])
    ):
        raise ValueError("Run calendar result differs from original request")
    if set(request["snapshot"]) != set(MasterSnapshot.__dataclass_fields__):
        raise ValueError("Unsupported inspected master snapshot")
    if request["snapshot"]["binding"] != packet["master"]["binding"]["binding"]:
        raise ValueError("Inspected master binding differs from captured basis")
    ledger = packet["master"]["ledger"]
    calendar_result = None
    if request["operation"] == "WorkingEdit":
        if capture.reason != "WorkingEdit" or not ledger["commands"]:
            raise ValueError("Working edit lacks its original command")
        final = ledger["commands"][-1]
        target = request["master_target"]
        if not isinstance(target, dict) or set(target) != set(MasterTarget.__dataclass_fields__) or (
            target["binding"] != request["snapshot"]["binding"] or
            target["target"] != request["calendar_request"]["target"] or
            target["target"]["channel"] != "Expected" or
            final["request"] != request["calendar_request"] or final["request"]["id"] != request["id"] or
            final["request"]["recorded_at"] != request["recorded_at"] or
            target["target"]["market_reference"] != request["snapshot"]["projection"]["reference"]
        ):
            raise ValueError("Working edit differs from its retained target/command")
        before = json.loads(_json(packet["master"]))
        before["ledger"]["commands"].pop()
        _, inspected = _read_projection(request["snapshot"]["projection"], before)
        old_rows, new_rows = inspected.cycles, capture.projection.cycles
        old_outer, new_outer = payload(inspected), payload(capture.projection)
        old_outer.pop("cycles")
        new_outer.pop("cycles")
        selected = next((r for r in old_rows if r.context.cycle.id == target["target"]["cycle"]["id"]), None)
        if selected is None or payload(selected.context.cycle) != target["target"]["cycle"] or (
            old_outer != new_outer or any(a.context != b.context or (
                a.context.cycle.id != selected.context.cycle.id and a != b
            ) for a, b in zip(old_rows, new_rows))
        ):
            raise ValueError("Working edit changed another retained scope or position")
        _, history = read_catalog_archive(ledger)
        result = final["result"]
        claim = next((c for c in history.claims if result["claim"] and c.id == result["claim"]["id"]), None)
        calendar_result = WorkingRevisionResult(claim, result["changed"])
    elif request["operation"] in ("Launch", "Capture"):
        if request["calendar_request"] is not None or request["master_target"] is not None:
            raise ValueError("Context capture cannot carry a phase write")
        if request["snapshot"]["projection"] != packet["projection"]:
            raise ValueError("Context capture silently substituted another projection")
        if request["operation"] == "Launch":
            _validate_launch_reference(request["binding"], capture.projection.reference)
            if request["reason"] != "Launch" or request["parent_capture_id"] is not None or (
                request["binding"]["launch_operation_id"] != request["id"] or
                request["binding"]["bound_at"] != request["recorded_at"] or
                request["binding"]["run_basis"] != request["run_context"]
            ):
                raise ValueError("Launch capture has inconsistent original basis")
        elif request["reason"] not in ("ContextUse", "CycleChange"):
            raise ValueError("Unsupported operational capture reason")
    else:
        raise ValueError("Unsupported run calendar operation")
    return RunCalendarResult(capture, calendar_result)


def read_run_calendar_archive(value):
    """Validate complete capture chain and reconstruct without a database/resolver."""
    _envelope(value, {"binding", "commands"})
    binding = _read_run_binding(value["binding"])
    results, identities, previous = [], set(), None
    for index, command in enumerate(value["commands"]):
        result = _read_operation(command)
        request = command["request"]
        if request["binding"] != binding or request["parent_capture_id"] != previous or (
            (request["operation"] == "Launch") != (index == 0)
        ):
            raise ValueError("Run capture chain has inconsistent binding/parent")
        for identity in (request["id"], result.capture.id):
            if identity in identities:
                raise ValueError("Run calendar operation/capture identity is repeated")
            identities.add(identity)
        results.append(result)
        previous = result.capture.id
    if not results:
        raise ValueError("Run archive has no original launch capture")
    return binding, tuple(results)


class AMDXRunCalendarRepository:
    def __init__(self, amdx):
        self.amdx = amdx
        self.connection = amdx.connection

    def _run_context(self, run_id):
        from ict_cockpit.database.trading_session_run_repository import RUN_COLUMNS, TradingSessionRunRepository
        row = self.connection.execute(TradingSessionRunRepository._select_sql("WHERE id=?"), (run_id,)).fetchone()
        if row is None:
            raise ValueError("Run does not exist")
        return dict(zip(RUN_COLUMNS, row))

    def get_binding(self, run_id):
        require_id(run_id)
        row = self.connection.execute("SELECT instrument,master_binding_id,catalog_id,launch_operation_id,payload_json FROM amdx_run_binding WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            raise ValueError("Run has no immutable calendar launch binding; legacy ownership is unknown")
        binding = _read_run_binding(json.loads(row[4]))
        if (binding["run_id"], binding["instrument"], binding["master_binding_id"], binding["catalog_id"], binding["launch_operation_id"]) != (run_id, *row[:4]):
            raise ValueError("Run binding disagrees with stored scope")
        return binding

    def _head(self, run_id):
        row = self.connection.execute("SELECT id FROM amdx_run_capture WHERE run_id=? ORDER BY sequence DESC LIMIT 1", (run_id,)).fetchone()
        return row[0] if row else None

    def prepare_launch(self, run, *, instrument, reference, snapshot=None):
        from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
        with self.amdx.review._snapshot():
            if self.connection.execute("SELECT 1 FROM trading_session_run WHERE id=?", (run.id,)).fetchone():
                raise ValueError("Calendar launch requires a new unsaved run")
            view = snapshot or self.amdx.master.load_stack(instrument, reference=reference)
            if view.binding.instrument != instrument or canonical_timestamp(view.projection.reference) != canonical_timestamp(reference):
                raise ValueError("Prepared launch has different instrument/reference")
            return PreparedCalendarLaunch(TradingSessionRunRepository(self.connection)._values_for_run(run), view)

    def prepare_capture(self, run_id, *, reference):
        with self.amdx.review._snapshot():
            binding = self.get_binding(run_id)
            context = self._run_context(run_id)
            snapshot = self.amdx.master.load_stack(binding["instrument"], reference=reference)
            parent = self._head(run_id)
            if parent is None:
                raise ValueError("Bound run has no original capture")
            return PreparedRunCapture(run_id, _json(binding), _json(context), parent, snapshot)

    def _request(self, prepared, *, operation_id, capture_id, recorded_at, operation, reason,
                 master_target=None, calendar_request=None):
        require_id(operation_id)
        require_id(capture_id)
        if operation_id == capture_id:
            raise ValueError("Operation and capture require distinct identities")
        recorded_at = canonical_timestamp(recorded_at)
        if operation == "Launch":
            from ict_cockpit.database.trading_session_run_repository import RUN_COLUMNS
            context = dict(zip(RUN_COLUMNS, prepared.run_values))
            master = prepared.snapshot.binding
            binding = dict(version=1, policy=RUN_CALENDAR_POLICY, run_id=context["id"], instrument=master.instrument,
                master_binding_id=master.id, catalog_id=master.catalog_id, launch_operation_id=operation_id,
                bound_at=recorded_at.isoformat(), run_basis=context)
            _read_run_binding(binding)
            _validate_launch_reference(binding, prepared.snapshot.projection.reference)
            parent = None
        else:
            binding, context = json.loads(prepared.binding_json), json.loads(prepared.run_context_json)
            if prepared.run_id != binding["run_id"]:
                raise ValueError("Prepared capture has different run ownership")
            parent = prepared.parent_capture_id
        return dict(id=operation_id, capture_id=capture_id, run_id=binding["run_id"], operation=operation,
            recorded_at=recorded_at.isoformat(), reason=reason, parent_capture_id=parent,
            binding=binding, run_context=context, snapshot=payload(prepared.snapshot),
            master_target=payload(master_target), calendar_request=calendar_request)

    def _stored_result(self, row):
        command = json.loads(row[6])
        result = _read_operation(command)
        request = command["request"]
        if (request["id"], request["run_id"], request["operation"], request["capture_id"], request["parent_capture_id"],
            request["id"] if request["operation"] == "WorkingEdit" else None) != tuple(row[:6]):
            raise ValueError("Run calendar receipt disagrees with stored scope")
        capture = self.connection.execute("SELECT operation_id,payload_json FROM amdx_run_capture WHERE id=? AND run_id=?", (result.capture.id, result.capture.run_id)).fetchone()
        if capture is None or capture[0] != request["id"] or capture[1] != result.capture.packet_json or (
            self.get_binding(request["run_id"]) != request["binding"]
        ):
            raise ValueError("Run calendar receipt differs from immutable capture/binding")
        if request["operation"] == "WorkingEdit":
            original = result.capture.packet["master"]["ledger"]["commands"][-1]
            saved = self.connection.execute("SELECT catalog_id,payload_json FROM amdx_catalog_command WHERE id=?", (request["id"],)).fetchone()
            if saved is None or saved[0] != request["binding"]["catalog_id"] or saved[1] != _json(original):
                raise ValueError("Run calendar receipt differs from original calendar command")
        return result

    def _existing(self, request):
        row = self.connection.execute("SELECT id,run_id,operation,capture_id,parent_capture_id,catalog_command_id,payload_json FROM amdx_run_calendar_command WHERE id=?", (request["id"],)).fetchone()
        if row is None:
            return None
        if _json(json.loads(row[6])["request"]) != _json(request):
            raise ValueError("Run calendar operation identity cannot be reused with another request")
        return self._stored_result(row)

    def _reserve(self, request):
        for identity in (request["id"], request["capture_id"]):
            for table, column in (("amdx_run_observed_command", "id"), ("amdx_run_calendar_command", "id"), ("amdx_run_capture", "id"),
                ("amdx_catalog_command", "id"), ("amdx_master_binding", "id"), ("amdx_claim", "id"),
                ("amdx_working_command", "id"), ("amdx_observed_command", "id"), ("amdx_observed_command", "comparison_id"),
                ("amdx_review_command", "id"), ("amdx_comparison", "id")):
                if self.connection.execute(f"SELECT 1 FROM {table} WHERE {column}=?", (identity,)).fetchone():
                    raise ValueError("Run operation/capture identity is already reserved")

    def _validate_current(self, request, snapshot):
        current = self.amdx.master.load_stack(snapshot.binding.instrument, reference=snapshot.projection.reference)
        if _json(payload(current)) != _json(request["snapshot"]):
            raise StaleAMDXUpdate("Inspected master stack/binding changed; reload before capture")
        if snapshot.projection.channel != "Expected" or snapshot.projection.branch_id != "working":
            raise ValueError("Run capture requires working Expected context")
        binding = request["binding"]
        if (binding["instrument"], binding["master_binding_id"], binding["catalog_id"]) != (
            snapshot.binding.instrument, snapshot.binding.id, snapshot.binding.catalog_id
        ):
            raise ValueError("Run and master snapshot ownership differ")
        if request["operation"] != "Launch":
            if self.get_binding(request["run_id"]) != binding or self._run_context(request["run_id"]) != request["run_context"] or self._head(request["run_id"]) != request["parent_capture_id"]:
                raise StaleAMDXUpdate("Run/capture basis changed; reload before capture")
            if request["run_context"]["status"] != "Active":
                raise ValueError("Concluded runs cannot consume new working context")

    def _store_capture(self, request):
        view = self.amdx.master.load_stack(request["binding"]["instrument"], reference=timestamp(request["snapshot"]["projection"]["reference"]))
        packet = dict(version=1, policy=RUN_CALENDAR_POLICY, id=request["capture_id"], run_id=request["run_id"],
            operation_id=request["id"], recorded_at=request["recorded_at"], reason=request["reason"], binding=request["binding"],
            run_context=request.get("updated_run_context", request["run_context"]), master=self.amdx.master.export_archive(request["binding"]["instrument"]),
            projection=payload(view.projection), unavailable_levels=[] if view.projection.market_open else
            [dict(level=level, reason="Closed") for level in ("day", "session")])
        command = dict(version=2 if "updated_run_context" in request else 1,
                       policy=RUN_CALENDAR_POLICY, request=request, result=dict(capture=packet))
        result = _read_operation(command)
        self.connection.execute("INSERT INTO amdx_run_capture(id,run_id,operation_id,payload_json) VALUES (?,?,?,?)",
            (request["capture_id"], request["run_id"], request["id"], _json(packet)))
        self.connection.execute("INSERT INTO amdx_run_calendar_command(id,run_id,operation,capture_id,parent_capture_id,catalog_command_id,payload_json) VALUES (?,?,?,?,?,?,?)",
            (request["id"], request["run_id"], request["operation"], request["capture_id"], request["parent_capture_id"],
             request["id"] if request["operation"] == "WorkingEdit" else None, _json(command)))
        return result

    def launch(self, prepared: PreparedCalendarLaunch, *, operation_id, capture_id, recorded_at):
        request = self._request(prepared, operation_id=operation_id, capture_id=capture_id,
                                recorded_at=recorded_at, operation="Launch", reason="Launch")
        with self.amdx._transaction():
            existing = self._existing(request)
            if existing is not None:
                return existing
            self._reserve(request)
            self._validate_current(request, prepared.snapshot)
            if self.connection.execute("SELECT 1 FROM trading_session_run WHERE id=?", (request["run_id"],)).fetchone():
                raise ValueError("Calendar launch requires a new unsaved run")
            from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
            TradingSessionRunRepository(self.connection)._save_values_locked(prepared.run_values)
            binding = request["binding"]
            self.connection.execute("INSERT INTO amdx_run_binding VALUES (?,?,?,?,?,?)", (
                binding["run_id"], binding["instrument"], binding["master_binding_id"], binding["catalog_id"],
                operation_id, _json(binding)))
            return self._store_capture(request)

    def capture(self, prepared: PreparedRunCapture, *, operation_id, capture_id, recorded_at, reason="ContextUse"):
        if reason not in ("ContextUse", "CycleChange"):
            raise ValueError("Capture requires an explicit operational reason")
        request = self._request(prepared, operation_id=operation_id, capture_id=capture_id,
                                recorded_at=recorded_at, operation="Capture", reason=reason)
        with self.amdx._transaction():
            existing = self._existing(request)
            if existing is not None:
                return existing
            self._reserve(request)
            self._validate_current(request, prepared.snapshot)
            return self._store_capture(request)

    def revise(self, prepared: PreparedRunCapture, target: MasterTarget, *, operation_id, capture_id,
               recorded_at, role=None, anchor_id=None, source_ref="", subtype=None, note="",
               capture=None, clear_applicability=False):
        if capture is None:
            environment = json.loads(prepared.run_context_json)["run_environment"]
            capture = CaptureBasis(kind="HistoricalEntry" if environment in ("Historical Backtest", "Replay") else "ForwardEntry")
        calendar_request = self.amdx.catalog._revision_request(target.target, command_id=operation_id,
            recorded_at=recorded_at, role=role, anchor_id=anchor_id, source_ref=source_ref, subtype=subtype,
            note=note, capture=capture, clear_applicability=clear_applicability)
        request = self._request(prepared, operation_id=operation_id, capture_id=capture_id, recorded_at=recorded_at,
            operation="WorkingEdit", reason="WorkingEdit", master_target=target, calendar_request=calendar_request)
        with self.amdx._transaction():
            existing = self._existing(request)
            if existing is not None:
                return existing
            self._reserve(request)
            self._validate_current(request, prepared.snapshot)
            if payload(target.binding) != request["snapshot"]["binding"] or target.target.channel != "Expected" or canonical_timestamp(target.target.market_reference) != canonical_timestamp(prepared.snapshot.projection.reference):
                raise ValueError("Working edit target has different binding/channel/reference")
            self.amdx.master.validate_target(target)
            self.amdx.catalog._revise_locked(target.target, calendar_request)
            return self._store_capture(request)

    def consume(self, prepared: PreparedRunCapture, updated_run, *, operation_id, capture_id, recorded_at):
        """Commit a run data action and the exact working basis it consumed together."""
        from ict_cockpit.database.trading_session_run_repository import RUN_COLUMNS, TradingSessionRunRepository
        writer = TradingSessionRunRepository(self.connection)
        values = writer._values_for_run(updated_run)
        request = self._request(prepared, operation_id=operation_id, capture_id=capture_id,
                                recorded_at=recorded_at, operation="Capture", reason="ContextUse")
        request["updated_run_context"] = dict(zip(RUN_COLUMNS, values))
        if request["updated_run_context"]["id"] != prepared.run_id:
            raise ValueError("Run consumption has different run ownership")
        with self.amdx._transaction():
            existing = self._existing(request)
            if existing is not None:
                return existing
            self._reserve(request)
            self._validate_current(request, prepared.snapshot)
            writer._save_values_locked(values)
            return self._store_capture(request)

    def get_result(self, operation_id):
        with self.amdx.review._snapshot():
            row = self.connection.execute("SELECT id,run_id,operation,capture_id,parent_capture_id,catalog_command_id,payload_json FROM amdx_run_calendar_command WHERE id=?", (operation_id,)).fetchone()
            if row is None:
                raise ValueError("Run calendar operation does not exist")
            return self._stored_result(row)

    def export_archive(self, run_id):
        with self.amdx.review._snapshot():
            binding = self.get_binding(run_id)
            rows = self.connection.execute("SELECT o.id,o.run_id,o.operation,o.capture_id,o.parent_capture_id,o.catalog_command_id,o.payload_json FROM amdx_run_calendar_command o JOIN amdx_run_capture c ON c.id=o.capture_id WHERE o.run_id=? ORDER BY c.sequence", (run_id,)).fetchall()
            for row in rows:
                self._stored_result(row)
            if len(rows) != self.connection.execute("SELECT COUNT(*) FROM amdx_run_capture WHERE run_id=?", (run_id,)).fetchone()[0]:
                raise ValueError("Run archive has incomplete capture/receipt coverage")
            archive = dict(version=1, policy=RUN_CALENDAR_POLICY, binding=binding,
                           commands=[json.loads(r[6]) for r in rows])
            read_run_calendar_archive(archive)
            return archive
