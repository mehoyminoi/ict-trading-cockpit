# AMDX stack review — 2026-10-12

Reviewed published checkpoint `1fc19d1b07195bc15b1d91670de9e9377e12f319`, application source `0efa822c5924c35ff6f654e649daacd5c237dbde`, against the accepted working/observed action, persistence and Watch/Review boundaries.

**Original review result: one integration-blocking finding in PR #66.** A subsequent source correction is implemented below; final developer validation passed (744 tests across all 70 isolated module processes) and focused operator check 260 is now PASS from the guided 2026-10-12 reports. No additional blocker was found in the reviewed domain/storage contracts. PRs #63–65 are now ready for review; #61/#62/#66 remain ready. Ready status does not imply approval or merge. All six PRs subsequently merged after operator authorization; see the integration record below.

## Finding — a later run can review the containing day's earlier date

The shell accepts a new run whenever the Trading Day is active and has no active run. `start_trading_run()` assigns `futures_day_label` only when it is empty, then passes that container label to the runtime as `review_day_label`. The Trading Day model validates ID/status ownership, but not whether the new run's historical reference belongs to that calendar day. `_load_review_cycles()` uses only the supplied container label to construct the observed Day/90m targets.

Affected locations at the reviewed source:

- `src/ict_cockpit/gui/trading_day_shell_widget.py`, `start_trading_run` (339–347, 383) and `load_state` (567–569);
- `src/ict_cockpit/gui/amdx_context_widget.py`, `_load_review_cycles` (218–245);
- `src/ict_cockpit/analysis/trading_day.py`, `activate_trading_run` checks ownership/status but not reference-date consistency.

Concrete source-level reproduction:

| Input/output | Value |
| --- | --- |
| Existing Trading Day label | 2026-10-08 |
| New Replay run's market reference | 2026-10-09 09:15 ET |
| Saved run-start context snapshot | `reference_market_time = 2026-10-09T09:15:00-04:00` |
| Expected containing Review cycle | `day:2026-10-09` |
| Current containing Review cycle | `day:2026-10-08` |

The case was reproduced by creating the real Trading Day/Run/context-snapshot objects, activating the new run successfully, and executing the exact `_load_review_cycles` function extracted from the published source. Minimal stand-ins supplied the combo/label/target methods so Qt was not required. This is a source-level cycle-selection reproduction, **not** a fresh native GUI test. No operator database or interpretation was changed.

The adapter can consequently supply an older valid cycle to the observed action for the newer run. The repository intentionally accepts explicit run-owned cycles for analysis; it cannot infer that the UI selected the wrong date. This needs correction before integrating #66. The ordinary same-date single-run checks 255–259 remain valid and accepted; they do not cover this additional case.

## Required correction and regression boundary

Resolve Review's date from the particular run's preserved original market context, rather than its latest advancing clock or an unchecked container label. `MarketContextSnapshot.reference_market_time` already preserves the supplied run-start reference, including a Not Configured provider, and is available independently of later clock refresh. Check its ownership/validity and define the legacy fallback explicitly. Missing or conflicting provenance must not silently select another date.

Keep the one-futures-day Trading Day contract explicit. The shell's ability to attach a different-date run is a related existing boundary gap; either prevent that combination through the canonical launcher or handle its historical provenance deliberately. Do not solve it by moving existing claims, rewriting the Trading Day label, selecting an expectation as a date/baseline default, or following today's clock.

The narrow follow-up needs native regressions for:

1. October 8 run followed by an October 9 run through the permitted launch path: reject the invalid container combination clearly or review the actual October 9 run; never show writable October 8 targets as its observation scope.
2. Live/Replay reference rollover after a run starts: preserve that run's reviewed date and in-flight target/reference.
3. Restart: recover the same run-owned date and committed working/observed profiles.
4. Older runs without the new source snapshot, and missing/malformed/conflicting references: preserve an explicit safe fallback or disable capture, without inventing interval history.
5. Retain all existing role/subtype/Unknown/applicability/no-op, stale-head, run/channel gesture and quiet Watch guarantees.

No correction is implemented by this review checkpoint. Restore the native test environment, run the focused cases and required full suite on the corrected source, then reassess the blocker. A source-only reproduction does not replace those checks.

## Reviewed contracts and evidence

| Area | Review result |
| --- | --- |
| AMDX/XAMD structure | A containing quartet owns four stable contiguous quarter identities; manual, implied and rule output remain distinct. Valid choices span both orders. |
| Working/observed revisions | Separate named policies/channels, compatible retention and contradictory retirement, no resurrection on clear, and honest unresolved X/Unknown/applicability. |
| Durable actions | Owned immediate transactions check scoped heads before action, store immutable receipts and reserve no-op identities. Original retries replay the original basis/result. |
| Review provenance | Explicit or null expectation references; no first/latest fallback; deliberately selected same-cycle basis carries through observed corrections. Source/pair/receipt commit atomically. |
| Reads and migrations | Review uses a consistent read snapshot; v38–41 migrations are additive and guarded. Earlier payload policies retain their replay meaning. |
| Watch/UI | Current working stack and position; no AMDX history/comparison option or launch route. Observed entry is Review-only, with direct X(C)/X(R), fixed orientation and scrollable content. |
| Definitions | Criteria/input/output/priority revisions retain their original basis; no actual classifier, published rule adoption, probability or competency/authorization effect is introduced. |

