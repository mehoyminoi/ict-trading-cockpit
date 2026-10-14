# ICT Trading Cockpit — Product Requirements & Milestone Roadmap

**Status:** Accepted reconciled product requirements and milestone roadmap  
**Reconciled:** 2026-10-08  
**Role:** Canonical current product requirements and milestone roadmap.

**Implementation-status clarification (2026-10-13):** Milestones A–C and the shared AMDX foundation/native consumers are implemented and merged on main, schema v46 / Alpha 0.7. Earlier descriptions of the “current frontier” and the reconciliation queue below are historical rationale, not an instruction to rebuild completed work. The active product frontier is review of the proposed [whole-cockpit UX/Study implementation plan](COCKPIT_UX_IMPLEMENTATION_PLAN.md). Its shell/startup/ranking choices are proposals; accepted 16:9, quiet Watch, shared calendar and nearby overview/detail requirements remain authoritative.

Companion documents:

- `docs/PROJECT_STATE.md` — exact current implementation checkpoint,
- `docs/DECISION_AUDIT.md` — supersession/conflict ledger,
- `docs/DECISIONS.md` — durable accepted architectural decisions,
- `docs/PROJECT_EVOLUTION.md` — chronological architecture history,
- `docs/HANDOFF.md` — continuity protocol,
- `docs/SMOKE_TEST.md` — manual acceptance record.
- `docs/COCKPIT_FUNCTIONAL_WALKTHROUGH.md` — source-verified whole-tool journeys, current/proposed surfaces and shared QT/AMDX contract review.
- `docs/AMDX_CYCLE_RULE_CONTRACT.md` — coupled quartet profiles, rule/anchor provenance, interpretive uncertainty and classification-rule requirements.
- `docs/AMDX_RULE_DEFINITION_FRAMEWORK.md` — versioned classifier definitions, priority/weighting, target scopes, news context and the narrow implementation boundary.
- `docs/AMDX_WORKING_QUARTET_ACTION_REVIEW.md` — reviewed one-entry working-quartet revision, compatible/retired anchors, X subtype and uncertainty cases; follow-up implementation authorized.
- `docs/AMDX_QUARTET_REVISION_OPERATOR_GUIDE.md` — the implemented follow-up action and four focused operator checks; original six entry results remain separate.

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

Operator clarification on 2026-10-11: the Focus/Deck relationship is a useful model for nearby detail and bird's-eye orientation, but the mature presentation should integrate the two closely rather than separate them behind tabs. This is a presentation direction; existing Focus/Deck tabs remain until a reviewed replacement preserves their shared process state and natural navigation.

Operator clarification on 2026-10-13: Deck is not merely an organizational overview. It implements workspace/layout parity with the external TradingView TDA deck. For a four-pane chart layout, the corresponding cockpit stations should occupy the same top-left, top-right, bottom-left and bottom-right positions, carry explicit chart roles, and support the same reading/traversal order across both monitors. Selecting a cockpit pane opens that mapped station in Focus; returning preserves the map and selection. Only the active pane needs full detail, while inactive panes can show quiet state and retained conclusions. Mapping is revisioned deck/station configuration and must not change through ordinary navigation or reflow. See `WORKSPACE_PARITY.md` and `UX_DESIGN_TOUCHSTONES.md`.

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

### 11.5 Coupled cycle profiles and plan-defined classification

Operator clarification on 2026-10-11: each applicable four-quarter cycle is interpreted in AMDX or XAMD order. AMDX means Q1=A, Q2=M, Q3=D, Q4=X; XAMD means Q1=X, Q2=A, Q3=M, Q4=D. X may be Continuation X(C) or Reversal X(R). One accepted quarter assignment constrains the full containing profile: Q3=D implies AMDX, while X subtype can remain unresolved. This supersedes treating the four sibling quarter roles as independent fields. See `AMDX_CYCLE_RULE_CONTRACT.md`.

Separate explicit technician anchors, rule-implied quarter/profile context and evidence-based phase classification. An inferred sibling role is not a fabricated manual answer or observed fact. Within-quartet inference does not automatically propagate a parent's phase/profile to child quartets. Preserve uncertainty, competing interpretations, conflicting active anchors, corrections and explicit manual judgment with provenance. Do not force a pattern or X subtype to satisfy a form.

