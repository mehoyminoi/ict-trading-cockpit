# ICT Trading Cockpit — Handoff Protocol

Use this file to make chat, branch, and developer handoffs deterministic and to prevent architectural regression when long conversation history is unavailable.

## Canonical handoff package

A new development chat should read these documents in this order:

1. **`docs/PROJECT_STATE.md`** — exact current checkpoint: branch, baseline, schema, Trade Plan revision, tests, current task.
2. **`docs/PROJECT_REQUIREMENTS.md`** — current intended product architecture and milestone roadmap.
3. **`docs/DECISION_AUDIT.md`** — conflict/supersession ledger; use this when an older idea disagrees with a newer one.
4. **`docs/DECISIONS.md`** — durable accepted architectural decisions and rationale.
5. **`docs/SYSTEM_GUIDE.md`** — human-readable conceptual map, terminology, subsystem relationships, and architecture loops.
6. **`docs/PROJECT_EVOLUTION.md`** — chronological architecture history explaining how the current model emerged.
7. **Relevant code/tests** — Git is authoritative for what is actually implemented.
8. **Historical source material** — consult only when clarification is still needed after the canonical package.

Do **not** infer current priority from the recency, detail, or enthusiasm of an older feature discussion. First check whether that idea was later implemented, refined, deferred, or superseded.

## Precedence rule

When sources appear to conflict, use this order:

1. verified current implementation + tests,
2. accepted current requirements,
3. explicit later durable decisions,
4. decision-audit supersession status,
5. earlier durable decisions,
6. project-evolution/history summaries,
7. raw historical transcript/chat discussion.

If a conflict cannot be resolved from these sources, stop and record it as an open design question. Do not silently choose the older or more detailed idea.

## Current-frontier rule

Every handoff must state the **current architectural frontier** in plain language, not merely the next Git branch.

This is intended to prevent a future chat from finishing a small convenience feature and then mistakenly treating the surrounding old roadmap items as the project's strategic priority.

For example, a frontier statement should look like:

> Milestone C — Evidence Maturity and progression governance is complete through operator-loop integration/guardrails. The next major roadmap frontier is Milestone E: context maturity for QT/AMDX, news, and distortions. Milestone D remains a parallel friction-driven hardening stream. Older Film Night, visual-polish, chart-gallery, broad integration, and Live-Watch enhancement ideas remain downstream unless actual use makes them blocking.

Update this statement whenever the project's center of gravity materially changes.

## When to update the handoff package

Update `docs/PROJECT_STATE.md` whenever any of these occurs:

- a substantial feature slice is completed,
- a schema migration lands,
- the published Trade Plan revision changes,
- a major architectural decision is accepted,
- a branch is about to be merged or switched,
- the current task or known blockers change materially,
- a long ChatGPT conversation is nearing its limit.

Also update:

- **`DECISIONS.md`** when a durable decision is accepted,
- **`DECISION_AUDIT.md`** when an older decision is refined/superseded or a conflict is discovered,
- **`PROJECT_EVOLUTION.md`** when the project changes architectural phase or center of gravity,
- **`SYSTEM_GUIDE.md`** when terminology, ownership boundaries, subsystem relationships, or major system loops materially change,
- **`PROJECT_REQUIREMENTS.md`** only when the accepted current product/roadmap itself changes.

Do not use `PROJECT_REQUIREMENTS.md` as a running diary.

## Minimum checkpoint fields

`PROJECT_STATE.md` must record:

- active branch,
- main/implementation baseline commit SHA + message,
- test status and exact count,
- schema version,
- Trade Plan revision,
- last completed work,
- current architectural frontier,
- current task,
- known unresolved issues,
- intentionally deferred behavior,
- next likely action.

## Decision-recording standard

A durable entry in `DECISIONS.md` should include:

- date,
- title,
- status,
- decision,
- rationale,
- consequences / intentionally deferred behavior,
- **Supersedes:** previous decision(s), when applicable.

If the new decision changes the meaning or priority of an older one, also update `DECISION_AUDIT.md`.

## Before ending a development slice

