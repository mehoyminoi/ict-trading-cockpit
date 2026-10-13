"""Explicit later-Review pairings and replayable archives; no default or UI.

Observed profiles are interpretations, not price facts. Pairings never mutate
either channel, select a first/latest baseline, or affect process permissions.
"""
from dataclasses import dataclass
from datetime import datetime

from ict_cockpit.analysis.amdx import (
    Claim, InterpretationHistory, Role, aware, payload, require_id, timestamp,
)


ARCHIVE_VERSION = 1
PAIRING_POLICY = "explicit-profile-pair-v1"


class StaleComparison(ValueError):
    """The caller's inspected comparison head is no longer current."""


@dataclass(frozen=True)
class Comparison:
    id: str
    run_id: str
    branch_id: str
    cycle_id: str
    expected_claim_id: str | None
    observed_claim_id: str
    previous_comparison_id: str | None
    recorded_at: datetime
    market_reference: datetime
    policy: str = PAIRING_POLICY

    @property
    def scope(self) -> tuple[str, str, str]:
        return self.run_id, self.branch_id, self.cycle_id


@dataclass(frozen=True)
class ComparisonSummary:
    order_relation: str
    subtype_relation: str
    expected_timing: str
    observed_timing: str


def _cycle_timing(claim: Claim) -> str:
    if claim.market_reference < claim.cycle.quarters[0].start:
        return "Before cycle"
    if claim.market_reference >= claim.cycle.quarters[-1].end:
        return "After cycle"
    return "During cycle"


