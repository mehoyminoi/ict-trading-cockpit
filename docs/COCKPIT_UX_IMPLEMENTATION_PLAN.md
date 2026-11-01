## Current checkpoint — 2026-10-26

Operator 325–327 PASS is published at `51ba1e5`; schema 48. The next accepted milestone is **Study investigation overview and return loop**, on `feature/study-investigation-overview-v0`. Read `STUDY_INVESTIGATION_OVERVIEW_SLICE.md` and its operator guide (328–330 pending). It composes existing explicitly linked captures and saved criterion results without new evidence/adoption semantics. No merge is authorized.

Near term: review this connected session, then use a realistic chart-assisted Study question to determine the next Study-to-Review handoff. Preserve the broader Lab identity; AMDX is one foundational lens. Further comparison dashboards, automatic scoring and isolated AMDX polishing remain deferred.

The dated entries below are historical checkpoints, not competing next-step instructions. Where they say pending/next, use this current checkpoint and the latest operator results instead.

# Whole-cockpit UX and Study implementation plan

**2026-10-20 operator checkpoint:** startup 296–300 and integrated Study 301–305 PASS. Next bounded UX3 work is adjacent native TDA map/Focus, as described in `TDA_MAPPED_FOCUS_SLICE.md`. It preserves the current five-station first Deck; it does not silently adopt the earlier prototype’s four-station content.

**2026-10-17 implementation checkpoint:** quiet-Watch checks 291–295 PASS. The [Study-first startup slice](STUDY_FIRST_STARTUP_SLICE.md) now implements the bounded idle-Study / active-runtime routing policy below. Operator checks 296–300 PASS (2026-10-20); the operator’s smoke-test file is saved locally and awaiting push. UX2 — Integrated Study task is the next planned milestone. Recommendation ordering and final Lab topology remain provisional; no complete integrated Study workspace is claimed.

**Status:** Proposed implementation plan for operator review, 2026-10-13. Accepted behavioral requirements are identified below; the workspace arrangement, startup policy and slice sequence are developer recommendations. Reviewing this document or the accompanying interactive walkthrough does not accept final styling, recommendation ranking or a production UI rewrite.

**Review hold — operator feedback, 2026-10-13:** The synthetic walkthrough is not accepted as a mature layout. The operator reports density, homogeneous sections, scattered AMDX context and loss of guided Focus versus accessible Deck. Read [the recovered-context comparison](UX_CONTEXT_RECONCILIATION.md) before another renderer or native UX slice. The original proposal below remains available as the comparison point; adjacency, calendar presentation, support-tool access and usability exits require reconciliation. No UI changes are authorized by this feedback record.

**Research discussion — 2026-10-13:** [UX friction research](UX_FRICTION_RESEARCH.md) adds professional methods, proposed UX-F01–F12 quality criteria and a future news/calendar/quarter-stack presentation direction. Discuss these with the reconciled task journeys before choosing controls or proceeding with a native slice. The original layout and UX1–UX4 sequence remain proposals; no renderer revision is implemented by this checkpoint.

**Focused interaction review — 2026-10-13:** [TDA layout parity](TDA_LAYOUT_PARITY_INTERACTION_SPEC.md) is the first corrected journey specification. Its [standalone prototype](prototypes/tda-layout-parity-v0.html) successfully validated four-pane TradingView-to-Cockpit correspondence, mapped Deck → Focus → unchanged Deck return, shared station work, quiet inactive panes and peripheral orientation cues. The [operator review](TDA_LAYOUT_PARITY_OPERATOR_REVIEW.md) accepts that direction and allows however many revision-defined mapped TDA Decks the analysis requires. Final styling, TDA content, control bindings and native implementation remain open.

**Second focused journey — partially successful, 2026-10-14:** [Quiet Watch and support return](WATCH_QUIET_SUPPORT_INTERACTION_SPEC.md) and its [operator review](WATCH_QUIET_SUPPORT_OPERATOR_REVIEW.md) establish Study Find access/return, direct legal active-cycle entry and peripheral reacquisition as strong directions. The flat AMDX list and enlarged inspection view are not accepted as the nested full-stack experience. The fixture corrects saved-field clearing, stable Full Stack return placement and excessive quiet-state emphasis. History/comparison, automatic classification and real persistence remain absent.

