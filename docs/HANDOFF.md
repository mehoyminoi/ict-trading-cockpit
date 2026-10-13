# ICT Trading Cockpit — Handoff Protocol

Use this file to make chat, branch, and developer handoffs deterministic and to prevent architectural regression when long conversation history is unavailable.

## Canonical handoff package

A new development chat should read these documents in this order:

1. **`docs/PROJECT_STATE.md`** — exact current checkpoint: branch, baseline, schema, Trade Plan revision, tests, current task.
2. **`docs/PROJECT_REQUIREMENTS.md`** — current intended product architecture and milestone roadmap.
3. **`docs/DECISION_AUDIT.md`** — conflict/supersession ledger; use this when an older idea disagrees with a newer one.
4. **`docs/DECISIONS.md`** — durable accepted architectural decisions and rationale.
5. **`docs/SYSTEM_GUIDE.md`** — human-readable conceptual map, terminology, subsystem relationships, and architecture loops.
6. **`docs/PROJECT_EVOLUTION.md`** — chronological architecture history explaining how the current model emerged.
7. **Relevant code/tests** — Git is authoritative for what is actually implemented.
8. **Historical source material** — consult only when clarification is still needed after the canonical package.

Do **not** infer current priority from the recency, detail, or enthusiasm of an older feature discussion. First check whether that idea was later implemented, refined, deferred, or superseded.

## Precedence rule

When sources appear to conflict, use this order:

1. verified current implementation + tests,
2. accepted current requirements,
3. explicit later durable decisions,
4. decision-audit supersession status,
5. earlier durable decisions,
6. project-evolution/history summaries,
7. raw historical transcript/chat discussion.

If a conflict cannot be resolved from these sources, stop and record it as an open design question. Do not silently choose the older or more detailed idea.

## Current-frontier rule

Every handoff must state the **current architectural frontier** in plain language, not merely the next Git branch.

This is intended to prevent a future chat from finishing a small convenience feature and then mistakenly treating the surrounding old roadmap items as the project's strategic priority.

For example, a frontier statement should look like:

> Milestone C — Evidence Maturity and progression governance is complete through operator-loop integration/guardrails. The next major roadmap frontier is Milestone E: context maturity for QT/AMDX, news, and distortions. Milestone D remains a parallel friction-driven hardening stream. Older Film Night, visual-polish, chart-gallery, broad integration, and Live-Watch enhancement ideas remain downstream unless actual use makes them blocking.

Update this statement whenever the project's center of gravity materially changes.

## When to update the handoff package

Update `docs/PROJECT_STATE.md` whenever any of these occurs:

- a substantial feature slice is completed,
- a schema migration lands,
- the published Trade Plan revision changes,
- a major architectural decision is accepted,
- a branch is about to be merged or switched,
- the current task or known blockers change materially,
- a long ChatGPT conversation is nearing its limit.

Also update:

- **`DECISIONS.md`** when a durable decision is accepted,
- **`DECISION_AUDIT.md`** when an older decision is refined/superseded or a conflict is discovered,
- **`PROJECT_EVOLUTION.md`** when the project changes architectural phase or center of gravity,
- **`SYSTEM_GUIDE.md`** when terminology, ownership boundaries, subsystem relationships, or major system loops materially change,
- **`PROJECT_REQUIREMENTS.md`** only when the accepted current product/roadmap itself changes.

Do not use `PROJECT_REQUIREMENTS.md` as a running diary.

## Minimum checkpoint fields

`PROJECT_STATE.md` must record:

- active branch,
- main/implementation baseline commit SHA + message,
- test status and exact count,
- schema version,
- Trade Plan revision,
- last completed work,
- current architectural frontier,
- current task,
- known unresolved issues,
- intentionally deferred behavior,
- next likely action.

## Decision-recording standard

A durable entry in `DECISIONS.md` should include:

- date,
- title,
- status,
- decision,
- rationale,
- consequences / intentionally deferred behavior,
- **Supersedes:** previous decision(s), when applicable.

If the new decision changes the meaning or priority of an older one, also update `DECISION_AUDIT.md`.

## Before ending a development slice

1. Run the full automated test suite.
2. Run relevant manual acceptance checks in `docs/SMOKE_TEST.md` for substantial workflow/schema/risk/time changes.
3. Record exact automated and manual results.
4. Confirm schema and Trade Plan revision.
5. Inspect the actual Git diff.
6. Update `PROJECT_STATE.md`.
7. Update `DECISIONS.md`, `DECISION_AUDIT.md`, and/or `PROJECT_EVOLUTION.md` if warranted.
8. Commit documentation with the slice or in a dedicated documentation checkpoint.
9. Make sure `Current task` and `Current architectural frontier` are precise enough for another chat to continue without reconstructing history.

## Before a conversation approaches its limit

Do not wait for the final message.

Perform a **handoff freeze**:

1. stop starting new feature work,
2. finish or explicitly mark the current working checkpoint,
3. make the Git state unambiguous,
4. update the canonical handoff package,
5. record any newly accepted decision or supersession,
6. include unresolved questions explicitly,
7. provide the user the next-chat prompt below.

The objective is that the next chat needs repository reading, not conversational archaeology.

## New-chat startup prompt

