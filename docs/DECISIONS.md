# ICT Trading Cockpit — Architectural Decisions

This file records durable project decisions and the rationale behind them. It is not a task list. Add a new entry when a decision would be expensive or confusing to rediscover from chat history.

## 2026-10-07 — Training environment semantics

**Status:** Accepted

The environment ladder is:

- Historical Backtest / Lab → **Study**
- Replay → **Rehearsal**
- Forward Test → **Validation**
- Live → **Execution**

Progression eligibility is a separate concern. Environment labels describe what the environment is for; they do not themselves certify readiness to advance.

## 2026-10-07 — Competency model separation

**Status:** Accepted

Keep three concepts separate:

1. **Competency definition** — the skill or mechanic the Trade Plan cares about.
2. **Competency state** — where that skill currently sits in the training ladder.
3. **Evidence** — observations that may later justify changing that state.

Do not collapse these into a single score.

Initial competency/proficiency v0 deliberately does **not** add:

- proficiency percentages,
- automatic promotion/demotion,
- a Live lock based on proficiency,
- a large proficiency dashboard.

Those behaviors require evidence rules and thresholds that have not yet been justified.

## 2026-10-07 — Competency definitions are plan-owned

**Status:** Accepted

The competency catalog is authoritative Trade Plan data. Adding or changing competency definitions therefore creates a new published Trade Plan revision.

Current proficiency state and accumulated evidence are mutable profile/evidence data and remain separate from the versioned Trade Plan.

This decision moved the default Trade Plan from Alpha 0.6 to Alpha 0.7.

## 2026-10-07 — First practical use of competencies

**Status:** Accepted

The first user-facing competency workflow is:

Trade Plan competency catalog
→ current proficiency state
→ Study Run focus links
→ future evidence accumulated against the competency

A Historical Backtest / Study Run can explicitly state which plan-owned competencies it is training, and those links should survive into Review.

## 2026-10-07 — Deterministic tests for time-aware Live Watch behavior

**Status:** Accepted

Tests that depend on timed Live Watch behavior should use explicit deterministic Replay market-time context rather than the wall clock.

The earlier 265-passed / 2-failed result on `feature/competency-proficiency-v0` was resolved by making the affected structured-playbook tests deterministic Replay runs. Production Live Watch code did not require a corresponding fix for that result.

## Decision-recording rule

For future substantial decisions, append an entry containing:

- date,
- short decision title,
- status,
- decision,
- rationale,
- important consequences or intentionally deferred behavior.

Prefer recording the reason a choice was made, not just the final implementation.


## 2026-10-08 — Summary templates are versioned Workbench configuration

**Status:** Accepted

Generated Trade Summary and Study Find text should not depend on hardcoded GUI strings.

Summary template definitions are separate configuration from the Trade Plan. Published template revisions are immutable, previous revisions remain available for provenance/history, and each summary kind has an explicit active revision used for new generated output.

Editing/publishing belongs in Workbench rather than the focused daily capture surfaces. Study Find and Trade Summary consume the active definition and remain responsible for structured record data, not template design.

The first slice intentionally supports revisioning of the existing default template families rather than a broad template-library/catalog UX. Expand that only when repeated use justifies it.


## 2026-10-08 — Canonical handoff package and decision precedence

**Status:** Accepted

Long-running project continuity must not depend on recovering a prior ChatGPT conversation.

The canonical handoff package is:

1. `PROJECT_STATE.md` — exact checkpoint,
2. `PROJECT_REQUIREMENTS.md` — current intended architecture/roadmap,
3. `DECISION_AUDIT.md` — conflict and supersession status,
4. `DECISIONS.md` — durable accepted rationale,
5. `PROJECT_EVOLUTION.md` — chronological architecture history,
6. current code/tests,
7. historical transcripts only when clarification remains necessary.

When sources conflict, prefer verified current implementation/tests, then accepted current requirements, then later explicit decisions and the decision-audit supersession record. Do not promote an older idea merely because it was discussed in more detail.

Every handoff must state the project's **current architectural frontier** in addition to the next concrete task.

