from dataclasses import dataclass, field
from enum import Enum

from ict_cockpit.process_blueprint import ProcessBlueprint
from ict_cockpit.progression import ProgressionBoundary


@dataclass(frozen=True)
class CompetencyDefinition:
    """One plan-owned skill or mechanic that can be trained and validated."""

    id: str
    name: str
    category: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("competency id cannot be empty")
        if not self.name.strip():
            raise ValueError("competency name cannot be empty")
        if not self.category.strip():
            raise ValueError("competency category cannot be empty")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "CompetencyDefinition":
        return cls(
            id=str(payload.get("id", "")),
            name=str(payload.get("name", "")),
            category=str(payload.get("category", "")),
            description=str(payload.get("description", "")),
        )


class ProgressionRequirementKind(str, Enum):
    EVIDENCE_MATURITY_STATE = "Evidence Maturity State"
    COMPETENCY_STATE = "Competency State"
    EVIDENCE_PURPOSE_PRESENT = "Evidence Purpose Present"
    HUMAN_CERTIFICATION = "Human Certification"


class ProgressionRequirementOperator(str, Enum):
    IS = "IS"
    IS_ONE_OF = "IS_ONE_OF"
    EXISTS = "EXISTS"


@dataclass(frozen=True)
class ProgressionRequirementDefinition:
    """One explicit gating requirement in a Trade Plan progression policy."""

    id: str
    name: str
    requirement_kind: ProgressionRequirementKind
    operator: ProgressionRequirementOperator
    expected_values: tuple[str, ...]
    competency_id: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", self.id.strip())
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "competency_id", self.competency_id.strip())
        object.__setattr__(self, "description", self.description.strip())
        if isinstance(self.requirement_kind, str):
            object.__setattr__(
                self,
                "requirement_kind",
                ProgressionRequirementKind(self.requirement_kind),
            )
        if isinstance(self.operator, str):
            object.__setattr__(
                self,
                "operator",
                ProgressionRequirementOperator(self.operator),
            )
        normalized_values = tuple(
            str(item).strip()
            for item in self.expected_values
            if str(item).strip()
        )
        object.__setattr__(self, "expected_values", normalized_values)

        if not self.id:
            raise ValueError("progression requirement id cannot be empty")
        if not self.name:
            raise ValueError("progression requirement name cannot be empty")
        if not self.expected_values:
            raise ValueError("progression requirement expected values cannot be empty")

        competency_scoped = {
            ProgressionRequirementKind.EVIDENCE_MATURITY_STATE,
            ProgressionRequirementKind.COMPETENCY_STATE,
            ProgressionRequirementKind.EVIDENCE_PURPOSE_PRESENT,
        }
        if self.requirement_kind in competency_scoped and not self.competency_id:
            raise ValueError(
                f"{self.requirement_kind.value} requires a competency id"
            )

        if self.requirement_kind is ProgressionRequirementKind.EVIDENCE_MATURITY_STATE:
            if self.operator not in {
                ProgressionRequirementOperator.IS,
                ProgressionRequirementOperator.IS_ONE_OF,
            }:
                raise ValueError(
                    "Evidence Maturity State requires IS or IS_ONE_OF"
                )
            allowed = {
                "Not Assessed",
                "Insufficient Evidence",
                "Developing Evidence",
                "Decision-Usable Evidence",
            }
            unknown = set(self.expected_values) - allowed
            if unknown:
                raise ValueError(
                    f"unknown Evidence Maturity State value(s): {sorted(unknown)}"
                )
        elif self.requirement_kind is ProgressionRequirementKind.COMPETENCY_STATE:
            if self.operator not in {
                ProgressionRequirementOperator.IS,
                ProgressionRequirementOperator.IS_ONE_OF,
            }:
                raise ValueError(
                    "Competency State requires IS or IS_ONE_OF"
                )
            allowed = {
                "Not Assessed",
                "Under Study",
                "Rehearsal Needed",
                "Validation Needed",
                "Proficient",
            }
            unknown = set(self.expected_values) - allowed
            if unknown:
                raise ValueError(
                    f"unknown Competency State value(s): {sorted(unknown)}"
                )
        elif self.requirement_kind is ProgressionRequirementKind.EVIDENCE_PURPOSE_PRESENT:
            if self.operator is not ProgressionRequirementOperator.EXISTS:
                raise ValueError("Evidence Purpose Present requires EXISTS")
            if len(self.expected_values) != 1:
                raise ValueError(
                    "Evidence Purpose Present requires exactly one purpose"
                )
            allowed = {"Study", "Rehearsal", "Validation"}
            if self.expected_values[0] not in allowed:
                raise ValueError(
                    "Evidence Purpose Present must use Study, Rehearsal, or Validation"
                )
        elif self.requirement_kind is ProgressionRequirementKind.HUMAN_CERTIFICATION:
            if self.operator is not ProgressionRequirementOperator.IS:
                raise ValueError("Human Certification requires IS")
            if self.expected_values != ("Confirmed",):
                raise ValueError(
                    "Human Certification expected value must be Confirmed"
                )

        if (
            self.operator is ProgressionRequirementOperator.IS
            and len(self.expected_values) != 1
        ):
            raise ValueError("IS requires exactly one expected value")
        if (
            self.operator is ProgressionRequirementOperator.IS_ONE_OF
            and len(self.expected_values) < 1
        ):
            raise ValueError("IS_ONE_OF requires at least one expected value")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "requirement_kind": self.requirement_kind.value,
            "operator": self.operator.value,
            "expected_values": list(self.expected_values),
            "competency_id": self.competency_id,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "ProgressionRequirementDefinition":
        return cls(
            id=str(payload.get("id", "")),
            name=str(payload.get("name", "")),
            requirement_kind=str(payload.get("requirement_kind", "")),
            operator=str(payload.get("operator", "")),
            expected_values=tuple(
                str(item) for item in payload.get("expected_values", [])
            ),
            competency_id=str(payload.get("competency_id", "")),
            description=str(payload.get("description", "")),
        )


