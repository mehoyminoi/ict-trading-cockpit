# ICT Trading Cockpit — Product Requirements & Milestone Roadmap

**Status:** Accepted reconciled product requirements and milestone roadmap  
**Reconciled:** 2026-10-08  
**Role:** Canonical current product requirements and milestone roadmap.

Companion documents:

- `docs/PROJECT_STATE.md` — exact current implementation checkpoint,
- `docs/DECISION_AUDIT.md` — supersession/conflict ledger,
- `docs/DECISIONS.md` — durable accepted architectural decisions,
- `docs/PROJECT_EVOLUTION.md` — chronological architecture history,
- `docs/HANDOFF.md` — continuity protocol,
- `docs/SMOKE_TEST.md` — manual acceptance record.

This document describes **current intended product truth**, not the chronological history of every idea considered. Older requirements and transcripts remain historical evidence only.

---

## 1. Product mission

Build a local-first **trading process operating system** that makes discretionary trading more structured, repeatable, analyzable, teachable, and deliberately boring.

The Cockpit is not primarily a P&L dashboard, not a replacement for TradingView, and not merely a trade journal. Its core purpose is to make the trading process explicit, executable, reviewable, and improvable.

A fully compliant **No Trade / Stand Down — Process Followed** outcome is a successful operating result.

The long-term product should help the operator:

1. form and record a top-down market interpretation,
2. translate that interpretation into concrete things to watch,
3. operate with low interaction cost while the market unfolds,
4. recognize and evaluate one or more valid opportunities,
5. authorize entry only when the versioned Trade Plan permits it,
6. review what actually happened without rewriting history,
7. turn repeated evidence into competency and process improvement,
8. progress through Study, Rehearsal, Validation, and Execution based on evidence rather than impulse,
9. compare performance and process adherence across revisions.

---

## 2. Core product principles

### 2.1 Process over P&L

Profitability matters, but it does not define whether the process was followed.

Performance and process adherence are separate analytical dimensions. A profitable violation is not automatically good process, and a process-compliant no-trade or loss is not automatically a process failure.

### 2.2 Structured records are authoritative

Trade summaries, Study Find text, screenshots, dashboards, share cards, Trilium notes, and future reports are derived views of structured records.

Important context must not exist only in generated prose or images.

### 2.3 Operate guided; design flexibly

The operating surface should reveal what is useful **now**.

Configuration, revision publishing, deeper research, evidence synthesis, and process design belong outside the active market-operating flow.

### 2.4 Preserve honest incompleteness

Unknown, not assessed, incomplete, overridden, failed, neutral, and false are not interchangeable states.

Intentional incompleteness and overrides are useful evidence and must remain visible.

### 2.5 Revision control is part of the product model

A process revision is not merely a software version.

Trade Plan definitions, Playbooks, process/workflow definitions, management/risk/safety rules, templates, and other behavior-defining artifacts should carry explicit revision identity when historical interpretation depends on them.

A published authoritative revision must not be silently mutated after use.

### 2.5A Stable vs candidate Trade Plan revisions

A proven/stable Trade Plan revision must be protectable as a trusted operating baseline while later candidate revisions are developed beside it.

Required behavior and future architecture:

- a published stable revision remains immutable,
- candidate revision development does not mutate the stable revision,
- runs and evidence retain the exact Trade Plan revision that governed them,
- competency evidence must preserve enough definition provenance to distinguish unchanged definitions from materially revised definitions,
- newly added competencies begin collecting evidence from the revision that defines them,
- historical records must not silently be reclassified under a later competency meaning,
- retrospective mapping of historical records is an explicit provenance-bearing analytical act,
- future comparison between stable and candidate revisions should support evaluating whether added models, competencies, or rules actually improved the system.

Revisioning therefore protects both **historical truth** and **experimental isolation**. A successful `rX` can remain trusted while `rY` is studied, rehearsed, validated, accepted, or rejected.

### 2.6 Low-friction operation

During active market work, the Cockpit should reduce interaction cost rather than create another journaling burden.

Navigation, evidence capture, acknowledgement, and future hardware bindings should target shared application actions rather than duplicate domain logic.

### 2.7 Persistence is a product feature

The Cockpit should remember where the operator was, what had been completed, what remained, and what meaningful context had already been established.

Closing or restarting the application must not imply process completion.

### 2.8 Safety grows from explicit state

Trade authorization, progression eligibility, competency state, evidence maturity, and future execution locks should be inspectable and explainable.

Do not invent hidden readiness logic, arbitrary percentages, or automatic restrictions before the supporting evidence and Trade Plan rules exist.

### 2.9 Build from whole-loop use

