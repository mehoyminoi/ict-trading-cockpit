# Shared AMDX calendar and captured run context

**Status: implementation contract following the operator's shared-calendar clarification and authorization to proceed, 2026-10-13. Not an implemented migration or consumer binding.** Product ownership follows `AMDX_MASTER_CALENDAR_CLARIFICATION.md`; the detailed transaction and capture design below is the developer's implementation specification, not a claim of additional operator acceptance.

One maintained calendar per instrument supplies Lab, TDA and Watch. Areas and Backtest/ForwardTest/Live purposes are views and provenance, not default calendar owners. Run captures preserve the basis actually used without making a separate everyday calendar for each run. MNQ is the initial instrument; NNQ remains a distinct identity.

## Ownership and supported meaning

Resolve the instrument through one canonical master binding. The binding identifies a stable existing ledger owner, rather than renaming or copying all catalog commands. Its creation/adoption and any later supersession have explicit identities and actual recording times. At most one current master binding exists for an instrument. A resolved binding is part of every inspected/editable scope and every captured run packet.

Use a dedicated master-owner creation/adoption operation. The existing `Catalog.purpose` only supports Backtest/ForwardTest, so creating a normal master with a fabricated purpose is not an acceptable shortcut. Version the new owner metadata/API while preserving exact existing v42 payloads and archive replay. A compatible existing ledger may be deliberately adopted, with its former purpose retained as provenance. Neither the first nor the most recently used collection is automatically designated master.

No catalog-purpose or destination chooser belongs in the ordinary entry path. On a clean database, selecting the default MNQ context can establish its empty master atomically. Existing collections/runs require the transition policy below. Separate experimental interpretations remain optional explicit alternatives; they do not silently replace the maintained record or feed Watch.

Scope is instrument, master-binding revision, ledger owner, supported branch, semantic channel and identified cycle. Cycle identities are reusable across instruments; cycle ID alone is never a cross-instrument claim key. The existing catalog adapter implements only its working branch. An alternative branch requires a supported versioned action before it can be written through the new interface.

| Normal operation | Semantic record | Display/capture behavior |
| --- | --- | --- |
| TDA/Watch working interpretation | Expected, working branch | Shared maintained working head for each pertinent occurrence; run expectations are exact captures of those heads. |
| Lab historical assessment/backfill | Observed, working branch | Shared observed head for the studied occurrence, independent of its working expectation. |
| Lab deliberate working-thesis study | Expected, working branch | Explicit working context; never silently substituted for Observed or represented as a contemporaneous prediction. |
| Run Review | Captured Expected basis and permitted Observed assessment | Reconstruct exact run captures; preserve an explicitly selected comparison basis without a first/latest baseline. |

“Expected” is the existing storage channel for working interpretation; it does not certify predictive knowledge. “Observed” does not certify correctness. Present the meaning of the operation plainly; normal Watch retains its existing working default, and normal historical Lab entry retains its existing observed default. Do not introduce a mandatory channel decision on every edit. Inspecting the other meaning is explicit, and a missing head remains missing rather than borrowing the other channel. A Lab backfill becomes available wherever that occurrence and observed record are inspected; it does not rewrite an earlier working expectation.

Mutable Trade Plan criteria and optional rule alternatives retain exact definition revision/input basis where available. An unspecified free-text reference is not a complete embedded rule snapshot. Classifier execution, rule adoption and empirical comparison remain separate actions; calendar ownership supplies the shared record, not an automatic interpretation policy.

## Shared views and captured views

The shared current view resolves pertinent occurrences at an explicit aware New York market reference and returns their exact maintained heads. Lab can inspect any supported historical reference without a rolling retention cutoff. Watch chooses the relevant current slice and keeps higher context quietly available; Lab retains the spacious full stack and adjacent detail. “Calendar” does not require a month-grid renderer. Closed/distortion/unassigned states remain distinct from an identified occurrence without an entry and from a read failure.

The captured run view resolves an immutable capture packet, not today's master heads. Switching between current study and a captured run is explicit in Lab/Review. Opening a run for Review must not silently refresh its expectation from the master. Returning to a live working view reads the master; the run's original capture remains intact.