AMDX/XAMD definition and classification rules should be prominent, versioned Trade Plan content with inspectable inputs, reasons, applicability and unknowns. The aim is to make classification follow the plan's declared criteria and evaluate those criteria empirically, rather than leave subjective disagreement hidden in labels. The structural order is specified here; complete objective price-action criteria are not yet specified and must not be invented. A live phase sensor is optional later work, not the foundation of this architecture.

Study/Lab can later evaluate rule revisions against scoped examples and recorded information available at the time. This is empirical rule/profile investigation, not a live quarter-correctness checklist, automatic competency score or new authorization policy. Authoritative adoption of new classification rules requires a published Trade Plan revision; current Alpha 0.7 remains unchanged. The previously proposed first-expectation Review default is not accepted by this clarification and needs to be reconsidered with cycle-profile provenance.

### 11.6 Changeable rule definitions, priority and interpretive event context

Operator direction on 2026-10-11: criteria should be changeable, trackable and actionable Trade Plan definitions so different approaches can be compared. Edit candidate definitions and publish identifiable revisions while protecting prior published rules and run history. Different criteria/priority/explicit weighting methods can produce different role/profile conclusions from the same facts; retain evaluation reasons, competing results and rule/input provenance. Input quarter/session and classified target must be distinct and explicit. Local X-like behavior need not be the final assigned quartet role; unsupported assignments remain conflicts/exceptions rather than forced patterns. Detailed classifier content and weight scales are not invented by the generic framework. See `AMDX_RULE_DEFINITION_FRAMEWORK.md`.

High-impact/red-folder news relationships are a key TDA/Study input for anticipating weeks and sessions alongside price-action evidence. Preserve event timing/classification/coverage, historical information availability, source/rule revisions and unknowns. Empirical correlation remains something to evaluate; it is not assumed predictive strength or an automatic entry-policy effect. Framework construction can proceed with structural/definition/action contracts while actual classifier methods are specified and evaluated.

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

The Cockpit is the primary working surface in the operator's desktop layout. Plan the mature interface around a **16:9 workspace** occupying the majority of the operator's ultrawide display, or the full display on a conventional screen. Charts, journals and other daily information are arranged around the Cockpit. This operator override on 2026-10-11 supersedes the earlier undefined smaller-footprint / compact-companion requirement.

16:9 is a design target, not an implemented fixed-aspect window restriction or an exact pixel resolution. Layout remains responsive to available space. More room should support nearby orientation and task detail while preserving low interaction and memory burden; it is not a reason to expose every control simultaneously.

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

## 22. Original reconciliation sequence — completed historical queue

This queue records the 2026-10-08 sequence; its A–C work is now complete. Use `PROJECT_STATE.md` and `COCKPIT_UX_IMPLEMENTATION_PLAN.md` for current work.

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


## Study sources, knowledge repository, and Ah-ha capture

Future Study-mode design should reduce duplicate documentation between Cockpit and the technician's long-form knowledge repository.

Proposed ownership boundary:

- Cockpit owns structured study/process state, Trade Plan candidates, competency links, evidence provenance, Development Direction, progression context, and actionable learning workflow.
- The external knowledge repository may remain the canonical home for rich long-form notes, transcripts, screenshots, annotations, and narrative study material.
- Video sources and repository notes should be linkable as source artifacts rather than requiring content duplication.

Future Cockpit concepts should include a lightweight **Study Capture / Learning Inbox** for low-friction capture while watching videos or reviewing notes.

A captured learning item may record source reference, video timestamp or repository-note reference, short observation, tags, and relationships such as:
- existing competency,
- candidate/new competency,
- Playbook or Trade Plan revision candidate,
- Study question,
- Cross-Run Observation support,
- terminology/reference note,
- general research item.

Important guardrail: instructional notes, video insights, "Ah-ha" moments, gems, or mentor/ICT statements are **learning inputs**, not competency evidence by themselves. They may create a study target or revision proposal; proficiency evidence still comes from deliberate reviewed performance/observation.

