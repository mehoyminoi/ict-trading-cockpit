# ICT Trading Cockpit — Product Requirements & Milestone Roadmap

**Status:** Reconciled working draft — 2026-10-08  
**Role:** Canonical product requirements and milestone roadmap once this reconciliation branch is accepted and merged.  
**Companion documents:** `docs/PROJECT_STATE.md` for the current implementation checkpoint, `docs/DECISIONS.md` for durable design rationale, and `docs/SMOKE_TEST.md` for manual acceptance.

This document supersedes the early living requirements/roadmap as the forward-looking product plan. The older document remains useful historical context, but its priority ordering no longer reflects the current Cockpit.

---

## 1. Product mission

Build a local-first **trading process operating system** that makes discretionary trading more structured, repeatable, analyzable, teachable, and deliberately boring.

The Cockpit is not primarily a P&L dashboard and is not intended to replace TradingView as the charting environment. Its first measure of success is **process adherence and decision quality**.

A fully compliant **No Trade — Process Followed** outcome is a successful operating result.

The long-term product should help the operator:

1. form and record a top-down market thesis,
2. translate that thesis into concrete things to watch,
3. observe the market with minimal interaction cost,
4. determine whether one or more opportunities satisfy a versioned Trade Plan,
5. execute only when authorization is explicit,
6. review what happened without rewriting history,
7. turn repeated evidence into process and competency improvement,
8. compare performance and adherence across process revisions.

---

## 2. Core product principles

### 2.1 Process over P&L

Profitability matters, but it does not define whether the process was followed. Performance and process adherence must remain separate analytical dimensions.

### 2.2 Structured records are authoritative

Trade summaries, Study Find text, screenshots, dashboards, share cards, Trilium notes, and future reports are derived views of structured records. They must not become the only copy of important context.

### 2.3 Guided when operating; flexible when designing

The daily operating surface should reveal only what is useful now. Process design, template editing, revision management, research configuration, and deeper analytics belong in **Workbench / Lab**.

### 2.4 Preserve honest incompleteness

Unknown/not assessed is not the same as Neutral, False, or Failed. Intentional overrides and incomplete records are useful evidence and should remain explicit.

### 2.5 Revision control is part of the product model

A process revision is not merely a software version. Trade Plans, process definitions, playbooks, templates, management rules, risk/safety rules, and other behavior-defining artifacts should carry revision identity where historical comparison requires it.

Once a published revision has been used as authoritative context for a record, it should not be silently mutated.

### 2.6 Low-friction operation

The application should reduce operator interaction cost during market hours. Navigation, evidence capture, acknowledgement, and future hardware bindings should map to shared application actions rather than duplicate domain logic.

### 2.7 Local-first and resilient

Loss of NAS, Trilium, external APIs, internet services, or future integrations must not prevent the core local process from recording authoritative state.

### 2.8 Safety grows from explicit state, not hidden magic

Trade authorization, progression eligibility, competency state, and evidence maturity should be inspectable. Automatic decisions should not appear until the evidence and rules supporting them are explicit and testable.

### 2.9 Build from whole-loop use

Expand the Cockpit from real operator friction observed across the full loop, not from speculative form growth. A hidden required control or awkward transition is a workflow defect, not merely a visual issue.

---

## 3. Operating model

### 3.1 Trading Day

A **Trading Day** is the top-level operating container for one futures trading day. It owns the collection of Trading Runs and day-level state.

### 3.2 Trading Run

The normal case is one **Trading Run** spanning the operator's active decision process for the day.

Market sessions such as Asia, London, NYAM, and NYPM are **market context inside a run**, not mandatory run containers.

Starting another Trading Run should be an explicit exception used when the operator intentionally wants a fresh process context after a meaningful break or reset.

The default `Run Trading Day` path should therefore naturally begin **Trading Run 1**, while **Start Another Trading Run** remains deliberate.

### 3.3 Core operating loop

The core loop is:

