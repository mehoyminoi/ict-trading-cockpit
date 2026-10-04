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
    weekly_bias: Bias | None = None
    daily_bias: Bias | None = None
    primary_draw: str | None = None
    secondary_draw: str = ""
    narrative: str = ""
    status: TDAStatus = TDAStatus.DRAFT
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if self.weekly_bias is not None and not isinstance(
            self.weekly_bias,
            Bias,
        ):
            raise ValueError("weekly_bias must be a Bias value or None")

        if self.daily_bias is not None and not isinstance(
            self.daily_bias,
            Bias,
        ):
            raise ValueError("daily_bias must be a Bias value or None")

        if not isinstance(self.status, TDAStatus):
            raise ValueError("status must be a TDAStatus value")

        self.instrument = self.instrument.strip().upper()

        if self.primary_draw is not None:
            self.primary_draw = self.primary_draw.strip()

            if not self.primary_draw:
                self.primary_draw = None

        self.secondary_draw = self.secondary_draw.strip()
        self.narrative = self.narrative.strip()

        if not self.instrument:
            raise ValueError("instrument cannot be empty")

        if self.status == TDAStatus.COMPLETE:
            missing = self.missing_required_fields()

            if missing:
                raise ValueError(
                    "Complete TDA is missing required fields: "
                    + ", ".join(missing)
                )

    def missing_required_fields(self) -> list[str]:
        missing = []

        if self.weekly_bias is None:
            missing.append("Weekly Bias")

        if self.daily_bias is None:
            missing.append("Daily Bias")

        if self.primary_draw is None:
            missing.append("Primary Draw")

        return missing