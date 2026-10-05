from dataclasses import dataclass, field
from pathlib import Path

from ict_cockpit.summary.trade_summary_data import TradeSummaryData


@dataclass
class TradeSummaryContext:
    trade: TradeSummaryData

    trade_number: int = 1
    model: str = ""
    entry_tf: str = ""
    trade_source: str = ""
    account_context: str = ""

    cycle_16y: str = ""
    quadrennial: str = ""
    quarter: str = ""
    month: str = ""
    week: str = ""
    day: str = ""
    session: str = ""
    macro_90m: str = ""

    summary: str = ""
    image_paths: list[str] = field(default_factory=list)

    def to_template_values(self) -> dict[str, object]:
        chart_images = "None"
        if self.image_paths:
            chart_images = "\n".join(
                f"- {Path(path).name}" for path in self.image_paths
            )

        return {
            "date": self.trade.entry_time.strftime("%y-%m-%d"),
            "trade_number": self.trade_number,
            "asset": self.trade.instrument,
            "model": self.model,
            "direction": self.trade.direction,
            "entry_tf": self.entry_tf,
            "trade_source": self.trade_source,
            "account_context": self.account_context,
            "entry_time": self.trade.entry_time.strftime("%I:%M%p").lower(),
            "entry_price": f"{self.trade.entry_price:,.2f}",
            "close_time": self.trade.close_time.strftime("%I:%M%p").lower(),
            "close_price": f"{self.trade.close_price:,.2f}",
            "trade_time": f"{self.trade.trade_duration_minutes()}m",
            "result_handles": f"{self.trade.result_handles():.2f}",
            "result_ticks": self.trade.result_ticks(),
            "stop_handles": f"{self.trade.stop_handles():.2f}",
            "stop_ticks": self.trade.stop_ticks(),
            "reward_risk": f"{self.trade.reward_risk():.2f}",
            "cycle_16y": self.cycle_16y,
            "quadrennial": self.quadrennial,
            "quarter": self.quarter,
            "month": self.month,
            "week": self.week,
            "day": self.day,
            "session": self.session,
            "macro_90m": self.macro_90m,
            "summary": self.summary,
            "chart_images": chart_images,
        }
