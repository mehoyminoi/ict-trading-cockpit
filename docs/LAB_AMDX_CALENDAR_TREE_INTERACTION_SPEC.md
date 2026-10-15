# Lab AMDX calendar and feature-tree interaction specification

**Status:** Directional checkpoint accepted after four iterations; isolated polishing is concluded. The [standalone prototype](prototypes/lab-amdx-calendar-tree-v0.html) is retained as reference, and the [operator review](LAB_AMDX_CALENDAR_TREE_OPERATOR_REVIEW.md) records the precise acceptance boundary. The full AMDX Lab product, renderer, native implementation and AMDX interpretation remain unaccepted until evaluated in integrated use.

Read with the [Quiet Watch operator review](WATCH_QUIET_SUPPORT_OPERATOR_REVIEW.md), [workspace parity](WORKSPACE_PARITY.md), [UX design touchstones](UX_DESIGN_TOUCHSTONES.md) and [Cockpit UX implementation plan](COCKPIT_UX_IMPLEMENTATION_PLAN.md).

## Review question

Can Lab make the maintained AMDX calendar feel simultaneously navigable at full-stack scale and spacious at the selected level, using a CAD-like feature tree to orient the technician while a synchronized calendar/detail workspace supports inspection, entry and analysis?

The trial should test hierarchy, semantic zoom and efficient movement. It must not become a generic file browser, a giant indented form or an unrestricted dockable dashboard.

## Working model

The screen has three coordinated projections of the same selected reference:

| Projection | Job | Deliberate limit |
| --- | --- | --- |
| Feature tree | Show the selected containment path and nearby siblings across 16-year, quadrennial, year, month, week, Trading Day, session and 90-minute layers | Current path plus a bounded sibling neighborhood; never expand the whole history by default |
| Calendar/workspace | Render the selected level spatially: month grid, week strip, day/session quartet or lower-cycle quartet | Changes with semantic zoom; it is not a second AMDX data owner |
| Detail/support rail | Show selected quartet, Expected/Observed channel, entered versus implied roles, definitions, provenance and deliberate edit actions | Contextual and bounded; no arbitrary widget wall or automatic rearrangement |

Tree selection, breadcrumb, calendar selection and detail heading always identify the same reference. Moving through the hierarchy records no interpretation. A deliberate legal role action uses the existing maintained-calendar command boundary.

The second iteration separates **temporal selection** from **context depth**. Zoom changes the selected temporal level. Quiet/Nested/Deep context changes how much ancestor and descendant structure is rendered without moving that selection. These are exploratory density settings, not final user preferences or proof that every nested layer should always be visible.

## Tree behavior

- Open the current path and one useful layer of siblings; collapse unrelated branches.
- Preserve parent context when a child is selected. The selected row remains visually obvious after the technician looks away and returns.
- Allow keyboard arrows, pointer disclosure controls and common navigation commands to perform the same logical actions.
- Treat wheel/gesture and later CAD-mouse or macro-pad bindings as alternative inputs to those commands, not separate behavior.
- Provide a breadcrumb or compact path summary outside the tree so deep indentation is never the only explanation of location.
- Remember useful navigation position separately from market time, process progress and draft state.
- Permit an explicit **Follow current** action without redirecting a pinned historical edit target.

## Semantic zoom

Zoom means changing the temporal projection and retained context, not merely changing font size.

| Selected level | Primary workspace |
| --- | --- |
| 16-year / quadrennial / year | Nested quarter overview with the selected descendant path visible |
| Month | Proper month calendar with week boundaries and compact AMDX/news cues |
| Week | Week strip showing Trading Days and their role/current-state cues |
| Trading Day | Asia/Q1, London/Q2, NYAM/Q3 and NYPM/Q4 quartet |
| Session | Four 90-minute cycles with the active or studied cycle emphasized |
| 90-minute | Quartet detail, definition basis, provenance and deliberate entry/edit action |

