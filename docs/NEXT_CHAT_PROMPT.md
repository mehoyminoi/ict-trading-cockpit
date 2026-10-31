## Local correction — full-size chart blocked by investigation modal

Published draft #107 (`b1005cc`) operator 358 exposed parentless image-window ownership: chart was blocked behind the modal investigation. Local correction uses an owned window-modal image dialog with Close/Escape and native-resolution scrolling. Ten targeted tests PASS including modal ownership and independent closure. 358 retest pending; 359 unreported. Same branch `feature/study-overview-reading-v0`, update #107 when authorized; do not merge. No schema changes.

## Current local slice — investigation overview reading

Operator 356–357 PASS on published draft #106 (`ca3e626`); actionable recovery endorsed suite-wide and recorded in UX_INTERACTION_STANDARDS.md. `feature/study-overview-reading-v0` adds capture previews, compact saved-context disclosure and read-only checkpoint browsing to the existing overview. Existing review/input/image owners retained; schema 53 unchanged. See `STUDY_OVERVIEW_READING_V0.md`, pending 358–359. 21 focused tests PASS plus seven affected checks rerun after render adjustments. Local only: draft stacked on #106 when authorized; do not merge. No new full-session exercise.

## Current local slice — Study workspace clarity

Connected natural Study review accepted: real-question material restored intent, emerging common threads useful; density and an inconspicuous unfinished-capture guard are the next UX targets. `feature/study-workspace-clarity-v0` groups primary vs supporting controls, explains read-only questions, provides direct navigation from a blocked switch, and filters existing overview material without replacing review state. No schema change (53). See `STUDY_WORKSPACE_CLARITY_V0.md`. Operator 356–357 pending; local only, draft stacked on #105 when authorized; do not merge. No new full-session exercise required.

## Current checkpoint — connected Study workflow review

Operator 355 PASS on published draft #105 (`f537759`), stacked on #104; unmerged. Schema 53. The component-level Study loop is accepted; the connected natural-session/return-visit review is pending. Read `STUDY_CONNECTED_WORKFLOW_REVIEW.md` for the current sequence, control distinctions, limits and next gates. Use the durable `~/ict-study-workspaces/study-v0`, never the older temporary narrative fixture. No application changes, new operator smoke number, publication or merge in this documentation checkpoint. Earlier entries below are chronological history and may describe now-completed work.

## Current local slice — questions from review

Operator 354 PASS on published #104 (`40f8069`). `feature/study-review-question-capture-v0` exposes the existing question-capture interaction at the review pause: selected prompt text saves directly, no selection opens the existing composer. Frozen review/investigation provenance distinguishes draft snapshots from saved checkpoints; no fake capture or market reference is created. Schema 53 reader barrier, existing question v1 preserved. Back up durable workspace before upgrade. See `STUDY_REVIEW_QUESTION_CAPTURE.md`; 355 pending. Publish draft stacked on #104 only when authorized; do not merge.

## Current local slice — Study reference alignment

Operator 352–353 PASS on published #103 (`5a6df7b`). `feature/study-reference-alignment-v0` adds visible retained/selected references, navigation to existing calendar controls and explicit atomic alignment for an unlinked draft in its current investigation. Content/images and identity remain, saved associations are protected. Schema 52 unchanged. See `STUDY_REFERENCE_ALIGNMENT.md`, pending 354. This cannot detect TradingView's date and does not correct already-saved receipts. Next: question capture directly from review. Publish draft stacked on #103 only when authorized; do not merge.

## Current local slice — investigation resumption

Operator 351 PASS on published #102 (`fac47c4`). Original temporary directory was absent; recovery used the verified archive and the operator confirmed meaningful material and image behavior in the durable workspace. Continue from `~/ict-study-workspaces/study-v0`, not `/tmp`.

`feature/study-investigation-resume-v0` adds schema-52 registry and per-capture opening context. Authored drafts block switching until saved/discarded. Current-revision historical wording choices are explicit; resumed questions are read-only, source snapshots unchanged. Calendar reference is retained, not inferred. See `STUDY_INVESTIGATION_RESUME.md`; 352–353 pending. Back up the durable workspace before upgrade. Local only; publish draft stacked on #102 when authorized; do not merge. Full lifecycle/revision and multi-draft editing deferred.

## Current local slice — durable Study workspace

