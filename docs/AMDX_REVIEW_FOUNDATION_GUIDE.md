# Explicit AMDX Review pairing — foundation

**Scope:** isolated pure domain/archive implementation in `analysis/amdx_review.py`. No app database table, migration, Review input widget or Watch history/comparison display. Active schema remains v39 and Alpha 0.7 remains unchanged. This slice is a draft follow-up on the operator-accepted quartet branch; it does not adopt a first-versus-latest baseline default.

## What is retained

`ReviewHistory` contains the original `InterpretationHistory` plus immutable `Comparison` revisions. Each comparison identifies one observed profile and an explicitly supplied expected profile, or an explicitly missing expected basis (`None`). It retains run, branch, containing-cycle identity, previous comparison, recording time, market reference and named `explicit-profile-pair-v1` policy. Source claims preserve their full cycle, anchors, structural/action policy, provenance, uncertainty and X subtype. These are interpreted profiles, not objective price classifications.

The caller must supply `expected_claim_id`; the action never picks first/latest or attaches a later expectation to a missing basis. Both sides must belong to the same run, branch and exact quartet, with the proper Expected/Observed channels. A parent quartet cannot pair with a child merely because their dates overlap. Later intentional cross-run or rule-method research needs its own explicit contract.

Selecting an alternate expected basis appends a new comparison without changing the observation or the original pair. Later source claims can extend the retained interpretation history; they cannot remove, reorder or replace its existing prefix and do not retarget any pair. A comparison cannot be recorded before its source claims or before the prior comparison in that scope. Market references remain explicit and may differ from recording time for Replay.

Exact command retries return the same history, including after later comparison revisions. Reusing an identity with changed content is rejected. A new action must identify the inspected scoped comparison head; stale actions reject rather than silently pairing against something else. Heads for runs, branches and containing cycles are independent. This is a pure action contract; it does not yet protect concurrent database writers or commit observation-plus-comparison atomically in the application.

## Archive and descriptive summary

Version-1 Review archives retain the original versioned interpretation archive alongside comparison revisions. Reload replays the source claims under their original v1 accumulation/v2 working policies, then validates comparison channels, ownership, identity, chronology, predecessor chain and policy. Legacy-only claims keep their original serialized fields; mixed-history claims retain their recorded retirement/applicability meaning. JSON output is detached from frozen in-memory state.

`summarize` describes **Same order**, **Different order**, **No expected baseline** or **Not comparable**. Same order is not a fully matched prediction: X subtype is separately Same/Different/Expected unresolved/Observed unresolved/Both unresolved. Different orders do not compare X at different quarter positions. Conflicting, unresolved or inapplicable profiles retain their source states and are not forced into a comparison result.

Before/During/After cycle refers only to each claim's supplied market reference. The archive retains recording time separately; a supplied Replay reference before a cycle does not establish that a live forecast existed then. Conditional Unknown markers and explicit/implied roles remain inspectable in the full selected claim. No correctness grade, score, probability, competency evidence, gate or completion follows from a summary.

## Read-only synthetic demonstration

```bash
python tools/amdx_review_demo.py
```

The demo explicitly chooses E1 (AMDX) against O1 (XAMD), then E2 (XAMD) against the same O1. Both pairings remain retained, O1 is unchanged, and mixed-history archive reload is checked. `--json` prints the self-contained synthetic archive. No database, feed, UI, published rule or order is touched. This is an optional developer/operator example, not another required smoke test or daily action.

## Integration boundary

Next repository work can persist pair revisions and an observation/pair transaction with immutable receipts, scoped-head protection, original source references and migration compatibility. It must preserve exact retries and nullable-baseline meaning. The current implementation stores nothing in the application database and does not wire this command into the runtime.

Later Review/Study may expose an intentionally opened comparison, or aggregate interpretation changes against recorded price-action events/noticed features with defined samples. Baseline defaults, contextual observation-entry gestures, event association/aggregation and layout remain separate decisions. Watch continues to promote the current working stack and current temporal position, with efficient entry and no visible change-history obligation. Mature X(C)/X(R) direct one-click access remains a future renderer requirement.

## Verified checkpoint

Source `7a31f7194c3053a7254a6a58f2edc3fc631eb570` on `feature/amdx-review-pairing-v0`, [draft PR #63](https://github.com/mehoyminoi/ict-trading-cockpit/pull/63), stacked on unmerged PR #62. Full suite **625 passed in 814.37s (13m34s)** with clean exit/no warnings; focused Review + existing foundation group **98 passed in 0.42s**, including **38 new Review cases**. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen. Python 3.10 syntax parsing passes; separate 3.10 execution was not run. The CLI demo, guide references/fences and git diff --check pass. Existing 254 smoke records are byte-identical to accepted `eb822bc`; no new manual smoke trial is required or claimed for this isolated module.
