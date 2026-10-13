# Canonical AMDX calendar foundation

This slice implements canonical instrument ownership and shared read/target access from `AMDX_MASTER_CALENDAR_CONTRACT.md`. It does not yet bind native Lab/TDA/Watch to that owner or persist run captures. Existing native entry behavior and smoke identities are unchanged.

## Implemented ownership

`AMDXRepository.master` exposes the foundation. New `MasterCalendar` metadata has explicit instrument identity and no Backtest/ForwardTest purpose. Its versioned metadata is stored in the existing ledger table; commands retain the existing quartet policies and tagged owner identities. An immutable `MasterBinding` records the instrument, ledger, operation identity, actual recording timestamp and source of creation/adoption.

Schema v43 adds `amdx_master_binding` and an instrument/owner index. Unique constraints enforce one binding per instrument and owner; a composite foreign key prevents a binding to another instrument's ledger. Update, delete and replacement triggers protect binding history. Superseding a binding requires a future versioned action; v0 supports first creation/adoption only.

The migration creates no owners, bindings or asset assignments and preserves every existing v42 row. Older code rejects v43 rather than pretending compatibility. New runs still have no persisted instrument/capture binding in this slice; creating a master does not identify old run assets or import their claims.

## Shared API and deliberate adoption

| API | Behavior |
| --- | --- |
| `master.resolve(instrument)` | Read existing canonical binding; missing/malformed ownership fails explicitly. |
| `master.ensure(instrument, recorded_at=...)` | Initialize an empty instrument context once; concurrent callers receive the same binding. Existing collections require deliberate adoption. |
| `master.create(owner, binding_id=..., recorded_at=..., source_ref=...)` | Identified atomic creation of a purpose-independent owner/binding; exact original retries return the original binding. |
| `master.adopt(instrument, catalog_id, binding_id=..., recorded_at=..., source_ref=...)` | Identified deliberate adoption of an existing ledger, preserving original metadata, judgments, commands and archives. |
| `master.load_stack(instrument, reference=..., channel=...)` | Consistent binding and projection snapshot; default Expected means working interpretation. Observed is explicit and independent. |
| `master.prepare_target(instrument, reference=..., level=..., position=..., channel=...)` | Pin the inspected binding and existing legal quartet target, including exact head/reference. |
| `master.validate_target(prepared)` | Read-only binding, temporal ownership and head check; not a substitute for transaction-owned write validation. |
| `master.export_archive(instrument)` | Self-contained binding provenance and original ledger; `read_master_archive` validates both before exposing them. |

All references/recording timestamps are aware; instrument keys must already be explicit normalized identities. NNQ never borrows MNQ heads. Read/navigation APIs never initialize missing owners, write phase revisions or fabricate a run. Full stack uses the existing seven identified layers during open market references; closed references retain five higher layers and do not fabricate intraday occurrences. Distortion/unassigned position handling remains unchanged.

Automatic initialization checks existing instrument ledgers under the owned transaction. Even one legacy collection is not implicitly adopted. `MasterAdoptionRequired` is an explicit recovery state; a later native adoption workflow can make the deliberate choice once. Competing adoption operations cannot produce two canonical owners. Current v0 binding is immutable and cannot silently change under a future gesture.

An adopted legacy collection keeps its original purpose as provenance. Other collections and conflicting run/collection judgments remain independent; they are not merged, deleted, copied or re-timed. Ordinary native collection lists keep their existing legacy collection contract and omit newly created master metadata. The normal master workspace will use the new facade when native integration is implemented.

## Archives and transaction boundary

Old collection archives still emit/validate the same v1 envelopes and original commands. New purpose-independent owner ledgers use v2 catalog archive framing with versioned master-owner metadata, retaining the existing command policy/replay. The outer master archive v1 retains exact binding source/time and owner content. Adopted legacy ledgers remain v1 inside that archive. Reading validates identity, instrument, owner metadata and original command/result replay, including nullable no-ops and unknown availability. Archive reconstruction uses retained payloads, not today's resolver or an absent source database.

`MasterSnapshot` is a transient consistent database projection, **not a persisted run capture**. Immutable run packets, launch/TDA source vectors and atomic calendar-write/run-capture receipts are next. Do not combine read-only `validate_target`, the independently committing low-level catalog writer and mutable run save as a purported atomic bound action.

Creation/adoption/initialization own a `BEGIN IMMEDIATE` transaction, reject a pending caller write and roll back new owner plus binding on failure. Exact operation ID retries validate the original complete binding/owner request. Reads honor an existing caller transaction without committing it. A shared read sees one consistent binding/head snapshot when another writer commits between its internal reads; a new read can then see the newer revision.

## Verification and downstream work

Focused 263 tests passed in 8.76s, including 34 new repository/migration cases. New evidence covers clean initialization, independent instruments/channels, all layers and closed references, deliberate conflicting-ledger adoption, exact retries/request drift, SQL immutability/cross-asset constraints, owned rollback/caller transaction retention, competing connections, interleaved read/write snapshots, standalone archive/reopen and actual archived-v42 migration/failure without guessing assets. Python 3.10 grammar parsed; runtime Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. Complete 970 tests passed across all 79 isolated module processes in 259.56s, with collection-matched JUnit counts, clean exits and no failures/errors/skips or pytest warnings. All regression processes exited; no combined single-process full run is claimed. Source `8269b647be6ccdce029694c8d9fed07d9a34ebce`, PR #71, stacked on #70 `f4f2363`.

Next implement immutable run instrument/capture identity and transaction-owned write/capture helpers before rebinding native consumers. The initial binding/facade is complete, but cross-area calendar behavior is not delivered end to end. Final rendering, bulk ingestion/performance, broad historical as-of reconstruction, classifiers and Study-first startup remain separate. There is no new Watch history/comparison control or new operator smoke trial for this backend slice.


## Run capture storage update

V44 now implements immutable run instrument/master binding, full-stack capture packets and owned launch/context/working-edit transactions; see `AMDX_RUN_CALENDAR_CAPTURE_GUIDE.md`. Earlier pending-storage statements describe the v43 checkpoint. Native automatic consumption and shared Lab/TDA/Watch binding remain the next integration, with no new operator trial in this backend slice.
