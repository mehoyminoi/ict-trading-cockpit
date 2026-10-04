from datetime import datetime

from ict_cockpit.summary.trade_summary_data import TradeSummaryData


def test_trade_summary_calculations_for_long_trade() -> None:
    trade = TradeSummaryData(
        instrument="MNQ",
        entry_time=datetime(2026, 10, 4, 9, 45),
        close_time=datetime(2026, 10, 4, 10, 31),
        entry_price=20589.00,
        close_price=20774.25,
        stop_price=20521.00,
        direction="Long",
        tick_size=0.25,
    )

    assert trade.trade_duration_minutes() == 46
    assert trade.result_handles() == 185.25
    assert trade.result_ticks() == 741
    assert trade.stop_handles() == 68.0
    assert trade.stop_ticks() == 272

def test_trade_summary_calculates_reward_risk() -> None:
    trade = TradeSummaryData(
        instrument="MNQ",
        entry_time=datetime(2026, 10, 4, 9, 45),
        close_time=datetime(2026, 10, 4, 10, 31),
        entry_price=20589.00,
        close_price=20774.25,
        stop_price=20521.00,
        direction="Long",
        tick_size=0.25,
    )

    assert round(trade.reward_risk(), 2) == 2.72

def test_trade_summary_calculations_for_short_trade() -> None:
    trade = TradeSummaryData(
        instrument="MNQ",
        entry_time=datetime(2026, 10, 4, 14, 0),
        close_time=datetime(2026, 10, 4, 14, 30),
        entry_price=20700.00,
        close_price=20600.00,
        stop_price=20740.00,
        direction="Short",
        tick_size=0.25,
    )

    assert trade.result_handles() == 100.0
    assert trade.result_ticks() == 400
    assert trade.stop_handles() == 40.0
    assert trade.stop_ticks() == 160
    assert trade.reward_risk() == 2.5