**Rationale:** Recovery of the prior long conversation showed that an old feature can remain richly documented even after later work deliberately demoted or superseded it. A chronological history plus an explicit supersession ledger prevents future chats from mistaking historical detail for current priority.

**Consequence:** `PROJECT_REQUIREMENTS.md` should remain current-state oriented rather than becoming a diary. Historical evolution and supersession belong in their dedicated documents.


## 2026-10-08 — Reconciled roadmap and learning frontier accepted

**Status:** Accepted

The recovered project trajectory is now authoritative for forward planning.

The current architectural frontier is:

`targeted Study -> competency evidence -> Replay integration -> Forward validation -> progression/eligibility -> Live Execution`

The accepted milestone order is:

1. Competency evidence loop
2. Review / Development synthesis
3. Evidence Maturity and progression governance
4. Continuous operator-loop hardening in parallel
5. Context maturity: QT/AMDX, news, and distortions
6. Execution-safety simulation
7. NinjaTrader execution integration
8. Shared / multi-device operation

Revision/provenance is a cross-cutting requirement that each slice must preserve; it is not the next standalone milestone.

**Supersedes:** the earlier reconciliation draft that placed abstract process/revision architecture first, and any older roadmap ordering that would elevate Film Night, visual-polish, broad Live-Watch expansion, hardware controls, or deep integrations ahead of the learning/progression loop.

**Rationale:** recovery of the full conversation history showed that the project had already deliberately pivoted from operating-surface expansion toward Study/Lab, competency evidence, and progression semantics before the previous chat ended.


## 2026-10-08 — Competency evidence is provenance, not competency state

**Status:** Accepted

Competency evidence is a first-class persisted record separate from both the Trade Plan-owned competency definition and the operator's mutable competency state.

The v0 evidence loop is:

`focused Study/Rehearsal/Validation run -> reviewed outcome -> persisted evidence for each focused competency`

Evidence should preserve enough provenance to understand where it came from, including the Trading Run, environment/purpose, Trade Plan revision, study intent/outcome, and relevant market-time/QT context.

Re-reviewing the same run+competency updates/replaces that evidence rather than manufacturing duplicate samples from one run.

**Rationale:** the project needs trustworthy observations before it can justify proficiency scoring, state transitions, or progression rules.

**Consequence / deferred behavior:** evidence creation does not automatically change `CompetencyState`, proficiency, eligibility, or Evidence Maturity. Those interpretations remain later work.


## 2026-10-08 — Human-readable system guide will accompany canonical project docs

**Status:** Accepted

Create `docs/SYSTEM_GUIDE.md` at the next convenient documentation checkpoint.

Its role is explanatory: give the operator a coherent mental model of the Cockpit using definitions, system-purpose descriptions, architecture diagrams, operating loops, learning/progression loops, sub-loop flowcharts, source-of-truth relationships, and examples of current paper-doll controls versus the underlying domain model.

The guide should help prevent accidental scope drift caused by imprecise terminology as the architecture grows.

A key example it should explain is competency extensibility:

- competency definitions are Trade Plan-owned and revisioned,
- a newly adopted ICT concept can become a new competency in a later Trade Plan revision,
- from that revision forward the shared competency catalog can expose it to Study/Rehearsal/Validation focus and evidence capture,
- historical records are not silently retrofitted unless an explicit migration/mapping rule is created,
- evidence and derived metrics may later support progression decisions, but the Cockpit must not invent readiness rules merely because a competency exists.

**Rationale:** the full architecture is now large enough that requirements, state, decisions, and evolution documents are individually correct but do not provide a single human-readable conceptual map.

**Consequence:** `SYSTEM_GUIDE.md` will be maintained when terminology, subsystem relationships, ownership boundaries, or major system loops materially change. It will remain explanatory and will not replace canonical requirements, decisions, current state, or implementation.


## 2026-10-08 — Competency evidence is surfaced before it is scored

**Status:** Accepted

Review / Development should first present accumulated competency evidence as human-legible history before the Cockpit attempts to derive proficiency, Evidence Maturity, or eligibility conclusions.

