# ICT Trading Cockpit — Current Project State

**Last handoff update:** 2026-10-10

This is the starting point for a new development chat or developer handoff. Git remains the source of truth for code; this file records the verified project checkpoint and the reasoning context needed to continue without reconstructing chat history.

## Repository state

- **Active branch:** `main` (E6 accepted and merged)
- **Main baseline:** `aaa931153f165b8ebb90c43126e00b6cd07beeeb` — Merge pull request #59, accepted E6 JSON capture/import v0. Assessment PR #58 merged as `0ca2acf6775622dfa5f755c5ed47a28ea197210a`; prior E5/E6 checkpoint was `59a9b984b398a10f54847315569b8179a37b38e6`.
- **Implementation checkpoint:** `130a50077bf18973aabb184cc9e588b57a62c71a` — Add immutable Forex Factory JSON captures and explicit provider coverage (E6). Branch starts from PR #58 assessment commit `2d9eed4c6acde448584a43fad923b1226de11ab1`; prior accepted feature is E5 `41f9d69c5b648873f6b95f2041e5daaeb2ea8508`.
- **Compatibility checkpoint:** `bd546d51d2e2c88610eec16e448f7eeeb1d98c8f` — normalize UTC `Z` coverage bounds for supported Python 3.10 in validation/comparison; exercise both UTC representations through coverage serialization/restoration.
- **Operator acceptance checkpoint:** `df4cac894f7e697bf65793c5f031265af5bdd9d4` — Record E6 operator smoke-test results; all nine checks PASS on 2026-10-10.
- **Last completed slice:** E6 — local Forex Factory JSON capture/import v0; operator accepted and merged
- **Current task:** E7 — inspect and scope generic model/playbook context predicates before implementation.
- **Schema:** v37
- **Trade Plan revision:** Alpha 0.7
- **Verified full test result:** **425 passed in 171.70s on Python 3.10.22** and **425 passed in 157.09s on Python 3.12.14**, both clean exits on 2026-10-11 UTC, PySide6 6.8.3 / pytest 9.1.1 / offscreen. Focused E6: **24 passed in 1.15s** on Python 3.12.14. Previous implementation validation: 424 passed in 150.46s on Python 3.12.14; focused E3/E4/E5/E6 76 passed in 2.32s; smoke-document round-trip 4 passed. Last accepted E5 result: 401 passed in 136.01s.
- **Operator automated-test report:** **425 passed** after the compatibility correction; runtime and Python version were not supplied. This supersedes the earlier **1 failed / 423 passed in 252.09s** report at `test_coverage_requires_both_window_and_selector_scope` parsing a UTC `Z` literal. The same test-setup and production coverage-parser failures were reproduced on Python 3.10.22 and corrected in the compatibility checkpoint above.
- **Fresh baseline verification:** `main` at `59a9b984b398a10f54847315569b8179a37b38e6`; **401 passed in 136.84s**, clean exit, Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1 / offscreen. Assessment changes in PR #58 were documentation only; the feature branch now contains E6 implementation. Fresh pre-code verification also passed 401 tests in 136.89s.
- **Manual acceptance:** E1 fully PASS. E3 required no new UI smoke pass. E4 focused operator smoke is **PASS**, per operator report of completed manual testing and acceptance on 2026-10-10. E5 focused operator acceptance is **PASS**, with all eight checklist checks pushed in `2e76e9dedf0dc85e059bdf94181d62a5fbc12617` on 2026-10-10.

- **E6 manual acceptance:** all nine focused operator checks **PASS**, verified in the pushed acceptance checkpoint above, including the real-export/normal-application check. Developer validation remains separate from operator acceptance.

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

The current major frontier is **Milestone E — context maturity: QT/AMDX, external events, schedules, and distortions**. E1 through E6 are merged and accepted. E4 exposes stored context to the operator. E5 provides explicit snapshotted context-policy evaluation and configured entry effects; real policy adoption remains deferred. E6 supplies local calendar captures and honest provider claims. E7 generic model/playbook context predicates are the next planned slice; source uncertainty remains authoritative.

