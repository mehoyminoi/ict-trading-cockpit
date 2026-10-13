# ICT Trading Cockpit — Current Project State

**Last handoff update:** 2026-10-12

This is the starting point for a new development chat or developer handoff. Git remains the source of truth for code; this file records the verified project checkpoint and the reasoning context needed to continue without reconstructing chat history.

## Repository state

- **Active branch:** `feature/amdx-higher-context-v0`, [PR #67](https://github.com/mehoyminoi/ict-trading-cockpit/pull/67), based on merged main `6dd43c845940874000f46371965441dec262e77a`. Pure higher-cycle identity/read projection is implemented at `e90255dd2be05402234ee685d9e95562d47e8fda`; final validation/readiness is recorded below. Main retains accepted PRs #61–66 and all operator 245–260 reports. No native/storage binding, schema or Alpha 0.7 change accompanies this foundation.
- **Main branch head before the E7 acceptance checkpoint:** `ce48e28ca2cb01e8b2c3e521795ebc20eefdbd25` — documentation handoff updates only; source/tests remain accepted E6.
- **Main handoff baseline:** `83d82323ca936dedf045027760d81a1cd7de76b1` — Checkpoint merged E7 and remaining intraday QT frontier.
- **Intraday QT design checkpoint:** `docs/INTRADAY_QT_DESIGN.md` inventories the flat legacy interpretation, mutable live reference time and interval-naming ambiguity; proposes explicit session/cycle identity, independent expectation/observation revisions, fixed comparison pairing and a compact selected-interval editor. Proposed only: production source/tests, schema v37 and Alpha 0.7 are unchanged.
- **Provisional design feedback:** embedded preview failed for the operator; PNG feedback suggests excessive interaction and memory burden, especially the separate Record action. Test automatic draft persistence next; independent scopes and first-expectation baseline remain tentative. No layout/design acceptance is inferred. See `INTRADAY_QT_DESIGN.md` for the precise feedback and hands-on evaluation gap.
- **Whole-stack orientation clarification:** quiet higher-order AMDX context stays visible across the core loop, with nearby selected-level detail/editing and shared actions for future shortcuts/macro-pad use. The collapsed-higher-stack and raw-day-history layout is superseded as a target; deeper historical exploration placement remains open. Updated requirements/context design preserve provenance without introducing quarter-correctness grading. No production behavior changed.
- **Whole-stack trial:** operator extended foundational QT/AMDX visibility into Study/Lab and authorized the next hands-on design trial. The synthetic browser prototype now has a continuously visible eight-level overview, one adjacent inspector, automatic draft capture, explicit browser-storage feedback, shared keyboard actions and no raw day-history list. **17 interaction assertions**, reopen checks and light/dark/320px layout inspection passed. This is proposed interaction only; production persistence, schema, plan and process completion are unchanged. Embedded renderer behavior and operator usability acceptance remain open.
- **Current zoom-out direction:** component layout iteration is parked. Foundational AMDX should support context-specific presentations: quiet Watch orientation/permitted capture, spacious Study/Lab investigation, analytical TDA and contextual Market Review. Immediate review is the broader Cockpit functional map plus shared data/action contracts; final renderers can follow later. Automatic phase recording is now accepted; In-place Watch updates are also accepted; comparison baseline remains the open contract. No architecture/UI implementation approval is inferred from a preview.
- **Whole-cockpit walkthrough checkpoint:** `COCKPIT_FUNCTIONAL_WALKTHROUGH.md` verifies actual navigation and current source, separates existing substrate from proposed presentations, walks through market operation and targeted Study, and offers concrete recommendations for the three open contracts. Current review is the two journeys and shared actions/ownership before architecture implementation; no new production behavior or rendering was added.
- **Walkthrough operator review:** reviewed on 2026-10-11; ready to continue to the concrete cases in `QT_ACTION_CONTRACT_REVIEW.md`. Mature overview/detail should coexist closely rather than be separated by Focus/Deck tabs. Proposed Study-first startup should offer a dismissible competency/next-study suggestion to reduce tired-operator planning burden; the ratio/destination/order and active-run handling are not enforced policy. No startup/UI changes are implemented. Contract decisions are recorded separately from walkthrough review; see the subsequent accepted-contract entry below.
- **Accepted contract 1:** on 2026-10-11 the operator accepted immediate automatic interpretation history on a deliberate phase choice, without a separate Save/Record click or station completion. Revisions preserve earlier values; note drafts and completion stay separate. Watch in-place updates were subsequently accepted; comparison baseline is the next review. This records a behavior decision, not implemented production functionality.
- **Accepted contract 2:** on 2026-10-11 the operator accepted small working-AMDX changes directly in Watch, with active input as 90-minute cycles pass. Shared actions append revisions without leaving Watch. Broader thesis changes retain easy full-stack/TDA review access. Passive clock changes do not infer phases or retarget active edits; no cycle-completion gate is added. Comparison baseline remains open. This is accepted design, not an implemented UI path.
- **Four-quarter profile correction:** operator clarification on 2026-10-11 supersedes independent sibling phases. AMDX and XAMD are coupled quartet orders; Q3=D implies AMDX roles with unresolved X subtype where needed. Explicit technician anchors, rule-implied context and evidence-based classification remain distinct. Preserve competing/conflicting interpretations and highlight versioned plan rules for empirical Study. `AMDX_CYCLE_RULE_CONTRACT.md` records the corrected domain unit; 12 structural worked-case assertions passed. Objective classification criteria and cycle-level Review baseline remain open. No sensor, source/schema or Alpha 0.7 change was introduced.
- **Rule-framework direction:** operator reviewed the cycle/rule contract on 2026-10-11. `AMDX_RULE_DEFINITION_FRAMEWORK.md` defines editable candidate/published rule revisions, explicit input/output targets, local-behavior versus quartet-role distinction, priority/weighting semantics and empirical comparison. News correlations are first-class TDA/Study research/anticipation context with source/as-of unknowns preserved. Enough is known for the narrow structural/definition/provenance foundation; unfinished classifiers and the Review default need not block generic storage/action interfaces. Coverflow scrolling/hotkeys are a parked, revisable UX idea. No source implementation or published rule adoption occurred in this documentation checkpoint.
- **AMDX foundation implementation checkpoint:** `215b9a75863fc625e863362479e1c4558e74c1ee` — Implement coupled AMDX cycle history and versioned priority criteria foundation. Operator authorized proceeding on 2026-10-11. Adds isolated `analysis/amdx.py` and `analysis/amdx_rules.py`, 39 focused tests and the read-only `tools/amdx_foundation_demo.py`. Day/session temporal identities reuse accepted NY time semantics; manual/derived roles, unresolved X, conflicts, channels/branches/runs and pinned targets remain distinct. Versioned snapshot reload validates the retained action/definition/input basis. The declared Cycle Profile Priority resolver can prefer London Q2=M over lower-priority Asia Q1=X while preserving both traces; unknown competing criteria and equal-priority contradictions remain unresolved/conflicting. Application persistence/rendering and actual classifiers are downstream. Schema v37, Alpha 0.7 and all existing 244 smoke identities/statuses remain unchanged.
- **AMDX persistence implementation checkpoint:** `550fc2358426c565b854d18fa496034553d75dfe` — Persist immutable run-owned AMDX revisions and criteria evaluations transactionally. Operator authorized the next slice on 2026-10-11. Schema v38 adds stable cycle/definition registries and append-only claim/evaluation tables; normal `TradingSessionRunRepository.amdx` actions own immediate transactions and explicit scoped-head checks. Identity retries are idempotent, changed content and stale writes are rejected, SQL UPDATE/DELETE/REPLACE is protected, and cycle/definition/result writes roll back together. Optional explicit claim bases never select a Review default. Old run/capture rows and QT meaning remain unchanged; actual E6 normal-window restoration at v38 is verified with empty AMDX history, retaining the original v37 backup/manifest. The disposable persistence demo verifies durable revision/evaluation reopen. Production Watch/TDA entry is NEXT; Alpha 0.7 and all 244 smoke identities/statuses remain unchanged. Migration is forward-only; an old v37 app requires an unmigrated copy.
- **AMDX entry implementation checkpoint:** `90afd511d02fec83595ab03179b0212641f4589b` — Connect durable AMDX entry and shared quartet orientation to Watch and TDA. Operator authorized proceeding from persistence on 2026-10-11. The normal MainWindow wires the v38 repository to one fixed Working AMDX panel in TDA/Watch/Review. Four direct roles plus subtype/uncertainty/clear actions commit immediately; daily/session profiles and higher legacy context remain nearby. Default current input follows time; inspected targets, keyboard selection and open gestures pin identity/reference. Failure/stale/read paths preserve committed meaning and require explicit retry. Earlier intraday flat inputs are read-only in the application-backed path; higher fields keep provenance. Runtime content scrolls under fixed orientation; wheel scrolls content, while Back/Forward/station navigation remain. `tools/amdx_entry_demo.py` opens/restores a separate retained synthetic normal-window fixture with explicit reference advancement. Schema v38 and Alpha 0.7 are unchanged by this UI slice. Six new smoke checks 245–250 are NOT TESTED; all previous 244 identities/results are preserved. Native usability/final layout acceptance is pending.
- **AMDX entry boundary review checkpoint:** `6cf65d2f514950089593b018d7e115a62f272834` — Keep AMDX entry targets stable across clock-boundary retries. Continuation review reproduced delayed current-quarter resumption after success/cancellation, stale-gesture reference rewind and an unpinned failed target that could move on the next clock refresh. Successful or cancelled unpinned gestures now immediately resume the latest current scope; their committed claim still retains the original gesture target/reference. Failed choices visibly pin their attempted target for deliberate retry or Follow current, and stale reloads update that scope's committed head while keeping the latest clock reference. Existing explicit inspection pins remain intact. Adds five regression cases and strengthens the original mouse-boundary check. No layout redesign, schema/plan change, automatic retry or operator acceptance is introduced.
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
- **Last completed functional slice:** durable one-entry working/observed AMDX stack and run-owned Review-date correction, merged through PRs #61–66. Complete verification: **744 PASS across 70 isolated modules** at `e12a2d4`, focused 77 PASS, and operator 245–260 PASS for covered cases. Main is schema v41 / Alpha 0.7; no new application suite is claimed for tree-identical merges.
- **Current slice/task:** pure higher-cycle resolver and scoped read projection implemented in `analysis/amdx_context.py`. It reuses existing New York calendar/futures positions, retains full week bounds and stable cross-month parent identity, leaves distortion/pre-first-Monday without invented anchors, preserves intraday IDs and carries exact legacy values separately. Read projection retains only requested run/channel/branch/cycle heads. `AMDX_HIGHER_CONTEXT_GUIDE.md` gives boundary examples. Storage/native binding and Study-owned selection remain next/separate contracts.
- **Working-quartet action review checkpoint — 2026-10-11:** readiness to continue authorized concrete contract refinement. `AMDX_WORKING_QUARTET_ACTION_REVIEW.md` provides ten before/action/after cases, structural choice limits, compatible/retired-anchor policy, X subtype reset/retention, selected-quarter uncertainty/clear, separate quartet Not Applicable judgment, atomic history/replay and stale/gesture requirements. The detailed policy is a developer recommendation for review, not accepted or implemented. Repeated identical explicit choices currently append; the older accepted contract declares a no-op, which the new command should cover. Earlier shared-action documentation is updated to distinguish implemented v38 entry from unimplemented notes/Review/replacement behavior. Structural table checks verified all 16 position/role pairs against the existing engine (8 resolved valid, 8 conflicting invalid). Four pure smoke-document test functions pass by direct invocation; all 250 checklist records remain byte-identical, including six AMDX PASS results. Changed Markdown links/tables/fences and git diff --check are verified. Source/tests/tools, schema v38 and Alpha 0.7 are unchanged; prior 546-pass application result is retained, not rerun for this document checkpoint. PR #61 remains ready for review and unmerged.
- **Schema:** v41 on the active native observed-entry follow-up, unchanged from PR #65; PR #64 retains v40, #62/#63 retain v39, #61 retains v38 and accepted merged main remains v37. Migration is forward-only; older v40 bootstrap rejects v41. Old rows and v1/v2 replay/exports remain unchanged; only new observed-policy claims use v3.
- **Trade Plan revision:** Alpha 0.7
- **Review date correction developer validation:** source `e12a2d4c4d4767f32dd13c3ea795ffab18531f78`; focused **77 passed in 784.90s**, and full **744 passed in 328.84s** across all 70 isolated module runs with clean exits/no warnings. All collected test counts matched JUnit reports, with no failures/errors/skips; this is the whole suite under module isolation, not one combined process. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. Python 3.10 syntax only; separate 3.10 execution not claimed. Restored native mismatched-day/rollover/restart/launch guard cases pass. All test processes are closed. Check 260 is operator PASS on 2026-10-12; previous 259 records preserved.
- **Review date correction operator acceptance — 2026-10-12:** check **260 PASS**, following guided date/rollover/restart/launch-guard reports. Operator guided report, 2026-10-12 (America/Denver): upper Trading Day advanced to October 10 while Observed AMDX remained October 9; NYAM 90m Q3=M was entered and the profile was XAMD. After window-X close and same-directory reopen, the date remained October 9; selecting NYAM restored XAMD and Q3 entered without another phase choice. After Conclude Trading Run, Start Another Trading Run created no second run and displayed: "Run not started - selected reference belongs to Trading Day 2026-10-13. Complete the current Trading Day, then choose Start New Trading Day". The October 13 request is the live reference after restart, not a change to the saved Review date. The heading-tooltip inspection was not separately reported; no operator hover acceptance is inferred. This documentation-only acceptance retains source `e12a2d4` and its completed 744-pass evidence; no application test rerun, merge, schema or plan change.
- **Review date correction source:** `e12a2d4c4d4767f32dd13c3ea795ffab18531f78` — Anchor AMDX Review to preserved run date and reject cross-date launches. No schema/plan/archive-policy change. Valid saved run-start reference wins over a mislabeled container; absent reference uses a documented legacy Day fallback, malformed reference disables capture. Different-date/unknown-date additional launches reject before process reset and point to the existing new-day path. Focused native/domain/working/observed/entry group **77 passed in 784.90s**, including **24 new cases** (15 pure date, 9 native). Full verification completed: **744 passed across all 70 isolated module runs in 328.84s (5m29s)**, clean exits/no warnings. Each module used a fresh Qt process, with its JUnit count checked against all collected node IDs; no combined single-process full run is claimed. Check 260 is operator PASS on 2026-10-12; all previous 259 records are preserved.
- **AMDX stack review — 2026-10-12:** `AMDX_STACK_REVIEW.md` records verified PR heads/bases/tested-source equivalence, five passing fresh CLI demonstrations and one integration-blocking source-level reproduction: a newer run with an October 9 reference can get October 8 observed targets from its containing Trading Day label. No source change or merge is made. #63–65 are now ready; all #61–66 remain unmerged. Existing 720-pass and operator 245–259 results remain valid for covered cases; no new native/full run is claimed because Qt/pytest are unavailable in this environment.
- **Native Review operator acceptance — 2026-10-12:** “All points passed” accepts checks 255–259 following check-258 clarification and fresh-sandbox restart guidance. No per-check log, fixture/run ID, local runtime or elapsed time was supplied. Original premature-close cause is unconfirmed. This checkpoint updates documentation/PR readiness only; source/tests/tools, v41 and Alpha 0.7 remain unchanged. Prior 720-pass result is retained, not rerun for documentation-only acceptance.
- **Native observed-entry developer validation:** final full suite **720 passed in 1412.41s (23m32s)** at source `0efa822c5924c35ff6f654e649daacd5c237dbde`, Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen, clean exit/no warnings. Focused UI **68 passed in 360.32s** plus final gesture/run/restart **4 passed in 3.72s**. Python 3.10 syntax only; separate 3.10 execution is not claimed. All previous 254 smoke records are preserved; checks 255–259 are PASS from the operator’s completed functional report. Source/test/tool bytes remain unchanged by the final documentation checkpoint. All test processes are closed.
- **Native observed-entry source:** `0efa822c5924c35ff6f654e649daacd5c237dbde` — Connect independent observed AMDX entry to native Review. Schema v41 / Alpha 0.7. 21 new native tests and a five-check retained Review trial are added; full **720 passed in 1412.41s (23m32s)**, clean exit/no warnings. Published in PR #66, now ready for review, stacked on unmerged #65. Focused native UI group **68 passed in 360.32s**; final gesture/run-ownership/restart regressions **4 passed in 3.72s**. The focused group began before the two final regression cases were added; the full suite covers the complete final source. Developer UI inspection confirms fixed-panel access and scrollable content at 1280×876 (existing application minimum when requesting 1280×720). Python 3.10 syntax passes; separate 3.10 execution is not claimed.
- **Observed revision source:** `d9d97dc60821d2f7730d91d1eb384eef92a989b4` — Add versioned one-entry observed AMDX revision. Independent v3 policy, shared structural helper, protected v41 observed receipts and disposable demo. Focused domain/storage/Review/E6 compatibility group **215 passed in 4.88s**, including **41 new observed tests**. Full suite completed: 699 PASS with a clean exit. Source is published in draft PR #65. The source branch is stacked on PR #64 because it uses the completed v40 pairing/transaction substrate.
- **Observed revision implementation:** operator accepted the two Review behaviors and authorized proceeding on 2026-10-12. Manual Observed/working input now uses independently named `revise-observed-v1`, sharing valid-role/compatible-retirement/subtype/Unknown/applicability/clear behavior with working entry while preserving earlier judgments. Immutable v41 receipts retain heads, original request, result and snapshot counts. V1/V2 claims and archives retain original serialization/replay; observed revision adds V3. UI binding is next, comparison remains deferred, and all 254 smoke records remain byte-identical.
- **Observed revision developer validation:** final full suite **699 passed in 830.49s (13m50s)**, clean exit/no warnings, Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen. Focused domain/storage/Review/E6 compatibility group **215 passed in 4.88s**; adds **41 observed cases** including all 16 position/role pairs, independent working/observed meaning, compatible retention/retirement, X subtype/Unknown/applicability/clear, no-op/nullable results and both ID reservations, selected/null basis carry, legacy conflict repair/exact old retries, mixed v1/v2/v3 archives, stale heads, atomic rollback, immutable receipts, inconsistent snapshot/result rejection, competing and exact-retry writers, separate-process reopen, scope guards, stable-cycle verification and actual archived-v40 schema/repository migration. Old rows remain byte-identical through migration; actual E6 normal-window compatibility passes at v41. Python 3.10 syntax parsing, disposable demo, guide references/fences and git diff --check pass; separate 3.10 execution was not run. GUI source and all 254 smoke records remain unchanged; native observed binding/trial is next, no new operator acceptance is inferred. The full test process exited 0; no background verification remains.
- **Review persistence source:** `e61c1aa5d27d20880adc476ef007328c89771001` — Persist explicit AMDX Review pairings and atomic observed actions. Source/tools/tests and guide changes are isolated on the v40 follow-up; the branch is stacked on PR #63 because it needs the pure Review pairing contract. Final focused Review/storage/E6 compatibility group **114 passed in 3.62s**, including **33 new repository/demo cases**. Full application suite completed with 658 PASS and a clean exit; this source is published in draft PR #64, stacked on PR #63.
- **Review persistence implementation:** operator authorized proceeding on 2026-10-12. Schema v40 adds `amdx_comparison` and `amdx_review_command`, SQL immutability and owned transactions. `record_comparison` selects an existing observation; `record_observation` atomically adds a new independent Observed accumulation claim and its explicit comparison. Scoped heads, original-request receipts, cross-action identity protection and consistent read snapshots are verified by the focused group. No baseline default, observed replacement policy, classifier or UI change is adopted. Existing 254 smoke records remain byte-identical.
- **Review persistence developer validation:** final full suite **658 passed in 813.57s (13m33s)**, clean exit/no warnings, Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen. Final focused Review/storage/E6 compatibility group **114 passed in 3.62s**; adds **33 repository/demo cases** covering atomic commit/rollback, original/alternate/missing bases, exact retries after later changes, identity drift/cross-action reuse, stale observed/comparison heads, SQL immutability/sequence collisions, ownership/channel guards, caller transaction retention, competing writers, concurrent exact retries, read snapshots, observed clear semantics, inconsistent receipts, separate-process reopen and actual archived-v39 schema/repository migration. Existing actual E6 normal-window compatibility passes at v40. Python 3.10 syntax parsing, disposable CLI, Markdown references/fences and git diff --check pass; separate 3.10 execution was not run. All 254 smoke records are byte-identical to `d940138`; no new operator result is inferred. The full test process exited 0 and no background verification remains.
- **Explicit Review foundation source:** `7a31f7194c3053a7254a6a58f2edc3fc631eb570` — Add explicit AMDX Review pairings and validated archives. Isolated module, 38 new tests and synthetic CLI demo; original application modules and all smoke records are unchanged. No schema migration, app database persistence, UI binding or baseline default is included. Draft PR #63 is stacked on PR #62 because it depends on the original coupled/v2 claim foundation.
- **Explicit Review foundation validation:** full suite **625 passed in 814.37s (13m34s)**, clean exit/no warnings, Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen. Focused Review + existing foundation group **98 passed in 0.42s**; adds **38 tests** for original/alternate/missing/late bases, scope/channel isolation, exact retries/identity drift/stale heads, recording chronology, uncertainty/conflicts/applicability, X subtype distinctions, v1/mixed archives, source-prefix preservation, inconsistent-record rejection and separate-process reload. Synthetic demo, Python 3.10 syntax parsing, guide references/fences and git diff --check pass. Separate Python 3.10 execution was not run. Existing application modules/schema/normal UI and all 254 smoke records are unchanged; no new manual result is inferred. This run has finished with exit code 0; no background verification remains.
- **Working-quartet implementation checkpoint:** `84167e9bec21189a6bca08e2206a191665df0caa` — Revise AMDX quartets with versioned anchors and valid phase choices. Operator authorized proceeding after reviewing the ten-case contract on 2026-10-11. This supersedes its proposed-only status and resolves the repeated-input no-op gap. Active branch starts at reviewed PR #61 head `4346c88b7d8a6b98e1dd776b12c41845ae35598a`; PR #62 is a separate accepted follow-up, ready for review. Schema v39 adds immutable working-command receipts with original request, expected head, result and changed flag. No-op identities remain idempotent after later edits without extra profile claims. v2 claims retain `revise-working-v1`, incoming anchor, prior basis, retired IDs and separate applicability. Original v1 claims/exports and analytical conflicts keep their original semantics. Normal valid entry retires incompatible anchors in one transaction; no cleanup or Save click, classifier adoption, parent/child propagation or new gate is introduced.
- **Working-quartet developer validation:** final full suite **587 passed in 757.42s (12m37s)**, clean exit/no warnings, Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen. Final focused domain/storage/UI/E6 compatibility group **133 passed in 108.59s**. Adds **41 cases** (21 domain, 11 repository, 9 UI), including all position/role pairs, compatible retention/retirement, X subtype, Unknown/applicability/clear, semantic no-ops and identity reservation, mixed archive/database replay, exact retries after later edits, immutable receipts, two writers, receipt-write rollback, actual archived-v38-schema migration and old-reader rejection, preserved claim bytes, explicit evaluation bases, normal restart, post-commit read failure and queued menu-close gesture protection. Earlier legacy and actual E6 normal-window compatibility tests pass at current v39 with original backups/manifest intact. Python 3.10 syntax parsing and git diff --check pass; a separate 3.10 execution was not run. TDA Focus, Thesis and Watch orientation/control fit inspected at 1024px width (existing minimum produced 1024×876). All original 250 smoke records are preserved; four additions make 254 total. Checks 251–254 are now PASS from the operator’s 2026-10-12 smoke completion, not from the developer suite. No separate per-check transcript, local runtime version or elapsed time was supplied. This test run finished with exit code 0; no background test work remains.

- **Follow-up operator acceptance — 2026-10-12:** “Smoke test complete. This feels much smoother.” records acceptance of checks 251–254 against the supplied `f81a3ec` checkpoint (source `84167e9`); no newer remote result commit was present when fetched. Mature X(C)/X(R) must be directly available in one click. This accepts the functional revision flow, while final rendering remains open. Documentation-only reconciliation retains the completed 587-pass suite; it does not claim a new application run. Four existing smoke-document checks pass by direct invocation in the resumed runtime; all 254 identities/comments and the first 250 statuses are preserved. Markdown fences and git diff --check pass. The earlier task venv is unavailable, so no fresh pytest application run is claimed.
- **Native AMDX feedback checkpoint — operator 2026-10-11:** operator prefers revising a working quartet with one new valid entry rather than finding/clearing an old anchor; normal role choices should match Q1 A/X, Q2 A/M, Q3 M/D, Q4 D/X across both legal orders. This affects the shared action as well as presentation; precise compatible-anchor/subtype/uncertainty handling needs refinement before implementation. Contextual hover and simultaneous session/day plus active 90-minute visibility received positive feedback. The operator explicitly superseded the smaller-companion footprint with a primary 16:9 workspace occupying most of an ultrawide or a full conventional screen, arranging charts/journals around the Cockpit. Requirements, decisions, audit and cycle contract now record those directions; no geometry/source change is made. At this feedback checkpoint, the locally saved checklist had not been pushed and all six new statuses remained NOT TESTED. The later operator-results checkpoint below supersedes that pending state. The one-entry working-quartet action remains the next refinement before another implementation slice. Full-suite baseline remains 546 passed; this documentation-only checkpoint does not repeat the application suite.
- **AMDX operator-results checkpoint — 2026-10-11:** `17b874b2c7fb48f2b35d2e30b9e2a6affe019072` — Record AMDX entry smoke results. Operator pushed all six checks 245–250 as PASS: orientation/provenance, immediate recording, in-place Watch and parent/child separation, X subtype/history, durable restart and follow-versus-pin navigation. All 250 identities/comments and the original 244 statuses are preserved. PR #61 is ready for review; no merge has occurred. This is acceptance of the existing functional entry path, not approval of final rendering or an implemented one-entry replacement action. The larger 16:9 workspace and structural-choice/replacement directions remain recorded follow-up work.
- **AMDX acceptance-reconciliation validation:** four existing pure smoke-document tests passed by direct invocation on Python 3.12.14; checklist comparison verified only the six new statuses changed, with all identities/comments preserved. Source/tests/tools exactly match tested boundary-review source `6cf65d2f514950089593b018d7e115a62f272834`; the 546-pass full-suite result remains valid and was not rerun for this documentation-only reconciliation. Schema v38 / Alpha 0.7 unchanged.
- **Native-feedback documentation validation:** four existing pure smoke-document test functions passed through direct invocation on Python 3.12.14; pytest and the previous test environment executable are unavailable in this resumed runtime. All 250 checklist records, including comments and six NOT TESTED additions, are byte-identical to the prior checkpoint. Changed Markdown fences are balanced and git diff --check passes. Source/tests/schema/plan are unchanged, so the prior 546-pass application result is retained rather than reported as a fresh run.
- **AMDX entry boundary-review developer validation:** final full suite **546 passed in 762.57s (12m42s)**, clean exit/no warnings, Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen. The UI/sandbox module now has **21 checks**: five added cases cover cancelled menus with/without inspection pins, actual menu selection across a boundary, failed-boundary retry/release and stale-boundary reference/head preservation. The original mouse-boundary check additionally verifies immediate resumption without a second revision. Four failing pre-fix regressions reproduced the defects; post-fix focused checks passed before the final full run. Python 3.10 syntax parsing and git diff --check pass; separate 3.10 execution/native desktop acceptance were not performed. All 250 smoke identities/statuses/comments remain unchanged, including six NOT TESTED AMDX entry checks. Schema v38 and Alpha 0.7 are unchanged.
- **AMDX entry developer validation:** final full suite **541 passed in 662.14s**, clean exit/no warnings, Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen. Focused AMDX/domain/storage/runtime/E4/dual-view/E6 compatibility group **114 passed in 78.03s**. Adds **16 UI/sandbox regressions** for actual mouse/menu/keyboard actions, immediate commit, source/gate/station isolation, parent/child separation, conflict and X/Unknown/clear, default follow versus pinned/gesture clock boundaries, failed/stale/read actions, normal-window restoration, retained demo and unrelated-file refusal. TDA Focus, Thesis and Watch were visually inspected at requested 1024px width (this runtime minimum yielded 1024×876); fixed panel width and control reachability pass, with natural runtime scrolling. Python 3.10 syntax parsing and git diff --check pass; a separate 3.10 execution/native desktop review was not run. The original 244 smoke identities/results are unchanged, with six NOT TESTED additions (250 total); no operator PASS is inferred.
- **AMDX persistence developer validation:** final full suite **525 passed in 274.19s**, clean exit/no warnings, Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen. Focused domain/storage/E6/E7/compatibility/database group **133 passed in 9.27s**; includes **30 new repository checks**. Separate-process restart, real two-writer contention, stale scope retries, failed append/migration rollback, immutable definition content and SQL replacement protection pass. The actual accepted-E6 writer → current normal-window restore tests verify original data and unchanged gates/source behavior at v38. Earlier schema tests now compare current-version constants; the v36 migration fixture constructs actual v36 instead of relabeling a newer database. The compatibility harness distinguishes original v37 and current schema. Disposable demo, Python 3.10 syntax parsing, documentation fences and git diff --check pass. A separate 3.10 execution was not run for this slice. Operator usability acceptance is not inferred from backend checks.
- **AMDX foundation developer validation:** final full suite **495 passed in 258.57s**, clean exit/no warnings, Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen. Focused foundation checks **39 passed in 0.53s**. The initial full run before the final X-subtype compatibility correction was **494 passed in 298.34s**; the final 495-pass run covers that correction and its new regression. The read-only synthetic demo and JSON archive/replay checks pass. Python 3.10 syntax parsing passes; this slice was not executed under a separate 3.10 runtime. Existing tracked source/tests/tools and all 244 smoke identities/statuses are byte-identical to the prior checkpoint; only new isolated domain modules/tests/demo and documentation are added. No new operator screen acceptance is required for this pure foundation; production persistence/renderers remain downstream.
- **Latest operator full-suite report:** **454 collected, 454 passed**, Python **3.10.12**, pytest **9.1.1**, pluggy **1.6.0**, on 2026-10-11; archived with the pushed results checkpoint above. Elapsed time and PySide6 version were not supplied.
- **Accepted E7 developer review validation:** **456 passed in 273.30s** on Python **3.12.14**, PySide6 **6.8.3**, pytest **9.1.1**, offscreen, clean exit and no warnings on 2026-10-11. The reviewed PR head and merged main have the same tree. Review found no blocking issues; GitHub had no review submissions, unresolved review threads, workflow runs or commit statuses. The handoff-only changes after merge do not change source/tests/schema/plan.
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

The current major frontier is **Milestone E — context maturity: QT/AMDX, external events, schedules, and distortions**. E1–E7 remain accepted and merged. PRs #61–66 now extend the merged baseline with durable session/90-minute quartet identities, versioned working/observed revision, optional explicit pairing persistence, immediate native input and preserved run-date Review. Schema v41 and Alpha 0.7 remain unchanged by integration. The final merge tree is identical to the accepted final head; the completed 744-pass module-isolated suite remains applicable. Higher interpretations still retain legacy/derived provenance; identified higher-cycle mapping, shared projections and purposeful Study access remain the next context architecture work. The first pure identity/read projection foundation is implemented in PR #67 and described in `AMDX_HIGHER_CONTEXT_GUIDE.md`; higher-cycle persistence and native binding remain downstream. Final 16:9 layouts, classifiers, comparison exploration and real model/news policy adoption remain downstream; policy adoption still requires explicit semantics and a published plan revision.

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

## Previous completed slice — E7

**E7 — generic model/playbook context predicates v0** is implemented on `feature/context-maturity-e7-v0`, reviewed in [PR #60](https://github.com/mehoyminoi/ict-trading-cockpit/pull/60). All nine checks are PASS, including controlled earlier-E6 compatibility. PR #60 merged on 2026-10-11 as `f57794cff6f128830655b458e999fd8f72038280`. This records the earlier E7 integration checkpoint; the AMDX stack is now merged through #66. E6 assessment/implementation PRs #58/#59 remain closed and merged.

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

Current action: pure higher context/projection source `e90255dd2be05402234ee685d9e95562d47e8fda` is published in PR #67, based on merged main `6dd43c8`. The implementation adds no database/native UI changes. Higher calendar positions and the futures-day monthly/weekly conventions remain distinct; unsupported relationships, absent interpretations and legacy provenance remain explicit. Full validation is recorded below; source/tests remained frozen throughout completed validation.

Next likely action: design the higher-cycle durable entry/restore path using these identities and projection before binding the native overview/editor. Retain the same permitted one-entry actions, own run/channel/cycle scope and historical reference. Study-owned selection and historical as-of research remain explicit later design; final renderer, comparison exploration and classifiers remain deferred. No new operator smoke trial is requested for this pure foundation.

Keep the Copy restart report as unconfirmed support friction; explicit E7 restarts are accepted. Before real model/news rule adoption, settle the Friday Asian Range Monday relationship, account applicability and policy effects. Forex Factory completeness, precision/status, normalized applicability and historical as-of knowledge remain unverified. No source refresh, readiness thresholds, competency evidence or order operations are introduced.

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


## 2026-10-12 — Higher-cycle identity/projection validation

Source `e90255dd2be05402234ee685d9e95562d47e8fda`, PR #67, branch `feature/amdx-higher-context-v0`, parent main `6dd43c8`. Focused **134 passed in 0.91s**, including **45 new cases**. Complete suite: **789 passed in 452.22s (7m32s)** across all **71 isolated module processes**, clean exits, no failures/errors/skips or pytest warnings. Each module’s JUnit count matched the full 789-node collection; no combined single-process full run is claimed. All test processes have exited. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen; Python 3.10 grammar parsed, separate 3.10 execution not claimed. New boundary API was exercised directly; existing native behavior is unchanged. All 260 smoke records are byte-preserved. Schema v41 / Alpha 0.7 unchanged. PR #67 is ready for review after completed validation; it remains unmerged.
