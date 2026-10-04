from datetime import datetime

from ict_cockpit.summary.trade_summary_context import TradeSummaryContext
from ict_cockpit.summary.trade_summary_data import TradeSummaryData
from ict_cockpit.summary.renderer import SummaryRenderer
from ict_cockpit.summary.templates import TRADE_SUMMARY_V1


def test_trade_summary_context_formats_template_values() -> None:
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

    context = TradeSummaryContext(
        trade=trade,
        trade_number=1,
        model="NYAM FVG",
        entry_tf="5m",
        cycle_16y="2023-2026 M",
        quadrennial="2026 X(R)",
        quarter="Q3 D",
        month="October A",
        week="W2 M",
        day="Tuesday A",
        session="NYAM D",
        summary="Testing summary formatting.",
    )

    values = context.to_template_values()


    assert values["date"] == "26-10-04"
    assert values["asset"] == "MNQ"
    assert values["entry_price"] == "20,589.00"
    assert values["close_price"] == "20,774.25"
    assert values["trade_time"] == "46m"
    assert values["result_handles"] == "185.25"
    assert values["result_ticks"] == 741
    assert values["stop_handles"] == "68.00"
    assert values["stop_ticks"] == 272
    assert values["reward_risk"] == "2.72"

def test_trade_summary_context_renders_standard_template() -> None:
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

    context = TradeSummaryContext(
        trade=trade,
        trade_number=1,
        model="NYAM FVG",
        entry_tf="5m",
        cycle_16y="2023-2026 M",
        quadrennial="2026 X(R)",
        quarter="Q3 D",
        month="October A",
        week="W2 M",
        day="Tuesday A",
        session="NYAM D",
        summary="Bullish morning bias. Waited for NYAM manipulation.",
    )

    renderer = SummaryRenderer()

    rendered = renderer.render(
        TRADE_SUMMARY_V1,
        context.to_template_values(),
    )

    assert "Date: 26-10-04 Trade #1" in rendered
    assert "Asset: MNQ" in rendered
    assert "Entry Price: 20,589.00" in rendered
    assert "Trade Results: 185.25 handles/ 741 ticks" in rendered
    assert "Reward/Risk: 2.72:1" in rendered
    assert "16Y Cycle: 2023-2026 M" in rendered
    assert "Summary: Bullish morning bias." in rendered