The preferred workflow is **capture once, classify/promote later** rather than entering the same insight independently in both Cockpit and the knowledge repository.

Future integration levels may progress from:
1. stable source links/deep links,
2. one-click export/import or synchronized metadata,
3. local API integration when feasible,
4. optional source-aware search/retrieval from the repository.

Cockpit should aim to become the technician's operating interface without requiring replacement of a mature external knowledge base.


## Guided visual process state and friction lubrication

Later UI maturity should make dense process/governance logic feel familiar, navigable, and low-friction even when the operator is cognitively tired.

A useful reference model is the clarity of revision/state workflows in engineering PDM systems combined with the familiarity, discoverability, and engagement-oriented interaction patterns of consumer software — without importing manipulative attention mechanics.

Priority UI goals:

- maintain a highly visual, interactive map of the current process position,
- clearly show what state the operator is in,
- clearly show available next transitions,
- clearly explain why a gated transition is unavailable,
- clearly show what specific action/evidence/review would make that transition available,
- expose definitions and terms contextually without forcing navigation away from the task,
- use progressive disclosure so technical depth is available without overwhelming the active surface,
- use tooltips, inline definitions, hover/click detail, state chips, path highlighting, and other quiet context aids where appropriate,
- preserve operator orientation across check-in, checkout, state change, revision control, progression, revalidation, and recovery workflows,
- minimize working-memory burden and avoid requiring the operator to remember hidden rules or terminology.

The target experience is not merely "usable." The Cockpit should become a familiar operating environment where the operator can reserve cognitive capacity for market understanding, learning, and skill formation rather than interface reconstruction.

For restrictive/gating surfaces especially, the UI should explain rather than merely deny:

```text
Where am I?
What does this state mean?
Why can't I progress?
What requirement is blocking me?
What can I do next?
What evidence/action would clear the block?
```

This requirement belongs primarily to later operator-loop/UI hardening, but current domain models should preserve the explainability and transition provenance needed to support it.


## Smoke-test and dense-surface operator guidance

Manual acceptance testing is part of product development and should not become a cognitive scavenger hunt.

As Review / Development and other governance surfaces become denser, the Cockpit should support low-friction verification and orientation without changing the underlying domain model.

Future UI/test-support options should include:

- a **guided smoke-test mode** that presents one verification step at a time,
- direct navigation/deep-linking from a smoke-test item to the relevant Cockpit section or control,
- temporary highlight/focus of the control, phrase, or state being verified,
- stable UI/control identifiers so tests can point to exact targets even as layout evolves,
- collapsible sections and progressive disclosure in dense governance surfaces,
- clear section headings, state chips, breadcrumbs, and visual grouping,
- search/filter within Review / Development,
- a compact "current state / why / next action" summary before detailed controls,
- optional test-only overlays or annotations that identify where a requirement is visible,
- smoke-test wording that refers to stable concepts and labels rather than forcing the operator to scan for incidental prose,
- preserving existing architecture and semantics while improving discoverability.

The objective is to reduce working-memory load and the temptation to skip or half-effort acceptance testing. Testing friction is itself product feedback: if an experienced operator cannot quickly locate a state or explanation during verification, the production surface likely also needs clearer information architecture.

This should be addressed opportunistically during later UI/operator-loop hardening, with small low-risk improvements allowed earlier when they materially improve testing without derailing architectural milestones.


---

## Intraday QT depth without form burden

The mature QT / AMDX experience must preserve the full intraday structure without turning active use into a large repetitive form.

The system should eventually capture, display, and preserve enough structure to represent at least:

- the four daily futures sessions (Asia, London, NYAM, NYPM),
- the four 90-minute cycles within each session,
- the relevant nested QT / AMDX interpretation at those intraday layers,
- the time-derived/raw quarter context that supports those interpretations,
- expected versus observed intraday interpretation where Review needs it,
- provenance sufficient for later Study, Review, and analytics.

This does **not** mean the operator should manually complete every layer on every run.

The UI should actively reduce entry burden through techniques such as:

