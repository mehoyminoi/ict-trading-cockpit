from datetime import datetime

import pytest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.market_context_event import (
    InMemoryMarketContextEventProvider,
    MarketContextEvent,
    MarketContextEventCategory,
    MarketContextImpact,
    MarketContextSnapshot,
    MarketContextSnapshotStatus,
    capture_market_context_snapshot,
    futures_day_event_window,
)
from ict_cockpit.analysis.market_time import (
    MARKET_TIMEZONE,
    build_market_time_context,
)
from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import RunEnvironment, TradingRun
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import (
    TradingDaySessionRepository,
)
from ict_cockpit.database.trading_session_run_repository import (
    TradingSessionRunRepository,
)
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def event(
    *,
    event_id: str,
    title: str,
    scheduled_at: str,
    actual: str = "",
) -> MarketContextEvent:
    return MarketContextEvent(
        id=event_id,
        provider="Fixture Calendar",
        source_event_id=event_id,
        category=MarketContextEventCategory.ECONOMIC,
        normalized_event_type=title.upper().replace(" ", "_"),
        title=title,
        scheduled_at=scheduled_at,
        source_timezone="America/New_York",
        impact=MarketContextImpact.HIGH,
        provider_native_impact="fixture-high",
        affected_markets=("USD",),
        actual=actual,
        captured_at="2026-10-10T12:00:00-04:00",
        provenance_reference=f"fixture://{event_id}",
    )


def test_futures_day_event_window_matches_18_to_18_boundary() -> None:
    start, end = futures_day_event_window(
        "2026-10-06",
        timezone=MARKET_TIMEZONE,
    )

    assert start.isoformat().startswith("2026-10-05T18:00:00")
    assert end.isoformat().startswith("2026-10-06T17:59:59.999999")


def test_not_configured_is_distinct_from_available_with_no_events() -> None:
    market = build_market_time_context(
        datetime(2026, 10, 6, 10, 15, tzinfo=MARKET_TIMEZONE),
        source="Historical Reference",
    ).to_dict()

    not_configured = capture_market_context_snapshot(
        provider=None,
        market_time_context=market,
        market_timezone=MARKET_TIMEZONE,
        captured_at="2026-10-10T12:00:00-04:00",
    )
    available_empty = capture_market_context_snapshot(
        provider=InMemoryMarketContextEventProvider("Fixture Calendar"),
        market_time_context=market,
        market_timezone=MARKET_TIMEZONE,
        captured_at="2026-10-10T12:00:00-04:00",
    )

    assert not_configured.status is MarketContextSnapshotStatus.NOT_CONFIGURED
    assert not_configured.events == ()
    assert available_empty.status is MarketContextSnapshotStatus.AVAILABLE
    assert available_empty.events == ()
    assert "no matching events" in available_empty.detail.lower()


def test_provider_failure_is_unavailable_not_no_event() -> None:
    class BrokenProvider:
        @property
        def provider_name(self) -> str:
            return "Broken Fixture"

        def events_between(self, start, end):
            raise RuntimeError("fixture outage")

    market = build_market_time_context(
        datetime(2026, 10, 6, 10, 15, tzinfo=MARKET_TIMEZONE),
        source="Historical Reference",
    ).to_dict()

    snapshot = capture_market_context_snapshot(
        provider=BrokenProvider(),
        market_time_context=market,
        market_timezone=MARKET_TIMEZONE,
        captured_at="2026-10-10T12:00:00-04:00",
    )

    assert snapshot.status is MarketContextSnapshotStatus.UNAVAILABLE
    assert snapshot.events == ()
    assert "fixture outage" in snapshot.detail


def test_replay_uses_selected_historical_futures_day_not_current_events() -> None:
    get_app()
    historical = event(
        event_id="cpi-2026-10-06",
        title="CPI",
        scheduled_at="2026-10-06T08:30:00-04:00",
    )
    later = event(
        event_id="fomc-2026-10-28",
        title="FOMC",
        scheduled_at="2026-10-28T14:00:00-04:00",
    )
    provider = InMemoryMarketContextEventProvider(
        "Fixture Calendar",
        (later, historical),
    )
    shell = TradingDayShellWidget(
        build_default_process_blueprint(),
        run_environment=RunEnvironment.REPLAY,
        market_context_event_provider=provider,
    )
    shell.run_market_timestamp = datetime(
        2026,
        10,
        6,
        10,
        15,
        tzinfo=MARKET_TIMEZONE,
    )

    assert shell.start_trading_run() is True
    run = shell.active_trading_run
    assert run is not None
    snapshot = MarketContextSnapshot.from_dict(run.market_context_snapshot)

    assert snapshot.status is MarketContextSnapshotStatus.AVAILABLE
    assert snapshot.reference_market_time.startswith("2026-10-06T10:15")
    assert snapshot.market_time_source == "Historical Reference"
    assert [item.id for item in snapshot.events] == ["cpi-2026-10-06"]
    assert snapshot.query_start.startswith("2026-10-05T18:00")
    assert snapshot.query_end.startswith("2026-10-06T17:59:59.999999")


