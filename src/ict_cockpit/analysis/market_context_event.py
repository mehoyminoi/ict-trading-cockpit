from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping, Protocol, Sequence

from ict_cockpit.analysis.context_source import ContextCoverage, ContextSourceProvenance


class MarketContextEventCategory(str, Enum):
    ECONOMIC = "Economic"
    HOLIDAY = "Holiday"
    EARLY_CLOSE = "Early Close"
    MARKET_SCHEDULE = "Market Schedule"
    OTHER_CONTEXT = "Other Context"


class MarketContextImpact(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    UNKNOWN = "Unknown"


class MarketContextEventStatus(str, Enum):
    SCHEDULED = "Scheduled"
    TENTATIVE = "Tentative"
    POSTPONED = "Postponed"
    CANCELLED = "Cancelled"
    RELEASED = "Released"
    UNKNOWN = "Unknown"


class MarketContextTimingPrecision(str, Enum):
    EXACT = "Exact"
    DATE_ONLY = "Date Only"
    TENTATIVE = "Tentative"
    UNKNOWN = "Unknown"


@dataclass(frozen=True)
class MarketContextEvent:
    """Provider-neutral external market-context fact.

    The event is descriptive context only. It deliberately contains no Trade
    Plan warning/restriction or authorization state.
    """

    id: str
    provider: str
    source_event_id: str
    category: MarketContextEventCategory
    normalized_event_type: str
    title: str
    scheduled_at: str
    source_timezone: str = ""
    impact: MarketContextImpact = MarketContextImpact.UNKNOWN
    provider_native_impact: str = ""
    affected_markets: tuple[str, ...] = field(default_factory=tuple)
    status: MarketContextEventStatus = MarketContextEventStatus.UNKNOWN
    actual: str = ""
    forecast: str = ""
    previous: str = ""
    source_updated_at: str = ""
    captured_at: str = ""
    provenance_reference: str = ""
    timing_precision: MarketContextTimingPrecision = MarketContextTimingPrecision.UNKNOWN
    identity_basis: str = "Provider/local identity supplied by adapter"
    native_record: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", self.id.strip())
        object.__setattr__(self, "provider", self.provider.strip())
        object.__setattr__(self, "source_event_id", self.source_event_id.strip())
        object.__setattr__(
            self,
            "normalized_event_type",
            self.normalized_event_type.strip(),
        )
        object.__setattr__(self, "title", self.title.strip())
        object.__setattr__(self, "scheduled_at", self.scheduled_at.strip())
        object.__setattr__(self, "source_timezone", self.source_timezone.strip())
        object.__setattr__(
            self,
            "provider_native_impact",
            self.provider_native_impact.strip(),
        )
        object.__setattr__(
            self,
            "affected_markets",
            tuple(
                item.strip()
                for item in self.affected_markets
                if str(item).strip()
            ),
        )
        object.__setattr__(self, "actual", self.actual.strip())
        object.__setattr__(self, "forecast", self.forecast.strip())
        object.__setattr__(self, "previous", self.previous.strip())
        object.__setattr__(
            self,
            "source_updated_at",
            self.source_updated_at.strip(),
        )
        object.__setattr__(self, "captured_at", self.captured_at.strip())
        object.__setattr__(
            self,
            "provenance_reference",
            self.provenance_reference.strip(),
        )

        if not self.id:
            raise ValueError("market context event id cannot be empty")
        if not self.provider:
            raise ValueError("market context event provider cannot be empty")
        if not self.title:
            raise ValueError("market context event title cannot be empty")
        if not self.scheduled_at:
            raise ValueError("market context event scheduled_at cannot be empty")

        scheduled = parse_event_datetime(self.scheduled_at)
        if scheduled.tzinfo is None:
            raise ValueError(
                "market context event scheduled_at must include timezone/offset"
            )

        if isinstance(self.category, str):
            object.__setattr__(
                self,
                "category",
                MarketContextEventCategory(self.category),
            )
        if isinstance(self.impact, str):
            object.__setattr__(
                self,
                "impact",
                MarketContextImpact(self.impact),
            )
        if isinstance(self.status, str):
            object.__setattr__(
                self,
                "status",
                MarketContextEventStatus(self.status),
            )
        object.__setattr__(self, "timing_precision", MarketContextTimingPrecision(self.timing_precision))

    @property
    def scheduled_datetime(self) -> datetime:
        return parse_event_datetime(self.scheduled_at)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "provider": self.provider,
            "source_event_id": self.source_event_id,
            "category": self.category.value,
            "normalized_event_type": self.normalized_event_type,
            "title": self.title,
            "scheduled_at": self.scheduled_at,
            "source_timezone": self.source_timezone,
            "impact": self.impact.value,
            "provider_native_impact": self.provider_native_impact,
            "affected_markets": list(self.affected_markets),
            "status": self.status.value,
            "actual": self.actual,
            "forecast": self.forecast,
            "previous": self.previous,
            "source_updated_at": self.source_updated_at,
            "captured_at": self.captured_at,
            "provenance_reference": self.provenance_reference,
            "timing_precision": self.timing_precision.value,
            "identity_basis": self.identity_basis,
            "native_record": self.native_record,
        }

    @classmethod
    def from_dict(cls, payload: Mapping) -> "MarketContextEvent":
        return cls(
            id=str(payload.get("id", "")),
            provider=str(payload.get("provider", "")),
            source_event_id=str(payload.get("source_event_id", "")),
            category=MarketContextEventCategory(
                payload.get(
                    "category",
                    MarketContextEventCategory.OTHER_CONTEXT.value,
                )
            ),
            normalized_event_type=str(
                payload.get("normalized_event_type", "")
            ),
            title=str(payload.get("title", "")),
            scheduled_at=str(payload.get("scheduled_at", "")),
            source_timezone=str(payload.get("source_timezone", "")),
            impact=MarketContextImpact(
                payload.get("impact", MarketContextImpact.UNKNOWN.value)
            ),
            provider_native_impact=str(
                payload.get("provider_native_impact", "")
            ),
            affected_markets=tuple(
                str(item)
                for item in list(payload.get("affected_markets", []) or [])
            ),
            status=MarketContextEventStatus(
                payload.get("status", MarketContextEventStatus.UNKNOWN.value)
            ),
            actual=str(payload.get("actual", "")),
            forecast=str(payload.get("forecast", "")),
            previous=str(payload.get("previous", "")),
            source_updated_at=str(payload.get("source_updated_at", "")),
            captured_at=str(payload.get("captured_at", "")),
            provenance_reference=str(
                payload.get("provenance_reference", "")
            ),
            timing_precision=payload.get("timing_precision", MarketContextTimingPrecision.UNKNOWN.value),
            identity_basis=str(payload.get("identity_basis", "Legacy identity basis not recorded")),
            native_record=str(payload.get("native_record", "")),
        )