The accepted v0 surface supports:

- all-competency evidence review,
- filtering by plan-owned competency,
- compact counts by environment purpose and reviewed outcome,
- detailed provenance for an individual evidence record.

**Rationale:** the operator should be able to inspect and challenge the underlying observations before later aggregation or progression rules are trusted.

**Consequence / deferred behavior:** evidence counts and outcomes are descriptive. They do not yet constitute a score, competency-state transition, Evidence Maturity judgment, or progression decision.


## 2026-10-08 — System Guide v0 accepted

**Status:** Accepted

`docs/SYSTEM_GUIDE.md` is accepted as the maintained human-readable conceptual map of the ICT Trading Cockpit.

It explains terminology, subsystem relationships, major operating/learning loops, competency/evidence semantics, source-of-truth relationships, and the distinction between temporary UI controls and underlying domain concepts.

**Rationale:** the project architecture is now broad enough that the operator needs one coherent explanatory document in addition to the canonical requirements, decisions, state, and evolution records.

**Consequence:** future material changes to terminology, ownership boundaries, or major system loops should update the guide. The guide remains explanatory and does not supersede canonical requirements, decisions, current state, or verified implementation.


## 2026-10-08 — Evidence routing stages intent; it does not bypass run launch

**Status:** Accepted

The Review / Development action **Study this competency** is an intent-staging action, not a second run-entry mechanism.

It prepares the shared Process Run launcher for Historical Backtest / Study, selects the chosen competency as the deliberate focus, preserves an already-authored Study question, and leaves final run creation to the existing **Begin Process Run** action.

**Rationale:** evidence should be able to route the technician toward deliberate practice without bypassing the shared launcher, its validation rules, environment semantics, or provenance capture.

**Consequence:** future Review-to-Study routing should preconfigure the canonical launcher rather than create parallel launch paths. The technician still controls the Study question and explicitly starts the run.


## 2026-10-08 — Development Direction separates synthesis from competency state

**Status:** Accepted

Introduce **Development Direction** as explicit human-reviewed synthesis over accumulated competency evidence.

Initial directions are:

- Study
- Rehearsal
- Validation
- Monitor / Gather Evidence
- No Active Focus

Development Direction answers **what deliberate work should happen next**. It is separate from Study Outcome, Competency State, Evidence Maturity, and Eligibility.

For v0:

- one current mutable direction is stored per Trade Plan + competency,
- an operator note is optional,
- supporting evidence links are optional,
- no automatic derivation occurs,
- no competency-state transition occurs,
- no eligibility or Evidence Maturity conclusion occurs,
- only the existing Study routing needs active behavior initially.

**Rationale:** accumulated evidence needs a human synthesis layer before later governance can safely reason about progression. This avoids turning descriptive evidence or Study outcomes into hidden readiness scores.

**Consequence:** Review / Development can become actionable without prematurely automating weakness detection or proficiency decisions.


## 2026-10-08 — Stable Trade Plan revisions are protected from candidate development

**Status:** Accepted

A proven/stable Trade Plan revision must remain immutable and historically interpretable while later candidate revisions are developed, studied, rehearsed, and validated.

Conceptually:

```text
stable / trusted rX
        |
        +-- continues to mean exactly what it meant
        +-- historical runs/evidence remain bound to rX
        |
        +--> candidate rY
              + new/changed models
              + new/changed competencies
              + new/changed rules/process
              + new evidence collected under rY
```

Development of `rY` must not mutate `rX`, retroactively change what old records mean, or silently make old evidence satisfy newly changed competency definitions.

If a competency definition is unchanged between Trade Plan revisions, evidence may still be comparable across those revisions. If the competency definition materially changes, evidence created under the earlier definition remains valid historical evidence for that earlier definition but must not silently be treated as evidence for the new meaning.

A newly added competency begins collecting evidence from the revision that defines it. Historical pre-definition records do not automatically become evidence for it. Any future retrospective classification/mapping must be an explicit analytical act with its own provenance.

