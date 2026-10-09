# Evidence Maturity Profile — v0 Design

**Status:** Accepted for v0 implementation  
**Milestone:** C — Evidence Maturity and progression governance

## Purpose

Milestone B completed the human synthesis chain:

```text
Evidence
  ↓
Competency Synthesis
  ↓
Cross-Run Observation
  ↓
Development Direction
  ↓
Targeted Study routing
```

Milestone C introduces governance over that evidence without collapsing evidence, competency state, progression policy, and eligibility into one score.

The first question is:

> How much confidence should we place in the available evidence for this competency and for the next progression decision?

The proposed answer is an **Evidence Maturity Profile**, not a readiness percentage.

---

## Core principle

Evidence Maturity is about the **quality and decision-usefulness of the evidence set**.

It is not:

- how good the technician is,
- whether the competency is proficient,
- whether the next environment is authorized,
- whether a trade is authorized,
- a P&L score,
- a hidden probability of success.

A technician can have strong skill but immature evidence because the evidence is too sparse, too old, too narrow, or collected in the wrong environment.

A technician can also have a large amount of evidence that is mature enough to support a decision while the evidence itself shows that advancement is not yet appropriate.

This distinction is important:

```text
Evidence Maturity
= can this evidence set support a trustworthy decision?

Competency State
= where the skill currently sits in the training ladder

Progression Policy
= what evidence/conditions the Trade Plan requires

Eligibility
= whether those requirements are currently satisfied
```

---

## Evidence Maturity should be a profile, not one number

A single maturity percentage would hide why the evidence is or is not decision-useful.

The proposed v0 profile has six dimensions:

1. **Volume / Sample Depth**
2. **Environment Relevance**
3. **Recency**
4. **Consistency**
5. **Context Coverage**
6. **Revision Relevance**

These dimensions are inspectable separately.

No weighted composite score is proposed.

---

## 1. Volume / Sample Depth

Question:

> Is there enough reviewed evidence to avoid making a decision from one or two isolated examples?

Possible descriptive inputs:

- total evidence records,
- records by Study / Rehearsal / Validation,
- number of distinct Trading Runs,
- date span of the evidence.

Important guardrail:

More records do not automatically mean stronger evidence.

Ten nearly identical Study examples are not equivalent to ten varied, realistic Validation observations.

No minimum sample threshold is defined in v0.

---

## 2. Environment Relevance

Question:

> Was the evidence gathered in an environment appropriate to the decision being considered?

The ladder is:

```text
Study       → recognition / isolated component work
Rehearsal   → integration under Replay
Validation  → live unfolding information without normal capital risk
Execution   → capital at risk
```

Evidence collected at a lower rung remains useful, but it may not be sufficient evidence for a higher-rung decision.

Example:

- strong Study evidence can support moving toward Rehearsal,
- strong Study evidence alone should not silently certify Live readiness,
- Validation evidence is especially relevant to a later Execution decision.

This is why Evidence Maturity is partly **decision-relative**.

---

## 3. Recency

Question:

> Is the evidence recent enough to represent the technician's current process and skill?

Possible descriptive inputs:

- newest evidence date,
- oldest evidence date,
- time since newest evidence,
- recent-vs-older evidence distribution.

Do not automatically declare evidence stale in v0.

A future Trade Plan policy may define recency requirements.

---

## 4. Consistency

Question:

> Does the reviewed evidence tell a reasonably coherent story, or is it materially mixed/conflicted?

Inputs may include:

- Study Outcome distribution,
- Cross-Run Observation,
- repeated supporting evidence,
- unresolved contradictory observations.

Important guardrail:

The Cockpit must not infer "consistent" merely because several evidence rows share the same Study Outcome.

For v0, consistency is primarily a **human-reviewed interpretation**, supported by descriptive evidence.

---

## 5. Context Coverage

Question:

> Has the competency been observed across enough relevant contexts to avoid overfitting the conclusion to one narrow condition?

Possible contexts can eventually include:

- session,
- market regime,
- volatility condition,
- time/QT context,
- model/playbook context,
- instrument,
- news/distortion context.

v0 should only use context that is already reliably structured.

Do not invent a universal list of required market conditions.

Coverage requirements belong to future Trade Plan progression policy.

---

## 6. Revision Relevance

Question:

> Does the evidence still correspond to the competency definition and Trade Plan meaning being evaluated?

This dimension must respect stable-vs-candidate revision isolation.

Whole Trade Plan revision mismatch alone is not enough to declare evidence irrelevant.

