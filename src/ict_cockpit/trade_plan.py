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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "EntryCriterionDefinition":
        return cls(
            id=str(payload.get("id", "")),
            name=str(payload.get("name", "")),
            description=str(payload.get("description", "")),
        )


@dataclass(frozen=True)
class WatchPointTemplateDefinition:
    """Plan-owned IF/THEN condition inherited into a Trading Run."""

    id: str
    if_condition: str
    then_action: str
    note: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("watch-point template id cannot be empty")
        if not self.if_condition.strip():
            raise ValueError("watch-point IF condition cannot be empty")
        if not self.then_action.strip():
            raise ValueError("watch-point THEN action cannot be empty")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "if_condition": self.if_condition,
            "then_action": self.then_action,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "WatchPointTemplateDefinition":
        return cls(
            id=str(payload.get("id", "")),
            if_condition=str(payload.get("if_condition", "")),
            then_action=str(payload.get("then_action", "")),
            note=str(payload.get("note", "")),
        )


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
class PlaybookDefinition:
    """Declarative, revisioned strategy definition owned by the Trade Plan.

    This object intentionally contains data only. A future no-code editor can
    create the same structure without generating Python, and renderers (runtime,
    review, PDF export) can consume it without becoming authoritative sources.
    """

    id: str
    name: str
    revision: str
    purpose: str = ""
    sessions: tuple[str, ...] = field(default_factory=tuple)
    preparation: tuple[str, ...] = field(default_factory=tuple)
    watch_point_templates: tuple[WatchPointTemplateDefinition, ...] = field(
        default_factory=tuple
    )
    entry_criteria: tuple[EntryCriterionDefinition, ...] = field(default_factory=tuple)
    required_entry_count: int | None = None
    entry_rules: tuple[str, ...] = field(default_factory=tuple)
    target_rules: tuple[str, ...] = field(default_factory=tuple)
    management_rules: tuple[str, ...] = field(default_factory=tuple)
    risk_summary: str = ""
    available: bool = True
    availability_note: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("playbook id cannot be empty")
        if not self.name.strip():
            raise ValueError("playbook name cannot be empty")
        if not self.revision.strip():
            raise ValueError("playbook revision cannot be empty")

        watch_ids = [item.id for item in self.watch_point_templates]
        if len(watch_ids) != len(set(watch_ids)):
            raise ValueError("playbook watch-point ids must be unique")

        # Reuse the same validation that Live Watch consumes.
        self.live_watch_policy()

    def live_watch_policy(self) -> LiveWatchPolicyDefinition:
        return LiveWatchPolicyDefinition(
            entry_criteria=self.entry_criteria,
            required_entry_count=self.required_entry_count,
            risk_summary=self.risk_summary,
        )

    def watch_point_runtime_id(self, template_id: str) -> str:
        return f"playbook:{self.id}:{template_id}"

    def to_snapshot(self) -> dict:
        """Return primitive data suitable for immutable run provenance storage."""
        return {
            "id": self.id,
            "name": self.name,
            "revision": self.revision,
            "purpose": self.purpose,
            "sessions": list(self.sessions),
            "preparation": list(self.preparation),
            "watch_point_templates": [
                item.to_dict() for item in self.watch_point_templates
            ],
            "entry_criteria": [item.to_dict() for item in self.entry_criteria],
            "required_entry_count": self.required_entry_count,
            "entry_rules": list(self.entry_rules),
            "target_rules": list(self.target_rules),
            "management_rules": list(self.management_rules),
            "risk_summary": self.risk_summary,
            "available": self.available,
            "availability_note": self.availability_note,
        }

    @classmethod
    def from_snapshot(cls, payload: dict) -> "PlaybookDefinition":
        return cls(
            id=str(payload.get("id", "")),
            name=str(payload.get("name", "")),
            revision=str(payload.get("revision", "")),
            purpose=str(payload.get("purpose", "")),
            sessions=tuple(str(item) for item in payload.get("sessions", [])),
            preparation=tuple(str(item) for item in payload.get("preparation", [])),
            watch_point_templates=tuple(
                WatchPointTemplateDefinition.from_dict(item)
                for item in payload.get("watch_point_templates", [])
            ),
            entry_criteria=tuple(
                EntryCriterionDefinition.from_dict(item)
                for item in payload.get("entry_criteria", [])
            ),
            required_entry_count=payload.get("required_entry_count"),
            entry_rules=tuple(str(item) for item in payload.get("entry_rules", [])),
            target_rules=tuple(str(item) for item in payload.get("target_rules", [])),
            management_rules=tuple(
                str(item) for item in payload.get("management_rules", [])
            ),
            risk_summary=str(payload.get("risk_summary", "")),
            available=bool(payload.get("available", True)),
            availability_note=str(payload.get("availability_note", "")),
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

    The current object is immutable once constructed. Future in-app editing should
    create a draft/new Trade Plan revision rather than silently mutating a revision
    that has already governed Trading Runs.
    """

    id: str
    name: str
    revision: str
    sections: tuple[TradePlanSectionDefinition, ...]
    process_blueprint: ProcessBlueprint
    playbooks: tuple[PlaybookDefinition, ...] = field(default_factory=tuple)
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

        playbook_ids = [playbook.id for playbook in self.playbooks]
        if len(playbook_ids) != len(set(playbook_ids)):
            raise ValueError("trade plan playbook ids must be unique")

    def section_by_id(self, section_id: str) -> TradePlanSectionDefinition | None:
        for section in self.sections:
            if section.id == section_id:
                return section
        return None

    def playbook_by_id(self, playbook_id: str) -> PlaybookDefinition | None:
        for playbook in self.playbooks:
            if playbook.id == playbook_id:
                return playbook
        return None