Operator archive verification PASS (schema 51, one referenced image). `feature/study-durable-workspace-v0` restores a verified archive into a new directory and resolves historical Study image paths through an explicit origin manifest. Database records remain unchanged; no fallback to original images. See `STUDY_DURABLE_WORKSPACE.md` for checkpoint 351, pending. Requires a current archive to include newer work. Pending capture destination limitations are not fixed here; investigation continuity remains next. Publish only when authorized, draft stacked on #101; do not merge.

## Current local slice — isolated Study backup verification

`feature/study-backup-verification-v0` adds `tools/verify_study_backup.py` and `STUDY_BACKUP_VERIFICATION.md`. Five targeted tests use the actual schema. Real operator archive verification is pending; archive creation alone is not recovery verification. No application/schema change or durable relocation yet. Absolute paths in immutable source snapshots require a deliberate resolver/relocation design; do not rewrite history. Includes preceding natural-session and dependable-workflow documentation. Publish as draft stacked on #100 only when explicitly authorized; do not merge.

## Current priority — dependable daily workflow, 2026-10-30

Operator explicitly prioritizes dependable personal Study/TDA/Watch integration over exploratory/nicety work and requests active scope control. Read `DEPENDABLE_WORKFLOW_MILESTONE.md` and `STUDY_INVESTIGATION_CONTINUITY_V0.md`. Backup archive creation is operator-reported; restore and durable workspace transition remain unverified. Next implementation must couple investigation registry/resumption with safe draft destination handling; pending capture context is currently in-memory, so a selector alone is insufficient. Full lifecycle and chart reconstruction deferred. This is a local design/documentation checkpoint, no production/schema changes or new publication.

## Natural Study acceptance and continuity needs

Published draft #100 (`a744dc9`) stacked on #99, unmerged; operator 350 PASS. Natural session produced useful observations and questions and strengthened acceptance of optional review pauses. Read the latest `STUDY_REAL_SESSION_FINDINGS.md` before new implementation. Priorities: preserve real material currently mixed with the synthetic `/tmp` fixture; specify investigation registry/resumption and deliberate revision; resolve repeated reference-date friction and offer question capture at review's point of need. No automatic competency claims; lifecycle states and chart reconstruction remain design proposals. This documentation update is local only.

## Current local slice — direct Study review entry

`feature/study-direct-review-v0` applies the accepted task-directed-entry requirement using the existing overview/review editor. Direct Review this investigation opens review immediately; ordinary overview remains collapsed. Hide preserves text/support and the existing close guard. History and schema 51 unchanged. Includes the preceding requirements documentation and operator 348–349 PASS. See `STUDY_DIRECT_REVIEW.md` for bounded checkpoint 350 (pending) and the subsequent natural-study evaluation. Publish only when authorized, as a draft stacked on #99; do not merge. No analytical prioritization or competency assessment is implemented.

## Current checkpoint — Study history accepted; task-directed entry required

Published draft #99 (`feature/study-history-browser-v0`, `fedd532`), stacked on #98; unmerged. Operator 348–349 PASS. Read-only cross-investigation retrieval is accepted, not analytical prioritization or competency assessment. This local documentation checkpoint records acceptance and the important suite-wide task-directed-entry requirement in `UX_INTERACTION_STANDARDS.md` and `PROJECT_REQUIREMENTS.md`.

Next bounded implementation: a direct Review this investigation route into the existing overview with its review editor already revealed; ordinary inspection remains collapsed and history remains retrieval-only. Preserve shared ownership, scope, drafts and close guards. Do not build a second review form or reverse all defaults. After that, use a natural study pause to evaluate the capture → finding → review → history loop before expanding analytical prioritization. No new operator test is needed for this documentation-only checkpoint. No UI/schema change, new publication or merge claimed.

## Current local slice — cross-investigation Study history

345–347 operator PASS on published #98 (`93ce461`). Recording simultaneous study outcomes is accepted; selecting what to study next through analysis is not yet implemented. Preserve the recording/analysis distinction in `STUDY_REAL_SESSION_FINDINGS.md` and requirements. `feature/study-history-browser-v0` adds read-only cross-investigation retrieval of questions, findings/partial answers and review checkpoints for the current plan, across revisions, through text and type filters. No inferred deficiencies, scoring, task replacement or source writes. Schema 51 unchanged. See `STUDY_HISTORY_BROWSER.md` for pending 348–349; use the retained review fixture. Local only; publication as draft stacked on #98 requires authorization. Do not merge.

