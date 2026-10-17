# Native quiet-Watch composition vertical slice

**Status:** Developer-verified on `feature/watch-quiet-composition-v0`, 2026-10-16. Operator checks 291–295 remain pending; no broker integration, merge or final Watch-layout acceptance is implied.

**Purpose:** Compose the two accepted contextual interactions inside one real native Watch surface that makes current operating context, maintained AMDX position and process-safety truth simultaneously reacquirable. This is a presentation boundary over existing owners, not a replacement runtime or a new dashboard state model.

Read with the directionally accepted [complete Watch composition](WATCH_COMPLETE_COMPOSITION_INTERACTION_SPEC.md), its [operator review](WATCH_COMPLETE_COMPOSITION_OPERATOR_REVIEW.md), the accepted [native decision dock](WATCH_NATIVE_DECISION_DOCK_SLICE.md), accepted [contextual Study Find](WATCH_CONTEXTUAL_STUDY_FIND_SLICE.md) and [cross-suite interaction standards](UX_INTERACTION_STANDARDS.md).

## Composition to prove

The active Watch page now coordinates four regions:

1. **Chart-facing orientation edge** — Watch/session, New York market time, exact active AMDX target, safety summary, next attention cue, Plan reference and Study Find launchers.
2. **Operating canvas** — the existing Live Watch current-state, TDA carry-forward, setup/gate, thesis and observation controls, hosted in its own scrollable region rather than forcing the whole Watch page to scroll.
3. **AMDX now** — a compact projection of the maintained source's day/session and active 90-minute quartets, exact legal role choices and full-Lab route. It invokes `choose_decision` on the existing `AMDXSharedContextWidget`; it owns no history or command.
4. **Broker & process safety** — environment/purpose and current authorization facts beside explicit unavailable broker, account, risk-envelope, position and order facts. P&L remains absent.

The full shared AMDX editor is hidden only while this Watch projection is active. TDA and Review retain the established editor. The existing decision dock and Study Find surface open from the chart-facing edge and return focus to those same buttons.

## Truth and ownership boundary

- `LiveWatchWidget` remains the owner of existing Watch controls and uses the same run-save paths.
- `AMDXSharedContextWidget` remains the maintained calendar projection and sole AMDX command owner.
- `AMDXDecisionDock` and `ContextualStudyFindDock` retain their accepted behavior and owners.
- `TradingRun` remains the source for environment, purpose and authorization state.
- No broker adapter exists in Alpha 0.7. The safety strip therefore says **Adapter not connected**, **Account identity unavailable**, **Position unavailable**, and **Order submission is not implemented**. Unavailable is never presented as safe, flat or connected.
- The safety strip adds no P&L, balance, performance stimulation, order staging or submission command.

## Named monitor profiles

The same remembered `workspace-displays/chart-relationship` setting controls the composition and reference dock:

- `tv-left`: a vertical orientation rail on Cockpit's left edge;
- `tv-below`: the same rail becomes a horizontal bottom edge.

Switching profile changes placement only. It does not change the run, AMDX target, Watch draft, process mode or command bindings. Arbitrary docking remains excluded.

## Included behavior

- one native four-region Watch composition at the existing 16:9-first application scale;
- fixed safety visibility while the operating canvas scrolls independently;
- current-page runtime sizing so hidden TDA/Review pages cannot force Watch below the viewport;
- compact maintained AMDX table selection and immediate legal role/X-subtype entry;
- no Watch AMDX history/comparison route;
- accepted Plan reference and Study Find launch/return behavior on the chart-facing edge;
- explicit unavailable broker/account/risk/position/order states and absent P&L;
- constrained remembered `tv-left` / `tv-below` profiles;
- retained synthetic demo and five operator checks.

## Explicit exclusions

- broker/NinjaTrader connection, account discovery or order commands;
- invented flat/connected/ready facts, numeric risk limits or Trade Plan policy;
- P&L, balance or performance presentation;
- new AMDX, Watch, Study or workspace persistence ownership;
- durable Study Find run/time/AMDX linkage;
- unrestricted panel docking, final shortcut settings or final theme/palette;
- final geometry, density, typography or whole-suite navigation approval;
- Study-first startup routing or integrated Lab/criteria authoring.

## Verification boundary

Automated and operator checks must prove:

1. all four regions remain simultaneously available in active Watch and the full AMDX editor is not duplicated there;
2. AMDX now selects the existing maintained target, exposes only legal roles and records through the same immediate command, including one-action `X(R)` where legal;
3. broker/account/position/order unavailability is explicit, P&L is absent and a real authorization change earns salience without making quiet state look positive;
4. Plan reference and Study Find retain their accepted draft/save/action/focus-return behavior from the new edge;
5. the two named profiles move one orientation edge, persist through restart and preserve run/process/AMDX state.

The trial asks whether the composition materially improves reacquisition and keeps the safety boundary legible. It does not ask for final visual approval.

Developer verification is **1,155 PASS across 95 isolated module processes**, with zero failures, errors, skips or warning-bearing logs. The focused quiet-composition and restart modules contribute six of those checks. Python 3.10 grammar, both named offscreen render profiles, CLI help, changed-document links and `git diff --check` also pass. Runtime: Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, Qt offscreen.

## Following milestones

1. bounded operator trial and density/reacquisition notes for this native composition;
2. Study-first doorway and safe active-run startup routing;
3. integrated Lab/criteria work, including explicit Study Find context association when its data contract is reviewed;
4. real broker projection only behind a separately reviewed execution-safety boundary;
5. global Workspace & Displays and input-binding settings after repeated native use.
