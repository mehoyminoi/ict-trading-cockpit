# ICT Trading Cockpit — Handoff Checklist

Use this file to make chat, branch, and developer handoffs deterministic.

## When to update the project state

Update `docs/PROJECT_STATE.md` whenever any of these occurs:

- a substantial feature slice is completed,
- a schema migration lands,
- the published Trade Plan revision changes,
- a major architectural decision is accepted,
- a branch is about to be merged or switched,
- the current task or known blockers change materially,
- a long ChatGPT conversation is nearing its limit.

If a durable architectural decision was made, also append it to `docs/DECISIONS.md`.

## Minimum checkpoint fields

Record:

- active branch,
- implementation baseline commit SHA + message,
- test status and exact count,
- schema version,
- Trade Plan revision,
- last completed work,
- current task,
- known unresolved issues,
- important accepted decisions,
- intentionally deferred behavior,
- next likely tasks.

## New-chat startup

At the beginning of a new development chat, use this instruction:

> Continue the ICT Trading Cockpit project. Treat `docs/PROJECT_STATE.md` as the current handoff, `docs/DECISIONS.md` as the durable architectural record, and Git as the source of truth for code. Verify the active branch, latest implementation commit, schema version, Trade Plan revision, and test status before proposing new work. Do not reconstruct missing decisions from memory when the repository can answer them.

Then provide fresh terminal output when local state may be ahead of GitHub.

## Before ending a development slice

1. Run the full automated test suite.
2. Run the relevant manual acceptance checks in `docs/SMOKE_TEST.md` for substantial branches or workflow/schema/risk/time changes. The developer utility `python tools/smoke_test_runner.py` may be used to record statuses/comments while keeping Markdown as the source of truth.
3. Record the exact automated and manual results.
4. Confirm the schema and Trade Plan revision.
5. Update `PROJECT_STATE.md`.
6. Append any durable decision to `DECISIONS.md`.
7. Commit those documentation changes with the feature.
8. Make sure "Current task" describes the next action precisely enough that another chat can continue without reconstruction.

## Principle

Chat history is useful working context, but it is not the canonical project record.

- **Git** is canonical for code and migrations.
- **PROJECT_STATE.md** is canonical for the current handoff.
- **DECISIONS.md** is canonical for durable design rationale.
- Versioned Trade Plan data is canonical for trading/process rules.