def test_run_snapshot_is_not_silently_rewritten_when_provider_changes() -> None:
    get_app()
    initial = event(
        event_id="cpi-2026-10-06",
        title="CPI",
        scheduled_at="2026-10-06T08:30:00-04:00",
        actual="",
    )
    revised = event(
        event_id="cpi-2026-10-06",
        title="CPI",
        scheduled_at="2026-10-06T08:30:00-04:00",
        actual="3.4%",
    )

    shell = TradingDayShellWidget(
        build_default_process_blueprint(),
        run_environment=RunEnvironment.REPLAY,
        market_context_event_provider=InMemoryMarketContextEventProvider(
            "Fixture Calendar",
            (initial,),
        ),
    )
    shell.run_market_timestamp = datetime(
        2026,
        10,
        6,
        10,
        15,
        tzinfo=MARKET_TIMEZONE,
    )
    assert shell.start_trading_run() is True
    run = shell.active_trading_run
    assert run is not None
    original_snapshot = dict(run.market_context_snapshot)

    shell.market_context_event_provider = InMemoryMarketContextEventProvider(
        "Fixture Calendar",
        (revised,),
    )
    shell.runtime.load_trading_run(run)

    assert run.market_context_snapshot == original_snapshot
    restored = MarketContextSnapshot.from_dict(run.market_context_snapshot)
    assert restored.events[0].actual == ""


def test_market_context_snapshot_round_trips_through_run_repository(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    run_repository = TradingSessionRunRepository(connection)
    day_repository = TradingDayRepository(connection)
    process_repository = TradingDaySessionRepository(connection)

    day = TradingDay(futures_day_label="2026-10-06")
    process = TradingDaySession(
        blueprint_revision="Alpha 0.2",
        mode_ids=["tda", "live-watch", "post-market"],
        current_mode_id="tda",
    )
    process_repository.save(process)
    day_repository.save(day)

    market = build_market_time_context(
        datetime(2026, 10, 6, 10, 15, tzinfo=MARKET_TIMEZONE),
        source="Historical Reference",
    ).to_dict()
    snapshot = capture_market_context_snapshot(
        provider=InMemoryMarketContextEventProvider(
            "Fixture Calendar",
            (
                event(
                    event_id="cpi-2026-10-06",
                    title="CPI",
                    scheduled_at="2026-10-06T08:30:00-04:00",
                ),
            ),
        ),
        market_time_context=market,
        market_timezone=MARKET_TIMEZONE,
        captured_at="2026-10-10T12:00:00-04:00",
    )

    run = TradingRun(
        day.id,
        "Trading Run 1",
        process.id,
        environment=RunEnvironment.REPLAY,
        market_time_context=market,
        market_context_snapshot=snapshot.to_dict(),
    )
    run_repository.save(run)

    restored = run_repository.get_by_id(run.id)

    assert restored is not None
    restored_snapshot = MarketContextSnapshot.from_dict(
        restored.market_context_snapshot
    )
    assert restored_snapshot == snapshot
    assert restored_snapshot.events[0].provenance_reference == (
        "fixture://cpi-2026-10-06"
    )
    connection.close()


def test_schema_v35_adds_market_context_snapshot_storage(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    version = connection.execute("PRAGMA user_version").fetchone()[0]
    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(trading_session_run)"
        ).fetchall()
    }

    assert version == CURRENT_SCHEMA_VERSION
    assert version >= 35
    assert "market_context_snapshot_json" in columns
    connection.close()



def test_run_without_historical_event_snapshot_stays_not_configured() -> None:
    run = TradingRun(
        "day-1",
        "Trading Run 1",
        "process-1",
    )

    snapshot = MarketContextSnapshot.from_dict(run.market_context_snapshot)

    assert snapshot.status is MarketContextSnapshotStatus.NOT_CONFIGURED
    assert snapshot.events == ()