1. Run the full automated test suite.
2. Run relevant manual acceptance checks in `docs/SMOKE_TEST.md` for substantial workflow/schema/risk/time changes.
3. Record exact automated and manual results.
4. Confirm schema and Trade Plan revision.
5. Inspect the actual Git diff.
6. Update `PROJECT_STATE.md`.
7. Update `DECISIONS.md`, `DECISION_AUDIT.md`, and/or `PROJECT_EVOLUTION.md` if warranted.
8. Commit documentation with the slice or in a dedicated documentation checkpoint.
9. Make sure `Current task` and `Current architectural frontier` are precise enough for another chat to continue without reconstructing history.

## Before a conversation approaches its limit

Do not wait for the final message.

Perform a **handoff freeze**:

1. stop starting new feature work,
2. finish or explicitly mark the current working checkpoint,
3. make the Git state unambiguous,
4. update the canonical handoff package,
5. record any newly accepted decision or supersession,
6. include unresolved questions explicitly,
7. provide the user the next-chat prompt below.

The objective is that the next chat needs repository reading, not conversational archaeology.

## New-chat startup prompt

Use this prompt when starting a fresh ChatGPT development conversation:

> Continue development of the **ICT Trading Cockpit** from the repository `mehoyminoi/ict-trading-cockpit`.
>
> **Do not begin feature work immediately and do not reconstruct the project from generic memory.** First recover the canonical project state from GitHub.
>
> Read these repository documents in this exact order:
>
> 1. `docs/PROJECT_STATE.md`
> 2. `docs/PROJECT_REQUIREMENTS.md`
> 3. `docs/DECISION_AUDIT.md`
> 4. `docs/DECISIONS.md`
> 5. `docs/SYSTEM_GUIDE.md`
> 6. `docs/PROJECT_EVOLUTION.md`
> 7. `docs/HANDOFF.md`
> 8. `docs/SMOKE_TEST.md` when acceptance/testing context is relevant
>
> Then inspect the relevant current code/tests and Git branch/commit state before proposing changes.
>
> Apply this precedence rule whenever sources appear to disagree:
>
> **verified current implementation/tests > accepted current requirements > explicit later durable decisions > decision-audit supersession status > earlier decisions > historical summaries/transcripts.**
>
> Do not revive an older feature or priority merely because it was discussed in detail. Check whether it was later **implemented, refined, deferred, or superseded**.
>
> Explicitly report back before coding:
>
> - current branch/main baseline,
> - schema version,
> - Trade Plan revision,
> - latest verified automated/manual test status,
> - last completed slice,
> - current architectural frontier,
> - current task,
> - the next recommended slice and why it follows from the current frontier,
> - any conflict or ambiguity you found in the handoff package.
>
> The project values architecture correctness, explicit revision/provenance semantics, small tested vertical slices, and substantial manual acceptance. Do not invent readiness percentages, thresholds, automation, or trading rules that the Trade Plan/evidence does not yet justify.
>
> Important recovered trajectory: the project deliberately shifted away from further Live-Watch embellishment toward the learning/progression loop. Milestone B's human synthesis chain is complete:
>
> **Evidence -> Competency Synthesis -> Cross-Run Observation -> Development Direction -> targeted Study routing**
>
> Milestone C is complete. The next major roadmap frontier is Milestone E, with Milestone D continuing only for proven operator friction:
>
> **boundary-aware Evidence Maturity -> Trade Plan progression policy -> explainable eligibility -> regression/downgrade semantics -> operator-loop integration -> later Live Execution governance**.
>
> Treat `docs/PROJECT_STATE.md` as the final authority for whether that frontier has changed since this prompt was written.
>
> If local terminal state may be ahead of GitHub, ask me for fresh `git status`, branch/SHA, or test output rather than assuming.
>
> Do not modify the roadmap merely to match an older conversation artifact. If historical clarification is required, explain the conflict first.

## Optional short startup prompt

When the canonical package is known to be current, this shorter form is acceptable:

> Continue the ICT Trading Cockpit from GitHub. Read `PROJECT_STATE.md`, `PROJECT_REQUIREMENTS.md`, `DECISION_AUDIT.md`, `DECISIONS.md`, `SYSTEM_GUIDE.md`, `PROJECT_EVOLUTION.md`, and `HANDOFF.md` in that order before coding. Respect the precedence/supersession rules in HANDOFF. Report the verified checkpoint and current architectural frontier before proposing the next slice.

## Principle

Chat history is useful working context, but it is not the canonical project record.

