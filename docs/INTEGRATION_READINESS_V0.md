# Integration readiness assessment

Assessment of published #113 acceptance `3d99dac` (tree `755469cd22eec2e843277df6602b9bbdf92ebb7c`), 2026-10-31. This is a release-readiness assessment, not authorization to merge or a new everyday-use launch instruction. Schema 53 / Alpha 0.7 unchanged.

## Findings

1. **Accepted behavior remains the baseline.** Meaningful Study use, connected review 364–365, normal TDA → Watch Replay journey 366–368, and durable backup recovery 369 are accepted. No repeat operator exercises requested. Operator data was not accessed.
2. **The shared application exists; launch selection is incomplete.** `src/ict_cockpit/main.py` opens the default application database through `app_paths.py` (normally `~/.local/share/ict-trading-cockpit/ict_cockpit.db`). The operator's accepted data is in `~/ict-study-workspaces/study-v0/demo.db`. These are different databases. Merely changing `XDG_DATA_HOME` does not select that `demo.db`.
3. **The current Study trial launcher is not the final everyday entry point.** `tools/study_criterion_demo.py` correctly opens the durable database and media root, but explicitly selects the calendar after constructing MainWindow, overriding normal idle-Study/active-run startup routing. It also retains fixture labeling and seeds synthetic material for fresh directories. Do not remove fixture provenance from existing historical records.
4. **TDA/Watch has the same runtime, not a second application.** `MainWindow` supplies repositories from one connection, and `ProcessRunLauncherWidget` invokes the same Trade Plan runtime for Replay/Backtest/Forward Test/Live with existing eligibility rules. The separate accepted Replay trial supplies a fixed reference and stops timers; it is not an everyday launcher and must not be pointed at the meaningful Study directory.
5. **Next bounded implementation recommendation:** an explicit existing-workspace launch route that opens the accepted database and media/settings context, validates the location before writing, preserves manifest handling and normal startup routing, and neither seeds a fixture nor starts/authorizes a run. Prove idle Study and active Replay restart on disposable copies before asking for one operator launch check. No folder move, data merge, schema migration, eligibility bypass or removal of historical fixture labels is implied. A policy for creating brand-new non-fixture workspaces is separate.

## Stack reconciliation

GitHub inspection found all 38 PRs #76–113 open, draft and unmerged. The named target chain runs from #76 → main through #113 → #112. All inspected current heads except #83 are ancestors of tested tip `3d99dac`.

#83's current head `a447a6b` is one documentation-only commit beyond the inherited `0f38a09`. Its only changes are PASS markers for 311 and 312. The tested tip already contains both PASS markers and the later acceptance wording. Therefore no behavioral change or missing operator result needs to be imported now. Preserve that commit/result during a separately authorized integration; do not blindly reset or rebase the stack. PR #84 metadata still reports base SHA `0f38a09`; verify fresh heads at merge time.

| PR | Inspected head | Target |
| --- | --- | --- |
| #76 | `611c8ff` | main |
| #77 | `be6439d` | #76 |
| #78 | `0988b4b` | #77 |
| #79 | `6561f2c` | #78 |
| #80 | `953c812` | #79 |
| #81 | `6b04866` | #80 |
| #82 | `bbf44f8` | #81 |
| #83 | `a447a6b` | #82 |
| #84 | `e9460fe` | #83 |
| #85 | `cf9f660` | #84 |
| #86 | `2b9fca5` | #85 |
| #87 | `1258b43` | #86 |
| #88 | `51ba1e5` | #87 |
| #89 | `c732866` | #88 |
| #90 | `212ddcf` | #89 |
| #91 | `6454e04` | #90 |
| #92 | `e733f41` | #91 |
| #93 | `f410179` | #92 |
| #94 | `6908b14` | #93 |
| #95 | `b8510d2` | #94 |
| #96 | `53ce5b8` | #95 |
| #97 | `c36c591` | #96 |
| #98 | `93ce461` | #97 |
| #99 | `fedd532` | #98 |
| #100 | `a744dc9` | #99 |
| #101 | `294e908` | #100 |
| #102 | `fac47c4` | #101 |
| #103 | `5a6df7b` | #102 |
| #104 | `40f8069` | #103 |
| #105 | `6aafeba` | #104 |
| #106 | `a561bb6` | #105 |
| #107 | `2843baf` | #106 |
| #108 | `ed8b247` | #107 |
| #109 | `9059e70` | #108 |
| #110 | `7917471` | #109 |
| #111 | `b8f7b42` | #110 |
| #112 | `64d72d8` | #111 |
| #113 | `3d99dac` | #112 |