Zooming in follows the selected quarter. Zooming out restores the parent and the child selection. A coverflow-like presentation may be explored for quick sibling traversal, but the requirement is spatial continuity and shared navigation—not a literal carousel.

## Calendar behavior

- Month layout uses real calendar geometry for the chosen month rather than a raw date list.
- New York civil date, futures Trading Day and Quarter Theory boundaries remain distinguishable.
- Weeks that cross months and months with a fifth visible row do not invent a fifth Quarter Theory quarter.
- Historical backfill can reach every maintained layer and both Expected and Observed channels with truthful recorded-at/provenance information.
- Current Watch, TDA and Review remain projections of the same instrument-owned master calendar; Lab does not create a separate purpose-owned catalog.
- Initially configured MNQ does not imply that unknown historical records belong to MNQ. Future NNQ remains a deliberate asset/binding concern.
- Familiar previous/next month plus month/year selection supplement tree navigation. They do not move the live clock.
- Month rows use a neutral physical week rail. Quiet shows grouping only; Nested adds the week and daily AMDX values; Deep adds interval and compact session context. Colored day-row headings are not used merely to say Q1–Q4.
- True opens appear at the relevant period position. Lab inspects/edits the fact; TDA owns the temporally relevant reminder. Recorded, unmarked and unavailable remain distinguishable. The prototype stages this visually only and does not establish true-open persistence.

Temporal color cues remain consistent when they add useful identity: Asia/Q1 yellow, London/Q2 red, NYAM/Q3 green and NYPM/Q4 blue. They are not sprayed across every Q1–Q4 grouping. Text, order, spacing and shape carry hierarchy first; color alone never carries meaning. The fourth trial retains that palette only as a restrained edge on the four named session cards; even this use remains reviewable.

The same policy applies outside the calendar. Tree path and selection, generic period groups, quartet cards, compact stacks and the detail profile do not receive Q1–Q4 color merely because they contain four positions. State cues remain available for selection/current, unavailable data, news, entered/implied values and action. Context depth changes information density, not color intensity.

Display policy may eventually expose restrained show/hide and color/no-color preferences. Configuration must not fragment the shared data model or turn the default into a dashboard-builder exercise.

## Workbench and lens hypothesis

The shell should continue testing a familiar workbench transition analogous to CAD software: TDA, Watch, Lab and Review retain shared orientation while presenting operation-specific tools. Inside Lab, AMDX Calendar is one analytical lens. The prototype's combined selector is a hypothesis only; global phases and local lenses may ultimately require separate but related controls.

## Entry and analytical detail

- The selected target and semantic channel are explicit before entry.
- Legal direct choices retain the existing rules: Q1 `A`/`X(C)`/`X(R)`/unresolved `X`; Q2 `A`/`M`; Q3 `M`/`D`; Q4 `D`/`X(C)`/`X(R)`/unresolved `X`.
- One new entry may revise the compatible quartet without requiring the technician to locate and clear an overwritten anchor.
- Entered anchors, implied sibling roles, current temporal position, uncertainty and applicability remain visually distinct.
- Definitions and alternative weighting/priority approaches can be inspected beside the selection. This specification does not add an objective classifier or silently adopt a rule.
- History, competing interpretations and empirical comparison may be opened deliberately for Study/Review. They remain absent from ordinary Watch.

## News cue direction

The month/week/day projections should reserve a restrained cue for snapshotted high-impact releases and their relationship to AMDX/quarter position. The cue should support questions such as whether a release aligns with a manipulation or delivery window. It does not claim event completeness, automatic causality, a new provider feed or an AMDX classifier. Unknown/incomplete source coverage remains visible.

## Trilium-derived constraint

The operator's current Trilium hierarchy validates disclosure-based containment as a natural navigation model. Its deep `year → quarter → month → week → day` path also shows why the tree cannot own the whole experience. The prototype should deliberately test:

1. whether the current path can remain legible with only nearby siblings expanded;
2. whether the center workspace makes month/week/day shape apparent without reading every node;
3. whether selecting or zooming preserves location across tree, breadcrumb and detail;
4. whether the technician can edit a lower level while keeping higher context quietly visible;
5. whether leaving for a chart and returning requires reacquisition rather than reconstruction.

## Fixture and acceptance boundary

Use a synthetic MNQ calendar containing at least two years, a cross-month week, all four sessions, four 90-minute cycles, Expected and Observed entries, one unresolved `X`, one unavailable reference and a small set of explicitly incomplete news snapshots. The fixture must be disposable and must not open or migrate the operator database.

The focused review may accept the tree/workspace relationship while rejecting exact sizing, icons, palette, labels, gestures or calendar density. It cannot establish final criteria, news policy, broker behavior, native performance, historical import throughput or production readiness.

## Goal-based operator review

Use the prototype at a normal 16:9 size. These are orientation goals rather than a script that must be memorized.

1. Keep October selected and compare Quiet, Nested and Deep context. Confirm Quiet retains physical week grouping without AMDX labels, Nested adds neutral week/daily values, and Deep adds interval/session detail.
2. Confirm the ancestor context spine keeps the month located within its quarter/year/quadrennial/16-year path while context depth changes.
3. Navigate September, October and November with familiar controls, and inspect the year. Confirm calendar movement does not move the live clock.
4. Identify week Q1–Q4 and distortion treatment from the neutral left rail without relying on colored day headings. Find true opens at their calendar positions; mark the due True Month Open from the detail rail, then reload and confirm its fixture state.
5. Zoom out through Year, Quadrennial and 16-year. Judge whether each workspace now exposes meaningful child structure rather than one generic row.
6. Move into Tuesday, NYAM and the 10:30–12:00 cycle. Switch Expected/Observed and make one legal direct role entry; confirm the quartet changes immediately without another Save.
7. Select 2025 and confirm unavailable data is not guessed. Then use **Follow current** and confirm historical navigation did not redirect or edit the current reference.
8. Open the **Lab · AMDX Calendar** workbench/lens control. Judge whether the CAD-workbench analogy is intuitive while the shell still communicates that Lab is a broader Study workspace.

9. Scan the tree, higher-level groups, generic quartet cards and detail profile. Confirm the quarter structure remains legible after decorative Q1–Q4 color is removed. Then enter a Trading Day and judge whether the restrained session-identity edges earn their attention cost.

Do not try to accept the Zoom In/Out interaction merely because hierarchy rendering improved. Record where its direction, target or selection-following behavior still feels wrong; temporal zoom remains a separate open design problem.

Record whether the tree supplied orientation without taking over the screen, whether the month/week/day/session projections reduced reading effort, whether the detail rail felt adjacent rather than detached, and whether returning from another monitor would require reacquisition or reconstruction. The calendar depth model may be accepted independently from the overall AMDX Lab form. Comments on exact tree width, calendar density, labels, controls, styling and remaining color remain provisional.

## Follow-on relationship to Watch

Only after the Lab spatial model is understood should Watch receive its compact derivative: a quiet current path, current session and active 90-minute detail, with one action into the fuller tree/workspace. Watch must not reproduce the complete Lab tree, history or comparison controls.

## Checkpoint handoff

The initial spatial model is now understood well enough to stop iterating in isolation. Carry these decisions into broader Lab composition:

- tree/workspace/support-rail as a coordinated relationship, not a fixed final geometry;
- calendar Quiet/Nested/Deep as the accepted density direction;
- neutral hierarchy with restrained named-session color shared with chart indicators;
- AMDX Calendar as one Lab lens inside a Study-first workbench;
- true-open facts in context, with temporally relevant reminders owned by TDA;
- truthful unavailable history and one shared maintained calendar;
- unresolved temporal zoom to be revisited only in a realistic integrated workflow.

The next trial should compose AMDX with competency/question guidance, chart evidence and Study Finds, criteria/definition work, historical/forward samples and routes to TDA, Watch and Review. It should not attempt another AMDX-only polish pass.