Expand from friction observed while using the complete process, not from speculative form growth.

A hidden required control, awkward transition, or repeated context reconstruction is a workflow defect, not merely a styling issue.

### 2.10 Later detail does not override later priority

A richly discussed old feature is not automatically current work.

Current priority follows accepted architecture, the decision audit, and the active frontier—not the amount of historical discussion devoted to a feature.

---

## 3. Trade Plan and product structure

The Trade Plan is the authoritative definition of the trading process and its non-negotiable rules.

The high-level mental model is:

```text
TRADE PLAN
├── Foundation
├── Rules / Safety
├── Process
├── Playbooks
└── Review / Development
```

The relationship is:

- **Foundation + Rules / Safety** define the operating constraints.
- **Playbooks** define reusable valid methods/setups.
- **Process** operates the current system.
- **Review / Development** improves the system.

Review / Development is parallel to Process; it is not merely the last step after Post-Market Review.

Plan-owned content may include:

- competency definitions,
- Playbooks/models,
- setup and entry criteria,
- authorization gates,
- market/time restrictions,
- risk/loss limits,
- trade/day capacity,
- management expectations,
- no-trade conditions,
- future news/event restrictions.

Changing authoritative plan-owned definitions requires a new published Trade Plan revision.

Not every configurable artifact belongs in the Trade Plan. Summary templates, for example, are versioned Workbench configuration because they change presentation rather than trading permission/process meaning.

---

## 4. Process Blueprint and station model

The process model is:

`Process -> Mode -> Deck -> Station`

A Station represents an intentional analytical operation, not merely a form field.

### 4.1 Station responsibilities

A mature station separates:

1. **Action** — what must be done on the chart/workspace,
2. **Observe** — what the operator sees,
3. **Carry Forward** — what conclusion/state matters later.

Manual chart actions are valid process steps. The Cockpit should not pretend automation exists where it does not.

If a later indicator automates a manual operation, the Station can remain stable while its implementation changes.

### 4.2 Focus and Deck views

Focus and Deck are complementary projections of the same underlying process state.

- **Focus View** answers: “What am I doing right now?”
- **Deck View** answers: “Where am I in the whole analytical picture?”

They must not fork into duplicate workflows.

### 4.3 Navigation versus certification

Navigation does not imply completion.

Entered work can be Pending/In Progress while explicit completion remains a deliberate certification step.

Mouse/wheel/navigation behavior that has become operationally natural should be protected from accidental redesign unless repeated use justifies a change.

---

## 5. Trading Day and Trading Run

### 5.1 Trading Day

A **Trading Day** is the top-level operating container for one futures trading day.

Market-time reasoning uses **America/New_York**, and the futures day rolls at **18:00 ET**.

### 5.2 Trading Run

The normal case is one **Trading Run** spanning the operator's active decision process.

Market sessions such as Asia, London, NYAM, and NYPM are **context inside the run**, not mandatory run containers.

Additional Trading Runs are deliberate exceptions when a genuinely fresh process context is desired.

Do not restore the older architecture where every market session automatically becomes a separate Session Run.

### 5.3 Core operating loop

The core loop is:

`TDA / Analysis -> Watch -> Post-Market Review`

The loop is conceptually shared across training/execution environments even though the operating emphasis can differ.

### 5.4 TDA / Analysis

TDA establishes the working interpretation and what matters next.

It should support:

- draft/autosave/restore,
- explicit completion and intentional incomplete override,
- top-down bias/draw/thesis,
- market-time and QT evidence,
- multiple setup/model candidates,
- watch points / IF-THEN expectations,
- carry-forward into Watch and Review,
- revision-aware context.

TDA is not required to generate a trade.

### 5.5 Watch

Watch is a quiet operating surface, not a high-attention journal.

Its job is to:

- preserve active thesis/context,
- surface actionable watch points,
- track meaningful state changes,
- expose candidate/setup state,
- expose authorization state,
- allow low-friction evidence capture,
- preserve useful evidence into Review.

Ordinary observations may eventually become almost invisible interactions. Meaningful decisions/state changes should remain deliberate.

### 5.6 Return to Analysis

Return to Analysis is **deliberate, not restrictive**.

A reason for re-analysis is useful evidence, but returning should not carry punitive friction or imply failure.

### 5.7 No Trade / Stand Down

No Trade / Stand Down is a first-class process outcome.

A no-trade run may still contain:

- notable setups,
- thesis confirmations/invalidations,
- Study Finds,
- market observations,
- process evidence,
- useful review material.

Capital protection plus process adherence can represent a successful run.

### 5.8 Post-Market Review

Post-Market Review should hand the run back to the operator rather than display raw telemetry.

