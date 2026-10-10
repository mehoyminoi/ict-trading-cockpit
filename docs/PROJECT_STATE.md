# ICT Trading Cockpit — Current Project State

**Last handoff update:** 2026-10-10

This is the starting point for a new development chat or developer handoff. Git remains the source of truth for code; this file records the verified project checkpoint and the reasoning context needed to continue without reconstructing chat history.

## Repository state

- **Active branch:** `feature/context-maturity-e4-v0`
- **Main baseline:** `9d1fb5d0181a9ed50675c95aeb189156c99c5af7` — PR #55 merged E3 historical market-context snapshots and Qt test cleanup
- **Implementation checkpoint:** `c9d49ef5bbfffcd157b3456cd0155b6ae16f56a7` — Present stored market context across TDA Watch and Review (E4)
- **Current slice:** E4 — compact operator context surfaces, pending operator acceptance
- **Schema:** v35
- **Trade Plan revision:** Alpha 0.7
- **Verified full test result:** **373 passed** in 132.53s on 2026-10-10, clean exit (Python 3.12 / PySide6 6.8.3 / offscreen)
- **Manual acceptance:** E1 fully PASS. E3 required no new UI smoke pass. E4 focused operator smoke is **NOT TESTED**.

## Completed foundation — Competency / Proficiency substrate v0

Implemented/established in this slice:

- plan-owned competency definitions,
- competency/profile persistence,
- Study Run focus links,
- competency assessment tracking/schema support,
- mentorship Trade Plan competency coverage/tests,
- deterministic Replay context for tests that exercise timed Live Watch behavior.

The first practical competency loop is:

Trade Plan competency catalog
→ current proficiency state
→ Study Run focus links
→ future evidence against the competency

Historical Backtest / Study is therefore able to identify which plan-owned mechanics it is training and preserve that association for later Review. Replay and Forward Test can also preserve competency-only run intent when the optional Focus/question is blank.

## Accepted architecture

### Environment ladder

- Historical Backtest / Lab → **Study**
- Replay → **Rehearsal**
- Forward Test → **Validation**
- Live → **Execution**

Progression eligibility remains separate from these semantic labels.

### Competency ownership and evidence

- Competency **definitions** belong to the versioned Trade Plan.
- Competency **state** is separate mutable profile data.
- Competency **evidence** is separate from both the definition and state.
- Changing the authoritative competency catalog requires a new published plan revision.

See `docs/DECISIONS.md` for rationale.

## Intentionally deferred

Do not assume these exist merely because the competency substrate exists:

- proficiency percentages or readiness scores,
- automatic promotion/demotion,
- automatic Live eligibility lock based on proficiency,
- fixed proficiency thresholds,
- a large competency/proficiency dashboard.

These require evidence/threshold rules that have not yet been justified.

## Test-history clarification

An earlier run on this branch collected 267 tests and reported **265 passed / 2 failed** in `tests/test_structured_playbook.py`.

Those failures were time-context dependent. Pulling through implementation commit `9fa5807` changed the affected structured-playbook tests to deterministic Replay runs; the subsequent full suite was **267 passed**. Do not carry the earlier result forward as an unresolved Live Watch production regression.

## Manual acceptance status

Current operator checks completed on 2026-10-07:

- non-Live environments expose the expected five competency focus checkboxes,
- competency focus selections persist into Post-Market Review,
- competency focus selections persist after application restart as part of the Trading Run,
- launcher checkbox selections do not repopulate after restart; this is expected because the launcher represents a new run while persisted Study Context belongs to the started/restored run,
- Post-Market Review reopening at Market Review stage 1 rather than the previously viewed stage 2 is accepted transient UI behavior,
- smoke testing exposed a Replay/Forward defect where competency-only intent was discarded when the optional question was blank,
- that defect was fixed and manually re-verified in both Replay and Forward Test,
- the full automated suite after the fix is 268 passed.

See `docs/SMOKE_TEST.md` for the completed acceptance record and repeatable checklist.

## Recently completed

### Competency / Proficiency substrate v0 — merged via PR #26

- plan-owned competency definitions,
- mutable competency/profile persistence kept separate from definitions,
- Study / Replay / Forward competency-focus provenance,
- competency focus preserved into Review and restart persistence,
- deterministic Replay context for time-aware tests,
- manual smoke-test acceptance complete.

### Developer smoke-test runner v0 — merged via PR #27

- PySide6 runner for `docs/SMOKE_TEST.md`,
- PASS / FAIL / QUESTION / NOT TESTED controls,
- per-item comments/evidence,
- previous/next and next-unresolved navigation,
- live acceptance summary,
- save-back to Markdown,
- Markdown round-trip unit tests,
- manually verified that edits persist and only intended Markdown changes appear in Git diff.

The runner remains a convenience layer over Markdown, not a second acceptance-data format.

## Current architectural frontier

Milestones A, B, and C are complete. The learning/progression chain remains intact:

`Evidence -> Competency Synthesis -> Cross-Run Observation -> Development Direction -> targeted Study -> Evidence Maturity -> Trade Plan Progression Policy -> Explainable Eligibility -> historical attainment / regression-revalidation -> operator-loop guardrails`