- **Git** is canonical for code and migrations.
- **PROJECT_STATE.md** is canonical for the exact current handoff.
- **PROJECT_REQUIREMENTS.md** is canonical for current intended product architecture/roadmap.
- **DECISION_AUDIT.md** is canonical for supersession/conflict status.
- **DECISIONS.md** is canonical for durable design rationale.
- **SYSTEM_GUIDE.md** explains the architecture in human-readable form without superseding canonical requirements/decisions.
- **PROJECT_EVOLUTION.md** preserves architectural history without making old priorities current.
- Versioned Trade Plan data is canonical for trading/process rules.

A successful handoff should require verification, not archaeology.

## 2026-10-12 — Quartet follow-up acceptance

Checks 251–254 are PASS from the operator’s message, “Smoke test complete. This feels much smoother.” No separate per-check log, local runtime details or new result commit was supplied. Initial checks 245–250 and all previous 250 records are preserved. Application source remains `84167e9bec21189a6bca08e2206a191665df0caa`, validated by the completed 587-pass suite; this reconciliation changes documents only. PR #62 is ready for review, stacked on unmerged PR #61; do not infer merge authorization. Active schema v39 / Alpha 0.7.

Mature X(C)/X(R) entry must each take one click from the active target, with direct future keyboard/macro-pad actions. The current submenu remains an interim renderer. Primary 16:9 geometry, whole-stack renderers and classifiers remain downstream.

Next is `AMDX_REVIEW_COMPARISON_CONTRACT_REVIEW.md`: containing-cycle observation and explicitly retained expectation pairing. The proposed first-expectation default remains unaccepted. No observed entry, comparison UI, automatic grade or rule adoption is added.

## 2026-10-12 — Watch history/comparison boundary

Operator clarified that normal Watch needs the AMDX stack as it is now and current position within it. Do not add prior stack versions or before/after comparisons to support the Review proposal. Preserve automatic immutable revision retention. Later purposeful Review/Study may explore changes associated with identified price-action events or noticed features; context links, samples and aggregation remain unimplemented. The first-versus-latest default remains open. This update changes documents only; source/tests/tools, accepted 254 smoke records, schema v39 and Alpha 0.7 are unchanged.

## 2026-10-12 — Explicit Review pairing foundation

Active follow-up `feature/amdx-review-pairing-v0` starts at accepted quartet checkpoint `eb822bc`. `analysis/amdx_review.py` adds a pure, frozen Review history with explicit expected/observed claim references, nullable expected basis, same run/branch/quartet checks, preserved comparison predecessors, exact retries and stale-head rejection. Its self-contained archive replays retained v1/v2 source claims. Order relation and X subtype are descriptive and separate.

`tools/amdx_review_demo.py` is a read-only synthetic CLI example, not a normal-window trial or required new smoke test. `AMDX_REVIEW_FOUNDATION_GUIDE.md` explains what exists and what does not: app database persistence/concurrency and observation-plus-pair transactions are next; UI/defaults/event aggregation remain downstream. Watch, schema v39, Alpha 0.7 and all accepted smoke records are unchanged. The broader architecture frontier remains Milestone E.

**Final verification:** source `7a31f7194c3053a7254a6a58f2edc3fc631eb570`, draft PR #63 stacked on PR #62. **625 passed in 814.37s**, clean exit/no warnings; focused group **98 passed in 0.42s**, including 38 new tests. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen; Python 3.10 syntax only. Synthetic CLI and Markdown/diff checks pass. All 254 smoke records are byte-identical to `eb822bc`. Full test process exited 0 and no background test work remains. Next is repository integration, not adding history to Watch or adopting an unreviewed baseline default.

## 2026-10-12 — Review pairing persistence

Follow-up `feature/amdx-review-persistence-v0` starts at the pure foundation’s `d940138`. Schema v40 adds immutable comparisons and original Pair / ObserveAndPair receipts. `TradingSessionRunRepository(connection).amdx.review` exposes validated history, original pair lookup, alternate pairing and atomic new-observation-plus-pair actions. Both inspected heads are explicit, exact retries remain original after later changes, and any source/cycle/pair/receipt failure rolls back the entire action. Readers use a consistent snapshot without changing caller transaction ownership.

