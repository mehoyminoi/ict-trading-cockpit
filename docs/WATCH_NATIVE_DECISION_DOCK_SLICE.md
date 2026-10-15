# Native Watch decision-dock vertical slice

**Status:** Implemented and developer verified on `feature/watch-native-decision-dock-v0`, 2026-10-15. Operator checks 281–285 remain pending; no merge or final Watch-layout acceptance is implied.

**Purpose:** Convert the accepted chart-edge AMDX reference-and-decision interaction into the smallest useful native proof without rewriting the Watch shell, duplicating calendar ownership or presenting fixture rules as published Trade Plan policy.

Read with the [complete Watch interaction specification](WATCH_COMPLETE_COMPOSITION_INTERACTION_SPEC.md), [operator review](WATCH_COMPLETE_COMPOSITION_OPERATOR_REVIEW.md), [cross-suite interaction standards](UX_INTERACTION_STANDARDS.md), [AMDX shared-native guide](AMDX_SHARED_NATIVE_GUIDE.md) and [AMDX rule-definition framework](AMDX_RULE_DEFINITION_FRAMEWORK.md).

## Accepted interaction exemplar

The operator accepted the bounded prototype interaction as the desired quality target:

> “Bam. Two clicks, AMDX for that entire 90m quartet dealt with … Smooth, snappy, lightweight.”

The reusable pattern is not merely low click count. It is a **contextual completion loop**:

1. open the relevant support at the point of discernment;
2. show the exact target, applicable rule context and only legal choices;
3. invoke the already-authoritative command once;
4. show the synchronized result everywhere that projects that state;
5. dismiss the temporary support and restore the operator's prior anchor.

This pattern should be reused across the suite where it reduces hunting or memory burden. It does not justify repeating state owners, Save steps or entire workflows.

## Why this is the first native boundary

The present application already has the difficult domain behavior:

- `AMDXSharedContextWidget` binds Watch/TDA to the maintained calendar;
- `AMDXContextWidget.choose(...)` owns legal-role input, direct `X(C)` / `X(R)`, unresolved `X(?)`, pinned gesture scope, stale-state rejection and immediate revision semantics;
- `TradingDayShellWidget` owns the active Trading Day/run and captures the displayed AMDX basis transactionally;
- `LiveWatchWidget` owns the existing Watch process facts and actions.

The implemented native slice is a thin projection and composition seam, not a second AMDX editor. It exercises shared command/state, constrained choices, truthful failure, interruption recovery and chart-edge placement before a larger shell composition makes debugging harder.

## Included behavior

The first native slice is limited to active `live-watch` mode:

- a chart-facing **Plan reference** launcher in the current native Trading Day shell;
- one temporary side dock or bottom sheet chosen by a constrained monitor profile;
- the exact prepared AMDX target and current explicit/implied result;
- only the roles/subtypes legal for that target;
- direct use of the existing shared AMDX action—no repository write in the dock;
- immediate synchronization of the dock and existing `AMDXSharedContextWidget`;
- dismissal after a successful choice and focus return to the launching Watch anchor;
- unresolved `X(?)` support where legal;
- local explanations for unavailable, stale or failed actions, with no automatic replay;
- keyboard access using the same command path as mouse input;
- an explicit provenance line for the active Trade Plan revision.

The existing Watch layout and tabs remain reachable. The slice may be introduced behind a narrow native feature toggle during verification, but the toggle must not create different data semantics.

## Reference-content truthfulness

The prototype's AMDX definition and criteria text is fixture language. Alpha 0.7 does not currently publish a plan-owned AMDX manual-reference definition.

The native dock must therefore render a truthful state such as **“No published AMDX definition is configured for Trade Plan Alpha 0.7”** until a later versioned plan revision supplies that content. It may still expose the current target and legal manual inputs because those constraints come from the implemented AMDX cycle model. It must not promote freeform catalog notes, historical evaluation definitions or prototype copy into authoritative policy.

A plan-owned reference projection is a prerequisite for showing real criteria. Authoring, weighting, comparison and empirical evaluation remain the later UX4 criteria milestone; they are not smuggled into this slice.

## Native ownership map

