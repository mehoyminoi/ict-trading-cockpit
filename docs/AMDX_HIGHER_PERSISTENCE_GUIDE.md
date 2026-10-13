# Durable higher AMDX context

The `AMDXRepository.context` adapter now reads and records identified higher quartets through the existing v41 storage and revision transactions. It covers 16-year, quadrennial, yearly, monthly and weekly working/observed interpretations. Normal entry keeps the original one-choice/no-op/clear/applicability policies; it adds no independent interpretation store or migration.

This backend follow-up is `feature/amdx-higher-persistence-v0`, PR #68, stacked on the pure identity/projection PR #67. Main remains the accepted `6dd43c8` baseline. Explicit higher Review-period selection is now proposed in [the selection contract](AMDX_HIGHER_REVIEW_PERIOD_CONTRACT.md), followed by scope-proof implementation and native overview/editor binding; this checkpoint adds no controls or operator smoke test.

## Read and prepare

`amdx.context.load_stack(run_id, reference=explicit_market_reference)` reads working context. The reference must be timezone-aware and deliberate. `load_stack(run_id, channel="Observed")` reads the saved original `reference_market_time` from that run's market-context snapshot; a caller clock is rejected. Neither read consults a provider or the wall clock.

A snapshot holds the projection and current optional pairing heads within one SQLite read snapshot. Legacy expected/observed maps are read exactly as stored, without model normalization, missing-field defaults or conversion into anchors. Parent/child and different run/channel/branch interpretations stay separate.

`prepare_target(snapshot, level, position)` freezes run, working/observed channel, containing cycle, selected quarter, original reference and inspected heads. Omit position to use the applicable active higher quarter. Friday/fifth-week/pre-first-Monday/closed states without an active quarter require deliberate Q1–Q4 selection; they are never converted to a fifth anchor or automatic Not Applicable answer. Analytical alternatives are readable, but manual revision stays in the working branch. The adapter prepares higher targets only; existing intraday controls/actions retain their path.

## Record through the shared action

```python
from ict_cockpit.analysis.amdx import Role

context = amdx.context.load_stack(run_id, reference=explicit_market_reference)
target = amdx.context.prepare_target(context, "year", 3)
result = amdx.context.revise(
    target,
    claim_id=unique_command_id,
    anchor_id=unique_anchor_id,
    role=Role.M,
    source_ref=technician_input_source,
    recorded_at=explicit_recording_time,
)
```

These names are caller-supplied data, not a runnable operator smoke command. The one accepted Q3=M choice records XAMD with its entered anchor and implied siblings. X(C)/X(R), Unknown, whole-quartet Not Applicable, clear and compatible/contradictory anchor handling retain the existing versioned policies. Pass no anchor content for clear. Observed requests also supply a distinct comparison command identity; this keeps the existing internal atomic receipt/pairing contract, without requiring the technician to choose a comparison or adding a Watch control.

The adapter acquires the existing owned `BEGIN IMMEDIATE` transaction before validating new temporal targets and the saved original observed reference. A different/malformed/missing saved reference rejects the new request before any cycle/claim/pair/receipt commit. Current clock changes do not affect a frozen target. The shared scoped-head checks reject concurrent edits and changed pairing selection. SQL failure rolls all new records back; retry is deliberate.

Exact committed retries validate and return the immutable original receipt/basis/result, including nullable no-op results, even if a later current reference or resolver changes. A reused identity with different content is rejected. New actions use the current canonical definition; an old registered payload is not silently redefined. Existing action bodies are reused through transaction-owned helpers, with their policies and serialized request meanings unchanged.

## Restore and boundaries

Reopening the connection, a separate Python process and the normal MainWindow retain higher claim/profile/reference meaning. Ordinary run state and legacy maps are not rewritten by higher entry. Consistent WAL reads keep saved run reference, source history and pairing heads in the same snapshot; reads preserve a caller's transaction, while writes refuse an unrelated pending transaction.

This v0 observed read selects the run-start higher occurrences. A run beginning before calendar midnight can cross into another Yearly quarter while its futures-day label stays the same; working entry can record both identified occurrences through explicit references. Reviewing an additional occurrence needs an explicit period-selection contract before native binding. This adapter does not silently pick a later current clock or use an expectation as a reference fallback.

Higher observed capture needs an actual saved starting timestamp. A saved containing Day alone cannot tell which side of calendar midnight/futures rollover governed higher context. Missing/malformed original references therefore make this adapter unavailable; the already accepted intraday legacy-Day fallback remains unchanged. Future UI should explain this availability and retain legacy context rather than inventing a higher anchor.

The backend owns the requested immutable data scope, not the operator's current process permission. Future UI/shortcut binding must recheck its active run/channel/selection through the gesture, use the prepared target and present stale/failure recovery. This is not a historical as-of query, classifier, comparison-exploration surface or final renderer. Study-owned selection and explicit historical information basis remain separately designed work.

## Verification

Focused **210 passed in 8.58s**, including **50 new cases**: all five levels/both channels, exact maps and untouched run rows, connection/process/normal MainWindow reload, saved reference/UTC normalization, write-lock reference race, scoped heads/pair basis, rollback, competing writers, consistent WAL snapshots, caller transactions, canonical target/role rejection, original subtype/uncertainty/applicability/clear and original nullable/obsolete-definition retries. Complete suite: **839 passed in 447.51s** across all 72 isolated module processes, with clean exits and no failures/errors/skips or pytest warnings. Every JUnit count matched collection; no combined single-process full run is claimed. All test processes exited. The actual previous `e27bd31` v41 reader also restored the new higher records/pair without changing any of seven table row sets. Python 3.10 grammar is checked; execution is Python 3.12.

Source `6c993c73000f354ce0cbdf3059ad5ea89376fd92`. Schema v41 / Alpha 0.7, old serialized action meanings, native controls and all 260 smoke records remain unchanged. No new operator trial is requested before native binding exists.


## Repeated-hour correction and final verification

Source `9c476df520efec8a7e50a04c015e0de4da78d850 fixes the guard's same-zone datetime equality: the two repeated-hour folds are distinct UTC instants. Quarter/Claim/Comparison normalize in memory to the already serialized numeric-offset representation, preserving ISO payload content while making repeated-hour chronology/replay exact. Five new regression cases cover changed-source rejection before writes, immutable original retry and quartet/claim replay in both channels.

Final focused **313 PASS in 13.20s**; complete **844 PASS in 508.64s across 72 isolated module processes**, clean exits, no failures/errors/skips or pytest warnings and collection-matched counts. All processes exited. Python 3.10 grammar passes; runtime remains Python 3.12. Previous 839-pass/old-reader evidence above describes its earlier source, not another final execution. Schema v41, Alpha 0.7, native controls and all 260 smoke records remain unchanged.

The explicit Review selector and durable scope proof in the new contract are proposals only. This adapter still accepts higher Observed context from the preserved original run-start reference; it has not been loosened to accept arbitrary historical references. No new operator trial or merge is requested by this backend checkpoint.