`TDA / Pre-market analysis -> Watch -> Post-Market Review`

This is the same conceptual loop across study and execution environments. The environment changes purpose, timing, and authorization semantics; it should not create a completely separate workflow.

### 3.4 TDA

TDA establishes the working interpretation of the market and the evidence that matters next.

TDA must support:

- draft/autosave/restore,
- complete and intentional incomplete paths,
- version-aware process context,
- top-down bias/draw/thesis,
- market-time and Quarter Theory evidence,
- multiple Models in Play where appropriate,
- explicit watch points and conditional expectations,
- carry-forward into Watch and Review.

TDA is not required to produce a trade. It can correctly conclude with no actionable opportunity.

### 3.5 Watch

Watch is the quiet operating surface for seconds-long decisions and evidence capture.

Its purpose is to:

- keep the active thesis visible,
- show actionable watch points,
- record whether expected evidence occurred,
- track thesis-state changes,
- expose relevant setup candidates,
- make candidate readiness/authorization visible,
- preserve observations into Review.

It should not require the operator to reconstruct TDA or navigate through large forms during active market observation.

### 3.6 Post-Market Review

Review is where the operator records outcome, process adherence, interpretation quality, lessons, and study follow-up.

Review should preserve rather than rewrite the run's historical context, including:

- Trade Plan revision,
- process/playbook snapshots,
- Study/Rehearsal intent,
- competency focus,
- market/QT context,
- captured evidence,
- setup candidates and authorization state,
- run outcome.

---

## 4. Environment ladder and training progression

The accepted environment semantics are:

| Environment | Purpose |
|---|---|
| Historical Backtest / Lab | **Study** |
| Replay | **Rehearsal** |
| Forward Test | **Validation** |
| Live | **Execution** |

These labels describe what the environment is for. **Progression eligibility is separate.**

All environments should increasingly share the same process model so that study evidence transfers toward execution rather than training a different interface.

### 4.1 Historical Backtest / Study

Used to answer explicit study questions, test concepts, catalogue observations, and accumulate evidence.

A focused study question is appropriate here because the environment exists to investigate something.

### 4.2 Replay / Rehearsal

Used to rehearse the process against historical data while preserving realistic sequencing and uncertainty.

Run intent may be present but need not be mandatory.

### 4.3 Forward Test / Validation

Used to validate the current process/model prospectively without live capital exposure.

### 4.4 Live / Execution

Used for actual execution only after the relevant process and safety behavior has matured sufficiently in earlier environments.

Competency scores or evidence thresholds must not become hidden automatic Live locks until the project has explicit, justified rules for doing so.

### 4.5 Eligibility precedes account/capital context

The hierarchy is:

1. **What level of practice is the operator currently eligible for?**
2. **What is the operator doing inside that level?**
3. **Only then, if applicable, which account/capital context is allowed?**

Account type is therefore not a peer to Lab/Replay/Forward/Live.

The intended mapping is:

- Historical Backtest / Lab -> no trading account,
- Replay -> no trading account,
- Forward Test -> Sim / Paper,
- Live -> Prop / Cash.

When the Trade Plan eventually defines justified proficiency requirements, a foundational competency that falls below the required level should make both Forward Test and Live unavailable. The remedy is not to take the same uncertain idea in a lower-risk account. The remedy is to return to targeted Study, demonstrate the competency, integrate it in Replay, validate it in Forward Test, and only then regain Live eligibility.

Moving **up** the ladder should require evidence. Moving **down** should be frictionless and welcoming.

Future eligibility logic should distinguish at least three reasons for restricting higher environments:

- **Eligibility regression** — evidence indicates a competency no longer meets the requirement.
- **Temporary pause** — current personal, market, news, or risk conditions do not permit Live execution today.
- **Unknown / insufficient evidence** — there is not yet enough evidence to certify the higher level.

These conditions may all prevent Live/Forward use, but they require different remedies and should not be collapsed into one generic blocked state.

