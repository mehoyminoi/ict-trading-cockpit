# UX friction research and proposed review criteria

Research checkpoint: 2026-10-13, operator-local date. Requested pause before further UI work. This is a source-backed discussion and proposed quality annex, not acceptance of a new renderer. Its cross-suite conclusions were accepted on 2026-10-14 in the [UX Interaction Standards](UX_INTERACTION_STANDARDS.md). Read alongside [the context reconciliation](UX_CONTEXT_RECONCILIATION.md), [requirements](PROJECT_REQUIREMENTS.md) and [implementation proposal](COCKPIT_UX_IMPLEMENTATION_PLAN.md).

## 1. What we are trying to reduce

For this Cockpit, friction includes finding a command, interpreting what it means, remembering context, switching/reorienting, repetitive movement, and recovering from a mistake. Quietness means giving attention a clear destination while retaining the needed context and reachable tools. A sparse screen that makes the technician hunt can still fail that goal.

The operator's existing direction supplies the product goals: a primary 16:9 workspace; foundational whole-stack AMDX accessibility; quiet current-state Watch; spacious Lab investigation; guided Focus with accessible Deck; recoverable support capture; and low planning burden after a tiring workday. Research below helps evaluate ways to deliver those goals. It does not replace domain contracts or settle visual composition.

## 2. Professional strategies and their limits

These are short paraphrases of authored or official guidance. The application column is our proposed Cockpit interpretation, not a reported finding about this application.

| Strategy | What the source supports | Proposed Cockpit application |
| --- | --- | --- |
| Progressive disclosure [S02] | Put important/frequent choices first; expose specialised detail through an understandable entry point. Incorrectly hiding frequent work creates extra navigation. | Keep active AMDX entry and required station decisions apparent. Offer definitions, Study Find and deeper investigation through clear support access. Decide visibility by actual task use. |
| Staged disclosure [S02] | Sequence meaningful task stages; tightly interdependent options may need to remain together. | Focus supports the current analytical operation. Deck supplies orientation and station selection. Do not turn every piece of analysis into a separate mandatory page. |
| Recognition, feedback and expert accelerators [S01] | Visible choices/status, familiar language, control and efficient experienced use are broad usability heuristics. | Show working scope and recording status. Use familiar domain labels. Add shortcuts to the same actions used by visible controls; prevent illegal phase placements. |
| Task-oriented command organisation [S03] | Ribbon guidance groups related commands; local commands may belong near their pane. Frequent tab changes and long repeated trips undermine efficiency. | Try a modest common command area with contextual tools near the work. Compare a ribbon with a simpler toolbar/task pane before choosing. |
| Perceptual grouping [S07] | Proximity and separating space communicate relationships. | Keep selected AMDX context, its entry target and relevant overview in a coherent region. Avoid competing AMDX summaries at opposite ends of the workspace. |
| Understandable labels [S09] | Unfamiliar icons are ambiguous; essential labels should not depend on hover discovery. | Icons can strengthen workspace/command cues. Keep meaningful labels for essential navigation and commands; tooltips provide extra explanation. |
| Stable navigation [S10] | Repeated navigation keeps a consistent relative order while allowing contextual variation. | Give major workspaces distinct compositions and emphasis, while retaining common command meanings and predictable navigation. |
| More than a click count [S08] | A universal three-click limit is unsupported; the work involved in each interaction differs. | Compare hunting, thought, movement and recovery alongside clicks. Preserve the accepted one-click X(C)/X(R) requirement; do not invent a global click quota. |
| Redundant visual meaning [S11] | Colour must not be the sole carrier of information. | Pair quarter colours with Q/session labels; give news markers their own text or shape. Check contrast, focus and keyboard operation during native design. |

Applicability matters. S01 is a set of broad inspection heuristics, not a prescribed layout. S03 explicitly describes legacy Windows 7 guidance: borrow command-organisation principles, not its platform-specific startup/tab behaviour or appearance. S10–S11 are web accessibility guidance; their relevant principles transfer to native work, but this document makes no WCAG-conformance claim for the Qt application. None of these sources demonstrates that our proposed ribbon, calendar or Focus/Deck presentation is already usable.

## 3. Proposed requirements annex

The following are candidate UX quality criteria for operator discussion. Existing accepted behaviour remains authoritative; the criteria make its presentation reviewable. They do not approve a particular ribbon, drawer, tab count, animation, recommendation ranking or startup policy.

