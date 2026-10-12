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


## 2026-10-09 — Progression attainment is historical truth separate from current eligibility

**Status:** Accepted

A previously cleared progression boundary remains a historical fact even if current eligibility later becomes BLOCKED.

C4 distinguishes:

- Competency State,
- current Eligibility,
- historical Progression Attainment,
- Development Direction.

An AVAILABLE -> BLOCKED transition under the same plan/policy may be detected as **Eligibility Loss**, but this does not automatically imply competency regression.

**Confirmed Competency Regression** requires explicit human review.

Trade Plan revision changes that require fresh contextual evidence are treated as **Revalidation Required** when the underlying competency may still be intact.

Never-attained insufficiency is not regression. Voluntary downward movement is non-punitive and preserves prior attainment. Temporary news/risk/personal/account restrictions remain outside progression-regression semantics.

Recovery uses the same published progression policy. C4 does not introduce a separate hidden recovery score.

Even after human-confirmed regression, Competency State, Evidence Maturity, and Development Direction remain deliberate separate state changes in v0 rather than automatic mutations.

**Rationale:** historical truth, skill state, present permission, and next-work intent are different concepts and must remain explainable rather than collapsing into one red/green progression state.


## 2026-10-10 — Review / Development should preserve depth while reducing simultaneous exposure

**Status:** Accepted

Review / Development is becoming cognitively expensive because too many legitimate controls and concepts are visible at once.

The accepted presentation model is:

- Overview
- Evidence
- Interpretation
- Progression
- Practice / Launch

This is a presentation-only reorganization. Existing domain objects, repositories, progression semantics, competency state, evidence maturity, attainment, regression review, and Trade Plan ownership do not change.

Overview is compact and read-only. Detailed work areas use progressive disclosure. Saved-state summaries remain visible while editors are hidden. Technical terms should provide quiet contextual definitions. Major areas receive stable UI anchor IDs to support future guided testing/navigation.

Smoke-test instructions should increasingly specify **Where / Look for / Expected** so manual acceptance does not require scanning the full interface.

Full-text Review / Development search and automatic smoke-runner -> Cockpit deep-link/highlight plumbing are deferred until the simpler structure is proven.

**Rationale:** operator cognition is part of system safety and learning quality. Dense governance capability should not consume the working memory needed for analysis, learning, and deliberate decision-making.


## 2026-10-10 — Progression gating applies at new upward environment starts, not continuous runtime policing

**Status:** Accepted

C5 integrates the progression-governance substrate into the operator loop.

Accepted behavior:

- progression eligibility governs new upward environment starts,
- a legitimately started run is not auto-terminated or auto-demoted if progression state later changes,
- progression eligibility remains distinct from setup/trade authorization,
- progression logic must never block exit/flatten,
- temporary operating/safety restrictions remain a separate future layer,
- BLOCKED may expose deterministic guidance from explicit requirement reasons but must not create inferred coaching,
- BLOCKED may stage the recommended lower environment but never auto-start it,
- lower-rung staging preserves semantically valid Study question/competency focus where possible and creates no regression/demotion event,
- Review / Development > Progression is the focused explanation surface,
- Human Certification remains authoritatively edited under Rules / Safety,
- restore/resume of an existing run does not re-run launch gating or create duplicate Progression Attainment,
- C5 integration state is derived on demand rather than persisted as mutable truth,
- Alpha 0.7 remains without a real progression policy.

**Rationale:** progression governance should constrain the correct transition while preserving historical truth, operator agency, downward movement, execution safety, and separation from trade authorization.


## 2026-10-10 — Context facts, technician interpretation, and Trade Plan restrictions remain separate

**Status:** Accepted

Milestone E will mature context through distinct layers:

- raw market-time/QT facts,
- external event/schedule facts,
- technician AMDX/XAMD interpretation,
- expected-vs-observed Review comparison,
- explicit Trade Plan context rules,
- derived warnings/restrictions,
- setup/trade authorization.

Accepted consequences:

