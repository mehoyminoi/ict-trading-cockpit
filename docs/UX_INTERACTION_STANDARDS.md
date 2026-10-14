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
- preserve ambiguity and allow a Study Find when the rule or evidence is unresolved;
- show provenance and never present prototype examples as published rules.

The Watch projection is a concise aid. Full definition authoring, comparison and empirical evaluation remain Lab / Trade Plan work.

## Cross-suite identity target

| Workspace | Distinct operating emphasis | Shared language retained |
| --- | --- | --- |
| TDA | Spatial map and chart-layout parity | shell, scope, status semantics, commands |
| Watch | Quiet current state, changed facts and process safety | provenance, support-return behavior, shortcuts |
| Lab / Study | Spacious exploration, nested context and evidence work | selection, save/draft meaning, plan ownership |
| Review / Development | Synthesis, weaknesses and routed next study | evidence states, traceability, safe transitions |

Exact visual identity remains a native-design question. Distinction must come from task composition and information hierarchy, not merely different accent colors.
