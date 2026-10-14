# ICT Trading Cockpit — Project Evolution

**Purpose:** Preserve the chronological architecture story so future handoffs can distinguish current decisions from older ideas that were later refined, superseded, or deliberately deferred.

This is not the canonical requirements document. Current product truth belongs in `PROJECT_REQUIREMENTS.md`; exact implementation state belongs in `PROJECT_STATE.md`; durable accepted decisions belong in `DECISIONS.md`; conflicts/supersession belong in `DECISION_AUDIT.md`.

## Reading rule

Later accepted decisions supersede earlier exploratory discussion unless a later decision explicitly preserves the earlier behavior.

Do **not** infer current priority merely from how detailed an older feature discussion was.

---

## Phase 1 — Stable capture substrate

Early work established:

- local-first SQLite persistence,
- migrations and restart recovery,
- Guided TDA foundations,
- Study Find capture/review,
- Trade Summary capture/sharing,
- chart attachments and clipboard paste,
- feedback capture and Markdown digest export.

The important realization from alpha use was that the Cockpit had useful tools but lacked a larger executable process architecture.

## Phase 2 — Process Blueprint / Workspace Parity

The project moved from isolated screens toward:

`Process -> Mode -> Deck -> Station`

A station became an intentional analytical operation rather than merely a form field.

Workspace parity with TradingView became a foundational principle: the Cockpit should guide the operator through chart-oriented analytical work without needing to electronically control TradingView.

Trade Plan high-level structure converged on:

- Foundation
- Rules / Safety
- Process
- Playbooks
- Review / Development

Review / Development was explicitly established as parallel to Process:

- Process = operate the current Trade Plan.
- Review / Development = improve the current Trade Plan.

## Phase 3 — Executable TDA and dual views

TDA became the first executable consumer of the Process Blueprint.

A station was refined into three generic responsibilities:

1. **Action** — what to do on the chart.
2. **Observe** — what is seen after doing it.
3. **Carry Forward** — what conclusion/state matters later.

Focus and Deck became two views over the same session state:

- Focus = current analytical operation.
- Deck = spatial/whole-deck orientation.

Explicit station completion was separated from navigation. Entering work or mouse-forward navigation does not certify completion.

The current mouse interaction pattern became important enough to protect from accidental redesign.

## Phase 4 — Trading Day runtime and explicit transitions

A Trading Day lifecycle was introduced above TDA:

`TDA -> Watch -> Review -> Complete`

Transitions became explicit process decisions rather than generic navigation.

Durable semantics included:

- incomplete TDA cannot silently advance,
- intentional incomplete override is recorded,
- Stand Down / No Trade is a first-class successful process outcome,
- Return to Analysis is deliberate but non-punitive,
- final completion is intentionally terminal,
- persistence should remember where the operator was, what was done, and what remained.

Persistence became a product design principle, not merely storage plumbing.

## Phase 5 — Session-Run model explored, then refined

An intermediate architecture proposed one or more market-session-shaped runs (Asia/London/NYAM/NYPM) inside a Trading Day, with selective TDA carry-forward/refresh.

This was useful for discovering several durable requirements:

- market sessions matter as context,
- application close/restart must not conclude a run,
- 18:00 New York defines the futures-day boundary,
- context can remain valid, require refresh, or become invalid,
- zero-trade periods still contain useful evidence,
- more than one intentional run in a futures day may be valid.

**Later refinement:** the normal case became one Trading Run across the active process, with market sessions treated as context rather than mandatory run containers. Additional Trading Runs remain deliberate exceptions. Do not resurrect the earlier per-session-run hierarchy as the default architecture.

## Phase 6 — Watch and Post-Market learn from actual use

The first visible Live Watch evidence-capture expression felt too much like journaling during a high-attention mode.

The project deliberately stopped polishing it and moved downstream to Review.

Post-Market evolved from a raw chronological log into:

1. **Market Review** — TDA expectation versus what changed.
2. **Process Review** — adherence and takeaway.

Raw telemetry remains useful as background evidence but should not dominate the operator surface.

Interpretation outcome was separated from process adherence:

- materially accurate,
- changed — missed critical information,
- changed — unexplained / study needed,
- changed — external / exogenous.

“Unexplained / Study Needed” means unknown to the technician at the current level of understanding, not random market behavior.

## Phase 7 — Shared Trading Run context

