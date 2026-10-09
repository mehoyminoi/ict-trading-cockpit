# Trade Plan Progression Policy — v0 Design

**Status:** Accepted for v0 implementation
**Milestone:** C2 — Progression Policy model

## Purpose

C1 established boundary-aware Evidence Maturity for:

- Study -> Rehearsal
- Rehearsal -> Validation
- Validation -> Execution

C2 defines the next layer:

> What explicit requirements does the Trade Plan impose before a technician may cross a progression boundary?

Progression Policy is declarative, versioned Trade Plan data. C2 defines policy; C3 will evaluate eligibility.

## Core separation

Evidence Maturity = can the available evidence support a trustworthy decision?

Progression Policy = what requirements does this Trade Plan revision impose?

Eligibility = are those configured requirements satisfied right now?

A policy must never be silently inferred from evidence.

## Ownership and revisioning

Progression Policy is Trade Plan-owned because it changes what is permitted.

Therefore:

- published policy definitions are immutable inside a Trade Plan revision,
- changing a requirement requires a new Trade Plan revision,
- historical eligibility decisions must remain reconstructable against the policy that governed them,
- candidate Trade Plan revisions may carry different progression policy from the stable revision,
- changing policy must never rewrite what an older revision required.

The current published Trade Plan is Alpha 0.7 and does not contain authoritative progression policy. If a later implementation publishes real policy definitions into the default plan, that is a plan-owned semantic change and must create a new Trade Plan revision. This design does not choose the revision number.

## Boundary-level policy

The natural unit is one policy per upward progression boundary:

- Study -> Rehearsal
- Rehearsal -> Validation
- Validation -> Execution

Candidate identity:

Trade Plan revision + progression boundary

Moving downward remains frictionless and does not require a progression policy.

## Structured requirements

A policy should contain explicit requirements with stable IDs rather than prose-only guidance.

Conceptually:

ProgressionPolicyDefinition
- id
- boundary
- name
- description
- requirements
- rationale / operator guidance

Each requirement must be independently inspectable so C3 can later explain exactly what passed, failed, or could not be evaluated.

## Competency-scoped vs boundary/global requirements

Two scopes are useful.

**Competency-scoped requirements** apply to one named plan-owned competency. Examples include an Evidence Maturity condition, Competency State condition, required evidence purpose, or explicit human certification.

**Boundary/global requirements** apply to the overall progression decision. Examples include completion of a deliberate progression review or another future plan-owned prerequisite not logically attached to one competency.

This prevents global progression conditions from being awkwardly attached to arbitrary competencies.

## Competency continuity across Trade Plan revisions

A Trade Plan revision change does **not** automatically erase demonstrated competency.

The important question is whether the competency definition itself is materially the same and whether the surrounding plan changes create a new context that needs revalidation.

Accepted model:

### Unchanged competency definition

If competency C in rY is materially unchanged from competency C in rX:

- historical evidence from rX remains valid evidence of the same competency definition,
- the technician's Competency State does not automatically fall back merely because the whole Trade Plan revision changed,
- prior proficiency can remain intact as a statement about understanding/execution of that competency,
- the new Trade Plan may nevertheless require **context revalidation** before the competency contributes to higher-level eligibility under rY.

This means a technician can remain **Proficient** in the competency while rY's progression policy requires fresh Rehearsal or Validation evidence in the context of the new plan.

That is preferable to mutating Competency State merely to force revalidation.

Conceptually:

```text
Competency knowledge continuity
        remains intact
                +
new-plan contextual integration
        may require revalidation
                ↓
rY progression eligibility
```

Example:

- rX demonstrates strong proficiency in Draw on Liquidity,
- rY keeps the Draw on Liquidity definition unchanged,
- rY changes session process, model composition, or another interacting competency,
- Draw on Liquidity does **not** become "unlearned,"
- rY may require Replay/Rehearsal or Forward/Validation evidence showing the known skill integrates correctly with the changed system.

### Materially changed competency definition

If the competency definition materially changes:

- old evidence remains valid historical evidence for the old definition,
- old proficiency must not silently certify the new meaning,
- the new definition requires explicit continuity/mapping or renewed evidence,
- the correct resulting state depends on the nature of the change and should not be hardcoded as an automatic universal fallback.

