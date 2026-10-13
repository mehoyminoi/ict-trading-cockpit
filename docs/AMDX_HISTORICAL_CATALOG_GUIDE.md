# Historical and forward-test AMDX catalog

The initial native entry workspace is now implemented in PR #70, source `678e9a0835a442f1de42ec6761bfcd7116fc6bad`, on top of the v42 catalog backend. See [the four-check Lab trial](AMDX_CATALOG_LAB_OPERATOR_GUIDE.md). Final rendering, automatic run linkage and bulk ingestion remain separate.

## Accepted requirement and ownership

Operator clarification on 2026-10-12 (America/Denver): comprehensive historical and forward-test AMDX data across all layers, as far back as needed, is foundational and should arrive early. Historical entry must not depend on a recent trading run or today's clock. MNQ is the present instrument; another instrument, including the user-mentioned NNQ, may be needed later. Multiple-instrument UI is not required now, but storage distinguishes instruments from the outset.

The catalog backend is an independent owner of interpretations. A collection identifies its instrument, study/forward-test purpose and optional definition reference. It creates no trading day or fabricated run. Existing run-owned AMDX remains intact; unknown legacy asset identity is not guessed or retroactively labeled MNQ. Catalog data and run data are not silently merged. Later deliberate linkage/ingestion must preserve both origins.

All currently identified levels are supported: 16-year, quadrennial, yearly, monthly, weekly, daily session quartet and the selected session's four 90-minute cycles. The last two are called `day` and `session` in the API. Future finer layers use this ownership/provenance contract when their temporal resolver exists; this checkpoint adds no 22.5-minute resolver. There is no rolling history cutoff or retention limit. Dates remain subject to the existing resolver's representable datetime bounds. Tests include 1900 and dates before the 2011 alignment origin; 2011 is not a retention cutoff.

Instrument identity is an explicit normalized key. New collections default to MNQ; other keys stay distinct even for identical temporal cycle IDs. This is catalog identity, not an implemented broker/data-feed/contract-roll mapping. An asset picker is not necessary for the initial MNQ workflow.

## Backend entry and navigation

The adapter is `AMDXRepository.catalog`. These are developer-supplied examples, not an operator smoke checklist:

```python
from ict_cockpit.analysis.amdx import Role
from ict_cockpit.analysis.amdx_catalog import CaptureBasis, Catalog

catalog = amdx.catalog.create(Catalog(
    "mnq-method-a", "MNQ historical study", definition_ref="candidate:method-a:r1"
))
target = amdx.catalog.prepare_target(
    catalog.id, reference=explicit_historical_market_time,
    level="session", position=3, channel="Observed",
)
result = amdx.catalog.revise(
    target, command_id=unique_command_id,
    anchor_id=unique_anchor_id, role=Role.M, source_ref=chart_evidence_ref,
    recorded_at=actual_recording_time,
    capture=CaptureBasis("HistoricalEntry", evidence_ref=chart_evidence_ref,
                         definition_ref="candidate:method-a:r1"),
)
```

The selected session's 90-minute quartet gets an explicit Q3=M anchor and implied XAMD context. Legal choices, compatible-anchor retention, contradiction retirement, direct X(C)/X(R), Unknown, Not Applicable and clear use the existing versioned pure revision engine. No classifier or trading rule is adopted. Catalog Observed revision is independent of Expected and creates no comparison pair or default baseline.

Use deliberate aware historical references and explicit Q1–Q4 positions, including past quarters in higher quartets. New commands reject unsupported/forged temporal targets. Friday/fifth-week/pre-Monday context is inspectable without a fifth anchor or invented applicability. `load_stack` and `prepare_target` write nothing. Entry pins collection/instrument/channel/cycle/quarter/reference/head. Native bindings must additionally pin active navigation and process permissions through the gesture.

`current_heads(catalog_id, channel=..., level=...)` enumerates stored occurrences without a recent-date filter; `history` retains all changed interpretations; `list_catalogs(instrument=...)` separates instruments/collections. Different methods can use separate collections on the same instrument. Collection identity/definition references are immutable; different approaches get separate collections or explicitly different command-level definition references, preserving earlier meaning. Definition references are retained identifiers, not enforced published-rule adoption.

## Retrospective versus forward provenance

Every accepted command, including unchanged meaning and an initially empty clear, retains its request and capture basis. Market reference identifies the studied temporal context; `recorded_at` is actual entry time. `CaptureBasis` declares `HistoricalEntry` or `ForwardEntry`, optional information-availability time, evidence reference and definition reference. Unspecified evidence/as-of/definition references stay unspecified.