- raw QT alignment never implies direction, probability, ranking, or authorization,
- event presence never automatically implies No Trade,
- holidays/early closes are not the same concept as QT structural Distortion,
- expected-vs-observed mismatch is descriptive and does not automatically create competency evidence,
- Replay/Historical event context must follow selected historical market time,
- run context should preserve historical event/schedule provenance rather than be silently rewritten by later provider changes,
- external event normalization is provider-neutral and preserves native/provider provenance,
- red-folder maps to High impact only when the source explicitly supports that meaning,
- Trade Plan context rules are the only layer allowed to turn context facts into warnings or entry restrictions,
- v0 rule effects are Informational / Warning / Block New Entry / Stand Down Day,
- context rules may be environment-sensitive,
- unknown/unavailable context is distinct from no event,
- provider selection is deferred until the normalized contract and rule semantics are stable,
- Friday Asian Range no-Monday-high-impact-news is a validation case for generic context predicates, not event-service hardcoding,
- justified schema migrations are allowed to preserve historical truth.

**Rationale:** context should become richer without creating hidden directional inference, accidental authorization logic, or provider-coupled domain semantics.


## 2026-10-10 — E4 presents stored context without refreshing or interpreting policy

**Status:** Accepted v0 implementation within the existing Milestone E presentation contract; operator reported manual testing complete and acceptance granted on 2026-10-10

TDA, Watch, and Review share a read-only compact context card with bounded detail. Availability is always visible. Normal startup without a provider remains Not Configured; fixtures are isolated from production data.

Watch uses explicit run market time to select the next recorded event time, retaining simultaneous-event visibility and schedule facts for the captured day. It does not invent an event-duration window or a warning threshold. Cancelled, postponed, and released records remain in full detail but are not presented as upcoming. When market time is absent or outside the snapshot window, the surface says so instead of claiming no remaining events.

Rendering and restore read the persisted snapshot. Neither refreshes a provider, rewrites event facts, evaluates context policy, nor mutates authorization or competency evidence.

**Rationale:** E3 established historical provenance. E4 makes that provenance usable without introducing a fresh-feed illusion or smuggling future E5 rules into presentation.

**Consequences:** details expansion is transient UI state. The dense Premarket Thesis station and expanded details allow scrolling so controls remain reachable; other compact Focus navigation is retained. Schema remains v35 and Trade Plan Alpha 0.7 is unchanged. Real provider integration, snapshot revision history, and declarative context rules remain later work.


## 2026-10-10 — E5 makes context policy explicit and historical

**Status:** Accepted v0; all eight focused operator checks passed and were pushed on 2026-10-10

**Decision:** Context rules are immutable versioned Trade Plan definitions, snapshotted into each Trading Run in schema v36. Rules specify conjunctive clock/event conditions, environments, matched effect, unknown effect, and rationale. Evaluation is read-only and uses normalized stored facts and explicit market time. Blocking effects participate in candidate entry authorization independently of manually cleared gates; informational/warning effects never grant authorization.

**Rationale:** A missing calendar cannot honestly mean no news. An incomplete day snapshot cannot prove a clear week. Explicit selectors avoid provider-native text inference. Stored definitions preserve the rules governing historical runs when the current plan changes.

**Consequences:** TDA, Watch, and Review explain result states, effects, reasons, and event IDs. Exits/flatten remain outside entry authorization. Stand Down Day does not conclude the run automatically. Alpha 0.7 remains published unchanged, with its existing manual trading-day gate and no automatic context policy. The example's live/eval/funded versus paper distinction cannot be inferred from run environments; actual policy adoption needs explicit account applicability, configured normalization/coverage, and a new plan revision. No warning buffers, FOMC duration, NFP coverage, readiness thresholds, real provider, or no-code policy editor are invented.

**Supersedes:** E4's presentation-only boundary only for explicitly configured snapshotted rules; unconfigured Alpha 0.7 behavior and historical event snapshot ownership remain intact.


## 2026-10-10 — E6 provider preference and sequence reconciliation

**Status:** Operator provider preference accepted; sequence clarified from the current Project State and accepted implementation sequence.

**Decision:** Forex Factory is the first-choice economic-calendar source because the operator already uses it and has an account; paid or unpaid access may be assessed. Trading Economics remains an evaluated alternative, not a selected dependency. Account membership does not imply a documented API or historical entitlement.

E6 means real provider integration. E7 means model-specific context predicates. Review/evidence provenance is cross-cutting context work rather than a conflicting E7 slice. The narrative headings in `CONTEXT_MATURITY.md` are reconciled to that sequence without changing roadmap order.

**Rationale:** honor the explicit operator source preference and remove known handoff ambiguity before provider implementation.

**Consequences:** `E6_PROVIDER_ASSESSMENT.md` records supported weekly-export observations and open contract gaps. Its local-import-first implementation scope is proposed, not operator accepted. No provider is wired into normal startup, no data access is purchased, and no automatic context policy is published.