A small refinement might justify Rehearsal or Validation. A fundamental redefinition might justify Study.

The system should preserve the distinction rather than blindly resetting every changed competency to the same rung.

### New competency

If rY adds a competency that did not exist in rX:

- no historical competency evidence is assumed,
- no proficiency state is inherited,
- evidence begins from the revision that defines the competency,
- any retrospective mapping must be explicit and provenance-bearing.

### Architectural consequence

Progression Policy should govern **what fresh evidence is required under the current Trade Plan**, while Competency State should continue to describe the technician's broader current skill state.

This avoids conflating:

```text
"I know this competency"
with
"I have validated this competency inside this revised system"
```

A future definition-level provenance/fingerprint mechanism should make unchanged-vs-changed competency identity machine-verifiable.

## Required competencies must be explicit

Do not assume every Trade Plan competency gates every progression boundary.

A policy should explicitly identify which competencies matter. This supports cases where:

- all foundational competencies are required,
- only a subset gates one boundary,
- a new competency begins as non-gating while evidence is gathered,
- different boundaries depend on different competencies.

A newly added competency must not silently become a blocker just because it exists in the catalog.

## Proposed v0 requirement kinds

### 1. Evidence Maturity State

A policy may deliberately require an accepted maturity state for a named competency and boundary.

The software must not assume that Decision-Usable Evidence is universally required. If that state is required, it is because the Trade Plan explicitly says so.

The C1 maturity-state layer remains removable. Future Trade Plan revisions may evolve away from this primitive if operator use shows the label is too evaluative.

### 2. Competency State

A policy may deliberately require one or more accepted Competency States.

No default state requirement is implied.

### 3. Evidence Purpose Present

A policy may require reviewed evidence from a specified purpose such as Study, Rehearsal, or Validation.

C2 does not invent sample counts, success rates, age windows, or other thresholds.

### 4. Human Certification

Some requirements cannot yet be safely inferred from structured evidence. A policy may require an explicit named human certification, such as confirming that contradictions were reviewed.

This is a first-class auditable requirement, not an invisible override.

## No arbitrary thresholds in C2

C2 defines policy vocabulary and ownership, not actual readiness criteria.

Do not invent rules such as:

- minimum 20 samples,
- 80 percent success rate,
- 30-day recency,
- 90 percent process adherence,
- three profitable weeks.

If a future Trade Plan adopts a numeric or temporal threshold, the value belongs in the versioned policy definition, never hidden in evaluator code.

## Requirement operators

A small explicit comparison vocabulary may be useful:

- IS
- IS_ONE_OF
- EXISTS
- DOES_NOT_EXIST
- AT_LEAST
- AT_MOST

Only operators required by accepted requirement kinds should be implemented. C2 should not become a generic rules engine or programming language.

## C3 evaluation vocabulary

C2 defines requirements; C3 evaluates them.

Candidate per-requirement outcomes for C3:

- Satisfied
- Not Satisfied
- Unknown / Cannot Evaluate
- Not Applicable

Unknown must never silently count as Satisfied.

Examples include missing structured context or competency-definition equivalence that cannot yet be machine verified.

## High-level eligibility remains separate

The existing substrate remains:

- AVAILABLE
- NOT CONFIGURED
- BLOCKED

Likely C3 semantics:

- no policy for boundary -> NOT CONFIGURED
- policy exists and all required conditions pass -> AVAILABLE
- policy exists and a required condition fails -> BLOCKED
- policy exists but a required condition cannot be evaluated -> not available with an explicit Unknown/Insufficient reason

C2 should preserve enough information for this explanation but should not implement the evaluator yet.

## Insufficient evidence vs regression vs temporary restriction

These are separate reasons.

- insufficient evidence means the progression requirement is not yet supported,
- regression means something previously satisfied is no longer satisfied,
- temporary restriction means today's operating conditions do not permit higher-risk operation,
- not configured means no policy exists.

Temporary news/risk/personal-condition restrictions do not belong inside progression policy. Regression/downgrade behavior belongs to C4.

