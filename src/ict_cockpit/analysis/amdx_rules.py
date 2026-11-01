"""Versioned, scoped criteria over explicitly supplied facts.

First resolver: conjunctive typed predicates and explicit priority, unresolved
ties/unknowns. No universal weighting formula, provider mapping or trading rules.
"""
from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from math import isfinite

from ict_cockpit.analysis.amdx import (
    Anchor, Cycle, Role, XSubtype, aware, cycle_from_payload, infer_profile,
    payload, require_id, timestamp,
)


EVALUATION_REVISION = "amdx-priority-v1"
SCOPED_EVALUATION_REVISION = "amdx-priority-scoped-v2"
RESOLUTION_POLICY = "Cycle Profile Priority"
Scalar = str | bool | int | float


def scalar(value):
    if type(value) not in (str, bool, int, float) or (
        type(value) is float and not isfinite(value)
    ):
        raise ValueError("Evidence/condition value must be a finite scalar")


class Operator(str, Enum):
    EQ = "eq"
    GT = "gt"
    GE = "ge"
    LT = "lt"
    LE = "le"


class OutputKind(str, Enum):
    LOCAL_BEHAVIOR = "Local Behavior"
    ASSIGNED_ROLE = "Assigned Role"


@dataclass(frozen=True)
class Fact:
    id: str
    scope_id: str
    key: str
    value: Scalar
    unit: str
    available_at: datetime | None
    source_ref: str

    def __post_init__(self):
        for value in (self.id, self.scope_id, self.key, self.source_ref):
            require_id(value)
        scalar(self.value)
        if self.available_at is not None:
            aware(self.available_at)


@dataclass(frozen=True)
class QuartetScope:
    """Versioned positional input within the explicitly evaluated quartet.

    Strings retain fixed-identity semantics; no reserved string is reinterpreted.
    The owning definition's layer determines what Q1–Q4 mean.
    """
    position: int
    kind: str = "selected-quartet-quarter-v1"

    def __post_init__(self):
        if self.kind != "selected-quartet-quarter-v1":
            raise ValueError("Unsupported reusable quarter scope")
        if type(self.position) is not int or self.position not in range(1, 5):
            raise ValueError("Reusable quarter scope must select Q1 through Q4")

    def bind(self, cycle: Cycle) -> str:
        return cycle.quarters[self.position - 1].id


@dataclass(frozen=True)
class Condition:
    scope_id: str | QuartetScope
    key: str
    operator: Operator
    value: Scalar
    unit: str = ""

    def __post_init__(self):
        if isinstance(self.scope_id, dict):
            if set(self.scope_id) != {"kind", "position"}:
                raise ValueError("Malformed reusable quarter scope")
            object.__setattr__(self, "scope_id", QuartetScope(**self.scope_id))
        if not isinstance(self.scope_id, QuartetScope):
            require_id(self.scope_id)
        require_id(self.key)
        scalar(self.value)
        object.__setattr__(self, "operator", Operator(self.operator))
        if self.operator is not Operator.EQ and type(self.value) not in (int, float):
            raise ValueError("Ordered conditions require a numeric threshold")


@dataclass(frozen=True)
class Definition:
    id: str
    revision: str
    plan_revision: str
    publication: str
    layer: str
    target_position: int
    output_kind: OutputKind
    role: Role
    priority: int
    conditions: tuple[Condition, ...]
    rationale: str
    subtype: XSubtype | None = None

    def __post_init__(self):
        for value in (self.id, self.revision, self.plan_revision, self.layer, self.rationale):
            require_id(value)
        if self.publication not in ("Candidate", "Published"):
            raise ValueError("Definition must identify Candidate or Published status")
        if type(self.target_position) is not int or self.target_position not in range(1, 5):
            raise ValueError("Rule output needs an explicit quarter position")
        if type(self.priority) is not int or self.priority < 0:
            raise ValueError("Priority must be a nonnegative integer; smaller wins")
        object.__setattr__(self, "output_kind", OutputKind(self.output_kind))
        object.__setattr__(self, "role", Role(self.role))
        object.__setattr__(self, "conditions", tuple(self.conditions))
        if not self.conditions:
            raise ValueError("Criteria must declare at least one condition")
        if self.role in (Role.UNKNOWN, Role.NOT_APPLICABLE):
            raise ValueError("An output must propose a concrete role/behavior")
        if self.subtype is not None:
            object.__setattr__(self, "subtype", XSubtype(self.subtype))
            if self.role is not Role.X:
                raise ValueError("Only X has a subtype")


