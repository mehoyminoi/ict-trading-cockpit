# ICT Trading Cockpit — Next Chat Startup Prompt

Copy the prompt below into a fresh ChatGPT conversation when this development chat is approaching or has reached its context limit.

---

Continue development of the **ICT Trading Cockpit** from the GitHub repository `mehoyminoi/ict-trading-cockpit`.

This is a long-running architecture-heavy project. **Do not begin feature work immediately, do not infer the roadmap from generic memory, and do not treat an older detailed feature discussion as current priority.** First reconstruct the canonical project state from the repository.

## Step 1 — Read the handoff package in order

Read these repository documents in this exact order:

1. `docs/PROJECT_STATE.md`
2. `docs/PROJECT_REQUIREMENTS.md`
3. `docs/DECISION_AUDIT.md`
4. `docs/DECISIONS.md`
5. `docs/PROJECT_EVOLUTION.md`
6. `docs/HANDOFF.md`
7. `docs/SMOKE_TEST.md` when testing/acceptance context is relevant
8. relevant current code and tests

If historical clarification is still necessary after those files, consult `docs/history/README.md` before asking me to recover old chat transcripts.

## Step 2 — Apply the precedence rule

When project sources appear to disagree, use this precedence:

**verified current implementation/tests**
>
**accepted current requirements**
>
**explicit later durable decisions**
>
**DECISION_AUDIT supersession status**
>
**earlier durable decisions**
>
**PROJECT_EVOLUTION/history summaries**
>
**raw historical transcript/chat discussion**

Do not revive an older feature, architecture, or priority merely because it was discussed in more detail. Determine whether it was later **implemented, refined, deferred, or superseded**.

If the repository documents themselves contain an unresolved contradiction, report it before modifying code or the roadmap.

## Step 3 — Verify the checkpoint before coding

Report back to me with:

- current repository branch and main baseline,
- latest relevant commit/SHA,
- schema version,
- Trade Plan revision,
- latest verified automated-test result,
- latest manual-acceptance result,
- last completed product slice,
- current documentation/reconciliation status,
- current architectural frontier,
- current task,
- known unresolved architectural questions,
- intentionally deferred areas,
- the next recommended slice and why it follows from the current frontier.

If my local terminal may be ahead of GitHub, ask me for fresh `git status`, `git log -1 --oneline`, branch output, or pytest output rather than guessing.

## Step 4 — Preserve the recovered architectural trajectory

Unless `PROJECT_STATE.md` records a later change, the recovered trajectory is:

**targeted Study**
-> **competency evidence**
-> **Replay integration**
-> **Forward validation**
-> **progression / eligibility**
-> **Live Execution**

with Review / Development synthesis and Evidence Maturity becoming stronger after the evidence substrate is trustworthy.

The project had deliberately shifted away from further Live-Watch embellishment toward the Study/Lab learning and progression loop.

Do **not** automatically move priority back toward:

- Film Night polish,
- responsive chart galleries,
- broad visual styling,
- additional Live-Watch widgets,
- deep TradingView integration,
- macro-pad/SpaceMouse hardware,
- KPI dashboards,
- automatic readiness scores,
- arbitrary proficiency thresholds,
- NinjaTrader live execution,

unless current repository state or new operator feedback makes one of them blocking.

## Step 5 — Preserve key architecture constraints

Treat these as important unless a later accepted repository decision supersedes them:

- The Cockpit is a **trading-process operating system**, not primarily a P&L dashboard.
- A compliant **No Trade / Stand Down** can be a successful outcome.
- Structured records are authoritative; summaries/images are derived views.
- Trade Plan Foundation/Rules define constraints; Playbooks define methods; Process operates; Review/Development improves.
- Process Blueprint uses Mode / Deck / Station concepts.
- Station work separates **Action -> Observe -> Carry Forward**.
- Focus and Deck are two projections of the same process state.
- Navigation does not silently certify completion.
- Persistence should restore operator orientation and unfinished state.
- Return to Analysis is deliberate, not punitive.
- Market sessions are context; do not automatically restore the earlier architecture where every Asia/London/NYAM/NYPM session is a mandatory separate run.
- Normally one Trading Run spans the active decision process; additional runs are deliberate exceptions.
- America/New_York is canonical market time; futures day rolls at 18:00 ET.
- Live/Replay/Backtest/Forward share a common process/data substrate, but interface emphasis may differ by purpose.
- Historical Backtest/Lab = Study.
- Replay = Rehearsal.
- Forward Test = Validation.
- Live = Execution.
- Environment and Study Intent/Purpose are separate concepts.
- Eligibility is separate from environment purpose.
- Account/capital context comes after eligibility; it is not a peer environment.
- Moving up the training ladder should eventually require evidence; moving down should be frictionless.
- Eligibility regression, temporary pause, and insufficient evidence are distinct reasons for restriction.
- Competency definition, competency state, and competency evidence are separate.
- Competency definitions are Trade Plan-owned/versioned.
- Do not invent proficiency percentages, automatic promotion/demotion, hard Live locks, or thresholds before evidence rules justify them.
- Raw market-time/QT facts, AMDX interpretation, probability, opportunity ranking, and authorization are separate layers.
- Named Playbooks are useful scaffolds but should not be the only possible opportunity source.
- Setup criteria and run-wide safety/authorization gates are separate.
- Authorization is not order submission.
- Historical records must retain enough revision/snapshot provenance to reconstruct what rules they operated under.
- Workbench configuration should evolve from actual configuration/research needs rather than becoming a generic shell for its own sake.
- TradingView remains the primary visual charting environment unless a later decision changes that.
- NinjaTrader execution comes only after the safety/authorization state machine is proven.

## Step 6 — Development discipline

Before implementing a substantial slice:

1. verify current branch and baseline,
2. state which current milestone/frontier the slice serves,
3. keep the slice small and vertical,
4. avoid opportunistic scope expansion,
5. add/update automated tests,
6. request/run relevant manual acceptance,
7. update `PROJECT_STATE.md`,
8. add durable decisions to `DECISIONS.md`,
9. update `DECISION_AUDIT.md` if a prior choice was refined/superseded,
10. update `PROJECT_EVOLUTION.md` if the project changes architectural phase,
11. merge only a known-good checkpoint.

Do not update `PROJECT_REQUIREMENTS.md` merely to mirror a transient implementation or old chat artifact. It should describe the accepted current product and roadmap.

## Step 7 — Communication style for this project

Favor architecture correctness over rapid feature output.

When something is uncertain, distinguish:

- **fix now because the current slice owns it**,
- **record as a later requirement**,
- **leave open because evidence is insufficient**.

I am comfortable doing substantial manual testing and prefer that important workflow/schema/risk/time changes receive both automated and manual validation.

Before coding, summarize your recovered understanding and wait only if you find an actual conflict or open decision that materially changes the next slice. Otherwise continue from the verified current task.

---

End of startup prompt.