**Supersedes:** the ambiguous narrative E6/E7 numbering only; the accepted implementation sequence and context-layering boundaries remain intact.

## 2026-10-10 — E6 alternative providers accepted for assessment

**Status:** Accepted operator source-selection flexibility; provider/implementation selection remains open.

**Decision:** Consider alternate calendar sources when they make implementation easier or safer. Forex Factory remains the operator's familiar first choice, but is not an exclusive dependency.

**Rationale:** verified export limitations justify evaluating a better documented identity/timing/provenance contract before adapter work.

**Consequences:** `E6_PROVIDER_ASSESSMENT.md` compares Trading Economics, FMP, and scoped official BLS/Fed/CME schedules. Trading Economics is an engineering recommendation for capability validation, not an accepted paid dependency or proof of historical as-of coverage. No purchase, provider wiring, automatic source fallback, or Trade Plan rule change is authorized by this assessment decision.

**Refines:** the earlier Forex Factory preference; it does not change E6/E7 order or historical snapshot ownership.

## 2026-10-10 — E6 recurring-cost constraint

**Status:** Accepted operator budget constraint; acquisition/implementation choice remains open.

**Decision:** Trading Economics at approximately $200/month is unaffordable and must not be assumed as an E6 dependency. A smaller recurring fee may be acceptable, but no exact maximum, plan purchase, or annual commitment has been accepted.

**Consequences:** assess endpoint-specific entitlements and billing frequency rather than headline provider prices. `E6_PROVIDER_ASSESSMENT.md` retains the free Forex Factory export path and records lower-cost FMP, Finnhub, and EODHD candidates. FMP is a proposed first paid candidate, not an accepted subscription or proof of safer feed semantics. Preserve the provider-independent uncertainty/provenance architecture.

**Supersedes:** the earlier recommendation to validate Trading Economics first under an unknown budget. The technical field comparison remains useful history, not the current acquisition priority.

## 2026-10-10 — E6 local source captures and honest provider claims

**Status:** Implemented and operator accepted on 2026-10-10; all nine focused smoke checks PASS in `df4cac894f7e697bf65793c5f031265af5bdd9d4`, with the local automated suite reported as 425 passed. Merged through PR #59 (`aaa931153f165b8ebb90c43126e00b6cd07beeeb`) after assessment PR #58.

**Decision:** Start E6 with the supported weekly JSON export, manually imported and previewed outside active operation. JSON preserves explicit offsets; the inspected XML's unlabeled timezone is insufficient for this first adapter. Each import creates a separate immutable local capture with original JSON, byte digest, import/file provenance, declared UTC week, adapter/mapping revisions, native rows, and explicit limitations. Selection is deliberate for new runs and resets to Not Configured on restart. Existing run snapshots remain authoritative.

**Rationale:** A successful query and its requested dates do not establish source completeness. The provider result now carries separate coverage bounds, completeness, explicit selector scope, and a source basis. Negative predicates require that claim to cover the entire rule window and scope. Positive exact facts may be recorded beyond the requested day when the source supplies week context. Missing legacy coverage/precision reads as Unknown without rewriting stored JSON during migration.

**Consequences:** Schema v37 adds insert-only capture storage. Forex Factory's timing precision, status, normalized event types, market applicability, and completeness remain unverified. Native Low/Medium/High impact and Holiday category mappings are explicit and revisioned; currency labels do not silently become affected-market mappings. IDs identify capture-local rows, not provider occurrences across rescheduling. Uncertain-time rows from the declared source week are retained rather than discarded by clock filtering; Watch does not advertise them as precise upcoming times or confirmed day schedule exceptions. Out-of-week requests are Unavailable, with the attempted capture provenance retained. Imports do not establish historical as-of knowledge. Alpha 0.7 and its manual gates remain unchanged.

**Deferred:** XML/ICS/CSV adapters, network acquisition, paid subscriptions, automatic latest-capture selection/freshness thresholds, within-run refresh, provider occurrence continuity, normalized model predicates, and published automatic trading exclusions.

**Refines:** the E3 tuple provider seam and E5 query-bound absence assumption. Synthetic fixtures explicitly certify their own scope; real exports never inherit that claim.

## 2026-10-10 — E7 explicit model scope and context predicates v0