Backfilling an old Expected profile does not make it a contemporaneous prediction. Declared ForwardEntry also does not prove absence of look-ahead. Supplied information availability cannot follow entry time; it remains a declared basis rather than a reconstructed historical feed snapshot. Future statistics must distinguish these sources/unknowns instead of pooling them as validated forward predictions. Series purpose Backtest/ForwardTest is organizational context, not an empirical success label.

The first backend supports manual API entry and portable archive validation. Bulk CSV/import, automatic ingestion/linkage of run captures, evidence/price/news fetching, empirical aggregation, competing rule evaluations and historical as-of reconstruction remain subsequent work. Catalog ownership is present now; these tools remain unimplemented. The native AMDX Lab workspace now supplies manual historical/forward catalog entry and recovered navigation/provenance drafts.

## Transactions, migration and archives

Schema v42 adds immutable `amdx_catalog` and `amdx_catalog_command` tables and indexes. They share the existing immutable cycle registry without rewriting original rows. There is no trading-run foreign key. The pure engine retains the field name `run_id`; catalog payloads put a tagged `catalog:<collection-id>` owner there, and never enter the run-owned `amdx_claim` table.

One command owns the existing `BEGIN IMMEDIATE` transaction. Stale-head checks, cycle registration and immutable command/result insertion commit or roll back together. Exact committed retries return original results after later entry/resolver changes; changed content or capture provenance under an old identity is rejected. No-op commands retain nullable original results and source metadata. Writes refuse unrelated caller transactions; reads preserve them.

`export_archive` takes a consistent snapshot of identity and every full command, including no-ops/capture metadata. `read_catalog_archive` validates identity, ownership, policy, head sequence and action/result replay. It returns the collection/history without database writes; the portable command list retains provenance for inspection. This is separate from the older run-only Review envelope and does not omit catalog ownership or capture basis.

Actual v41 migration tests preserve every original application table, changed claims/pairs, nullable receipts and exact old retries. Injected DDL failure rolls back added tables/indexes/triggers and the version bump. Old v41 bootstrap rejects v42; an older branch cannot open an upgraded database. Legacy instruments are not automatically assigned. Normal database backups remain separate.

## Next work

Catalog ownership precedes native higher-stack binding. The bounded run Review selector remains a separate integration: another higher orientation inside that run's reviewed futures day. The catalog deliberately has broader scope and must not inherit that day boundary.

The spacious Lab should expose the full catalog-backed stack with nearby details for deep investigation; Watch retains quiet current orientation and efficient entry. The initial native workspace now supports manual catalog accumulation from the cockpit. Automatic run-capture linkage remains unimplemented; native entry is covered by its separate operator trial. Performance/indexing for large imports and high-volume analytical queries should be measured against realistic data when those workflows are introduced; this slice makes no bulk-throughput claim. The backend checkpoint itself requested no smoke trial; native checks 261–264 are now requested through the separate Lab guide.

Source `d9ccb4422cf9f2f517e38869acb8f57e143e344f`, PR #69 stacked on #68. Focused **382 PASS in 21.22s**, including **60 new cases**. Complete-suite evidence is recorded in project state/handoff when verified. Schema v42 applies only to this unmerged catalog branch; main remains v41 / Alpha 0.7. All 260 smoke records are unchanged.


## Final verification

The complete **904-test collection passed across all 75 isolated module processes in 441.57s**, with collection-matched JUnit counts, clean exits and no failures/errors/skips or pytest warnings. The 382-pass focused group includes all 60 new cases. Separate-process and connection restore, both channels/all seven layers, 1900/pre-2011 dates, instrument/collection separation, revision/subtype/applicability/clear, original nullable retries, capture/archive provenance, SQL rollback, competing writers, immutability and actual parent-v41 migration are covered. All regression work finished. Python 3.10 grammar passes; runtime is Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. Published source remains `d9ccb4422cf9f2f517e38869acb8f57e143e344f`. No new operator smoke trial or merge.


## Next linkage contract — 2026-10-13

[Run-to-catalog linkage](AMDX_RUN_CATALOG_LINK_CONTRACT.md) now concretely proposes explicit instrument/catalog binding once, automatic source coverage and separate run/manual interpretation ownership. Current runs have no saved instrument field; legacy identity cannot be inferred from a collection default or unrelated TDA. This proposal is not an implemented importer/collector or migration. Manual native catalog entry remains accepted and unchanged.