Milestone D continues only for demonstrated operator friction. Film Night, gallery polish, broad TradingView integration, hardware controls, and broker execution remain downstream.

## Previous completed slice

**E3 — historical context snapshots**, merged through PR #55:

- run-start event/schedule snapshot persisted in schema v35,
- selected historical futures-day queries for Replay/Study,
- Available-empty / Not Configured / Unavailable remain distinct,
- restore reads stored context rather than re-querying a provider,
- provider revisions do not silently rewrite historical runs,
- full automated acceptance: **364 passed**, clean exit,
- test-session Qt cleanup stops test-owned timers and disposes windows before draining events.

## Previous completed slice

**E4 — compact operator context surfaces**, merged through PR #56 after operator acceptance on 2026-10-10.

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
- operator reported manual testing complete and acceptance granted on **2026-10-10**; the E4 checklist in `docs/SMOKE_TEST.md` is recorded as **PASS**.

## Last completed slice

**E5 — declarative Trade Plan context rules v0**, merged through PR #57 after all eight operator checks passed on 2026-10-10.

Implemented behavior:

- immutable plan-owned rule definitions with IDs, rationale, explicit environments, conjunctive conditions, matched effect, and unknown effect,
- NY weekday/strict-after clock predicates and normalized event-presence selectors (category/type/impact/affected market) over futures-day or calendar-week windows,
- Matched / Not Matched / Unknown / Not Applicable results; informational, warning, block-entry, and stand-down-day effects are explicit,
- positive recorded event facts can establish presence; a negative event result requires full requested-window coverage,
- unavailable calendar, missing time/coverage/selectors, tentative/unknown status, and incomplete NFP-week coverage remain unknown,
- cancelled/postponed events do not satisfy presence; released events remain relevant to day/week rules,
- schema **v36** stores each run's context rules; v35 runs migrate to empty rules without invented policy,
- candidate entry authorization adds configured context blockers independently of manual gate clearance; warnings never grant permission,
- compact TDA/Watch/Review effects and expandable rule rationale, applicability, reasons, and event IDs,
- pure evaluation: no provider queries, wall-clock fallback, snapshot rewriting, or evaluation-time mutation,
- disposable fixtures: `python tools/context_policy_demo.py`, with frozen time and unpublished fixture-only policy,
- published **Alpha 0.7 remains unchanged** with no declarative context rules; existing manual gates remain in force.

Validation:

- full automated suite: **401 passed in 136.01s**, clean exit on 2026-10-10 (Python 3.12 / PySide6 6.8.3 / offscreen),
- focused E3/E4/E5 regressions: **45 passed**; smoke-document round-trip: **4 passed**,
- developer offscreen fixture inspection confirmed clock boundaries, event availability, coverage unknowns, and configured entry blocking with cleared manual gates; visually inspected Watch and expanded Review at 1100×850,
- operator acceptance is **PASS** on 2026-10-10; all eight E5 checks in `docs/SMOKE_TEST.md` are PASS, including the reported local full suite and normal Alpha 0.7 restore/workflow checks.

## Current task

