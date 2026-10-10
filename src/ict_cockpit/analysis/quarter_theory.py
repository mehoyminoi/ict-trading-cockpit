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



class QTComparisonState(str, Enum):
    MATCHED = "Matched"
    CHANGED = "Changed"
    EXPECTED_UNKNOWN = "Expected Unknown"
    OBSERVED_UNKNOWN = "Observed Unknown"
    NOT_COMPARABLE = "Not Comparable"


RAW_QT_STACK_LEVELS = (
    ("cycle_16y", "16Y"),
    ("quadrennial", "4Y"),
    ("year", "Year"),
    ("month", "Month"),
    ("week", "Week"),
    ("day", "Day"),
    ("session", "Session"),
)


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


def apply_time_derived_qt_context(
    qt_context: dict | None,
    market_time_context: dict | None,
) -> dict[str, str]:
    """Apply only QT roles that are explicitly derivable from market time."""

    result = normalize_qt_context(qt_context)
    market = dict(market_time_context or {})
    derived_month = str(market.get("calendar_month_phase", "")).strip()
    if derived_month in {
        QTPhase.ACCUMULATION.value,
        QTPhase.MANIPULATION.value,
        QTPhase.DISTRIBUTION.value,
    }:
        result["month"] = derived_month
    return result


def raw_quarter_stack(
    market_time_context: dict | None,
    *,
    level_ids: tuple[str, ...] = tuple(
        level_id for level_id, _label in RAW_QT_STACK_LEVELS
    ),
) -> tuple[str, ...]:
    """Return known factual raw quarter positions in a stable level order."""

    market = dict(market_time_context or {})
    raw = dict(market.get("raw_quarters", {}) or {})
    return tuple(
        str(raw.get(level_id, "")).strip()
        for level_id in level_ids
        if str(raw.get(level_id, "")).strip()
    )


def raw_quarter_stack_summary(market_time_context: dict | None) -> str:
    stack = raw_quarter_stack(market_time_context)
    return " / ".join(stack) if stack else "Not available"


def raw_quarter_stack_detail(market_time_context: dict | None) -> str:
    market = dict(market_time_context or {})
    raw = dict(market.get("raw_quarters", {}) or {})
    parts = [
        f"{label} {str(raw.get(level_id, '')).strip()}"
        for level_id, label in RAW_QT_STACK_LEVELS
        if str(raw.get(level_id, "")).strip()
    ]
    return " · ".join(parts) if parts else "Not available"


def raw_quarter_alignment(market_time_context: dict | None) -> dict[str, int]:
    """Count repeated raw Q1-Q4 values across currently assigned stack levels."""

    counts: dict[str, int] = {}
    for value in raw_quarter_stack(market_time_context):
        if value in {"Q1", "Q2", "Q3", "Q4"}:
            counts[value] = counts.get(value, 0) + 1
    return counts


def raw_quarter_layer_contexts(
    market_time_context: dict | None,
) -> tuple[dict, ...]:
    market = dict(market_time_context or {})
    return tuple(
        dict(item)
        for item in list(market.get("raw_quarter_layers", []) or [])
        if isinstance(item, dict)
    )


def raw_quarter_contextual_summary(
    market_time_context: dict | None,
) -> str:
    """Compact raw stack with enough child identity to remove nomenclature ambiguity."""

    layers = raw_quarter_layer_contexts(market_time_context)
    if not layers:
        return raw_quarter_stack_detail(market_time_context)

    parts = []
    for item in layers:
        quarter = str(item.get("quarter", "")).strip()
        if not quarter:
            continue
        short = str(item.get("short_label", item.get("id", ""))).strip()
        child = str(item.get("active_child_label", "")).strip()

        if item.get("id") == "cycle_16y":
            compact_child = child.replace("4-year block ", "")
        elif item.get("id") == "quadrennial":
            compact_child = child.replace("Year ", "")
        elif item.get("id") == "year":
            compact_child = child
        elif item.get("id") == "month":
            compact_child = child.replace("Monday-week ", "").replace("Fifth ", "")
        elif item.get("id") == "week":
            compact_child = child.split(" ")[0] if child else ""
        elif item.get("id") == "day":
            compact_child = child
        elif item.get("id") == "session":
            compact_child = child
        else:
            compact_child = child

        qualifier = f" ({compact_child})" if compact_child else ""
        parts.append(f"{short}{qualifier} {quarter}")

    return " · ".join(parts) if parts else "Not available"


def raw_quarter_provenance_tooltip(
    market_time_context: dict | None,
) -> str:
    layers = raw_quarter_layer_contexts(market_time_context)
    if not layers:
        return ""

    lines = ["Raw QT layer reference"]
    for item in layers:
        quarter = str(item.get("quarter", "")).strip() or "Unassigned"
        parent = str(item.get("parent_label", "")).strip()
        child = str(item.get("active_child_label", "")).strip()
        start = str(item.get("effective_start", "")).strip()
        end = str(item.get("effective_end", "")).strip()
        source = str(item.get("source", "Derived")).strip()

        line = (
            f"{item.get('short_label', item.get('id', 'Layer'))}: "
            f"{parent} → {child} · {quarter}"
        )
        if start or end:
            line += f" · {start or '?'} → {end or '?'}"
        line += f" · {source}"
        lines.append(line)

    return "\n".join(lines)


