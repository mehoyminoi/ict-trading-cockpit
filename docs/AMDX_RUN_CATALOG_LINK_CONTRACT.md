# Preserved run captures in the AMDX catalog

**Status: concrete linkage proposal, not an implemented collector or migration.** The operator authorized continuation after syncing the accepted native Lab checkpoint `b91b344`. This contract defines the next integration before changing storage or run launch. Manual historical catalog entry remains implemented and accepted for checks 261–264.

The recommendation is to associate a run with an instrument/catalog once, then make its accepted AMDX history available automatically as a **run source within that catalog**. Keep original run ownership and timestamps. A link must not overwrite the manual catalog profile or turn multiple runs' different judgments into one latest-value answer.

## Superseded primary ownership direction — 2026-10-13

The operator clarified that “catalog” means one maintained master AMDX stackup calendar used across Lab, TDA and Watch, rather than separate purpose collections. The collection-destination-at-launch/run-source-only collector proposed above must not be implemented as the primary workflow. `AMDX_MASTER_CALENDAR_CLARIFICATION.md` replaces that next-step direction with a shared instrument/calendar owner and run capture references/snapshots. Original ownership, immutable receipts, explicit assets, unknown availability and archive-preservation principles below remain useful for transition/import/reconstruction. This older proposal introduced no collector or migration.

## Findings from the current source

`TradingRun` and `trading_session_run` currently have no saved instrument field. The separate TDA record has an instrument, but there is no demonstrated immutable run-to-that-record instrument relationship. The latest TDA, current launcher fields and the catalog's MNQ default cannot establish an older run's asset.

Run AMDX scope is `(run, branch, channel, cycle)`. Manual catalog scope is `(collection, instrument, working branch, channel, cycle)`, with a tagged catalog owner in the shared pure engine. Their identical temporal cycle IDs do not imply identical interpretation ownership. Current catalog commands preserve their own requests/results and capture basis; run receipts, pairings and evaluations remain in the run stores.

An actual disposable v42 database confirmed two runs can hold XAMD and AMDX for the same yearly cycle while a manual catalog holds its own independent XAMD head. Validated scoped source reads left every row in seven inspected run/AMDX/catalog tables unchanged. The run model has no instrument field, and the schema stayed v42. This verifies the ownership problem against existing code; it does not implement or validate the proposed linker.

## Instrument association without a recurring publication task

For future runs, recommend a visible instrument identity at launch, initially defaulting to MNQ, persisted as the run's instrument snapshot before capture. A new run must receive its instrument deliberately from that launch context; model/database defaults for loading older rows remain empty. This avoids retroactively labeling old data MNQ. An eventual NNQ key stays distinct, with no automatic instrument equivalence or feed/contract-roll inference.

Associate the collection at launch using a remembered valid default. Make instrument/catalog compatibility visible and validate it before resetting/creating a run. Do not add a per-quarter Publish, Export, Save or end-of-day synchronization obligation. Once bound, accepted capture accumulates through the shared transaction. Watch continues to present current orientation and efficient input, without a catalog history/comparison panel or route.

Older runs lacking instrument identity need an explicit assignment in Lab/Review. Allow a deliberate batch assignment for selected runs so this does not become repeated clerical work. Retain the declared instrument, assignment source/note and actual assignment time separately from original source data; a retrospective assignment is not an original instrument snapshot. Missing assignment means unavailable automatic instrument grouping, not guessed MNQ. Contradictory known identity/catalog asset rejects the link. A later correction retires/supersedes association through explicit append-only provenance, rather than rewriting original run or interpretation rows.

The catalog purpose Backtest/ForwardTest remains organizational context. Linking a Live, Forward Test, Replay or Historical Backtest run retains its actual environment/purpose; it does not silently convert it to the collection's purpose or certify contemporaneous prediction.

## What a catalog link contains

Keep an identified source association and append-only coverage records. Retain collection/instrument, original run ID, binding/assignment revision, source policy, linked-at time and the exact captured source basis. Original claims remain run-owned; do not replay them as newly entered catalog commands or replace their recording times with import time.

Coverage must include changed interpretations and original no-op/clear receipts, with their immutable request/result identities, scoped heads and action policies. Preserve existing comparison provenance without choosing a first/latest expectation or adding comparison UI. Preserve run-scoped evaluation/definition/input references where present; unknown information availability stays unknown. Flat legacy QT maps remain labeled legacy context, not invented quartet anchors.

A standalone archive needs the retained association plus original interpretation/comparison basis, applicable command receipts including nullable no-ops, required cycle/definition/evaluation content and captured run metadata. A bare foreign-key list is insufficient when the source database is unavailable. Archive reading must validate ownership, identities, counts, receipt replay and retained policies before exposing data. No source provider refresh or reclassification under today's rules occurs while linking/exporting.

Capture the relevant original source metadata in a consistent snapshot. Preserve exact stored values and unknowns rather than passing them through a model that adds current defaults. A later change to mutable run metadata does not rewrite an already captured source packet. For new linked requests, revalidate the inspected binding and source basis under the owned transaction; record explicit new provenance where source changes require recovery. Routine changing live clock/notes are not substitutes for the original source reference.

## Browsing and editing