**Lab journey — AMDX directional checkpoint accepted:** The [operator review](LAB_AMDX_CALENDAR_TREE_OPERATOR_REVIEW.md) confirms the initial AMDX Lab direction is satisfied and isolated polishing should stop. Carry forward the tree/workspace/support-rail relationship, Follow Current, truthful unavailable state, real calendar, calendar Quiet/Nested/Deep, neutral hierarchy and restrained named-session color shared with chart indicators. This is not final AMDX Lab approval: real historical editing, temporal movement, evidence/definitions/news, broader Lab composition, integration and native use remain. The [standalone prototype](prototypes/lab-amdx-calendar-tree-v0.html) is now reference only. Next compose the broader Study-first Lab—competency/question guidance, chart evidence and Study Finds, criteria/definitions, sample work and routes to TDA/Watch/Review—with AMDX Calendar as one lens. Revisit unresolved zoom only when that integrated workflow supplies a concrete use case.

**Broader Study-first Lab — directional checkpoint accepted:** The [operator review](LAB_STUDY_WORKBENCH_OPERATOR_REVIEW.md) reports that the broad layout and front-and-center **Study this competency** doorway are a good start with no immediate first-inspection friction. The Study map / workspace / contextual-rail composition and coordinated Study Plan, Evidence, Criteria, Samples and AMDX Calendar lenses may carry forward without another isolated polish pass. This is not final Lab approval: acclimation, repeated use and a realistic end-to-end Study/Replay session must still test the full workflow. Exact controls, styling, native behavior and integration remain open. Next compose the complete Watch experience—including broker/process-safety projection and monitor-orientation profiles—before selecting the smallest native slice.

**Complete Watch composition — native trial developer verified:** The [interaction specification](WATCH_COMPLETE_COMPOSITION_INTERACTION_SPEC.md), [operator review](WATCH_COMPLETE_COMPOSITION_OPERATOR_REVIEW.md) and [standalone prototype](prototypes/watch-complete-composition-v0.html) retain the accepted quiet/current-state Watch behavior, compact nested AMDX, restrained setup cues and always-visible broker/process-safety facts. The chart-adjacent [native decision dock](WATCH_NATIVE_DECISION_DOCK_SLICE.md) is accepted through checks 281–285 and [contextual Study Find](WATCH_CONTEXTUAL_STUDY_FIND_SLICE.md) through checks 286–290. The [native quiet-Watch composition slice](WATCH_QUIET_COMPOSITION_SLICE.md) now coordinates those interactions with the existing Live Watch, a compact maintained-AMDX projection and truthful safety strip; developer verification is 1,155 PASS across 95 isolated modules and checks 291–295 remain pending. Broker/account/risk/position/order facts remain explicitly unavailable, P&L and commands absent. After this bounded trial, Study-first routing is next; final styling and global Workspace & Displays UI remain later work.

**Verified baseline:** main `6aa8d4ec990d8d371440271278bbb7368f186a64`, schema v46, Trade Plan Alpha 0.7. AMDX PRs #67–75 are merged. The integrated code tree retains 1,136 PASS across 89 isolated modules and operator PASS for checks 261–280. This planning checkpoint changes documentation only; it introduces no schema, plan, runtime or smoke-result change.

## 1. What this screen is for

The Cockpit is the primary process and learning workspace. Its mature composition should help a tired technician choose useful Study work, keep market context visible while doing it, and carry the resulting observations into deliberate Review and further practice. Live operation remains directly reachable through the same process substrate.

Design around a primary 16:9 desktop workspace, with external charts and journals arranged around it. Available window geometry still governs reflow. The accepted 16:9 override replaces the old smaller companion-window target; it does not force fullscreen, a fixed aspect ratio or a particular resolution.

