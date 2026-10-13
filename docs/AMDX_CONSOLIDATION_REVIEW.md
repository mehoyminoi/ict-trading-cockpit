# AMDX consolidation review

Review date: **2026-10-13 (America/Denver)**. This checkpoint reviews the nine stacked AMDX PRs as one integration. It does not merge them or open the operator's regular database. The complete final regression passed; the integration is ready for the separately authorized merge.

## Baseline and reviewed sequence

Main remains **`6dd43c845940874000f46371965441dec262e77a`**, schema **v41**, Trade Plan **Alpha 0.7**. The entry checkpoint for this review is **`53bcf6b001186dad737b742dd65c48c12a97cc38`** (#75 operator acceptance), with all higher Review source unchanged from **`310c4747d208ebb6a5852ca30008d0fd4d790390`**. This consolidation adds only two direct-main compatibility tests and review/handoff documentation; production source, schema and plan are unchanged.

| Order | PR | Reviewed entry head | Final schema | Delivered boundary |
| --- | --- | --- | --- | --- |
| 1 | [#67](https://github.com/mehoyminoi/ict-trading-cockpit/pull/67) | `e27bd31` | v41 | Identified higher cycles and scoped projections |
| 2 | [#68](https://github.com/mehoyminoi/ict-trading-cockpit/pull/68) | `e80a17b` | v41 | Pinned higher input, exact timestamps and DST correction |
| 3 | [#69](https://github.com/mehoyminoi/ict-trading-cockpit/pull/69) | `5219524` | v42 | Historical catalog ledger, asset and capture provenance |
| 4 | [#70](https://github.com/mehoyminoi/ict-trading-cockpit/pull/70) | `f4f2363` | v42 | Spacious native historical entry and direct subtype |
| 5 | [#71](https://github.com/mehoyminoi/ict-trading-cockpit/pull/71) | `6c7362b` | v43 | Canonical instrument/master calendar ownership |
| 6 | [#72](https://github.com/mehoyminoi/ict-trading-cockpit/pull/72) | `20efbee` | v44 | Immutable run captures and atomic calendar actions |
| 7 | [#73](https://github.com/mehoyminoi/ict-trading-cockpit/pull/73) | `fcc6138` | v44 | Native shared Lab/TDA/Watch calendar |
| 8 | [#74](https://github.com/mehoyminoi/ict-trading-cockpit/pull/74) | `9d6ab3e` | v45 | Maintained Observed Review and immutable assessments |
| 9 | [#75](https://github.com/mehoyminoi/ict-trading-cockpit/pull/75) | `53bcf6b` plus this consolidation checkpoint | v46 | Bounded higher Review, retained scope proof and final compatibility evidence |

All nine are open, ready for review, and GitHub reports clean mergeability. Each head contains the preceding reviewed head; #67 contains current main. Local simulation of **nine two-parent merge commits** produces the exact reviewed tree at each stage, without moving branches or the index. No unrelated main changes need reconciliation. There are no GitHub commit statuses or check runs attached to the entry tip; the aggregate status says pending because its count is zero. Validation comes from the recorded developer suite and operator trials, not an unobserved GitHub CI run.

The earlier independent Backtest/ForwardTest catalog interpretation in #69–70 was refined by #71–73. The final normal cockpit uses one maintained calendar per instrument. Purpose/environment remains provenance; it is not a recurring destination chooser. Old collections and unknown legacy ownership remain preserved instead of being silently combined.

## Compatibility and regression evidence

`tests/test_amdx_consolidation_migration.py` archives **actual merged main**, runs its own normal-window v41 fixture in a separate process, creates original Expected/Observed run-owned judgments and legacy notes, and closes that database cleanly. It then verifies:

- direct v41 → v46 migration preserves every original table row;
- denial at the **last v46 format-barrier write** rolls the entire chain back to v41, including its original schema, rows and triggers;
- no catalog, master binding, run binding, run capture or maintained assessment is invented by migration;
- the original run, Review mode, exact reference, notes and XAMD Observed quartet restore in the final native application and after reopening;
- old histories and comparison packets remain exact; the old run does not acquire guessed MNQ ownership or the bound higher editor;
- the v41 reader rejects v46, foreign keys remain valid, and the retained original database copy remains byte-identical.

Both new cases passed. The retained v42/v43/v44/v45 migration tests, E6 normal-window compatibility, shared native entry, atomic write/retry/concurrency and portable archive cases remain in the complete regression.

Final regression: **1,136 PASS across 89 isolated module processes in 450.24s**. Every JUnit test count matches collection; all processes exit cleanly with no failures/errors/skips or pytest warning summaries. Python **3.10 grammar** passes for all **55 changed production/test/tool files** relative to main. Actual runtime is **Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1**, Qt offscreen. The two added direct-main cases strengthen the previous 1,134-test validation; no production fix was needed. All verification workers have exited.

Published compatibility-test source: `ec96aa0719585f2d2e0117890eeb85ffc2c6fedb`. The final #75 PR head includes the review/handoff documentation and is the exact expected head to verify before merging.

All **280 smoke-test identities/results/comments are unchanged** in this review. The **20 operator checks 261–280 are PASS**, covering historical entry, direct X(R), shared native Watch/Lab, captured launch context, maintained Observed Review, boundary selection, write-failure recovery and restart/proof inspection. This does not imply final-layout acceptance or unseen operator notes. No additional manual trial is required for a test/documentation-only checkpoint.

## Review conclusions and remaining limits

No consolidation blocker was found in the reviewed scope. The final architecture provides broad historical Lab input, quiet operational stack/position, current shared Expected/Observed judgments and immutable run launch/use/assessment provenance. Navigation and temporal context do not invent phase judgments, copy interpretations between occurrences or select an Expected comparison baseline. A failed owned action rolls back its records together; stale or unavailable input requires deliberate recovery.

Existing unbound run-owned data remains available through its legacy path. It is not silently imported into the maintained MNQ calendar. Deliberate legacy assignment/import, bulk historical import, large-history performance and future instruments remain work to evaluate explicitly. The complete mature cockpit renderer, closer overview/detail topology, Study-first doorway/Study loop and usable versioned criteria/evidence evaluation are also unfinished. Classifiers, coverflow/macropad and Watch history/comparison routes are not adopted by this consolidation. These are preserved scope boundaries, not newly discovered reasons to reopen the accepted trials.

## Concrete merge procedure after authorization

1. Re-fetch main and all nine PRs. Confirm the reviewed heads and main baseline still match, with #75 at the published consolidation checkpoint. Stop and review any new changes before mutation.
2. Merge **#67 → #75 in order**, using **merge commits**. Retarget each remaining PR to **main immediately before merging it**, so the merge advances main instead of changing its old feature base.
3. Use each PR's exact expected head SHA when merging. The repository permits merge commits and does not automatically delete merged branches. Retain feature branches and historical commits until final verification; migration tests use those historical commit objects.
4. Verify every intermediate main tree matches the corresponding reviewed feature tree. At the end verify main matches the final #75 checkpoint tree, the nine PRs are merged, and production source has not drifted. No squash/rebase rewrite is needed for this linear stack.
5. Publish a main handoff checkpoint and provide exact user-side sync commands. Before opening the regular application on v46, preserve local smoke notes/stashes and take a consistent SQLite backup of the regular v41 database, including committed WAL content. An old application requires an unmigrated database copy; switching Git branches does not downgrade SQLite. The user's regular database has not been migrated by this review.

Merge authorization is still outstanding. The next product milestone after consolidation is a comprehensive whole-cockpit UX/Study implementation plan using the accepted 16:9 primary frame, quiet Watch, analytical TDA and spacious Lab requirements, rather than another speculative AMDX storage layer. Keep comparison exploration lower priority in Study/Review.