Lab can inspect **manual entries** or a deliberately selected **linked run source**, with the full stack and nearby quarter detail retained. Different linked runs remain independently selectable observations, including when they share asset/cycle and disagree. The source chooser is navigation; it creates no interpretation, merge, ranking, correctness grade or comparison baseline. Do not make a raw day-history list the default working AMDX view.

`catalog.current_heads` currently means manual catalog heads. Preserve that meaning instead of changing it silently to the newest linked run. Add an explicit source-aware projection/query for linked captures. Collection membership does not erase origin: downstream aggregation must retain original `(run, branch, channel, cycle, claim/command)` identity, avoiding duplicate counting when one source is deliberately referenced by multiple study collections.

Linked source inspection is read-only in the initial integration. Correct an original Observed run judgment through its permitted run Review action, preserving history and automatic coverage. A technician may deliberately enter an independent catalog judgment using the existing manual action, with an explicit source reference and actual entry time. Automatic adoption, merged interpretations and analytical forks need separately versioned actions; they are not implied by linking.

## Transactions, retries and incomplete sources

Recommend additive storage after v42: source identity/assignment and catalog association/coverage records, with exact ownership constraints and immutable provenance. The proposed migration must assign no instruments or collections to prior rows. **No new migration, automatic collector, launch control or linked-source renderer exists in this checkpoint.**

For a bound future run, the accepted AMDX command and its catalog coverage write share the owned transaction. Failure rolls back that new action and is reported through the existing deliberate recovery path; no silent missing catalog record or background retry reorders history. Unbound legacy capture retains its current behavior. The binding is resolved/pinned before input, rather than adding a new mandatory choice after every phase.

Existing committed source commands retain their exact receipt/basis/result on retry. A retry must not attach a different collection, reinterpret source data or refresh the original link packet. Linking an already committed source later is a distinct explicit association/backfill operation with its own identity/time, not reuse of the old phase command. Duplicate same-source coverage is a no-op in that association; new revisions extend coverage without replacing old revisions. Concluded runs can be linked for study without reopening their operating process.

Missing run-start timestamp does not invalidate an existing identified claim's own preserved cycle/reference. Keep that claim's recorded meaning and mark missing run-start/information basis explicitly. This does not loosen the higher Observed entry guard or invent an as-of context. A flat-only run can retain its legacy source context with zero identified quartets; no role is fabricated. Unavailable/malformed source history must fail validation before any association/coverage commit.

## Worked cases for review

| Before/action | Proposed result |
| --- | --- |
| New MNQ run, compatible remembered collection at launch | Instrument/binding saved once; accepted AMDX choices accumulate automatically with no per-quarter publication step. |
| Older run has no instrument; destination defaults to MNQ | Require deliberate assignment, optionally for a selected batch; retain retrospective assignment provenance. |
| Known MNQ source, NNQ collection | Reject; do not normalize or equate the instruments. |
| Two MNQ runs assign Q3=M and Q3=D for the same 2026 yearly cycle | Preserve both run sources independently; no latest-run winner. |
| Manual collection already has a yearly judgment | Linking either run leaves that manual head/receipt history unchanged. |
| The same original claim is referenced by two study collections | Preserve origin identity for analytical deduplication; collection membership is not a second market observation. |
| Replay/old Expected judgment linked today | Original studied/recorded times and environment remain; link time is additional provenance, not a historical prediction time. |
| Source has a deliberately selected expectation pairing | Preserve that original pairing; create no default baseline or Watch control. |
| Repeated unchanged entry has a nullable/no-op receipt | Retain receipt and coverage; do not invent a source profile revision. |
| New source revision after binding | Append coverage of the new immutable source revision; earlier captures and manual catalog profile stay intact. |
| Binding/source basis changes during input or coverage write fails | Reject/roll back the new bound action atomically; require explicit recovery, no silent retry. |
| Exact old committed phase retry after the destination changes | Return the original phase result; attaching elsewhere is a separate operation. |
| Concluded source run | Link for study without reopening it or changing process completion. |
| Missing original run reference but valid identified claims | Preserve their own cycle/reference; disclose missing original information basis, without enabling new unsupported higher capture. |
| Only legacy flat AMDX values exist | Retain them as legacy context, with no synthesized quartet anchors or classifier output. |
| Study correction of a linked source | Use its permitted run Review action, or make a separate deliberate manual catalog judgment; no automatic copying or overwriting. |

## Implementation boundary and verification

This proposal resolves the data-ownership contract before another migration. Current runtime/source/tests/tools, schema v42, Alpha 0.7 and all 264 smoke results remain unchanged. The completed 97-focused/936-complete native validation remains applicable to its source `678e9a0`; no new full regression run is claimed for this document.

The source/domain inventory and disposable database check establish missing instrument identity, independent same-cycle interpretations, different run judgments and inert scoped reads. Transactional collector/assignment/archive behavior in this proposal still requires implementation and dedicated verification. Expected tests include actual v42 migration without asset guessing, assignment/binding revisions, two-run disagreement, manual-head isolation, complete archives with no-ops and definitions, stale/cross-asset rejection, atomic write failure, exact original retries and automatic native capture/restart.

Next: implement immutable new-run instrument/binding identity and the source-aware catalog projection/coverage transaction, then bind deliberate legacy assignment and automatic future capture. The separate bounded higher run Review selection/proof remains additional integration; broad catalog history is not limited to its one-day window. Keep the existing low-memory/low-motion Watch behavior and spacious Lab overview/detail direction.