Navigation, rendering, passive clock refresh, read-only inspection and archive export create no phase revisions, captures or comparisons. Other accepted calendar edits may invalidate/refresh a live view; refresh does not itself mean the run used that new basis. A prepared gesture stays pinned to its inspected instrument, binding, channel, cycle, quarter, reference and head. A clock tick cannot retarget it. Scope changes cancel the gesture; concurrent head/binding changes reject its new action until deliberate recovery.

## Run identity and capture packet

New runs persist instrument identity and canonical binding as part of launch. Initially use the valid MNQ launch context; there is no collection destination choice. A loaded legacy row's absent instrument remains unknown. Neither current preferences, the latest TDA nor a Catalog constructor default supplies historical ownership proof.

A run capture has a stable operation/capture identity, run and instrument identity, master-binding revision, capture reason, actual recording time, studied market reference with offset, environment/purpose and the versioned resolver/action basis. Retain all supported stack rows even if Watch displays fewer. Each identified row records cycle/quarter identity, semantic channel/branch, exact head revision or explicit absent head, and the original content needed to reconstruct it. Preserve unavailable/nonidentified rows with their reason. A null head is meaningful and must not later be filled from a new calendar entry.

The packet retains original claim/action identities, receipts including no-ops, capture availability/evidence/definition basis and required temporal/definition/input payloads. Availability and recording time are different facts. Unknown availability stays unknown; a backfilled 1985 entry recorded in 2026 is not evidence that it was known in 1985. Declared ForwardEntry or a retrospective availability timestamp alone does not prove a leak-free backtest. Ordinary historical study may inspect the current maintained record, but any claim of historical prediction requires the retained information basis. Broad historical as-of query reconstruction remains separate.

The launch packet is immutable. Later operational captures append with their own identities/reasons; they never replace launch or change an earlier comparison's selected basis. Captures occur automatically at run launch, an accepted run-linked working edit, and before a subsequent decision consumes a changed cycle/head vector. No separate Save/Publish action is required. Identical already-captured decision basis can be reused; an actual no-op input still retains its original command receipt. Do not capture every render/timer tick or deduplicate solely by displayed AMDX letters.

A TDA context used at launch is pinned as a versioned source vector. If relevant master heads/binding change before launch, reject/reload the prepared launch instead of substituting a new thesis basis silently. Where there is no saved TDA vector, launch explicitly captures its own current basis and does not claim to reproduce an earlier analysis.

After an external Lab edit, a Watch refresh may show the new maintained working head, while earlier run captures still show the old one. The next operation that consumes that basis records the exact new vector automatically. A decision/evidence action must refer to the capture it actually consumed; a passive current view is not retroactively attached to an earlier decision.

## Writes, consistency and retries

Read a complete stack/head vector and its binding in one consistent database snapshot. Never assemble a capture from independent reads of individual layers while another writer changes them. Persist capture rows as immutable append-only records; ordinary `TradingSessionRunRepository.save()` currently upserts mutable run metadata and must not overwrite them.

For a run-linked working edit, the shared calendar command and the run's new capture/operation receipt commit in one owned transaction. For launch or a decision that consumes existing data, validate the prepared instrument/binding/head vector and persist its capture plus consuming operation in one owned transaction. Do not wrap the current independently committing catalog API/run `save()` as two sequential writes. Extract/reuse locked action helpers under a single transaction owner when implementing the integration.

Lab-only backfill commits a calendar command with provenance and no fabricated run. A permitted run Review assessment uses an explicit observed action and retains its selected run basis; if it also updates the maintained observed record, both writes share one operation/transaction with separate provenance. Retrospective Review never replaces the maintained working expectation. The existing higher Observed run-start guard remains enforced until its separately specified bounded Review reference/proof action is implemented; shared ownership is not permission to bypass it.

Any new bound-write/capture failure rolls back the whole new operation. A committed write followed by a failed read is reported as committed with refresh unavailable, preserving the current recovery distinction. UI input remains disabled until deliberate Reload after stale/read/write errors. Read failure is not an empty calendar.