def parse_event_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def normalize_provider_impact(
    native_value: str,
    mapping: Mapping[str, MarketContextImpact | str],
) -> MarketContextImpact:
    """Normalize impact only through an adapter-supplied explicit mapping.

    The domain layer intentionally has no built-in meaning for terms such as
    "red folder". A provider adapter must explicitly map its own vocabulary.
    """

    key = native_value.strip()
    if not key:
        return MarketContextImpact.UNKNOWN
    mapped = mapping.get(key)
    if mapped is None:
        return MarketContextImpact.UNKNOWN
    return (
        mapped
        if isinstance(mapped, MarketContextImpact)
        else MarketContextImpact(mapped)
    )


class MarketContextEventProvider(Protocol):
    @property
    def provider_name(self) -> str:
        ...

    def query_context(
        self,
        start: datetime,
        end: datetime,
    ) -> "MarketContextQueryResult":
        ...


@dataclass(frozen=True)
class MarketContextQueryResult:
    events: tuple[MarketContextEvent, ...] = ()
    coverage: ContextCoverage = field(default_factory=ContextCoverage)
    source_provenance: ContextSourceProvenance = field(default_factory=ContextSourceProvenance)

    def __post_init__(self):
        object.__setattr__(self, "events", tuple(
            event if isinstance(event, MarketContextEvent) else MarketContextEvent.from_dict(event)
            for event in self.events
        ))
        if not isinstance(self.coverage, ContextCoverage):
            object.__setattr__(self, "coverage", ContextCoverage.from_dict(self.coverage))
        if not isinstance(self.source_provenance, ContextSourceProvenance):
            object.__setattr__(self, "source_provenance", ContextSourceProvenance.from_dict(self.source_provenance))


