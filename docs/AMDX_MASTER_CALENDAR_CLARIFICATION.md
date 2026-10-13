# One maintained AMDX stackup calendar

**Status: explicit product clarification, 2026-10-13. Shared ownership/rendering integration is not yet implemented.** The operator meant one maintained AMDX stackup calendar, usable across Lab/backtesting, TDA, Watch and Review. Purpose-specific collections were a developer interpretation of “catalog”; they are not the intended primary ownership model.

The master calendar is the continuously maintained, revision-preserving AMDX timeline for an instrument. Historical backfill and current interpretation contribute to this same underlying timeline. Different cockpit areas present and operate on the relevant slice, without requiring the technician to choose or synchronize separate Backtest/ForwardTest catalogs.

## Shared data, different presentations

| Area | Intended use of the shared calendar |
| --- | --- |
| Lab | Backfill earlier periods across all layers, inspect the full stack with nearby detail, and investigate definitions/evidence. |
| TDA | Read the same contextual stack while building the current thesis; deliberate permitted edits update its maintained interpretation. |
| Watch | Show a quiet view of pertinent cycles/current position and allow efficient permitted updates to the same calendar. |
| Review | Reconstruct the run's captured context and later judgments without replacing what was known/recorded at the time with today's calendar state. |

Initially MNQ is the one default instrument/calendar. Instrument identity still belongs in storage so NNQ or another instrument can be added without mixing periods. The normal workflow needs no catalog-purpose chooser or run-to-catalog destination selection. Backtest/forward/live/historical origin and rule/definition basis are retained provenance or analytical filters, not separate primary calendars.

“Calendar” denotes the maintained nested temporal record: 16-year, quadrennial, yearly, monthly, weekly, session/day and 90-minute occurrences, with finer layers added when supported. It does not require a conventional month-grid renderer. Existing cycle/quarter identities, distortion states and coupled role rules remain applicable.

## One owner without rewriting history

Use one canonical calendar owner per instrument. Its supported semantic channels and interpretation branches stay explicit; cockpit area or study purpose must not create another owner for the same maintained calendar. Expected working judgments, later observed/backfilled judgments and alternative rule interpretations do not become interchangeable simply because they reside in one calendar. Existing accepted Expected/Observed independence and immutable revisions remain valid.

Which semantic channel a particular operation displays/updates must be explicit in the shared action/view contract; do not solve presentation defaults by silently merging channels or choosing a latest/first comparison baseline. Ordinary use should not require the technician to manage multiple catalogs to access that distinction. Purpose-specific experiments may retain optional alternatives, with explicit adoption rather than automatic replacement of the maintained interpretation.

An accepted Lab backfill is saved once against the instrument's identified occurrence and appropriate semantic record. Other cockpit views can retrieve that same entry when inspecting that occurrence. A permitted current Watch update appends a calendar revision and updates relevant current views without a separate Publish/Export/Save. Run records retain the revision identities/snapshots actually used or captured through the action, with actual recording time, studied market time and known/unknown information basis intact.

For example, a Lab entry for MNQ's 1985 yearly Q3 must remain available when TDA or another Lab view inspects that period. Watch today shows today's pertinent stack rather than that old year. A later correction to an occurrence changes the maintained current judgment, while an earlier run still reconstructs its captured judgment. Multiple runs' frozen expectations remain evidence, not competing default calendars or automatic latest-value winners.

This preserves the earlier provenance insight without making separately run-owned judgment sets the primary source for current calendar use. A run reads/captures the calendar; it does not need an isolated everyday AMDX calendar that must later be manually attached to a purpose collection.

## What can be reused and what needs correction

Reusable foundation: stable instrument-aware collection metadata, temporal identities, aware timestamps/DST handling, coupled AMDX/XAMD actions, legal quarter choices/direct subtype controls, immutable revision/no-op receipts, archive validation, scoped stale/transaction handling and the native full-stack/adjacent editor.

Current limits: the v42 catalog owner is a user-created collection, allowing separate collections on the same instrument; the native Lab creates/selects those collections. TDA/Watch still use their run-owned AMDX path and do not automatically read or update the Lab collection. There is no canonical instrument-to-master mapping or run snapshot-reference integration yet. Thus the desired shared behavior is achievable from this implementation, but is not already delivered end to end.

An actual disposable v42 check verified that one collection exposes the same recorded yearly backfill at multiple reference points, while another purpose collection has an independent empty head. This demonstrates that temporal identity/history are reusable and that owner selection/consumer binding is the boundary to change. It does not demonstrate current shared TDA/Watch behavior.

Recommended next implementation:

1. Establish a canonical instrument/master-calendar mapping and a shared read/action interface, retaining existing ledger identities/records.
2. Make the normal Lab workspace open the instrument's master calendar; remove purpose/collection management from the primary entry flow. Keep explicit experimental alternatives separate from default use.
3. Bind TDA/Watch to that same owner and appropriate semantic context, while recording exact calendar revision references/snapshots for runs and guarding scope through each gesture/transaction.
4. Retain historical capture provenance and address existing run/collection data through an explicit migration/association policy. Conflicting legacy heads are preserved; no blind newest-value merge, deletion or asset guessing occurs.

The detailed shared write/snapshot/channel contract comes before changing persistence. New run instrument identity remains needed; older unidentified assets may need a deliberate batch assignment. The collection-destination-at-launch and run-source-only collector design in `AMDX_RUN_CATALOG_LINK_CONTRACT.md` is superseded as the primary model and must be revised before implementation. Its immutable source/receipt/archive/availability principles remain useful for legacy import and run reconstruction.

## Acceptance and current state

Checks 261–264 remain PASS for the tested native entry/subtype/historical occurrence/restart behaviors. Those results do not accept separate purpose catalogs as the final architecture or the current controls as the final renderer. No runtime, schema, action policy or data was changed by this clarification. Source remains `678e9a0`, schema v42 / Alpha 0.7, with the completed 97-focused/936-complete evidence retained. All 264 smoke records are unchanged.

Next is the shared master owner plus run snapshot/write contract, replacing the earlier collector-first plan. No new smoke trial or terminal action is required for this design correction.
