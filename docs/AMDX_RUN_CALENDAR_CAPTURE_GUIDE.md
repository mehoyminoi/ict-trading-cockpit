# Immutable run context and atomic calendar updates

Current native integration is documented in `AMDX_SHARED_NATIVE_GUIDE.md`; this document retains the scope and evidence of its earlier foundation checkpoint.

This slice implements the run binding/capture and transaction primitives from `AMDX_MASTER_CALENDAR_CONTRACT.md`. Native Lab/TDA/Watch and existing decision/evidence/Observed Review actions are not rebound yet. There is no new visible workflow or operator trial in this backend checkpoint.

## Implemented data and actions

Schema v44 adds immutable `amdx_run_binding`, `amdx_run_capture` and `amdx_run_calendar_command` tables. Foreign keys and deferred launch/capture receipt references require complete committed records, with instrument/master ownership and capture-parent run scope retained. Update, delete and replacement triggers protect all three histories. The additive migration preserves every actual v43 source row and gives no legacy run an instrument, binding or capture.

`AMDXRepository.run_calendar` provides:

| API | Result |
| --- | --- |
| `prepare_launch(run, instrument=..., reference=..., snapshot=...)` | Freeze new unsaved run storage values and the inspected master stack; optionally retain the TDA's previously inspected snapshot. |
| `launch(prepared, operation_id=..., capture_id=..., recorded_at=...)` | Atomically save the new run, immutable instrument/master binding, original capture and complete operation receipt. |
| `get_binding(run_id)` | Read original launch identity/basis; unbound legacy ownership is explicitly unknown. |
| `prepare_capture(run_id, reference=...)` | Consistently freeze run metadata, original binding, inspected working stack and current capture parent. |
| `capture(prepared, ..., reason="ContextUse" or "CycleChange")` | Append the exact inspected context for an operational use without a phase revision. |
| `revise(prepared, master_target, ..., role=..., subtype=...)` | Atomically append the maintained working calendar command and the run's resulting capture/receipt. |
| `get_result(operation_id)` | Reconstruct the original immutable capture/result for recovery, including after later edits or run conclusion. |
| `export_archive(run_id)` / `read_run_calendar_archive(value)` | Export and validate the complete original launch/operation/capture chain without requiring the source database or today's temporal resolver. |

The APIs are integration primitives. Native controllers will call them automatically at launch, accepted working input and consumption of changed context; this slice does not add per-quarter Save/Publish or timer/render logging. Capture IDs and operation IDs are distinct and reserved against competing action namespaces. Current v0 operates on the maintained Expected/working channel. Observed Lab data stays independently scoped; the existing higher Observed run-start guard is unchanged.

## Preserved context

Each packet contains exact original run/master identity, immutable launch basis and the current operation's frozen raw run metadata, numeric-offset market reference, actual recording time/reason, complete identified stack and original ledger content. Null heads remain explicit absence. Closed references retain five higher rows plus explicit unavailable day/session records; open references retain all seven identified rows. Unknown/distortion/unassigned interpretation/position states retain their existing meanings. No labels are borrowed from another instrument/channel or fabricated from a legacy flat map.

A later calendar correction changes current maintained heads. It does not fill an earlier missing head, overwrite a captured revision or replace the selected basis of an earlier run. Mutating ordinary run metadata also leaves packets unchanged. The original launch packet and later operational captures are separate records with an immutable parent chain.

Known saved run-start reference must match the launch calendar reference; malformed/contradictory values reject rather than being overridden. If original metadata lacks that reference, its absence stays in the raw source and the deliberate explicit launch reference is retained separately. This does not enable unsupported old higher Observed entry or infer a historical timestamp from a day label. References with different repeated-hour offsets remain distinct captured bases.

Working edits default capture origin from the frozen environment: Historical Backtest/Replay use HistoricalEntry; Live/Forward Test use ForwardEntry. An explicit CaptureBasis may be supplied. Environment/purpose, original evidence/definition/as-of references and unknown availability remain intact; neither default proves a contemporaneous prediction or a leak-free backtest. Free-text definition references do not imply complete embedded rule definitions. No classifier, rule adoption or provider refresh occurs.

## Transaction and retry boundary

Existing run serialization/SQL mappings are unchanged, but the writer now exposes frozen storage values and a helper used under the owned launch transaction. Existing catalog request construction/revision logic is similarly extracted for a shared owned transaction. The public old save/revise paths retain their behavior. The new operations own `BEGIN IMMEDIATE`; they reject a pending caller write and roll back the new run/binding/capture or calendar-command/capture as a unit on failure.

New requests revalidate the full inspected master vector, run metadata and parent capture under that lock. A changed TDA/master head, run basis or capture parent rejects until reload, instead of substituting a newer thesis. Working target instrument/binding/channel/reference/head is independently validated. Read-only inspection/export honors a caller transaction without committing it.

An exact committed retry validates the complete original request and returns its original capture/result before checking today's resolver or heads. Changed request under the same operation ID rejects, as does attaching an existing manual command as a new run operation. An unchanged entry still retains its original no-op command receipt and resulting context; it does not fabricate a phase revision. New context consumption on a concluded run rejects, while original retries/archive inspection remain available.

Standalone archive validation checks run/master identity, original metadata, capture absence/inference/temporal boundaries, exact edited target and command/result replay, source availability, complete launch/parent chain and operation/capture identities. Retained context reconstructs without resolving through today's calendar. Existing v1 collection and master archive meanings remain intact. V0 embeds original ledger content in packets for self-contained replay; compaction and large-history performance remain downstream work.

## Completed evidence and next work

Source `c822d0469e28a788d36caae82ec7b70b28794f24`, PR #72, `feature/amdx-run-calendar-capture-v0`, parent #71 `6c7362b`. Focused **310 PASS in 14.39s**, including **58 new cases**. Complete **1028 PASS across all 81 isolated module processes in 266.04s**, collection-matched JUnit counts and clean exits with no failures/errors/skips or pytest warnings. All regression processes exited; no combined single-process full run is claimed. Python 3.10 grammar passes; runtime Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen.

Actual archived-v43 migration/failure preserves all original rows and binds no legacy runs. Tests cover launch/edit rollback, two runs sharing a calendar while retaining independent packets, competing launches/consumers and exact retries, stale TDA/run/head/parent basis, cross-asset/action identity rejection, no-ops/unresolved X, SQL immutability, environment capture defaults, known/missing/malformed launch reference, repeated-hour offsets, archive tampering, separate-process reopen and actual previous run-writer serialization equality. Existing native Lab/TDA/Watch/Study, run Review and E6 compatibility regressions pass.

Next bind native Lab/TDA/Watch to the master and these storage primitives, preserving the quiet Watch/full Lab views and explicit legacy adoption/recovery. Existing decision/evidence consumption must be connected under its own owned operation boundary; an isolated ContextUse packet is not a claim that those existing actions already consume it. Retrospective legacy-run assignment/import and new Observed Review coupling are not implemented here. #67–72 remain unmerged; main remains `6dd43c8` (v41), Alpha 0.7. GUI/tools and all 264 smoke records are unchanged. No new operator trial or terminal action is required for this backend slice.
