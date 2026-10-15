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
5. `docs/SYSTEM_GUIDE.md`
6. `docs/PROJECT_EVOLUTION.md`
7. `docs/HANDOFF.md`
8. `docs/SMOKE_TEST.md` when testing/acceptance context is relevant
9. relevant current code and tests

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

Latest frontier: AMDX PRs #67–75 are merged into `main`, schema v46 / Alpha 0.7. Final code merge `8b7f8ae0e8e6da76bed266f771fce75d4bfaaefb` has the exact reviewed consolidation tree from `15e64af8d51f946696e9927b5ce731857bdc8602`. Complete validation: 1,136 PASS / 89 isolated modules / 450.24s; all 20 operator checks 261–280 PASS. Read the latest `PROJECT_STATE.md` and `AMDX_CONSOLIDATION_REVIEW.md`. User sync/database backup is documented in `AMDX_MAIN_SYNC_GUIDE.md`; preserve local smoke notes and earlier stashes. Native UI work has not begun. First read `UX_CONTEXT_RECONCILIATION.md`, `UX_FRICTION_RESEARCH.md`, `UX_DESIGN_TOUCHSTONES.md`, `UX_INTERACTION_STANDARDS.md` and `WORKSPACE_PARITY.md`. TDA parity, Study-first Lab and complete Watch are directionally accepted checkpoints; final integrated/native judgment remains open. The Watch reference-and-decision dock passed its bounded operator review and is now the accepted contextual-completion exemplar: exact target, legal choices, one existing command, synchronized state, dismissal and focus return. Stop standalone Watch polishing. The selected next milestone is `WATCH_NATIVE_DECISION_DOCK_SLICE.md`, a thin native projection over the current shared AMDX command and current Watch shell. Alpha 0.7 contains no published AMDX manual-reference definition; show truthful unavailability until a versioned plan supplies it. Study Find integration, broader quiet-Watch recomposition and Study-first routing follow this proof. Monitor relationship belongs to future global Workspace & Displays settings. P&L, order submission and real broker policy remain absent.

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

Unless `PROJECT_STATE.md` records a later change, Milestone B — Review / Development synthesis is complete.

The accepted human synthesis chain is:

**Competency Evidence**
-> **Competency Synthesis**
-> **Cross-Run Observation**
-> **Development Direction**
-> **targeted Study routing**

Milestone C — Evidence Maturity and progression governance is complete:

**C1 Evidence Maturity Profile**
-> **C2 Progression Policy model**
-> **C3 Explainable Eligibility evaluation**
-> **C4 Regression / downgrade semantics**
-> **C5 Operator-loop integration and guardrails**

Historical roadmap statement: **Milestone E — Context maturity: QT/AMDX, news, and distortions** was the next frontier at this earlier checkpoint. Its shared AMDX foundation is now merged; use the current UX/Study planning frontier above. Milestone D remains parallel and should be activated only by friction observed through actual operator use.

Evidence Maturity is boundary-aware from v0 and is keyed conceptually by:

**Trade Plan + competency + progression boundary**

Candidate boundaries are Study -> Rehearsal, Rehearsal -> Validation, and Validation -> Execution.

Do not collapse Evidence Maturity, Competency State, Progression Policy, and Eligibility. Do not invent numeric readiness percentages, hidden weighted scores, automatic advancement/demotion, or Live locks before explicit policy exists.

The project remains deliberately shifted away from further Live-Watch embellishment toward the learning/progression loop.

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