Use this prompt when starting a fresh ChatGPT development conversation:

> Continue development of the **ICT Trading Cockpit** from the repository `mehoyminoi/ict-trading-cockpit`.
>
> **Do not begin feature work immediately and do not reconstruct the project from generic memory.** First recover the canonical project state from GitHub.
>
> Read these repository documents in this exact order:
>
> 1. `docs/PROJECT_STATE.md`
> 2. `docs/PROJECT_REQUIREMENTS.md`
> 3. `docs/DECISION_AUDIT.md`
> 4. `docs/DECISIONS.md`
> 5. `docs/SYSTEM_GUIDE.md`
> 6. `docs/PROJECT_EVOLUTION.md`
> 7. `docs/HANDOFF.md`
> 8. `docs/SMOKE_TEST.md` when acceptance/testing context is relevant
>
> Then inspect the relevant current code/tests and Git branch/commit state before proposing changes.
>
> Apply this precedence rule whenever sources appear to disagree:
>
> **verified current implementation/tests > accepted current requirements > explicit later durable decisions > decision-audit supersession status > earlier decisions > historical summaries/transcripts.**
>
> Do not revive an older feature or priority merely because it was discussed in detail. Check whether it was later **implemented, refined, deferred, or superseded**.
>
> Explicitly report back before coding:
>
> - current branch/main baseline,
> - schema version,
> - Trade Plan revision,
> - latest verified automated/manual test status,
> - last completed slice,
> - current architectural frontier,
> - current task,
> - the next recommended slice and why it follows from the current frontier,
> - any conflict or ambiguity you found in the handoff package.
>
> The project values architecture correctness, explicit revision/provenance semantics, small tested vertical slices, and substantial manual acceptance. Do not invent readiness percentages, thresholds, automation, or trading rules that the Trade Plan/evidence does not yet justify.
>
> Important recovered trajectory: the project deliberately shifted away from further Live-Watch embellishment toward the learning/progression loop. Milestone B's human synthesis chain is complete:
>
> **Evidence -> Competency Synthesis -> Cross-Run Observation -> Development Direction -> targeted Study routing**
>
> Milestone C is complete. The next major roadmap frontier is Milestone E, with Milestone D continuing only for proven operator friction:
>
> **boundary-aware Evidence Maturity -> Trade Plan progression policy -> explainable eligibility -> regression/downgrade semantics -> operator-loop integration -> later Live Execution governance**.
>
> Treat `docs/PROJECT_STATE.md` as the final authority for whether that frontier has changed since this prompt was written.
>
> If local terminal state may be ahead of GitHub, ask me for fresh `git status`, branch/SHA, or test output rather than assuming.
>
> Do not modify the roadmap merely to match an older conversation artifact. If historical clarification is required, explain the conflict first.

## Optional short startup prompt

When the canonical package is known to be current, this shorter form is acceptable:

> Continue the ICT Trading Cockpit from GitHub. Read `PROJECT_STATE.md`, `PROJECT_REQUIREMENTS.md`, `DECISION_AUDIT.md`, `DECISIONS.md`, `SYSTEM_GUIDE.md`, `PROJECT_EVOLUTION.md`, and `HANDOFF.md` in that order before coding. Respect the precedence/supersession rules in HANDOFF. Report the verified checkpoint and current architectural frontier before proposing the next slice.

## Principle

Chat history is useful working context, but it is not the canonical project record.

- **Git** is canonical for code and migrations.
- **PROJECT_STATE.md** is canonical for the exact current handoff.
- **PROJECT_REQUIREMENTS.md** is canonical for current intended product architecture/roadmap.
- **DECISION_AUDIT.md** is canonical for supersession/conflict status.
- **DECISIONS.md** is canonical for durable design rationale.
- **SYSTEM_GUIDE.md** explains the architecture in human-readable form without superseding canonical requirements/decisions.
- **PROJECT_EVOLUTION.md** preserves architectural history without making old priorities current.
- Versioned Trade Plan data is canonical for trading/process rules.

A successful handoff should require verification, not archaeology.

## 2026-10-12 — Quartet follow-up acceptance

Checks 251–254 are PASS from the operator’s message, “Smoke test complete. This feels much smoother.” No separate per-check log, local runtime details or new result commit was supplied. Initial checks 245–250 and all previous 250 records are preserved. Application source remains `84167e9bec21189a6bca08e2206a191665df0caa`, validated by the completed 587-pass suite; this reconciliation changes documents only. PR #62 is ready for review, stacked on unmerged PR #61; do not infer merge authorization. Active schema v39 / Alpha 0.7.

Mature X(C)/X(R) entry must each take one click from the active target, with direct future keyboard/macro-pad actions. The current submenu remains an interim renderer. Primary 16:9 geometry, whole-stack renderers and classifiers remain downstream.

Next is `AMDX_REVIEW_COMPARISON_CONTRACT_REVIEW.md`: containing-cycle observation and explicitly retained expectation pairing. The proposed first-expectation default remains unaccepted. No observed entry, comparison UI, automatic grade or rule adoption is added.

## 2026-10-12 — Watch history/comparison boundary