- deriving factual time/session/quarter state automatically,
- showing only the current/relevant intraday layer during active operation,
- progressive disclosure for deeper hierarchy,
- inheritance/carry-forward where semantically honest,
- compact visual timelines or nested-state maps,
- defaults that preserve Unknown rather than forcing an answer,
- editing by exception instead of repeated confirmation,
- Review views that can expand the full hierarchy after the fact,
- pruning redundant inputs when the same fact is already known elsewhere.

The product requirement is therefore:

> **Preserve the full intraday QT hierarchy in the data model and historical record while minimizing how much of that hierarchy the operator must explicitly touch during live use.**

Do not solve completeness by exposing every session × 90-minute cycle × QT layer as a permanent grid of fields. The operator-facing design should preserve depth while reducing simultaneous exposure and repetitive entry.

### Whole-stack orientation and nearby detail — operator clarification 2026-10-11

The full AMDX stack, including higher-order context, should remain visible in a quiet, easily accessible form throughout TDA / Watch / Market Review and into Study, whether in Lab or another study surface. QT/AMDX is foundational context across the learning and operating process. A bird's-eye view and accessible minutiae belong closely together: inspecting or editing a selected level should preserve the overview and its relationship to the surrounding levels. Progressive disclosure applies to detail; it should not hide the higher-order stack or imply that it is less important than sessions/cycles. Minimize clicking, hunting and digging while keeping the environment clutter-free. Exact layout remains open to hands-on evaluation; shared presentation does not imply that different runs share or overwrite interpretations.

Make all editable levels reachable with minimal motion and navigation burden, within the existing process permissions. Anticipated heavy use of keyboard shortcuts and a macro pad is a design constraint: selection, inspection and editing should use shared application actions that mouse, keyboard and later hardware can invoke. Actual macro-pad integration remains downstream.

Operator clarification on 2026-10-12: especially in Watch, show the current working AMDX stack and the technician’s current position within it, with quiet whole-stack orientation and efficient entry. Do not display prior stack versions, before/after changes or expectation-comparison panels as part of the normal Watch surface. Revision history is retained automatically for later purposeful Review/Study exploration, without a daily history-checking obligation.

Preserve interval/revision history for reconstruction and contextual Review/Study use. A raw day-history list or "was I right this quarter" presentation does not belong on the active QT workspace. Comparison is a lower-priority, optional Study/Review exploration tool, to be developed when a concrete need arises; it has no entry point in Watch. Routine observed entry must not automatically choose a first/latest expectation. If a comparison basis is deliberately selected for a cycle, corrections retain it until changed/cleared. Observed corrections should use the same efficient one-entry quartet behavior as working entry through an independently versioned action, preserving earlier observed judgments. These accepted behaviors are documented in `AMDX_REVIEW_INTERACTION_CONTRACT_REVIEW.md`; v40 pairing storage and v41 versioned observed revision exist, while contextual UI remains downstream. Later Review/Study aggregation may investigate whether interpretation changes tend to follow identified price-action events or things the technician noticed. Preserve revision, event/observation and rule/plan provenance for such research where explicitly captured; the aggregation, feature definitions and statistics remain future work. No event detection or numerical likelihood is inferred. The placement and form of deeper historical exploration remain open; no correctness scoring or mandatory quarter-by-quarter grading is introduced. Current suggestions about exact controls, baseline selection and inheritance remain provisional rather than inferred design acceptance.

### Maintained master AMDX calendar — operator clarification 2026-10-13

One continuously maintained AMDX stackup calendar must supply foundational context across Lab, TDA, Watch and Review. Lab backtesting backfills the same underlying timeline across every layer as far back as needed; TDA uses it for thesis context; Watch exposes a quiet pertinent slice with efficient permitted updates. Purpose/context changes the rendering and operation, not the primary owner or a separate catalog to synchronize. The normal workflow should not require choosing Backtest/ForwardTest catalogs or a run-to-catalog destination. Initially this is MNQ; preserve explicit instrument identity so later NNQ/other calendars cannot mix.

The master calendar retains revisions, semantic working/observed distinctions, rule/definition/evidence basis, actual recording time and studied time. Backfilled expectations must not silently become contemporaneous predictions. A run captures the specific calendar context/revisions it used; later edits to the maintained calendar do not rewrite those historical captures. Optional experimental alternatives remain explicit, with no automatic adoption or default comparison baseline. Preserve quiet current-state Watch behavior and spacious Lab overview with nearby detail.

