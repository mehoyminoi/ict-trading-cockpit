from ict_cockpit.summary.renderer import SummaryRenderer
from ict_cockpit.summary.templates import TRADE_SUMMARY_V1


def test_trade_summary_template_renders_values() -> None:
    renderer = SummaryRenderer()

    values = {
        "date": "26-10-04",
        "trade_number": 1,
        "asset": "MNQ",
        "trade_source": "TradingView Replay",
        "account_context": "October 2026 replay",
        "model": "NYAM FVG",
        "direction": "Long",
        "entry_tf": "5m",
        "entry_time": "09:45am EST",
        "entry_price": "20,589.00",
        "close_time": "10:31am EST",
        "close_price": "20,774.25",
        "trade_time": "46m",
        "result_handles": "185.25",
        "result_ticks": "741",
        "stop_handles": "68",
        "stop_ticks": "272",
        "reward_risk": "2.72",
        "cycle_16y": "2023-2026 M",
        "quadrennial": "2026 X(R)",
        "quarter": "Q3 D",
        "month": "October A",
        "week": "W2 M",
        "day": "Tuesday A",
        "session": "NYAM D",
        "macro_90m": "",
        "summary": (
            "Bullish morning bias. Waited for NYAM manipulation "
            "and entered after bullish displacement."
        ),
        "chart_images": "- chart-1.png",
    }

    rendered = renderer.render(
        TRADE_SUMMARY_V1,
        values,
    )

    assert "Asset: MNQ" in rendered
    assert "Source: TradingView Replay" in rendered
    assert "Account: October 2026 replay" in rendered
    assert "Trade Results: 185.25 handles/ 741 ticks" in rendered
    assert "Reward/Risk: 2.72:1" in rendered
    assert "16Y Cycle: 2023-2026 M" in rendered
    assert "Summary: Bullish morning bias." in rendered
    assert "- chart-1.png" in rendered


def test_renderer_allows_blank_optional_values() -> None:
    renderer = SummaryRenderer()

    template = "Model: {model}\n90m Macro Cycle: {macro_90m}"

    rendered = renderer.render(
        template,
        {
            "model": None,
            "macro_90m": None,
        },
    )

    assert rendered == "Model: \n90m Macro Cycle: "