## Current local implementation — investigation review checkpoint

The operator accepted the proposed checkpoint, emphasizing optional reflection and simultaneous study outcomes rather than another required form. `feature/study-review-checkpoint-v0` adds a hidden-by-default review area within the existing overview, optional prompts, explicit support snapshots and immutable checkpoint history. Schema 51; use a new separate fixture. 228 targeted tests PASS. Read `STUDY_REVIEW_OPERATOR_GUIDE.md` for pending 345–347. No competency/run/eligibility writes or automatic completion. 343–344 PASS remains recorded. This branch also includes the local design/acceptance documentation atop published #97; publish as a draft stacked on #97 only when authorized. Do not merge.

## Next design checkpoint — investigation review (2026-10-29)

343–344 operator PASS on #97. Capture-loop correction is accepted; return to broader Study-to-Review work. `STUDY_REVIEW_CHECKPOINT_V0.md` inventories existing overview/findings and proposes a small investigation-owned review: current understanding, uncertainty/counterexamples, next study step, with explicit supporting-source references. Existing competency evidence requires a run; independent investigations must not manufacture one or silently become proficiency evidence. No review implementation, schema change, publication or merge in this documentation checkpoint. Review the bounded contract before building it; no new smoke test requested yet.

## Current local slice — next Study capture

341–342 operator PASS. Branch `feature/study-next-capture-v0` starts from published #96 (`53ce5b8`). Both full Study save actions prepare a new capture; link-only and failed saves preserve the current form. View last saved opens a separate read-only inspector. Opening-context defaults carry over and can reseed untouched forms through calendar reentry. Watch dock semantics stay unchanged. See `STUDY_NEXT_CAPTURE.md`, pending 343–344. Schema 50 unchanged. Local only; do not merge. Next return to broader Study-to-Review work after this bounded correction.

## Current local slice — save to investigation

Operator 338–340 PASS on #95. `feature/study-save-to-investigation-v0`, based on published `b8510d2`, combines content, ordered image references, explicit association and draft removal in one transaction. Save destination is beside the save controls; plain save remains available, and link-only moves to More. Context differences require explicit confirmation for combined save; existing associations cannot be reassigned. Schema 50 unchanged. 67 targeted tests PASS. Read `STUDY_SAVE_TO_INVESTIGATION.md` for pending 341–342. Local only; publication as a draft stacked on #95 still requires authorization. Do not merge.

## Current local slice — Study findings / partial answers

Operator accepted #94 post-discard context recheck on 2026-10-28. Based on published `6908b14`, branch `feature/study-findings-v0` adds independent findings with optional explicit investigation association; partial answers require it. Read `STUDY_FINDINGS_V0.md` for scope and operator checkpoints 338–340 (pending). Schema 50; use a new separate fixture. Existing question quick capture remains intact. No investigation completion, validated-answer status, automatic source-capture link or competency evidence. Screenshot workflow is accepted and refinements deferred. This slice is local only until explicitly authorized for publication as a draft stacked on #94; do not merge.

## Current delivery checkpoint — 2026-10-28

Screenshot capture and Cockpit paste are operator-accepted on KDE/X11; further refinement is deferred. Prepared branch `feature/study-discard-context-fix-v0` contains the untouched-discard context correction and narrative-session feedback, based on #93 acceptance `f410179`. Publish as a draft stacked on #93 only after explicit publication authorization; do not merge. Targeted operator recheck is documented in `STUDY_DISCARD_CONTEXT_FIX.md`. Next implementation priority is retaining a Finding/partial answer with explicit investigation association.

## Narrative-session findings — 2026-10-28

Post-discard context handoff defect confirmed and locally corrected; see `STUDY_DISCARD_CONTEXT_FIX.md`. Updated `STUDY_REAL_SESSION_FINDINGS.md` records Finding/partial-answer capture as the next learning blocker, Link/Save control integration, screenshot shortcut troubleshooting and accepted calendar orientation cues. Pause additional narrative-session requests until these reported blockers are addressed. No new smoke pass inferred; no automatic finding-to-evidence promotion. Local correction and documentation are not published yet.

## Current next step — narrative/context Study session

