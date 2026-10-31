# Cross-suite UX interaction standards

**Status:** Accepted design guardrails, 2026-10-14. These standards govern UX proposals across TDA, Watch, Lab, Review / Development and later workbenches. They do not prescribe one final layout.

Read with [UX Friction Research](UX_FRICTION_RESEARCH.md), [UX Design Touchstones](UX_DESIGN_TOUCHSTONES.md), [Workspace Parity](WORKSPACE_PARITY.md) and [Project Requirements](PROJECT_REQUIREMENTS.md).

## Core standard

**Salience should be earned.** The interface should answer **“What changed since my last glance?”** before asking the technician to reread stable information. Stable facts remain available and legible; changed, unsafe, unresolved or newly actionable facts receive stronger treatment.

## Accepted interaction standards

1. **Clear attention states.** Quiet/background, current/selected, attention requested, blocked/unsafe, confirmed and unavailable/unknown must remain distinguishable. “No action needed” should not compete visually with a real change.
2. **Interruption recovery.** A return from TradingView, a support tool or a restart should restore the working scope, selection, unfinished work and next relevant action without reconstruction.
3. **Shared command grammar.** Common actions retain their meaning and relative placement across workspaces. Visible controls and shortcuts invoke the same scoped action; shortcuts do not create a second workflow.
4. **Constraint-based error prevention.** Prevent invalid actions where the domain contract is known, make the safe path the easiest path, and explain blocked actions locally. In hardware terms this resembles “idiot proofing,” but the design target is a system that does not depend on perfect memory or attention.
5. **Redundant encoding.** Do not rely on color alone. Pair color with labels, position, shape, border, icon or text state as appropriate.
6. **Distinct modes, cohesive suite.** Each major workspace should create a recognizable operating mode through composition and task emphasis. Shared chrome, typography, status meanings, command behavior and provenance keep the suite coherent.
7. **Context beside the work.** Frequently consulted definitions, criteria and process steps should be reachable at the point of discernment without displacing the primary operation. Chart-correlated reference belongs on the chart-facing edge.
8. **Truthful provenance.** Plan definitions, current-run observations, derived cues, drafts, fixtures and broker facts must not be visually conflated.
9. **Theme-ready semantics.** Dark and future light themes should map the same semantic tokens and preserve hierarchy, contrast and redundant meaning. Theme is presentation, not a second information model.
10. **Evaluate journeys, not decoration.** Review reacquisition, hunting, interpretation, movement, recovery and error prevention in realistic tasks. Click count, density and visual preference are evidence, not standalone verdicts.

## Task-directed entry and disclosure — accepted 2026-10-29

**Keep the current task ready to use; disclose supporting tasks when needed.** This is an important suite-wide requirement, not a blanket preference for fewer clicks or fewer visible controls.

An explicit entry action must open its primary task ready for use, without a second reveal action for the feature just requested. Inspection and other secondary tasks may keep that same feature collapsed. Initial presentation must follow the named action predictably, not inferred intent, click frequency or surprise adaptive rearrangement. Keep familiar spatial anchors, accessible controls and a way to collapse supporting areas. Different entry routes must use the same authoritative workspace, commands and data owners.

For Study investigations:

| Entry purpose | Required initial presentation |
| --- | --- |
| Inspect investigation material | Evidence/findings prominent; review editor may remain collapsed. |
| Review this investigation | Existing review editor already open, supporting material nearby, collapse available. |
| Browse Study history | Saved records prominent; no new-entry form. |

Entering or collapsing must preserve the investigation, reference, unfinished capture and unsaved review protections. Opening review must not create a checkpoint, complete an investigation or imply an obligation to fill every prompt. Do not change all overview entry routes to show a form by default.

Acceptance should include mouse and keyboard entry, immediate access to the requested task, stable return to prior work, and preservation of unfinished content. Assess total interaction cost: hunting, reading, remembering, reorientation and clicks. Revisit frequency and utility in natural study sessions; scripted repeated reviews alone do not establish the best universal default.

Status: accepted requirement; the local `feature/study-direct-review-v0` implementation applies it to Study review (see `STUDY_DIRECT_REVIEW.md`); operator 350 remains pending. Operator noticed the extra reveal click repeatedly during checkpoint 348 and explicitly endorsed this resolution. Functional checks 348–349 passed independently of this UX refinement.