@dataclass(frozen=True)
class ProgressionPolicyDefinition:
    """Immutable Trade Plan-owned policy for one upward progression boundary."""

    id: str
    boundary: ProgressionBoundary
    name: str
    requirements: tuple[ProgressionRequirementDefinition, ...]
    description: str = ""
    rationale: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", self.id.strip())
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "description", self.description.strip())
        object.__setattr__(self, "rationale", self.rationale.strip())
        if isinstance(self.boundary, str):
            object.__setattr__(
                self,
                "boundary",
                ProgressionBoundary(self.boundary),
            )
        if not self.id:
            raise ValueError("progression policy id cannot be empty")
        if not self.name:
            raise ValueError("progression policy name cannot be empty")
        if not self.requirements:
            raise ValueError(
                "progression policy must contain at least one gating requirement"
            )
        requirement_ids = [item.id for item in self.requirements]
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError("progression requirement ids must be unique")
        signatures = [
            (
                item.requirement_kind.value,
                item.operator.value,
                item.competency_id,
                item.expected_values,
            )
            for item in self.requirements
        ]
        if len(signatures) != len(set(signatures)):
            raise ValueError(
                "duplicate equivalent progression requirements are not allowed"
            )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "boundary": self.boundary.value,
            "name": self.name,
            "description": self.description,
            "rationale": self.rationale,
            "requirements": [item.to_dict() for item in self.requirements],
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "ProgressionPolicyDefinition":
        return cls(
            id=str(payload.get("id", "")),
            boundary=str(payload.get("boundary", "")),
            name=str(payload.get("name", "")),
            description=str(payload.get("description", "")),
            rationale=str(payload.get("rationale", "")),
            requirements=tuple(
                ProgressionRequirementDefinition.from_dict(item)
                for item in payload.get("requirements", [])
            ),
        )