Historical/forward/live/study origin is provenance or an analytical filter, not a separate default calendar. Existing collections/run records must be preserved through an explicit transition rather than blind latest-value merging or guessed legacy assets. This clarification supersedes the earlier interpretation of “catalog” as separate purpose-owned collections and the proposed collection-destination collector as the primary workflow. See `AMDX_MASTER_CALENDAR_CLARIFICATION.md` for the implemented/reusable boundary and revised next architecture work.

### First native AMDX trial — operator feedback 2026-10-11

The operator prefers revising the working quartet with one new valid entry rather than finding and clearing an older anchor that contradicts the intended new order. This is a shared-action direction, beyond control styling: ordinary quartet revision should preserve earlier claims as history without requiring manual conflict cleanup. Precise treatment of other compatible anchors, X subtype, uncertainty and explicit alternatives still needs an action-contract refinement before implementation. Existing domain conflict/evaluation traces remain valid; no stored claim is silently rewritten or discarded.

Normal phase-entry controls should offer only roles structurally possible at the selected quarter position across AMDX and XAMD:

| Quarter | Available roles |
| --- | --- |
| Q1 | A, X |
| Q2 | A, M |
| Q3 | M, D |
| Q4 | D, X |

Availability must not be restricted to the currently selected order, which would prevent a one-entry order change. X(C), X(R) and X(?) belong only at positions where X is possible. Operator clarification on 2026-10-12: in the mature UI, X(C) and X(R) must each be directly available in one click from the active entry target, without first opening an X-subtype menu. The same shared commands must be accessible to keyboard/macro-pad bindings. This is an accepted interaction requirement; the current menu is an interim renderer. A direct subtype choice records one normal working revision without a separate Save or confirmation step. Target selection and structurally invalid positions retain their existing boundaries. Unknown, Not Applicable and clear remain distinct from phase roles, with effects defined by the implemented and operator-accepted `revise-working-v1` policy. Invalid normal phase placements are prevented by the UI and shared action, while existing history and explicit analytical conflicts/exceptions remain inspectable.

The operator likes quiet contextual hover explanations and having the session/day quartet and active session's 90-minute quartet visible together. Retain those relationships in later, more visual presentations within the primary workspace; the current table is not an accepted final renderer.

### Context-specific presentation — operator direction 2026-10-11

Foundational QT/AMDX context can have different rendering/interaction profiles across the Cockpit. Watch should emphasize quiet at-a-glance self-orientation and efficient permitted capture; Study/Lab should allow a more spacious investigative experience tailored to insight gathering. TDA and Market Review can emphasize their own analytical and comparison tasks. These are projections of the shared domain state and application actions, not additional process modes or independent interpretation stores. Whole-stack accessibility, historical truth and low interaction/memory burden carry across profiles; identical widget layout is not required.

Park component layout iteration while reviewing the broader Cockpit functional map, context placement and action/ownership boundaries. Architectural contract work can progress independently of final rendering choices. Before production UI development, review a coherent overall-tool view covering Trade Plan/governance, Process, Study/Lab, Review/Development and Workbench, including existing behavior versus proposed behavior. Exact draft commit timing, permitted Watch interpretation edits versus observation capture, and comparison baseline remain explicit contract decisions rather than consequences of a mockup's controls.

### Proposed Study-first startup — operator direction 2026-10-11

Study should be the default/most anticipated workspace in the mature UX, especially while building a validated successful Trade Plan. The operator expects time spent studying to substantially outweigh live-trade activity during that period; no numeric ratio or enforced quota is specified.

A proposed startup surface should offer Study this Competency / a relevant next study task in the spirit of a dismissible recent-project suggestion. Its purpose is to answer: "After a tiring workday, what is the best use of my limited time and mental energy?" It should minimize planning/navigation burden while remaining easy to dismiss or navigate around. This direction is explicitly subject to change and is not a mandatory study gate or an implemented new startup behavior.