Operator clarified that normal Watch needs the AMDX stack as it is now and current position within it. Do not add prior stack versions or before/after comparisons to support the Review proposal. Preserve automatic immutable revision retention. Later purposeful Review/Study may explore changes associated with identified price-action events or noticed features; context links, samples and aggregation remain unimplemented. The first-versus-latest default remains open. This update changes documents only; source/tests/tools, accepted 254 smoke records, schema v39 and Alpha 0.7 are unchanged.

## 2026-10-12 — Explicit Review pairing foundation

Active follow-up `feature/amdx-review-pairing-v0` starts at accepted quartet checkpoint `eb822bc`. `analysis/amdx_review.py` adds a pure, frozen Review history with explicit expected/observed claim references, nullable expected basis, same run/branch/quartet checks, preserved comparison predecessors, exact retries and stale-head rejection. Its self-contained archive replays retained v1/v2 source claims. Order relation and X subtype are descriptive and separate.

`tools/amdx_review_demo.py` is a read-only synthetic CLI example, not a normal-window trial or required new smoke test. `AMDX_REVIEW_FOUNDATION_GUIDE.md` explains what exists and what does not: app database persistence/concurrency and observation-plus-pair transactions are next; UI/defaults/event aggregation remain downstream. Watch, schema v39, Alpha 0.7 and all accepted smoke records are unchanged. The broader architecture frontier remains Milestone E.

**Final verification:** source `7a31f7194c3053a7254a6a58f2edc3fc631eb570`, draft PR #63 stacked on PR #62. **625 passed in 814.37s**, clean exit/no warnings; focused group **98 passed in 0.42s**, including 38 new tests. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen; Python 3.10 syntax only. Synthetic CLI and Markdown/diff checks pass. All 254 smoke records are byte-identical to `eb822bc`. Full test process exited 0 and no background test work remains. Next is repository integration, not adding history to Watch or adopting an unreviewed baseline default.

## 2026-10-12 — Review pairing persistence

Follow-up `feature/amdx-review-persistence-v0` starts at the pure foundation’s `d940138`. Schema v40 adds immutable comparisons and original Pair / ObserveAndPair receipts. `TradingSessionRunRepository(connection).amdx.review` exposes validated history, original pair lookup, alternate pairing and atomic new-observation-plus-pair actions. Both inspected heads are explicit, exact retries remain original after later changes, and any source/cycle/pair/receipt failure rolls back the entire action. Readers use a consistent snapshot without changing caller transaction ownership.

See `AMDX_REVIEW_PERSISTENCE_GUIDE.md` and the disposable `tools/amdx_review_persistence_demo.py`. v39 migration preserves old row bytes and working no-op receipts; older v39 bootstrap rejects v40. Current Watch and Review controls are unchanged, all existing smoke records remain unchanged, and Alpha 0.7 publishes no new rule/default. Contextual Review binding is downstream; no comparison/history belongs on normal Watch.