**E7 — generic model/playbook context predicates** is the current design/implementation frontier. E6 JSON capture/import v0 is accepted and merged through [PR #59](https://github.com/mehoyminoi/ict-trading-cockpit/pull/59), after assessment PR #58 merged and PR #59 was retargeted to main. All nine E6 smoke checks are PASS in `df4cac894f7e697bf65793c5f031265af5bdd9d4`. The merged main tree exactly matches the accepted E6 feature tree; the latest verified 425-test results remain applicable without a code change at merge.

The operator accepted proceeding with the recommended free import direction. No paid subscription is assumed; Trading Economics at approximately $200/month remains excluded. FMP is an assessed future paid candidate, not a selected dependency. See `E6_PROVIDER_ASSESSMENT.md` for the source comparison and XML findings.

Implemented:

- provider query result separates requested bounds from explicit completeness, coverage bounds, selector scope, and source basis,
- negative rule results require complete coverage for the entire rule window and selector scope; legacy tuple responses and missing legacy coverage cannot certify absence,
- explicit timing precision defaults Unknown, separate from native clock values and status,
- schema v37 adds immutable source-capture storage with update/delete protection; migration preserves existing snapshot JSON,
- local weekly JSON preview/import requires an operator-declared Sunday UTC week and validates every record atomically; malformed/empty/wrong-week files are rejected,
- saved capture preserves original JSON/digest, file/import provenance, native fields, declared week, capture-local row IDs, adapter/mapping revisions, and limitations,
- **Trade Plan > Process > Calendar captures** exposes preview, save, and explicit source selection for future runs,
- missing requested weeks are Unavailable with attempted capture provenance; uncertain source-week rows are retained rather than filtered by unverified clocks,
- compact context and details expose completeness/timing uncertainty; Watch does not present uncertain rows as exact upcoming times or confirmed day schedule exceptions,
- later imports and source selection leave started/restored run snapshots unchanged; selection resets to Not Configured after restart while saved captures remain,
- disposable manual sandbox: `python tools/context_import_demo.py`; printed `--data-dir` command reuses its separate database for restart checks.

Validation: latest full suites **425 passed in 171.70s on Python 3.10.22** and **425 passed in 157.09s on Python 3.12.14**, both clean exits; focused E6 **24 passed in 1.15s** on Python 3.12.14. The operator's earlier 1 failed / 423 passed report exposed UTC `Z` parsing incompatible with Python 3.10; test setup and production coverage validation/comparison now use compatible offsets while preserving serialized bounds. The subsequent operator rerun reported **425 passed**. Before this correction, focused E3/E4/E5/E6 passed 76 tests and smoke-document round-trip passed 4 tests. Developer real-format/offscreen integration and sandbox startup/clean exit were exercised. The public JSON representation's 83 records imported and restored in a separate database; direct HTTP retrieval returned 403, so automatic network acquisition is not claimed. Main-window import/Watch/Review were visually inspected at its current minimum size of 1120×876; removing the new import tab leaves the same pre-existing minimum height. All nine operator E6 checks are **PASS** in `SMOKE_TEST.md`, pushed in the acceptance checkpoint above.

Next action: scope a small E7 slice for explicit playbook targeting, event presence/absence and calendar-day selection, because the snapshot, rule, and source-capture contracts are now accepted. Friday Asian Range's no-Monday-high-impact-news condition is an accepted validation use case, but preceding versus following Monday is not specified; any fixture must declare its week relationship and must not publish that assumption as a trading rule. Preserve explainable Unknown outcomes: an incomplete Forex Factory capture cannot certify event absence. E6 v0 provides captured context with honest limitations, not provider-certified timing, historical as-of reconstruction, or automatic Alpha 0.7 exclusions.

## Explicitly deferred / open

- Forex Factory local JSON import is implemented; network acquisition and XML/ICS/CSV adapters remain deferred,
- no within-run snapshot refresh/version history,
- no published automatic Alpha 0.7 context policy: the example allows paper trading on live/eval/funded no-trade days, and run environment is not account type; actual adoption needs explicit account applicability and a new plan revision,
- exact normalized event types, full-week calendar coverage, and any event duration/buffer must be explicitly configured rather than inferred from titles or provider folder colors,
- rule results are derived on demand; no decision-time policy-result audit log is persisted in E5,
- no no-code rule editor, automatic run conclusion/stand-down transition, exit/flatten restriction, order submission, readiness score, or automatic competency evidence,
- no full intraday session × 90-minute interpretation grid,
- E6/E7 narrative numbering is reconciled to the accepted sequence: provider integration before model predicates; Review/evidence provenance remains cross-cutting. Provider limitations and implemented v0 scope remain explicit in `E6_PROVIDER_ASSESSMENT.md`.

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