The organizing principle remains: **Focus supports the operation at hand; Deck supplies the spatial analytical overview.** In TDA, Deck also preserves layout parity with the external TradingView deck: corresponding chart and station panes retain the same physical positions and reading order so the two monitors behave like facing pages. Focus and Deck are nearby projections of the same state; selecting a mapped pane opens its detailed operation and returning restores the map. Whole-stack AMDX orientation stays quiet and accessible; selected context, definitions and task detail remain coherent with it. See [Workspace Parity](WORKSPACE_PARITY.md) and the [design touchstones](UX_DESIGN_TOUCHSTONES.md).

This plan is the bridge between the completed architecture and native UI development. The interactive walkthrough explores information placement and transitions. It is synthetic, local and disposable: it does not connect to the repository database, calculate eligibility or classify price action.

## 2. Existing capabilities and remaining presentation work

| Area | Implemented at the baseline | Presentation still to build |
| --- | --- | --- |
| Trade Plan | Revisioned process, playbooks, competencies, rules and progression governance | A coherent route to definitions and controlled revision from the working context |
| Process | Shared launcher and TDA → Watch → Market/Process Review; explicit environments and intent | Common workspace chrome, adjacent station overview/detail and clearer return paths |
| Study | Targeted competency staging, Historical Backtest intent, Study Find capture/drafts and Study Review | Study-first doorway and an integrated question → investigate → capture → review experience |
| Learning governance | Evidence, synthesis, cross-run observation, Development Direction, Evidence Maturity, eligibility and attainment/revalidation | Selectively visible reasons and next actions, with detailed records available when needed |
| AMDX | One maintained instrument calendar; manual all-layer historical entry; native TDA/Watch/Lab binding; immediate quartet revision; exact run captures; independent Observed Review | Quiet and spacious renderers sharing those actions; nearby overview/detail; usable criteria/evidence authoring |
| Workbench | Summary-template authoring | Further tools only when required by an explicit authoring task |
| External context | Retained event/provider snapshots and plan-scoped context predicate foundation | Purposeful event/evidence inspection and empirical research; actual policy adoption stays explicit |

The present MainWindow has seven top-level tabs: Trade Plan, Guided TDA, Study Find, Trade Summary, Study Review, Workbench and AMDX Lab. These are existing access paths, not seven mandatory steps or the mature navigation design. Milestones A–C and the integrated AMDX foundation must not be rebuilt because an older roadmap paragraph calls them unfinished.

## 3. Shared shell and workspace map

Recommend four primary destinations—Study, Process, Review and Plan—with authoring tools reached from the relevant Plan/Review task. TDA and Watch are process modes, not additional parallel workflows. The walkthrough exposes TDA and Watch separately so their different presentation needs can be tried directly; that does not commit the mature application to five top-level tabs.

| Destination | Primary question | Nearby overview | Focused work and return path |
| --- | --- | --- | --- |
| Study / Lab | What am I investigating, and what would help me learn next? | Spacious full AMDX stack at an explicit studied reference, selected question and competency | Selected quarter/context, governing definitions, observations and Study Find capture; return to the question without losing reference or draft |
| Process / TDA | What is my thesis, and which analysis operation am I completing? | Quiet higher AMDX context plus station map and completion state | Current station, required decisions, notes and deliberate Complete & Continue; inspect context without advancing the process |
| Process / Watch | Where am I now, and what valid action am I waiting for? | Quiet whole-stack context, current session and 90-minute position | Current watch points, plan criteria/risk/authorization state and direct legal AMDX entry; broader thesis review is easy to reach |
| Review / Development | What happened, what did I do, and what should I study next? | Original captured context and run orientation; recorded evidence when relevant | Market then Process Review, explicit evidence/synthesis/development action; optional deeper history/comparison stays here or in Study |
| Plan / authoring | Which definition governs this work, and what revision am I proposing? | Published revision and selected definition/competency/playbook | Read the current basis, author a candidate deliberately, evaluate it and publish through the existing revision boundary |

Keep instrument, studied/operational reference, process environment and mode distinguishable. Workspace selection, process progress, market time and selected AMDX layer are independent positions. A change of destination must not advance a station, move the live clock, create a run or write an interpretation.

Show only applicable chrome. An idle Study workspace needs no fake active-run badge. A resumed run needs its captured revision, environment and reference. Missing context remains Available-empty, Not Configured or Unavailable as applicable, with a useful remedy rather than a guessed value.

