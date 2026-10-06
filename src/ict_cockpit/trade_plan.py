from dataclasses import dataclass, field

from ict_cockpit.process_blueprint import ProcessBlueprint


@dataclass(frozen=True)
class EntryCriterionDefinition:
    """One plan-owned condition that contributes to entry authorization."""

    id: str
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("entry criterion id cannot be empty")
        if not self.name.strip():
            raise ValueError("entry criterion name cannot be empty")


@dataclass(frozen=True)
class LiveWatchPolicyDefinition:
    """Trade Plan rules inherited by the Live Watch operating surface.

    An empty policy is valid. It means the active Trade Plan revision has not yet
    encoded these rules, and lower layers must display that fact rather than
    inventing defaults.
    """

    entry_criteria: tuple[EntryCriterionDefinition, ...] = field(default_factory=tuple)
    required_entry_count: int | None = None
    risk_summary: str = ""

    def __post_init__(self) -> None:
        criterion_ids = [criterion.id for criterion in self.entry_criteria]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("entry criterion ids must be unique")

        if not self.entry_criteria:
            if self.required_entry_count is not None:
                raise ValueError(
                    "required entry count cannot be set without entry criteria"
                )
            return

        if self.required_entry_count is None:
            raise ValueError(
                "configured entry criteria require an explicit required entry count"
            )
        if self.required_entry_count < 1:
            raise ValueError("required entry count must be at least 1")
        if self.required_entry_count > len(self.entry_criteria):
            raise ValueError(
                "required entry count cannot exceed configured entry criteria"
            )


@dataclass(frozen=True)
class TradePlanSectionDefinition:
    id: str
    name: str
    purpose: str
    topics: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("trade plan section id cannot be empty")
        if not self.name.strip():
            raise ValueError("trade plan section name cannot be empty")
        if not self.purpose.strip():
            raise ValueError("trade plan section purpose cannot be empty")


@dataclass(frozen=True)
class TradePlanDefinition:
    """Read-only alpha definition of the trading system that owns the process map.

    The Trade Plan is the authoritative system definition. The Process Blueprint is
    its executable/runtime view: the ordered modes, decks, and stations used while
    operating the plan. Live Watch policy is also owned here so runtime surfaces
    inherit rules rather than defining trading policy themselves.
    """

    id: str
    name: str
    revision: str
    sections: tuple[TradePlanSectionDefinition, ...]
    process_blueprint: ProcessBlueprint
    live_watch_policy: LiveWatchPolicyDefinition = field(
        default_factory=LiveWatchPolicyDefinition
    )

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("trade plan id cannot be empty")
        if not self.name.strip():
            raise ValueError("trade plan name cannot be empty")
        if not self.revision.strip():
            raise ValueError("trade plan revision cannot be empty")
        if not self.sections:
            raise ValueError("trade plan must contain at least one section")

        section_ids = [section.id for section in self.sections]
        if len(section_ids) != len(set(section_ids)):
            raise ValueError("trade plan section ids must be unique")

        if "process" not in section_ids:
            raise ValueError("trade plan must contain a process section")

    def section_by_id(self, section_id: str) -> TradePlanSectionDefinition | None:
        for section in self.sections:
            if section.id == section_id:
                return section
        return None