@dataclass(frozen=True)
class ReviewHistory:
    interpretations: InterpretationHistory = InterpretationHistory()
    comparisons: tuple[Comparison, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "comparisons", tuple(self.comparisons))
        # Recompute source claims under their original policies, including v1/v2.
        if InterpretationHistory.from_payload(self.interpretations.to_payload()) != self.interpretations:
            raise ValueError("Interpretation source cannot be replayed")
        known_ids = {c.id for c in self.interpretations.claims}
        heads: dict[tuple[str, str, str], Comparison] = {}
        for pair in self.comparisons:
            for value in (pair.id, pair.run_id, pair.branch_id, pair.cycle_id,
                          pair.observed_claim_id):
                require_id(value)
            if pair.expected_claim_id is not None:
                require_id(pair.expected_claim_id)
            if pair.previous_comparison_id is not None:
                require_id(pair.previous_comparison_id)
            if pair.policy != PAIRING_POLICY:
                raise ValueError("Unsupported comparison policy")
            if pair.id in known_ids:
                raise ValueError("Comparison identity cannot be reused")
            known_ids.add(pair.id)
            observed = self.claim(pair.observed_claim_id)
            if observed.channel != "Observed":
                raise ValueError("Observed basis must be an Observed claim")
            if pair.scope != (observed.run_id, observed.branch_id, observed.cycle.id):
                raise ValueError("Comparison scope disagrees with its observed basis")
            sources = [observed]
            if pair.expected_claim_id is not None:
                expected = self.claim(pair.expected_claim_id)
                if expected.channel != "Expected":
                    raise ValueError("Expected basis must be an Expected claim")
                if (expected.run_id, expected.branch_id, expected.cycle) != (
                    observed.run_id, observed.branch_id, observed.cycle
                ):
                    raise ValueError("Expected and observed bases require the same run, branch and quartet")
                sources.append(expected)
            aware(pair.recorded_at)
            aware(pair.market_reference)
            if any(pair.recorded_at < source.recorded_at for source in sources):
                raise ValueError("Comparison cannot be recorded before its source claims")
            previous = heads.get(pair.scope)
            if pair.previous_comparison_id != (previous.id if previous else None):
                raise ValueError("Comparison predecessor disagrees with its scope history")
            if previous and pair.recorded_at < previous.recorded_at:
                raise ValueError("Comparison recording time cannot move backward")
            heads[pair.scope] = pair

    def claim(self, claim_id: str) -> Claim:
        require_id(claim_id)
        claim = next((c for c in self.interpretations.claims if c.id == claim_id), None)
        if claim is None:
            raise ValueError("Comparison basis is absent from retained interpretation history")
        return claim

    def head(self, run_id: str, branch_id: str, cycle_id: str) -> Comparison | None:
        return next((p for p in reversed(self.comparisons)
                     if p.scope == (run_id, branch_id, cycle_id)), None)

    def with_interpretations(self, interpretations: InterpretationHistory) -> "ReviewHistory":
        if interpretations.claims[:len(self.interpretations.claims)] != self.interpretations.claims:
            raise ValueError("Existing interpretation history cannot be replaced or removed")
        return ReviewHistory(interpretations, self.comparisons)

    def record(self, *, comparison_id: str, expected_claim_id: str | None,
               observed_claim_id: str, expected_head_id: str | None,
               recorded_at: datetime, market_reference: datetime) -> "ReviewHistory":
        observed = self.claim(observed_claim_id)
        pair = Comparison(
            comparison_id, observed.run_id, observed.branch_id, observed.cycle.id,
            expected_claim_id, observed_claim_id, expected_head_id,
            recorded_at, market_reference,
        )
        existing = next((p for p in self.comparisons if p.id == comparison_id), None)
        if existing is not None:
            if existing != pair:
                raise ValueError("A comparison identity cannot be overwritten or reused")
            return self  # Original exact retry remains valid after later edits.
        head = self.head(*pair.scope)
        if expected_head_id != (head.id if head else None):
            raise StaleComparison("Comparison head changed; inspect it before a new action")
        return ReviewHistory(self.interpretations, self.comparisons + (pair,))

    def summarize(self, comparison_id: str) -> ComparisonSummary:
        pair = next((p for p in self.comparisons if p.id == comparison_id), None)
        if pair is None:
            raise ValueError("Unknown comparison identity")
        observed = self.claim(pair.observed_claim_id)
        if pair.expected_claim_id is None:
            return ComparisonSummary("No expected baseline", "Not comparable",
                                     "No expected baseline", _cycle_timing(observed))
        expected = self.claim(pair.expected_claim_id)
        timing = (_cycle_timing(expected), _cycle_timing(observed))
        if expected.inference.state != "Resolved" or observed.inference.state != "Resolved":
            return ComparisonSummary("Not comparable", "Not comparable", *timing)
        if expected.inference.candidates != observed.inference.candidates:
            return ComparisonSummary("Different order", "Not comparable", *timing)
        expected_x = next(r for r in expected.inference.roles if r.role is Role.X)
        observed_x = next(r for r in observed.inference.roles if r.role is Role.X)
        if expected_x.subtype is None:
            relation = "Expected subtype unresolved"
            if observed_x.subtype is None:
                relation = "Both subtypes unresolved"
        elif observed_x.subtype is None:
            relation = "Observed subtype unresolved"
        else:
            relation = "Same subtype" if expected_x.subtype == observed_x.subtype else "Different subtype"
        return ComparisonSummary("Same order", relation, *timing)

    def to_payload(self) -> dict:
        return {"version": ARCHIVE_VERSION, "policy": PAIRING_POLICY,
                "interpretations": self.interpretations.to_payload(),
                "comparisons": payload(self.comparisons)}

    @classmethod
    def from_payload(cls, value: dict) -> "ReviewHistory":
        if set(value) != {"version", "policy", "interpretations", "comparisons"} or (
            type(value["version"]) is not int or value["version"] != ARCHIVE_VERSION
            or value["policy"] != PAIRING_POLICY
        ):
            raise ValueError("Unsupported Review archive envelope")
        pairs = []
        for item in value["comparisons"]:
            if set(item) != set(Comparison.__dataclass_fields__):
                raise ValueError("Unsupported comparison fields")
            pairs.append(Comparison(**{**item, "recorded_at": timestamp(item["recorded_at"]),
                                       "market_reference": timestamp(item["market_reference"])}))
        return cls(InterpretationHistory.from_payload(value["interpretations"]), tuple(pairs))
