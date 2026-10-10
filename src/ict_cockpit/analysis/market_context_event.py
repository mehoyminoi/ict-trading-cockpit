from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping, Protocol, Sequence


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

    def events_between(
        self,
        start: datetime,
        end: datetime,
    ) -> tuple[MarketContextEvent, ...]:
        ...


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