PR metadata, review submissions and inline threads were read for #61–66: no submitted reviews or inline threads existed at review time. This report is a local source review, not an independent GitHub approval. Main still points to `83d82323ca936dedf045027760d81a1cd7de76b1`.

| PR | Tested source | Recorded full result | Published head before this review | Base |
| --- | --- | --- | --- | --- |
| #61 | `6cf65d2` | 546 PASS | `4346c88` | main |
| #62 | `84167e9` | 587 PASS | `eb822bc` | #61 branch |
| #63 | `7a31f71` | 625 PASS | `d940138` | #62 branch |
| #64 | `e61c1aa` | 658 PASS | `1bf3933` | #63 branch |
| #65 | `d9d97dc` | 699 PASS | `d058215` | #64 branch |
| #66 | `0efa822` | 720 PASS in 1412.41s | `1fc19d1` | #65 branch |

For every PR, the published source/tests/tools were verified byte-equivalent through a Git diff restricted to later documentation changes. These are previously completed test results, **not six fresh runs**. The current source still matches the completed 720-pass suite; that suite lacks the newly identified different-date case. Checks 245–259 remain operator accepted with their existing evidence limitations.

Fresh review verification: all five existing CLI demonstrations completed successfully (foundation, persistence, Review pairing, Review persistence, observed revision); Python 3.10 syntax parsing passed. Qt/pytest are unavailable in the current scratch environment, so no fresh native/full-suite execution is claimed. Schema v41 and Alpha 0.7 remain unchanged.

## Integration recommendation

First correct and verify the #66 date-provenance blocker. Then assess the stack in dependency order **#61 → #62 → #63 → #64 → #65 → #66**. Preserve ancestry with merge commits; retarget each child to main only after its parent actually merges. Keep parent branches until dependent retargeting is complete. Recheck the actual resulting source/tree if any head, base or implementation changes.

This review performs no merge, retarget, source change or new operator acceptance. Comparison UI/research, primary 16:9 geometry, higher-order cycle mapping, shortcut assignments and broader Study presentation remain downstream. The immediate next slice is the date-scope correction, not a renderer expansion.


## Correction follow-up — 2026-10-12

Source `e12a2d4c4d4767f32dd13c3ea795ffab18531f78` implements the recommended run-owned period correction. `analysis/amdx_review_date.py` resolves a valid saved run-start reference using New York futures-day semantics; the mutable clock/expectation claims are never date substitutes. Missing retained reference can use the explicitly described legacy containing Day; malformed retained reference or absence of both sources disables capture. The heading hover explains its origin and a valid original reference differing from an old container. Changed date provenance cannot record an older in-flight target.

The canonical shell rejects a different-date additional run, or an undated existing container with prior runs, before process/TDA reset or run creation. It points to Complete Trading Day → Start New Trading Day. Same-date additional runs remain allowed. Native restoration of a previously accepted mismatched grouping now uses the run's valid original date without rewriting the containing Day or old claims.

Focused **77 passed in 784.90s**, covering 24 new cases (15 pure date / 9 native), normal-window restart and the existing working/observed gesture/failure paths. Full verification completed: **744 passed in 328.84s (5m29s)** across all 70 isolated module runs, clean exits/no warnings. Each module’s JUnit count was matched against the full collected node IDs, with no failures/errors/skips. No combined single-process full run is claimed; the focused group ran in one process. The native environment is restored (Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen); no separate Python 3.10 execution is claimed. A requested 1280×720 sandbox produced the existing 1280×876 minimum and was inspected. Source remains frozen during validation.

`AMDX_REVIEW_DATE_OPERATOR_GUIDE.md` provides one new operator check 260, NOT TESTED. Its retained separate native fixture deliberately constructs the older-label discrepancy only in synthetic data; it is not original operator data or a migration. Previous 259 records remain unchanged. Schema v41 / Alpha 0.7 / action and archive policies remain unchanged. No merge/retarget occurs. Reassess integration after full verification and this focused check.

**Developer reassessment:** the source-level date blocker is corrected and covered by passing native regressions, actual restoration, the preserved-reference fixture and the complete module-isolated suite. The implementation finding is resolved at `e12a2d4`; check 260 is now PASS for the targeted operator path; dependency-order integration can be reassessed. Previous accepted results are not reinterpreted. All verification processes have exited; no merges occurred.


## Operator correction trial — 2026-10-12

Operator guided report, 2026-10-12 (America/Denver): upper Trading Day advanced to October 10 while Observed AMDX remained October 9; NYAM 90m Q3=M was entered and the profile was XAMD. After window-X close and same-directory reopen, the date remained October 9; selecting NYAM restored XAMD and Q3 entered without another phase choice. After Conclude Trading Run, Start Another Trading Run created no second run and displayed: "Run not started - selected reference belongs to Trading Day 2026-10-13. Complete the current Trading Day, then choose Start New Trading Day". The October 13 request is the live reference after restart, not a change to the saved Review date. The heading-tooltip inspection was not separately reported; no operator hover acceptance is inferred.

The date/rollover/restart/launch-guard acceptance gap is closed. Earlier pending-trial statements describe pre-trial checkpoints. Source/tests/tools remain byte-identical to `e12a2d4`; retain its completed 744-pass module-isolated result rather than claiming a fresh application run. Reassess #61 → #62 → #63 → #64 → #65 → #66 integration with preserved ancestry and current-head verification; all PRs remain ready/unmerged, and no merge/retarget occurs in this documentation checkpoint. Final rendering and comparison exploration remain deferred.


## Integration completed — 2026-10-12

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
