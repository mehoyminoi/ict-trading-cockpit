from datetime import datetime, timezone

import pytest

from ict_cockpit.analysis.market_context_event import (
    InMemoryMarketContextEventProvider,
    MarketContextEvent,
    MarketContextEventCategory,
    MarketContextEventStatus,
    MarketContextImpact,
    normalize_provider_impact,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema


def economic_event(**overrides) -> MarketContextEvent:
    values = {
        "id": "fixture:cpi:2026-10-13T08:30-04:00",
        "provider": "Fixture Calendar",
        "source_event_id": "cpi-2026-10-13",
        "category": MarketContextEventCategory.ECONOMIC,
        "normalized_event_type": "CPI",
        "title": "CPI",
        "scheduled_at": "2026-10-13T08:30:00-04:00",
        "timing_precision": "Exact",
        "source_timezone": "America/New_York",
        "impact": MarketContextImpact.HIGH,
        "provider_native_impact": "red",
        "affected_markets": ("USD", "US Index Futures"),
        "status": MarketContextEventStatus.SCHEDULED,
        "forecast": "0.3%",
        "previous": "0.2%",
        "captured_at": "2026-10-10T12:00:00-04:00",
        "provenance_reference": "fixture://calendar/cpi-2026-10-13",
    }
    values.update(overrides)
    return MarketContextEvent(**values)


def test_market_context_event_round_trip_preserves_provider_provenance() -> None:
    event = economic_event()

    restored = MarketContextEvent.from_dict(event.to_dict())

    assert restored == event
    assert restored.provider_native_impact == "red"
    assert restored.impact is MarketContextImpact.HIGH
    assert restored.affected_markets == ("USD", "US Index Futures")
    assert restored.provenance_reference == (
        "fixture://calendar/cpi-2026-10-13"
    )


def test_event_requires_timezone_aware_schedule() -> None:
    with pytest.raises(ValueError, match="timezone/offset"):
        economic_event(scheduled_at="2026-10-13T08:30:00")


def test_provider_impact_normalization_requires_explicit_adapter_mapping() -> None:
    mapping = {
        "red": MarketContextImpact.HIGH,
        "orange": MarketContextImpact.MEDIUM,
        "yellow": MarketContextImpact.LOW,
    }

    assert (
        normalize_provider_impact("red", mapping)
        is MarketContextImpact.HIGH
    )
    assert (
        normalize_provider_impact("red folder", mapping)
        is MarketContextImpact.UNKNOWN
    )
    assert (
        normalize_provider_impact("", mapping)
        is MarketContextImpact.UNKNOWN
    )


def test_context_categories_keep_schedule_and_economic_facts_distinct() -> None:
    holiday = economic_event(
        id="fixture:holiday:2026-11-26",
        source_event_id="holiday-2026-11-26",
        category=MarketContextEventCategory.HOLIDAY,
        normalized_event_type="US_MARKET_HOLIDAY",
        title="Thanksgiving",
        scheduled_at="2026-11-26T00:00:00-05:00",
        impact=MarketContextImpact.UNKNOWN,
        provider_native_impact="",
    )
    early_close = economic_event(
        id="fixture:early-close:2026-11-27",
        source_event_id="early-close-2026-11-27",
        category=MarketContextEventCategory.EARLY_CLOSE,
        normalized_event_type="EARLY_CLOSE",
        title="US index futures early close",
        scheduled_at="2026-11-27T13:15:00-05:00",
        impact=MarketContextImpact.UNKNOWN,
        provider_native_impact="",
    )

    assert holiday.category is MarketContextEventCategory.HOLIDAY
    assert early_close.category is MarketContextEventCategory.EARLY_CLOSE
    assert economic_event().category is MarketContextEventCategory.ECONOMIC


def test_event_model_contains_context_facts_not_trade_restrictions() -> None:
    payload = economic_event().to_dict()

    assert "warning" not in payload
    assert "restriction" not in payload
    assert "authorization" not in payload
    assert "block_new_entry" not in payload
    assert "stand_down" not in payload


def test_in_memory_provider_returns_deterministic_window_in_time_order() -> None:
    first = economic_event(
        id="fixture:nfp",
        source_event_id="nfp",
        normalized_event_type="NFP",
        title="Nonfarm Payrolls",
        scheduled_at="2026-10-09T08:30:00-04:00",
    )
    second = economic_event()
    outside = economic_event(
        id="fixture:fomc",
        source_event_id="fomc",
        normalized_event_type="FOMC",
        title="FOMC Rate Decision",
        scheduled_at="2026-10-28T14:00:00-04:00",
    )
    provider = InMemoryMarketContextEventProvider(
        "Fixture Calendar",
        (outside, second, first),
    )

    events = provider.events_between(
        datetime(2026, 10, 9, 0, 0, tzinfo=timezone.utc),
        datetime(2026, 10, 14, 0, 0, tzinfo=timezone.utc),
    )

    assert provider.provider_name == "Fixture Calendar"
    assert [event.id for event in events] == [
        "fixture:nfp",
        "fixture:cpi:2026-10-13T08:30-04:00",
    ]


def test_in_memory_provider_rejects_ambiguous_query_bounds() -> None:
    provider = InMemoryMarketContextEventProvider("Fixture Calendar")

    with pytest.raises(ValueError, match="timezone-aware"):
        provider.events_between(
            datetime(2026, 10, 9, 0, 0),
            datetime(2026, 10, 10, 0, 0),
        )

    with pytest.raises(ValueError, match="end cannot be before start"):
        provider.events_between(
            datetime(2026, 10, 10, tzinfo=timezone.utc),
            datetime(2026, 10, 9, tzinfo=timezone.utc),
        )


def test_e2_domain_model_does_not_change_schema(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    version = connection.execute("PRAGMA user_version").fetchone()[0]

    assert version == CURRENT_SCHEMA_VERSION
    connection.close()
