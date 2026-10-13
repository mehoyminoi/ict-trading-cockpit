"""Versioned master ownership; purpose and run captures are separate concepts."""
from dataclasses import dataclass
from datetime import datetime

from ict_cockpit.analysis.amdx import canonical_timestamp, payload, require_id


MASTER_OWNER_POLICY = "amdx-master-owner-v1"
MASTER_BINDING_POLICY = "amdx-master-binding-v1"


def require_instrument(value):
    require_id(value)
    if value != value.strip().upper():
        raise ValueError("Use an explicit normalized instrument identity")


@dataclass(frozen=True)
class MasterCalendar:
    id: str
    title: str
    instrument: str
    definition_ref: str = ""

    def __post_init__(self):
        require_id(self.id)
        require_id(self.title)
        require_instrument(self.instrument)
        if not isinstance(self.definition_ref, str):
            raise ValueError("Definition reference must be text")

    @property
    def owner_id(self):
        return "catalog:" + self.id


def master_owner_payload(owner):
    return dict(version=1, policy=MASTER_OWNER_POLICY, owner=payload(owner))


def read_master_owner(value):
    if set(value) != {"version", "policy", "owner"} or (
        type(value["version"]) is not int or value["version"] != 1 or value["policy"] != MASTER_OWNER_POLICY
    ):
        raise ValueError("Unsupported master owner envelope")
    if set(value["owner"]) != set(MasterCalendar.__dataclass_fields__):
        raise ValueError("Unsupported master owner fields")
    return MasterCalendar(**value["owner"])


@dataclass(frozen=True)
class MasterBinding:
    id: str
    instrument: str
    catalog_id: str
    recorded_at: datetime
    operation: str
    source_ref: str

    def __post_init__(self):
        for value in (self.id, self.catalog_id, self.source_ref):
            require_id(value)
        require_instrument(self.instrument)
        object.__setattr__(self, "recorded_at", canonical_timestamp(self.recorded_at))
        if self.operation not in ("Create", "Adopt"):
            raise ValueError("Unsupported master binding operation")
