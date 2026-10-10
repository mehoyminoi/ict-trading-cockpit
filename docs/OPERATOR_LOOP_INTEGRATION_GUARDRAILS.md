# C5 — Operator-loop integration and guardrails v0 design candidate

**Status:** Design candidate for operator review  
**Milestone:** C5 — Operator-loop integration and guardrails  
**Schema expectation:** no change unless implementation proves otherwise

## Purpose

C1-C4 created the governance substrate:

```text
Evidence
  ↓
Evidence Maturity
  ↓
Trade Plan Progression Policy
  ↓
Explainable Eligibility
  ↓
Historical Attainment / Regression-Revalidation semantics
```

C5 should make that substrate behave coherently in the actual operator loop.

The question is no longer "can the system calculate the right state?" It is:

> When the operator tries to move through Study -> Rehearsal -> Validation -> Execution, does the Cockpit apply the right guardrail, explain it clearly, preserve safe lower-rung options, and avoid leaking progression logic into unrelated safety/authorization layers?

C5 is therefore primarily an **integration and boundary-enforcement** slice, not a new scoring/governance model.

## Core guardrail contract

For a configured progression boundary:

```text
AVAILABLE
    → higher-rung launch is permitted
    → deliberate crossing records Progression Attainment

BLOCKED
    → higher-rung launch is prevented
    → exact failing/unknown requirements remain visible
    → lower-rung operation remains available

NOT CONFIGURED
    → explicitly ungoverned by progression policy
    → Alpha 0.7 remains non-restrictive
    → no Progression Attainment is created
```

The launcher is the enforcement point for **starting a higher-rung environment**.

Progression eligibility is not a general-purpose runtime kill switch.

## Guardrail boundary: launch versus active run

Once a Process Run has legitimately started, a later change in progression eligibility must not silently:

- terminate the active run,
- demote its environment,
- rewrite its provenance,
- close/flatten a trade,
- alter setup authorization,
- alter Competency State,
- alter Evidence Maturity,
- alter Development Direction.

If eligibility changes while a run is active, the Cockpit may surface the changed progression context for the **next transition/run**, but v0 should not retroactively invalidate the already-started run.

This prevents progression governance from becoming accidental execution-control logic.

## Guardrail boundary: progression versus trade authorization

Keep these separate:

```text
Progression Eligibility
= may I start/use this training/execution environment?

Trade / Setup Authorization
= does the recorded setup + safety state permit an entry now?
```

A progression AVAILABLE result does not authorize a trade.

A trade/setup Clear result does not grant progression eligibility.

A progression BLOCKED result prevents the upward environment launch; it must not be repurposed as an entry/exit authorization state inside an already-active run.

**Exit/flatten remains outside entry/progression gating and must never be blocked.**

## Guardrail boundary: temporary operating restrictions

C4 established:

```text
Progression Eligibility
        +
Temporary Operating / Safety Restrictions
        ↓
Effective Environment Access
```

C5 should preserve this boundary but **not invent a temporary-restriction engine** merely to complete Milestone C.

Examples still belong to a separate future layer:

- NFP/FOMC/news restrictions,
- daily loss/risk limits,
- account lock,
- broker/platform outage,
- personal-condition pause,
- market closure.

If/when that layer exists, the operator should be able to tell whether access is unavailable because of:

1. progression,
2. temporary operating/safety restriction,
3. both.

For C5 v0, do not merge those concepts.

## Operator-loop states

The launcher should expose one concise state model for the selected environment.

### Historical Backtest / Study

No upward boundary applies.

Show:
- purpose = Study,
- progression = Foundation / no boundary required,
- launch remains available subject to normal run prerequisites such as a focused Study question.

### Replay / Rehearsal

Boundary:
- Study -> Rehearsal

### Forward Test / Validation

Boundary:
- Rehearsal -> Validation

### Live / Execution

Boundary:
- Validation -> Execution

For Replay/Forward/Live show:

- current eligibility status,
- governing boundary,
- concise reason,
- requirement-level detail on demand,
- prior attainment/current standing when applicable,
- lower-rung route when blocked.