## Development Direction relationship

Development Direction answers: What deliberate work should happen next?

Progression Policy answers: What must be true before the boundary may be crossed?

They must not rewrite one another.

A technician may have Development Direction = Validation while Rehearsal -> Validation eligibility is still blocked. Validation can still be the correct next development target even before permission to cross the boundary exists.

## Competency State relationship

Competency State remains mutable profile state:

- Not Assessed
- Under Study
- Rehearsal Needed
- Validation Needed
- Proficient

Progression Policy may reference Competency State, but it does not own or mutate it. C2 does not define when Competency State changes.

## Evidence Maturity dimensions

C1 intentionally made the six-dimensional profile more durable than the overall maturity label.

For v0, do not create a generic condition builder over all six dimensions because several dimensions are not yet normalized machine-evaluable facts. Consistency and Context Coverage include human notes, and Revision Relevance has a known provenance limitation.

The policy model should remain extensible enough to reference dimensions later without pretending they are already evaluable.

## Policy composition

Proposed v0 composition:

> Every listed gating requirement must be satisfied.

That means simple AND semantics.

Do not add weighted scoring, majority rules, or nested arbitrary boolean logic in v0. If a real Trade Plan later needs OR logic, add it deliberately after a concrete use case exists.

## Gating-only policy

Proposed v0:

Progression Policy contains gating requirements only.

Advisory or informational observations remain in Review / Development and Evidence Maturity. This gives every policy item a clear meaning: if it is in the policy, it matters to permission.

## Manual override

Proposed v0:

No manual progression override.

If overrides are introduced later, they should be explicit, reasoned, provenance-bearing, auditable, and distinct from actually satisfying a requirement.

## Candidate domain model

Conceptually:

ProgressionPolicyDefinition
- id
- boundary
- name
- description
- requirements

ProgressionRequirementDefinition
- id
- name
- requirement_kind
- competency_id, optional for global requirements
- operator
- expected_value
- description

Definitions should be immutable/frozen and owned by the published Trade Plan.

## Candidate v0 requirement-kind enum

- EVIDENCE_MATURITY_STATE
- COMPETENCY_STATE
- EVIDENCE_PURPOSE_PRESENT
- HUMAN_CERTIFICATION

These map to concepts already present, are operator-readable, and are enough to prove policy/evaluation separation.

No configured readiness rules are proposed yet.

## NOT CONFIGURED semantics

No ProgressionPolicyDefinition for a boundary means NOT CONFIGURED.

A ProgressionPolicyDefinition with zero requirements should be invalid, not automatically available. Otherwise an accidental empty policy could become an unintended permission grant.

## Policy validation

A published Trade Plan should reject malformed progression policy.

Candidate validations:

- unique policy IDs,
- at most one policy per progression boundary,
- recognized boundary,
- at least one requirement,
- unique requirement IDs within policy,
- referenced competency IDs exist in the same Trade Plan,
- requirement kind/operator/value combination is valid,
- no silent reference to an unknown competency.

## Alpha 0.7 and the first real policy

Two implementation steps should remain separate.

### C2 substrate implementation

Add immutable policy definition classes, validation, serialization/snapshot support, Trade Plan container support, and read-only rendering if useful.

This can be done without inventing actual readiness criteria.

### First configured progression policy

Choosing real progression requirements is a trading-process policy decision, not software plumbing.

It should happen only after the operator explicitly accepts the real requirements. Publishing those rules requires a new Trade Plan revision.

## Proposed C2 implementation boundary

If accepted, C2 implementation should include:

- ProgressionPolicyDefinition,
- ProgressionRequirementDefinition,
- the accepted minimal requirement-kind vocabulary,
- progression-boundary identity compatible with C1,
- validation against the Trade Plan competency catalog,
- serialization/snapshot support,
- Trade Plan support for zero or more boundary policies,
- read-only rendering of configured policy definitions,
- tests proving malformed and unknown references are rejected,
- tests proving zero policies preserves NOT CONFIGURED semantics.

Do not yet implement:

- eligibility evaluation,
- launcher enforcement,
- automatic promotion/demotion,
- regression handling,
- manual overrides,
- arbitrary numeric thresholds,
- generic expression engines,
- automatic Competency State changes,
- real Alpha 0.7 progression rules.

## C2 -> C3 handoff

C3 should combine:

Trade Plan Progression Policy
+ current evidence/governance state
-> per-requirement explanations
-> boundary eligibility result

It should answer which policy revision was evaluated, which boundary, which requirements applied, which passed, which failed, which were unknown, and why the resulting environment is available or unavailable.

## Operator confirmation questions

1. Should Progression Policy be strictly Trade Plan-owned and revisioned, with the first real configured policy requiring a new Trade Plan revision?
2. Should v0 use one policy per progression boundary, with explicit competency-scoped and boundary/global requirements?
3. Do the four proposed v0 requirement kinds make sense: Evidence Maturity State, Competency State, Evidence Purpose Present, and Human Certification?
4. Do you agree that C2 should build the policy substrate without inventing actual Alpha 0.7 readiness rules, and that we should separately decide the first real requirements before publishing a new Trade Plan revision?
5. Should v0 policy composition be simple ALL requirements must pass, with no weighting, majority rule, or arbitrary nested boolean logic?
6. Should Progression Policy contain gating requirements only, leaving advisory/non-gating observations in Review / Development?
7. Should an empty published policy be invalid, so it can never accidentally mean automatically available?
8. Do you agree with no manual progression override in v0?
9. For later C3, should an unevaluable required condition be treated conservatively as not available with an explicit Unknown/Insufficient reason rather than silently passing?
10. Does the split between C2 substrate implementation and later publication of the first real configured policy feel right?


## Progression policy as a learning-rate lever

Long term, progression policy is not only a safety gate. It is also a tunable learning-system lever.

The Cockpit should eventually make it possible to study:

- time spent from first exposure to usable competence,
- time between Study, Rehearsal, Validation, and Execution readiness,
- number and type of evidence observations needed before progression,
- regressions and revalidation events,
- competency families / genres that tend to learn similarly,
- whether prior mastery of related concepts shortens learning time for a new concept,
- marginal learning benefit from additional Study versus moving into Rehearsal or Validation,
- differences between technician-estimated readiness and policy/evidence outcomes.

The long-term aim is not to rush progression blindly. It is to understand the technician's learning curve well enough to allocate deliberate-practice time efficiently and recognize diminishing returns.

A useful future question is:

> For a new concept of this type, how long has it historically taken this technician to reach useful competence, and which practice sequence produced the fastest trustworthy progression?

This supports future KPI/analytics work around learning velocity and progression friction without changing C2 v0.

C2 must preserve stable IDs, revision provenance, requirement identity, and boundary identity so these analytics are possible later.

## Accepted operator decisions

Accepted on 2026-10-09:

1. Progression Policy is strictly Trade Plan-owned and revisioned.
2. v0 uses one policy per progression boundary with explicit competency-scoped and boundary/global requirements.
   - This is preferred because the boundary is the permission decision, while competency requirements are inputs to that decision. It avoids fragmenting one boundary decision across many independent competency policies.
3. v0 requirement kinds are:
   - Evidence Maturity State,
   - Competency State,
   - Evidence Purpose Present,
   - Human Certification.
4. C2 builds the policy substrate without inventing Alpha 0.7 readiness rules.
5. v0 composition is simple ALL/AND.
6. Progression Policy contains gating requirements only.
7. Empty published policies are invalid.
8. No manual progression override in v0.
9. A required condition that cannot be evaluated must not silently pass; C3 should treat it as not available with an explicit Unknown/Insufficient reason.
10. C2 substrate implementation and publication of the first real configured progression policy remain separate steps.

Additional accepted clarification:

- unchanged competency definitions may preserve prior proficiency across Trade Plan revisions,
- revised-plan context may still require fresh Rehearsal/Validation evidence before eligibility under the new plan,
- materially changed competency definitions require explicit revalidation/mapping rather than silent inheritance,
- new competencies do not inherit historical proficiency/evidence automatically,
- future analytics should treat progression rate and learning time as measurable system outputs, with eventual competency-family/genre comparisons and diminishing-returns analysis.