The existing progression substrate intentionally separates environment purpose from eligibility and supports AVAILABLE / NOT CONFIGURED / BLOCKED states. NOT CONFIGURED means readiness rules do not yet exist; it must not be treated as evidence of readiness or as an automatic hard lock.

---

## 5. Playbooks, opportunities, and authorization

### 5.1 Models are scaffolds, not cages

Named models/playbooks such as the 2022 Mentorship Model and Silver Bullet are useful teaching and process structures, but the Cockpit should not force every opportunity into a named model.

The system must support:

- multiple simultaneous setup candidates,
- named playbook-derived candidates,
- custom/day-specific candidates,
- technician-defined opportunities as the process matures.

### 5.2 Opportunity evidence can outrank model labels

Time, QT/AMDX state, TDA evidence, liquidity, displacement, imbalance, and other observed market facts may establish a valid opportunity even when a named model label is incomplete or absent.

The architecture should reduce execution subjectivity while preserving disciplined technician interpretation.

### 5.3 Authorization separation

Candidate setup conditions and Trade Plan/global safety gates are separate concerns.

A candidate can be technically complete yet still blocked by a day/account/risk gate.

Authorization semantics:

- **Pending blocks entry.**
- **Blocked blocks entry.**
- Only explicit **Clear** safety gates plus satisfied setup conditions can authorize entry.
- Entry authorization may later expire when required context becomes stale.
- Exit/flatten actions must never be blocked by entry authorization logic.

Future broker integration should follow an explicit lifecycle such as:

`analysis -> candidate -> checklist/evidence -> authorization -> arm -> submit -> manage -> close/flatten`

No live order adapter should bypass the same state used in simulation.

---

## 6. Trade Plan and process ownership

The Trade Plan is the authoritative definition of the trading process and its non-negotiable rules.

Plan-owned content may include:

- competencies,
- playbooks/models,
- entry criteria,
- authorization gates,
- market/time restrictions,
- risk and loss limits,
- trade/day capacity,
- management expectations,
- no-trade conditions,
- later economic-news rules.

Changing authoritative plan-owned definitions requires a new published Trade Plan revision.

Not every configurable artifact belongs inside the Trade Plan. For example, summary-template revisions are separate Workbench configuration because they change presentation/output rather than trading permission or process meaning.

---

## 7. Revision and provenance architecture

Historical records should retain enough information to answer **what process was actually in force when this decision was made?**

Revision/provenance targets include:

- Trade Plan revision,
- process/TDA workflow revision,
- playbook/model revision,
- management-rule revision,
- risk/safety-rule revision,
- summary-template revision,
- future checklist revisions.

The current implementation already snapshots selected playbook definitions and records Trade Plan revision on Trading Runs. Summary templates now publish immutable revisions with active pointers and generated-output provenance.

### 7.1 Future revision analytics

The system should eventually support analysis such as:

- process adherence by revision,
- win/loss and expectancy by revision,
- average handles and R by revision,
- drawdown and sample size by revision,
- TDA interpretation quality by revision,
- complete-process outcomes vs override/non-adhered outcomes,
- competency evidence by revision,
- behavior before/after a process change.

Performance and adherence must remain separate axes so a profitable violation is not misclassified as good process.

---

## 8. Competency and evidence model

Keep these concepts separate:

1. **Competency definition** — a plan-owned skill/mechanic.
2. **Competency state** — the operator's current mutable training state.
3. **Evidence** — observations that may later justify changing competency state.

The current plan-owned competency substrate includes:

- HTF liquidity recognition,
- draw on liquidity,
- displacement/FVG recognition,
- premium/discount context,
- time/session awareness.

Study/Rehearsal runs can identify which competencies are being trained, and those links persist into Review.

### 8.1 Evidence maturity

Evidence maturity is a useful future governance concept: concepts and revisions should earn confidence through structured Study, Rehearsal, and Validation evidence before they are treated as mature enough for Execution.

The intended training loop is:

`Lab teaches components -> Replay integrates them -> Forward proves them against live information flow -> Live executes them with capital at risk -> Review sends weaknesses back down the ladder.`

However, the project does **not** currently have justified fixed thresholds for:

- readiness percentages,
- automatic promotion/demotion,
- automatic competency-based Live lock,
- universal minimum sample counts.

Those rules should be derived from actual accumulated evidence rather than invented prematurely.

When a concept is below whatever future maturity standard is adopted, the Cockpit should provide an actionable path back to study/backtest/rehearsal rather than merely showing a bad score.

---

## 9. Market time, Quarter Theory, and AMDX/XAMD

### 9.1 Canonical time

Market-time reasoning uses **America/New_York**.

The futures trading day rolls at **18:00 ET**.

Replay/Historical environments must use the selected historical market timestamp rather than wall-clock time.

### 9.2 Structured temporal evidence

The application should persist factual time/session/QT context as run evidence, including where useful:

- futures-day identity,
- session,
- killzone/window,
- temporal quarter,
- relevant opens,
- prior-cycle relationships.

The current direction is to derive factual temporal/QT state first and keep interpretive AMDX/XAMD classification owned by the Trade Plan/operator rather than hiding it inside opaque automation.

### 9.3 Quarterly Theory hierarchy

The accepted hierarchy for future structured context is:

- 16-year cycle,
- Quadrennial,
- Yearly,
- Monthly,
- Weekly,
- Daily,
- session,
- 90-minute cycle.

The 22.5-minute cycle remains omitted for stability unless later evidence justifies bringing it back.

Weekly QT uses Monday–Thursday as the four quarters; Friday is distortion / separate PO3 context rather than a fifth standard quarter.

Q1 should be interpreted relative to the prior cycle's Q4 where applicable.

### 9.4 AMDX/XAMD

AMDX/XAMD should be recorded as structured expected-vs-observed process context rather than only free text.

The application should be able to preserve:

- anticipated phase/profile,
- observed phase/profile,
- relevant prior-quarter relationship,
- whether the observed behavior confirmed, distorted, or invalidated the expectation.

The product should not force an AMDX interpretation solely because a timestamp falls in a quarter.

---

## 10. Economic news and calendar context

Economic/news integration is a meaningful later priority because it can alter both interpretation and trading permission.

Future requirements:

- ingest an economic calendar/news source,
- identify especially high-impact/red-folder events,
- preserve event timing/context with the run,
- support Trade Plan-specific warnings and lockouts,
- support model-specific conditions such as Friday Asian Range news filters,
- handle major events such as NFP, FOMC, and CPI explicitly,
- account for holidays, early closures, and other schedule distortions.

News should become structured context usable by TDA, QT/AMDX interpretation, authorization, and later analytics—not merely a decorative calendar panel.

---

## 11. Study, observations, summaries, and sharing

### 11.1 Study Find

Study Find is a structured way to catalogue a notable observation with market context, an available move, notes, and chart attachments.

### 11.2 Trade Summary

Trade Summary captures execution/trade context and produces a shareable summary from structured fields.

### 11.3 Configurable summary templates

Summary templates are Workbench-owned, versioned configuration separate from the Trade Plan.

Published template revisions are immutable. New generated summaries use the active revision, and generated/copyable text includes template provenance.

Future useful fields may include additional structured provenance such as the **Trade Plan revision** once that value is exposed through the summary context.

### 11.4 Chart workflow

TradingView remains the preferred chart/study environment.

Near-term and medium-term chart workflow is:

`TradingView -> screenshot/copy/import -> structured Cockpit record -> generated share/review artifact`

A later responsive chart-gallery / Film Night review surface should reuse the existing managed image attachments rather than introduce a second media model. Desired behavior already discussed includes:

- 1 image -> large primary view,
- 2 images -> side-by-side when space permits,
- 3 images -> balanced 2+1 or equivalent layout,
- 4+ images -> compact responsive grid,
- selecting/clicking an image -> full-resolution view,
- layout adapting to the available panel/window size,
- shared gallery behavior across Study Find, Trade Summary, Film Night, and Lab review where practical.