## Operator action guidance

C5 may provide **deterministic action guidance** derived directly from explicit state. It must not become an inferred coaching engine.

Examples:

### BLOCKED — insufficient evidence

Permitted UI guidance:

> This boundary is blocked because required evidence is missing. Continue in the recommended lower environment or review the requirement in Progression.

This is not an automatic Development Direction.

### BLOCKED — Evidence Maturity

Permitted UI guidance:

> Review Evidence Maturity for the named competency/boundary.

Do not auto-change the maturity state.

### BLOCKED — Human Certification

Permitted UI guidance:

> Human Certification is required under the current Trade Plan revision.

Do not self-certify or treat certification as an override.

### UNKNOWN / cannot evaluate

Permitted UI guidance:

> This requirement cannot currently be evaluated. Review the source/provenance before relying on progression.

Unknown never passes.

### Revalidation Required

Permitted UI guidance:

> Historical attainment remains recorded, but the current Trade Plan revision requires fresh validation/review.

Do not label this competency regression.

### Eligibility Loss Detected

Permitted UI guidance:

> This boundary was previously attained under the same policy but is currently blocked. Review the loss of support before the next upward transition.

Do not auto-demote Competency State.

## Recommended lower-rung routing

When a configured boundary is BLOCKED, the launcher may offer a low-friction route to the normal lower environment:

```text
Replay blocked
→ Study

Forward blocked
→ Replay

Live blocked
→ Forward
```

Accepted semantics:

- routing may preselect/stage the lower environment,
- routing does not auto-start a Process Run,
- existing question/focus context should be preserved when semantically valid,
- no penalty/regression event is created,
- historical attainment remains untouched,
- the operator may choose an even lower rung deliberately.

This is navigation assistance, not automatic demotion.

## Review / Development integration

The new focused Review / Development structure should become the explanation/work surface for progression.

### Overview

May show a concise progression line for a selected competency/boundary, but must avoid pretending that one competency alone represents whole-environment eligibility when policy is boundary/global or multi-competency.

### Progression

Should be the authoritative operator-facing place to inspect:

- Evidence Maturity,
- progression policy requirements,
- current Eligibility,
- historical Attainment,
- Eligibility Loss / Revalidation standing,
- Regression/Revalidation Review when applicable.

The launcher may link/navigate here when blocked.

### Practice & Launch

Should remain the action surface for:

- targeted Study,
- staged lower-rung practice,
- starting a new Process Run.

The operator should not have to hunt across the application to understand a block and then find the lower-rung action.

## Human Certification placement

Human Certification currently lives in Rules / Safety because it is Trade Plan-owned progression-policy data.

C5 should keep its authoritative edit control there.

However, Progression may show the requirement result and provide navigation guidance such as:

> Human Certification required — manage under Rules / Safety > Progression Policy.

Do not duplicate editable certification controls in multiple places in v0.

## Active-run context

A started Trading Run already snapshots its environment, purpose, Trade Plan revision, and other provenance.

C5 should make progression provenance understandable without rewriting history.

Recommended v0 behavior:

- launcher evaluates current eligibility before start,
- configured AVAILABLE crossing records immutable attainment,
- started run continues with its recorded environment/revision,
- Review can later see that run's environment and governing revision,
- no continuous progression reevaluation is required during the active run,
- a new run/next upward transition evaluates current policy afresh.

## Restart / restore guardrail

Restoring an already-started run is not the same event as launching a new upward transition.

Therefore:

> **Restoring an existing run should not create a second attainment or rerun launch gating as though the operator were initiating a new boundary crossing.**

The restored run should preserve its original provenance.

A future explicit "start new run in higher environment" action must go through current eligibility again.

## Explainability contract

A blocked transition must be able to answer:

```text
Where am I?
Which boundary am I trying to cross?
Is that boundary configured?
What is the current eligibility result?
Which exact requirement(s) prevent progression?
Is the problem missing evidence, failed requirement, human certification, or inability to evaluate?
What lower-rung action remains available?
Where can I review/fix the relevant state?
```