## 4. Study-first doorway: proposed behavior

The accepted direction is a dismissible relevant Study suggestion that lowers planning burden. Recommend the following initial behavior, subject to operator review:

1. When there is no active run, open Study. Present one relevant task with its recorded reason, plus access to unfinished work and competency selection.
2. When a run is already active, restore its working surface and offer Study without displacing that run. Do not conclude it, change its environment or open a second conflicting run.
3. Prefer an explicitly chosen/resumable study task. A saved Development Direction can supply another suggestion. If there is no recorded basis, say so and offer competency selection rather than inventing a weakest skill or ranking.
4. “Study this Competency” stages the existing targeted-study path. It does not begin a run or change proficiency, maturity, eligibility or attainment. Show the staged question, focus and environment before an explicit Begin Process Run action.
5. A normal navigation action dismisses the suggestion without a confirmation or study obligation. Longer-term dismissal preferences and recommendation ordering remain open; do not create a new persistence subsystem for them in the first slice.

An unfinished Study Find draft is resumable capture, not proof that a historical process run is unfinished. A suggestion must identify what it resumes. A recorded development need is a reason to offer study, not permission to assume a practice environment is available.

## 5. The integrated Study loop

The technician chooses a question and, when appropriate, a competency. Historical Backtest keeps its required explicit question and historical reference; hypothesis and scope remain supporting fields. Current defaults must not silently imply that a past expectation was known prospectively.

Investigation can begin in the maintained AMDX calendar without manufacturing a trading run. An explicit process launch remains available when the question needs Replay, Historical Backtest or another permitted environment. Reuse the shared launcher and eligibility explanation; do not introduce a separate Lab execution or authorization path.

The spacious Lab view exposes all existing layers, with the selected quartet and its rule/definition basis adjacent. Navigation and interval inspection are read-only. A deliberate legal phase choice uses the existing immediate revision action; notes remain drafts and process completion remains a separate action. Historical entry carries actual recording time, studied reference, instrument and semantic channel. Lab backfill contributes to the maintained calendar used by TDA/Watch without overwriting immutable historical run captures.

Keep Study Find capture reachable from the investigation. Preserve the question/reference/competency association only where actually recorded, and show unknown links truthfully. A learning note or source excerpt does not automatically create competency evidence. At deliberate Review, the technician can interpret the observation, record explicit evidence, inspect synthesis and choose a Development Direction. The next Study suggestion may use that recorded direction.

Study sources and knowledge capture can support the task without becoming a mandatory detour. The original trade-plan references reinforce preparation, expectations, an AMDX calendar, observations, daily/weekly Review, improvement topics and dedicated Study time. They are examples subordinate to current published plan definitions; their sample risk percentages, performance claims, no-trade rules and practice-hour claims are not new UI policy or recommendation logic.

## 6. AMDX presentation and actions

One instrument calendar supplies all views. Purpose/environment is provenance, not a normal destination picker. MNQ is the current configured instrument; future NNQ support and deliberate legacy assignment/import remain separate work. Never substitute MNQ for unknown historical ownership.

| Selected quarter | Direct normal choices |
| --- | --- |
| Q1 | A, X(C), X(R), unresolved X |
| Q2 | A, M |
| Q3 | M, D |
| Q4 | D, X(C), X(R), unresolved X |

Choices span both legal profiles so one new entry can change the quartet order. Preserve the existing compatible/retired-anchor semantics and history; do not ask the technician to find and clear an overwritten anchor. Entered anchors, profile-implied siblings, temporal current position and applicability/uncertainty are different meanings and must remain distinguishable.

In Watch, show the current stack and where the technician is in it. Expose X(C) and X(R) directly when legal. Inspecting another interval pins an explicit edit target; the clock must not redirect an open gesture. Follow current is a deliberate return to current orientation. Commit failures preserve the attempted target and visible committed state; never show an unsaved role as saved or retry automatically.

Watch has no history list, comparison panel or comparison entry point. Small changes stay in place. A larger thesis change can open the full stack/TDA context with an explicit return path, retaining run ownership and permitted edit scope. Returning must not conclude, replace or silently relaunch the run.

