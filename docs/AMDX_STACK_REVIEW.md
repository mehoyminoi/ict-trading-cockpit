# AMDX stack review — 2026-10-12

Reviewed published checkpoint `1fc19d1b07195bc15b1d91670de9e9377e12f319`, application source `0efa822c5924c35ff6f654e649daacd5c237dbde`, against the accepted working/observed action, persistence and Watch/Review boundaries.

**Result: one integration-blocking finding in PR #66.** No additional blocker was found in the reviewed domain/storage contracts. PRs #63–65 are now ready for review; #61/#62/#66 remain ready. Ready status does not imply approval or merge. All six PRs remain unmerged.

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