Rebuilding a full TradingView-style charting environment inside the Cockpit is not a current priority.

---

## 12. Workbench / Lab

Workbench is the design and reflection environment, not the active market-operating surface.

Expected long-term responsibilities:

- Trade Plan/process configuration,
- workflow/TDA definition editing,
- playbook configuration,
- summary-template editing,
- revision history,
- study/backtesting catalogue,
- process/revision analytics,
- competency/evidence review,
- friction/feedback review,
- later rule/configuration publishing.

The first Workbench capability exists because summary-template revisioning created a real configuration need.

Do not build a large generic Workbench shell merely to satisfy an old roadmap checkbox. Add Workbench capabilities as real configuration/research needs appear.

---

## 13. Interaction and workspace requirements

### 13.1 TradingView/Cockpit parity

The Cockpit is intended to operate beside TradingView. Workflow modes/stations should correspond naturally to the operator's chart/deck context so the two workspaces advance together rather than fighting each other.

### 13.2 Responsive operating surface

The active operating surface should work as a compact shared-pane desktop companion to TradingView.

Required controls must remain discoverable without forcing excessive scrolling. Hiding a required Models-in-Play control or critical gate because of layout is a functional failure.

### 13.3 Shared application actions

Long-term input bindings should target logical actions such as:

- workflow next/back,
- capture chart,
- mark friction,
- save observation,
- complete no-trade,
- arm trade,
- flatten.

Possible triggers can include GUI, keyboard, mouse, macro pad, SpaceMouse, or future custom hardware.

Dangerous actions require stronger safeguards than navigation/capture actions.

---

## 14. Feedback and process friction

A low-friction feedback mechanism is useful for recording where the Cockpit itself impedes the process.

The current feedback capture/digest capability establishes the substrate.

Future analysis can include:

- friction by workflow step/revision,
- repeated backtracking,
- time per step,
- fields frequently revised,
- commonly overridden requirements,
- recurring user-interface failures.

Do not build large friction dashboards until repeated usage produces enough meaningful evidence.

---

## 15. Data and technical architecture

### 15.1 Current stack

- Python 3.10+
- PySide6 / Qt
- SQLite local authoritative database
- pytest
- Git / GitHub
- Linux primary workstation
- TradingView for charting
- NinjaTrader as the eventual execution target
- Trilium as a future narrative/journal companion
- NAS for safe backup/snapshots, not the live database

### 15.2 Database rules

- authoritative SQLite database stays on local storage,
- WAL enabled,
- foreign keys enabled,
- explicit schema migrations via `PRAGMA user_version`,
- transactional multi-step writes,
- safe backup/snapshot practices,
- RAID is redundancy, not backup.

Do not operate the authoritative SQLite database directly from a NAS share or across the VPN.

### 15.3 Multi-device direction

Near term:

- code travels through Git,
- each machine may keep local application data,
- NAS provides backups,
- interfaces use stable IDs, explicit timestamps/revisions, configurable paths, and repository boundaries.

If shared study data becomes necessary, add deliberate export/sync or a central application service.

If live safety state must be shared across devices, use one authoritative central state/service. Independently synchronized SQLite databases are not sufficient for cross-device trade lockouts, counters, or account safety.

---

## 16. External integrations

### TradingView

Primary charting/study workspace. Prefer screenshot/copy/import and workflow parity over embedded chart replacement.

### NinjaTrader

Primary intended execution platform for eventual real orders.

Integration remains later because the Cockpit must first prove:

- authorization semantics,
- risk/safety state,
- entry vs flatten behavior,
- counters/lockouts,
- persistence/recovery,
- simulation behavior,
- state reconciliation.

### Trilium

Future narrative/journal companion. Cockpit structured records remain authoritative; Trilium can receive links, generated summaries, and richer narrative packages later.