Live, Replay, Historical Backtest, and Forward Test were placed on the same underlying process substrate.

A Trading Run carries provenance such as:

- environment,
- Trade Plan revision,
- TDA,
- Watch,
- Review.

The architectural claim became: practice the same process intended for live use, rather than maintain a separate “Lab process.”

Later work refined this further: shared substrate does **not** mean identical interface emphasis across environments.

## Phase 8 — Operationalize the Trade Plan

Structured Playbooks became declarative, revisioned Trade Plan data rather than GUI-embedded strategy logic.

Playbooks can define:

- applicability,
- standard IF -> THEN watch points,
- setup/entry criteria,
- authorization requirements,
- management/target rules,
- risk/stop guidance.

Runs snapshot the operational rules they actually used so historical records remain reconstructable after later revisions.

Long-term direction: authoritative Playbook/process definitions should be configurable/no-code from the Cockpit, with published revision boundaries protecting changes.

## Phase 9 — Authorization becomes explicit

Authorization was separated into layers:

- setup/candidate criteria,
- run-wide Trade Plan/safety gates,
- candidate-specific risk gate.

Pending and Blocked both prevent entry. Only explicit Clear state plus satisfied setup conditions can authorize.

Authorization means “the recorded information says the Trade Plan permits this candidate”; it is not an order submission action.

Future execution must preserve separate entry authorization and always-safe exit/flatten behavior.

## Phase 10 — Time and QT become first-class state

Whole-loop use exposed that the Cockpit knew too little about **when** market behavior was occurring.

Market Time Context established:

- America/New_York as canonical market time,
- 18:00 ET futures-day rollover,
- session/time-window context,
- deterministic historical time for Replay/Backtest.

Watch then consumed timed model relevance such as Upcoming / Active / Closed.

QT/AMDX work added:

- structured QT interpretation,
- raw QT stack independent of AMDX interpretation,
- derived calendar-month AMD role,
- higher-order raw quarter stack,
- descriptive stack alignments.

A key safety principle was established:

**raw/time facts != interpretation != probability != authorization**

Stack alignment is currently descriptive context only.

## Phase 11 — Opportunity synthesis and attention cues

The Cockpit began synthesizing trusted dimensions without collapsing them:

- temporal relevance,
- TDA state,
- QT stack context,
- setup development,
- authorization.

Attention cues such as MONITOR / PREPARE / FOCUS were introduced as a reusable “when should I care?” concept.

The architecture was deliberately generalized beyond named models: a future temporal opportunity source could come from a named Playbook, technician hypothesis, empirical tendency, or future Trade Plan rule.

At this point, the project explicitly recognized diminishing returns from further Live-Watch embellishment.

## Phase 12 — Deliberate pivot toward Lab / Study

The center of gravity shifted toward the learning system.

The immediate direction became:

- first-class Study/Lab purpose,
- structured study evidence,
- Replay progression semantics,
- Review/Development consumption,
- later empirical hypotheses and evidence maturity.

The goal was not statistics yet. The goal was to make deliberate practice produce trustworthy structured evidence.

## Phase 13 — Environment and purpose semantics settle

The canonical ladder became:

- Historical Backtest / Lab -> **Study**
- Replay -> **Rehearsal**
- Forward Test -> **Validation**
- Live -> **Execution**

Baseball analogy:

- Backtest = drills,
- Replay = scrimmage,
- Forward = preseason/exhibition against live information,
- Live = real game.

Environment and intent were separated:

- **Environment** = how market reality/information is being presented.
- **Purpose / Intent** = what the technician is trying to accomplish.

Study intent can therefore exist in Replay or Forward without redefining those environments.

Evidence from different environments must not be pooled casually because Study samples, Rehearsal runs, Forward validations, and Live observations represent different evidence quality.

## Phase 14 — Eligibility is separate from environment and account

The hierarchy was refined again:

1. What level of practice is the operator eligible for?
2. What are they doing inside that level?
3. Only then, which account/capital context applies?

Account type is therefore not a peer to Lab / Replay / Forward / Live.

Expected mapping:

- Historical Backtest -> no account,
- Replay -> no account,
- Forward -> Sim / Paper,
- Live -> Prop / Cash.

Moving **up** should require evidence. Moving **down** should be frictionless and inviting.

Future higher-level restrictions should distinguish:

- eligibility regression,
- temporary pause,
- unknown / insufficient evidence.

The first progression substrate introduced AVAILABLE / NOT CONFIGURED / BLOCKED without inventing readiness thresholds.

## Phase 15 — Competency / Proficiency substrate

The project then moved into the competency layer.

Three things were explicitly separated:

1. **Competency definition** — plan-owned skill/mechanic.
2. **Competency state** — mutable current training state.
3. **Competency evidence** — future observations that may justify state change.

The first practical loop became:

`Trade Plan competency catalog -> current proficiency state -> Study Run focus -> future evidence`

The competency catalog is authoritative Trade Plan data and therefore versioned with the plan.

No percentages, automatic promotion/demotion, automatic competency-based Live lock, or fixed thresholds were introduced.

## Phase 16 — Configurable summary templates

After competency v0, a smaller roadmap item was completed:

- versioned immutable Study Find / Trade Summary templates,
- Workbench editing/publishing,
- active revision pointers,
- template revision provenance in generated output.

This was useful but did **not** change the larger architectural frontier.

## Current architectural frontier

The recovered development trajectory had already shifted away from more Live-Watch expansion and toward the learning/progression loop.

The frontier has advanced through the human Review / Development synthesis layer. The current progression-governance frontier is:

`boundary-aware Evidence Maturity -> Trade Plan progression policy -> explainable eligibility -> regression/downgrade semantics -> operator-loop integration -> later Live Execution governance`

The completed human synthesis chain beneath it is:

`Evidence -> Competency Synthesis -> Cross-Run Observation -> Development Direction -> targeted Study routing`.

Do not return to older Film Night, responsive-gallery, visual-polish, broad TradingView-integration, hardware-controller, or Live-Watch feature queues merely because those discussions were detailed. They remain valid later ideas unless actual use makes them blocking.


## Phase 16 — Review / Development synthesis

After the first competency-evidence loop became operator-complete, the project moved from collecting/inspecting evidence into the next architectural question: how accumulated evidence should inform deliberate development without becoming an automatic proficiency score.

The first design candidate introduces a human-reviewed **Development Direction** layer between evidence and later competency-state/progression governance.

This phase preserves the separation:

`Study Outcome -> evidence -> human synthesis / Development Direction -> later state/maturity/progression decisions`

Automatic weakness inference, readiness scoring, competency-state mutation, and eligibility changes remain deferred.


## Phase 17 — Evidence Maturity and progression governance

Milestone B completed the Review / Development human-synthesis chain:

`Evidence -> Competency Synthesis -> Cross-Run Observation -> Development Direction -> targeted Study routing`

The project then moved into Milestone C.

The first accepted governance concept is a boundary-aware **Evidence Maturity Profile**. Its purpose is not to score the technician or authorize advancement. It answers whether the available evidence is trustworthy enough to support a decision at a specific progression boundary.

The accepted profile dimensions are:

- Volume / Sample Depth,
- Environment Relevance,
- Recency,
- Consistency,
- Context Coverage,
- Revision Relevance.

Evidence Maturity is explicitly distinct from Competency State, Trade Plan Progression Policy, and Eligibility.

The profile is boundary-aware from the beginning:

`Trade Plan + competency + progression boundary`

with candidate boundaries:

- Study -> Rehearsal,
- Rehearsal -> Validation,
- Validation -> Execution.

Four human maturity states are accepted for v0 — Not Assessed, Insufficient Evidence, Developing Evidence, Decision-Usable Evidence — but the overall state is deliberately removable if operator use shows that it is too evaluative. The dimensional profile must remain useful without it.

The accepted Milestone C sequence is:

`C1 Evidence Maturity Profile -> C2 Progression Policy -> C3 Explainable Eligibility -> C4 Regression/downgrade semantics -> C5 Operator-loop integration and guardrails`

No numeric readiness score, hidden weighting, automatic promotion/demotion, or Live lock is implied by entering this phase.


## 2026-10-10 — Milestone C completed

Milestone C closed the progression-governance architecture without introducing arbitrary readiness math.

The completed chain is:

```text
Evidence Maturity
    ↓
Trade Plan Progression Policy
    ↓
Explainable Eligibility
    ↓
Historical Attainment / Regression-Revalidation semantics
    ↓
Operator-loop integration and guardrails
```