The preferred separation is:

1. **Market Review** — what was expected versus what changed,
2. **Process Review** — adherence, behavior, takeaway, and study follow-up.

Interpretation quality and process adherence remain independent.

Raw transition/button telemetry may remain stored but should not dominate the operator-facing review.

---

## 6. Interpretation outcomes and process learning

The system should distinguish an initial interpretation that remained materially accurate from one that changed.

Useful change categories include:

- **Missed critical information**
- **Cause unclear / Study needed**
- **External / exogenous event**

“Cause unclear / Study needed” means:

> I cannot currently explain the change from my present level of understanding; this should become a candidate for study.

It does not mean random or inherently unknowable market behavior.

Future process-weighted analytics may include:

- thesis stability,
- missed-information rate,
- unexplained/study-needed rate,
- external-event rate,
- process-adherence rate.

P&L remains available but secondary to the learning/process interpretation.

---

## 7. Playbooks, opportunities, and authorization

### 7.1 Playbooks

Playbooks are declarative, revisioned Trade Plan definitions.

They may define:

- applicability/context,
- standard IF -> THEN watch points,
- setup criteria,
- entry criteria,
- management/target guidance,
- risk/stop guidance,
- authorization requirements.

Trading Runs should preserve the rules/revisions actually used so historical records remain reconstructable.

Long term, authoritative Playbook editing should become configuration-driven/no-code where practical, with publish/revision boundaries protecting history.

### 7.2 Models are scaffolds, not cages

Named models such as the 2022 Mentorship Model or Silver Bullet are useful reusable structures but are not the only valid opportunity source.

The system should support:

- named Playbook candidates,
- multiple simultaneous candidates,
- technician-defined/day-specific candidates,
- later empirical or rule-derived temporal opportunities.

### 7.3 Opportunity state is multidimensional

Do not collapse:

- available,
- contextually relevant,
- temporally eligible,
- developing,
- authorized,
- expired/not-current

into one checkbox or score.

### 7.4 Authorization separation

Setup/candidate conditions and run-wide Trade Plan/safety gates are separate.

Semantics:

- **Pending blocks entry.**
- **Blocked blocks entry.**
- Only explicit **Clear** safety gates plus satisfied setup conditions can authorize entry.
- Authorization may expire when required context becomes stale.
- Exit/flatten must never be blocked by entry authorization logic.

Authorization means that the recorded process state permits entry. It is not itself order submission.

Future execution should follow an explicit lifecycle such as:

`analysis -> candidate -> evidence/checklist -> authorization -> arm -> submit -> manage -> close/flatten`

---

## 8. Environment, purpose, and learning progression

The accepted environment semantics are:

| Environment | Default purpose | Analogy |
|---|---|---|
| Historical Backtest / Lab | **Study** | Drills |
| Replay | **Rehearsal** | Scrimmage |
| Forward Test | **Validation** | Preseason/exhibition |
| Live | **Execution** | Real game |

### 8.1 Environment and intent are separate

- **Environment** = how market information/reality is being presented.
- **Purpose / Study Intent** = what the technician is trying to accomplish.

A Replay or Forward run may carry a focused study objective without becoming a Lab run.

### 8.2 Shared substrate, different emphasis

All environments should share the core process/data substrate:

- Trade Plan revision,
- market time,
- QT/AMDX context,
- TDA,
- observations/evidence,
- setup/authorization state,
- outcome,
- Review,
- provenance.

But the interface emphasis may differ:

- Study asks what is being investigated and learned.
- Rehearsal emphasizes integrated decision making without hindsight.
- Validation emphasizes live information flow without normal capital risk.
- Execution emphasizes compliant real-risk operation.

### 8.3 Evidence types should not be casually pooled

Historical Study samples, Replay/Rehearsal runs, Forward Validation evidence, and Live observations are different evidence types.

Future analytics/progression logic must preserve that distinction.

---

## 9. Eligibility, account context, and competency

### 9.1 Eligibility hierarchy

The order is:

1. **What level of practice is currently justified?**
2. **What is being done inside that level?**
3. **Only then, which account/capital context applies?**

Account type is not a peer to Lab/Replay/Forward/Live.

Expected mapping:

- Study -> no trading account,
- Replay -> no trading account,
- Forward -> Sim / Paper,
- Live -> Prop / Cash.

### 9.2 Progression behavior

Moving **up** the ladder should eventually require evidence.

Moving **down** should be frictionless and welcoming.

When justified Trade Plan rules exist, a foundational competency below requirement should route the operator back toward targeted Study rather than merely toward a lower-risk account.

The desired loop is:

