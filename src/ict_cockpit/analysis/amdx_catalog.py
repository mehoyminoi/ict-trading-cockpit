"""Independent historical/forward AMDX collections; no trading-run fabrication."""
from dataclasses import dataclass
from datetime import datetime

from ict_cockpit.analysis.amdx import canonical_timestamp, require_id


CATALOG_POLICY = "amdx-catalog-v1"


@dataclass(frozen=True)
class Catalog:
    id: str
    title: str
    instrument: str = "MNQ"
    purpose: str = "Backtest"
    definition_ref: str = ""

    def __post_init__(self):
        for value in (self.id, self.title, self.instrument):
            require_id(value)
        if self.instrument != self.instrument.strip().upper():
            raise ValueError("Use an explicit normalized instrument identity")
        if self.purpose not in ("Backtest", "ForwardTest"):
            raise ValueError("Catalog purpose must be Backtest or ForwardTest")
        if not isinstance(self.definition_ref, str):
            raise ValueError("Definition reference must be text; empty means unspecified")

    @property
    def owner_id(self):
        # The shared pure engine retains its original run_id field name.
        # Catalog claims use a tagged owner, never a saved trading run.
        return "catalog:" + self.id


@dataclass(frozen=True)
class CaptureBasis:
    kind: str = "HistoricalEntry"
    information_available_at: datetime | None = None
    evidence_ref: str = ""
    definition_ref: str = ""

    def __post_init__(self):
        if self.kind not in ("HistoricalEntry", "ForwardEntry"):
            raise ValueError("Capture kind must be HistoricalEntry or ForwardEntry")
        if self.information_available_at is not None:
            object.__setattr__(self, "information_available_at",
                               canonical_timestamp(self.information_available_at))
        if any(not isinstance(v, str) for v in (self.evidence_ref, self.definition_ref)):
            raise ValueError("Evidence and definition references must be text")

    def validate_recording(self, recorded_at):
        if self.information_available_at is not None and self.information_available_at > canonical_timestamp(recorded_at):
            raise ValueError("Declared information availability cannot follow recording time")

    # A declared ForwardEntry is provenance, not proof of absence of look-ahead.
    # Empty evidence/as-of/definition references remain explicitly unspecified.
