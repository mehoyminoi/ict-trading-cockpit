from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


TRADE_SOURCES = (
    "TradingView Replay",
    "TradingView Paper",
    "NinjaTrader Sim",
    "NinjaTrader Prop",
    "NinjaTrader Cash",
    "Manual / Other",
)


@dataclass
class TradeRecordDraft:
    instrument: str = ""
    trade_source: str = "TradingView Replay"
    account_context: str = ""
    trade_number: int = 1
    model: str = ""
    direction: str = "Long"
    entry_tf: str = ""
    entry_time: datetime | None = None
    close_time: datetime | None = None
    entry_price: float | None = None
    close_price: float | None = None
    stop_price: float | None = None
    tick_size: float = 0.25
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
    id: str = field(default_factory=lambda: str(uuid4()))

    def has_content(self) -> bool:
        return any(
            (
                self.instrument.strip(),
                self.account_context.strip(),
                self.model.strip(),
                self.entry_tf.strip(),
                self.entry_price is not None,
                self.close_price is not None,
                self.stop_price is not None,
                self.cycle_16y.strip(),
                self.quadrennial.strip(),
                self.quarter.strip(),
                self.month.strip(),
                self.week.strip(),
                self.day.strip(),
                self.session.strip(),
                self.macro_90m.strip(),
                self.summary.strip(),
                bool(self.image_paths),
            )
        )


@dataclass
class TradeRecord:
    instrument: str
    trade_source: str
    account_context: str
    trade_number: int
    model: str
    direction: str
    entry_tf: str
    entry_time: datetime
    close_time: datetime
    entry_price: float
    close_price: float
    stop_price: float
    tick_size: float
    cycle_16y: str = ""
    quadrennial: str = ""
    quarter: str = ""
    month: str = ""
    week: str = ""
    day: str = ""
    session: str = ""
    macro_90m: str = ""
    summary: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self.instrument = self.instrument.strip().upper()
        self.trade_source = self.trade_source.strip()
        self.account_context = self.account_context.strip()
        self.model = self.model.strip()
        self.direction = self.direction.strip().title()
        self.entry_tf = self.entry_tf.strip()
        self.summary = self.summary.strip()

        if not self.instrument:
            raise ValueError("instrument cannot be empty")
        if self.trade_source not in TRADE_SOURCES:
            raise ValueError("unsupported trade source")
        if self.direction not in ("Long", "Short"):
            raise ValueError("direction must be Long or Short")
        if self.close_time < self.entry_time:
            raise ValueError("close_time cannot be before entry_time")
        if self.tick_size <= 0:
            raise ValueError("tick_size must be positive")
