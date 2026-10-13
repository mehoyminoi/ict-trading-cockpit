"""Coupled AMDX interpretations. Pure domain foundation, not a price classifier.

No legacy QT conversion, database mutation, clock fallback or authorization.
Callers provide explicit scope, identities and timestamps for accepted actions.
"""
from dataclasses import asdict, dataclass
from datetime import datetime, time, timedelta
from enum import Enum

from ict_cockpit.analysis.market_time import (
    MARKET_TIMEZONE, as_new_york, futures_trading_day_for,
    raw_qt_layer_contexts_for, session_for,
)


STRUCTURAL_REVISION = "amdx-xamd-v1"
PAYLOAD_VERSION = 3
LEGACY_POLICY = "accumulate-v1"
WORKING_POLICY = "revise-working-v1"
OBSERVED_POLICY = "revise-observed-v1"


class Role(str, Enum):
    A = "A"
    M = "M"
    D = "D"
    X = "X"
    UNKNOWN = "Unknown"
    NOT_APPLICABLE = "Not Applicable"


class XSubtype(str, Enum):
    CONTINUATION = "C"
    REVERSAL = "R"


class Profile(str, Enum):
    AMDX = "AMDX"
    XAMD = "XAMD"


ORDERS = {
    Profile.AMDX: (Role.A, Role.M, Role.D, Role.X),
    Profile.XAMD: (Role.X, Role.A, Role.M, Role.D),
}


def available_roles(position: int) -> tuple[Role, ...]:
    if type(position) is not int or position not in range(1, 5):
        raise ValueError("Quarter position must be 1 through 4")
    return tuple(r for r in (Role.A, Role.M, Role.D, Role.X)
                 if any(order[position - 1] is r for order in ORDERS.values()))


def aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("An explicit timezone-aware timestamp is required")
    return value


def timestamp(value: str) -> datetime:
    # Accept UTC Z on supported Python 3.10 as well as newer runtimes.
    return aware(datetime.fromisoformat(value.replace("Z", "+00:00")))


def canonical_timestamp(value: datetime) -> datetime:
    """Keep the exact written offset/instant, without ZoneInfo fold equality.

    Domain records already serialize ISO timestamps with numeric offsets.
    Match that representation in memory so valid repeated-hour values replay
    and compare correctly, without changing their serialized content.
    """
    return timestamp(aware(value).isoformat())


