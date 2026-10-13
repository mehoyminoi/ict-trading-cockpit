# AMDX transactional persistence v0

**Checkpoint:** initial storage used schema v38; quartet revision used v39 with immutable working receipts. Review persistence used v40 with comparison/original-request tables. The observed revision follow-up uses v41; see `AMDX_OBSERVED_REVISION_GUIDE.md`. Alpha 0.7 is unchanged. Initial entry checks 245–250 and quartet follow-up checks 251–254 are accepted; the backend Review slice does not add an entry screen.

## Stored records and ownership

The additive v37 → v38 migration creates four tables:

| Table | Responsibility |
| --- | --- |
| `amdx_cycle_identity` | Stable containing-cycle/quarter bounds and labels; an existing identity cannot acquire different content |
| `amdx_definition_revision` | Immutable definition content identified by plan revision, rule ID, rule revision and Candidate/Published status |
| `amdx_claim` | Append-only accepted-action claims, owning run, branch/channel/cycle and preceding claim in that same working scope |
| `amdx_evaluation` | Append-only criteria snapshots, owning run/cycle, explicit recorded time and optional explicitly chosen claim basis |
| `amdx_working_command` (v39) | Immutable original command, inspected head and result/changed flag; reserves retry identities even for semantic no-ops |
| `amdx_comparison` (v40) | Immutable explicit expected/observed source references, owning scope and previous comparison |
| `amdx_review_command` (v40) | Immutable original pairing or atomic observation/pair request, with exact retry result |
| `amdx_observed_command` (v41) | Independent observed revision policy, inspected heads, original snapshot/result and reserved changed/no-op identities |

Existing `trading_session_run` columns and row contents are preserved. Older expected/observed QT maps are not converted into interval anchors or fabricated histories. Existing saved runs load with empty AMDX records until an explicit action is accepted. Ordinary run snapshot saves cannot truncate or overwrite the separate AMDX tables.

Foreign keys require an existing saved run and protect referenced history from deletion. Definition/cycle registries and claims/evaluations reject SQL UPDATE, DELETE and conflicting INSERT/REPLACE, including collisions on sequence identities. This is append-only application history, not a cryptographic tamper-proof guarantee or a general retention/deletion editor.

## Shared durable actions

The normal run repository exposes `TradingSessionRunRepository(connection).amdx`:

- `review` exposes explicit pairing reads/actions and atomic observed-claim-plus-pair commits; see `AMDX_REVIEW_PERSISTENCE_GUIDE.md`.
- `get_history(run_id)` reloads the validated immutable action transcript and profile claims in recorded append order.
- `accept(...)` retains the original accumulation action for v1 replay and analytical scopes. It cannot append accumulation into a scope already advanced by the new working policy; exact retries of older actions still return their original claims.
- `revise_working(...)` is the normal Expected/working phase, Unknown, applicability and clear action. Valid entry selects the order, keeps compatible anchors and retires incompatible anchors into history. It returns `WorkingRevisionResult(claim, changed)`, where a semantic no-op has `changed=False` and may have no claim when the scope was empty. Cycle registration, optional v2 claim and command receipt commit together.
- `save_evaluation(evaluation, recorded_at=..., basis_claim_id=...)` stores original definitions, facts/source availability, result/reason traces and governing policy. A linked claim must belong to that run and quartet. None means no basis was chosen; it does not choose a Review default.
- `get_evaluation(id)` / `get_evaluations(run_id)` reload the original snapshots and recorded/basis metadata without substituting current plan definitions or source captures.

Accepted choices require explicit claim/anchor revision IDs, run/branch/channel/cycle/quarter scope, aware recorded/market timestamps and an **expected head ID**. None means the caller inspected an empty scope. The transaction takes the SQLite writer reservation before loading/checking current state. If another accepted action changed that scope, `StaleAMDXUpdate` requires reload; the repository never silently applies a stale edit to newly changed context. Different branches, channels, quartets and runs have independent heads.

An exact retry with the same action ID, original expected head and unchanged parameters returns the original stored claim, even after later revisions; it does not append twice or move the current head backward. Reusing an ID with different content or ownership is rejected. Evaluations have the same immutable/idempotent identity behavior. A different interpretation method requires a separate evaluation ID; changed definition content needs a new revision identity. Candidate/Published status is part of this snapshot namespace, not an implementation of real Trade Plan publication.

The repository owns its transaction boundary (`BEGIN IMMEDIATE`, commit/rollback). It rejects a connection with unrelated pending work instead of accidentally committing or rolling back the caller's transaction. Cycle/definition registration and claim/evaluation insertion commit together or roll back together. UI integration must save/ensure the owning run before invoking the action and only present the new interpretation as accepted after successful commit. A database failure is surfaced; no silent in-memory success is reported.