@dataclass(frozen=True)
class EntryCriterionDefinition:
    """One plan-owned condition that contributes to setup authorization."""

    id: str
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("entry criterion id cannot be empty")
        if not self.name.strip():
            raise ValueError("entry criterion name cannot be empty")

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "description": self.description}

    @classmethod
    def from_dict(cls, payload: dict) -> "EntryCriterionDefinition":
        return cls(
            id=str(payload.get("id", "")),
            name=str(payload.get("name", "")),
            description=str(payload.get("description", "")),
        )


@dataclass(frozen=True)
class AuthorizationGateDefinition:
    """A Trade Plan safety/risk gate outside model-specific setup criteria.

    ``scope`` is either ``Run`` for conditions shared by every candidate in the
    Trading Run, or ``Candidate`` for conditions that must be evaluated for each
    setup independently. The definition is declarative so later no-code editing
    and automatic evaluators can use the same object.
    """

    id: str
    name: str
    description: str = ""
    scope: str = "Run"

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("authorization gate id cannot be empty")
        if not self.name.strip():
            raise ValueError("authorization gate name cannot be empty")
        if self.scope not in {"Run", "Candidate"}:
            raise ValueError("authorization gate scope must be 'Run' or 'Candidate'")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "AuthorizationGateDefinition":
        return cls(
            id=str(payload.get("id", "")),
            name=str(payload.get("name", "")),
            description=str(payload.get("description", "")),
            scope=str(payload.get("scope", "Run")),
        )


@dataclass(frozen=True)
class WatchPointTemplateDefinition:
    """Plan-owned IF/THEN condition inherited into a Trading Run.

    ``satisfies_criterion_ids`` is explicit process wiring: when this watch point
    is marked Occurred, those entry criteria become satisfied for that setup
    candidate. No text matching or implicit inference is used.
    """

    id: str
    if_condition: str
    then_action: str
    note: str = ""
    satisfies_criterion_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("watch-point template id cannot be empty")
        if not self.if_condition.strip():
            raise ValueError("watch-point IF condition cannot be empty")
        if not self.then_action.strip():
            raise ValueError("watch-point THEN action cannot be empty")
        if len(self.satisfies_criterion_ids) != len(set(self.satisfies_criterion_ids)):
            raise ValueError("watch-point criterion links must be unique")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "if_condition": self.if_condition,
            "then_action": self.then_action,
            "note": self.note,
            "satisfies_criterion_ids": list(self.satisfies_criterion_ids),
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "WatchPointTemplateDefinition":
        return cls(
            id=str(payload.get("id", "")),
            if_condition=str(payload.get("if_condition", "")),
            then_action=str(payload.get("then_action", "")),
            note=str(payload.get("note", "")),
            satisfies_criterion_ids=tuple(
                str(item) for item in payload.get("satisfies_criterion_ids", [])
            ),
        )


@dataclass(frozen=True)
class LiveWatchPolicyDefinition:
    """Legacy/global Live Watch policy retained for compatibility."""

    entry_criteria: tuple[EntryCriterionDefinition, ...] = field(default_factory=tuple)
    required_entry_count: int | None = None
    risk_summary: str = ""

    def __post_init__(self) -> None:
        criterion_ids = [criterion.id for criterion in self.entry_criteria]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("entry criterion ids must be unique")
        if not self.entry_criteria:
            if self.required_entry_count is not None:
                raise ValueError("required entry count cannot be set without entry criteria")
            return
        if self.required_entry_count is None:
            raise ValueError("configured entry criteria require an explicit required entry count")
        if self.required_entry_count < 1:
            raise ValueError("required entry count must be at least 1")
        if self.required_entry_count > len(self.entry_criteria):
            raise ValueError("required entry count cannot exceed configured entry criteria")


