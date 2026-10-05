from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


FEEDBACK_CATEGORIES = (
    "Friction",
    "Wish",
    "Bug",
    "Review Later",
)


@dataclass
class FeedbackEntry:
    category: str
    note: str
    context: str
    record_id: str = ""
    app_version: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
    )
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self.category = self.category.strip()
        self.note = self.note.strip()
        self.context = self.context.strip()
        self.record_id = self.record_id.strip()
        self.app_version = self.app_version.strip()

        if self.category not in FEEDBACK_CATEGORIES:
            raise ValueError(f"unsupported feedback category: {self.category}")

        if not self.note:
            raise ValueError("feedback note cannot be empty")