C5 established that progression eligibility is enforced at the moment of a deliberate **new upward environment start**. It is not a continuous runtime kill switch.

A configured BLOCKED boundary now has an explainable lower-friction operator path:

```text
BLOCKED upward transition
    ↓
concise reason + requirement detail on demand
    ↓
Review / Development > Progression
    or
stage normal lower environment
    ↓
operator explicitly starts next run when ready
```

The integration preserves these separations:

- progression eligibility != trade/setup authorization,
- current eligibility != historical attainment,
- eligibility loss != competency regression,
- progression restriction != temporary operating/safety pause,
- lower-rung movement != punishment/demotion.

Started runs preserve historical provenance and are not silently terminated or demoted if progression support later changes. Restore/browse/staging do not create duplicate attainment. Exit/flatten remains outside progression and entry gating.

Alpha 0.7 intentionally remains without a real progression policy. Milestone C therefore completes the **machinery and governance semantics**, not the future policy thresholds themselves.

The next major roadmap frontier is Milestone E — Context maturity: QT/AMDX, news, and distortions. Milestone D remains a parallel friction-driven hardening stream.


## 2026-10-10 — Milestone E1 expected-vs-observed QT review

Milestone E began by maturing the existing QT/AMDX substrate rather than immediately adding external news ingestion.

E1 preserved the run-time TDA QT/AMDX interpretation as **expected/working context** and added a separate **observed Review context**.

The resulting structure is:

```text
TDA expected QT / AMDX
        ↓ preserved
Watch / market unfolds
        ↓
Post-Market observed QT / AMDX
        ↓
descriptive comparison
```

Comparison is deliberately non-numeric and uses Matched / Changed / Expected Unknown / Observed Unknown / Not Comparable.

Observed Review state persists independently and does not overwrite the original TDA expectation. Time-derived QT roles remain factual/read-only. A mismatch does not automatically create competency evidence.

Schema advanced to v34 for observed Review context and its optional human note.

Operator acceptance completed with 348 automated tests passing and the guided smoke test fully PASS.

The operator also clarified an important future UI requirement: the mature system must preserve full intraday QT depth—including four sessions per day and four 90-minute cycles per session—without becoming a large form. This is now a durable requirement for later Milestone E interaction design.


## 2026-10-10 — Milestone E2 provider-neutral market context

E2 introduced the external-context domain boundary without selecting a permanent vendor.

The accepted contract separates:

- Economic,
- Holiday,
- Early Close,
- Market Schedule,
- Other Context

and normalizes impact to Low / Medium / High / Unknown while preserving provider-native impact and provenance.

A provider adapter must explicitly map its own vocabulary. Terms such as "red folder" therefore have no hidden built-in meaning.

The event object remains factual context only. It does not contain Trade Plan warning, stand-down, authorization, or block-entry state.

A provider protocol plus deterministic in-memory provider established the integration seam for future API/import/manual adapters.

E2 required no schema migration; schema remains v34. Historical run-specific event snapshots are intentionally deferred to E3.

Acceptance completed with the full automated suite green at 356 passed.

## 2026-10-10 — E6 source capture/import boundary

After E3 historical snapshots, E4 context presentation, and accepted E5 declarative rules, the operator selected the recommended free Forex Factory import direction. E6 v0 adds local weekly JSON preview/import, immutable source captures, explicit future-run selection, and persisted capture provenance in the existing operating loop. Schema v37 stores captures separately from Trading Runs.

Real export inspection required refining the earlier tuple seam: requested dates are not completeness claims, native clocks are not certified precision, and currency labels/detail URLs do not establish market applicability or occurrence continuity. Source completeness, scope, timing/status uncertainty, and historical-knowledge limitations remain visible rather than becoming silent absence or permission. Alpha 0.7 remains unchanged and network/paid acquisition is deferred. Operator acceptance completed on 2026-10-10, with all nine checks PASS in `df4cac894f7e697bf65793c5f031265af5bdd9d4` and the local automated suite reported as 425 passed, after correcting UTC coverage parsing for Python 3.10. Merged through PR #59 (`aaa931153f165b8ebb90c43126e00b6cd07beeeb`) after assessment PR #58. This advances the existing Milestone E frontier without changing roadmap order; E7 model predicates remain downstream at this checkpoint.

## 2026-10-10 — E7 generic model context predicates v0

