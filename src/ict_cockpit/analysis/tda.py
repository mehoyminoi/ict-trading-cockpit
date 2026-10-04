from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from uuid import uuid4


class Bias(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"

class TDAStatus(str, Enum):
    DRAFT = "Draft"
    COMPLETE = "Complete"
    INCOMPLETE_OVERRIDE = "Incomplete Override"


@dataclass
class TDARecord:
    analysis_date: date
    instrument: str
    weekly_bias: Bias
    daily_bias: Bias
    primary_draw: str
    secondary_draw: str = ""
    narrative: str = ""
    status: TDAStatus = TDAStatus.DRAFT
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not isinstance(self.weekly_bias, Bias):
            raise ValueError("weekly_bias must be a Bias value")

        if not isinstance(self.daily_bias, Bias):
            raise ValueError("daily_bias must be a Bias value")

        self.instrument = self.instrument.strip().upper()
        self.primary_draw = self.primary_draw.strip()
        self.secondary_draw = self.secondary_draw.strip()
        self.narrative = self.narrative.strip()

        if not self.instrument:
            raise ValueError("instrument cannot be empty")

        if not self.primary_draw:
            raise ValueError("primary_draw cannot be empty")
        
        if not isinstance(self.status, TDAStatus):
            raise ValueError("status must be a TDAStatus value")