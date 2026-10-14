# Lab AMDX calendar and feature-tree interaction specification

**Status:** Proposed focused investigation. No renderer, native implementation or AMDX interpretation is accepted by this document.

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

Temporal color cues remain consistent when used: Asia/Q1 yellow, London/Q2 red, NYAM/Q3 green and NYPM/Q4 blue. Text, order and shape still carry meaning; color alone does not.

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

## Follow-on relationship to Watch

Only after the Lab spatial model is understood should Watch receive its compact derivative: a quiet current path, current session and active 90-minute detail, with one action into the fuller tree/workspace. Watch must not reproduce the complete Lab tree, history or comparison controls.