| ID | Proposed criterion | Observable review check |
| --- | --- | --- |
| UX-F01 | Identify the workspace and working scope without reconstructing them from scattered panels. | In TDA, Watch and Lab, the technician can identify where they are, the relevant instrument/reference and which target an action will affect. |
| UX-F02 | Give the current operation a clear attention hierarchy. | A guided station exposes its action/observation/carry-forward work. Required choices such as Models in Play remain findable; unrelated history does not dominate Watch. |
| UX-F03 | Preserve distinct Focus/Deck purposes, TDA layout parity and a short, clear return route. | A four-pane cockpit Deck retains the physical positions and chart roles of its four-pane TradingView deck. Select a mapped station, continue its Focus work and return to the unchanged map without re-entering data. Both views do not need permanent expanded panels. |
| UX-F04 | Keep foundational AMDX orientation and selected detail coherently accessible. | Locate the current day/session/90-minute context, then inspect higher context without hunting across duplicate summaries. Lab can reach the supported full stack and editable selected lower context. |
| UX-F05 | Support frequent entry directly. | From the active permitted target, each legal X(C)/X(R) choice is one click. A deliberate accepted phase choice records normally without a second Save; illegal placements are unavailable. |
| UX-F06 | Make support work easy to invoke and leave. | Capture a Study Find or inspect extra context, then return to the same operational station/selection with recoverable work. Opening or dismissing support must not certify analysis or conclude a run. |
| UX-F07 | Combine recognisable workspaces with stable common commands. | Major areas are distinguishable at a glance; common navigation, labels and action meanings remain predictable across them. Verify command discovery rather than assuming familiar styling is sufficient. |
| UX-F08 | Support both discoverable mouse use and efficient keyboard use. | Essential commands have understandable labels. Relevant shortcuts invoke the same scoped actions; keyboard focus remains visible and returns usefully after support work. Macro-pad bindings remain later work. |
| UX-F09 | Make recording, uncertainty and recovery understandable. | Distinguish recorded interpretation, recoverable draft, unknown data and blocked action. Correction uses revision-preserving actions; navigation is not completion. Errors offer an actionable recovery path. |
| UX-F10 | Preserve context through interruption and passive time changes. | Resume the station and recoverable draft after interruption. An active AMDX edit remains pinned when the clock crosses a boundary; a newly selected reference is not silently the edited target. |
| UX-F11 | Keep semantic cues understandable without colour alone. | Q/session identity, current marker, editability and news presence can be distinguished using labels/shapes as well as colour. Reflow preserves associations in the supported window geometry. |
| UX-F12 | Evaluate complete task cost before declaring a presentation improved. | Record correct completion and scope, hunting/backtracking, time and context recovery for repeated tasks. Functional pass counts alone do not constitute layout acceptance. |

Traceability: F01–F07 primarily operationalise the operator requirements and the reconciliation's three journeys; S02/S03/S07/S09/S10 supply presentation checks. F05/F09/F10 must respect the existing [QT action contract](QT_ACTION_CONTRACT_REVIEW.md), shared calendar ownership and immutable run provenance. F08/F11 adapt S01/S11 to the operator's keyboard and quarter-colour wishes. F12 follows the evaluation methods below. These are proposed quality gates, not new domain permissions or data stores.

## 4. How professionals evaluate the choices

Use several complementary methods, rather than asking whether a screenshot looks convenient:

1. **Task analysis and command inventory.** List what the technician is trying to accomplish, the necessary information, dependencies and commonly repeated actions. Mark required-now, support-on-request and deep-investigation material. Use observed use to revise that split [S02].
2. **Heuristic inspection.** Review a small proposal against feedback, control, terminology, consistency, error prevention and the other broad heuristics [S01]. This is developer inspection, not a claim that independent UX experts or users have approved it.
3. **Cognitive walkthrough.** Step through a particular goal and ask whether the intended action is discoverable, its meaning is understandable, and its result recognisable [S04]. This checks learnability before asking the operator to try the task; it is not user testing.
4. **Goal-based usability trials.** Observe the operator trying realistic tasks. State the goal and necessary starting context, not which buttons to click; record where assistance is needed [S05]. The interface is being evaluated, not the technician.
5. **Repeatable local comparison.** Reuse equivalent goals, starting states and outcome checks after changes. Record time, completion and perceived difficulty/confidence [S06]. Small operator trials guide this personal tool; they are not a population benchmark or statistically established improvement.

Start with the journeys already prioritised by the historical comparison:

| Journey | Example usability goal | Outcome to inspect |
| --- | --- | --- |
| Guided TDA and Deck return | Continue analysis, inspect overall station progress, revisit a relevant station and resume its work. | Correct scope and intact work; understandable movement between overview and operation. |
| Quiet Watch and support return | Record an active 90-minute interpretation, capture an observation worth studying, then continue watching. | Direct permitted entry; recoverable support capture; same operational context and no accidental completion. |
| Lab calendar investigation | Find a historical period, inspect its stack, backfill a selected lower context and retain a Study observation. | Correct historical target; whole-stack accessibility; working/Observed and original captured context remain distinct. |

Include an interruption/resume case and a meaningful blocked-action or correction case. Use disposable fixtures. The later news scenario should be added when that renderer exists, not counted as a pass now.

