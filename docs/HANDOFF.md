# ICT Trading Cockpit — Handoff Protocol

Use this file to make chat, branch, and developer handoffs deterministic and to prevent architectural regression when long conversation history is unavailable.

## Canonical handoff package

A new development chat should read these documents in this order:

1. **`docs/PROJECT_STATE.md`** — exact current checkpoint: branch, baseline, schema, Trade Plan revision, tests, current task.
2. **`docs/PROJECT_REQUIREMENTS.md`** — current intended product architecture and milestone roadmap.
3. **`docs/DECISION_AUDIT.md`** — conflict/supersession ledger; use this when an older idea disagrees with a newer one.
4. **`docs/DECISIONS.md`** — durable accepted architectural decisions and rationale.
5. **`docs/PROJECT_EVOLUTION.md`** — chronological architecture history explaining how the current model emerged.
6. **Relevant code/tests** — Git is authoritative for what is actually implemented.
7. **Historical source material** — consult only when clarification is still needed after the canonical package.

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

> Competency / Proficiency v0 is complete. The larger trajectory has shifted toward the Study/Lab learning loop: targeted Study -> competency evidence -> Replay integration -> Forward validation -> progression/eligibility. Older Film Night, visual-polish, chart-gallery, broad integration, and Live-Watch enhancement ideas remain downstream unless actual use makes them blocking.

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
> 5. `docs/PROJECT_EVOLUTION.md`
> 6. `docs/HANDOFF.md`
> 7. `docs/SMOKE_TEST.md` when acceptance/testing context is relevant
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
> Important recovered trajectory: the project had deliberately shifted away from further Live-Watch embellishment toward the learning/progression loop. The current frontier after Competency / Proficiency v0 is approximately:
>
> **targeted Study -> competency evidence -> Replay integration -> Forward validation -> progression/eligibility -> Live Execution**, with Review/Development and Evidence Maturity becoming stronger only after the evidence substrate is trustworthy.
>
> Treat `docs/PROJECT_STATE.md` as the final authority for whether that frontier has changed since this prompt was written.
>
> If local terminal state may be ahead of GitHub, ask me for fresh `git status`, branch/SHA, or test output rather than assuming.
>
> Do not modify the roadmap merely to match an older conversation artifact. If historical clarification is required, explain the conflict first.

## Optional short startup prompt

When the canonical package is known to be current, this shorter form is acceptable:

> Continue the ICT Trading Cockpit from GitHub. Read `PROJECT_STATE.md`, `PROJECT_REQUIREMENTS.md`, `DECISION_AUDIT.md`, `DECISIONS.md`, `PROJECT_EVOLUTION.md`, and `HANDOFF.md` in that order before coding. Respect the precedence/supersession rules in HANDOFF. Report the verified checkpoint and current architectural frontier before proposing the next slice.

## Principle

Chat history is useful working context, but it is not the canonical project record.

- **Git** is canonical for code and migrations.
- **PROJECT_STATE.md** is canonical for the exact current handoff.
- **PROJECT_REQUIREMENTS.md** is canonical for current intended product architecture/roadmap.
- **DECISION_AUDIT.md** is canonical for supersession/conflict status.
- **DECISIONS.md** is canonical for durable design rationale.
- **PROJECT_EVOLUTION.md** preserves architectural history without making old priorities current.
- Versioned Trade Plan data is canonical for trading/process rules.

A successful handoff should require verification, not archaeology.
