from dataclasses import dataclass, field
from enum import Enum


class QTPhase(str, Enum):
    NOT_APPLICABLE = "N/A"
    X_CONTINUATION = "X(C)"
    X_REVERSAL = "X(R)"
    ACCUMULATION = "A"
    MANIPULATION = "M"
    DISTRIBUTION = "D"
    DISTORTION = "Distortion"


QT_LEVELS = (
    ("cycle_16y", "16Y"),
    ("quadrennial", "Quadrennial"),
    ("quarter", "Quarter"),
    ("month", "Month"),
    ("week", "Week"),
    ("day", "Day"),
    ("session", "Session"),
    ("macro_90m", "90m Macro"),
)


def normalize_qt_context(payload: dict | None = None) -> dict[str, str]:
    source = dict(payload or {})
    result: dict[str, str] = {}
    valid = {item.value for item in QTPhase}
    for level_id, _label in QT_LEVELS:
        value = str(source.get(level_id, QTPhase.NOT_APPLICABLE.value))
        result[level_id] = value if value in valid else QTPhase.NOT_APPLICABLE.value
    return result


def qt_context_summary(payload: dict | None, *, include_na: bool = False) -> str:
    context = normalize_qt_context(payload)
    parts = []
    for level_id, label in QT_LEVELS:
        value = context[level_id]
        if not include_na and value == QTPhase.NOT_APPLICABLE.value:
            continue
        parts.append(f"{label} {value}")
    return " · ".join(parts) if parts else "No QT / AMDX interpretation recorded"


@dataclass
class QuarterTheoryContext:
    """Technician interpretation layered on top of factual market-time context."""

    phases: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.phases = normalize_qt_context(self.phases)

    def set_phase(self, level_id: str, phase: QTPhase | str) -> None:
        if level_id not in {item[0] for item in QT_LEVELS}:
            raise ValueError(f"unknown QT level: {level_id}")
        self.phases[level_id] = QTPhase(phase).value

    def to_dict(self) -> dict[str, str]:
        return dict(self.phases)

    @classmethod
    def from_dict(cls, payload: dict | None) -> "QuarterTheoryContext":
        return cls(phases=dict(payload or {}))

    def summary(self, *, include_na: bool = False) -> str:
        return qt_context_summary(self.phases, include_na=include_na)