Do not reduce this to a generic red/green light.

The recent friction-reduction work gives C5 the presentation foundation for this contract.

## Proposed C5 implementation slices

### C5.1 — Integrated progression status model

Create a presentation/service-level object that combines already-existing derived facts for one selected environment:

- environment,
- purpose,
- boundary,
- eligibility,
- progression standing,
- recommended lower environment,
- deterministic action hints/navigation targets.

This object should not persist mutable current truth and should not create a new score.

### C5.2 — Launcher guardrail presentation

Refine the launcher so configured BLOCKED states:

- clearly prevent upward start,
- show concise reason first,
- allow requirement details on demand,
- expose recommended lower-rung action,
- offer a route to Review / Development > Progression.

AVAILABLE and NOT CONFIGURED remain clearly distinct.

### C5.3 — Lower-rung staging

Add explicit staging/navigation to the recommended lower environment without auto-start.

Preserve semantically valid Study/competency intent where possible.

### C5.4 — Progression work-area integration

Make Review / Development > Progression the focused explanation surface for:

- policy,
- eligibility,
- maturity,
- attainment,
- revalidation/regression standing.

Add navigation hooks from launcher using the stable UI anchors created in the friction slice.

### C5.5 — Restore and mutation guardrails

Automated tests should prove:

- restore does not create attainment,
- browse does not create attainment,
- NOT CONFIGURED does not create attainment,
- configured BLOCKED cannot start upward environment,
- lower rung remains launchable,
- progression gating does not mutate competency/maturity/direction,
- progression gating does not alter setup authorization,
- no progression logic can block exit/flatten,
- active run is not silently terminated or demoted when governance state later changes.

## Schema expectation

C5 should be implementable with existing v33 state.

The preferred design is:

- derive current integration state on demand,
- reuse immutable Progression Attainment,
- reuse existing repositories,
- add navigation/presentation wiring,
- add tests.

Do not add persistence merely to remember a derived launcher status.

## Explicit non-goals

C5 v0 should not:

- publish the first real Alpha progression policy,
- introduce readiness percentages,
- introduce weighted scoring,
- auto-promote or auto-demote,
- auto-change Competency State,
- auto-change Evidence Maturity,
- auto-change Development Direction,
- create time-based skill decay,
- create temporary operating/safety restriction infrastructure,
- merge progression and setup authorization,
- gate exit/flatten,
- continuously police an already-started run,
- build NinjaTrader integration,
- build the final PDM-like process map.

## Acceptance target

A successful C5 v0 should make this true:

> A configured upward boundary is enforced at the correct moment, the operator can immediately understand why it is available or blocked, blocked progression leaves a clear lower-rung path, historical truth remains intact, and progression governance never masquerades as trade authorization or runtime execution control.

## Operator confirmation questions

1. Treat progression eligibility as a **new-run/upward-transition guardrail**, not a continuous active-run kill switch?
2. Once a run has legitimately started, do not auto-terminate/demote it if progression state later changes?
3. Keep progression eligibility completely separate from setup/trade authorization, including never using progression state to block exit/flatten?
4. Keep temporary operating/safety restrictions outside C5 v0 while preserving the future composition boundary?
5. Allow deterministic action guidance from explicit requirement reasons, but no inferred coaching/recommendation engine?
6. When BLOCKED, offer a **Stage recommended lower environment** action that preselects but never auto-starts the lower rung?
7. Preserve semantically valid Study question/competency focus when staging downward, but never create a regression/demotion event?
8. Make Review / Development > Progression the focused explanation surface and let the launcher navigate there when blocked?
9. Keep Human Certification editing authoritative in Rules / Safety, while Progression only explains its requirement/result and points there?
10. Treat restore/resume of an already-started run as historical continuation: no new launch gating and no duplicate Progression Attainment?
11. Derive C5 integration state on demand with no new persisted current-status table and preferably no schema change from v33?
12. After C5, leave real progression thresholds/policies unconfigured in Alpha 0.7 until separately and deliberately designed?