Operator 336–337 PASS is published at `f410179`. Local documentation-only branch `docs/study-narrative-session-v0` prepares `STUDY_NARRATIVE_SESSION_GUIDE.md`: one familiar historical day to evaluate Observation/Notes, time/timeframe context and HTF narrative. This follows the agreed real-session findings sequence; no new production change or numbered smoke gate. Use the existing accepted application. Gather qualitative feedback before adding fields or a larger task-promotion workflow. No publication or merge claimed for this documentation checkpoint.

## Current local increment — discard unfinished Study capture

Operator 334–335 PASS; retain the dual selected-text/direct-save and empty-selection/composer behavior. Discoverability is parked for later optimization. `feature/study-draft-discard-v0` adds confirmed current-draft discard with autosave cancellation, new identity, retained date/instrument/session and preserved saved records/questions/source references. Schema 49 unchanged. See `STUDY_DRAFT_DISCARD.md`; checks 336–337 pending. No publication or merge claimed by this local checkpoint.

## Current local increment — direct question capture

331–333 PASS published at `6454e04`. `feature/study-question-quick-capture-v0` removes the mandatory composer for selected text, retaining source snapshots and in-place confirmation/failure feedback. Empty selection still opens the optional composer. Schema 49 unchanged. Read `STUDY_QUESTION_QUICK_CAPTURE.md` for pending 334–335; no repeat of earlier tests. No publication/merge claimed by this local checkpoint.

## Current implementation — Study question inbox

Capture-context targeted checks all PASS; the operator endorses quiet, metered mismatch guidance. The next local branch is `feature/study-question-inbox-v0`, based on published #90 head `212ddcf`. Read `STUDY_QUESTION_INBOX_SLICE.md` and the operator guide before older entries. Schema 49 adds independent question/source snapshots. Keep a question from Study Find, inspect it from the investigation and return without replacing current work. Operator 331–333 pending. No automatic task promotion, competency evidence or question ranking. Keep draft/unmerged; no publication is claimed by this local checkpoint.

## Current implementation — capture-context continuity

Local `feature/study-capture-context-v0` implements the next slice from real-session feedback. See [STUDY_CAPTURE_CONTEXT_SLICE.md](STUDY_CAPTURE_CONTEXT_SLICE.md): new capture suggestions from inspected context, preserved unfinished drafts with visible mismatch guidance, and fresh entry after a saved capture. Schema 48 unchanged. Configurable global instrument preference and the follow-up-question inbox remain later work. Targeted operator recheck pending; no publication or merge claimed.

## Latest qualitative Study checkpoint — 2026-10-27

Operator 328–330 PASS and save-feedback correction recheck accepted. Real chart-assisted Study exposed a wrong-date capture handoff, desired selected-session/default-instrument suggestions, and a concrete need to park follow-up questions without losing the current inquiry. Read [STUDY_REAL_SESSION_FINDINGS.md](STUDY_REAL_SESSION_FINDINGS.md) before new work. Next recommended slice: capture-context continuity, followed by a bounded Study question inbox. This supersedes the earlier generic next-step wording below. Current fields remain provisional; vocabulary linking, multiple moves and confluence sequences are exploratory directions. No new operator smoke pass or market classification is inferred from the qualitative session.

## Current checkpoint — 2026-10-26

Operator 325–327 PASS is published at `51ba1e5`; schema 48. The next accepted milestone is **Study investigation overview and return loop**, on `feature/study-investigation-overview-v0`. Read `STUDY_INVESTIGATION_OVERVIEW_SLICE.md` and its operator guide (328–330 pending). It composes existing explicitly linked captures and saved criterion results without new evidence/adoption semantics. No merge is authorized.

Near term: review this connected session, then use a realistic chart-assisted Study question to determine the next Study-to-Review handoff. Preserve the broader Lab identity; AMDX is one foundational lens. Further comparison dashboards, automatic scoring and isolated AMDX polishing remain deferred.

The dated entries below are historical checkpoints, not competing next-step instructions. Where they say pending/next, use this current checkpoint and the latest operator results instead.