**Status:** Implemented on `feature/context-maturity-e7-v0`; all nine focused operator checks PASS on 2026-10-11; merged through PR #60 as `f57794cff6f128830655b458e999fd8f72038280`.

**Decision:** Extend the existing plan-owned context-rule contract with explicit playbook IDs, event absence, selected NY calendar weekdays and an explicit relative calendar-week offset. Offset 0 is the calendar week containing the explicit market reference; negative/positive offsets select earlier/later weeks. Rules retain separate matched, not-matched and Unknown effects. The new not-matched effect defaults to no effect for old rules; empty playbook scope preserves run-wide E5 semantics.

**Rationale:** Model conditions must remain generic and explainable. Absence inverts known presence/absence only; Unknown is never inverted into evidence of no events. A negative event conclusion requires complete source coverage of every selected window and selector dimension. Uncertain timing/status/selectors remain conservative. Day bounds use America/New_York civil dates, including DST, rather than fixed UTC durations.

**Consequences:** Plan definitions validate scoped playbook references. Candidate evaluation uses the stored Playbook source ID, never a display name or a Custom setup's incidental source ID. Scoped effects affect only targeted candidates; Stand Down Day remains run-wide and cannot be configured on a scoped rule. TDA/Watch/Review show candidate scope, revision, resolved dates, outcome/effect and event IDs from stored rules/facts. Existing schema v37 JSON snapshots carry the additive fields; legacy rules read with their original scope/effect behavior. Evaluation does not grant entry, change playbook definitions or competency state, query a provider, or mutate history.

**Open:** Friday Asian Range's no-Monday-high-impact-news condition is a validation use case, not an adopted rule. Preceding versus following Monday, normalized market applicability and final policy effects require explicit Trade Plan decisions. The demo labels its current-week Monday and following-week offset explicitly. Forex Factory captures cannot certify event absence. Alpha 0.7 publishes no new rule or threshold.

**Refines:** E5 run-wide positive-event predicates; preserves E6 explicit coverage/uncertainty and immutable source/run ownership. No readiness percentage, account applicability, automatic freshness policy, order execution or source mapping is introduced.

## 2026-10-11 — Coupled AMDX domain foundation and versioned criteria

**Status:** Operator reviewed the cycle contract and authorized proceeding with the narrow foundation. Pure domain/action/archive implementation is developer verified; production persistence/renderers are not integrated.

**Decision:** Model a containing quartet with stable quarter identities, explicit anchors, coupled AMDX/XAMD structural consequences, unresolved X subtype and visible conflicts. Preserve accepted interpretation revisions automatically through a shared action contract, with run/channel/branch/cycle isolation and explicit timestamps. Keep recorded features, local behavior, assigned roles and governing profiles distinct. Definition/evaluation snapshots retain plan/rule revisions, scoped inputs, source/availability and reasons for replay/comparison.

**Rationale:** One quarter assignment constrains its siblings, while subjective disagreements and competing rule methods require traceable alternatives rather than independent fields or opaque scores. The complete rulebook is not needed before the foundation; only executable criteria require operational inputs/targets and resolver semantics.

**Implementation choice:** the first named resolver is Cycle Profile Priority. Smaller integers govern; all equally best-priority assigned-role matches constrain the quartet. Competing unknowns at equal/higher priority leave the result unresolved, ties can conflict, and lower-priority/local-behavior outputs remain in the trace. This is a declared developer framework policy, not an adopted trading method or universal weighting formula.

**Consequences:** versioned JSON history/evaluation save/reload is verified without changing schema v37, Alpha 0.7 or the desktop. Actual application writes, plan publication, higher-order temporal mapping, operational classifiers, Review default, source adapters/sensors and coverflow rendering remain downstream. News interpretation/research is part of the definition direction, but no correlation or provider as-of capability is assumed validated.

**Supersedes:** independent sibling-role assumptions and the separate Record-click target in the earlier intraday prototype. Existing legacy flat QT storage/behavior is preserved until reviewed repository integration; no historical interval claims are invented.

## 2026-10-11 — Transactional run-owned AMDX history

**Status:** Operator authorized proceeding after the pure foundation checkpoint. Implemented in schema v38; developer storage/compatibility verification recorded in `PROJECT_STATE.md`. Production phase-entry UI and operator usability review remain downstream.

**Decision:** Store accepted-action claims and criteria evaluations in separate append-only tables owned by existing saved runs. Registry rows protect stable cycle identities and exact definition revision content. Ordinary mutable run snapshot saves do not own or overwrite these histories. New AMDX data is absent on legacy runs until an explicit action occurs; never synthesize interval history from flat QT values.