### Economic calendar/news

Future structured context and authorization input as described above.

---

## 17. Current capability status

### Implemented / established

- local SQLite persistence with migrations through schema v27,
- draft autosave/restore for major capture surfaces,
- Guided TDA foundations,
- Trade Plan and process blueprint,
- Trading Day / Trading Run persistence,
- shared runtime across Live/Replay/Backtest/Forward Test,
- TDA -> Watch -> Review workflow,
- watch-point evidence and thesis-state persistence,
- Models in Play / multiple setup candidates,
- declarative playbooks and playbook snapshots,
- setup criteria and separate authorization gates,
- market-time context,
- QT context substrate,
- Study/Rehearsal/Validation/Execution environment semantics,
- Study intent and competency-focus provenance,
- plan-owned competency catalogue and mutable competency-assessment substrate,
- Post-Market Review,
- Study Find capture/review,
- Trade Summary capture,
- chart image import/paste,
- text summary generation/copy,
- configurable/versioned Study Find and Trade Summary templates,
- template provenance in generated text,
- feedback capture/digest,
- manual acceptance smoke-test runner,
- project handoff/decision discipline.

### Partially implemented / needs maturation

- full Trade Plan/process revision architecture across all definition types,
- Workbench as a coherent design environment,
- QT/AMDX top-down interpretation workflow,
- evidence maturity and progression governance,
- process/adherence analytics,
- competency evidence accumulation,
- operator-loop ergonomics from sustained real use,
- richer linkage between Trading Runs, Trade Summaries, Study Finds, and review artifacts.

### Intentionally deferred

- fixed readiness percentages,
- automatic competency promotion/demotion,
- automatic competency-based Live lock,
- broad generic Workbench framework,
- large analytics dashboards before enough data exists,
- multi-device sync,
- Trilium integration,
- NinjaTrader order submission,
- authoritative cross-device Live safety,
- embedded TradingView replacement.

---

## 18. Reconciled milestone roadmap

The roadmap is now organized around product outcomes rather than the old P0/P1/P2 feature queue.

### Milestone A — Coherent process/revision architecture

**Goal:** Every behavior-defining artifact that matters to historical interpretation has clear ownership, revision semantics, and provenance.

Includes:

- define the revision boundary among Trade Plan, process blueprint, TDA workflow, playbooks, management/risk/safety rules, and templates,
- remove remaining ambiguous mutable definitions,
- ensure runs/reviews link to exact revisions/snapshots,
- expose useful revision provenance in generated artifacts where appropriate,
- establish publish/edit semantics in Workbench without building unnecessary generic infrastructure.

**Why first:** analytics and trustworthy evidence are weak if the process that generated a record cannot be identified.

### Milestone B — Harden the whole operator loop

**Goal:** Make `TDA -> Watch -> Review` comfortable enough for repeated daily Study/Rehearsal/Validation use.

Includes:

- use the complete loop repeatedly,
- fix layout/discoverability friction,
- refine transitions and attention cues,
- improve linkage among TDA evidence, setup candidates, Watch, and Review,
- reduce duplicate data entry,
- keep TradingView/Cockpit workspace parity,
- capture genuine friction instead of speculating about more fields.

**Exit condition:** the process can be used repeatedly without the software itself becoming the dominant source of friction.

### Milestone C — Evidence, adherence, and process analytics substrate

**Goal:** Turn accumulated records into evidence about both the trading process and operator development.

Includes:

- explicit adherence facts,
- competency evidence records linked to runs/studies/revisions,
- revision-aware aggregation,
- separate process-quality and P&L/performance views,
- study/rehearsal/validation evidence pathways,
- Evidence Maturity reporting without premature universal thresholds.

**Why before Live:** the system should be able to demonstrate what has actually been practiced and validated before it makes execution-readiness claims.

### Milestone D — Structured QT/AMDX and economic context

**Goal:** Make major temporal/news context first-class and usable by TDA, opportunity interpretation, and later authorization.

