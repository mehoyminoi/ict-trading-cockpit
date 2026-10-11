from copy import deepcopy
from datetime import datetime

import pytest
from PySide6.QtCore import Qt

from ict_cockpit.analysis.market_context_event import (
    MarketContextEvent,
    MarketContextEventCategory as Category,
    MarketContextEventStatus as EventStatus,
    MarketContextImpact,
    MarketContextSnapshot,
    MarketContextSnapshotStatus as SnapshotStatus,
    InMemoryMarketContextEventProvider,
)
from ict_cockpit.analysis.market_context_view import build_market_context_view
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, build_market_time_context
from ict_cockpit.analysis.trading_session_run import RunEnvironment, TradingRun
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.market_context_widget import MarketContextWidget
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


def market(hour=10, *, day=6, minute=15):
    return build_market_time_context(
        datetime(2026, 10, day, hour, minute, tzinfo=MARKET_TIMEZONE),
        source="Historical Reference",
    ).to_dict()


def event(title, at, *, category=Category.ECONOMIC, status=EventStatus.SCHEDULED):
    return MarketContextEvent(
        id=title,
        provider="Fixture Calendar",
        source_event_id=f"source-{title}",
        category=category,
        normalized_event_type="FIXTURE",
        title=title,
        scheduled_at=at,
        timing_precision="Exact",
        source_timezone="America/New_York",
        impact=MarketContextImpact.HIGH,
        provider_native_impact="fixture-high",
        affected_markets=("USD",),
        status=status,
        provenance_reference=f"fixture://{title}",
        forecast="3%",
    )


def run_with_snapshot(status=SnapshotStatus.AVAILABLE, events=()):
    return TradingRun(
        "day", "Trading Run 1", "process",
        environment=RunEnvironment.REPLAY,
        trade_plan_revision="Alpha 0.7",
        market_time_context=market(),
        market_context_snapshot=MarketContextSnapshot(
            status=status,
            provider="Fixture Calendar" if status is not SnapshotStatus.NOT_CONFIGURED else "",
            query_start="2026-10-05T18:00:00-04:00",
            query_end="2026-10-06T17:59:59.999999-04:00",
            reference_market_time="2026-10-06T10:15:00-04:00",
            market_time_source="Historical Reference",
            captured_at="2026-10-10T12:00:00-04:00",
            events=events,
        ).to_dict(),
    )


@pytest.mark.parametrize("status,expected", [
    (SnapshotStatus.AVAILABLE, "no matching events"),
    (SnapshotStatus.NOT_CONFIGURED, "context unknown"),
    (SnapshotStatus.UNAVAILABLE, "context unknown"),
])
def test_availability_is_visible_and_empty_is_not_unknown(status, expected):
    view = build_market_context_view(run_with_snapshot(status))
    assert status.value in view.availability
    assert expected in view.availability
    if status is not SnapshotStatus.AVAILABLE:
        assert "Event and schedule facts are unknown" in view.events
        assert "No upcoming" not in view.events


def test_legacy_missing_snapshot_does_not_present_successful_empty_query():
    run = TradingRun("day", "Legacy", "process")
    view = build_market_context_view(run)
    assert "Not Configured" in view.availability
    assert "no matching events" not in view.availability
    assert "Provider: Not recorded" in view.detail
    assert "Market-time / raw QT context unknown" in view.temporal


def test_watch_uses_historical_time_timezone_and_status_without_warning_horizon():
    records = (
        event("Later", "2026-10-06T20:00:00+00:00"),
        event("Cancelled", "2026-10-06T10:20:00-04:00", status=EventStatus.CANCELLED),
        event("Postponed", "2026-10-06T10:25:00-04:00", status=EventStatus.POSTPONED),
        event("Released", "2026-10-06T10:30:00-04:00", status=EventStatus.RELEASED),
        event("Next", "2026-10-06T18:00:00+00:00", status=EventStatus.TENTATIVE),
        event("Same time", "2026-10-06T14:00:00-04:00"),
        event("Past", "2026-10-06T08:30:00-04:00"),
        event("Early close", "2026-10-06T09:00:00-04:00", category=Category.EARLY_CLOSE),
    )
    run = run_with_snapshot(events=records)
    before = deepcopy(run.__dict__)
    view = build_market_context_view(run, mode_id="live-watch")
    assert "Next recorded time: Next 14:00 ET [High; Tentative]" in view.events
    assert "+1 at the same time" in view.events
    assert "Schedule fact: Early close" in view.events
    assert "Cancelled" not in view.events
    assert "Past" not in view.events
    assert "Released" not in view.events
    assert "Cancelled" in view.detail and "Postponed" in view.detail
    assert run.__dict__ == before


def test_watch_current_timestamp_and_missing_or_outside_window_are_explicit():
    run = run_with_snapshot(events=(event("Now", "2026-10-06T10:15:00-04:00"),))
    assert "At reference time: Now" in build_market_context_view(run, mode_id="live-watch").events
    assert "outside the captured event window" in build_market_context_view(
        run, mode_id="live-watch", market_time_context=market(day=7)
    ).events
    assert "Event timing unknown" in build_market_context_view(
        run, mode_id="live-watch", market_time_context={}
    ).events