**Rationale:** revision control must protect a known-good trading system while allowing experimentation beside it. It also makes later comparisons meaningful: what exactly changed, which evidence belonged to which definition, and whether the candidate revision actually improved the process/system.

**Consequence:** future Workbench/revision tooling should distinguish stable/trusted revisions from candidate development revisions and preserve exact definition provenance. Competency Synthesis should show revision provenance but should not issue a generic warning merely because records span Trade Plan revisions; meaningful caution depends on whether the competency definition itself changed.


## 2026-10-09 — Cross-Run Observation separates recurring interpretation from Development Direction

**Status:** Accepted

Introduce **Cross-Run Observation** as the human-authored interpretation layer over multiple competency-evidence records.

Cross-Run Observation answers:

> What seems to be happening across these reviewed runs?

Development Direction remains separate and answers:

> What should I do next?

For v0:

- one current mutable Cross-Run Observation is stored per Trade Plan + competency,
- observation text is human-authored,
- supporting evidence links are optional,
- multiple evidence records may be linked deliberately,
- no minimum sample count is required,
- no automatic pattern detection or trend classification occurs,
- saving an observation does not change Development Direction,
- saving Development Direction does not rewrite the observation,
- no competency-state, Evidence Maturity, progression, or eligibility change occurs.

**Rationale:** Review / Development should distinguish raw evidence, descriptive aggregation, human interpretation, and next-development intent before Evidence Maturity/governance is introduced.

**Terminology:** use **Cross-Run Observation**, not Pattern Observation. "Pattern" has an unwanted trading-pattern connotation and could blur the distinction between study-data synthesis and market-pattern hunting.

**Consequence:** successful implementation/acceptance of this slice completes the intended Milestone B human-synthesis chain:

`Evidence -> Competency Synthesis -> Cross-Run Observation -> Development Direction -> targeted Study routing`


## 2026-10-09 — Evidence Maturity is boundary-aware evidence governance

**Status:** Accepted

Introduce **Evidence Maturity Profile** as the governance layer that answers:

> Can this evidence set support a trustworthy decision at this progression boundary?

Evidence Maturity remains separate from:

- Competency State — where the skill sits in the training ladder,
- Progression Policy — what evidence/conditions the Trade Plan requires,
- Eligibility — whether the configured policy is currently satisfied.

The v0 profile uses six inspectable dimensions:

- Volume / Sample Depth,
- Environment Relevance,
- Recency,
- Consistency,
- Context Coverage,
- Revision Relevance.

No weighted composite score or readiness percentage is introduced.

The v0 profile is explicitly boundary-aware and is identified by:

`Trade Plan + competency + progression boundary`

Candidate boundaries are:

- Study -> Rehearsal,
- Rehearsal -> Validation,
- Validation -> Execution.

The v0 human maturity states are:

- Not Assessed,
- Insufficient Evidence,
- Developing Evidence,
- Decision-Usable Evidence.

These states describe whether the evidence set is usable for a decision. They do **not** say what that decision should be.

**Removability guardrail:** the overall maturity-state label is not load-bearing architecture. The six-dimensional profile, notes, and descriptive evidence facts must remain meaningful without it. If operator use shows the labels are too evaluative, the state can be hidden/removed without redesigning the evidence model. Progression policy must not become irreversibly coupled to the label before its usefulness is validated.

**Rationale:** the same evidence set can be sufficient for one progression boundary and insufficient for another. Boundary-aware maturity prevents a global "mature" label from silently becoming Live readiness.

**Consequence:** C1 builds the Evidence Maturity Profile; C2 later defines Trade Plan-owned progression policy; C3 evaluates eligibility explainably. No automatic advancement/demotion or Live lock is introduced in C1.


## 2026-10-09 — Progression Policy is Trade Plan-owned permission logic

**Status:** Accepted

Progression Policy is immutable, revisioned Trade Plan data.

The v0 unit is one policy per upward progression boundary:

- Study -> Rehearsal,
- Rehearsal -> Validation,
- Validation -> Execution.

A policy may contain competency-scoped and boundary/global gating requirements. Required competencies are explicit; adding a competency to the Trade Plan does not automatically make it a progression blocker.