In Study, full-stack inspection and independent Expected/Observed entry remain spacious. Criteria definitions should be easy to read beside the selected quartet. Mutable criteria authoring, priority/weighting evaluation, competing interpretations and empirical comparisons need their own vertical slice; do not imply an automatic classifier exists.

In Review, identify **Original captured Expected** separately from **Maintained Observed**. Routine observed entry selects no first/latest expectation baseline. The existing bounded higher Review proof stays tied to the actual run day and explicit orientation; the broad historical Lab is not constrained to that run editor. Optional deliberate comparison stays a later Review/Study tool.

## 7. Interaction and continuity contracts

Use shared logical actions for workspace navigation, interval selection, legal role revision, draft capture, station completion and return-to-context. Mouse, keyboard and later macro-pad inputs should reach the same command boundary. Hardware bindings and coverflow are deferred, revisable renderers rather than prerequisites.

Navigation restores visible selection/reference/drafts without generating domain revisions. Deliberate phase choices commit through current repository transactions and stale-target checks. Existing evidence replacement, captured-use/assessment ownership and published-plan boundaries must not be bypassed by moving widgets into a new shell.

The wider desktop layout places required decisions and primary actions in the main task area. Details may reflow or collapse before required controls are displaced. Wheel scrolling within text/detail content must remain usable; station navigation gets an explicit shared action rather than being an undocumented consequence of scrolling. Essential meaning cannot depend on hover alone.

Until the native surface is verified, retain existing tabs or a clearly reachable fallback. Use synthetic/disposable fixtures for development and smoke testing. Do not open or migrate the operator's regular database merely to inspect a layout.

## 8. Immediate and intermediate slices

| Slice | Concrete deliverable | Exit evidence |
| --- | --- | --- |
| UX1 — Study doorway and safe routing | Native Study landing surface; recorded-basis suggestion or truthful empty state; targeted-study staging; dismissal/navigation; active-run resume behavior after review of that proposal | Idle/active-run/restart cases; staging creates no run or governance records; draft preserved; operator can begin useful work without hunting through nested pages |
| UX2 — Integrated Study task | Question and reference stay beside full-stack AMDX investigation; selected detail/definitions; linked capture and explicit Review route using existing capabilities | All-layer backfill/reopen, entered versus implied roles, draft continuity, no fabricated evidence or prospective expectation; brief guided operator trial |
| UX3 — Shared operational shell | Adjacent TDA station overview/detail; quiet Watch stack and legal direct subtype controls; larger-context return; clear Review original/Observed basis | Permissions, pinned gestures/clock boundaries, current position, failure/retry, run capture and Review-date regressions; 16:9 and reduced-window usability |
| UX4 — Criteria study and authoring | Read published/candidate definitions in context; deliberate versioned criteria editing and retained evaluation/evidence basis | Competing rule approaches remain traceable; no silent plan adoption or classifier claim; useful empirical study question demonstrated |

The broader-Lab fixture is a pre-native composition review spanning the relationships later implemented by UX1, UX2 and UX4. It does not reorder those implementation boundaries or authorize production work by itself.

UX1 should be a bounded native slice rather than a seven-tab replacement. UX2 can provide the spacious AMDX Lab rendering the operator requested while building a usable Study loop. UX3 then applies the shared presentation contracts to operating surfaces. Ordering between parts of UX2/UX3 can change if actual use exposes blocking friction. Controlled legacy/history import and large-history performance remain explicit parallel/subsequent work when real data volume demands them; they are not replaced by this plan.

Execution-safety simulation, NinjaTrader orders and multi-device operation remain later roadmap milestones. No additional storage framework, readiness score, automatic classifier, chart integration, Film Night gallery or hardware dependency is needed to begin UX1.

## 9. First native slice implementation map