After E6 acceptance and merge, the next small slice extends the existing snapshotted context-rule contract rather than putting strategy logic in the calendar adapter. Explicit playbook scope, selected NY calendar-day/week windows, event absence and separately configured outcome effects now support generic model conditions. Candidate effects are isolated by stored Playbook identity, with explanatory results in the shared TDA/Watch/Review context surfaces.

The source-completeness boundary remains decisive: an incomplete Forex Factory export cannot become proof of no news, and Unknown is never inverted into a satisfied absence predicate. The Friday Asian Range example is a labeled validation fixture; preceding/following Monday and final policy adoption remain open. Schema v37 and Alpha 0.7 remain unchanged. E7 is operator accepted on 2026-10-11 and merged through PR #60 (`f57794cff6f128830655b458e999fd8f72038280`), after a fresh 456-test review suite passed on Python 3.12.14 with a clean exit. All nine checks PASS after the persistence retest and controlled E6→E7 compatibility retest in `9454414`. The controlled fixture establishes old-code restoration and capture isolation without recovering missing operator history; Milestone E remains current and no roadmap priority changes.


## 2026-10-12 — Durable AMDX quartets integrated into the core loop

PRs #61–66 extend accepted Milestone E with identified day/session quartets, independent expected/observed revision, atomic persistence, retained action/archive meaning, immediate native entry and stable historical Review scope. The operator accepted 245–260 and explicitly authorized dependency-order merging. Main's final merge `d092ac7` exactly matches the accepted `c851e9a` tree and tested `e12a2d4` implementation (744 tests across 70 isolated module processes); no fresh application run is claimed for the identical merge tree. Schema v41 and Alpha 0.7 remain the integrated baseline.

The architectural frontier stays context maturity. The next proposed contract connects existing higher temporal facts to explicit quartet identities and shared projections while preserving legacy interpretation provenance. Study/Lab and Watch can later render the same state with different emphasis. This advances the foundational context direction without elevating final layouts, comparisons, classifiers or execution integration. See `AMDX_HIGHER_STACK_CONTRACT_REVIEW.md`.


## 2026-10-12 — Historical AMDX accumulation moves into the early foundation

The operator made comprehensive historical/forward-test entry across all layers explicit, as far back as needed, initially for MNQ with possible later NNQ use. This changes the next architectural sequence before native higher binding: catalog ownership must be independent of trading runs and retain explicit instrument/capture provenance. PR #69 implements the first v42 catalog backend while preserving existing run history. The bounded higher Review selector remains a separate integration, and mature Lab will provide spacious catalog-backed analysis. Native input, automatic run linkage, bulk imports and statistics follow; no comparison controls are added to Watch.


## 2026-10-13 — Shared calendar reaches bounded higher Review

After operator acceptance of maintained Observed Review (270–274), the shared master calendar now supports higher-stack Review across distinct calendar contexts within a run's original futures day. Context selection is quiet/read-only; legal immediate input records both canonical Observed and immutable assessment proof. The existing receipt owns that proof, avoiding a redundant interpretation or metadata store. Original launch Expected and earlier v1 assessments remain intact, including nullable heads and unknown information availability. A native boundary trial adds checks 275–280 pending operator acceptance. This completes the next functional integration slice before stable consolidation; it does not complete final rendering, criteria/classification, broad legacy imports or the Study-first workflow.


## 2026-10-13 — AMDX consolidation before the next UX frontier

Operator acceptance of bounded higher Review completes checks 261–280 across the historical/shared-native/Observed/higher integration. The consolidation review treats #67–75 as one linear stack, verifies merge order/tree preservation and strengthens direct compatibility with actual main's v41 run/Review data, including late migration rollback. It preserves the earlier purpose-catalog clarification, legacy unknown ownership, immutable operational context and unfinished final renderer/criteria/import scope. This is a stabilization/review checkpoint; merge requires separate authorization before the whole-cockpit UX/Study plan becomes the next active product milestone. See `AMDX_CONSOLIDATION_REVIEW.md`.


## 2026-10-13 — Consolidated AMDX foundation becomes main