@dataclass(frozen=True)
class Result:
    rule_id: str
    rule_revision: str
    state: str
    target_quarter_id: str
    reasons: tuple[str, ...]
    fact_ids: tuple[str, ...]


@dataclass(frozen=True)
class Resolution:
    output_kind: OutputKind
    target_quarter_id: str
    state: str
    selected_rule_ids: tuple[str, ...]
    role: Role | None
    subtype: XSubtype | None
    reason: str


@dataclass(frozen=True)
class Evaluation:
    id: str
    run_id: str
    cycle: Cycle
    market_reference: datetime
    definitions: tuple[Definition, ...]
    facts: tuple[Fact, ...]
    results: tuple[Result, ...]
    resolutions: tuple[Resolution, ...]
    governing_rule_ids: tuple[str, ...]
    governing_state: str
    resolution_policy: str = RESOLUTION_POLICY
    revision: str = EVALUATION_REVISION

    def assigned_anchors(self) -> tuple[Anchor, ...]:
        """Rule anchors for a separate hypothesis, never replacements for manual ones."""
        definitions = {d.id: d for d in self.definitions}
        return tuple(Anchor(
            f"{self.id}:role:{r.target_quarter_id}", r.target_quarter_id, r.role,
            self.id, r.subtype, "Rule",
            ";".join(f"{i}@{definitions[i].revision}" for i in r.selected_rule_ids),
        ) for r in self.resolutions if r.output_kind is OutputKind.ASSIGNED_ROLE and r.state == "Resolved")

    def profile(self):
        # Global policy can prefer manipulation in Q2 over conflicting Q1
        # classification. Per-target proposals and all lower-priority traces
        # remain available. Local behavior never constrains the quartet.
        governing = tuple(d for d in self.definitions if d.id in self.governing_rule_ids)
        anchors = tuple(Anchor(
            f"{self.id}:governing:{d.id}", self.cycle.quarters[d.target_position - 1].id,
            d.role, self.id, d.subtype, "Rule", f"{d.id}@{d.revision}",
        ) for d in governing)
        result = infer_profile(self.cycle, anchors)
        if self.governing_state == "Unknown":
            return type(result)(result.candidates, result.roles, "Unresolved", result.reasons + (
                "An unknown criterion could govern the cycle under the selected priority policy.",
            ))
        return result

    def to_payload(self) -> dict:
        return {"version": 1, "evaluation": payload(self)}

    @classmethod
    def from_payload(cls, value: dict) -> "Evaluation":
        if (value.get("version") != 1 or value["evaluation"]["revision"] not in (EVALUATION_REVISION, SCOPED_EVALUATION_REVISION)
                or value["evaluation"]["resolution_policy"] != RESOLUTION_POLICY):
            raise ValueError("Unsupported AMDX evaluation revision")
        item = value["evaluation"]
        definitions = tuple(Definition(**{
            **d, "conditions": tuple(Condition(**c) for c in d["conditions"]),
        }) for d in item["definitions"])
        facts = tuple(Fact(**{**f, "available_at": timestamp(f["available_at"]) if f["available_at"] else None})
                      for f in item["facts"])
        result = evaluate(
            evaluation_id=item["id"], run_id=item["run_id"], cycle=cycle_from_payload(item["cycle"]),
            market_reference=timestamp(item["market_reference"]), definitions=definitions, facts=facts,
        )
        if result.to_payload() != value:
            raise ValueError("Stored result disagrees with retained definition/input basis")
        return result


def _condition(condition: Condition, facts: tuple[Fact, ...], reference: datetime):
    scoped = tuple(f for f in facts if f.scope_id == condition.scope_id and f.key == condition.key)
    eligible = tuple(f for f in scoped if f.available_at is not None and f.available_at <= reference)
    if not eligible:
        return "Unknown", "Input missing or unavailable at the explicit reference.", tuple(f.id for f in scoped)
    # Different capture revisions must be explicitly selected by the caller.
    if len(eligible) != 1:
        return "Unknown", "Competing input captures require explicit selection.", tuple(f.id for f in eligible)
    fact = eligible[0]
    numeric = type(fact.value) in (int, float) and type(condition.value) in (int, float)
    if fact.unit != condition.unit or not (numeric or type(fact.value) is type(condition.value)):
        return "Unknown", "Input units/type disagree with the declared condition.", (fact.id,)
    if condition.operator is Operator.EQ:
        matched = fact.value == condition.value
    else:
        matched = {
            Operator.GT: lambda: fact.value > condition.value,
            Operator.GE: lambda: fact.value >= condition.value,
            Operator.LT: lambda: fact.value < condition.value,
            Operator.LE: lambda: fact.value <= condition.value,
        }[condition.operator]()
    return ("Matched" if matched else "Not Matched"), "Declared typed comparison evaluated.", (fact.id,)


