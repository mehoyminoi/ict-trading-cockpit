# AMDX Review pairing persistence

**Scope:** schema v40 backend slice on `feature/amdx-review-persistence-v0`, based on the pure Review foundation checkpoint `d940138`. Alpha 0.7 is unchanged. This integrates explicit pairings into the existing saved-run repository; it adds no Watch history/comparison or Review input widget and chooses no first/latest default.

## Records and migration

The atomic v39 → v40 migration adds:

| Record | Responsibility |
| --- | --- |
| `amdx_comparison` | Immutable comparison, owning run/branch/quartet, selected Expected claim or explicit missing basis, Observed claim and preceding comparison in the same scope |
| `amdx_review_command` | Immutable original Pair / ObserveAndPair request, operation, owning run and observed result; its identity is the comparison identity |

Foreign keys protect run and source-claim ownership, cycle registration and comparison predecessors. Each atomic observation has at most one producing ObserveAndPair receipt; other Pair receipts can reference that same observation. UPDATE, DELETE and conflicting INSERT/REPLACE are blocked, including comparison sequence collisions. Source/branch/channel equality, chronology and original-request consistency are additionally verified by the domain/repository replay.

Existing run, claim, evaluation, cycle/definition and working-command rows are preserved, including v39 semantic no-op receipts. Legacy runs acquire no invented observed profile or comparison; their new tables remain empty until explicit actions. Ordinary mutable run saves cannot truncate these separate records. The migration is forward-only: older v39 code rejects a v40 file through its normal bootstrap; use an original unmigrated copy for old-code comparisons. No original data backup is rewritten by this slice.

## Application action boundary

Use `TradingSessionRunRepository(connection).amdx.review`:

- `get_history(run_id)` returns a validated `ReviewHistory` with the run's retained source claims and comparisons. Standalone reads own a consistent read transaction across claim/pair/receipt queries; reads inside an existing caller/writer transaction preserve that boundary.
- `get_comparison(id)` returns the original comparison or None, with the same validated read snapshot.
- `record_comparison(run_id=..., comparison_id=..., expected_claim_id=..., observed_claim_id=..., expected_head_id=..., recorded_at=..., market_reference=...)` creates an explicit pairing against existing source profiles. Alternate selection appends a new pairing, without re-entering or changing the observation.
- `record_observation(comparison_id=..., expected_claim_id=..., expected_comparison_head_id=..., claim_id=..., run_id=..., branch_id=..., cycle=..., quarter_id=..., anchor=..., recorded_at=..., market_reference=..., expected_observed_head_id=...)` accepts a new Observed action, its comparison and original request in one transaction. It returns the committed `Comparison`; its `observed_claim_id` identifies the new source claim.

All IDs, scopes and aware timestamps are supplied explicitly. Expected basis is a required argument: None records a missing basis rather than selecting first/latest. A later expectation does not attach retroactively. Expected and Observed claims must identify the same run, branch and exact quartet, with the correct channels. Historical comparison of unrelated runs/branches needs a separate declared research contract.

The combined action reuses the existing independent Observed `accumulate-v1` anchor/clear semantics. It does not silently extend the Expected-only `revise-working-v1` policy to observed judgments or adopt new observed replacement controls. Original conflicts, Unknown, clear and applicability remain replayable; contextual observed-entry UX is still downstream.

The combined action supplies one recording/reference pair for both observation and comparison. Both inspected heads are required; None means the corresponding scope was inspected empty. A stale observed head raises `StaleAMDXUpdate`; a stale comparison head raises `StaleComparison`. The source claim, any new cycle, comparison and receipt all roll back on a stale second head, wrong basis or failed insertion. Existing-pair commands also reserve the writer with `BEGIN IMMEDIATE` before inspecting their basis/head.

An exact original request returns its original comparison even after later expected, observed or comparison changes. Changed arguments, operation or ownership under the same identity reject. A new ObserveAndPair command must use a new distinct claim ID; pairing an existing observation is the separate Pair action. Comparison identities cannot be reused as claims or working commands, and claim/working/no-op identities cannot be reused for Review.

Actions reject unrelated pending caller work rather than committing or rolling it back. Success is returned only after the owned transaction commits. Readers validate source replay, stored metadata, predecessor chains and required original receipts; inconsistencies fail explicitly instead of resetting history or choosing another basis. This is application immutability and validated replay, not a cryptographic tamper-proof archive.

## Disposable demonstration

```bash
python tools/amdx_review_persistence_demo.py
```

The synthetic example records E1 AMDX, adapts to E2 XAMD, then atomically records O1 XAMD paired with E1. An alternate comparison pairs E2 with that same O1. It checks original exact retry after the alternate, ordinary run save, connection reopen and foreign-key consistency. The database is temporary and removed afterward. Nothing connects to a source feed or the user's normal cockpit database, publishes a policy, changes a gate or places orders.

Order relation and X subtype are descriptive and independent. Same order with unresolved X is not a predicted subtype or a correctness grade. Before/During/After cycle reflects supplied Replay market reference, not proof of what was known live.

## Remaining integration

Later Review input and intentionally opened comparison views can call this boundary without a separate Save obligation. First-versus-latest default, observed-entry gestures, event/change aggregation and final rendering still need their own contracts. Watch continues to emphasize current working stack, current position and efficient entry. Mature one-click X(C)/X(R) and primary 16:9 geometry remain renderer requirements rather than behavior added here.

## Verified checkpoint

Source `e61c1aa5d27d20880adc476ef007328c89771001` on `feature/amdx-review-persistence-v0`, [draft PR #64](https://github.com/mehoyminoi/ict-trading-cockpit/pull/64), stacked on unmerged PR #63. Full suite **658 passed in 813.57s (13m33s)**, clean exit/no warnings; final focused group **114 passed in 3.62s**, including 33 new repository/demo cases. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. Archived-v39 schema/repository migration, row-byte preservation, failure rollback, old-reader rejection and actual E6 normal-window compatibility pass at v40. Python 3.10 syntax passes; separate 3.10 execution was not run. Disposable demo, Markdown guide references/fences and git diff --check pass. All 254 smoke records are byte-identical to `d940138`; no new operator result or UI acceptance is inferred.