`Lab teaches components -> Replay integrates -> Forward validates -> Live executes -> Review routes weaknesses back down`

### 9.3 Restriction reasons

Higher environments may eventually be unavailable for different reasons:

- **Eligibility regression** — evidence indicates a requirement is no longer met.
- **Temporary pause** — current personal/market/news/risk conditions do not permit higher-risk operation.
- **Unknown / insufficient evidence** — the system cannot yet certify the level.

These require different remedies.

### 9.4 Current progression substrate

The current architecture supports:

- AVAILABLE,
- NOT CONFIGURED,
- BLOCKED.

NOT CONFIGURED means readiness rules do not yet exist. It is neither proof of readiness nor an automatic hard lock.

### 9.5 Competency model

Keep separate:

1. **Competency definition** — plan-owned skill/mechanic.
2. **Competency state** — mutable current training state.
3. **Competency evidence** — observations that may justify state changes.

Current plan-owned competency definitions include:

- HTF liquidity recognition,
- draw on liquidity,
- displacement/FVG recognition,
- premium/discount context,
- time/session awareness.

Changing competency definitions requires a new Trade Plan revision.

The current practical loop is:

`Trade Plan competency catalog -> current state -> Study Run focus -> future evidence`

### 9.6 Do not invent proficiency math yet

The project does not yet have justified:

- proficiency percentages,
- automatic promotion/demotion,
- automatic competency-based Live lock,
- universal minimum sample counts,
- fixed readiness thresholds.

Those must be earned from actual evidence and explicit Trade Plan policy.

---

## 10. Competency evidence and Evidence Maturity

This is the **current architectural frontier**.

The next major product arc is to make deliberate practice produce trustworthy competency evidence that can move through the learning ladder.

### 10.1 Evidence should preserve provenance

Competency evidence should be able to identify, where relevant:

- competency definition,
- Trading Run / Study Run,
- environment and purpose,
- timestamp/market-time context,
- Trade Plan revision,
- process/Playbook revision or snapshot,
- QT/AMDX context,
- study question/focus,
- observed outcome,
- review judgment,
- supporting screenshot/Study Find/Trade Summary linkage.

### 10.2 Evidence should be human-legible

Evidence should remain inspectable rather than disappearing into a hidden score.

The operator should be able to understand why a competency state or future eligibility decision is supported.

### 10.3 Evidence Maturity

Evidence Maturity is an accepted future governance concept, not a current numeric scoring system.

It should eventually answer questions such as:

- Has this concept only been studied historically?
- Has it survived integration in Replay?
- Has it held up prospectively in Forward Test?
- Has Live evidence confirmed or weakened confidence?
- Is more targeted Study required?

Thresholds should be configured only after accumulated evidence makes them meaningful.

### 10.4 Review should route weaknesses toward a remedy

The mature loop should not merely display a low state.

It should support:

`observed weakness -> targeted Study -> competency evidence -> Replay integration -> Forward validation -> regained eligibility`

---

## 11. Market time, QT, and AMDX/XAMD

Market-time and QT are already established architectural substrate and should be matured through use rather than treated as a greenfield future system.

### 11.1 Canonical time

- America/New_York is canonical.
- Futures day rolls at 18:00 ET.
- Replay/Historical environments use explicit historical market time, not wall-clock time.

### 11.2 Factual context versus interpretation

Keep distinct:

- raw market-time/QT facts,
- AMDX/XAMD interpretation,
- directional/probability claims,
- opportunity ranking,
- authorization.

Do not infer an AMDX interpretation merely because a timestamp falls in a temporal quarter.

### 11.3 QT context

Current/future structured context may include:

- futures-day identity,
- session,
- killzone/window,
- relevant opens,
- temporal quarter,
- prior-cycle relationships,
- higher-order raw quarter stack,
- descriptive stack alignments.

Raw stack alignment is currently **descriptive context only** unless later evidence/Trade Plan rules justify stronger meaning.

### 11.4 QT hierarchy

The accepted conceptual hierarchy includes:

- 16-year cycle,
- Quadrennial,
- Yearly,
- Monthly,
- Weekly,
- Daily,
- session,
- 90-minute cycle.

The 22.5-minute cycle remains omitted unless later work justifies it.

Weekly QT uses Monday-Thursday as the four quarters; Friday is distortion/separate PO3 context rather than a fifth ordinary quarter.

Q1 should be interpreted relative to the prior cycle's Q4 where applicable.

---

## 12. Economic news and calendar context

Economic/news integration remains a meaningful later contextual/safety enhancement.

Future requirements include:

- ingest an economic calendar/news source,
- identify high-impact/red-folder events,
- preserve event timing/context with the run,
- support Trade Plan-specific warnings and lockouts,
- support model-specific conditions such as Friday Asian Range news filters,
- handle major events such as NFP, FOMC, and CPI,
- account for holidays, early closures, and other schedule distortions.

News should become structured context usable by TDA, QT/AMDX interpretation, authorization, and later analytics—not merely a decorative calendar panel.

---

## 13. Study, observations, summaries, and media

### 13.1 Study Find

Study Find is a structured notable-observation record with market context, move/context details, notes, and chart attachments.

It should eventually be linkable to:

- Trading/Study Run,
- competency focus/evidence,
- Trade Plan/process revision,
- Review/Development follow-up.

### 13.2 Trade Summary

Trade Summary captures structured trade/execution context and produces shareable output.

It should eventually link cleanly back to the governing Trading Run and revision provenance.

### 13.3 Summary templates

Summary templates are versioned Workbench configuration separate from the Trade Plan.

Published revisions are immutable, active revisions are explicit, and generated output includes template provenance.

Exposing **Trade Plan revision** as a template field remains a valid later enhancement.

### 13.4 Chart/media workflow

TradingView remains the preferred charting/study environment.

Current workflow:

`TradingView -> screenshot/copy/import -> structured Cockpit record -> generated review/share artifact`

Managed image attachments should remain reusable if later review surfaces need richer image comparison.

Responsive Film Night/gallery behavior is a downstream UX idea, not a current roadmap driver.

---

## 14. Workbench, Lab, and Review / Development

These concepts overlap operationally but are not identical.

### 14.1 Workbench

Workbench is the configuration/design surface.

Responsibilities may grow to include:

- Trade Plan/process configuration,
- Playbook editing,
- workflow definition editing,
- summary-template publishing,
- revision history,
- evidence/process configuration,
- later revision analytics.

Do not build a generic Workbench framework merely to satisfy an old roadmap item. Add capabilities when actual configuration needs justify them.

### 14.2 Lab / Study

Lab is the **Study operating environment** for deliberate historical investigation and targeted skill work.

It should emphasize:

- study question,
- hypothesis,
- scope,
- competency focus,
- sample/example observations,
- what was learned,
- evidence provenance.

It shares the core process/data substrate but need not look identical to Replay or Live.

### 14.3 Review / Development

Review / Development is the improvement side of the Trade Plan.

Over time it should consume accumulated evidence to support:

- targeted study recommendations,
- cross-run/cross-day synthesis,
- competency review,
- process/revision comparison,
- feedback/friction review,
- revision proposals,
- eventual Evidence Maturity interpretation.

Film Night is one possible later consumption workflow inside this area, not the architectural center.

---

## 15. Interaction and workspace requirements

### 15.1 TradingView/Cockpit parity

The Cockpit operates beside TradingView.

Workflow modes/decks/stations should correspond naturally to the chart workspace so the two systems advance together conceptually even when they are not electronically connected.

### 15.2 Responsive active workspace

The active operating surface should work as a compact desktop companion to TradingView.

Required controls must remain discoverable without excessive scrolling or hidden layout dependencies.

### 15.3 Shared application actions

Future input bindings should target logical actions such as:

- previous/next station,
- Focus/Deck,
- complete station,
- capture observation,
- capture Study Find,
- return to analysis,
- stand down,
- confirm/back,
- arm trade,
- flatten.

GUI, keyboard, mouse, macro pad, SpaceMouse, or custom hardware can later invoke the same actions.

Hardware design remains deferred until the action vocabulary stabilizes.

Dangerous actions require stronger safeguards than navigation/capture actions.

---

## 16. Feedback and process friction

The existing low-friction feedback capture system should continue to record where the Cockpit itself impedes the process.

Potential future analysis includes:

- friction by workflow step/revision,
- repeated backtracking,
- time per step,
- frequently revised fields,
- commonly overridden requirements,
- recurring UI failures.

Do not build a large friction dashboard before repeated usage produces enough meaningful evidence.

Incremental “new since last handoff” feedback export is a valid later improvement; cumulative digest export is sufficient for now.

---

## 17. Revision and provenance architecture

Historical records must preserve enough information to answer:

> What process/rules/context were actually in force when this decision or observation was made?

Relevant provenance may include:

- Trade Plan revision,
- process/TDA workflow revision,
- Playbook/model revision or snapshot,
- management/risk/safety rule revision,
- competency definition revision through the Trade Plan,
- summary-template revision,
- future checklist/template revisions.

The current implementation already records Trade Plan revision on Trading Runs, snapshots selected Playbook definitions, and versions summary templates.

### 17.1 Provenance is cross-cutting