def evaluate(*, evaluation_id: str, run_id: str, cycle: Cycle, market_reference: datetime,
             definitions: tuple[Definition, ...], facts: tuple[Fact, ...]) -> Evaluation:
    require_id(evaluation_id)
    require_id(run_id)
    aware(market_reference)
    definitions, facts = tuple(definitions), tuple(facts)
    if len({d.id for d in definitions}) != len(definitions):
        raise ValueError("Compare definition revisions in separate evaluations")
    if len({f.id for f in facts}) != len(facts):
        raise ValueError("Fact revision identities must be unique")
    results = []
    for definition in definitions:
        target = cycle.quarters[definition.target_position - 1].id
        if definition.layer != cycle.layer:
            results.append(Result(definition.id, definition.revision, "Not Applicable", target,
                                  ("Definition layer does not apply to this quartet.",), ()))
            continue
        bound = tuple(replace(c, scope_id=c.scope_id.bind(cycle))
                      if isinstance(c.scope_id, QuartetScope) else c for c in definition.conditions)
        conditions = tuple(_condition(c, facts, market_reference) for c in bound)
        states = {c[0] for c in conditions}
        state = "Not Matched" if "Not Matched" in states else "Unknown" if "Unknown" in states else "Matched"
        reasons = tuple(
            (f"Selected quartet Q{source.scope_id.position} -> " if isinstance(source.scope_id, QuartetScope) else "")
            + f"{c.scope_id}/{c.key}: {r[1]}"
            for source, c, r in zip(definition.conditions, bound, conditions))
        ids = tuple(dict.fromkeys(i for c in conditions for i in c[2]))
        results.append(Result(definition.id, definition.revision, state, target, reasons, ids))
    resolutions = []
    keys = tuple(dict.fromkeys((d.output_kind, r.target_quarter_id) for d, r in zip(definitions, results)))
    for kind, target in keys:
        pairs = tuple((d, r) for d, r in zip(definitions, results)
                      if (d.output_kind, r.target_quarter_id) == (kind, target))
        matched = tuple(d for d, r in pairs if r.state == "Matched")
        unknown = tuple(d for d, r in pairs if r.state == "Unknown")
        if not matched:
            state = "Unknown" if unknown else (
                "Not Applicable" if all(r.state == "Not Applicable" for _, r in pairs) else "No Match")
            resolutions.append(Resolution(kind, target, state, (), None, None, "No governing matched criterion."))
            continue
        priority = min(d.priority for d in matched)
        top = tuple(d for d in matched if d.priority == priority)
        if any(d.priority <= priority for d in unknown):
            resolutions.append(Resolution(kind, target, "Unknown", (), None, None,
                                          "An unresolved criterion could equal or outrank the matched result."))
        elif (len({d.role for d in top}) != 1
              or len({d.subtype for d in top if d.subtype is not None}) > 1):
            resolutions.append(Resolution(kind, target, "Conflict", tuple(d.id for d in top), None, None,
                                          "Equal-priority criteria propose different outputs."))
        else:
            resolutions.append(Resolution(kind, target, "Resolved", tuple(d.id for d in top),
                                          top[0].role, next((d.subtype for d in top if d.subtype is not None), None),
                                          "Explicit priority selected this output; all rule traces are retained."))
    assigned = tuple((d, r) for d, r in zip(definitions, results)
                     if d.output_kind is OutputKind.ASSIGNED_ROLE)
    matched = tuple(d for d, r in assigned if r.state == "Matched")
    unknown = tuple(d for d, r in assigned if r.state == "Unknown")
    priority = min((d.priority for d in matched), default=None)
    governing = tuple(d.id for d in matched if d.priority == priority)
    governing_state = "Matched" if matched else "Unknown" if unknown else "No Match"
    if any(priority is None or d.priority <= priority for d in unknown):
        governing, governing_state = (), "Unknown"
    return Evaluation(evaluation_id, run_id, cycle, market_reference, definitions, facts,
                      tuple(results), tuple(resolutions), governing, governing_state,
                      revision=SCOPED_EVALUATION_REVISION if any(isinstance(c.scope_id, QuartetScope)
                          for d in definitions for c in d.conditions) else EVALUATION_REVISION)