Reload checks payload versions, ownership, stable cycle content, revision chains, retained action transcripts and evaluation definition/input/result consistency. Unsupported or inconsistent records fail explicitly; they are not emptied, normalized into guessed history or automatically reinterpreted under current rules.

The v39 working action has policy `revise-working-v1`. v2 claims explicitly record the incoming anchor, preceding basis claim, retired anchor IDs and separate applicability markers. Mixed histories replay original Accept/Clear claims under their original accumulation semantics and new claims under this policy; v1 exports and old stored bytes remain intact. Replaying a receipt validates its original basis and changed/no-op result. A repeated explicit identical judgment stores only a command receipt, with no extra interpretation claim; a first explicit selection of an implied role is a new judgment.

Receipts reject UPDATE, DELETE and conflicting INSERT/REPLACE. Their IDs cannot be reused as another working or legacy action. An exact retry, including a no-op retry after later changes, returns the original result. No-op receipts are internal command provenance, not quarter-phase records or an operator history form. Normal run saves and evaluation snapshots remain independent; an explicit evaluation basis may point to a v2 claim without being replaced by later working revisions.

## Migration and compatibility

The v38 migration explicitly opens a transaction when SQLite DDL has not already opened one, keeping all four tables, indices/triggers and the version bump atomic. An injected migration failure leaves v37 and no partial AMDX schema; a subsequent normal migration succeeds. Earlier application columns and source captures retain their existing meanings.

Migration is forward-only. v38 → v39 atomically adds the receipt table/triggers and the forward-version guard, preserving all earlier claims. A failed receipt-schema migration leaves v38 and no partial new table; an older v38 application explicitly rejects v39. Use the original unmigrated copy for old-code comparisons rather than relabeling/downgrading a migrated file. The controlled E6 fixture retains its original v37 backup.

Developer verification includes an actual accepted-v37 schema with populated QT expectation/observation rows, plus the controlled database written by accepted E6 source `42e3b346`. The normal current application restores the original run, captures, context snapshot, workflow and manual authorization boundaries at v38, with empty AMDX records. The original E6 v37 backup and provenance manifest remain unchanged. The compatibility harness now distinguishes original v37 from the current schema in its label.

This does not certify real Forex Factory completeness, event timing/status, historical as-of knowledge, AMDX classifier quality, or a new automatic trading policy. Source acquisition/mapping and actual classifier criteria remain separate work.

## Disposable worked example and validation

```bash
python tools/amdx_persistence_demo.py
```

The command creates a temporary application database, saves a synthetic owning run, accepts Q3=M then Q3=D, stores the London-priority criteria evaluation with an explicit claim basis, performs an ordinary run save, closes/reopens the database and verifies both histories and foreign-key consistency. The temporary directory is removed after the demonstration. It does not open a real database, publish a plan, query a source or operate orders.

```bash
python -m pytest tests/test_amdx_repository.py tests/test_amdx_foundation.py -q
python -m pytest -q
```

The focused domain/storage/E6/E7/compatibility/database group passed **133 tests in 9.27s**, including **30 new repository checks**. Tests cover a separate-process restart, immutable action/evaluation retries, changed methods, conflicting anchors, clear/revision history, scope isolation, stale ordinary saves, competing writers, pending caller transactions, rejected ownership/basis/content drift, failed append/migration rollback and SQL UPDATE/DELETE/REPLACE protection. The complete suite result is recorded in `PROJECT_STATE.md`. Smoke identities/statuses remain the prior 244; no new phase-entry surface is presented for operator acceptance here.

## Next boundary

The minimal shared Watch/TDA entry is functionally accepted in PR #61. The follow-up implements one-entry quartet revision and valid role choices; see `AMDX_QUARTET_REVISION_OPERATOR_GUIDE.md`. It preserves pinning, reports failures, restores mixed histories and distinguishes entered/implied meaning. Four follow-up checks 251–254 are operator accepted. The native observed-entry follow-up now binds independent one-entry correction in Review, with new checks 255–259 pending; see `AMDX_OBSERVED_ENTRY_OPERATOR_GUIDE.md`. Direct one-click X(C)/X(R) is implemented, while broader renderers and purposeful comparison controls remain downstream.

Review default pairing, higher-order cycle mapping, note-draft semantics, keyboard/macro-pad and coverflow details, real price/news classifiers, plan-editing UI and broad Lab statistics remain separately defined work. No new entry/completion/competency gate is introduced by stored AMDX uncertainty.