**Final persistence verification:** source `e61c1aa5d27d20880adc476ef007328c89771001`, [draft PR #64](https://github.com/mehoyminoi/ict-trading-cockpit/pull/64), stacked on PR #63. Full **658 passed in 813.57s**, clean exit/no warnings; focused **114 passed in 3.62s**, including 33 new repository/demo tests. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen; Python 3.10 syntax only. Archived-v39 schema/repository migration preserves old row bytes and retry meaning; actual E6 normal-window restoration passes at v40. All 254 smoke records are byte-identical to `d940138`. Test process exited 0; no background verification remains. Next: review contextual observed-entry behavior and baseline/default before wiring the separate Review surface; this does not add history/comparison to Watch. No merge occurred.

## 2026-10-12 — Review interaction proposal

The concrete contract review is `AMDX_REVIEW_INTERACTION_CONTRACT_REVIEW.md`. Two unaccepted recommendations: independently versioned observed quartet correction matching the accepted working semantics, and routine observed capture with no automatic comparison. Optional deliberately selected comparison basis would persist through same-cycle corrections until changed/cleared. v40 already supports explicit/null pairing, but observed replacement/no-op/applicability still needs a versioned action extension before controls. No runtime/source/schema/smoke changes are made; retain the completed 658-pass result. Do not infer acceptance from readiness to review, or put history/comparison on Watch.

## 2026-10-12 — Review behavior accepted; comparison lower priority

The operator accepted both principal interaction behaviors: independently versioned one-entry observed correction and optional comparison with no automatic first/latest pairing. Deliberately selected same-cycle basis remains through corrections until changed/cleared. Comparison is lower priority, deferred to a demonstrated Study/Review need; there is no comparison option or launch route from Watch.

Next effort supports efficient observed entry and current-stack orientation, using the completed v40 storage. Versioned observed replacement/no-op/applicability semantics are not yet implemented and must preserve original accumulation replay. Do not expand comparison UI as the automatic next slice. This checkpoint changes documentation only; the 658-pass source, schema v40, Alpha 0.7 and all 254 smoke records remain unchanged. No merge occurred.

## 2026-10-12 — Observed revision shared action

Active follow-up `feature/amdx-observed-revision-v1` starts at accepted behavior checkpoint `1bf3933`. Schema v41 adds immutable observed revision receipts and original source/comparison snapshot counts. Named `revise-observed-v1` implements one-entry normal Observed/working correction with the accepted subtype/Unknown/applicability/clear/no-op behavior. Earlier Expected and observed claims remain independent and immutable. V1/V2 replay/exports retain original meaning; new observed claims use V3.

Use `amdx.review.revise_observed` / `ObservedRevisionResult`. Changed actions atomically persist source, quiet pairing metadata and receipt; no-ops reserve IDs with no source/pair change. Both heads are checked, original exact retries survive later edits, selected same-cycle basis remains pinned and None never falls back to first/latest. v40 migration preserves old row bytes; older bootstrap rejects v41. See `AMDX_OBSERVED_REVISION_GUIDE.md` and the disposable CLI demo. Native Review binding is next; comparison controls remain deferred with no Watch entry point.

**Final observed-action verification:** source `d9d97dc60821d2f7730d91d1eb384eef92a989b4`, [draft PR #65](https://github.com/mehoyminoi/ict-trading-cockpit/pull/65), stacked on PR #64. Full **699 passed in 830.49s**, clean exit/no warnings; focused **215 passed in 4.88s**, including 41 new tests. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen; Python 3.10 syntax only. Archived-v40 migration preserves original rows and exact old retries; actual E6 normal-window restore passes at v41. All 254 smoke records and GUI source remain unchanged. Test process exited 0; no background verification remains. Next is native Review entry/gesture/restart binding, followed by its focused hands-on trial. Comparison controls remain deferred and excluded from Watch. No merge occurred.

## 2026-10-12 — Native observed entry follow-up

Active `feature/amdx-observed-entry-v1` starts from `d058215` / draft #65. Source `0efa822c5924c35ff6f654e649daacd5c237dbde` connects one-entry Observed/working actions in normal Post-Market Review. It uses the saved Trading Day identity, offers all-session inspection and stays on the inspected target across rollover. Missing day identity disables entry rather than guessing. Direct X(C)/X(R) controls also serve working TDA/Watch. Both heads/run/channel/reference remain pinned through gestures; failure/stale/read/restart paths preserve committed meaning and require deliberate recovery.

No AMDX comparison/history surface or Watch route is added. Application-backed legacy flat intraday observed controls/comparison are hidden without rewriting their saved values; higher legacy fields remain. Schema v41 / Alpha 0.7 unchanged. The retained `tools/amdx_observed_entry_demo.py` uses normal transitions with an explicit synthetic incomplete-TDA override and offers a sandbox-only write fault. Five new operator checks 255–259 are NOT TESTED; all previous 254 records are unchanged. Follow `AMDX_OBSERVED_ENTRY_OPERATOR_GUIDE.md`. Final 16:9 geometry and broader Study/comparison work remain deferred.

**Final native verification:** [draft PR #66](https://github.com/mehoyminoi/ict-trading-cockpit/pull/66), stacked on unmerged #65. Full **720 passed in 1412.41s (23m32s)**, clean exit/no warnings, at source `0efa822c5924c35ff6f654e649daacd5c237dbde`. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. Focused UI group **68 passed in 360.32s**; final gesture/run-ownership/restart regressions **4 passed in 3.72s**. The focused group began before two final cases were added; the full suite covers all 21 new native cases and the complete final source. Python 3.10 syntax passes, separate 3.10 execution not claimed. Native fixed-panel/scroll layout inspected at 1280×876; existing minimum prevented requested 1280×720. Changed Markdown links/fences and git diff --check pass. All previous 254 smoke records are unchanged; new 255–259 remain NOT TESTED by the operator. Test process exited 0 and no background verification remains. Next is this five-check functional trial; keep draft until its results are reviewed. No merge occurred.


## 2026-10-12 — Native Review functional acceptance

The operator reported “All points passed,” accepting checks 255–259 after check-258 clarification and fresh-sandbox restart guidance. No separate per-check log, fixture/run ID, local runtime details or elapsed time was supplied. The original premature-close launcher error remains undiagnosed: the guard covers a missing expected active run and a manifest/run mismatch, so do not assert that the operator concluded the run. The successful retest accepts the functional smoke; it does not claim original-fixture recovery.

`AMDX_OBSERVED_ENTRY_OPERATOR_GUIDE.md` now explicitly establishes NYAM **90m Q3 (09:00)** and XAMD before fault testing, distinguishes the Day target, uses the **18:00 ET futures-day rollover**, checks that disabling a fault does not replay an action, and uses the window X for restart rather than Conclude Trading Run. Existing smoke identities are preserved; only 255–259 change to PASS. PR #66 is ready for review, stacked on unmerged draft #65. #61/#62 remain ready, #63–65 remain draft; no merge occurred.

Source/tests/tools are unchanged from tested source `0efa822c5924c35ff6f654e649daacd5c237dbde` / checkpoint `7aeb0f9`. Retain the completed **720 passed in 1412.41s**, clean exit/no warnings, rather than repeating a full suite for documentation-only acceptance. Schema v41 / Alpha 0.7 unchanged. Next is review of the unmerged stack against accepted contracts; comparison controls/research remain lower priority and excluded from Watch. Final renderer geometry and higher-stack/Study work remain downstream.

**Acceptance-document verification:** four existing smoke-document test functions pass by direct invocation; all 259 identities/comments and the first 254 results are preserved, with only 255–259 statuses changed to PASS. Markdown links/fences and git diff --check pass. The prior Qt/pytest virtual environment is unavailable at this documentation-only checkpoint; no Qt execution or repeated full suite is claimed. Source/tests/tools remain byte-identical to `7aeb0f9`.


## 2026-10-12 — Stack review finding before integration

See `AMDX_STACK_REVIEW.md`. Published heads/bases #61–66 and their recorded tested-source equivalence are verified. Five existing CLI demos pass freshly and Python 3.10 syntax is valid. No submitted reviews/inline threads existed at inspection. #63–65 are marked ready; all six remain unmerged. No source change is made, and no native/full rerun is claimed with Qt/pytest currently unavailable.

**Blocker in #66:** the shell preserves an existing Trading Day label when starting another run, and the Review adapter uses that unchecked container date. The real models accept an October 9 Replay run in an October 8 container; executing the exact cycle-selection source produces `day:2026-10-08`, despite the run's stored `reference_market_time` being October 9. This is a source-level reproduction, not new native UI evidence. Correct run-owned original-date selection / cross-date launch handling before integrating #66. Preserve fallback/missing-provenance safety, rollover/gesture/restart behavior and all accepted 245–259 results. The completed 720-pass suite lacks this edge case and remains evidence for the covered source. The original premature-close report is still undiagnosed and is separate from this finding.

Next is the narrow correction and native/full verification. After it passes, proposed integration order is #61 → #62 → #63 → #64 → #65 → #66, preserving ancestry and retargeting children only after actual parent merges. No merge is authorized or performed by this checkpoint. Comparison and broader rendering remain deferred.


## 2026-10-12 — Review date correction implementation

Source `e12a2d4c4d4767f32dd13c3ea795ffab18531f78` fixes the reviewed date selection with the existing run-start market-context snapshot. Valid original reference wins over an older container label with explanatory hover provenance. Absent reference uses explicit legacy Day fallback; malformed reference or absence of both sources disables capture rather than substituting the clock or an expectation. An in-flight target cannot commit after its original-date provenance changes. Different-date/undated-existing additional launch rejects before process reset; same-date runs and the existing new-day path remain functional. Old misgrouped saved runs restore their own reference without moving claims or relabeling their container.

Focused **77 passed in 784.90s**, with 24 new date/launch/native/restore cases. Full verification is running over all 744 collected tests in 70 module processes, with a fresh Qt application per module to avoid accumulated fixtures. The exact execution method/count/result must be recorded; do not call a running suite finished. Restored native environment: Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. The scratch-local Qt installation initially crashed before app import; a fresh installation under `/tmp/ict-amdx-fix-venv` imports/runs correctly. That environment issue is not an application test failure or a source fix.

The retained synthetic `tools/amdx_review_date_demo.py` and `AMDX_REVIEW_DATE_OPERATOR_GUIDE.md` map to one new check 260, NOT TESTED. All previous 259 identities/results/comments are preserved. Schema v41 / Alpha 0.7 and domain/storage/archive policies are unchanged. No merge occurs. Complete developer validation/publication and this focused operator trial before reassessing integration.


**Final date-correction verification:** source `e12a2d4c4d4767f32dd13c3ea795ffab18531f78`; focused **77 passed in 784.90s**, full **744 passed in 328.84s (5m29s)** over all 70 isolated module processes, clean exits/no warnings. The full collection was checked at 744 node IDs and every module's JUnit tests/failures/errors/skips counts validated; no combined single-process full run is claimed. This execution method avoids Qt fixture accumulation. All processes exited 0 and no background test work remains. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen; Python 3.10 syntax only. The original native import environment issue is resolved with the temporary-directory environment. Native 1280×876 layout, CLI help, Markdown/diff checks and unchanged prior smoke records are verified. No schema/archive/Alpha 0.7 change. The implementation blocker is corrected; new check 260 remains NOT TESTED before integration. No merge/retarget is performed.


## 2026-10-12 — Guided Review date operator acceptance

Check **260 PASS** from the guided trial reports. Operator guided report, 2026-10-12 (America/Denver): upper Trading Day advanced to October 10 while Observed AMDX remained October 9; NYAM 90m Q3=M was entered and the profile was XAMD. After window-X close and same-directory reopen, the date remained October 9; selecting NYAM restored XAMD and Q3 entered without another phase choice. After Conclude Trading Run, Start Another Trading Run created no second run and displayed: "Run not started - selected reference belongs to Trading Day 2026-10-13. Complete the current Trading Day, then choose Start New Trading Day". The October 13 request is the live reference after restart, not a change to the saved Review date. The heading-tooltip inspection was not separately reported; no operator hover acceptance is inferred.

This supersedes earlier pending-trial wording. Source/tests/tools remain unchanged from `e12a2d4` (published correction checkpoint `eeab093`); completed focused 77 / whole-suite 744 across 70 isolated modules remains the application verification evidence. This documentation-only result needs no new application test run. Preserve all first 259 smoke records. PRs #61–66 remain ready and unmerged; next is dependency-order integration reassessment, not another renderer or comparison slice. This checkpoint neither authorizes nor performs merge/retarget. The concluded sandbox is intentionally finished; use a fresh empty directory for any future trial.


## 2026-10-12 — Merged AMDX stack and next architecture frontier

The operator explicitly authorized merge and continuation. All six PRs were freshly checked against the rehearsed heads, merged with merge commits in #61 → #62 → #63 → #64 → #65 → #66 order, and retargeted to main only after the preceding parent actually merged. Each merge's two parents and exact tree were verified against GitHub. All PRs are closed/merged into main; original feature branches are retained. Earlier unmerged/pending integration statements are historical.

| PR | Merge commit | Reviewed head |
| --- | --- | --- |
| #61 | `c29506eceb36e9c55416ab0a081f3cfaa840499d` | `4346c88` |
| #62 | `26de0d06ea245c7192cbb48ec853e28cee8ea3f5` | `eb822bc` |
| #63 | `7fb664ed20c72ef5c75a6acff293df9f8dcb9d10` | `d940138` |
| #64 | `b2d1741b751881d0799e0edb053c9308412945b3` | `1bf3933` |
| #65 | `fdfb2424bd94580bb4bf44ad33e2c18ad02b2949` | `d058215` |
| #66 | `d092ac7516f585b03c74276d3936201c9aab9117` | `c851e9a` |

Final merge tree exactly equals `c851e9a`; source/tests/tools byte-match tested correction `e12a2d4c4d4767f32dd13c3ea795ffab18531f78`. Retain focused 77 PASS and complete 744 PASS across 70 isolated module processes; these are completed prior runs, not new merge-checkpoint executions. Smoke identities/statuses/comments, v41 and Alpha 0.7 are unchanged. Check 260 operator reports and its unreported-tooltip limitation remain authoritative.

Milestone E remains current. `AMDX_HIGHER_STACK_CONTRACT_REVIEW.md` inventories existing raw higher positions versus legacy flat interpretation, proposes shared cycle/projection ownership and makes boundary examples explicit before persistence or renderer changes. This is the next architecture proposal, not a new accepted trading rule or implementation. Final 16:9 presentation, comparison exploration, classifiers and Study-first startup remain downstream. No new smoke trial is required for this documentation checkpoint.


## 2026-10-12 — Pure higher-cycle context foundation

The operator authorized proceeding from the merged-stack architecture contract. Source `e90255dd2be05402234ee685d9e95562d47e8fda` adds `analysis/amdx_context.py` with versioned higher temporal identities, explicit aware reference, four half-open quarters, stable parent/prior-Q4 references and a shared immutable read projection. Calendar-year and futures-day conventions remain distinct. Friday/fifth-week/pre-first-Monday/closed states do not invent input targets. A cross-month week retains the parent derived from its own Monday, including when the currently selected monthly occurrence changes. Existing intraday IDs/content remain byte-equivalent.

Projection selects current heads only for the requested run/channel/branch/cycle and retains the original claim/inference/anchor/applicability/reference provenance. No parent phase, other-run interpretation, prior-cycle head or flat legacy value supplies a fallback. Exact legacy values remain separate and missing fields stay missing. Empty history stays Unresolved despite factual Q positions. The caller chooses an explicit reference; future Review must bind its preserved original source, and retrospective Study must select its historical information basis explicitly. This projection is not an as-of query.

Focused **134 PASS in 0.91s**, 45 new cases; complete suite: **789 passed in 452.22s (7m32s)** across all **71 isolated module processes**, clean exits, no failures/errors/skips or pytest warnings. Each module’s JUnit count matched the full 789-node collection; no combined single-process full run is claimed. All test processes have exited. Python 3.10 syntax only, execution Python 3.12. Main is unchanged at `6dd43c8`; PR #67 is the isolated follow-up. All smoke records, schema v41, Alpha 0.7, action policies and existing GUI/storage stay unchanged. No operator trial or merge is implied. Higher persistence/native binding is next; final 16:9 rendering, Study-owned selection, comparison exploration and classifiers remain separate. See `AMDX_HIGHER_CONTEXT_GUIDE.md` for boundary examples.


## 2026-10-12 — Higher entry/restore over existing v41 storage

The operator authorized proceeding from the pure higher foundation. Source `6c993c73000f354ce0cbdf3059ad5ea89376fd92` in PR #68 adds `AMDXRepository.context`. It takes consistent run/claim/pair snapshots, preserves exact stored legacy maps, prepares frozen higher targets and delegates to the existing working/observed revision transactions. The action bodies are extracted into guarded transaction-owned helpers without changing policy or serialized request meaning. No schema migration or run-field conversion occurs.

New observed requests check the run's saved starting timestamp after acquiring the write transaction; a changed/malformed/missing source rejects all new records. A saved Day alone is insufficient for higher calendar/futures-boundary identity; existing intraday fallback remains unchanged. Exact committed retries continue to use their original receipt/basis/result even after a current reference or definition resolver changes. Stale heads/pair selection and SQL failure preserve committed meaning; reads retain caller transactions and writes refuse unrelated pending work.

Focused **210 PASS in 8.58s**, **50 new cases** including connection/process and normal MainWindow reopen, reference race under the write lock, consistent WAL read under concurrent reference/history updates, competing writers, nullable/old-definition retries and all five higher levels/both channels. Full suite: **839 passed in 447.51s (7m28s)** across all **72 isolated module processes**, clean exits with no failures/errors/skips or pytest warnings. Each module’s JUnit count matched the complete 839-node collection; no combined single-process full run is claimed. All test processes have exited. Python 3.10 grammar only, runtime Python 3.12. Main remains `6dd43c8`; #67 and #68 are unmerged, with #68 based on #67. All 260 smoke records, schema v41, Alpha 0.7 and native controls remain unchanged. No new operator trial is requested. Next is native higher overview/editor binding with complete gesture/permission checks, before final rendering or Study-owned/as-of research. See `AMDX_HIGHER_PERSISTENCE_GUIDE.md`.


**Review-period boundary:** this v0 observed adapter resolves the run-start higher occurrences. A single futures-day run can cross calendar midnight into another Yearly quarter; working entry may record both scopes. Before native binding, specify explicit selection of another identified higher Review occurrence. Do not silently use a later live clock or an expectation claim as a fallback reference. This is a known next contract, not a new as-of replay/default-pairing policy or an implemented selector.


**Previous-reader compatibility:** the actual parent `e27bd31` v41 source, isolated through Git archive, restored newly written higher working/observed claims and their pairing. All seven run/cycle/claim/command/pair table row sets remained unchanged; schema stayed v41. Synthetic evidence was retained in `/tmp/ict-higher-v41-compat-83u8j2pu`. This is a separate compatibility check, not recovered operator history or an additional full suite.


## 2026-10-13 — Exact DST instants and explicit higher Review proposal

PR #68 source `9c476df520efec8a7e50a04c015e0de4da78d850 corrects repeated-hour source comparison and domain replay by retaining exact numeric-offset instants. New source validation compares UTC instants; Quarter/Claim/Comparison in-memory timestamps match their serialized representation. Original ISO payload content, policies, schema v41, Alpha 0.7 and all 260 smoke records are preserved. Five new regressions; **313 focused PASS in 13.20s**, then **844 complete PASS across 72 isolated modules in 508.64s**, clean exits with no failures/errors/skips or pytest warnings and collection-matched counts. Python 3.10 grammar only; runtime Python 3.12. All test work finished.

`AMDX_HIGHER_REVIEW_PERIOD_CONTRACT.md` now concretely proposes explicit orientation within the whole reviewed futures day, defaulting to the preserved run-start reference and deduplicating unchanged higher context. Navigation writes no interpretation; another orientation is available independently of expectation history. Eighteen temporal assertions passed against existing mapping. Scope-proof metadata/migration and selection/native bindings remain proposed and unimplemented; current v0 Observed loading remains run-start scoped. Review this semantic contract before implementation. No new smoke trial or merge occurred; main remains `6dd43c8`, #67/#68 unmerged.

The mature Lab is intended to have a spacious full-stack AMDX workspace with nearby detail, prominent versioned definitions and purposeful investigation. Watch keeps quiet current-state orientation/direct entry. Lab presentation, Study-owned historical information basis and final geometry are not implemented by this checkpoint; comparison exploration remains lower priority and excluded from Watch.


## Final historical/forward catalog checkpoint — 2026-10-13

The operator explicitly required early comprehensive historical AMDX entry across all layers on 2026-10-12 (America/Denver), initially MNQ with potential later NNQ use. Source `d9ccb4422cf9f2f517e38869acb8f57e143e344f` in [PR #69](https://github.com/mehoyminoi/ict-trading-cockpit/pull/69), branch `feature/amdx-historical-catalog-v1`, implements independent collection ownership using the shared pure working/observed quartet actions. Parent is #68 checkpoint `e80a17be3d9ff28896aeb344e5f76a69722228cd`; #67–69 remain unmerged, main remains `6dd43c8`.

Schema v42 adds immutable catalog/command tables and indexes; the existing cycle registry is shared. Collections retain explicit instrument, purpose and definition references. Entries freeze collection/instrument/channel/cycle/quarter/reference/head and retain actual recording time, declared historical/forward capture, optional availability/evidence/definition basis and original changed/no-op result. There is no fabricated trading run, run-owned claim/pair, implicit expectation baseline, guessed legacy asset or recent-date cutoff. All seven currently identified levels are covered; future finer temporal resolvers remain separate. Portable archives retain every command, including nullable no-ops, and validate action replay. Current scoped occurrence heads are enumerable. Catalog scope is broader than run-bound Review; the bounded higher Review selector remains unimplemented.

Focused **382 PASS in 21.22s**, including **60 new cases** across domain/catalog/migration. Complete **904 PASS across 75 isolated module processes in 441.57s**, no failures/errors/skips or pytest warnings, with every JUnit count matching collection. Every module and the full runner exited successfully; no background regression work remains. Runtime Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. Python 3.10 grammar passes; separate 3.10 execution is not claimed. Normal native entry/Review and old E6 compatibility tests remain covered by the full run.

Actual parent-v41 schema migration preserves every original application table, including changed claims/pairs and original nullable receipts/retries. Injected DDL failure leaves v41 and every original row intact, without added catalog objects; successful migration assigns no assets or collections to prior data. Parent bootstrap explicitly rejects v42. All 260 smoke records are byte-identical to parent; Alpha 0.7 is unchanged. No new operator trial or merge occurred. PR #69 is ready after final verification.

Next is efficient native historical catalog navigation/entry and deliberate linkage of run captures, alongside the separate higher Review selection/proof integration before native higher binding. Spacious full-stack Lab is planned presentation, not implemented by this backend. Bulk import, throughput tuning/large analytical queries, as-of reconstruction, classifiers and statistics remain downstream. Declared ForwardEntry is provenance, not proof of no look-ahead; backfilled Expected must not be silently treated as contemporaneous prediction. Watch remains quiet current orientation/direct input without history/comparison controls. See `AMDX_HISTORICAL_CATALOG_GUIDE.md`.


## Native AMDX Lab checkpoint — 2026-10-13 (regression in progress)

Published source `678e9a0835a442f1de42ec6761bfcd7116fc6bad`, draft PR #70 on `feature/amdx-catalog-lab-v1`, parent #69 `5219524`. Full-stack/adjacent native catalog entry, explicit historical New York time and session inspection, legal phase/direct subtype choice, automatically recovered per-database navigation/provenance drafts and deliberate stale/read/write recovery are implemented. MainWindow's AMDX Lab tab and the retained 16:9 trial host the same widget. Prepared scope/capture basis is guarded through gestures and tab/selection changes. Repeated-hour occurrence is explicit; nonexistent spring times reject entry; closed references retain higher context and unavailable intraday rows.

Final focused **97 PASS in 23.81s**, including **32 new native/trial cases**. Python 3.10 grammar passes; runtime Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. Source is frozen during the complete **936-test / 77-module** regression run. That full run is in progress; its outcome is not yet claimed. Native render inspected at 1344×756 with provenance collapsed/expanded and at 1280×720 with a recorded yearly profile. These are standalone frames around the same widget; overall application's earlier minimum geometry is not changed or accepted as final.

The retained trial and exact four-check guide are `tools/amdx_catalog_lab_demo.py` and `docs/AMDX_CATALOG_LAB_OPERATOR_GUIDE.md`. New checks 261–264 are NOT TESTED; the earlier 260 items retain exact text/status/comments. Closing/reopening has no concluded-run state or reseed requirement. Schema v42 / Alpha 0.7 and catalog action meanings are unchanged; main remains `6dd43c8` (v41), and #67–70 are unmerged. Keep #70 draft until developer completion and operator trial review.

Remaining work for this checkpoint: finish complete regression verification, append final evidence, and publish final operator handoff. No operator trial has been reported yet. Run-capture linkage, bounded higher run Review selection/proof, bulk ingestion, broad as-of reconstruction, analytics/classifiers, Study-first startup and final visual rendering remain separate. Watch gains no history/comparison route.


## Final native AMDX Lab verification — 2026-10-13

Source `678e9a0835a442f1de42ec6761bfcd7116fc6bad`, draft [PR #70](https://github.com/mehoyminoi/ict-trading-cockpit/pull/70), `feature/amdx-catalog-lab-v1`, parent #69 `5219524`. The prior regression-in-progress checkpoint is historical; verification is now complete. The native/manual catalog surface is implemented, with all seven identified layers adjacent to the editor, direct X(C)/X(R), historical/session/quarter inspection, automatically recovered navigation/provenance drafts and pinned-gesture/failure recovery. MainWindow's AMDX Lab tab and the retained standalone trial host the same widget.

Final focused **97 PASS in 23.81s**, including **32 new native/trial cases**. Complete **936 PASS in 581.68s across 77 isolated module processes**, clean exits, no failures/errors/skips or pytest warnings, and every JUnit count matching the complete collection. All modules and the full runner exited; no background regression work remains. Python 3.10 grammar passes; runtime Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. No combined single-process full run or separate 3.10 execution is claimed. Native entry, older-data compatibility, MainWindow, Study and progression regressions remain covered.

Verified actual mouse/keyboard input at every layer, legal subtype, independent catalog/channel heads, scope/capture/tab changes during a gesture, stale external edits, write rollback, committed-write/read-failure distinction, exact historical reference and metadata restore, no-op provenance, historical/forward collection defaults, closed/skipped/repeated-hour contexts and explicit missing-catalog recovery. The retained 1998/1985 trial restores independently recorded profiles after close/reopen with no trading run or conclusion/reseed requirement. Standalone native render inspected at 1344×756 with provenance collapsed/expanded and at 1280×720 with a recorded yearly profile; overall main application minimum geometry and final visual acceptance remain separate.

All earlier **260 smoke items retain exact text/status/comments**. Four new checks **261–264 are NOT TESTED** by the operator; do not infer acceptance from developer tests. Use `AMDX_CATALOG_LAB_OPERATOR_GUIDE.md` and `python tools/amdx_catalog_lab_demo.py --data-dir /tmp/ict-amdx-catalog-lab-v1`. Keep #70 draft until those results and hands-on feedback are reviewed. Schema v42, Alpha 0.7 and catalog/run action semantics are unchanged; main remains `6dd43c8` (v41), #67–70 unmerged. No merge occurred.

Next is this focused native trial. Subsequent integration is deliberate run-capture linkage and bounded higher run Review selection/proof with quiet higher orientation; those are not implemented by this slice. Final renderer/topology, broad historical as-of reconstruction, bulk import/performance, statistics/classifiers and Study-first startup remain separate. Watch has no new history/comparison route.