Revision/provenance work is not a standalone abstraction project that should displace the learning frontier.

Each new evidence/learning slice should preserve enough provenance to remain historically interpretable.

### 17.2 Future revision analytics

Eventually support analysis such as:

- process adherence by revision,
- interpretation quality by revision,
- performance by revision,
- competency evidence by revision,
- behavior before/after a process change,
- compliant versus overridden/non-adhered outcomes.

Performance and adherence remain separate axes.

---

## 18. Data and technical architecture

### 18.1 Current stack

- Python 3.10+
- PySide6 / Qt
- local SQLite authoritative database
- pytest
- Git / GitHub
- Linux primary workstation
- TradingView for charting
- NinjaTrader as eventual execution target
- Trilium as future narrative companion
- NAS for backup/snapshots, not the live database

### 18.2 Database rules

- authoritative SQLite stays on local storage,
- WAL enabled,
- foreign keys enabled,
- explicit migrations via `PRAGMA user_version`,
- transactional multi-step writes,
- safe backup/snapshot practices,
- RAID is redundancy, not backup.

Do not operate the authoritative SQLite database directly from a NAS share or through VPN/shared-file synchronization.

### 18.3 Multi-device direction

Near term:

- code travels through Git,
- local application data remains authoritative per machine,
- NAS provides backups,
- interfaces use stable IDs, explicit timestamps/revisions, configurable paths, and repository boundaries.

If shared study data later becomes valuable, use deliberate export/sync or a central service.

Cross-device Live safety requires one authoritative central state/service. Independently synchronized SQLite files are not sufficient for shared lockouts/counters/safety state.

---

## 19. External integrations

### TradingView

Primary charting/study workstation.

Prefer conceptual workspace parity and screenshot/import workflows over embedded chart replacement.

A narrow Pine alert/webhook bridge remains a possible later integration if the process develops a clear need for specific machine-readable events.

### NinjaTrader

Primary intended execution platform.

Integration remains late because the Cockpit must first prove:

- authorization semantics,
- entry versus flatten behavior,
- risk/safety state,
- counters/lockouts,
- restart/recovery,
- simulated order state,
- broker/platform reconciliation.

### Trilium

Future narrative/journal companion.

Cockpit structured records remain authoritative. Trilium may later receive links, summaries, or richer narrative packages.

### Economic calendar/news

Future structured context and authorization input as described above.

---

## 20. Current capability status

### Implemented / established

- local SQLite persistence through schema v27,
- draft autosave/restore,
- Trade Plan shell and Process Blueprint,
- executable TDA with Focus/Deck concepts,
- explicit station completion semantics,
- Trading Day / Trading Run persistence,
- TDA -> Watch -> Review runtime and process transitions,
- Stand Down / No Trade outcomes,
- Post-Market Market Review / Process Review separation,
- shared Live/Replay/Backtest/Forward process substrate,
- declarative Playbooks and snapshots,
- multiple setup candidates / Models in Play substrate,
- setup criteria and separate authorization gates,
- market-time context,
- QT context and raw stack substrate,
- timed model relevance / opportunity-attention substrate,
- Study/Rehearsal/Validation/Execution semantics,
- Study intent provenance,
- AVAILABLE / NOT CONFIGURED / BLOCKED progression substrate,
- plan-owned competency definitions,
- mutable competency/profile state,
- Study/Replay/Forward competency-focus provenance,
- Study Find capture/review,
- Trade Summary capture,
- chart image import/paste,
- summary generation/copy,
- configurable/versioned summary templates and output provenance,
- feedback capture/digest,
- manual smoke-test runner,
- canonical handoff/decision/evolution/audit package.

### Partially implemented / needs maturation

- explicit competency-evidence records,
- evidence linkage across Study/Rehearsal/Validation/Live,
- Review/Development consumption of competency evidence,
- evidence-maturity interpretation,
- justified progression/eligibility rules,
- richer run <-> Study Find <-> Trade Summary linkage,
- process/revision analytics,
- Workbench configuration beyond summary templates,
- QT/AMDX integration/maturation from sustained use,
- operator-loop ergonomics from continued dogfooding.

### Intentionally deferred

- readiness percentages,
- automatic competency promotion/demotion,
- automatic competency-based Live lock,
- fixed evidence thresholds,
- large competency/KPI dashboards,
- broad Film Night/gallery polish,
- deep TradingView integration,
- dedicated hardware controller,
- generic Workbench framework,
- Trilium integration,
- multi-device sync,
- centralized Live safety service,
- NinjaTrader live order submission,
- embedded TradingView replacement.

---

## 21. Reconciled milestone roadmap