The v0 requirement kinds are:

- Evidence Maturity State,
- Competency State,
- Evidence Purpose Present,
- Human Certification.

v0 composition is simple ALL/AND. Empty policies are invalid. Progression Policy contains gating requirements only. No manual progression override exists in v0.

C2 defines policy substrate only. C3 later evaluates it into explainable eligibility. A required condition that cannot be evaluated must never silently pass.

**Rationale:** progression rate/restriction is a core Trade Plan lever. Policy therefore belongs with the known/gold-standard system rather than in mutable profile state or hidden evaluator code.

**Consequence:** Alpha 0.7 remains without configured progression policy. Publishing the first real policy requires a new Trade Plan revision and a separate deliberate operator decision.


## 2026-10-09 — Competency continuity survives whole-plan revision when the definition is unchanged

**Status:** Accepted

A whole Trade Plan revision change does not automatically reset competency knowledge.

If a competency definition is materially unchanged between rX and rY:

- prior evidence remains valid evidence of that competency,
- prior Competency State may remain intact,
- a technician who was Proficient does not become unskilled merely because surrounding plan content changed,
- rY may still require fresh Rehearsal or Validation evidence to prove the known competency integrates correctly with the revised system.

Therefore distinguish:

- **competency knowledge/proficiency continuity**, from
- **current-plan contextual validation / progression eligibility**.

If the competency definition materially changes, old evidence remains historically valid for the old definition but must not silently certify the new definition. The needed return point depends on the change; it is not universally hardcoded to Study, Rehearsal, or Validation.

New competencies do not inherit historical evidence or proficiency automatically.

**Rationale:** resetting unchanged competencies discards real learning, while automatically accepting old proficiency for a materially changed system can overstate readiness.

**Consequence:** future definition-level identity/fingerprinting should support machine-verifiable unchanged/changed competency continuity. Progression Policy may require fresh evidence under rY without mutating broader Competency State.


## 2026-10-09 — Learning velocity and progression friction are future analytics targets

**Status:** Accepted future direction

The Cockpit should eventually analyze the rate and efficiency of learning, not only trade outcomes.

Future analytics may examine:

- time from first exposure to usable competence,
- time spent at each Study/Rehearsal/Validation stage,
- evidence volume/type before progression,
- revalidation and regression events,
- competency families/genres,
- transfer learning from already-mastered related concepts,
- diminishing returns from additional practice at one rung,
- progression-policy friction and whether a different practice sequence would have produced equally trustworthy competence faster.

The long-term objective is lifetime mastery while improving allocation of learning time.

**Guardrail:** this does not justify numeric readiness scores, arbitrary current thresholds, or rushing progression. C2 only preserves the structured provenance needed for later analytics.


## 2026-10-09 — Explainable Eligibility is derived from published progression policy

**Status:** Accepted

Eligibility is a deterministic derived result, not manually authored mutable truth.

Top-level states remain AVAILABLE / NOT CONFIGURED / BLOCKED. Requirement-level results use SATISFIED / NOT SATISFIED / UNKNOWN. Unknown never silently passes.

Missing required evidence is a normal NOT SATISFIED / INSUFFICIENT_EVIDENCE result. UNKNOWN is reserved for cases the system genuinely cannot evaluate safely.

For v0, Evidence Purpose Present uses evidence from the current Trade Plan revision by default. Older-revision Evidence Maturity does not silently carry forward into a new policy context; it yields UNKNOWN until reviewed under the current revision.

Human Certification is a revision-bound, auditable requirement source, not an override.

A future configured BLOCKED result may prevent upward transition, while downward movement remains frictionless. Alpha 0.7 remains NOT CONFIGURED and non-restrictive until real progression policy is deliberately published.

Regression/demotion belongs to C4. Temporary operating/safety restrictions remain a separate layer.

**Rationale:** this preserves explicit Trade Plan ownership, cross-revision provenance, and operator explainability without collapsing evidence, competency state, policy, eligibility, and operating restrictions into one score or lock.