Newest frontier: multi-day criterion Study on `feature/study-multiday-criterion-v0`, based on 321–324 PASS `1258b43` (draft #87). See `STUDY_MULTIDAY_SLICE.md` and guide 325–327. Explicit date navigation retains criterion/question, clears observation values/sources, preserves independent saved results, and leaves the calendar alone. Schema 48 unchanged. Explain full-program purpose and review scope before each operator trial. Keep draft/unmerged.

Newest frontier: integrated criterion Study on `feature/study-criterion-evaluation-v0`, based on 318–320 PASS `2b9fca5`. Schema 48 adds independent immutable Study results; no fake run or adopted criterion. See `STUDY_CRITERION_SLICE.md` and operator guide 321–324. User requested clearer orientation: explain where each round fits, what it enables and what they are judging. Seeded synthetic demo avoids repeating criterion setup. Keep draft/unmerged.

Newest frontier: UX4c reusable selected-quartet input scopes on `feature/amdx-reusable-scopes-v0`, based on operator 313–317 PASS `cf9f660` (draft #85). See `AMDX_REUSABLE_SCOPES_SLICE.md` and operator guide for 318–320. Fixed identities remain unchanged; reusable positions bind only within the selected quartet, with layer checks and retained evaluation binding trace. New scoped evaluations use v2; old fixed-only payloads remain v1. No schema change. Keep PRs draft/unmerged. Next: deliberate evidence/fact selection and saved evaluation in Study.

Newest frontier: UX4b contextual Study criteria browser/editor on `feature/study-criteria-editor-v0`, stacked on draft #84. Operator 313–317 pending; see `STUDY_CRITERIA_EDITOR_OPERATOR_GUIDE.md`. Candidate saves are independent, immutable and never publication/adoption/evaluation. Explicit input scopes remain cycle-specific; recurring bindings and empirical evaluation are not complete. No schema change; keep draft/unmerged.

Newest frontier (2026-10-21): operator 311–312 PASS. UX4a independent candidate-definition revisions are implemented on `feature/amdx-criteria-revisions-v0`; see `AMDX_CRITERIA_REVISIONS_SLICE.md`. No new UI trial or schema change. Next is a contextual candidate editor using this registry; do not claim the whole UX4 milestone complete or infer automatic publication/adoption. Multi-monitor mode-aware companion requirements are recorded for later refinement. Keep PRs draft/unmerged.

# ICT Trading Cockpit — Next Chat Startup Prompt

Latest: 306–310 PASS in published `bbf44f8`. Shared MainWindow/Study Review restoration is the next bounded slice (`WORKSPACE_RESTORATION_SLICE.md`); 311–312 pending. Preserve plan-driven layout versus workstation geometry distinction. No merge authorized. Criteria study/authoring follows this shared-shell closure.

Latest frontier: integrated Study checks 301–305 PASS, published as `6b04866`. Native mapped Focus is the next bounded UX3 trial on `feature/tda-mapped-focus-v0`; read its slice and operator guide before older frontier entries. The current first Deck contains five stations; final four-chart content assignment remains open. No merge authorized.

Latest checkpoint (2026-10-17): quiet-Watch checks 291–295 PASS. Study-first routing is implemented locally on `feature/study-first-startup-v0`; read `STUDY_FIRST_STARTUP_SLICE.md`, its operator guide and the newest `PROJECT_STATE.md` entry before older frontier text. Startup was published as `81468de` in draft PR #80, stacked on #79. Operator checks 296–300 PASS (2026-10-20); smoke notes are saved on the operator’s workstation but not yet pushed. Next planned milestone is UX2 — Integrated Study task. Preserve local smoke notes; no merge is authorized.

Latest local follow-up: `feature/integrated-study-task-v0` implements the schema-47 retained investigation/capture association trial. Read `INTEGRATED_STUDY_TASK_SLICE.md`, its operator guide and newest PROJECT_STATE entry. No publication or merge; 301–305 pending. Operator startup smoke results from remote head `953c812` are incorporated.


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

Latest frontier: AMDX PRs #67–75 are merged into `main`, schema v46 / Alpha 0.7. Native decision-dock checks 281–285 and contextual Study Find checks 286–290 PASS in draft PRs #77–78. The next slice is implemented on `feature/watch-quiet-composition-v0`; read `WATCH_QUIET_COMPOSITION_SLICE.md` and its operator guide. It coordinates one profile-aware chart edge, the existing Live Watch, a compact projection of the maintained AMDX source/command and a fixed safety strip. Broker/account/risk/position/order facts remain explicitly unavailable, P&L and commands absent. Checks 291–295 remain pending. Do not infer final styling/layout, broker integration or merge authorization. After bounded review, Study-first startup routing is next. Preserve local smoke notes and earlier stashes.

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