**Rationale:** Automatic durable capture must preserve earlier interpretations, survive restart and prevent stale editors or ordinary application saves from losing records. The interpretation and its input/rule basis should be independently reviewable without choosing a default Review comparison.

**Consequences:** shared actions own an immediate SQLite transaction, validate the inspected scope head and append/commit once. Exact retries are idempotent; changed IDs/content, stale heads and inconsistent ownership/bases are rejected. Cycle/definition registration and result insertion roll back together on failure. An unrelated pending caller transaction is rejected rather than committed or rolled back. SQL UPDATE/DELETE/REPLACE guards protect existing rows. Explicit evaluation basis IDs are optional and never select a Review default. Definition snapshot identity includes Candidate/Published status; actual Trade Plan editing/publication remains separate.

**Compatibility:** v37 → v38 is additive and atomic, with old run/capture data preserved and actual accepted-E6 restoration verified through the normal application. Alpha 0.7, existing gates and competency behavior remain unchanged. New Watch/TDA bindings, higher-order mapping, note drafts, Review defaults and final UX remain the next/separate work.

**Refines:** the previous pure JSON archive contract into actual database persistence. No manual Save/Record obligation, automatic cycle-completion gate or inferred legacy history is introduced.

## 2026-10-11 — Minimal shared Watch/TDA AMDX entry

**Status:** Implemented and developer verified. Operator accepted all six functional checks 245–250 on 2026-10-11, pushed in `17b874b2c7fb48f2b35d2e30b9e2a6affe019072`; PR #61 is ready for review. This does not constitute final component/layout, replacement-action or classifier acceptance.

**Decision:** Use one shared Working AMDX panel in the normal runtime, outside the content scroll area. Daily and active-session quartets remain near the input target, with higher legacy/derived QT context quietly visible. Four direct role choices and a secondary subtype/uncertainty/clear menu invoke committed repository actions. Current-quarter input follows time after successful entry; a deliberately inspected target stays pinned. Mouse/menu gestures pin their scope/reference through a clock boundary.

**Rationale:** fulfill the accepted immediate-recording and in-place Watch contracts without a separate Save step, repetitive grid entry or forced return to TDA. Reuse the same data/actions for the analytical path and restore; preserve uncertain/conflicting interpretations and distinguish entered anchors from implied siblings.

**Consequences:** recording reports success only after commit, retains the last committed view on failure, rejects/reloads stale scope without replay and disables recording on unavailable history. Earlier intraday flat inputs become read-only in the application-backed path; higher fields retain their legacy behavior/provenance. The shared panel remains visible in Market Review as working context, with no observed-cycle edit or default comparison adopted.

**Layout/navigation choice:** fixed orientation leaves the rest of the runtime scrollable; in the application-backed path the wheel scrolls content, while mouse Back/Forward and station controls still navigate. Standalone legacy runner wheel behavior remains. This narrow fit choice avoids clipping the role controls or compressing station guidance; final context-specific rendering remains open.

**Review path:** `tools/amdx_entry_demo.py` opens a retained separate normal-window Replay sandbox; the same command restores its committed run/claims/reference. Its explicit demo reference action changes time only. `AMDX_ENTRY_OPERATOR_GUIDE.md` maps six hands-on checks to smoke items 245–250. No synthetic classifier, weighting scale, competency evidence, entry/completion gate, Study-first startup or coverflow implementation is introduced.

**Refines:** the persistence-next UI boundary into an implemented functional surface. Actual price/news criteria, higher-order cycle mapping, note drafts and contextual Review/Study presentation remain separately defined work.

## 2026-10-11 — Cockpit as the primary desktop workspace

**Status:** Accepted operator override; future layout target, not yet implemented geometry.

**Decision:** Plan around a 16:9 Cockpit workspace taking the majority of the operator's ultrawide display, or the full display otherwise. The operator will arrange charts, journals and other daily information around it. The Cockpit is the primary focus of the working layout.

**Rationale:** broader spatial context supports the desired nearby overview/detail relationship and makes the session/day and active 90-minute quartets easier to orient within the full process. Low clutter, low motion and low memory burden still govern what each context promotes.

