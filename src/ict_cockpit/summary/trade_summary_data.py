from dataclasses import dataclass
from datetime import datetime


@dataclass
class TradeSummaryData:
    instrument: str
    entry_time: datetime
    close_time: datetime
    entry_price: float
    close_price: float
    stop_price: float
    direction: str
    tick_size: float

    def trade_duration_minutes(self) -> int:
        duration = self.close_time - self.entry_time
        return int(duration.total_seconds() // 60)

    def result_handles(self) -> float:
        if self.direction.lower() == "long":
            return self.close_price - self.entry_price

        if self.direction.lower() == "short":
            return self.entry_price - self.close_price

        raise ValueError("direction must be Long or Short")

    def result_ticks(self) -> int:
        return round(
            self.result_handles() / self.tick_size
        )

    def stop_handles(self) -> float:
        return abs(
            self.entry_price - self.stop_price
        )

    def stop_ticks(self) -> int:
        return round(
            self.stop_handles() / self.tick_size
        )

    def reward_risk(self) -> float:
        stop = self.stop_handles()

        if stop == 0:
            raise ValueError("stop distance cannot be zero")

        return self.result_handles() / stop