The current major frontier is **Milestone E — context maturity: QT/AMDX, external events, schedules, and distortions**. E1, E2, and E3 are merged. E4 now exposes the stored context to the operator; it does not introduce context-policy evaluation.

Milestone D continues only for demonstrated operator friction. Film Night, gallery polish, broad TradingView integration, hardware controls, and broker execution remain downstream.

## Last completed slice

**E3 — historical context snapshots**, merged through PR #55:

- run-start event/schedule snapshot persisted in schema v35,
- selected historical futures-day queries for Replay/Study,
- Available-empty / Not Configured / Unavailable remain distinct,
- restore reads stored context rather than re-querying a provider,
- provider revisions do not silently rewrite historical runs,
- full automated acceptance: **364 passed**, clean exit,
- test-session Qt cleanup stops test-owned timers and disposes windows before draining events.

## Current task

**E4 — compact operator context surfaces** is implemented for operator validation on `feature/context-maturity-e4-v0`.

Implemented behavior:

- one shared read-only Market context card in TDA, Watch, and Review,
- visible snapshot availability and event/schedule counts without treating missing context as a successful empty query,
- TDA summary keeps raw QT facts separate from AMDX expectation,
- Watch shows the next recorded event time relative to the run's market timestamp, with simultaneous events accounted for; no arbitrary warning horizon or event-duration window,
- cancelled, postponed, and already released events are not advertised as upcoming; all stored records remain inspectable,
- recorded schedule facts remain distinct from economic events and QT structural distortion,
- outside-window or missing market-time context is explicit,
- bounded expandable detail includes run/Trade Plan provenance, QT expectation/observed Review state, snapshot query/reference/capture times, and all provider/native event fields,
- rendering, passive timer refresh, mode changes, and restored runs never query a provider or mutate the stored snapshot,
- normal compact Focus navigation remains unchanged outside Premarket Thesis; the dense Thesis station and expanded context detail permit scrolling,
- stable UI anchors under `process.market_context`,
- disposable fixture window: `python tools/context_surface_demo.py`,
- schema remains **v35**; Trade Plan remains **Alpha 0.7**.

Acceptance:

- final full automated suite: **373 passed**, clean exit,
- automated coverage includes availability/legacy honesty, historical time, timezone normalization, event statuses, simultaneous events, explicit unknown/outside-window timing, full Review provenance, plain-text rendering, progressive disclosure, normal runtime transitions, passive refresh, and repository-backed restore without provider re-query,
- developer offscreen visual inspection at 1024×768 covers compact TDA, the dense Thesis controls, and expanded Review detail,
- operator acceptance is still **NOT TESTED**; use the E4 section in `docs/SMOKE_TEST.md`,
- do not merge E4 until the focused operator pass is recorded.

Next action: pull E4, run pytest, exercise the fixture and normal application checklist, record acceptance, then merge. The next implementation slice after accepted E4 is **E5 — declarative Trade Plan context rules**.

## Explicitly deferred / open

- no real calendar provider selected or wired into normal application startup,
- no within-run snapshot refresh/version history,
- no warnings, restrictions, authorization changes, readiness scores, or automatic competency evidence,
- no full intraday session × 90-minute interpretation grid in E4,
- `CONTEXT_MATURITY.md` has inconsistent later E6/E7 numbering between narrative sections and the implementation sequence. Reconcile that when planning those slices; it does not block E4/E5 and is not permission to reorder the roadmap.

## System guide maintenance

`docs/SYSTEM_GUIDE.md` is now part of the maintained handoff package.

Update it when terminology, subsystem relationships, ownership boundaries, or major system loops materially change. Do not update it for ordinary bug fixes or minor UI changes.

The guide is explanatory and must not supersede `PROJECT_REQUIREMENTS.md`, `DECISIONS.md`, `PROJECT_STATE.md`, the decision audit, or verified implementation.

## Continuity protocol

For every substantial feature slice, update this file before the slice is considered complete.

At minimum update:

- branch,
- implementation baseline SHA/message,
- test count/status,
- schema,
- Trade Plan revision,
- completed work,
- current task,
- unresolved issues,
- intentionally deferred behavior.

Append durable design decisions to `docs/DECISIONS.md`.

See `docs/HANDOFF.md` for the complete handoff procedure.


## E1 operator note — intraday QT depth

**Intraday QT depth requirement recorded.**

The E1 QT/AMDX surface is sufficient for current testing, but the future working version must preserve and expose the full intraday hierarchy—including four sessions per futures day and four 90-minute cycles per session—without forcing the operator through a large repetitive form.

The durable requirement is now in `PROJECT_REQUIREMENTS.md`, with Milestone E design guidance in `CONTEXT_MATURITY.md`.

Preferred future direction: derive factual state automatically, focus the active layer, progressively disclose deeper hierarchy, use compact visual/nested views, and allow edit-by-exception. Completeness in the data model must not require simultaneous exposure of every intraday field.

Current E1 validation status:

- full automated suite: **348 passed**,
- guided smoke test: **fully PASS and committed/pushed**,
- future intraday QT depth remains a documented Milestone E requirement, not a blocker to E1 acceptance.
