from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SummaryTemplateKind(str, Enum):
    TRADE_SUMMARY = "Trade Summary"
    STUDY_FIND = "Study Find"


@dataclass(frozen=True)
class SummaryTemplateDefinition:
    template_id: str
    revision: int
    kind: SummaryTemplateKind
    name: str
    body: str
    created_at: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "template_id", self.template_id.strip())
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "body", self.body.rstrip() + "\n")
        object.__setattr__(self, "created_at", self.created_at.strip())
        if not self.template_id:
            raise ValueError("summary template id cannot be empty")
        if self.revision < 1:
            raise ValueError("summary template revision must be >= 1")
        if not self.name:
            raise ValueError("summary template name cannot be empty")
        if not self.body.strip():
            raise ValueError("summary template body cannot be empty")

    @property
    def label(self) -> str:
        return f"{self.name} · r{self.revision}"
