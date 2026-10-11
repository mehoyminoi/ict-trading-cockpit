# ICT Trading Cockpit — Current Project State

**Last handoff update:** 2026-10-11

This is the starting point for a new development chat or developer handoff. Git remains the source of truth for code; this file records the verified project checkpoint and the reasoning context needed to continue without reconstructing chat history.

## Repository state

- **Active branch:** `feature/intraday-qt-design-v0` (design-only; operator review pending)
- **Main branch head before the E7 acceptance checkpoint:** `ce48e28ca2cb01e8b2c3e521795ebc20eefdbd25` — documentation handoff updates only; source/tests remain accepted E6.
- **Main handoff baseline:** `83d82323ca936dedf045027760d81a1cd7de76b1` — Checkpoint merged E7 and remaining intraday QT frontier.
- **Intraday QT design checkpoint:** `docs/INTRADAY_QT_DESIGN.md` inventories the flat legacy interpretation, mutable live reference time and interval-naming ambiguity; proposes explicit session/cycle identity, independent expectation/observation revisions, fixed comparison pairing and a compact selected-interval editor. Proposed only: production source/tests, schema v37 and Alpha 0.7 are unchanged.
- **Design checkpoint verification:** twelve synthetic browser interaction assertions passed; light/dark desktop and 320px layouts inspected, including expanded-history overflow check. The older Qt browser required resolving the specified theme palette in the harness; native host theme switching is unverified. Smoke-document checks **4 passed in 0.50s**; all 244 checklist identities/statuses unchanged. Documentation-only checkpoint; the accepted 456-pass full suite was not repeated, and these preview checks do not establish production persistence or operator acceptance.
- **Main implementation baseline:** `f57794cff6f128830655b458e999fd8f72038280` — Merge PR #60, accepted E7 model/playbook context predicates. Its tree `5d153069e7be045e7c80a9930f946b7c1d199518` exactly matches reviewed head `3ac8000b60929c60cf37eaefc634c66788229a81` and the fresh full-suite checkout.
- **Accepted E6 source/test baseline:** `42e3b346245de17e61a062e29fa6cd082d2527bf` — Checkpoint merged E6 and explicit E7 context-predicate frontier. Accepted E6 PR #59 merged as `aaa931153f165b8ebb90c43126e00b6cd07beeeb`, after assessment PR #58 merged as `0ca2acf6775622dfa5f755c5ed47a28ea197210a`.
- **Implementation checkpoint:** `130a50077bf18973aabb184cc9e588b57a62c71a` — Add immutable Forex Factory JSON captures and explicit provider coverage (E6). Branch starts from PR #58 assessment commit `2d9eed4c6acde448584a43fad923b1226de11ab1`; prior accepted feature is E5 `41f9d69c5b648873f6b95f2041e5daaeb2ea8508`.
- **Compatibility checkpoint:** `bd546d51d2e2c88610eec16e448f7eeeb1d98c8f` — normalize UTC `Z` coverage bounds for supported Python 3.10 in validation/comparison; exercise both UTC representations through coverage serialization/restoration.
- **E7 implementation checkpoint:** `70f9f6c1bb9ca8aafeec4ddedee80a0930fb355f` — Add playbook-scoped context predicates with explicit calendar windows (E7); reviewed in [PR #60](https://github.com/mehoyminoi/ict-trading-cockpit/pull/60).
- **E7 acceptance-fixture correction:** `8892f1a16624a7a034a621801469cf409953817d` — Seed the required synthetic TDA watch point and normal day-specific identity so Watch renders Custom fixture; add actual card/control and save/restore/reopen regression coverage. Operator check 236 retest is PASS in the results checkpoint below.
- **E7 operator-support checkpoint:** `53fd507849cd80b65ceeaea56c0287270c9b2c1c` — Expose the sandbox database path, Copy restart command and the reason Restore is disabled. Add a [practical operator guide](E7_OPERATOR_GUIDE.md) for the same checks 236–244; existing smoke results and acceptance criteria are unchanged.
- **E7 operator-results checkpoint:** `8f1ad50c6a62c37c1b331ad0ca84a7542b33aa87` — Pushed on 2026-10-11: checks 236–241 and 244 PASS, 242 QUESTION, 243 NOT TESTED. This commit changes only `SMOKE_TEST.md`; its source/tests are identical to parent `25ac4e5dd062fdab2539abf0c5d76317ddf5b322`. This historical tally was superseded by the controlled retests below; E7 is now operator accepted and merged through PR #60.
- **E7 controlled compatibility-support checkpoint:** `bfd398946277869dcaeb07e6bcdf9a9dad059d3c` — add a disposable old-code database writer and current normal-window opener, preserve the E6 backup/manifest, and verify cross-version capture/run restoration without reconstructing missing operator history. Operator check 243 subsequently passed the controlled retest below.
- **E7 persistence-retest checkpoint:** `19ecc042b1562e128799a0cc0b7c2bc1fa6edd8b` — operator changed 242 to PASS after controlled identity/source/rule restoration before and after restart. The current tally supersedes the earlier results tally.
- **E7 compatibility-retest evidence checkpoint:** `9454414b7da5be9ad131d6683fd95b42f7aefc62` — operator recorded successful controlled E6→E7 restoration, navigation, restart and capture-selection checks on 2026-10-11. This acceptance checkpoint changes the stale 243 checkbox to PASS to match that evidence; all other checkbox identities/statuses are preserved.
- **Operator acceptance checkpoint:** `df4cac894f7e697bf65793c5f031265af5bdd9d4` — Record E6 operator smoke-test results; all nine checks PASS on 2026-10-10.
- **Last completed slice:** E7 — generic model/playbook context predicates v0; all nine operator checks PASS and merged through PR #60.
- **Current slice/task:** review the concrete intraday QT design and interaction preview. No production implementation or migration is approved by this design checkpoint. E7 remains the last accepted and merged slice.
- **Schema:** v37
- **Trade Plan revision:** Alpha 0.7
- **Latest operator full-suite report:** **454 collected, 454 passed**, Python **3.10.12**, pytest **9.1.1**, pluggy **1.6.0**, on 2026-10-11; archived with the pushed results checkpoint above. Elapsed time and PySide6 version were not supplied.
- **Latest developer review validation:** **456 passed in 273.30s** on Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen, clean exit and no warnings on 2026-10-11. The reviewed PR head and merged main have the same tree. Review found no blocking issues; GitHub had no review submissions, unresolved review threads, workflow runs or commit statuses. The handoff-only changes after merge do not change source/tests/schema/plan.
- **Post-merge handoff validation:** **4 document tests passed in 0.04s** with the normal Qt conftest. All 244 checklist identities/statuses remain unchanged, including nine E7 PASS results. This checkpoint changes only handoff/acceptance documentation.
- **Prior developer compatibility-support validation:** **456 passed in 338.01s on Python 3.10.22** and **456 passed in 305.11s on Python 3.12.14**, clean exits on 2026-10-11, PySide6 6.8.3 / pytest 9.1.1 / offscreen. The 3.12 full run reported one archive-extraction deprecation warning; an explicit supported extraction filter removed it. Final focused compatibility/document tests after that cleanup: **6 passed in 3.08s on 3.10** and **6 passed in 2.64s on 3.12**, without warnings. The full suite was not repeated for that extraction-policy-only cleanup. Production source, schema and published plan are unchanged by this support slice.
- **Acceptance-checkpoint document validation:** **4 passed in 0.02s** on Python 3.12.14, using `python -m pytest --noconftest tests/test_smoke_test_document.py -q` (pure Markdown tests; the shared Qt conftest dependency was unavailable at that checkpoint). All 244 checklist identities were compared with `9454414`: only 243 changed from NOT TESTED to PASS, and all nine E7 items are PASS. The merge of main’s documentation updates and this checkpoint change no source/tests/schema/plan; full-suite results above were not rerun.
- **Prior developer full test result:** **453 passed in 180.58s on Python 3.10.22** and **453 passed in 163.34s on Python 3.12.14**, both clean exits on 2026-10-11 UTC, PySide6 6.8.3 / pytest 9.1.1 / offscreen, at the Custom fixture correction checkpoint. E7 added **28 tests** at that checkpoint. Prior focused E5/E6/E7: **79 passed in 1.71s**; smoke-document tests: **4 passed in 0.02s**. Prior accepted E6 suites: 425 passed in 171.70s on Python 3.10.22 and 425 passed in 157.09s on Python 3.12.14.
- **Operator-support verification:** focused E7 plus smoke-document tests **33 passed in 1.35s on Python 3.10.22** and **33 passed in 1.32s on Python 3.12.14**, clean exits. One additional regression verifies copied command/path quoting, no saved fixture in a different database, and original run ID/Review/context block after reopening the saved database. The full suite has not been rerun for this demo/documentation-only support change.
- **Prior accepted E6 operator automated-test report:** **425 passed** after the compatibility correction; runtime and Python version were not supplied. This supersedes the earlier 1 failed / 423 passed UTC `Z` parsing report. The later E7 operator result is recorded separately above.
- **Baseline verification:** merged E6 main tree exactly matched accepted feature checkpoint `9ae4d78920609c27ed0df4712398e3835fc3a3cd`. Main checkpoint `42e3b346` changed documentation only; its source/tests retain the accepted 425-test E6 implementation. E7 branches directly from that main checkpoint.
- **Manual acceptance:** E1 fully PASS. E3 required no new UI smoke pass. E4 focused operator smoke is **PASS**, per operator report of completed manual testing and acceptance on 2026-10-10. E5 focused operator acceptance is **PASS**, with all eight checklist checks pushed in `2e76e9dedf0dc85e059bdf94181d62a5fbc12617` on 2026-10-10.

- **E6 manual acceptance:** all nine focused operator checks **PASS**, verified in the pushed acceptance checkpoint above, including the real-export/normal-application check. Developer validation remains separate from operator acceptance.
- **Current E7 checklist:** **9 PASS**, after reconciling the 243 checkbox with the successful retest evidence in pushed `9454414b7da5be9ad131d6683fd95b42f7aefc62`. The missing Custom fixture has passed operator retest. Developer checks remain separate from operator acceptance.
- **Check 242 — PASS:** controlled retest in `/tmp/ict-e7-242-retest/demo.db`, saved run `edca6b3f-e64d-4f8a-a9fd-570b633dfa80`. Operator confirmed the same ID, Review, `fixture-friday@fixture-v0`, Not Matched / Block New Entry and event `fixture-monday` after restoring from Legacy rules and again after restart. The pushed PASS closes the earlier identity evidence gap; repeated bare launches had used different sandboxes.
- **Check 243 — PASS:** controlled E6→E7 compatibility in `/tmp/ict-e6-e7-compatibility`, using accepted E6 writer `42e3b346`. Original run `16b5fe86-e5d3-4f4a-b9da-432afe1be23f` and capture `ee87fcdd-1423-4f91-bcdc-9b69dbe904f2` matched in Watch, TDA, Review and after restart. Pending manual gates kept Silver Bullet Model Blocked; no declarative rules appeared, and completeness/precision/status stayed unknown. Both captures were inspectable; selecting the revised capture for new runs preserved the original run snapshot and native previous `1%`. This supersedes the earlier unavailable-data NOT TESTED gap with controlled old-version evidence, not recovered operator history.
- **Unconfirmed support report:** Copy restart command or its use was reported to make the tool stop responding; the exact step and reproduction have not yet been supplied. Use an explicit printed restart command while clarifying this separately from saved-run restoration.

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

The current major frontier is **Milestone E — context maturity: QT/AMDX, external events, schedules, and distortions**. E1 through E7 are merged and accepted. E4 exposes stored context to the operator. E5 provides explicit snapshotted context-policy evaluation and configured entry effects; real policy adoption remains deferred. E6 supplies local calendar captures and honest provider claims. E7 generic model/playbook context predicates v0 are accepted and merged, with all nine operator checks PASS; source uncertainty remains authoritative. Milestone E remains the frontier because full intraday session/90-minute interpretation and provenance still need a compact interaction design. Acceptance of E7 does not declare every mature context requirement complete. Adopting a real model/news policy still requires explicit Trade Plan semantics and a new published revision.

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

## Previous completed slice

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

## Last completed slice — E7

**E7 — generic model/playbook context predicates v0** is implemented on `feature/context-maturity-e7-v0`, reviewed in [PR #60](https://github.com/mehoyminoi/ict-trading-cockpit/pull/60). All nine checks are PASS, including controlled earlier-E6 compatibility. PR #60 merged on 2026-10-11 as `f57794cff6f128830655b458e999fd8f72038280`. E7 is the last accepted and merged feature; E6 assessment/implementation PRs #58/#59 remain closed and merged.

Use `E7_OPERATOR_GUIDE.md` for concrete actions/observations and retain the pushed results. The controlled 242 identity/source/rule restoration retest is PASS in `19ecc04`. For 243, `tools/e6_compatibility_demo.py --data-dir /tmp/ict-e6-e7-compatibility` creates a controlled synthetic database using accepted E6 source at `42e3b346` in an isolated subprocess, then opens it in the normal current application. The original E6 database backup and provenance manifest are retained. First launch requires an empty directory; restart reuses the same working database without reseeding. Operator observations are PASS in `9454414`; the run and captures were genuinely written by accepted E6 code, rather than newly imported by E7. The predicate demo displays its database path and explains disabled Restore; the compatibility tool uses normal automatic application restoration. Operator support addresses observed testing friction without changing the roadmap, trading policy, or required acceptance criteria.

Implemented:

- plan-owned rules can target explicit known playbook IDs; an empty scope preserves run-wide legacy behavior,
- candidate authorization uses stored Playbook source identity, with no effect leakage to other models or Custom setups,
- Event Absent inverts known presence/absence only; Unknown remains Unknown,
- selected NY calendar weekdays and an explicit relative calendar-week offset resolve inspectable windows, including DST civil-day boundaries,
- negative conclusions require complete source coverage of every selected window and selector scope; Forex Factory captures never certify absence,
- matched, not-matched and Unknown effects are separately configured; old not-matched behavior defaults to no effect,
- Stand Down Day remains run-wide and is invalid for playbook-scoped rules,
- shared TDA/Watch/Review details show scoped candidate revision, dates, outcome/effect and event IDs; rendering is read-only,
- persisted rule/candidate/source snapshots survive database reopen and current-definition changes without a migration; schema v37 and Alpha 0.7 remain unchanged,
- a disposable acceptance sandbox supports explicit save/restore and restart: `python tools/context_predicate_demo.py --data-dir /tmp/ict-e7-acceptance`.
- check 236's missing Custom card was a sandbox defect: Watch requires a TDA watch point before rendering a Custom setup. The corrected demo seeds one synthetic IF/THEN point and uses the normal `day-specific` source identity. A regression exercises the actual Watch card and point controls, scope isolation, save/restore and database reopen. Operator retest is PASS; older saved fixtures retain their original state.

Validation after the Custom fixture correction: full suites **453 passed in 180.58s on Python 3.10.22** and **453 passed in 163.34s on Python 3.12.14**, both clean exits. Prior focused E5/E6/E7 **79 passed in 1.71s**; smoke-document tests **4 passed in 0.02s**. New tests cover scoped/custom isolation, selected-day completeness, prior/following weeks, 23/25-hour DST days, explicit outcome effects, legacy-field defaults and historical database reopen. The correction regression reproduced the missing card before the fix and now verifies its Watch controls and identity through save/restore/reopen; the displayed Custom card was also inspected offscreen after a TDA-to-Watch transition. Prior developer demo checks exercised all nine scenarios and environment exclusions, save/rebuild/restore and Review restart. The operator reports the local **454-pass** suite on Python 3.10.12. The controlled 242 and 243 retests complete all nine operator checks; the 243 checkbox is reconciled with the pushed retest note in this checkpoint. Earlier support verification remains the separate 33-test focused pass above. The controlled E6 compatibility tool adds two tests: an actual E6 writer → E7 normal-window restore/selection/TDA/Watch/Review/reopen regression (including old rule-field defaults), and refusal to overwrite existing files. The original E6 backup and manifest stay unchanged across current-application use. Watch and expanded Review were visually inspected offscreen at 1100×850. Latest full/focused developer results are recorded above; operator check 243 is PASS with the IDs and observations recorded above.

## Current task

Current action: operator review of `INTRADAY_QT_DESIGN.md` and its compact synthetic interaction preview. The design proposes independent session/cycle records, explicit Unknown versus Not Applicable, preserved expectation revisions and a saved comparison baseline. First-recorded expectation is a proposed Review default, not an accepted trading rule or score. No new production fields, migration, gates or competency evidence were added. After design review, the recommended first implementation is interval identity and versioned run persistence with a focused disposable editor; production UI consolidation follows verified legacy/restart behavior. This continues the accepted intraday-depth requirement without changing milestone order. Keep the ambiguous Copy restart report as an unconfirmed support issue; explicit restart commands were successfully exercised in checks 242 and 243. Before adopting a model/news rule in a new Trade Plan revision, settle the real Friday Asian Range Monday relationship, applicability and policy effects. The accepted example does not specify preceding versus following Monday; fixtures explicitly declare current-week or following-week offsets and do not publish either assumption. Real Forex Factory completeness, timing/status, normalized type/market applicability and historical as-of knowledge remain unverified. No readiness thresholds, source refresh, automatic model definition changes, competency evidence or order operations are introduced.

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
