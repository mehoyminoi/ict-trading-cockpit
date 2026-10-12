# One-entry observed quartet revision

**Scope:** shared domain/repository action on `feature/amdx-observed-revision-v1`, based on accepted behavior checkpoint `1bf3933`. Schema v41 / Alpha 0.7. This implements observed revision semantics before native Review binding. It adds no comparison controls or Watch access, no new price classifier and no source-derived observation.

## Accepted entry behavior implemented

`InterpretationHistory.revise_observed` uses named `revise-observed-v1` in the manual Observed/working scope. It shares structural revision logic with Expected `revise-working-v1` without changing that policy or its serialized records. Valid phase positions remain Q1 A/X, Q2 A/M, Q3 M/D, Q4 D/X across both orders.

One valid quarter choice selects AMDX/XAMD, keeps compatible manual anchors and retires contradictory anchors into immutable earlier claims. Correcting Q1=A with Q3=M selects observed XAMD immediately. Clearing Q3 never reactivates retired Q1=A. Expected claims and parent/child quartets remain independent.

X subtype remains only at the same compatible X quarter; a changed order does not copy C/R to the new X position. Unknown remains explicit beside a conditional implied role. Not Applicable is a whole-quartet judgment; a valid phase restores applicability, and explicit applicability clear retains any Unknown markers without reviving older anchors. Selecting an implied phase explicitly is a new judgment; repeating already-explicit unchanged meaning is a no-op.

The action rejects incompatible channel/branch, invalid normal role positions, unsupported mixed rule/technician bases and unsafe identities/timing. Explicit analytical alternatives retain the original accumulation action; they are not silently revised under this normal-entry policy.

## Durable routine action

Use `TradingSessionRunRepository(connection).amdx.review.revise_observed` with:

- distinct `claim_id` and `comparison_id`, plus run/branch/cycle/quarter target;
- explicit technician anchor or clear, optional `clear_applicability`;
- timezone-aware `recorded_at` and `market_reference`;
- both inspected `expected_observed_head_id` and `expected_comparison_head_id` (None means inspected empty).

It returns frozen `ObservedRevisionResult(claim, comparison, changed)` only after the owned transaction commits. Changed entry commits new observed claim, quiet pairing metadata and original command receipt atomically. An unchanged entry adds no observation or pairing; it reserves both request identities and retains original nullable results. Empty clear is a no-op with no source claim or comparison. Different content under either identity is rejected; exact original retry remains idempotent after later changes.

Routine entry chooses no first/latest expectation. Initial pairing metadata has no selected basis, even if working expectations exist. Corrections carry the same-cycle basis from its last explicitly saved pairing, or retain None after a deliberate clear. Later working changes cannot substitute a newer expectation. This is hidden provenance behavior; it introduces neither a baseline-selection obligation nor a comparison surface.

Both observed and comparison heads are checked before deciding changed/no-op. Stale input requires deliberate inspection/retry. Registration, source claim, pairing and receipt all roll back on failure; unrelated caller transactions are rejected rather than committed or rolled back. Existing read snapshots prevent mixing source/pair states across concurrent commits.

## Versioning and compatibility

Schema v41 adds immutable `amdx_observed_command`. It retains original request/policy, inspected heads, result IDs, changed flag and source/comparison snapshot counts. Snapshot counts identify the original replay basis, including no-ops after later edits. SQL UPDATE/DELETE/conflicting REPLACE is blocked, and both claimed and unused comparison request identities are protected from cross-action reuse.

Changed observed claims use envelope/history version 3 with their original action, prior claim, retired anchors, applicability and original incoming anchor. Legacy v1 accumulation and Expected v2 working claims keep their fields and replay meaning. Legacy-only exports stay v1; working-only/mixed legacy-working exports stay v2; histories containing the new observed policy use v3. New accumulation cannot append into a scope already advanced by observed revision, but exact original old-command retries still return their retained result.

The atomic v40 → v41 migration preserves existing run, source, comparison, old Review/working receipt and registry rows. It invents no observed history and changes no flat expected/observed maps or process gates. Older v40 bootstrap rejects a migrated v41 file; use the original unmigrated copy for old-code comparisons. Ordinary run saves cannot truncate the new command records.

Reload validates new claim/receipt/pair correspondence, scope, chronology, stable cycle content, snapshot heads and original changed/no-op replay. Unsupported or inconsistent data fails explicitly; no guessed basis or empty-history fallback is applied. This is application immutability, not a cryptographic tamper-proof archive.

## Disposable demonstration

```bash
python tools/amdx_observed_revision_demo.py
```

Synthetic observed Q1=A selects AMDX; Q3=M revises to XAMD; repeat M is a no-op; clear Q3 becomes Unresolved without old A returning. The original retry, unchanged working expectation, absence of automatically chosen baseline and connection reopen are checked in a temporary database that is removed afterward. Supplied Replay references are not evidence of a live forecast or objective price classification.

## Native integration follow-up

`feature/amdx-observed-entry-v1` now binds this action to the normal Review panel; see `AMDX_OBSERVED_ENTRY_OPERATOR_GUIDE.md` for the retained trial and operator-accepted checks 255–259. It supplies both scoped heads from a consistent Review read, carries deliberately selected pairing metadata quietly and preserves run/channel/cycle/reference through gestures. The saved Trading Day supplies the review date; missing identity disables entry. Direct X(C)/X(R) choices also serve working entry. This changes no schema or published plan. The following paragraph records the integration boundary originally proposed before that implementation.

Bind efficient observed entry to the permitted Review surface with pinned reviewed cycle/reference, quiet success/failure feedback and no extra Save obligation. Restore explicit/manual versus implied/Unknown context without exposing a raw change-history list. Comparison controls and event/change research remain deferred to a concrete Study/Review need and have no Watch entry point. Mature one-click X(C)/X(R), primary 16:9 geometry, higher-stack mapping and macro-pad bindings remain separate renderer/architecture work.

## Verified checkpoint

Source `d9d97dc60821d2f7730d91d1eb384eef92a989b4` on `feature/amdx-observed-revision-v1`, [draft PR #65](https://github.com/mehoyminoi/ict-trading-cockpit/pull/65), stacked on unmerged PR #64. Full **699 passed in 830.49s (13m50s)**, clean exit/no warnings; focused group **215 passed in 4.88s**, including **41 new observed cases**. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. Archived-v40 schema/repository migration and row-byte preservation, old-reader rejection, separate-process replay and existing actual E6 normal-window compatibility pass at v41. Python 3.10 syntax passes; separate 3.10 execution was not run. Disposable CLI, guide references/fences and git diff --check pass. All 254 smoke records are byte-identical to `1bf3933`; native Review binding and operator trial remain next, with no inferred new UI acceptance.