| Native owner | Narrow responsibility in this slice |
| --- | --- |
| `amdx_context_widget.py` | Expose a small public read-only decision projection/change notification around the existing prepared target, legal choices, current result and availability; retain `choose(...)` as the command path. |
| `amdx_shared_context_widget.py` | Continue binding the maintained calendar and emitting successful shared revisions. No new state owner. |
| New contextual dock widget | Render plan provenance/reference availability and invoke the injected shared action. It never opens the repository or creates AMDX commands itself. |
| `trading_day_shell_widget.py` | Place/show/dismiss the support surface in live Watch, retain the launcher anchor and restore focus. |
| Workspace/display preference adapter | Remember only a constrained named physical profile and derive chart-facing edge. This is presentation state, not trading data. |
| `live_watch_widget.py` | Remain the owner of current Watch process content. No behavioral rewrite in this slice. |

## Required action contract

The dock receives one immutable projection at a time:

- target identity and human label;
- prepared scope/reference and availability;
- legal phase choices and legal X subtypes;
- current explicit role/subtype and inferred quartet profile;
- plan revision and reference-content availability;
- a change token suitable for rejecting stale gestures.

Its selection delegates to the existing command owner. A successful command updates the maintained calendar and normal run capture through the existing owned path. A stale or failed command keeps the dock open, preserves the attempted context for explanation and requires explicit Reload/retry. Merely opening, closing, moving focus or switching a monitor profile records nothing.

## Explicit exclusions

This slice does **not** include:

- a full Watch visual rewrite or replacement shell;
- real AMDX rule wording, rule authoring, classifier behavior or inferred confidence;
- Study Find drawer integration;
- broker connectivity, order commands, P&L or execution simulation;
- AMDX history/comparison in Watch;
- unrestricted docking or arbitrary pane construction;
- new calendar/repository ownership, schema migration or Trade Plan revision;
- macropad configuration, though the command seam must remain shortcut-friendly;
- final typography, palette or global settings application.

## Verification boundary

Automated native tests should prove:

1. the dock and existing AMDX panel show the same target and legal choices;
2. Q-position constraints remain exact—illegal roles cannot be invoked through either route;
3. one dock choice creates exactly the same calendar/run result as the existing control;
4. direct `X(C)` and `X(R)` remain one action and unresolved `X(?)` remains possible where legal;
5. both projections refresh after success, then the dock dismisses and focus returns;
6. stale target, changed run, changed tab/scope and write/read failures do not record or replay;
7. open/close/profile movement is inert and restart restores only the presentation profile, not an unfinished command;
8. absent published criteria is clearly unavailable rather than replaced by fixture text;
9. legacy/unbound Watch behavior remains reachable and unchanged;
10. the current complete regression and smoke identities are preserved.

The first operator guide should use a fresh disposable directory, exact control names and visible results. The review question is whether the same two-action loop feels equally immediate in native Watch—not whether the entire Watch composition is final.

## Implementation checkpoint

The existing `AMDXContextWidget` now publishes an immutable decision projection and retains its established command path as the only write route. `AMDXDecisionDock` renders that projection, shows truthful Alpha 0.7 reference unavailability, limits actions to the prepared quarter, and delegates choices back to the shared owner. `TradingDayShellWidget` supplies the Watch-only launcher, dismissal and focus return. Workspace settings retain only the constrained `tv-left` / `tv-below` display profile.

Automated coverage includes projection synchronization, legal-role constraints, direct X subtype selection, stale/failure handling, profile persistence, focus return and the rule that the single-key shortcut cannot steal text entry. The retained synthetic demo and exact operator procedure are documented in [the operator guide](WATCH_NATIVE_DECISION_DOCK_OPERATOR_GUIDE.md). Checks 281–285 are deliberately separate from developer verification.

## Following milestones

1. **Operator review:** complete checks 281–285 against the retained native demo before broadening the pattern.
2. **Contextual Study Find:** reuse the same open / act / return-anchor mechanics around the existing draft and screenshot-capable Study Find widget.
3. **Quiet Watch composition:** reorganize existing Watch projections around changed facts, compact AMDX now and process-safety priority without changing their owners.
4. **Study-first doorway:** implement the accepted competency/question on-ramp and safe active-run routing.
5. **Integrated Lab/criteria work:** connect the broader Study workspace, full AMDX lens and versioned definition authoring/evaluation.

This ordering is deliberately incremental. It proves a reusable native interaction grammar before applying it to the larger suite.
