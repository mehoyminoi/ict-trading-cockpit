from datetime import datetime, timezone

from ict_cockpit.analysis.market_time import (
    MARKET_TIMEZONE,
    build_market_time_context,
    cycle_16y_quarter_for,
    futures_trading_day_for,
    month_week_quarter_for,
    quadrennial_year_quarter_for,
    temporal_relevance_for,
    week_day_quarter_for,
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


def test_temporal_relevance_prefers_active_configured_window() -> None:
    context = build_market_time_context(
        datetime(2026, 10, 6, 10, 15, tzinfo=MARKET_TIMEZONE)
    ).to_dict()

    relevance = temporal_relevance_for(
        context,
        (
            "london-silver-bullet",
            "nyam-silver-bullet",
            "nypm-silver-bullet",
        ),
    )

    assert relevance["state"] == "Active"
    assert relevance["window_id"] == "nyam-silver-bullet"
    assert relevance["minutes_until_start"] == 0


def test_temporal_relevance_uses_next_model_window_not_unrelated_window() -> None:
    context = build_market_time_context(
        datetime(2026, 10, 6, 11, 8, tzinfo=MARKET_TIMEZONE)
    ).to_dict()

    relevance = temporal_relevance_for(
        context,
        (
            "london-silver-bullet",
            "nyam-silver-bullet",
            "nypm-silver-bullet",
        ),
    )

    assert relevance["state"] == "Upcoming"
    assert relevance["window_id"] == "nypm-silver-bullet"
    assert relevance["minutes_until_start"] == 172


def test_temporal_relevance_is_closed_after_last_model_window() -> None:
    context = build_market_time_context(
        datetime(2026, 10, 6, 15, 5, tzinfo=MARKET_TIMEZONE)
    ).to_dict()

    relevance = temporal_relevance_for(
        context,
        (
            "london-silver-bullet",
            "nyam-silver-bullet",
            "nypm-silver-bullet",
        ),
    )

    assert relevance["state"] == "Closed"


def test_calendar_month_role_follows_quarter_po3_rule() -> None:
    expected = {
        1: ("Q1", 1, "A"),
        2: ("Q1", 2, "M"),
        3: ("Q1", 3, "D"),
        7: ("Q3", 1, "A"),
        8: ("Q3", 2, "M"),
        9: ("Q3", 3, "D"),
    }

    for month, (quarter, index, phase) in expected.items():
        context = build_market_time_context(
            datetime(2026, month, 10, 10, 15, tzinfo=MARKET_TIMEZONE)
        )
        assert context.calendar_quarter == quarter
        assert context.calendar_quarter_month_index == index
        assert context.calendar_month_phase == phase


def test_market_time_context_exposes_known_raw_qt_stack() -> None:
    context = build_market_time_context(
        datetime(2026, 10, 6, 9, 15, tzinfo=MARKET_TIMEZONE)
    )

    assert context.raw_quarters == {
        "cycle_16y": "Q4",
        "quadrennial": "Q4",
        "year": "Q4",
        "month": "Q1",
        "week": "Q2",
        "day": "Q3",
        "session": "Q3",
    }


def test_higher_order_raw_qt_anchors_match_established_cycles() -> None:
    q1 = datetime(2011, 6, 1, 10, 0, tzinfo=MARKET_TIMEZONE)
    q4 = datetime(2026, 6, 1, 10, 0, tzinfo=MARKET_TIMEZONE)
    next_cycle = datetime(2027, 6, 1, 10, 0, tzinfo=MARKET_TIMEZONE)

    assert cycle_16y_quarter_for(q1) == "Q1"
    assert quadrennial_year_quarter_for(q1) == "Q1"
    assert cycle_16y_quarter_for(q4) == "Q4"
    assert quadrennial_year_quarter_for(q4) == "Q4"
    assert cycle_16y_quarter_for(next_cycle) == "Q1"
    assert quadrennial_year_quarter_for(next_cycle) == "Q1"


def test_monthly_raw_quarter_starts_on_first_monday_and_fifth_week_distorts() -> None:
    before_first_monday = datetime(2026, 10, 2, 10, 0, tzinfo=MARKET_TIMEZONE)
    week_1 = datetime(2026, 10, 5, 10, 0, tzinfo=MARKET_TIMEZONE)
    week_4 = datetime(2026, 10, 26, 10, 0, tzinfo=MARKET_TIMEZONE)
    week_5 = datetime(2026, 11, 30, 10, 0, tzinfo=MARKET_TIMEZONE)

    assert month_week_quarter_for(before_first_monday) == ""
    assert month_week_quarter_for(week_1) == "Q1"
    assert month_week_quarter_for(week_4) == "Q4"
    assert month_week_quarter_for(week_5) == "Distortion"


def test_weekly_raw_quarter_uses_futures_trading_day() -> None:
    monday_nyam = datetime(2026, 10, 5, 10, 0, tzinfo=MARKET_TIMEZONE)
    monday_evening_asia = datetime(2026, 10, 5, 18, 15, tzinfo=MARKET_TIMEZONE)
    friday = datetime(2026, 10, 9, 10, 0, tzinfo=MARKET_TIMEZONE)

    assert week_day_quarter_for(monday_nyam) == "Q1"
    assert week_day_quarter_for(monday_evening_asia) == "Q2"
    assert week_day_quarter_for(friday) == ""


def test_raw_qt_layers_explain_parent_child_and_effective_interval() -> None:
    context = build_market_time_context(
        datetime(2026, 10, 6, 9, 15, tzinfo=MARKET_TIMEZONE)
    )
    layers = {item["id"]: item for item in context.raw_quarter_layers}

    assert layers["cycle_16y"]["parent_label"] == "16Y Cycle 2011–2026"
    assert layers["cycle_16y"]["active_child_label"] == "4-year block 2023–2026"
    assert layers["cycle_16y"]["quarter"] == "Q4"
    assert layers["cycle_16y"]["source"] == "Derived"

    assert layers["quadrennial"]["parent_label"] == "Quadrennial 2023–2026"
    assert layers["quadrennial"]["active_child_label"] == "Year 2026"
    assert layers["quadrennial"]["quarter"] == "Q4"

    assert layers["year"]["parent_label"] == "Calendar Year 2026"
    assert layers["year"]["active_child_label"] == "Oct–Dec"
    assert layers["year"]["quarter"] == "Q4"

    assert layers["month"]["parent_label"] == "October 2026"
    assert "Oct 5–11, 2026" in layers["month"]["active_child_label"]
    assert layers["month"]["quarter"] == "Q1"

    assert layers["week"]["active_child_label"] == "Tuesday 2026-10-06"
    assert layers["week"]["effective_start"].startswith("2026-10-05T18:00")
    assert layers["week"]["effective_end"].startswith("2026-10-06T18:00")

    assert layers["day"]["parent_label"] == "Trading Day 2026-10-06"
    assert layers["day"]["active_child_label"] == "NYAM"

    assert layers["session"]["parent_label"] == "NYAM Session 06:00–12:00"
    assert layers["session"]["active_child_label"] == "09:00–10:30"