After explicit approval of the reviewed nine-PR merge sequence, #67–75 were merged into main in order with merge commits and exact-tree verification. The final code merge `8b7f8ae` is identical to reviewed checkpoint `15e64af`; 1,136-test validation and operator checks 261–280 remain applicable. Main advances from v41 to v46 without a Trade Plan revision change. The maintained historical/operational calendar, immutable run provenance and bounded Observed Review are now the stable foundation for the next whole-cockpit UX/Study implementation plan. Regular-app database backup/sync is documented separately; no user database was opened by the agent and no final renderer/criteria/import work is implied by the merge.


## 2026-10-13 — Whole-cockpit UX/Study implementation plan

After AMDX PRs #67–75 merged, the next authorized work is a comprehensive UX/Study plan rather than more speculative storage. `COCKPIT_UX_IMPLEMENTATION_PLAN.md` maps current capabilities to a primary 16:9 shell, Study doorway, nearby overview/detail, quiet Watch and spacious AMDX Lab. It proposes UX1 safe Study routing, UX2 integrated Study task, UX3 operational renderers and UX4 criteria authoring. Startup active-run handling, ranking, navigation and layout remain explicit proposals. A synthetic interactive walkthrough supports meaningful whole-tool review without changing native behavior or recorded acceptance.

The storyboard's old smaller companion-window target and current-state sections describing unfinished PR #72 integration are reconciled to the accepted override and merged v46 baseline. Historical checkpoint entries remain preserved. Production source/tests/tools, Alpha 0.7, schema and all 280 smoke records are unchanged; no new full-suite result or operator layout acceptance is inferred.


## 2026-10-13 — Operator UX feedback and recovered-context comparison

The HTML walkthrough made the proposal reviewable, and the operator identified dense/homogeneous presentation, inadequate quietness, scattered AMDX context and over-combined Focus/Deck work. The requested historical comparison found supporting requirements in the prequel and continuation: guided action/observation/carry-forward work, spatial Deck → selected Focus access, quiet capture commands, calendar-like QT hub, selective Review and different Lab/Rehearsal/operational emphasis. The repeated 148-pass handoff and cumulative feedback digest are handled as overlap rather than independent new approvals.

`UX_CONTEXT_RECONCILIATION.md` records that comparison and the newer month-calendar/quarter-color and familiar ribbon/task-bar trial preferences. Later shared calendar ownership, exact historical captures, legal quartet revision, primary 16:9 footprint and evidence/eligibility separation remain intact. UI work is paused while the corrected meaning and journey priorities are reviewed. Documentation only; no source/schema/plan/smoke changes or accepted replacement layout.


## 2026-10-13 — UX friction methods and future news/calendar presentation

At the operator's request, UI work remains paused for distinct professional-method research. `UX_FRICTION_RESEARCH.md` connects task analysis, progressive/staged disclosure, command organisation, perceptual grouping, stable navigation and understandable cues with inspection, cognitive walkthroughs and goal-based operator trials. Twelve quality criteria are proposed for discussion, with actual usability evidence separate from functional pass counts. The calendar news/quarter/AMDX cue wish is retained as future presentation, preserving historical knowledge and empirical-versus-temporal distinctions. No new renderer, feed, schema, plan policy or operator acceptance is introduced.

## 2026-10-13 — Layout parity and design touchstones preserved

The operator clarifies that the four-pane TDA Deck is more than an overview: it maps positionally to the four-pane TradingView layout so both monitors can be read like facing pages while capturing criteria and points of interest. `WORKSPACE_PARITY.md` now makes that mapping, shared Focus/Deck state and revision ownership explicit. `UX_DESIGN_TOUCHSTONES.md` retains the compact phrases and motifs that carry product meaning and supplies cross-examination questions for future proposals. This documentation checkpoint changes no renderer or production behavior.

## 2026-10-13 — Focused TDA layout-parity review artifact

`TDA_LAYOUT_PARITY_INTERACTION_SPEC.md` turns the accepted parity principle into a reviewable journey. Its standalone HTML pairs a schematic four-pane TradingView monitor with the position-matched Cockpit Deck, then demonstrates mapped station Focus, Action/Observe/Carry Forward, shared state, return without completion, explicit completion and disposable reload persistence. Automated browser assertions cover the principal interaction, and Deck/Focus were inspected at 1600×900. This remains a disposable proposal rather than native UI or operator acceptance.

## 2026-10-13 — TDA parity focused trial succeeds