class MarketContextQueryUnavailable(ValueError):
    def __init__(self, message, source_provenance):
        super().__init__(message)
        self.source_provenance = source_provenance


class InMemoryMarketContextEventProvider:
    """Deterministic provider used for tests and provider-contract development."""

    def __init__(
        self,
        provider_name: str,
        events: Sequence[MarketContextEvent] = (),
    ) -> None:
        self._provider_name = provider_name.strip()
        if not self._provider_name:
            raise ValueError("provider_name cannot be empty")
        self._events = tuple(events)

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def query_context(self, start, end):
        return MarketContextQueryResult(
            events=self.events_between(start, end),
            coverage=ContextCoverage(start.isoformat(), end.isoformat(), True,
                ("*",), ("*",), ("*",), ("*",), "Complete deterministic in-memory fixture"),
        )

    def events_between(
        self,
        start: datetime,
        end: datetime,
    ) -> tuple[MarketContextEvent, ...]:
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("event query bounds must be timezone-aware")
        if end < start:
            raise ValueError("event query end cannot be before start")

        matches = [
            event
            for event in self._events
            if start <= event.scheduled_datetime <= end
        ]
        return tuple(
            sorted(
                matches,
                key=lambda event: (
                    event.scheduled_datetime,
                    event.id,
                ),
            )
        )



class MarketContextSnapshotStatus(str, Enum):
    AVAILABLE = "Available"
    NOT_CONFIGURED = "Not Configured"
    UNAVAILABLE = "Unavailable"


@dataclass(frozen=True)
class MarketContextSnapshot:
    """Immutable run-level snapshot of external market-context facts."""

    status: MarketContextSnapshotStatus
    provider: str
    query_start: str
    query_end: str
    reference_market_time: str
    market_time_source: str
    captured_at: str
    events: tuple[MarketContextEvent, ...] = field(default_factory=tuple)
    detail: str = ""
    coverage: ContextCoverage = field(default_factory=ContextCoverage)
    source_provenance: ContextSourceProvenance = field(default_factory=ContextSourceProvenance)

    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            object.__setattr__(
                self,
                "status",
                MarketContextSnapshotStatus(self.status),
            )
        object.__setattr__(self, "provider", self.provider.strip())
        object.__setattr__(self, "query_start", self.query_start.strip())
        object.__setattr__(self, "query_end", self.query_end.strip())
        object.__setattr__(
            self,
            "reference_market_time",
            self.reference_market_time.strip(),
        )
        object.__setattr__(
            self,
            "market_time_source",
            self.market_time_source.strip(),
        )
        object.__setattr__(self, "captured_at", self.captured_at.strip())
        object.__setattr__(self, "detail", self.detail.strip())
        if not isinstance(self.coverage, ContextCoverage):
            object.__setattr__(self, "coverage", ContextCoverage.from_dict(self.coverage))
        if not isinstance(self.source_provenance, ContextSourceProvenance):
            object.__setattr__(self, "source_provenance", ContextSourceProvenance.from_dict(self.source_provenance))
        object.__setattr__(
            self,
            "events",
            tuple(
                item
                if isinstance(item, MarketContextEvent)
                else MarketContextEvent.from_dict(item)
                for item in self.events
            ),
        )

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "provider": self.provider,
            "query_start": self.query_start,
            "query_end": self.query_end,
            "reference_market_time": self.reference_market_time,
            "market_time_source": self.market_time_source,
            "captured_at": self.captured_at,
            "events": [item.to_dict() for item in self.events],
            "detail": self.detail,
            "coverage": self.coverage.to_dict(),
            "source_provenance": self.source_provenance.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: Mapping | None) -> "MarketContextSnapshot":
        source = dict(payload or {})
        return cls(
            status=MarketContextSnapshotStatus(
                source.get(
                    "status",
                    MarketContextSnapshotStatus.NOT_CONFIGURED.value,
                )
            ),
            provider=str(source.get("provider", "")),
            query_start=str(source.get("query_start", "")),
            query_end=str(source.get("query_end", "")),
            reference_market_time=str(
                source.get("reference_market_time", "")
            ),
            market_time_source=str(source.get("market_time_source", "")),
            captured_at=str(source.get("captured_at", "")),
            events=tuple(
                MarketContextEvent.from_dict(item)
                for item in list(source.get("events", []) or [])
            ),
            detail=str(source.get("detail", "")),
            coverage=ContextCoverage.from_dict(source.get("coverage")),
            source_provenance=ContextSourceProvenance.from_dict(source.get("source_provenance")),
        )