An exact committed retry returns the original complete receipt/capture, even if the calendar, resolver, clock or binding has changed. Changed payload under the same operation ID rejects. Reassociating/adopting already-recorded data is a new operation, not a retry that attaches it to today's owner. Reserving command, capture and consuming-operation identities prevents reuse across action types. No background retry silently refreshes a target or reorders history.

Archives must include the resolved instrument/binding provenance and sufficient original content to reconstruct captured heads without access to the source database. Validate ownership, temporal identity, exact result/receipt replay, absent-state records and supported versions before exposing an archive. A list of revision foreign keys alone is insufficient. Do not rerun today's criteria, provider queries or resolver in place of retained payloads during reconstruction.

## Transition from existing data

An additive migration preserves all v42 rows byte-for-byte and leaves legacy run instrument/binding absent. Keep old catalog and run archives readable. New master metadata and capture payloads require their own versioned envelope; schema number and exact SQL are assigned by the implementation, not claimed here.

Where existing MNQ collections exist, deliberate one-time adoption identifies the maintained ledger; optional batch association/adoption can reduce clerical work. Multiple candidates do not select a first/latest winner. Legacy instrument assignment retains assignment source and actual time, rather than rewriting an original capture. Known MNQ/NNQ mismatch rejects.

Older run-owned claims and conflicting collection heads remain immutable independent evidence. Importing/adopting a judgment into the maintained calendar requires an identified new action with preserved original source and current adoption time; do not re-time, blindly merge or delete source records. A concluded run may be inspected/associated without reopening its process. Flat legacy QT maps retain their raw period keys and unknown basis; no synthesized quartet anchors appear.

Normal clean-data use has no repeated migration choice. Missing/malformed binding or ambiguous legacy ownership yields an explicit recovery state rather than silently creating another primary calendar or redirecting an edit. Once binding is resolved, ordinary Lab/TDA/Watch interaction shares it automatically.

## Required implementation evidence and next slice

| Case | Required result |
| --- | --- |
| Two normal MNQ workspaces | Same canonical owner; no Backtest/ForwardTest destination selection. |
| Historical Lab observed backfill, then another area's observed inspection of that occurrence | Exact same revision/content; other periods and Expected remain independent. |
| Run captures R1; a later calendar correction creates R2 | Current view uses R2; the run's earlier packet reconstructs R1 or its explicit absent head. |
| Other writer changes one head while a seven-layer capture is prepared | Consistent single snapshot followed by stale validation; no mixed or silently substituted vector. |
| Bound edit/capture or launch/consumer write fails | Whole new operation rolls back; no orphan master edit, capture or decision. |
| Exact committed retry after newer heads/binding exist | Original receipt/capture returns; different request with same ID rejects. |
| Same letters, different revision/criteria or a no-op receipt | Preserve identities/basis; do not conflate evidence from visual equality. |
| NNQ selected or an old run has unknown instrument | No MNQ head borrowing or automatic historical asset assignment. |
| Fresh/migrated/reopened database and standalone archive | One master, preserved source rows, exact reconstructable run packets and explicit unknowns. |
| Passive navigation, mode/clock changes, comparison inspection | No writes, provider refresh, automatic baseline or Watch history panel. |

Implement the canonical master binding and shared read/target facade first, including versioned owner metadata, deliberate legacy adoption and focused actual v42 migration/reopen/concurrency tests. Then add immutable run instrument/capture identity and the owned write/capture helpers before rebinding native consumers. Do not advertise cross-area sharing until Lab/TDA/Watch are actually bound and the above evidence passes. Final renderer, bulk ingestion/performance, broad as-of queries, classifiers and Study-first startup remain separate.

This checkpoint changes documentation only: runtime source remains `678e9a0`, schema v42 / Alpha 0.7, and all 264 smoke records are unchanged. Retain prior 97-focused/936-complete validation; it is not a new validation of this proposed integration. The disposable existing-ledger probe and document checks recorded in project state verify reuse boundaries only. No new user smoke trial or merge is requested.