See `AMDX_REVIEW_PERSISTENCE_GUIDE.md` and the disposable `tools/amdx_review_persistence_demo.py`. v39 migration preserves old row bytes and working no-op receipts; older v39 bootstrap rejects v40. Current Watch and Review controls are unchanged, all existing smoke records remain unchanged, and Alpha 0.7 publishes no new rule/default. Contextual Review binding is downstream; no comparison/history belongs on normal Watch.

**Final persistence verification:** source `e61c1aa5d27d20880adc476ef007328c89771001`, [draft PR #64](https://github.com/mehoyminoi/ict-trading-cockpit/pull/64), stacked on PR #63. Full **658 passed in 813.57s**, clean exit/no warnings; focused **114 passed in 3.62s**, including 33 new repository/demo tests. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen; Python 3.10 syntax only. Archived-v39 schema/repository migration preserves old row bytes and retry meaning; actual E6 normal-window restoration passes at v40. All 254 smoke records are byte-identical to `d940138`. Test process exited 0; no background verification remains. Next: review contextual observed-entry behavior and baseline/default before wiring the separate Review surface; this does not add history/comparison to Watch. No merge occurred.

## 2026-10-12 — Review interaction proposal

The concrete contract review is `AMDX_REVIEW_INTERACTION_CONTRACT_REVIEW.md`. Two unaccepted recommendations: independently versioned observed quartet correction matching the accepted working semantics, and routine observed capture with no automatic comparison. Optional deliberately selected comparison basis would persist through same-cycle corrections until changed/cleared. v40 already supports explicit/null pairing, but observed replacement/no-op/applicability still needs a versioned action extension before controls. No runtime/source/schema/smoke changes are made; retain the completed 658-pass result. Do not infer acceptance from readiness to review, or put history/comparison on Watch.

## 2026-10-12 — Review behavior accepted; comparison lower priority

The operator accepted both principal interaction behaviors: independently versioned one-entry observed correction and optional comparison with no automatic first/latest pairing. Deliberately selected same-cycle basis remains through corrections until changed/cleared. Comparison is lower priority, deferred to a demonstrated Study/Review need; there is no comparison option or launch route from Watch.

Next effort supports efficient observed entry and current-stack orientation, using the completed v40 storage. Versioned observed replacement/no-op/applicability semantics are not yet implemented and must preserve original accumulation replay. Do not expand comparison UI as the automatic next slice. This checkpoint changes documentation only; the 658-pass source, schema v40, Alpha 0.7 and all 254 smoke records remain unchanged. No merge occurred.

## 2026-10-12 — Observed revision shared action

Active follow-up `feature/amdx-observed-revision-v1` starts at accepted behavior checkpoint `1bf3933`. Schema v41 adds immutable observed revision receipts and original source/comparison snapshot counts. Named `revise-observed-v1` implements one-entry normal Observed/working correction with the accepted subtype/Unknown/applicability/clear/no-op behavior. Earlier Expected and observed claims remain independent and immutable. V1/V2 replay/exports retain original meaning; new observed claims use V3.

Use `amdx.review.revise_observed` / `ObservedRevisionResult`. Changed actions atomically persist source, quiet pairing metadata and receipt; no-ops reserve IDs with no source/pair change. Both heads are checked, original exact retries survive later edits, selected same-cycle basis remains pinned and None never falls back to first/latest. v40 migration preserves old row bytes; older bootstrap rejects v41. See `AMDX_OBSERVED_REVISION_GUIDE.md` and the disposable CLI demo. Native Review binding is next; comparison controls remain deferred with no Watch entry point.

**Final observed-action verification:** source `d9d97dc60821d2f7730d91d1eb384eef92a989b4`, [draft PR #65](https://github.com/mehoyminoi/ict-trading-cockpit/pull/65), stacked on PR #64. Full **699 passed in 830.49s**, clean exit/no warnings; focused **215 passed in 4.88s**, including 41 new tests. Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, offscreen; Python 3.10 syntax only. Archived-v40 migration preserves original rows and exact old retries; actual E6 normal-window restore passes at v41. All 254 smoke records and GUI source remain unchanged. Test process exited 0; no background verification remains. Next is native Review entry/gesture/restart binding, followed by its focused hands-on trial. Comparison controls remain deferred and excluded from Watch. No merge occurred.
