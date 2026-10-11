"""Offline import of the supported weekly JSON export; no network or policy."""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
import json
from uuid import uuid4

from ict_cockpit.analysis.context_source import ContextCoverage, ContextSourceProvenance
from ict_cockpit.analysis.market_context_event import (
    MarketContextEvent, MarketContextEventCategory, MarketContextEventStatus,
    MarketContextImpact, MarketContextTimingPrecision, MarketContextQueryResult,
    MarketContextQueryUnavailable,
    parse_event_datetime,
)


PROVIDER = "Forex Factory weekly export"
ADAPTER_REVISION = "forex-factory-json-v0"
MAPPING_REVISION = "forex-factory-native-impact-v0"
IMPACTS = {"Low": MarketContextImpact.LOW, "Medium": MarketContextImpact.MEDIUM,
           "High": MarketContextImpact.HIGH}
LIMITATIONS = (
    "Export clock values do not certify exact timing; All Day precision may be lost.",
    "Lifecycle status and normalized event type are not supplied.",
    "Country values are native currency labels, not verified affected-market mappings.",
    "Occurrence IDs are capture-local; rescheduling continuity is not established.",
    "Declared week is operator supplied; source completeness is unverified.",
    "Bank holidays do not establish futures exchange closures or early closes.",
    "Import time does not prove what was known at an earlier Replay timestamp.",
)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")


@dataclass(frozen=True)
class ImportedContextCapture:
    provenance: ContextSourceProvenance
    events: tuple[MarketContextEvent, ...]
    raw_payload: str

    @property
    def id(self):
        return self.provenance.capture_id

    def to_dict(self):
        return {"provenance": self.provenance.to_dict(),
                "events": [x.to_dict() for x in self.events], "raw_payload": self.raw_payload}

    @classmethod
    def from_dict(cls, value):
        return cls(ContextSourceProvenance.from_dict(value["provenance"]),
                   tuple(MarketContextEvent.from_dict(x) for x in value["events"]),
                   value["raw_payload"])


def import_forex_factory_json(raw: bytes, *, week_start: str, imported_at: str,
                             source_reference: str) -> ImportedContextCapture:
    """Validate the entire file before producing a capture. Never skip bad rows.

    The declared week uses UTC, the basis of the inspected JSON export. Each
    record still retains its original explicit offset. Bounds are a source-file
    selection boundary, not certified coverage or a historical knowledge claim.
    """
    first = date.fromisoformat(week_start)
    if first.weekday() != 6:
        raise ValueError("Select the Sunday starting the exported week (UTC)")
    imported = parse_event_datetime(imported_at)
    if imported.utcoffset() is None:
        raise ValueError("Import timestamp must include an offset")
    if not source_reference.strip():
        raise ValueError("Source file reference is required")
    try:
        text = raw.decode("utf-8-sig")
        rows = json.loads(text, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
    except (UnicodeError, ValueError) as exc:
        raise ValueError("Not a valid UTF-8 Forex Factory JSON export") from exc
    if not isinstance(rows, list) or not rows:
        raise ValueError("Expected a non-empty weekly event array; an empty file cannot verify its week")
    start = datetime.combine(first, time(), timezone.utc)
    end = start + timedelta(days=7) - timedelta(microseconds=1)
    capture_id = str(uuid4())
    events = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"Record {index + 1}: expected an event object")
        required = ("title", "country", "date", "impact", "forecast", "previous")
        if any(key not in row or not isinstance(row[key], str) for key in required):
            raise ValueError(f"Record {index + 1}: missing or non-text export fields")
        if not row["title"].strip():
            raise ValueError(f"Record {index + 1}: title is empty")
        try:
            stamp = parse_event_datetime(row["date"])
        except ValueError as exc:
            raise ValueError(f"Record {index + 1}: invalid date") from exc
        if stamp.utcoffset() is None:
            raise ValueError(f"Record {index + 1}: date has no offset")
        if not start <= stamp <= end:
            raise ValueError(f"Record {index + 1}: date is outside the declared UTC export week")
        holiday = row["impact"] == "Holiday"
        events.append(MarketContextEvent(
            id=f"{capture_id}:{index + 1}", provider=PROVIDER, source_event_id="",
            category=(MarketContextEventCategory.HOLIDAY if holiday else
                      MarketContextEventCategory.ECONOMIC if row["impact"] in IMPACTS else
                      MarketContextEventCategory.OTHER_CONTEXT),
            normalized_event_type="", title=row["title"], scheduled_at=row["date"],
            source_timezone="Explicit offset in JSON date",
            impact=IMPACTS.get(row["impact"], MarketContextImpact.UNKNOWN),
            provider_native_impact=row["impact"], affected_markets=(),
            status=MarketContextEventStatus.UNKNOWN, forecast=row["forecast"], previous=row["previous"],
            captured_at=imported_at, provenance_reference=source_reference,
            timing_precision=MarketContextTimingPrecision.UNKNOWN,
            identity_basis="Capture-local row ID; no provider occurrence ID",
            native_record=json.dumps(row, ensure_ascii=False, sort_keys=True),
        ))
    provenance = ContextSourceProvenance(
        capture_id=capture_id, content_sha256=sha256(raw).hexdigest(),
        source_reference=source_reference, imported_at=imported_at,
        declared_start=start.isoformat(), declared_end=end.isoformat(),
        timezone_basis="Week declared in UTC; event dates retain supplied offsets",
        adapter_revision=ADAPTER_REVISION, mapping_revision=MAPPING_REVISION,
        knowledge_basis="Imported export; retrieval time and historical as-of knowledge unverified",
        limitations=LIMITATIONS,
    )
    return ImportedContextCapture(provenance, tuple(events), raw.decode("utf-8"))


class ImportedCaptureProvider:
    """An explicitly selected immutable capture, never an automatic latest feed."""
    provider_name = PROVIDER

    def __init__(self, capture: ImportedContextCapture):
        self.capture = capture

    def query_context(self, start, end):
        p = self.capture.provenance
        if start.utcoffset() is None or end.utcoffset() is None or end < start:
            raise ValueError("Query requires ordered aware bounds")
        if start < parse_event_datetime(p.declared_start) or end > parse_event_datetime(p.declared_end):
            raise MarketContextQueryUnavailable("Selected capture does not contain the complete requested futures day", p)
        # Include uncertain-time rows for the declared week. Filtering by their
        # exported clock could silently lose an All Day or tentative occurrence.
        return MarketContextQueryResult(
            events=self.capture.events,
            coverage=ContextCoverage(start=p.declared_start, end=p.declared_end,
                                     basis="Declared export week; completeness unverified"),
            source_provenance=p,
        )