Supporting guidance: [Progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/) and [Interaction cost](https://www.nngroup.com/articles/interaction-cost-definition/). The task-specific routing above is the project's design decision, not a claim that these sources prescribe this exact layout.

## Contextual completion loop

The accepted Watch reference-and-decision dock supplies a reusable interaction pattern for low-friction work:

1. reveal support at the point of discernment;
2. carry the exact current target and only legal actions into that support;
3. invoke the existing authoritative command once;
4. reflect the result through every synchronized projection;
5. dismiss temporary support and restore the previous work anchor.

This is the preferred pattern when reference and action naturally belong to one brief task. It is not a blanket two-click target and does not justify hiding essential state, multiplying commands or adding popouts everywhere. Apply it only when it reduces hunting, process memory or cross-screen travel without concealing consequential choices.

## Color namespaces

The stable session identity palette—Asia/Q1 yellow, London/Q2 red, NYAM/Q3 green and NYPM/Q4 blue—may support recognition where session identity is useful. Operational states such as safe, warning, blocked, selected and complete are a separate semantic namespace. If the same hue could imply both, labels plus another non-color cue must disambiguate it, or the operational state takes precedence.

## Design-conflict review rule

Operator and developer suggestions are valuable design inputs, not silent overrides of accepted safety, accessibility, semantic-clarity or low-friction standards.

When a proposal appears to conflict with an accepted principle, the proposal must be flagged before adoption. The review records:

- the exact suggestion and the task it is trying to improve;
- the principle or invariant in tension;
- the concrete adverse effect that may result;
- at least one alternative or mitigation and its tradeoff;
- the explicit decision after discussion.

This is not an automatic veto. A preference may still be chosen after an informed tradeoff when no non-negotiable safety or domain constraint is violated. The rule applies equally to operator requests, developer convenience and visually attractive prototypes.

## Chart-adjacent Trade Plan reference

Watch should offer a contextual reference for manual discernment, especially AMDX/QT interpretation:

- source the definition, criteria, weighting and process from the active versioned Trade Plan;
- follow the current asset, time/cycle and relevant operation without claiming an answer the plan does not support;
- open from the chart-facing edge and remain physically closest to TradingView in the active monitor profile;
- support a direct mouse and keyboard route, then return focus to the same Watch anchor;
- remain a support surface rather than a permanent dashboard panel;
- culminate in the active quarter's legal one-action choices when opened for AMDX discernment, then dismiss after the choice;
- preserve ambiguity and allow a Study Find when the rule or evidence is unresolved;
- show provenance and never present prototype examples as published rules.

The decision controls are a second **projection** of the existing shared AMDX action, not a second workflow. They must use the same target, legal-choice constraints, labels, immediate revision semantics and state as the main AMDX surface. They may not introduce a separate Save, history or popout-only domain behavior. Full definition authoring, comparison and empirical evaluation remain Lab / Trade Plan work.

## Workspace and display settings

Monitor relationship is a suite-wide, infrequently changed preference. A future **Workspace & Displays** settings area should retain a constrained named profile such as TradingView-left/Cockpit-right or Cockpit-above/TradingView-below, preview the resulting chart-facing edge, and reuse that relationship across relevant workspaces. Theme and shortcut/macro-pad bindings belong in the same broader settings system when implemented. Do not turn this into unrestricted panel docking or a separate data model.

## Cross-suite identity target

| Workspace | Distinct operating emphasis | Shared language retained |
| --- | --- | --- |
| TDA | Spatial map and chart-layout parity | shell, scope, status semantics, commands |
| Watch | Quiet current state, changed facts and process safety | provenance, support-return behavior, shortcuts |
| Lab / Study | Spacious exploration, nested context and evidence work | selection, save/draft meaning, plan ownership |
| Review / Development | Synthesis, weaknesses and routed next study | evidence states, traceability, safe transitions |

Exact visual identity remains a native-design question. Distinction must come from task composition and information hierarchy, not merely different accent colors.

## Actionable blocked states — operator accepted 2026-10-30

When a safe resolution path exists, a blocked action must explain the cause locally and offer a direct route to resolve it while preserving unfinished work. A warning alone is insufficient when the operator must hunt for the blocking object. The accepted Study example is Return to unfinished capture beside blocked New/Resume. The route must not bypass the guard, silently save/discard, or change association/reference. Apply this suite-wide where the domain provides a valid recovery action. Operator 356–357 PASS.

## Familiar inspection dismissal — 358–359 acceptance

Preserve native Escape/Close for temporary read-only inspection. The image viewer must belong to its containing dialog/window and close independently without losing the work beneath it. Do not generalize this into silent dismissal/discard of unsaved authoring; review and capture protections retain precedence. Native Ctrl+Z in observation editing is likewise a behavior to preserve through future widget/layout changes.

## Fixed action-status location — operator clarification

The operator requests a globally visible, stable status area, not an error-log browser. A failed action should be noticeable in the same location without searching for an inserted line or a shifting layout. Use the existing bottom status bar as the initial shared location, paired with local corrective context and field focus when appropriate. Navigation recovery remains appropriate for blocked transitions; invalid input needs local correction instead. Neither a diagnostic log nor animation replaces a clear textual explanation. Motion/highlight proposals remain exploratory and must not rely on color or motion alone.

Initial application: Study summary success/failure also reports in the bottom status bar; missing-field feedback uses reserved local space and field focus. This does not normalize every existing subsystem. Follow-up should define severity, persistence/acknowledgment and precedence so routine status cannot silently displace an unresolved important error. Current status bar still represents the latest reported message, not a persistent unresolved-error queue. No new log area is planned for this request.