The operator reports a meaningful improvement in feel and flow. The accepted direction now includes however many revision-defined four-pane TDA Deck/TradingView layout pairs the full analysis requires, mapped Deck/Focus state, quiet inactive panes, and subtle border/state cues that support rapid reacquisition after looking to the chart monitor. Existing scroll and mouse-button behavior remains valuable; direct `1`–`4` selection is promising; later macro-pad/CAD-mouse bindings should target the same actions. `TDA_LAYOUT_PARITY_OPERATOR_REVIEW.md` records the accepted relationship and remaining control/styling choices. No native UI change is inferred.


## 2026-10-13 — Quiet Watch/support-return journey becomes reviewable

`WATCH_QUIET_SUPPORT_INTERACTION_SPEC.md` and a disposable standalone HTML isolate the second corrected journey. The proposal consolidates current AMDX context, direct legal active-90-minute entry, contextual Study Find capture and read-only full-stack inspection around an unchanged Watch return anchor. It intentionally omits history/comparison, automatic classification and real persistence. Automated browser checks cover direct X(R), capture/save/return, inspection/return, unfinished-draft recovery and reload; 1600×900 Watch, capture and inspection states were visually checked. This is a review artifact, not operator acceptance or native implementation.

## 2026-10-14 — Quiet Watch review and nested Lab direction

The operator strongly endorses contextual Study Find access/return, including main-body dismissal, and reports improved quietness and rapid reacquisition after looking to TradingView. Direct active-cycle entry and current-state-only Watch scope remain intact. The trial also exposes three correctable defects: saved Study Find text reappears as a draft, Full Stack return moves away from its entry command and the green quiet cue demands attention. The standalone fixture corrects those behaviors without changing production code.

The Watch/full-stack AMDX layout is not accepted. A flat list does not convey temporal containment, and enlarging it does not create analytical space. The operator's Trilium screenshot validates a disclosure-tree path from year through quarter, month, week and day while also demonstrating deep indentation and vertical-scan costs. `LAB_AMDX_CALENDAR_TREE_INTERACTION_SPEC.md` therefore proposes a bounded current-path feature tree synchronized with a calendar/detail workspace and semantic zoom. The tree navigates; the workspace supports inspection, entry and analysis.

The review also records a constrained contextual support rail, early synthetic broker/process-safety projection and explicit ultrawide/dedicated-monitor composition trials. Broker information supports adherence rather than P&L stimulation; the rail is not an unrestricted dashboard builder. No native renderer, broker integration, schema, plan or smoke record changes.

## 2026-10-14 — Lab calendar/feature-tree journey becomes reviewable

`prototypes/lab-amdx-calendar-tree-v0.html` makes the Trilium-informed direction tangible without copying a permanently expanded tree. A bounded current path and nearby siblings remain on the left; breadcrumb, selection and detail stay synchronized; the center changes shape across year/quarter overview, real October month grid, week strip, session quartet and 90-minute quartet. Expected/Observed switching, direct legal role entry, profile implication, explicit unavailable history, incomplete-news cues and Follow Current are disposable local fixture behavior.

Focused interaction assertions cover month geometry, semantic zoom through week/day/session/cycle, immediate X(R) revision, channel independence, zoom-out parent restoration, truthful unavailable selection, Follow Current and reload continuity. JavaScript parsing, local links, smoke-document checks and diff formatting pass. The prototype does not open the operator database or change source, schema, Trade Plan or smoke records. Operator review remains required before deriving the compact Watch renderer or attempting native composition.

## 2026-10-14 — Lab review requires independent context depth

The operator reports that the tree, center workspace and right rail feel good together; Follow Current and missing-entry handling are useful; and the real October calendar with visible news is a strong step. The review is recorded in `LAB_AMDX_CALENDAR_TREE_OPERATOR_REVIEW.md`. Higher views remain too generic and do not expose enough of what lies inside the selected period.

The updated prototype separates temporal zoom from Quiet/Nested/Deep context depth. A month can retain its ancestor chain while optionally revealing compact session quartets and selected lower-cycle cues inside days. Standard month/year navigation, week Q1–Q4/distortion markers, true-open due/recorded/unavailable states and richer Year/Quadrennial/16-year child canvases are added. True opens are presented as adjacent market facts, not AMDX judgments; fixture marking adds no production repository. The shell names AMDX Calendar as the active Lab lens and explicitly retains broader Study, evidence, criteria and sample work outside this focused lens.