**Consequences:** future Watch, TDA, Review and Study renderers should use this primary-workspace target rather than optimize for an undefined small companion window. No exact resolution, fixed aspect-ratio enforcement, new minimum window size or screen-layout implementation is adopted in this documentation checkpoint. TradingView remains the charting workstation.

**Supersedes:** `PROJECT_REQUIREMENTS.md` §15.2's compact desktop-companion footprint.

## 2026-10-11 — Native AMDX entry feedback and structural choice limits

**Status:** Operator direction recorded; exact replacement-action semantics pending, current UI unchanged.

**Decision:** Normal phase entry should be limited to structurally valid positions across both quartet orders: Q1 A/X, Q2 A/M, Q3 M/D, Q4 D/X. The operator prefers a new valid entry to revise the working quartet without locating an older conflicting anchor. Preserve earlier interpretations as immutable history; retain explicit analytical alternatives/conflicts separately. The control set must still permit switching order in one deliberate entry.

**Rationale:** searching for an anchor to clear makes the operator reason about the form rather than the quartet's meaning. Impossible phase choices do not belong in ordinary entry. Session/day plus active 90-minute visibility and quiet hover explanations received positive feedback; more visual renderers remain future work.

**Consequences:** refine the shared action before implementing the preferred quartet replacement flow. Other compatible anchors, X subtype, Unknown/Not Applicable/clear and deliberately retained alternatives need explicit semantics. Existing stored claims/evaluation conflicts keep their original meaning; future actions must carry their revision basis. This feedback alone did not supply individual smoke statuses or final layout acceptance. The subsequently pushed checklist records all six functional checks PASS in `17b874b2c7fb48f2b35d2e30b9e2a6affe019072`; the new action/geometry directions remain unimplemented.

**Refines:** the original native panel's unrestricted role buttons and per-quarter anchor-accumulation interaction target; preserves domain uncertainty, parent/child separation and historical truth.

## 2026-10-11 — Versioned one-entry working-quartet revision

**Status:** operator authorized implementation after the ten-case action review. Implemented on `feature/amdx-quartet-revision-v1`; four follow-up operator checks 251–254 are accepted from the completed smoke report on 2026-10-12. PR #61's initial six PASS results remain separate.

**Decision:** normal Expected/working input uses `revise-working-v1`. One structurally valid entry selects AMDX/XAMD, retains compatible technician anchors and retires incompatible ones from the active basis into immutable prior history. The selected quarter's old anchor is replaced. X subtype remains only at the same compatible X quarter; switching order does not copy it to the new X position. Unknown and clearing are selected-phase operations. Not Applicable is a separate whole-quartet judgment that retires phase anchors; a valid phase restores applicability directly. Clearing never revives retired anchors.

**Rationale:** ordinary interpretation revision should take one meaningful entry, without manual conflict cleanup or a separate Save step. The operator can change the working hypothesis while retaining earlier judgments and independent classifier disagreement for later analysis.

**Consequences:** normal controls and the shared action enforce Q1 A/X, Q2 A/M, Q3 M/D, Q4 D/X. Unknown is displayed alongside a conditional implied role when another anchor still supports the order. Identical already-explicit semantic input creates no extra interpretation claim; first explicit selection of an implied phase remains a judgment. Original accumulation actions retain their v1 replay meaning, with v2 claims carrying action policy, incoming choice, prior basis, retired IDs and separate applicability. Analytical conflicts and evaluation snapshots remain independent. Unsupported mixed rule/technician working bases are rejected rather than silently overwritten.

**Storage:** schema v39 adds immutable command receipts and a forward-version guard. Receipts reserve identities for changed actions and no-ops, so exact retries return their original result after later edits. Cycle registration, optional claim and receipt commit atomically. Existing claim bytes remain unchanged through v38 migration; failed migration rolls back. Older v38 apps reject v39; use an original unmigrated copy for old-code comparisons.

**Supersedes:** the original accumulation action as the normal Watch/TDA entry command and unrestricted phase choices. Preserves generic accumulation for original histories/analytical scopes, fixed structural rules, parent/child independence, failure/stale/gesture behavior and Alpha 0.7. Final primary 16:9 rendering, higher-order mapping, note drafts, classifiers and Review default remain separate.

## 2026-10-12 — Working-quartet acceptance and direct X subtype entry

**Status:** operator completed the four-check follow-up smoke and reported a smoother flow. Checks 251–254 are PASS by that completion report; no individual logs or new local runtime details were supplied. PR #62 is ready for review, stacked on unmerged PR #61. Source is unchanged from the 587-pass developer checkpoint.

