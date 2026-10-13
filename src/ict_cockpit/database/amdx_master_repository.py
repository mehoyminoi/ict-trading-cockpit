"""Canonical instrument owner and consistent shared stack/target reads.

No run capture, implicit legacy adoption, channel merging or native rebinding.
The first binding is immutable; supersession needs a separate versioned action.
"""
from dataclasses import dataclass
from datetime import datetime
import json
from uuid import uuid4

from ict_cockpit.analysis.amdx import canonical_timestamp, payload, require_id, timestamp
from ict_cockpit.analysis.amdx_catalog import Catalog
from ict_cockpit.analysis.amdx_context import StackProjection
from ict_cockpit.analysis.amdx_master import (
    MASTER_BINDING_POLICY, MasterBinding, MasterCalendar, master_owner_payload,
    read_master_owner, require_instrument,
)
from ict_cockpit.database.amdx_catalog_repository import CatalogTarget, read_catalog_archive
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate, _json


class MasterAdoptionRequired(ValueError):
    """Existing instrument collections require a deliberate owner choice."""


@dataclass(frozen=True)
class MasterSnapshot:
    binding: MasterBinding
    projection: StackProjection


@dataclass(frozen=True)
class MasterTarget:
    binding: MasterBinding
    target: CatalogTarget


def _binding_payload(binding, owner):
    return dict(version=1, policy=MASTER_BINDING_POLICY,
                binding=payload(binding), owner=owner)


def _read_binding(value):
    if set(value) != {"version", "policy", "binding", "owner"} or (
        type(value["version"]) is not int or value["version"] != 1 or value["policy"] != MASTER_BINDING_POLICY
    ):
        raise ValueError("Unsupported master binding envelope")
    fields = dict(value["binding"])
    if set(fields) != set(MasterBinding.__dataclass_fields__):
        raise ValueError("Unsupported master binding fields")
    fields["recorded_at"] = timestamp(fields["recorded_at"])
    binding = MasterBinding(**fields)
    owner = (Catalog(**value["owner"]) if set(value["owner"]) == set(Catalog.__dataclass_fields__)
             else read_master_owner(value["owner"]))
    if (owner.id, owner.instrument) != (binding.catalog_id, binding.instrument):
        raise ValueError("Master binding disagrees with owner identity")
    if binding.operation == "Create" and not isinstance(owner, MasterCalendar):
        raise ValueError("New master requires purpose-independent owner metadata")
    return binding, owner


def read_master_archive(value):
    """Validate standalone binding provenance plus the exact original ledger."""
    if set(value) != {"version", "policy", "binding", "ledger"} or (
        type(value["version"]) is not int or value["version"] != 1 or value["policy"] != MASTER_BINDING_POLICY
    ):
        raise ValueError("Unsupported master archive envelope")
    binding, owner = _read_binding(value["binding"])
    archived_owner, history = read_catalog_archive(value["ledger"])
    if owner != archived_owner or value["binding"]["owner"] != value["ledger"]["catalog"]:
        raise ValueError("Master archive ledger differs from bound owner")
    return binding, owner, history


