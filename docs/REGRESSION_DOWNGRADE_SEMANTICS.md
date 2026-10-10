# Regression / Downgrade Semantics — v0 Design Candidate

**Status:** Design candidate for operator review  
**Milestone:** C4 — Regression / downgrade semantics

## Purpose

C3 answers:

> Is this progression boundary available **now**, under the current Trade Plan policy, and why?

C4 must answer a different question:

> What does it mean when a boundary that was previously cleared is no longer currently supported?

The critical guardrail is:

> **Loss of current eligibility is not automatically loss of competency.**

A technician may retain skill while needing fresh contextual validation, additional evidence, or a deliberate lower-risk operating period.

---

## Four concepts that must remain separate

### 1. Competency State

What the technician currently knows/can do at the skill level.

Example:

`Draw on Liquidity = Proficient`

Competency State is mutable human/governance state. C4 must not automatically rewrite it because eligibility changed.

### 2. Current Eligibility

Whether the current Trade Plan's requirements for one progression boundary are satisfied now.

C3 derives this on demand.

### 3. Progression Attainment

A historical fact:

> This boundary was deliberately cleared and the technician actually attained/entered the higher rung under a specific Trade Plan revision.

Attainment is provenance. It should not disappear merely because current eligibility later changes.

### 4. Development Response

What should happen next:

- Study,
- Rehearsal,
- Validation,
- Monitor / Gather Evidence,
- No Active Focus.

Development Direction remains human-reviewed and must not be silently rewritten by C4.

---

## Recommended terminology

Avoid using **downgrade** as a generic synonym for every loss of access.

Use more precise language:

- **Eligibility loss** — the current policy result changed from AVAILABLE to BLOCKED.
- **Revalidation required** — previously learned material must be demonstrated in a new/current context.
- **Regression review** — a previously attained boundary has lost current support and requires interpretation.
- **Confirmed competency regression** — human-reviewed conclusion that the underlying skill itself has materially deteriorated.
- **Voluntary step-down** — technician deliberately chooses a lower rung despite higher access being available.
- **Temporary operating pause** — market/risk/personal/account conditions restrict operation; separate from progression eligibility.

---

## Objective transition vs interpreted cause

C4 should distinguish what the system can know mechanically from what requires judgment.

### Mechanically detectable

If the system has a trusted prior eligibility snapshot/attainment record:

```text
same Trade Plan revision
same boundary
same published policy
previously AVAILABLE
currently BLOCKED
```

then the system can say:

> **Eligibility loss detected.**

It cannot automatically say:

> **Competency regressed.**

### Human-reviewed interpretation

The technician may later classify the loss as:

- Confirmed Competency Regression
- Evidence / Governance Reassessment
- Revalidation Required
- Certification Withdrawn
- Other / Needs Study

Temporary operating restrictions remain outside this classification because they are not progression-policy failures.

---

## Why historical attainment is needed

C3 intentionally does not persist a mutable current-eligibility flag.

C4 nevertheless needs a trusted historical reference to distinguish:

```text
never cleared this boundary
```

from:

```text
cleared it previously, but current support has changed
```

Recommendation:

Introduce an immutable **Progression Attainment** record at the moment an upward boundary is deliberately crossed.

Conceptual record:

```text
ProgressionAttainment
- id
- trade_plan_id
- trade_plan_revision
- boundary
- policy_id
- eligibility_snapshot
- attained_environment
- attained_at
- source
- note
```

The eligibility snapshot should preserve the per-requirement C3 explanation that justified the crossing.

Attainment is an event/history record, not a current permission flag.

---

## Crossing a boundary

A future configured boundary can be crossed only when current C3 eligibility is AVAILABLE.

When the technician deliberately starts/enters the higher rung for the first time after clearing the boundary, Cockpit may record the attainment event.

This should be explicit and auditable.

Do not create an attainment record merely because the evaluator happens to return AVAILABLE while the technician is browsing the launcher.

---

## Eligibility loss after attainment

If a current evaluation for an already-attained boundary becomes BLOCKED:

1. higher-rung launch follows current C3 behavior and is blocked,
2. the prior attainment record remains intact,
3. Competency State does not change automatically,
4. Evidence Maturity does not change automatically,
5. Development Direction does not change automatically,
6. Cockpit surfaces a **Regression Review / Revalidation Review** condition,
7. the operator classifies what the change means.

The historical statement remains true:

> The technician previously cleared this boundary under the recorded plan/policy.

The current statement may also be true:

> The current requirements are no longer satisfied.

Both must coexist.

---

## Never-attained vs lost eligibility

These cases should be visibly different.

### Never attained

```text
Boundary never cleared
Current eligibility: BLOCKED
Reason: insufficient evidence
```

Meaning:

> progression has not yet been earned.

### Previously attained, now blocked

```text
Boundary previously attained
Current eligibility: BLOCKED
Regression/Revalidation Review: required
```

Meaning:

> previous attainment is historical truth, but current support is no longer sufficient.

This distinction is important for future learning analytics.

---

## Trade Plan revision changes are not regression

A new Trade Plan revision may require fresh contextual evidence even when the underlying competency is unchanged.

Example:

```text
rX
Draw on Liquidity = Proficient
Validation -> Execution attained

rY
same competency definition
different process/model/session context
fresh Validation evidence required
```

Result:

- prior rX attainment remains valid historical provenance,
- competency can remain Proficient,
- rY Live/Execution eligibility may be BLOCKED,
- classification should be **Revalidation Required**, not Competency Regression.

This is one of the most important C4 distinctions.

---

## Materially changed competency definitions

If a competency definition changes materially between revisions:

- prior evidence remains evidence for the old definition,
- prior attainment remains historical truth for the old plan,
- the new definition must not silently inherit certification,
- re-entry may require Study, Rehearsal, or Validation depending on the change.

Until definition fingerprinting exists, Cockpit should not automatically decide the correct re-entry rung.

This should surface as explicit revalidation/review work rather than automatic demotion.

---

## Evidence age / staleness

Current architecture does not automatically declare evidence stale merely because time passed.

Therefore C4 must not invent time-based decay.

If a future Trade Plan explicitly defines recency requirements, failure of those requirements may create:

- current BLOCKED eligibility,
- a revalidation requirement,

but not automatic Competency State regression.

---

## Human Certification withdrawal

If an explicit Human Certification requirement was previously confirmed and is later withdrawn:

- current eligibility can become BLOCKED,
- prior attainment remains historical,
- reason should identify certification withdrawal/current absence,
- no other competency or evidence state changes automatically.

This may lead to Regression Review, but is not itself proof of skill regression.

---

## Voluntary step-down

Moving downward remains frictionless and non-punitive.

A technician may deliberately choose Replay, Study, or Forward despite being eligible for a higher rung.

This is **not regression**.

Future analytics may record a voluntary step-down event with an optional reason such as:

- refresh,
- deliberate practice,
- confidence rebuilding,
- new market condition,
- experimenting with candidate plan,
- personal preference.

The action must not erase attainment or reduce Competency State automatically.

---

## Temporary operating restrictions remain separate

Examples:

- NFP/FOMC restriction,
- daily loss limit,
- account lock,
- personal health/condition,
- market closure,
- operational/broker restriction.

These may prevent effective access to Live/Execution while progression eligibility remains AVAILABLE.

Future effective access should compose layers:

```text
Progression Eligibility
        +
Temporary Operating / Safety Restrictions
        ↓
Effective Environment Access
```

C4 should not classify a temporary pause as regression.

---

## Proposed Regression Review classification

For v0, keep classification small and human-readable:

- **Revalidation Required**
- **Confirmed Competency Regression**
- **Evidence / Governance Reassessment**
- **Certification Withdrawn**
- **Needs Study / Unresolved**

A Regression Review may include:

- boundary,
- governing Trade Plan revision,
- prior attainment ID,
- current C3 eligibility result/snapshot,
- selected classification,
- note,
- supporting evidence IDs,
- reviewed_at.

The classification is human-reviewed.

