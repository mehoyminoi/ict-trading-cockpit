from datetime import datetime, timezone

from ict_cockpit.analysis.market_time import (
    MARKET_TIMEZONE,
    build_market_time_context,
    futures_trading_day_for,
)


def window_by_id(context, window_id: str):
    return next(item for item in context.timed_windows if item.id == window_id)


def test_0915_ny_is_nyam_q3_with_silver_bullet_upcoming() -> None:
    context = build_market_time_context(
        datetime(2026, 10, 6, 9, 15, tzinfo=MARKET_TIMEZONE),
        source="Historical Reference",
    )

    assert context.timezone == "America/New_York"
    assert context.futures_trading_day == "2026-10-06"
    assert context.session == "NYAM"
    assert context.daily_quarter == "Q3"
    assert context.session_quarter == "Q3"
    nyam = window_by_id(context, "nyam-silver-bullet")
    assert nyam.state == "Upcoming"
    assert nyam.minutes_until_start == 45
    assert context.next_window_id == "nyam-silver-bullet"


def test_1015_ny_marks_nyam_silver_bullet_active() -> None:
    context = build_market_time_context(
        datetime(2026, 10, 6, 10, 15, tzinfo=MARKET_TIMEZONE)
    )

    nyam = window_by_id(context, "nyam-silver-bullet")
    assert nyam.state == "Active"
    assert "nyam-silver-bullet" in context.active_window_ids
    assert context.session == "NYAM"
    assert context.session_quarter == "Q3"


def test_1815_ny_rolls_to_next_futures_day_and_asia_q1() -> None:
    moment = datetime(2026, 10, 6, 18, 15, tzinfo=MARKET_TIMEZONE)
    context = build_market_time_context(moment)

    assert futures_trading_day_for(moment).isoformat() == "2026-10-07"
    assert context.futures_trading_day == "2026-10-07"
    assert context.session == "Asia"
    assert context.daily_quarter == "Q1"
    assert context.session_quarter == "Q1"


def test_aware_non_ny_timestamp_is_normalized_to_new_york() -> None:
    context = build_market_time_context(
        datetime(2026, 10, 6, 13, 15, tzinfo=timezone.utc)
    )

    assert context.captured_at.startswith("2026-10-06T09:15")
    assert context.session == "NYAM"


def test_weekend_context_is_explicitly_closed() -> None:
    context = build_market_time_context(
        datetime(2026, 10, 10, 10, 0, tzinfo=MARKET_TIMEZONE)
    )

    assert context.market_open is False
    assert context.session == "Closed"
    assert context.daily_quarter == ""
    assert context.session_quarter == ""