Recommendations should explain their recorded basis, such as saved Development Direction, selected competency focus or an unfinished study; no unsupported mastery score or invented personalized priority is introduced. Details of recommendation ordering, manual preference and handling an already-active run remain open. Startup guidance should not silently create a run, change an environment, overwrite in-progress context, or change Trade Plan/progression rules.

### Parked coverflow-style AMDX navigation idea — 2026-10-11

Subject to evaluation against other methods, explore a coverflow-style focus/detail feature controlled by scrolling/wheel and hotkeys. It should expose an appropriate amount of information while retaining nearby quiet whole-stack orientation. Navigation alone must not accept an interpretation, create history or retarget a pending edit. Reuse shared actions and keep layout/animation/binding choices downstream; this is an exploratory UX idea, not an approved renderer or implementation dependency.

### Accepted automatic interpretation recording — 2026-10-11

A deliberate accepted AMDX phase choice should immediately become recorded interpretation history, without waiting for station completion or requiring a separate Save/Record action. Later changes preserve the earlier interpretation as revisions. Note text remains automatically recoverable during editing. Scope navigation and analytical completion remain separate actions. Option browsing/untouched Unknown defaults do not invent an interpretation. See `QT_ACTION_CONTRACT_REVIEW.md`; the default comparison baseline remains open.

### Accepted in-place Watch AMDX updates — 2026-10-11

Small working-interpretation changes and active 90-minute cycle input should be directly and easily reachable in Watch. An accepted phase change uses the shared automatic revision-preserving command and does not require leaving Watch. The operator expects to keep up with at least the 90-minute cycles as they pass; factual current-marker updates are automatic. Explicit anchors remain technician input; a constrained containing quartet may show marked rule-implied roles, while a new containing cycle receives no arbitrary copy-forward. An active edit remains pinned to its target across a passive clock boundary. No mandatory cycle-completion gate is introduced.

Broader thesis changes should have easy full-stack inspection and full TDA/Return to Analysis access. Inspection alone does not alter the process; the technician decides when broader re-analysis is needed. Do not automatically force re-analysis based solely on phase/level or edit count. These are shared action/permission requirements, not a chosen widget layout or an implemented production edit path.


### Shared calendar implementation specification — 2026-10-13

`AMDX_MASTER_CALENDAR_CONTRACT.md` develops the accepted master-calendar ownership requirement into canonical instrument binding, shared working/observed actions and immutable run capture/retry/transition rules. Normal areas use the same maintained owner; a run retains exact captured revisions and explicit absent heads rather than today's head. No purpose/destination chooser or extra Save is required for normal entry. Technical transaction/capture boundaries are developer implementation choices following authorization to proceed, not separately confirmed product wishes. This remains unimplemented; current source/schema and smoke results are unchanged.


## 2026-10-13 — Canonical master foundation implemented

PR #71/source `8269b64` implements canonical first instrument/ledger binding, purpose-independent owner metadata, clean initialization or deliberate existing-ledger adoption, consistent shared reads/pinned targets and self-contained binding/ledger archives. Schema v43 preserves all actual v42 source rows and invents no assets/bindings. Existing v1 collection archive semantics remain intact; no working/observed or conflicting-source merge occurs. Focused 263 PASS (34 new cases), complete 970 PASS across 79 isolated module processes in 259.56s, clean exits/no pytest warnings. GUI/tools and all 264 smoke records are unchanged. Native shared ownership and persisted run captures remain unimplemented; owned run capture integration is next. #67–71 remain unmerged, main `6dd43c8` (v41), Alpha 0.7. See `AMDX_MASTER_CALENDAR_GUIDE.md` for API/transaction/transition boundaries.


## 2026-10-13 — Run capture/atomic storage boundary implemented

PR #72/source `c822d04` implements schema-v44 immutable run/master binding, captured full stack/absence and original operation receipts, owned new launch and working calendar-edit/capture transactions, context-use primitives and standalone original-basis reconstruction. Extracted run/catalog helpers retain old public mappings/action semantics. Legacy rows/unknown assets are preserved; migration assigns nothing. Focused 310 PASS (58 new), complete 1028 PASS across 81 isolated modules in 266.04s, clean exits/no pytest warnings. All verification processes exited. GUI/tools and all 264 smoke records remain unchanged. Native Lab/TDA/Watch and existing decision/Observed Review consumers remain to be rebound; `AMDX_RUN_CALENDAR_CAPTURE_GUIDE.md` records that next boundary. #67–72 remain unmerged, main `6dd43c8` (v41), Alpha 0.7. No new operator trial or merge.