No automatic proficiency score or severity rating.

---

## Response to confirmed competency regression

Even after human confirmation, do not automatically choose a new Competency State.

Recommended v0 behavior:

1. preserve the regression review,
2. surface it in Review / Development,
3. allow the technician to deliberately update Competency State if appropriate,
4. allow Development Direction to be deliberately set,
5. current eligibility continues to be determined by the Trade Plan evaluator.

This preserves the rule that no layer silently mutates another layer.

A later policy may define explicit automatic consequences, but v0 should not.

---

## Re-entry after regression/revalidation

The same published progression policy should determine when the higher boundary becomes AVAILABLE again.

Do not create a separate hidden "regression recovery score."

Recovery is:

```text
targeted Study/Rehearsal/Validation
        ↓
new reviewed evidence / governance updates
        ↓
same transparent policy evaluation
        ↓
AVAILABLE again
```

A later **Revalidated / Regression Cleared** event may close the review and preserve learning-history provenance.

---

## Recommended current standing presentation

Cockpit can eventually present a boundary as:

```text
Validation -> Execution

Historical attainment:
Attained under rX on 2026-...

Current rY eligibility:
BLOCKED

Interpretation:
Revalidation Required

Competency State:
Proficient

Next work:
Validation
```

This tells the truth without flattening all concepts into one red/green state.

---

## Analytics value

This structure enables future analysis of:

- first attainment time,
- time retained before revalidation,
- frequency of eligibility loss,
- confirmed regressions versus plan-revision revalidation,
- time to regain eligibility,
- voluntary step-down frequency,
- which competency families require more refresh,
- whether related prior competencies shorten revalidation,
- learning decay versus contextual-change effects.

This directly supports the previously accepted learning-efficiency direction.

---

## Proposed C4 implementation boundary

If accepted, C4 implementation should include:

- immutable Progression Attainment history,
- explicit attainment recording only when a configured AVAILABLE boundary is deliberately crossed,
- current eligibility vs historical attainment comparison,
- a derived **eligibility loss / review required** condition,
- human-authored Regression Review classification,
- optional links to supporting competency evidence,
- no automatic Competency State mutation,
- no automatic Evidence Maturity mutation,
- no automatic Development Direction mutation,
- revalidation semantics across Trade Plan revisions,
- voluntary step-down semantics that preserve attainment,
- tests proving historical attainment is never erased by later blocking,
- UI that explains historical attainment separately from current eligibility.

Do not yet implement:

- temporary operating restriction composition,
- competency-definition fingerprinting,
- automatic regression detection from performance metrics,
- automatic demotion,
- automatic rung selection after regression,
- readiness percentages,
- severity scores,
- time-based skill decay,
- real Alpha 0.7 progression policy.

---

## Operator confirmation questions

1. Should C4 formally separate **historical Progression Attainment** from **current Eligibility**, so prior clearance is never rewritten by a later block?
2. Should an attainment record be created only when the technician deliberately crosses an AVAILABLE boundary, rather than whenever the evaluator happens to report AVAILABLE?
3. Do you agree that AVAILABLE -> BLOCKED under the same plan/policy can be called **Eligibility Loss Detected**, but not automatically **Competency Regression**?
4. Should **Confirmed Competency Regression** require explicit human review rather than automatic inference from policy failure?
5. Should a new Trade Plan revision requiring fresh evidence be classified as **Revalidation Required**, not regression, when the underlying competency may still be intact?
6. Should ordinary evidence insufficiency for a boundary that was never attained remain simply **not yet attained**, rather than be called regression?
7. Should voluntary movement downward remain non-punitive, preserve all prior attainment, and never reduce Competency State automatically?
8. Should temporary news/risk/personal/account restrictions remain entirely outside C4 progression regression semantics?
9. After confirmed regression/revalidation work, should recovery use the same transparent Trade Plan progression policy rather than a separate recovery/readiness mechanism?
10. Do you agree that even a human-confirmed competency regression should **not automatically mutate Competency State or Development Direction** in v0; those changes remain deliberate separate actions?