The important distinction is whether the **competency definition itself** changed.

Current limitation:

The Cockpit does not yet persist a competency-definition fingerprint/revision independent of the whole Trade Plan revision.

Therefore v0 may show Trade Plan revision provenance and an explicit limitation, but must not pretend it can automatically determine semantic equivalence across changed definitions.

A later provenance slice may add competency-definition identity/fingerprint.

---

## Decision-relative maturity

Evidence Maturity should not become one global "mature / immature" label detached from the decision being made.

The same evidence set may be:

- sufficiently useful to justify more Replay,
- insufficient to justify Forward Validation,
- entirely irrelevant to a Live-capital authorization question.

Therefore the long-term model should evaluate maturity against a **progression boundary** or **decision context**.

Candidate boundaries:

```text
Study -> Rehearsal
Rehearsal -> Validation
Validation -> Execution
```

For v0, the profile is explicitly evaluated against a selected **progression boundary / decision context** even though the profile itself does not make the progression decision.

---

## Proposed v0 maturity states

Avoid a numeric score.

For the overall profile, propose a small human-governance state:

- **Not Assessed**
- **Insufficient Evidence**
- **Developing Evidence**
- **Decision-Usable Evidence**

These labels describe whether the evidence set can support a decision.

They do **not** say what the decision should be.

Example:

```text
Evidence Maturity:
Decision-Usable Evidence

Cross-Run Observation:
"Session context remains inconsistent in London."

Development Direction:
Rehearsal
```

This means:

> There is enough trustworthy evidence to make a decision, and that evidence currently supports more Rehearsal.

It does **not** mean:

> The technician is ready to advance.

### Removability guardrail

The four maturity states are accepted for v0, but they must remain a **removable human-governance layer**, not a load-bearing readiness mechanism.

Architectural requirements:

- the six-dimensional profile remains meaningful without the overall state,
- `maturity_state` is human-authored and may be optional/unset,
- descriptive facts do not depend on the state,
- Cross-Run Observation and Development Direction do not depend on the state,
- no progression policy should become irreversibly coupled to the state before operator use validates it,
- if the labels later feel too evaluative, the UI can hide/remove them while retaining the underlying dimensions, notes, and evidence provenance.

This makes trying the labels inexpensive rather than an architectural pivot.

---

## Human judgment vs derived facts

The profile should distinguish:

### Derived/descriptive facts

Examples:

- 14 reviewed records,
- 6 Study / 5 Rehearsal / 3 Validation,
- newest evidence 8 days ago,
- three Trade Plan revisions represented.

### Human maturity judgment

Examples:

- current maturity state,
- maturity note,
- consistency interpretation,
- known gaps,
- unresolved contradictions.

The Cockpit may calculate descriptive facts.

It must not silently convert those facts into a maturity judgment unless a future explicit policy defines the rule.

---

## Relationship to Cross-Run Observation

Cross-Run Observation remains:

> What seems to be happening?

Evidence Maturity adds:

> How trustworthy/useful is the evidence set supporting that interpretation?

Example:

```text
Cross-Run Observation
"External draw recognition is stable in Study and Replay,
but Forward examples remain sparse."

Evidence Maturity
Developing Evidence

Maturity note
"Replay evidence is coherent, but only two Forward observations exist."

Development Direction
Validation
```

This creates a clean IF/THEN chain:

```text
IF the evidence says X
AND the evidence is mature enough for decision Y
THEN apply the explicit progression policy for boundary Y
```

The policy itself remains a later Milestone C slice.

---

## Relationship to progression policy

Evidence Maturity does not define progression requirements.

A future Trade Plan progression rule may say something like:

```text
For Rehearsal -> Validation:
- Evidence Maturity must be Decision-Usable
- relevant Rehearsal evidence must exist
- no unresolved critical failure mode may be present
- required competencies must satisfy their configured criteria
```

That rule is **Trade Plan-owned policy** and therefore revisioned.

The Evidence Maturity Profile is mutable evidence/governance state.

Do not hardcode progression thresholds into the profile.

---

## Relationship to eligibility

Eligibility remains an output of explicit policy.

```text
Evidence
  ↓
Evidence Maturity Profile
  ↓
Trade Plan progression policy
  ↓
Eligibility result
```

Possible eligibility states already established:

- AVAILABLE
- NOT CONFIGURED
- BLOCKED

Future unavailable reasons should remain distinguishable:

- eligibility regression,
- temporary pause,
- insufficient evidence.

