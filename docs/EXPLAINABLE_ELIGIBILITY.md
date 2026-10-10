# Explainable Eligibility — v0 Design Candidate

C3 design in progress.

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