### Higher Review scope alongside broad historical Lab — current clarification

Review may inspect distinct higher contexts on either calendar side of its original reviewed futures day, defaulting to the original run reference. Selection updates factual higher orientation without retargeting the intraday editor or recording a judgment. Deliberate phase input retains the original launch and selected scope together in its immutable assessment basis. The bounded run window does not restrict all-layer historical Lab backfill. Current maintained Observed and original captured Expected remain distinct; no Watch comparison/history control or automatic Expected baseline is implied. `AMDX_HIGHER_REVIEW_GUIDE.md` records the current implementation boundary; final full-cockpit rendering and the Study/criteria/import milestones remain subsequent work.


## 2026-10-13 — UX review feedback and recovered context

The operator's review of the whole-cockpit walkthrough identifies density, homogeneous major sections, dispersed related AMDX information and an over-combined Focus/Deck presentation. Guided work and readily accessible bird's-eye orientation remain distinct responsibilities; close integration does not require all expanded detail and overview panels to stay visible simultaneously. The existing synthetic layout is not accepted as the mature renderer.

Retain the calendar-like QT hub direction, now specified more concretely: in Lab, an actual month calendar with appropriate week/day/session-cycle indications, period selection exposing editable lower context, and access to the supported 16-year-to-smallest-cycle stack. A calendar shortcut/access path from other cockpit contexts is desired. Shared calendar ownership, explicit studied/operational references and immutable run captures still govern those views.

For future quarter/session colorization, record Q1/Asia yellow, Q2/London red, Q3/NYAM green and Q4/NYPM blue. This is a temporal identity convention, not an AMDX-phase or completion-state palette; exact colors and accessibility/theme treatments are not implemented here.

Familiar CAD/SolidWorks, Office and tuning-software navigation, ribbons/toolbars/tabs/icons, and one-action support tools are exploratory preferences to try. Study Find, extra context and subroutines should be easy to invoke and leave, while required current-step decisions remain discoverable. Major sections should be identifiable at a glance. The operator explicitly keeps these layout suggestions provisional.

Before further UI changes, compare the recovered prequel/continuation with the current plan. `UX_CONTEXT_RECONCILIATION.md` records the overlap, surviving contracts, proposal gaps and three journeys to refine. This feedback neither accepts a replacement layout nor reopens completed storage work.


## 2026-10-13 — UX friction research and future news/calendar cues

The operator requests a distinct review of established professional UX methods before further UI development. `UX_FRICTION_RESEARCH.md` records primary sources, their limits, and proposed UX-F01–F12 quality criteria: task-oriented attention, coherent context, direct frequent entry, discoverable support tools, stable navigation, keyboard access, recoverability and complete-task evaluation. These form a candidate requirements annex for discussion, not accepted final controls or measured usability improvement. Ribbons/toolbars remain trial options. Existing behavioral contracts and the recovered-context review hold remain authoritative.

Use task analysis, structured inspection, cognitive walkthroughs and small goal-based operator trials to refine the guided TDA/Deck return, quiet Watch/support return and Lab calendar investigation journeys. Usability records should supplement rather than rewrite functional smoke instructions. Evaluate correct scope/outcome, hunting/backtracking, context recovery, time and operator effort; no arbitrary global click quota, readiness score or automatic telemetry is introduced.

Retain the requested future news presentation: scheduled releases should appear on the maintained calendar, with useful news/quarter/AMDX-stack context cues. Exact markers, filters and composition remain open. Reuse event/provider provenance and historical as-of/coverage semantics; unavailable coverage is not no-news. Temporal alignment, plan-defined expectation and measured association must remain distinguishable. Quarter colours retain temporal identity, with separate labelled news cues. This wish does not authorise feed acquisition, a new classifier, automatic trading restrictions or another calendar owner.