def futures_day_event_window(
    futures_trading_day: str,
    *,
    timezone,
) -> tuple[datetime, datetime]:
    """Return the Cockpit's 18:00-to-18:00 futures-day event window."""

    from datetime import date, time, timedelta

    trading_date = date.fromisoformat(futures_trading_day)
    start = datetime.combine(
        trading_date - timedelta(days=1),
        time(18, 0),
        tzinfo=timezone,
    )
    end = datetime.combine(
        trading_date,
        time(18, 0),
        tzinfo=timezone,
    ) - timedelta(microseconds=1)
    return start, end


def capture_market_context_snapshot(
    *,
    provider: MarketContextEventProvider | None,
    market_time_context: Mapping,
    market_timezone,
    captured_at: str,
) -> MarketContextSnapshot:
    """Capture external context once for a Trading Run.

    The resulting snapshot is historical run provenance. Restoring a run should
    read this stored snapshot rather than re-querying a provider.
    """

    futures_day = str(
        market_time_context.get("futures_trading_day", "")
    ).strip()
    reference_time = str(
        market_time_context.get("captured_at", "")
    ).strip()
    source = str(market_time_context.get("source", "")).strip()

    if not futures_day:
        return MarketContextSnapshot(
            status=MarketContextSnapshotStatus.UNAVAILABLE,
            provider=(
                provider.provider_name if provider is not None else ""
            ),
            query_start="",
            query_end="",
            reference_market_time=reference_time,
            market_time_source=source,
            captured_at=captured_at,
            detail="Futures trading day is unavailable.",
        )

    query_start, query_end = futures_day_event_window(
        futures_day,
        timezone=market_timezone,
    )

    if provider is None:
        return MarketContextSnapshot(
            status=MarketContextSnapshotStatus.NOT_CONFIGURED,
            provider="",
            query_start=query_start.isoformat(),
            query_end=query_end.isoformat(),
            reference_market_time=reference_time,
            market_time_source=source,
            captured_at=captured_at,
            detail="No market-context event provider is configured.",
        )

    try:
        if hasattr(provider, "query_context"):
            result = provider.query_context(query_start, query_end)
            if not isinstance(result, MarketContextQueryResult):
                raise ValueError("Provider must return a MarketContextQueryResult")
        else:
            # Transitional adapters preserve availability, never claim completeness.
            result = MarketContextQueryResult(events=provider.events_between(query_start, query_end))
        events = result.events
    except Exception as exc:
        return MarketContextSnapshot(
            status=MarketContextSnapshotStatus.UNAVAILABLE,
            provider=provider.provider_name,
            query_start=query_start.isoformat(),
            query_end=query_end.isoformat(),
            reference_market_time=reference_time,
            market_time_source=source,
            captured_at=captured_at,
            detail=f"Provider query unavailable: {exc}",
            source_provenance=getattr(exc, "source_provenance", ContextSourceProvenance()),
        )

    return MarketContextSnapshot(
        status=MarketContextSnapshotStatus.AVAILABLE,
        provider=provider.provider_name,
        query_start=query_start.isoformat(),
        query_end=query_end.isoformat(),
        reference_market_time=reference_time,
        market_time_source=source,
        captured_at=captured_at,
        events=events,
        coverage=result.coverage,
        source_provenance=result.source_provenance,
        detail=(
            "Provider query completed with no matching events."
            if not events
            else f"{len(events)} event(s) captured."
        ),
    )