For each trial, record starting state, build, goal, input device/window geometry, correct outcome/scope, elapsed time, hunting/backtracking, workspace switches, repeated entry, accidental edits/completion, assistance and operator comments on effort/confidence. Separate interface discovery from analytical judgement. Compare recurring problems; do not set arbitrary universal time or click thresholds. Learning, task order, fatigue and device changes can affect a single operator's results. No automatic telemetry collection is proposed.

Keep this record separate from `SMOKE_TEST.md`. Button-by-button functional smoke instructions establish implemented semantics; goal-based usability tasks reveal discovery and workflow problems. The previous 28 walkthrough interaction assertions and 1,136 production test passes are functional evidence, not usability proof. No new operator trial or replacement-layout acceptance is claimed here.

## 5. Future news/calendar/quarter-stack direction

Record the operator's requested future capability: show scheduled news releases in the calendar and provide a useful visual relationship between news, quarters and the AMDX stack. This extends presentation/access around the maintained calendar; it does not introduce a second calendar owner or authorise a new feed now.

Proposed design boundaries, following the existing [AMDX rules framework](AMDX_RULE_DEFINITION_FRAMEWORK.md):

- A month/week view can use restrained event markers, with selected-day/event detail and nearby quarter/stack context. Exact marker, filter and interaction formats remain open.
- Use explicit event source, release time and coverage/unknown information. Market/session alignment uses America/New_York; unavailable coverage must not look like a day with no releases.
- Preserve what was known at the selected historical reference. Later actuals, revisions or reclassifications must not silently become prospective historical knowledge. Reuse retained event/provider snapshots and existing provenance boundaries.
- Distinguish temporal alignment (an event falls in a quarter), a plan-defined expectation, and measured historical association. A cue does not prove causation, forecast probability, classify AMDX or grant trading permission.
- Keep Q1/Asia yellow, Q2/London red, Q3/NYAM green and Q4/NYPM blue as temporal identity. Give news impact/category another labelled cue so Q2 red does not also mean high-impact news solely by colour.

This wish should be revisited with spacious Lab investigation and quiet operational projections. News definitions, criteria weighting and empirical evaluation remain versioned Trade Plan/research concerns. No current plan rule, provider integration, schema or classifier changes result from this research checkpoint.

## 6. Proposed immediate path

Discuss the quality criteria and task priorities first. Then specify one representative guided journey and its support/return behaviour in a small prototype. Compare a task-oriented toolbar/ribbon approach with a simpler contextual arrangement where it would answer an actual open choice. Inspect it, try goal-based tasks, and correct the dominant friction before expanding the whole-tool renderer.

The immediate decision is what the current task must make visible and what can safely be one invocation away. The exact container can follow that decision. UX1–UX4 remain proposed implementation slices; this research does not authorise their native implementation or another walkthrough revision.

## Sources

Consulted 2026-10-13. These are primary authored guidance or official documentation, not a systematic literature review or numerical prediction of improvement.

- **S01:** Jakob Nielsen, [10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/), Nielsen Norman Group; original 1994, reviewed 2024.
- **S02:** Jakob Nielsen, [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/), Nielsen Norman Group, 2006; also distinguishes staged disclosure.
- **S03:** Microsoft, [Windows 7 Ribbons](https://learn.microsoft.com/en-us/windows/win32/uxguide/cmd-ribbons), legacy Windows desktop design guidance; explicit applicability warning on page.
- **S04:** Kim Flaherty, [Evaluate Interface Learnability with Cognitive Walkthroughs](https://www.nngroup.com/articles/cognitive-walkthroughs/), Nielsen Norman Group.
- **S05:** GOV.UK Service Manual, [Using moderated usability testing](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing).
- **S06:** GOV.UK Service Manual, [Usability benchmarking a website or whole service](https://www.gov.uk/service-manual/measuring-success/usability-benchmarking-a-website-or-whole-service). Its formal multi-participant protocol is not claimed by our proposed local comparisons.
- **S07:** Aurora Harley, [Proximity Principle in Visual Design](https://www.nngroup.com/articles/gestalt-proximity/), Nielsen Norman Group.
- **S08:** Page Laubheimer, [The 3-Click Rule for Navigation Is False](https://www.nngroup.com/articles/3-click-rule/), Nielsen Norman Group.
- **S09:** Nielsen Norman Group, [Icon Usability](https://www.nngroup.com/articles/icon-usability/).
- **S10:** W3C WAI, [Understanding SC 3.2.3: Consistent Navigation](https://www.w3.org/WAI/WCAG22/Understanding/consistent-navigation.html), WCAG 2.2 explanatory guidance.
- **S11:** W3C WAI, [Understanding SC 1.4.1: Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html), WCAG 2.2 explanatory guidance.
