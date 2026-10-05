from dataclasses import dataclass, field

from ict_cockpit.process_blueprint import ProcessBlueprint


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
    operating the plan.
    """

    id: str
    name: str
    revision: str
    sections: tuple[TradePlanSectionDefinition, ...]
    process_blueprint: ProcessBlueprint

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