def require_id(value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("An explicit non-empty identity is required")


@dataclass(frozen=True)
class Quarter:
    id: str
    position: int
    label: str
    start: datetime
    end: datetime

    def __post_init__(self):
        require_id(self.id)
        if type(self.position) is not int or self.position not in range(1, 5):
            raise ValueError("Quarter position must be 1 through 4")
        object.__setattr__(self, "start", canonical_timestamp(self.start))
        object.__setattr__(self, "end", canonical_timestamp(self.end))
        if self.start >= self.end:
            raise ValueError("Quarter bounds must increase")


@dataclass(frozen=True)
class Cycle:
    id: str
    layer: str
    quarters: tuple[Quarter, ...]
    parent_quarter_id: str = ""

    def __post_init__(self):
        require_id(self.id)
        require_id(self.layer)
        object.__setattr__(self, "quarters", tuple(self.quarters))
        if tuple(q.position for q in self.quarters) != (1, 2, 3, 4):
            raise ValueError("A cycle must contain exactly four ordered quarters")
        if len({q.id for q in self.quarters}) != 4:
            raise ValueError("Quarter identities must be unique")
        if any(a.end != b.start for a, b in zip(self.quarters, self.quarters[1:])):
            raise ValueError("Cycle quarters must have contiguous bounds")

    def quarter_at(self, moment: datetime) -> Quarter | None:
        aware(moment)
        return next((q for q in self.quarters if q.start <= moment < q.end), None)


def intraday_cycles(moment: datetime) -> tuple[Cycle, Cycle] | tuple[()]:
    """Day/session quartets using the accepted NY clock, never higher-layer guesses.

    Closed weekends have no applicable active quartet. Friday remains a normal
    intraday day; this does not construct or classify the special weekly Q5.
    """
    aware(moment)
    local = as_new_york(moment)
    if session_for(local) == "Closed":
        return ()
    trading_date = futures_trading_day_for(local)
    start = datetime.combine(trading_date - timedelta(days=1), time(18), MARKET_TIMEZONE)
    day_id = f"day:{trading_date.isoformat()}"
    quarters = []
    for index in range(4):
        reference = start + timedelta(hours=6 * index)
        layer = next(x for x in raw_qt_layer_contexts_for(reference) if x["id"] == "day")
        quarters.append(Quarter(
            f"{day_id}:Q{index + 1}", index + 1, layer["active_child_label"],
            timestamp(layer["effective_start"]), timestamp(layer["effective_end"]),
        ))
    day = Cycle(day_id, "day", tuple(quarters))
    parent = day.quarter_at(local)
    assert parent is not None
    session_id = f"session:{parent.id}"
    children = tuple(Quarter(
        f"{session_id}:Q{i + 1}", i + 1, f"90m {i + 1}",
        parent.start + timedelta(minutes=90 * i),
        parent.start + timedelta(minutes=90 * (i + 1)),
    ) for i in range(4))
    return day, Cycle(session_id, "session", children, parent.id)


@dataclass(frozen=True)
class Anchor:
    id: str
    quarter_id: str
    role: Role
    source_ref: str
    subtype: XSubtype | None = None
    origin: str = "Technician"
    rule_revision: str = ""
    note: str = ""

    def __post_init__(self):
        require_id(self.id)
        require_id(self.quarter_id)
        require_id(self.source_ref)
        object.__setattr__(self, "role", Role(self.role))
        if self.subtype is not None:
            object.__setattr__(self, "subtype", XSubtype(self.subtype))
            if self.role is not Role.X:
                raise ValueError("Only X has a continuation/reversal subtype")
        if self.origin not in ("Technician", "Rule"):
            raise ValueError("Anchor origin must be Technician or Rule")
        if self.origin == "Rule":
            require_id(self.rule_revision)


@dataclass(frozen=True)
class ImpliedRole:
    quarter_id: str
    role: Role
    subtype: XSubtype | None
    origin: str


@dataclass(frozen=True)
class Inference:
    candidates: tuple[Profile, ...]
    roles: tuple[ImpliedRole, ...]
    state: str
    reasons: tuple[str, ...]
    structural_revision: str = STRUCTURAL_REVISION


def infer_profile(cycle: Cycle, anchors: tuple[Anchor, ...]) -> Inference:
    """Intersect active anchors within one quartet; never discard a conflict."""
    ids = {q.id for q in cycle.quarters}
    anchors = tuple(anchors)
    if any(a.quarter_id not in ids for a in anchors):
        raise ValueError("Anchor target is outside this quartet")
    if len({a.id for a in anchors}) != len(anchors):
        raise ValueError("Anchor identities must be unique")
    by_quarter = {q.id: tuple(a for a in anchors if a.quarter_id == q.id) for q in cycle.quarters}
    applicable = all(a.role is not Role.NOT_APPLICABLE for a in anchors)
    constraints = tuple(a for a in anchors if a.role not in (Role.UNKNOWN, Role.NOT_APPLICABLE))
    candidates = tuple(profile for profile, order in ORDERS.items() if all(
        a.role == order[next(q.position - 1 for q in cycle.quarters if q.id == a.quarter_id)]
        for a in constraints
    )) if applicable else ()
    subtype_conflict = any(len({a.subtype for a in values if a.subtype is not None}) > 1
                           for values in by_quarter.values())
    if not applicable:
        return Inference((), (), "Not Applicable", ("An explicit anchor excludes this quartet.",))
    if not candidates or subtype_conflict:
        return Inference(candidates, (), "Conflict", (
            "Active anchors do not support a consistent role/subtype profile; all inputs are retained.",
        ))
    roles = []
    for q in cycle.quarters:
        values = {ORDERS[p][q.position - 1] for p in candidates}
        role = next(iter(values)) if len(values) == 1 else Role.UNKNOWN
        explicit = tuple(a for a in by_quarter[q.id] if a.role is role and role is not Role.UNKNOWN)
        subtype = next((a.subtype for a in explicit if a.subtype is not None), None)
        origins = {a.origin for a in explicit}
        origin = (next(iter(origins)) if len(origins) == 1 else "Mixed") if explicit else (
            "Implied" if role is not Role.UNKNOWN else "Unresolved")
        roles.append(ImpliedRole(q.id, role, subtype, origin))
    return Inference(candidates, tuple(roles), "Resolved" if len(candidates) == 1 else "Unresolved", (
        "Roles are conditional structural consequences of the retained anchors, not price observations.",
    ))


@dataclass(frozen=True)
class Claim:
    id: str
    run_id: str
    branch_id: str
    channel: str
    cycle: Cycle
    anchors: tuple[Anchor, ...]
    inference: Inference
    recorded_at: datetime
    market_reference: datetime
    action_quarter_id: str
    action: str
    structural_revision: str = STRUCTURAL_REVISION
    action_policy: str = LEGACY_POLICY
    basis_claim_id: str | None = None
    retired_anchor_ids: tuple[str, ...] = ()
    applicability: tuple[Anchor, ...] = ()
    action_anchor: Anchor | None = None

    def __post_init__(self):
        object.__setattr__(self, "recorded_at", canonical_timestamp(self.recorded_at))
        object.__setattr__(self, "market_reference", canonical_timestamp(self.market_reference))


def claim_payload(claim: Claim) -> dict:
    value = payload(claim)
    if claim.action_policy == LEGACY_POLICY:
        for key in ("action_policy", "basis_claim_id", "retired_anchor_ids", "applicability", "action_anchor"):
            value.pop(key)
    return value


@dataclass(frozen=True)
class InterpretationHistory:
    claims: tuple[Claim, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "claims", tuple(self.claims))
        if len({c.id for c in self.claims}) != len(self.claims):
            raise ValueError("Claim identities must be unique")

    def _validate_action(self, *, claim_id: str, run_id: str, branch_id: str, channel: str,
               cycle: Cycle, quarter_id: str, anchor: Anchor | None,
               recorded_at: datetime, market_reference: datetime) -> Claim | None:
        for value in (claim_id, run_id, branch_id):
            require_id(value)
        aware(recorded_at)
        aware(market_reference)
        if channel not in ("Expected", "Observed"):
            raise ValueError("Channel must be Expected or Observed")
        if quarter_id not in {q.id for q in cycle.quarters}:
            raise ValueError("Action target is outside this quartet")
        if anchor is not None and (anchor.quarter_id != quarter_id or anchor.origin != "Technician"):
            raise ValueError("This action accepts an explicit technician anchor for its pinned target")
        if any(c.id == claim_id for c in self.claims):
            raise ValueError("Claim identity already exists")
        previous = next((c for c in reversed(self.claims) if (
            c.run_id, c.branch_id, c.channel, c.cycle.id
        ) == (run_id, branch_id, channel, cycle.id)), None)
        if any(c.cycle.id == cycle.id and c.cycle != cycle for c in self.claims):
            raise ValueError("Stable cycle identity cannot be reused with different bounds")
        if previous and recorded_at < previous.recorded_at:
            raise ValueError("Recorded action time cannot move backward within a working scope")
        if anchor is not None and any(a.id == anchor.id for c in self.claims for a in c.anchors + c.applicability):
            raise ValueError("A new accepted choice needs a new anchor revision identity")
        return previous

    def accept(self, **kwargs) -> "InterpretationHistory":
        """Original accumulation policy; retained for historical replay/analytical use."""
        previous = self._validate_action(**kwargs)
        if previous and previous.action_policy != LEGACY_POLICY:
            raise ValueError("Legacy accumulation cannot follow a versioned revision; use the scoped revision action")
        claim_id, run_id, branch_id, channel = (kwargs[k] for k in ("claim_id", "run_id", "branch_id", "channel"))
        cycle, quarter_id, anchor = (kwargs[k] for k in ("cycle", "quarter_id", "anchor"))
        recorded_at, market_reference = (kwargs[k] for k in ("recorded_at", "market_reference"))
        active = tuple(a for a in (previous.anchors if previous else ()) if a.quarter_id != quarter_id)
        if anchor is not None:
            active += (anchor,)
        claim = Claim(claim_id, run_id, branch_id, channel, cycle, active,
                      infer_profile(cycle, active), recorded_at, market_reference,
                      quarter_id, "Accept" if anchor else "Clear")
        return InterpretationHistory(self.claims + (claim,))

    def revise_working(self, *, clear_applicability: bool = False, **kwargs) -> "InterpretationHistory":
        return self._revise(WORKING_POLICY, clear_applicability=clear_applicability, **kwargs)

    def revise_observed(self, *, clear_applicability: bool = False, **kwargs) -> "InterpretationHistory":
        return self._revise(OBSERVED_POLICY, clear_applicability=clear_applicability, **kwargs)

    def _revise(self, policy: str, *, clear_applicability: bool = False, **kwargs) -> "InterpretationHistory":
        previous = self._validate_action(**kwargs)
        channel = "Expected" if policy == WORKING_POLICY else "Observed"
        if policy not in (WORKING_POLICY, OBSERVED_POLICY) or kwargs["branch_id"] != "working" or kwargs["channel"] != channel:
            raise ValueError(f"Revisions require the manual {channel}/working scope")
        if type(clear_applicability) is not bool:
            raise ValueError("clear_applicability must be a boolean")
        cycle, quarter_id, anchor = (kwargs[k] for k in ("cycle", "quarter_id", "anchor"))
        if clear_applicability and anchor is not None:
            raise ValueError("Clearing applicability cannot also assign a phase")
        before = previous.anchors + previous.applicability if previous else ()
        if any(a.origin != "Technician" for a in before):
            raise ValueError("Working revision cannot rewrite a mixed rule/technician basis")
        applicability = tuple(a for a in before if a.role is Role.NOT_APPLICABLE)
        active = tuple(a for a in before if a.role is not Role.NOT_APPLICABLE)
        if clear_applicability:
            applicability = ()
        elif anchor is not None and anchor.role is Role.NOT_APPLICABLE:
            active, applicability = (), (anchor,)
        else:
            active = tuple(a for a in active if a.quarter_id != quarter_id)
            if anchor is not None:
                if anchor.role is not Role.UNKNOWN:
                    position = next(q.position for q in cycle.quarters if q.id == quarter_id)
                    if anchor.role not in available_roles(position):
                        raise ValueError("Phase is not structurally valid at this quarter position")
                    order = next(order for order in ORDERS.values() if order[position - 1] is anchor.role)
                    positions = {q.id: q.position - 1 for q in cycle.quarters}
                    active = tuple(a for a in active if a.role is Role.UNKNOWN or a.role is order[positions[a.quarter_id]])
                    applicability = ()
                active += (anchor,)
        # Identity/time are metadata, not a reason to repeat an unchanged judgment.
        def meaning(anchors):
            return sorted((a.quarter_id, a.role.value, a.subtype.value if a.subtype else "",
                           a.source_ref, a.origin, a.rule_revision, a.note) for a in anchors)
        if meaning(before) == meaning(active + applicability):
            return self
        inference = infer_profile(cycle, active + applicability)
        retained = {a.id for a in active + applicability}
        claim = Claim(kwargs["claim_id"], kwargs["run_id"], kwargs["branch_id"], kwargs["channel"],
                      cycle, active, inference, kwargs["recorded_at"], kwargs["market_reference"],
                      quarter_id, "ClearApplicability" if clear_applicability else (
                          "ReviseWorking" if policy == WORKING_POLICY else "ReviseObserved") if anchor else (
                          "ClearWorking" if policy == WORKING_POLICY else "ClearObserved"),
                      action_policy=policy, basis_claim_id=previous.id if previous else None,
                      retired_anchor_ids=tuple(a.id for a in before if a.id not in retained),
                      applicability=applicability, action_anchor=anchor)
        return InterpretationHistory(self.claims + (claim,))

    def to_payload(self) -> dict:
        version = 3 if any(c.action_policy == OBSERVED_POLICY for c in self.claims) else (
            2 if any(c.action_policy == WORKING_POLICY for c in self.claims) else 1)
        return {"version": version, "claims": [claim_payload(c) for c in self.claims]}

    @classmethod
    def from_payload(cls, value: dict) -> "InterpretationHistory":
        if value.get("version") not in (1, 2, 3):
            raise ValueError("Unsupported AMDX history payload version")
        claims = []
        for item in value["claims"]:
            if item["structural_revision"] != STRUCTURAL_REVISION:
                raise ValueError("Unsupported structural revision; historical claims cannot be reinterpreted")
            cycle = cycle_from_payload(item["cycle"])
            anchors = tuple(Anchor(**a) for a in item["anchors"])
            policy = item.get("action_policy", LEGACY_POLICY)
            if policy not in (LEGACY_POLICY, WORKING_POLICY, OBSERVED_POLICY) or (
                policy == WORKING_POLICY and value["version"] < 2
            ) or (policy == OBSERVED_POLICY and value["version"] < 3):
                raise ValueError("Unsupported action policy/history version")
            applicability = tuple(Anchor(**a) for a in item.get("applicability", ()))
            inference = infer_profile(cycle, anchors + applicability)
            if payload(inference) != item["inference"]:
                raise ValueError("Stored inference disagrees with its retained structural basis")
            claim = Claim(item["id"], item["run_id"], item["branch_id"], item["channel"],
                          cycle, anchors, inference, timestamp(item["recorded_at"]),
                          timestamp(item["market_reference"]), item["action_quarter_id"],
                          item["action"], item["structural_revision"], policy,
                          item.get("basis_claim_id"), tuple(item.get("retired_anchor_ids", ())),
                          applicability, Anchor(**item["action_anchor"]) if item.get("action_anchor") else None)
            # Validate the action transcript rather than accepting inconsistent active snapshots.
            action_anchor = (next((a for a in anchors if a.quarter_id == claim.action_quarter_id), None)
                             if policy == LEGACY_POLICY else claim.action_anchor)
            allowed = (("Accept", "Clear") if policy == LEGACY_POLICY else
                       ("ReviseWorking", "ClearWorking", "ClearApplicability") if policy == WORKING_POLICY else
                       ("ReviseObserved", "ClearObserved", "ClearApplicability"))
            if claim.action not in allowed or (claim.action in ("Accept", "ReviseWorking", "ReviseObserved")) != (action_anchor is not None):
                raise ValueError("Invalid stored action")
            arguments = dict(
                claim_id=claim.id, run_id=claim.run_id, branch_id=claim.branch_id,
                channel=claim.channel, cycle=cycle, quarter_id=claim.action_quarter_id,
                anchor=action_anchor, recorded_at=claim.recorded_at, market_reference=claim.market_reference,
            )
            history = cls(tuple(claims))
            updated = (history.accept(**arguments) if policy == LEGACY_POLICY else
                       (history.revise_working if policy == WORKING_POLICY else history.revise_observed)(
                           **arguments, clear_applicability=claim.action == "ClearApplicability"))
            if len(updated.claims) != len(claims) + 1 or updated.claims[-1] != claim or set(claim_payload(claim)) != set(item):
                raise ValueError("Stored profile snapshot disagrees with action history")
            claims.append(claim)
        return cls(tuple(claims))


def payload(value):
    """Detached JSON-compatible snapshot; no live mutable containers are exposed."""
    if hasattr(value, "__dataclass_fields__"):
        return payload(asdict(value))
    if isinstance(value, datetime):
        return aware(value).isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: payload(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [payload(item) for item in value]
    return value


def cycle_from_payload(value: dict) -> Cycle:
    return Cycle(value["id"], value["layer"], tuple(Quarter(
        q["id"], q["position"], q["label"], timestamp(q["start"]), timestamp(q["end"]),
    ) for q in value["quarters"]), value["parent_quarter_id"])
