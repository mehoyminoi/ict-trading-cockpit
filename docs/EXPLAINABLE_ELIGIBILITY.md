# Explainable Eligibility — v0 Design

**Status:** Accepted for v0 implementation\n\nAll ten operator confirmation points were accepted on 2026-10-09.

## Purpose

C3 evaluates the current Trade Plan progression policy against current evidence/governance state and returns an explainable boundary decision.

Core separation:

- Evidence Maturity: can the evidence support a trustworthy decision?
- Progression Policy: what does this Trade Plan revision require?
- Eligibility: are those requirements satisfied now?

Eligibility is derived, not authored. No readiness score, weighting, or hidden policy is introduced.

## Result model

Top-level states remain:

- AVAILABLE
- NOT CONFIGURED
- BLOCKED

Requirement-level states are proposed as:

- SATISFIED
- NOT SATISFIED
- UNKNOWN / CANNOT EVALUATE

NOT APPLICABLE is omitted in v0 because every C2 policy item is an explicit gating requirement. If a requirement does not apply, it should not be in the policy.

Mapping:

- no policy -> NOT CONFIGURED
- policy + all requirements satisfied -> AVAILABLE
- policy + any unsatisfied or unknown requirement -> BLOCKED

Unknown never silently passes.

## Explanation categories

A blocked result should preserve why:

- REQUIREMENT_NOT_SATISFIED
- INSUFFICIENT_EVIDENCE
- CANNOT_EVALUATE
- HUMAN_CERTIFICATION_REQUIRED

Regression belongs to C4 because it requires comparison with prior eligibility. Temporary operating restrictions remain outside progression policy.

## Boundary mapping

- Study is the foundation environment.
- Replay corresponds to Study -> Rehearsal.
- Forward Test corresponds to Rehearsal -> Validation.
- Live corresponds to Validation -> Execution.

The progression boundary remains the canonical decision object.

## Derived state and provenance

Current eligibility should be calculated on demand from current policy plus current evidence/governance state rather than persisted as one mutable AVAILABLE/BLOCKED flag.

Future audit workflows may persist evaluation snapshots at meaningful events, but those snapshots should not become current truth.

## Requirement sources

Evidence Maturity State uses the boundary-aware competency maturity profile.

Competency State uses the current competency assessment.

Evidence Purpose Present uses reviewed competency evidence for the named competency and purpose.

Human Certification should use dedicated progression-certification state. Certification is not an override; it is the source for a requirement the Trade Plan deliberately made human-verifiable.

## Cross-revision evidence semantics

Competency knowledge can survive a Trade Plan revision while current-plan contextual validation may still be required.

For Evidence Purpose Present, proposed v0 scope is **CURRENT TRADE PLAN REVISION**.

Older evidence remains visible historical evidence and may still support broader competency knowledge, but it does not automatically satisfy a later revision's contextual-validation requirement.

Later, after competency-definition fingerprinting exists, policy can add broader explicit evidence scopes. Matching competency IDs alone is not enough to infer unchanged meaning.

For Evidence Maturity, a profile reviewed under an older Trade Plan revision should return UNKNOWN / CANNOT EVALUATE for a current-plan policy until it is reviewed under the current revision.

This does not reset Competency State.


## Accepted operator decisions

1. Top-level eligibility states remain AVAILABLE / NOT CONFIGURED / BLOCKED.
2. Requirement-level results use SATISFIED / NOT SATISFIED / UNKNOWN; NOT APPLICABLE is omitted in v0.
3. Current eligibility is derived on demand rather than persisted as mutable truth.
4. Evidence Purpose Present uses current-Trade-Plan-revision evidence by default.
5. Older-revision Evidence Maturity evaluates as UNKNOWN / needs current-plan review.
6. Human Certification gets dedicated, revision-bound, auditable state.
7. Missing required evidence is NOT SATISFIED / INSUFFICIENT_EVIDENCE; UNKNOWN is reserved for genuinely unevaluable cases.
8. A configured BLOCKED result prevents upward transition while downward movement remains frictionless.
9. NOT CONFIGURED remains non-restrictive for Alpha 0.7 until the first real progression policy is deliberately published.
10. Regression/demotion remains C4; temporary operating restrictions remain a separate layer.

## Human Certification candidate state

Candidate identity:

`Trade Plan revision + progression boundary + requirement ID`

Candidate fields:

- trade_plan_id
- trade_plan_revision
- boundary
- requirement_id
- confirmed
- note
- confirmed_at
- updated_at

Certification is tied to the exact policy revision context. It does not carry forward automatically, does not override failed requirements, and satisfies only its own HUMAN_CERTIFICATION requirement.

## Requirement evaluation semantics

Evidence Maturity State:
- current-revision profile + expected state -> SATISFIED
- current-revision profile + different state -> NOT SATISFIED
- no profile -> NOT SATISFIED / INSUFFICIENT_EVIDENCE
- older-revision profile only -> UNKNOWN / CANNOT_EVALUATE

Competency State:
- state matches -> SATISFIED
- state differs -> NOT SATISFIED
- no assessment -> NOT SATISFIED / INSUFFICIENT_EVIDENCE

Evidence Purpose Present:
- qualifying current-plan evidence exists -> SATISFIED
- none exists -> NOT SATISFIED / INSUFFICIENT_EVIDENCE
- source cannot be evaluated reliably -> UNKNOWN / CANNOT_EVALUATE

Human Certification:
- matching current-plan certification confirmed -> SATISFIED
- absent/not confirmed -> NOT SATISFIED / HUMAN_CERTIFICATION_REQUIRED
- source cannot be evaluated reliably -> UNKNOWN / CANNOT_EVALUATE

## Launcher behavior

Alpha 0.7 has no progression policy, so Replay, Forward Test, and Live remain NOT CONFIGURED and preserve current behavior.

For a future Trade Plan revision with configured policy:

- AVAILABLE permits the upward environment,
- BLOCKED prevents that upward transition and explains each failing or unknown requirement,
- the normal lower environment is recommended,
- moving downward remains frictionless.

This means the first actual progression restriction occurs only after a future Trade Plan deliberately publishes progression rules.

## C3 implementation boundary

C3 implementation should include:

- immutable requirement-result and eligibility-result domain objects,
- deterministic evaluation for all four C2 requirement kinds,
- environment-to-boundary mapping,
- current-plan revision provenance checks,
- dedicated Human Certification state and persistence,
- observed/expected values and source provenance in explanations,
- reason categories,
- integration with the existing environment eligibility substrate,
- launcher explanation of configured eligibility,
- configured BLOCKED behavior preventing upward launch,
- NOT CONFIGURED preserving Alpha 0.7 behavior,
- focused automated tests for satisfied, unsatisfied, unknown, and mixed results,
- tests proving no mutation of Competency State, Evidence Maturity, or Development Direction,
- focused manual smoke-test coverage.

Do not yet implement:

- actual Alpha 0.7 progression rules,
- a new Trade Plan revision with readiness criteria,
- regression/demotion behavior,
- temporary-pause composition,
- numeric readiness percentages,
- weighted scoring,
- overrides,
- automatic competency-definition equivalence,
- arbitrary sample-count or recency thresholds.