| Existing source | Reuse / narrow change for UX1 |
| --- | --- |
| `src/ict_cockpit/gui/main_window.py` | Startup destination and workspace routing; reuse active-run restoration and draft restoration; keep existing destinations reachable |
| `src/ict_cockpit/gui/trade_plan_widget.py` | Reuse `_prepare_targeted_study` and its existing launcher routing rather than duplicate staging behavior |
| `src/ict_cockpit/gui/process_run_launcher_widget.py` | Reuse `prepare_targeted_study`, eligibility explanations and explicit Begin Process Run; retain required Historical Backtest intent |
| `src/ict_cockpit/gui/competency_evidence_review_widget.py` | Reuse `study_competency_requested` and competency selection; read recorded context without altering assessments |
| `src/ict_cockpit/database/competency_development_direction_repository.py` | Read an explicitly saved direction; inspect exact query semantics before choosing a suggestion; no invented ranking |
| `src/ict_cockpit/gui/amdx_master_lab_widget.py` and `amdx_shared_context_widget.py` | Preserve canonical binding/run-scope/captured context hooks; no duplicate ledger or bypass of revision commands |
| Existing Study Find widgets/repository | Reuse draft/capture/Review paths; do not treat a draft as an unfinished process run |

A small dedicated landing widget and routing adapter are reasonable implementation choices. Start with read-only suggestion composition and staging; introduce persistent preference fields only if an accepted behavior requires them. No schema change is expected for that initial boundary, but verify existing query/state contracts before claiming it.

The first operator guide should explain the visible starting state, exact action, expected result and restart path using a fresh disposable directory. Avoid instruction-only smoke checks that require guessing, unexplained step references or reuse of a concluded fixture. Add checklist records only for actual new production behavior.

## 10. Review scope and validation

The immediate review is about whether Study, overview/detail and operational context fit together, and whether the proposed startup/resume behavior removes effort. Individual dropdown appearance and final colors are secondary; all usability feedback remains useful and provisional.

Open choices: startup handling of an active run; suggestion priority/manual preference; exact primary navigation; density and position of overview versus detail; Study capture placement; definition-authoring affordances. Accepted invariants—quiet Watch, one-click legal X subtypes, shared calendar, nearby higher context, immediate phase recording and truthful provenance—do not depend on choosing those details now.

Validate this documentation checkpoint by checking source hooks, local document links, preservation of all 280 smoke records and a clean docs-only Git diff. Validate the interactive walkthrough independently for navigation, shared quartet changes, legal role availability, selected-layer detail, task/draft continuity, Review capture immutability, light/dark appearance and narrow reflow. Browser-preview results establish local interaction behavior, not host-renderer reliability or native/operator acceptance. The existing 1,136-pass result belongs to the unchanged production baseline; do not report it as a fresh suite for this plan.

### Verified planning checkpoint

- Four existing smoke-document tests PASS; the complete `SMOKE_TEST.md` is byte-identical to main, retaining all 280 records.
- 28 local browser interaction assertions PASS: navigation, seven-layer access, deliberate staging, direct legal X subtypes, shared Expected changes, independent Observed context, fixed original capture, Study/station draft continuity, deliberate completion and required thesis decisions.
- No JavaScript errors; no horizontal overflow at 1440px, 1024px or 320px. Light, exact authored dark palette and narrow layouts were visually inspected in QtWebEngine 6.8.3. The conversation host renderer/theme switch and native/operator usability remain unverified.
- Local Markdown links and `git diff --check` pass. Production source/tests/tools and the schema/plan/smoke results are unchanged. The prior 1,136-pass production result was not rerun for documentation.

## Source trail

- [Current state](PROJECT_STATE.md), [requirements](PROJECT_REQUIREMENTS.md), [decision audit](DECISION_AUDIT.md) and [system guide](SYSTEM_GUIDE.md).
- [Reviewed functional walkthrough](COCKPIT_FUNCTIONAL_WALKTHROUGH.md) and [updated storyboard](UX_STORYBOARD.md).
- [Master calendar clarification](AMDX_MASTER_CALENDAR_CLARIFICATION.md), [shared native guide](AMDX_SHARED_NATIVE_GUIDE.md), [higher Review guide](AMDX_HIGHER_REVIEW_GUIDE.md) and [criteria framework](AMDX_RULE_DEFINITION_FRAMEWORK.md).
- Original provided references: `01-ICT-Concepts-Trading-Plan-Example.docx`, Daily Checklist; `02-Building-a-Trade-Plan.pdf`, pp. 2–5, 12 and 21. These inform workflow motifs only and remain unmodified.