class AMDXMasterRepository:
    def __init__(self, amdx):
        self.amdx = amdx
        self.connection = amdx.connection
        self.catalog = amdx.catalog

    def _from_row(self, row):
        value = json.loads(row[3])
        binding, owner = _read_binding(value)
        if (binding.id, binding.instrument, binding.catalog_id) != tuple(row[:3]):
            raise ValueError("Master binding payload disagrees with stored scope")
        saved_owner = self.connection.execute(
            "SELECT instrument,payload_json FROM amdx_catalog WHERE id=?", (owner.id,)).fetchone()
        if saved_owner is None or saved_owner[0] != binding.instrument or (
            _json(json.loads(saved_owner[1])) != _json(value["owner"])
        ):
            raise ValueError("Master binding owner metadata changed or is unavailable")
        self.catalog.get(owner.id)
        return binding

    def resolve(self, instrument):
        """Read only. Missing binding is distinct from an empty valid stack."""
        require_instrument(instrument)
        with self.amdx.review._snapshot():
            row = self.connection.execute(
                "SELECT id,instrument,catalog_id,payload_json FROM amdx_master_binding WHERE instrument=?",
                (instrument,)).fetchone()
            if row is None:
                raise ValueError("Instrument has no canonical AMDX master; initialize or adopt deliberately")
            return self._from_row(row)

    def _write_locked(self, binding, owner_content):
        encoded = _json(_binding_payload(binding, owner_content))
        # Retry validation precedes current initialization/adoption checks.
        existing = self.connection.execute(
            "SELECT id,instrument,catalog_id,payload_json FROM amdx_master_binding WHERE id=?",
            (binding.id,)).fetchone()
        if existing is not None:
            if existing[3] != encoded:
                raise ValueError("Master operation identity cannot be reused with another request")
            return self._from_row(existing)
        if self.connection.execute(
            "SELECT 1 FROM amdx_master_binding WHERE instrument=? OR catalog_id=?",
            (binding.instrument, binding.catalog_id)).fetchone():
            raise ValueError("Instrument or owner already has a canonical master binding")
        if binding.operation == "Create":
            if self.connection.execute("SELECT 1 FROM amdx_catalog WHERE instrument=?", (binding.instrument,)).fetchone():
                raise MasterAdoptionRequired("Existing instrument collections require deliberate adoption")
            self.connection.execute("INSERT INTO amdx_catalog(id,instrument,payload_json) VALUES (?,?,?)",
                                    (binding.catalog_id, binding.instrument, _json(owner_content)))
        self.connection.execute(
            "INSERT INTO amdx_master_binding(id,instrument,catalog_id,payload_json) VALUES (?,?,?,?)",
            (binding.id, binding.instrument, binding.catalog_id, encoded))
        return binding

    def create(self, owner: MasterCalendar, *, binding_id, recorded_at: datetime, source_ref):
        if not isinstance(owner, MasterCalendar):
            raise ValueError("New master requires purpose-independent owner metadata")
        binding = MasterBinding(binding_id, owner.instrument, owner.id, recorded_at, "Create", source_ref)
        with self.amdx._transaction():
            return self._write_locked(binding, master_owner_payload(owner))

    def ensure(self, instrument, *, recorded_at: datetime):
        """Initialize clean instrument context once; never guess a legacy owner."""
        require_instrument(instrument)
        # Validate timestamp even when an existing binding makes this read-only.
        recorded_at = canonical_timestamp(recorded_at)
        with self.amdx._transaction():
            existing = self.connection.execute(
                "SELECT id,instrument,catalog_id,payload_json FROM amdx_master_binding WHERE instrument=?",
                (instrument,)).fetchone()
            if existing is not None:
                return self._from_row(existing)
            owner = MasterCalendar(str(uuid4()), instrument + " AMDX calendar", instrument)
            binding = MasterBinding(str(uuid4()), instrument, owner.id, recorded_at, "Create",
                                    "Initial instrument context")
            return self._write_locked(binding, master_owner_payload(owner))

    def adopt(self, instrument, catalog_id, *, binding_id, recorded_at: datetime, source_ref):
        """Explicit existing-owner adoption preserves original metadata/commands."""
        require_instrument(instrument)
        require_id(catalog_id)
        with self.amdx._transaction():
            owner = self.catalog.get(catalog_id)
            if owner.instrument != instrument:
                raise ValueError("Cannot adopt a different instrument's ledger")
            original = json.loads(self.connection.execute(
                "SELECT payload_json FROM amdx_catalog WHERE id=?", (catalog_id,)).fetchone()[0])
            binding = MasterBinding(binding_id, instrument, catalog_id, recorded_at, "Adopt", source_ref)
            return self._write_locked(binding, original)

    def load_stack(self, instrument, *, reference, channel="Expected"):
        with self.amdx.review._snapshot():
            binding = self.resolve(instrument)
            projection = self.catalog.load_stack(binding.catalog_id, reference=reference, channel=channel)
            return MasterSnapshot(binding, projection)

    def prepare_target(self, instrument, *, reference, level, position=None, channel="Expected"):
        with self.amdx.review._snapshot():
            binding = self.resolve(instrument)
            target = self.catalog.prepare_target(binding.catalog_id, reference=reference,
                level=level, position=position, channel=channel)
            return MasterTarget(binding, target)

    def validate_target(self, prepared: MasterTarget):
        """Read-only scope/head validation; not a substitute for a write lock."""
        with self.amdx.review._snapshot():
            binding = self.resolve(prepared.binding.instrument)
            if binding != prepared.binding:
                raise StaleAMDXUpdate("Canonical master binding changed; reload before entry")
            owner = self.catalog.get(binding.catalog_id)
            self.catalog._validate_target(prepared.target, owner, canonical=True)
            projection = self.catalog.load_stack(binding.catalog_id,
                reference=prepared.target.market_reference, channel=prepared.target.channel)
            row = next(r for r in projection.cycles if r.context.cycle.id == prepared.target.cycle.id)
            if (row.claim.id if row.claim else None) != prepared.target.expected_head_id:
                raise StaleAMDXUpdate("Master quartet changed; reload before entry")
            return prepared

    def export_archive(self, instrument):
        with self.amdx.review._snapshot():
            binding = self.resolve(instrument)
            encoded = self.connection.execute("SELECT payload_json FROM amdx_master_binding WHERE id=?",
                                              (binding.id,)).fetchone()[0]
            archive = dict(version=1, policy=MASTER_BINDING_POLICY, binding=json.loads(encoded),
                           ledger=self.catalog.export_archive(binding.catalog_id))
            read_master_archive(archive)
            return archive
