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

The frontier is:

`targeted Study -> competency evidence -> Replay integration -> Forward validation -> progression/eligibility -> Live Execution`

with Review / Development eventually consuming accumulated evidence to:

- identify weaknesses,
- recommend targeted Study,
- compare process revisions,
- assess evidence maturity,
- support justified progression rules.

Do not return to older Film Night, responsive-gallery, visual-polish, broad TradingView-integration, hardware-controller, or Live-Watch feature queues merely because those discussions were detailed. They remain valid later ideas unless actual use makes them blocking.


## Phase 16 — Review / Development synthesis

After the first competency-evidence loop became operator-complete, the project moved from collecting/inspecting evidence into the next architectural question: how accumulated evidence should inform deliberate development without becoming an automatic proficiency score.

The first design candidate introduces a human-reviewed **Development Direction** layer between evidence and later competency-state/progression governance.

This phase preserves the separation:

`Study Outcome -> evidence -> human synthesis / Development Direction -> later state/maturity/progression decisions`

Automatic weakness inference, readiness scoring, competency-state mutation, and eligibility changes remain deferred.