**Decision:** in the mature renderer, X(C) and X(R) are each one-click choices from the active entry target, without opening a subtype menu first or adding a confirmation/Save step. Shared actions also support future direct keyboard/macro-pad bindings. Structural validity, target/gesture identity, persistence and failure handling remain intact.

**Rationale:** subtype selection is frequent working interpretation input; the extra menu action adds motion and process burden. The current menu remains interim. Exact control arrangement and bindings remain open alongside the primary 16:9 renderer.

**Next contract:** identified observed-profile/expected-profile comparison, prepared in `AMDX_REVIEW_COMPARISON_CONTRACT_REVIEW.md`. A first-expectation default remains proposed, rather than inferred from smoke acceptance.

## 2026-10-12 — Watch orientation now; change research later

**Decision:** normal Watch shows the current working AMDX stack and the technician’s position within it. Prior stack versions and before/after or expectation comparison panels do not need visible space there. Whole-stack accessibility, current uncertainty, quiet hover context and efficient direct entry remain. Immutable revisions continue to be retained automatically.

**Rationale:** the working meaning now supports the operation at hand. Visible change tracking adds clutter and mental work during the day. Later purposeful Review/Study may investigate associations between interpretation changes, identified price-action events and features the technician noticed.

**Consequences:** historical comparison is a context-specific later tool, not a daily viewing/capture obligation. No extra explanation or confirmation step is introduced. Event association, sample definitions and aggregation remain unimplemented; no causal conclusion or likelihood is invented. This clarifies presentation ownership, not acceptance of a first-versus-latest comparison default.

## 2026-10-12 — Explicit later-Review pairing foundation

**Status:** operator ready to continue after syncing the accepted quartet checkpoint. Narrow domain/archive foundation implemented on a separate follow-up branch. Database and UI integration remain downstream; no first/latest default is adopted.

**Implementation choice:** a comparison explicitly identifies an Expected claim or missing basis, an Observed claim, run/branch/quartet, preceding comparison, recording/reference timing and named pairing policy. Same-run/branch/cycle ownership and channels are validated. Alternate pairings append without rewriting either source or the earlier pair. Source-history extension preserves its prefix; missing baselines never attach retroactively. Exact retries preserve the original result and changed identities or stale heads reject.

**Consequences:** archives replay original v1/v2 claims and validate comparison scope/chronology/predecessors. Descriptive order relation and X subtype remain separate; uncertain/conflicting/inapplicable states are retained. Market-reference position is not evidence of a live forecast. Schema v39, Alpha 0.7, existing runtime and all operator smoke records remain unchanged. The pure contract does not yet provide database durability, concurrent-writer protection or observation-plus-pair atomic application commits.

**Boundary:** this supports later purposeful Review/Study without adding Watch history or comparison. Event links/aggregation, observed-entry gestures, Review defaults, primary 16:9 rendering and one-click X subtype controls remain separately scoped work.

## 2026-10-12 — Durable explicit Review pairings

**Status:** operator authorized proceeding from the pure foundation. Backend integration implemented on `feature/amdx-review-persistence-v0`; no baseline default or contextual input widget is adopted.

**Decision:** schema v40 stores immutable run-owned comparisons and original Pair / ObserveAndPair command receipts. Record an observed action, selected expected basis or explicit missing basis, comparison and receipt in one owned transaction. Alternate pairings refer to the same immutable observation and preserve earlier pairings. The existing Observed accumulation semantics remain unchanged.

**Consequences:** take the writer reservation before checking observed/comparison heads; exact original retries work after later changes. IDs cannot cross claim/working/Review boundaries. New cycle/source/pair/receipt inserts roll back together. Standalone readers use a consistent snapshot across sources, comparisons and receipts, preventing a concurrent commit from producing a false missing-basis result. Caller-owned transactions are not committed or rolled back.

**Compatibility:** atomic v39 migration preserves run/claim/working-receipt bytes and semantic no-op retries, adds no inferred history and rejects older v39 bootstrap on v40. Ordinary run saves cannot truncate comparisons. Existing Watch/UI, Alpha 0.7 and all operator smoke records are preserved. Event association/statistics and renderer/default decisions remain later work.

## 2026-10-12 — Accepted observed correction; comparison deferred

**Decision:** the operator accepted one-entry observed quartet correction, independently versioned and preserving earlier judgments, plus optional comparison with no automatic first/latest pairing during routine observed capture. A deliberately selected same-cycle comparison basis carries through corrections until changed/cleared.