## Regression reconciliation

The initial full collection contained 1,317 nodes in 127 modules. Modules ran in separate processes, with four workers and separate HOME/config/data/cache directories, offscreen. Runtime: Python 3.12.14, PySide6 6.12.0, pytest 9.1.1; Python 3.10 syntax checked, not a Python 3.10 execution claim.

Initial run: 403.08 seconds, 121 modules clean. Four modules reported a failing test; two hit the 240-second per-module budget. This is not presented as an uninterrupted green full-suite run.

| Check needing reconciliation | Evidence and bounded correction |
| --- | --- |
| AMDX Lab feedback label | Accepted connected Study now reports `Study · Calendar / AMDX context`; retain the original catalog ID assertion. |
| Study Find feedback label | Accepted connected Study now reports `Study · Capture / current draft`; retain capture identity assertion. |
| Small Study window scrolling | Verify the active Study view's scroll area and actual scroll movement, rather than require overflow on the now-fitting outer shell. Calendar identity remains checked. |
| E6 compatibility | The old-source subprocess replaces PYTHONPATH, so target-installed Qt was unavailable. Rerun with Qt visible through an isolated interpreter. Then replace the obsolete hardcoded `46` assertion with current schema version; original v37 source, IDs, immutable snapshots, rules and original file-preservation checks remain intact. |
| Draft discard | An authored draft now requires destination confirmation before opening investigation capture. The test explicitly answers Yes at that step, then retains its separate Discard choice and preservation assertions. The diagnosed unattended modal wait was stopped. |
| AMDX small-window orientation | Study-first startup leaves the runtime hidden. Select the Trade Plan surface before inspecting runtime geometry. The focused geometry check and queued-menu gesture check each pass. Full-module rerun first exited 139 after prolonged cumulative Qt activity; the native crash location was not fully captured. The fixture now drains deferred widget deletion while its database is still open, instead of retaining per-test windows until session teardown; final result is recorded below. |

Only six existing test files change. No assertions about historical identity, retained originals, database integrity, authorization or migration preservation are removed. No runtime/source/tools/schema changes. Previously passing modules are retained evidence; affected modules are rerun. No operator tests are changed or newly requested.

## Next decision boundary

Publish this assessment and test maintenance as a draft stacked on #113 only with explicit authorization. Then prepare the bounded existing-workspace launch contract and one copy-based continuity proof. Consolidation/merges remain separately authorized and should use freshly verified heads; do not require the operator to resolve the #83 documentation delta manually. The regular Study command remains unchanged until the new launch route is implemented and reviewed.


## Final validation result

Cumulative validation covers all **1,317 collected tests across 127 modules**: 121 unchanged modules / 1,237 tests passed in the initial run; the six affected modules / 80 tests passed after the bounded test corrections. Reruns: 45 PASS in 48.03 seconds (labels, inner scrolling, real E6 migration), 5 PASS in 13.98 seconds (discard), and 30 PASS in 35.85 seconds (AMDX, including per-test Qt disposal). JUnit counts match the original collection, with zero failures/errors/skips in the accepted results. Initial failures, timeouts and native exit are retained above; this is cumulative evidence, not a claim of one uninterrupted green invocation. All validation processes have exited.

The final AMDX module passed with a clean exit after deferred window disposal was drained before closing each test database. This supports the fixture-lifetime correction; it is not a proven diagnosis of the earlier native crash's exact internals. Application code and ownership remain unchanged. Python 3.10 grammar and diff checks pass. Operator checks 364–369 remain accepted and unchanged; there is no new manual test for this test/documentation slice.