Evidence Maturity may explain **insufficient evidence**, but must not absorb temporary risk/news/personal-condition restrictions.

---

## Proposed v0 persistence

One current mutable Evidence Maturity Profile per:

```text
Trade Plan + competency + progression boundary
```

Candidate fields:

- trade_plan_id,
- trade_plan_revision,
- competency_id,
- maturity_state,
- maturity_note,
- consistency_note,
- known_gap_note,
- progression_boundary / decision_context (required in v0),
- source = Review / Development,
- created_at,
- updated_at.

Descriptive measurements should be derived from evidence when possible rather than duplicated into the persisted profile.

The progression boundary is part of the identity from v0. This prevents one global maturity judgment from being reused across materially different decisions such as Study -> Rehearsal and Validation -> Execution.

---

## UI proposal

Extend the existing Competency Synthesis area without turning Review / Development into a dashboard.

For one selected competency:

```text
Competency Synthesis
────────────────────────────────

Evidence coverage
Study 6 · Rehearsal 5 · Validation 2

Cross-Run Observation
"Recognition is stable in Replay; live-flow examples remain sparse."

Development Direction
Validation

Evidence Maturity
Developing Evidence

Why
"Replay evidence is coherent, but only two Validation observations exist."

Profile
Volume / Depth        descriptive facts
Environment Relevance descriptive facts
Recency               descriptive facts
Consistency           human-reviewed note
Context Coverage       descriptive facts + known gaps
Revision Relevance    provenance + limitation
```

This should remain compact and scrollable.

No traffic-light readiness dashboard is proposed.

---

## v0 implementation boundary

If accepted, implement first:

- Evidence Maturity domain model,
- one persisted current profile per Trade Plan + competency + progression boundary,
- non-numeric maturity state if accepted,
- human maturity note,
- descriptive evidence facts already supported by current records,
- explicit profile dimensions,
- clear distinction between derived facts and human judgment,
- Review / Development display/editing,
- restart persistence,
- no automatic progression/eligibility change.

Do not yet implement:

- Trade Plan progression thresholds,
- automatic advancement,
- automatic demotion,
- Live lockout,
- composite readiness percentage,
- hidden weighted score,
- machine-inferred maturity state,
- competency-definition fingerprinting unless separately approved,
- broad analytics/dashboarding.

---

## Milestone C sequencing

Proposed Milestone C order:

```text
C1 Evidence Maturity Profile
        ↓
C2 Progression Policy model
        ↓
C3 Explainable Eligibility evaluation
        ↓
C4 Regression / downgrade semantics
        ↓
C5 Operator-loop integration and guardrails
```

This sequence keeps evidence confidence separate from rules and rules separate from permission.

---

## Operator confirmation questions

1. Does **Evidence Maturity Profile** feel like the right name?
2. Do the six dimensions — Volume / Sample Depth, Environment Relevance, Recency, Consistency, Context Coverage, Revision Relevance — capture the right concerns?
3. Should v0 include the four human maturity states (**Not Assessed / Insufficient Evidence / Developing Evidence / Decision-Usable Evidence**), or should v0 remain dimension-only with no overall maturity label?
4. Should maturity be stored globally per competency first, or should it be explicitly tied to a progression boundary such as Study -> Rehearsal / Rehearsal -> Validation / Validation -> Execution from the start?
5. Does the separation **Evidence Maturity = can the evidence support a trustworthy decision** versus **Progression Policy = what decision rule applies** feel correct?
6. Is the proposed Milestone C sequence C1 -> C2 -> C3 -> C4 -> C5 appropriate?


## Operator acceptance

Accepted on 2026-10-09.

Confirmed:

- **Evidence Maturity Profile** is the accepted name.
- The six dimensions are accepted:
  - Volume / Sample Depth,
  - Environment Relevance,
  - Recency,
  - Consistency,
  - Context Coverage,
  - Revision Relevance.
- v0 includes the four human maturity states:
  - Not Assessed,
  - Insufficient Evidence,
  - Developing Evidence,
  - Decision-Usable Evidence.
- The maturity-state layer must remain removable if real use shows that it feels too evaluative.
- Evidence Maturity is boundary-aware from the start.
- v0 profile identity is **Trade Plan + competency + progression boundary**.
- Evidence Maturity answers whether the evidence can support a trustworthy decision; Progression Policy defines what rule applies to that decision.
- Milestone C sequencing C1 -> C2 -> C3 -> C4 -> C5 is accepted.