@dataclass(frozen=True)
class PlaybookDefinition:
    """Declarative, revisioned strategy definition owned by the Trade Plan."""

    id: str
    name: str
    revision: str
    purpose: str = ""
    sessions: tuple[str, ...] = field(default_factory=tuple)
    timed_window_ids: tuple[str, ...] = field(default_factory=tuple)
    preparation: tuple[str, ...] = field(default_factory=tuple)
    watch_point_templates: tuple[WatchPointTemplateDefinition, ...] = field(default_factory=tuple)
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
        criterion_ids = {criterion.id for criterion in self.entry_criteria}
        for watch_point in self.watch_point_templates:
            unknown = set(watch_point.satisfies_criterion_ids) - criterion_ids
            if unknown:
                raise ValueError(
                    f"watch point {watch_point.id!r} links unknown criteria: {sorted(unknown)}"
                )
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
        return {
            "id": self.id,
            "name": self.name,
            "revision": self.revision,
            "purpose": self.purpose,
            "sessions": list(self.sessions),
            "timed_window_ids": list(self.timed_window_ids),
            "preparation": list(self.preparation),
            "watch_point_templates": [item.to_dict() for item in self.watch_point_templates],
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
            timed_window_ids=tuple(
                str(item) for item in payload.get("timed_window_ids", [])
            ),
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
            management_rules=tuple(str(item) for item in payload.get("management_rules", [])),
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
    """Immutable published Trade Plan definition.

    Future in-app editing should create a draft/new revision rather than mutate a
    revision that has already governed Trading Runs.
    """

    id: str
    name: str
    revision: str
    sections: tuple[TradePlanSectionDefinition, ...]
    process_blueprint: ProcessBlueprint
    playbooks: tuple[PlaybookDefinition, ...] = field(default_factory=tuple)
    competencies: tuple[CompetencyDefinition, ...] = field(default_factory=tuple)
    authorization_gates: tuple[AuthorizationGateDefinition, ...] = field(default_factory=tuple)
    progression_policies: tuple[ProgressionPolicyDefinition, ...] = field(default_factory=tuple)
    live_watch_policy: LiveWatchPolicyDefinition = field(default_factory=LiveWatchPolicyDefinition)

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
        competency_ids = [item.id for item in self.competencies]
        if len(competency_ids) != len(set(competency_ids)):
            raise ValueError("trade plan competency ids must be unique")
        gate_ids = [gate.id for gate in self.authorization_gates]
        if len(gate_ids) != len(set(gate_ids)):
            raise ValueError("trade plan authorization gate ids must be unique")
        policy_ids = [policy.id for policy in self.progression_policies]
        if len(policy_ids) != len(set(policy_ids)):
            raise ValueError("trade plan progression policy ids must be unique")
        policy_boundaries = [policy.boundary for policy in self.progression_policies]
        if len(policy_boundaries) != len(set(policy_boundaries)):
            raise ValueError(
                "trade plan can define at most one progression policy per boundary"
            )
        known_competencies = set(competency_ids)
        for policy in self.progression_policies:
            for requirement in policy.requirements:
                if (
                    requirement.competency_id
                    and requirement.competency_id not in known_competencies
                ):
                    raise ValueError(
                        f"progression policy {policy.id!r} references unknown "
                        f"competency {requirement.competency_id!r}"
                    )

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

    def competency_by_id(
        self,
        competency_id: str,
    ) -> CompetencyDefinition | None:
        for competency in self.competencies:
            if competency.id == competency_id:
                return competency
        return None

    def progression_policy_by_boundary(
        self,
        boundary: ProgressionBoundary | str,
    ) -> ProgressionPolicyDefinition | None:
        target = ProgressionBoundary(boundary)
        for policy in self.progression_policies:
            if policy.boundary is target:
                return policy
        return None

    def progression_policy_snapshot(self) -> list[dict]:
        return [policy.to_dict() for policy in self.progression_policies]

    def authorization_snapshot(self) -> list[dict]:
        return [gate.to_dict() for gate in self.authorization_gates]