def qt_interpretation_provenance(
    qt_context: dict | None,
    market_time_context: dict | None,
) -> dict[str, str]:
    """Describe whether each AMDX interpretation is derived, entered, or missing."""

    context = normalize_qt_context(qt_context)
    market = dict(market_time_context or {})
    derived_month = str(market.get("calendar_month_phase", "")).strip()

    provenance: dict[str, str] = {}
    for level_id, _label in QT_LEVELS:
        value = context[level_id]
        if level_id == "month" and derived_month and value == derived_month:
            provenance[level_id] = "Derived"
        elif value == QTPhase.NOT_APPLICABLE.value:
            provenance[level_id] = "Unknown"
        else:
            provenance[level_id] = "Technician"
    return provenance


def raw_quarter_stack_relevance(
    market_time_context: dict | None,
    *,
    min_count: int = 2,
) -> tuple[dict, ...]:
    """Describe repeated raw-quarter alignments without assigning significance.

    A returned alignment is factual context only. Count, direction, probability,
    ranking, and authorization meaning belong to future Trade Plan/evidence rules.
    """

    minimum = max(int(min_count), 2)
    market = dict(market_time_context or {})
    raw = dict(market.get("raw_quarters", {}) or {})
    labels = dict(RAW_QT_STACK_LEVELS)

    grouped: dict[str, list[str]] = {quarter: [] for quarter in ("Q1", "Q2", "Q3", "Q4")}
    for level_id, _label in RAW_QT_STACK_LEVELS:
        quarter = str(raw.get(level_id, "")).strip()
        if quarter in grouped:
            grouped[quarter].append(level_id)

    alignments = []
    for quarter in ("Q1", "Q2", "Q3", "Q4"):
        level_ids = grouped[quarter]
        if len(level_ids) < minimum:
            continue
        alignments.append(
            {
                "quarter": quarter,
                "count": len(level_ids),
                "level_ids": tuple(level_ids),
                "level_labels": tuple(labels[level_id] for level_id in level_ids),
                "kind": "Raw Quarter Alignment",
                "meaning": "Descriptive only",
            }
        )

    return tuple(
        sorted(
            alignments,
            key=lambda item: (-int(item["count"]), str(item["quarter"])),
        )
    )


def raw_quarter_stack_relevance_summary(
    market_time_context: dict | None,
    *,
    min_count: int = 2,
) -> str:
    alignments = raw_quarter_stack_relevance(
        market_time_context,
        min_count=min_count,
    )
    if not alignments:
        return "No repeated raw-quarter alignment"

    parts = []
    for item in alignments:
        layers = ", ".join(item["level_labels"])
        parts.append(
            f"{item['quarter']}×{item['count']} ({layers})"
        )
    return " · ".join(parts)


def raw_quarter_stack_relevance_tooltip(
    market_time_context: dict | None,
    *,
    min_count: int = 2,
) -> str:
    alignments = raw_quarter_stack_relevance(
        market_time_context,
        min_count=min_count,
    )
    if not alignments:
        return (
            "No Q1–Q4 value currently repeats across two or more assigned raw QT layers."
        )

    lines = [
        "Raw QT alignment reference",
        "Descriptive context only — no directional, probability, ranking, or authorization meaning is assigned.",
    ]
    for item in alignments:
        lines.append(
            f"{item['quarter']} × {item['count']}: "
            + ", ".join(item["level_labels"])
        )
    return "\n".join(lines)



def compare_qt_context(
    expected: dict | None,
    observed: dict | None,
) -> tuple[dict, ...]:
    """Compare technician QT/AMDX interpretations without scoring them."""

    expected_context = normalize_qt_context(expected)
    observed_context = normalize_qt_context(observed)
    rows = []
    for level_id, label in QT_LEVELS:
        expected_value = expected_context[level_id]
        observed_value = observed_context[level_id]
        if (
            expected_value == QTPhase.NOT_APPLICABLE.value
            and observed_value == QTPhase.NOT_APPLICABLE.value
        ):
            state = QTComparisonState.NOT_COMPARABLE
        elif expected_value == QTPhase.NOT_APPLICABLE.value:
            state = QTComparisonState.EXPECTED_UNKNOWN
        elif observed_value == QTPhase.NOT_APPLICABLE.value:
            state = QTComparisonState.OBSERVED_UNKNOWN
        elif expected_value == observed_value:
            state = QTComparisonState.MATCHED
        else:
            state = QTComparisonState.CHANGED
        rows.append(
            {
                "level_id": level_id,
                "label": label,
                "expected": expected_value,
                "observed": observed_value,
                "state": state.value,
            }
        )
    return tuple(rows)


def qt_context_comparison_summary(
    expected: dict | None,
    observed: dict | None,
) -> str:
    rows = compare_qt_context(expected, observed)
    meaningful = [
        row for row in rows
        if row["state"] != QTComparisonState.NOT_COMPARABLE.value
    ]
    if not meaningful:
        return "No comparable QT / AMDX interpretation recorded"
    return " · ".join(
        f'{row["label"]}: {row["expected"]} → {row["observed"]} ({row["state"]})'
        for row in meaningful
    )