**Priority:** comparison is lower priority and belongs in Study/Review for purposeful exploration if needed. Do not add a comparison option or launch route to Watch. Further comparison UI/research expansion is deferred; current-stack orientation and efficient AMDX entry remain the focus.

**Consequences:** retain the completed v40 persistence substrate. The next shared-action refinement supports observed entry without requiring comparison controls or a baseline choice. Preserve original observed accumulation replay when introducing the new versioned action. Final controls/layout remain separate; no source, schema, operator smoke or merge change accompanies this acceptance record.

## 2026-10-12 — Versioned observed quartet revision

**Status:** operator accepted the entry behavior and authorized proceeding. Shared action/domain/storage implemented on `feature/amdx-observed-revision-v1`; native Review binding remains downstream.

**Decision:** use independent `revise-observed-v1`, sharing the accepted structural correction logic with Expected working revision without changing its policy. One valid entry keeps compatible manual anchors and retires contradictions, with the same subtype/Unknown/applicability/clear semantics. Earlier observed judgments remain immutable; Expected and parent/child context remain independent.

**Persistence:** schema v41 adds immutable observed-command receipts. Changed source/pair metadata/receipt commit together; unchanged meaning reserves both identities without a source/pair revision. Snapshot counts preserve exact replay of changed/no-op original requests after later edits. Scoped heads and cross-action identity checks remain explicit; failures roll back the entire action. Existing selected basis is carried, or None remains unselected; no first/latest fallback or comparison UI is added.

**Compatibility:** version-3 observed claims retain their own action policy. Original v1/v2 payloads and old v40 record bytes are preserved. Atomic v40 migration adds no guessed history; older bootstrap rejects v41. Existing legacy analytical accumulation and exact old retries remain valid, but new accumulation cannot follow an observed revision in that same scope. Alpha 0.7 and process gates are unchanged.

## 2026-10-12 — Native observed quartet entry

**Status:** accepted entry behavior implemented; checks 255–259 operator PASS on 2026-10-12 from “All points passed,” following clarification/retest guidance.

**Implementation:** the shared fixed AMDX panel edits Expected/working in TDA/Watch and Observed/working in Post-Market Review. The saved Trading Day supplies Review's date; all four sessions are available without following today's clock into another day. Missing saved identity disables capture. One accepted choice commits immediately with both observed/pair heads pinned through its gesture. Failures and stale writes retain meaning, with no automatic replay; read failure disables writes while keeping committed context. Direct X(C)/X(R) buttons now satisfy one-click entry in both channels.

**Presentation:** current observed profiles, entered/implied distinctions and structural hover context remain near the input. The application-backed path hides flat intraday observed controls and the old descriptive comparison list while preserving stored values and higher legacy fields. No AMDX comparison/history control or Watch launch route is added. Selected pairing provenance, if already present, is retained quietly by the shared action; routine capture has no first/latest default.

**Boundary:** schema v41 and Alpha 0.7 are unchanged. `AMDX_OBSERVED_ENTRY_OPERATOR_GUIDE.md` supplies a retained synthetic normal-window Review fixture and new checks 255–259. Existing 254 records retain their results. Final 16:9 geometry, higher-order cycle mapping, rule classifiers, shortcut assignments, notes drafts and purposeful Study/Review comparison remain downstream. The later functional report accepts this narrow Review entry behavior. It does not accept the final renderer or authorize a merge.


## 2026-10-12 — Run-owned Review date correction

**Status:** correction of the accepted reviewed-scope contract, implemented with focused 77-pass and complete module-isolated 744-pass validation; focused check 260 pending.

Review's date resolves from the particular run's preserved starting market reference, not its latest advancing clock or an unchecked container label. Older runs lacking that reference may use an explicit saved-Day fallback; malformed original references or absence of both sources disable recording. A valid run reference can restore an older misgrouped run without rewriting container labels or claims, and its differing provenance is explained in the heading hover. In-flight older-date targets cannot record after provenance changes.

The existing one-futures-day container boundary is enforced at additional-run launch before process/TDA reset: a different-date request or undated existing container with prior runs is rejected with the existing complete-day/new-day path. Same-date additional runs remain allowed. This introduces no classifier, comparison default, history panel, new confirmation/save obligation, schema or published-plan change. Final renderer/Study work remains downstream.