def test_review_retains_every_fact_and_distinct_qt_interpretations():
    run = run_with_snapshot(events=(event("CPI", "2026-10-06T08:30:00-04:00"),))
    run.set_qt_context({"day": "M"})
    run.set_review_observed_qt_context({"day": "D"}, "Changed interpretation")
    view = build_market_context_view(run, mode_id="post-market")
    for text in (
        "AMDX expectation / TDA:", "Day M", "AMDX observed / Review:", "Day D",
        "Changed interpretation", "Trade Plan revision: Alpha 0.7",
        "Query start: 2026-10-05 18:00", "Snapshot market reference: 2026-10-06 10:15",
        "Snapshot captured at: 2026-10-10 12:00", "Historical Reference",
        "Economic · High · Scheduled", "Fixture Calendar / source-CPI",
        "fixture-high", "USD", "3%", "fixture://CPI",
        "do not imply QT structural distortion or entry permission",
    ):
        assert text in view.detail
    assert "Stored event / schedule facts" in view.events


def test_widget_is_plain_text_read_only_and_details_do_not_reopen_on_refresh():
    widget = MarketContextWidget()
    run = run_with_snapshot(events=(event("<b>Fixture</b>", "2026-10-06T14:00:00-04:00"),))
    widget.load_run_context(run, mode_id="tda")
    assert widget.detail_text.isReadOnly()
    assert widget.events_label.textFormat() is Qt.TextFormat.PlainText
    assert "<b>Fixture</b>" in widget.events_label.text()
    assert widget.detail_text.isHidden()
    widget.details_button.click()
    assert not widget.detail_text.isHidden()
    widget.detail_text.verticalScrollBar().setValue(10)
    previous = widget.detail_text.verticalScrollBar().value()
    widget.load_run_context(run, mode_id="tda")
    assert widget.details_button.isChecked()
    assert widget.detail_text.verticalScrollBar().value() == previous
    widget.load_run_context(run, mode_id="live-watch")
    assert widget.detail_text.isHidden()
    widget.load_run_context(None, mode_id="tda")
    assert widget.isHidden() and not widget.detail_text.toPlainText()


def test_runtime_modes_timer_and_restore_use_persisted_snapshot_without_provider_query(tmp_path):
    class CountingProvider(InMemoryMarketContextEventProvider):
        calls = 0

        def events_between(self, start, end):
            self.calls += 1
            return super().events_between(start, end)

    provider = CountingProvider("Fixture Calendar", (event("Historical", "2026-10-06T14:00:00-04:00"),))
    shell = TradingDayShellWidget(
        build_default_process_blueprint(), run_environment=RunEnvironment.REPLAY,
        trade_plan_revision="Alpha 0.7", market_context_event_provider=provider,
    )
    shell.run_market_timestamp = datetime(2026, 10, 6, 10, 15, tzinfo=MARKET_TIMEZONE)
    assert shell.start_trading_run()
    run = shell.active_trading_run
    original = deepcopy(run.market_context_snapshot)
    card = shell.runtime.market_context_widget
    assert card.heading_label.text().endswith("TDA")
    card.details_button.click()
    assert shell.runtime_scroll.verticalScrollBarPolicy() is Qt.ScrollBarPolicy.ScrollBarAsNeeded
    card.details_button.click()
    assert shell.runtime_scroll.verticalScrollBarPolicy() is Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    shell.runtime.tda_station_runner_widget.open_station_from_deck("tda-thesis")
    assert shell.runtime_scroll.verticalScrollBarPolicy() is Qt.ScrollBarPolicy.ScrollBarAsNeeded
    shell.runtime.go_next_mode()
    assert card.heading_label.text().endswith("Watch")
    assert "Historical 14:00" in card.events_label.text()
    shell._refresh_market_time_display()
    shell.runtime.go_next_mode()
    assert card.heading_label.text().endswith("Review")
    assert run.market_context_snapshot == original and provider.calls == 1

    connection = create_connection(tmp_path / "e4.db")
    initialize_schema(connection)
    TradingDayRepository(connection).save(shell.trading_day)
    TradingDaySessionRepository(connection).save(shell.runtime.session)
    repository = TradingSessionRunRepository(connection)
    repository.save(run)
    restored = repository.get_by_id(run.id)
    new_shell = TradingDayShellWidget(build_default_process_blueprint(), market_context_event_provider=provider)
    new_shell.load_state(shell.trading_day, [restored], process_session=shell.runtime.session)
    new_shell._refresh_market_time_display()
    assert provider.calls == 1
    assert restored.market_context_snapshot == original
    assert "Historical" in new_shell.runtime.market_context_widget.detail_text.toPlainText()
    assert "2026-10-06" in new_shell.market_time_label.text()
    connection.close()