Includes:

- complete top-down QT evidence model,
- expected vs observed AMDX/XAMD capture,
- distortion/holiday context,
- economic calendar ingestion,
- red-folder event context,
- Trade Plan warnings/no-trade rules,
- preserved event context for later analytics.

This milestone may overlap B/C in small slices where it removes real TDA friction.

### Milestone E — Execution-safety simulation

**Goal:** Prove the full authorization and safety state machine without sending live orders.

Includes:

- explicit arm/submit/manage/flatten lifecycle,
- stale-authorization handling,
- max trades/day,
- consecutive-loss/day-loss rules,
- cooldowns/lockouts,
- account context,
- restart/recovery behavior,
- simulated order/execution state reconciliation,
- guaranteed ungated flatten/exit behavior.

### Milestone F — NinjaTrader execution integration

**Goal:** Connect the proven Cockpit authorization/safety model to NinjaTrader without creating a second execution truth.

Includes:

- adapter/interface,
- order intent transfer,
- acknowledgement/rejection handling,
- broker/platform state reconciliation,
- recovery from disconnect/restart,
- simulation/shadow mode before real-money enablement.

### Milestone G — Shared/multi-device operation

**Goal:** Provide cross-device access only when it is operationally valuable.

Study data may use export/sync or a central service earlier. Cross-device Live safety requires one authoritative central service/database state.

---

## 19. Near-term sequence after reconciliation

Unless the reconciliation review changes the ordering:

1. Finish and merge the reconciliation documentation itself.
2. Begin **Milestone A — Coherent process/revision architecture** with a small inventory/design slice before changing runtime behavior.
3. Identify the highest-value revision/provenance gap from that inventory.
4. Continue whole-loop Study/Rehearsal usage in parallel and capture friction.
5. Prefer fixes that strengthen the core loop over isolated convenience features.
6. Move toward Milestone C only after revision identities are trustworthy enough for analytics.

---

## 20. Later pile / accepted but not current

These are valid ideas that should not silently become the next task:

- expose Trade Plan revision as a field available to generated summary templates,
- broader summary-template library/catalog management,
- chart-image summary cards,
- responsive chart gallery / Film Night visual review,
- Trilium package/link generation,
- generalized macro/binding system,
- friction heat maps,
- large competency dashboard,
- embedded charting,
- multi-device study sync,
- centralized PostgreSQL service,
- direct NinjaTrader execution.

---

## 21. Open design questions

Keep these explicit until evidence or implementation work resolves them:

- exact ownership/revision boundaries among Trade Plan, process blueprint, TDA workflow, playbooks, management rules, risk rules, and safety rules,
- final TDA station/field structure,
- exact Workbench publishing UX for non-template definitions,
- competency evidence taxonomy and evidence-maturity calibration,
- criteria for future Live eligibility,
- how a completed Trading Run links to one or more executed Trade Records,
- how Study Finds should link to runs/competencies/revisions,
- economic-calendar provider and normalization model,
- exact holiday/early-close distortion representation,
- NinjaTrader bridge and reconciliation protocol,
- initial multi-device study-data strategy,
- Trilium linking/package format.

---

## 22. Development and acceptance discipline

For each substantial slice:

1. start from an up-to-date `main`,
2. use an isolated branch,
3. prefer a small vertical slice,
4. run the automated suite,
5. run relevant manual acceptance checks,
6. inspect the diff,
7. update `PROJECT_STATE.md`,
8. append durable decisions to `DECISIONS.md`,
9. merge only a known-good checkpoint.

The manual smoke-test runner is a convenience layer over `docs/SMOKE_TEST.md`; Markdown remains the durable acceptance record.

---

## 23. Priority test for future work

Before adding a feature, ask:

> Does this materially improve process adherence, reduce operating friction, preserve honest/structured evidence, strengthen safety, or make accumulated evidence meaningfully analyzable?

If not, it is probably not the next priority.