This remains a disposable interaction study. No source, schema, plan, news feed, true-open persistence, market-data integration or smoke records change. Operator review of density and hierarchy remains required before deriving Watch.

## 2026-10-14 — Lab hierarchy favors semantic grouping over decorative color

The second Lab review accepts Quiet/Nested/Deep as a useful configuration and endorses the calendar controls and higher-timeframe context spine. It also identifies that Q1–Q4 color across every day in a month row only repeats ordinal position and creates attention cost without enough analytical information. The corrected trial uses a neutral left week rail: Quiet preserves physical grouping only, Nested adds actual week/daily AMDX values, and Deep adds the interval and compact session roles.

True opens now sit at their period location in the year/month/week/day projections. Lab may inspect or edit the fact, while TDA owns the reminder when an unmarked open becomes temporally relevant. A later display policy may permit restrained cue/color visibility without changing shared ownership.

The combined **Lab · AMDX Calendar** control preserves a promising CAD-workbench analogy for movement among Cockpit phases and analytical lenses, but it does not settle the taxonomy. Temporal zoom also remains open: separating it from context depth helps, but the current controls and selection behavior are not accepted. The third standalone iteration tests these narrower questions only; production behavior remains unchanged.

## 2026-10-14 — Calendar depth accepted as a direction, full Lab remains open

The third review finds the calendar's Quiet/Nested/Deep distinction materially better and asks that the same semantic-density discipline reach the tree and other layers. The full AMDX Lab portion remains a good start rather than a final form.

The fourth trial removes generic quarter color from tree marks, higher-level groups, quartet cards, compact stacks and the detail profile. Text/order/grouping carry Q1–Q4; selection, current reference, unavailable data, news and entered/implied states retain their own cues. Only the four named Trading Day session cards retain a restrained palette edge as a provisional test of stable domain identity. Increasing context depth adds information, not saturation.

This records partial acceptance precisely: the calendar depth model advances, while the overall workspace, remaining color policy, temporal zoom, controls and native composition stay open. No production source, schema, persistence or smoke records change.

## 2026-10-14 — Isolated AMDX Lab direction checkpointed

The operator confirms that the initial direction questions are satisfied and agrees to stop polishing the standalone AMDX Lab fixture. Quiet/Nested/Deep calendar density, neutral hierarchy and restrained session color carry forward. The session palette earns its place because it matches established Asia/London/NYAM/NYPM chart indicators and can aid cross-monitor recognition.

This is a directional checkpoint rather than full/final approval. Real historical editing, temporal movement, definitions/evidence/news/Study Find use, broader Lab composition, TDA/Watch/Review integration, native input and monitor layouts still determine the mature result. The unresolved zoom interaction is deferred until an integrated workflow makes the problem concrete.

The active design frontier now moves outward: compose a Study-first Lab that can coordinate competency/question guidance, chart evidence and Study Finds, criteria/definition research, historical and forward samples, and transitions to the other Cockpit workbenches. AMDX Calendar remains foundational but is one lens, not the identity of Lab.

## 2026-10-14 — Broader Study-first Lab composition becomes reviewable

`LAB_STUDY_WORKBENCH_INTERACTION_SPEC.md` and `prototypes/lab-study-workbench-v0.html` move outward from the accepted isolated AMDX direction. The proposed Lab opens with one dismissible, bounded competency question for the tired-technician use case, then keeps that question stable while Study Plan, Evidence, Criteria, Samples and AMDX Calendar provide different analytical lenses. A left Study map orients, the center performs the current operation and the right rail exposes one contextual support tool with an optional pinned companion.

The proposal reflects the supplied trading-plan material without copying it into one large form: plan-owned definitions, preparation, chart evidence, backtest/replay/forward samples, measurement, review and deliberate revision remain distinct operations. Study Find inherits the active question and context, preserves a draft on close and returns to Evidence after save. The AMDX calendar uses the same maintained foundation and does not become a separate catalog or consume every Lab screen.

Focused mock-DOM interaction assertions cover startup/resume, lens continuity, draft close/reopen, save-and-return, evidence count, AMDX routing, contextual support, pinning, keyboard lens access and reload recovery. HTML and inline JavaScript parse cleanly. The fixture remains browser-local and synthetic; no application source, schema, Trade Plan, smoke record, database or screenshot storage changes. Operator review is required before selecting a first native composition slice.