The roadmap is organized around the recovered **current architectural frontier**, not the old feature queue.

### Milestone A — Competency evidence loop

**Goal:** Make deliberate Study/Rehearsal/Validation work produce explicit, trustworthy evidence against plan-owned competencies.

Includes:

- competency-evidence domain model,
- provenance to competency/run/environment/purpose/plan revision,
- human-legible evidence notes/judgments,
- links to Study Finds/screenshots where useful,
- evidence creation from Study and Review without inventing scores,
- preservation of distinct evidence types by environment.

**Why first:** the competency substrate exists, but the evidence that should eventually justify state/progression changes does not yet have a first-class loop.

### Milestone B — Review / Development synthesis

**Goal:** Turn accumulated evidence into an actionable learning loop.

Includes:

- review competency evidence across runs,
- identify recurring weaknesses,
- route weaknesses toward targeted Study,
- support cross-run/cross-day process comparison,
- surface revision context,
- improve Study launch/focus from observed weaknesses.

**Exit direction:** Review should be able to say not merely “this was weak,” but “this is what should be studied next.”

### Milestone C — Evidence Maturity and progression governance

**Goal:** Establish evidence-grounded progression logic without arbitrary readiness math.

Includes:

- define evidence-maturity concepts using accumulated data,
- distinguish Study/Rehearsal/Validation evidence,
- distinguish eligibility regression / temporary pause / insufficient evidence,
- define transparent Trade Plan-owned progression requirements when justified,
- support explainable AVAILABLE / BLOCKED outcomes,
- preserve frictionless movement downward.

Automatic competency-based Live/Forward locks belong only here, after explicit rules and evidence exist.

### Milestone D — Continuous operator-loop hardening

**Goal:** Keep the daily operating loop comfortable and trustworthy while the evidence system matures.

This runs in parallel with A-C rather than displacing them.

Includes only friction proven through use:

- TDA/Watch/Review linkage,
- required-control visibility,
- low-friction capture,
- orientation/restart continuity,
- TradingView/Cockpit parity,
- run/summary/Study Find linkage,
- targeted UX refinement.

Do not turn this into a generic polish milestone.

### Milestone E — Context maturity: QT/AMDX, news, and distortions

**Goal:** Mature already-existing temporal/QT context and add external event context where it materially improves interpretation or safety.

Includes as justified:

- expected-versus-observed AMDX/XAMD refinement,
- QT context integration with Study/evidence,
- holiday/early-close/distortion context,
- economic calendar ingestion,
- red-folder context,
- Trade Plan news warnings/no-trade rules,
- preservation of event context for later analysis.

This is not a greenfield QT build; substantial QT/time substrate already exists.

### Milestone F — Execution-safety simulation

**Goal:** Prove the complete authorization/safety state machine before sending live orders.

Includes:

- arm/submit/manage/flatten lifecycle,
- stale authorization,
- trade/day limits,
- loss/cooldown/lockout rules,
- account context,
- restart/recovery,
- simulated execution reconciliation,
- guaranteed ungated exit/flatten behavior.

### Milestone G — NinjaTrader execution integration

**Goal:** Connect the proven Cockpit state machine to NinjaTrader without creating a second execution truth.

Includes:

- adapter/interface,
- order-intent transfer,
- acknowledgement/rejection handling,
- broker/platform reconciliation,
- disconnect/restart recovery,
- simulation/shadow mode before real-money enablement.

### Milestone H — Shared / multi-device operation

**Goal:** Add cross-device access only when it provides clear operational value.

Study data may use export/sync or a central service earlier.

Cross-device Live safety requires one authoritative central service/database state.

---

## 22. Near-term sequence after reconciliation

Subject to final operator confirmation:

1. Merge this reconciliation/handoff documentation checkpoint.
2. Start **Milestone A — Competency evidence loop** with a small design/inventory slice.
3. Define the minimal competency-evidence record and ownership/provenance boundaries.
4. Implement one narrow vertical loop, preferably:
   `Study/Review -> explicit competency evidence -> persisted retrieval`.
5. Manually exercise that loop before adding aggregation or scores.
6. Let the evidence produced by actual use inform Milestone B.
7. Continue whole-loop dogfooding and only interrupt the learning frontier for blocking operator friction.

Revision/provenance work should be done as required by these slices, not promoted into an abstract detour.

---

## 23. Later pile / accepted but not current

Valid ideas that should not silently become the next task:

- Trade Plan revision as an available summary-template field,
- broader summary-template library/catalog UX,
- chart-image summary cards,
- Film Night / responsive visual comparison,
- richer TradingView webhook/event integration,
- Trilium package/link generation,
- generalized macro/binding system,
- dedicated cockpit hardware,
- friction heat maps,
- large competency/KPI dashboard,
- embedded charting,
- multi-device study sync,
- centralized PostgreSQL/service architecture,
- direct NinjaTrader order execution.

---

## 24. Open design questions

Keep explicit until implementation/evidence resolves them:

- exact minimal competency-evidence taxonomy,
- whether competency state remains manually assessed initially or gets a separate reviewed-transition workflow,
- what Review action creates/accepts evidence,
- how Study Finds link to competencies/runs/revisions,
- how Trade Summaries link to Trading Runs and exact process provenance,
- exact ownership/revision boundaries among Trade Plan, Process Blueprint, TDA workflow, management rules, risk rules, and safety rules,
- final TDA station/content structure,
- Workbench publishing UX for non-template definitions,
- evidence-maturity calibration and future progression requirements,
- exact criteria for future Live/Forward eligibility,
- economic-calendar provider/normalization model,
- holiday/early-close distortion representation,
- NinjaTrader bridge/reconciliation protocol,
- initial multi-device study-data strategy,
- Trilium linking/package format.

---

## 25. Development and acceptance discipline

For each substantial slice:

1. start from an up-to-date `main`,
2. use an isolated branch,
3. state which milestone/current frontier the slice serves,
4. prefer a small vertical slice,
5. run the full automated suite,
6. run relevant manual acceptance checks,
7. inspect the diff,
8. update `PROJECT_STATE.md`,
9. update `DECISIONS.md` when a durable decision changes,
10. update `DECISION_AUDIT.md` when an older decision is refined/superseded,
11. update `PROJECT_EVOLUTION.md` when the architectural phase changes,
12. merge only a known-good checkpoint.

Markdown remains the durable manual acceptance record; the smoke-test runner is a convenience layer.

---

## 26. Priority test for future work

Before adding a feature, ask:

> Does this materially strengthen the current learning/progression loop, improve process adherence, reduce proven operator friction, preserve trustworthy evidence/provenance, or strengthen safety?

If not, it is probably not the next priority.

When a later milestone becomes the new center of gravity, update the current frontier explicitly rather than allowing old roadmap order to take over.


## Evidence Maturity accepted refinement

Evidence Maturity is the boundary-aware governance layer that asks:

> Can this evidence set support a trustworthy decision at this progression boundary?

It is separate from Competency State, Progression Policy, and Eligibility.

The accepted v0 profile is non-numeric and uses six inspectable dimensions:

- Volume / Sample Depth,
- Environment Relevance,
- Recency,
- Consistency,
- Context Coverage,
- Revision Relevance.

The v0 profile is identified by:

`Trade Plan + competency + progression boundary`

Candidate boundaries are:

- Study -> Rehearsal,
- Rehearsal -> Validation,
- Validation -> Execution.

The accepted human maturity states are:

- Not Assessed,
- Insufficient Evidence,
- Developing Evidence,
- Decision-Usable Evidence.

These states describe whether evidence is usable for a decision; they do not decide progression.

The overall maturity-state label is intentionally removable if real operator use shows it is too evaluative. The underlying dimensional profile, notes, and descriptive evidence facts must remain useful without it.

Do not introduce a weighted readiness score, automatic promotion/demotion, or eligibility change in the Evidence Maturity layer.


## Progression policy and cross-revision competency continuity

Progression Policy is Trade Plan-owned, immutable within a published revision, and defined per upward progression boundary.

v0 boundaries:

- Study -> Rehearsal,
- Rehearsal -> Validation,
- Validation -> Execution.

Each policy contains explicit gating requirements only. v0 uses simple ALL/AND composition. Required competencies must be named explicitly; a competency does not become a blocker merely because it exists in the catalog.

Accepted v0 requirement kinds:

- Evidence Maturity State,
- Competency State,
- Evidence Purpose Present,
- Human Certification.

C2 builds the policy substrate without inventing real readiness criteria. The first configured progression rules require separate operator acceptance and a new published Trade Plan revision.

Whole-plan revision change must not automatically reset unchanged competencies. If a competency definition is materially unchanged between rX and rY, prior evidence and Competency State may remain valid. rY may still require fresh Rehearsal/Validation evidence to establish contextual integration under the revised plan.

If a competency definition materially changes, historical evidence remains valid for the old definition but must not silently certify the new one. New competencies do not inherit historical evidence/proficiency automatically.

Long-term analytics should preserve enough provenance to study learning velocity, time-to-proficiency, progression friction, revalidation, competency-family/genre transfer, and diminishing returns. These are analytics goals, not current readiness thresholds.
