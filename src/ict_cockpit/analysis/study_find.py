from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


@dataclass
class StudyFind:
    observation_date: date
    instrument: str
    session: str
    pattern_name: str
    observation: str
    available_move_handles: float | None = None
    notes: str = ""
    image_path: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self.instrument = self.instrument.strip().upper()
        self.session = self.session.strip()
        self.pattern_name = self.pattern_name.strip()
        self.observation = self.observation.strip()
        self.notes = self.notes.strip()
        self.image_path = self.image_path.strip()

        if not self.instrument:
            raise ValueError("instrument cannot be empty")

        if not self.session:
            raise ValueError("session cannot be empty")

        if not self.pattern_name:
            raise ValueError("pattern_name cannot be empty")

        if not self.observation:
            raise ValueError("observation cannot be empty")