# Complete Watch composition interaction specification

**Status:** Complete Watch composition directionally accepted. The chart-adjacent shared-action decision dock passed bounded operator review and is now a reference for the [first native vertical slice](WATCH_NATIVE_DECISION_DOCK_SLICE.md). Read the [operator review](WATCH_COMPLETE_COMPOSITION_OPERATOR_REVIEW.md). This remains a synthetic composition trial, not native implementation, broker integration, a published order workflow or final visual approval.

Read with the [earlier Quiet Watch specification](WATCH_QUIET_SUPPORT_INTERACTION_SPEC.md), [operator review](WATCH_QUIET_SUPPORT_OPERATOR_REVIEW.md), [broader Study-first Lab review](LAB_STUDY_WORKBENCH_OPERATOR_REVIEW.md), [UX design touchstones](UX_DESIGN_TOUCHSTONES.md) and [workspace parity](WORKSPACE_PARITY.md).

## Review question

Can Watch present the current operating situation, next relevant action, nested AMDX position and process-safety state as one quiet composition—then increase salience only when a real safety condition changes—across the two most likely chart/Cockpit monitor arrangements?

The trial extends the accepted Watch support-return behavior. It does not re-review the isolated AMDX Lab, add P&L, submit orders, choose a broker API, publish risk values or settle final shell navigation.

## Composition model

The prototype uses four coordinated regions:

1. **Chart-facing orientation edge.** The closest Cockpit edge to TradingView repeats only the physical reacquisition cues: mode, session/time, active interval, next-action verb and safety state.
2. **Operating canvas.** Current thesis, one primary next action, watch points, setup criteria and compact TDA carry-forward answer what matters now.
3. **AMDX now.** A quiet ancestor path plus spatial daily-session and active-90-minute quartets replace the earlier flat all-layer list. One legal active-quarter choice records immediately; the full maintained calendar remains a separate Lab route with a Watch return anchor.
4. **Process-safety strip.** Connection, environment/account, authorization, risk envelope, position and staged/submitted state remain adjacent and always visible. They are not optional support widgets.

Study Find remains a contextual drawer. The main layout does not rearrange around support activity, and saving returns to the same Watch anchor.

## Chart-adjacent Trade Plan reference

The chart-facing edge offers a concise definition/criteria/process reference for manual AMDX discernment. It follows the physical chart relationship: left-side popout when TradingView is left, bottom sheet when TradingView is below. It opens with one click or `P`, closes to the same Watch anchor and does not add a permanent dashboard pane.

The accepted refinement places the exact active target and legal `D`, `X(C)`, `X(R)` and unresolved `X(?)` choices at the end of that reference. These buttons invoke the same shared immediate action as **AMDX now**; they are not a second owner or workflow. A choice updates both projections, appends the same revision and dismisses the popout. There is no second Save. This temporary duplication is justified only at this one rule-consultation/decision step.

Prototype wording is explicitly a fixture, not an Alpha 0.7 published rule. The mature surface must resolve its content and provenance from the active versioned Trade Plan. Full definition authoring, comparison and empirical evaluation remain Lab / Trade Plan work. This interaction follows the accepted [cross-suite UX standards](UX_INTERACTION_STANDARDS.md).

## Quiet versus safety salience

The normal fixture is intentionally recessive: connected, Forward Test / Sim101, flat, no candidate and no staged order. It does not use green to demand attention merely because nothing is wrong.

The scenario controls expose synthetic states solely to test hierarchy:

| Scenario | Expected presentation |
| --- | --- |
| Quiet | Safety strip is legible but subordinate; no immediate action |
| Candidate blocked | Amber emphasis identifies the unmet criterion and a locally staged, unsubmitted order |
| Connection lost | Strong safety emphasis; submission is unavailable and no trading action is offered |
| Staged draft | Clear distinction between staged locally and submitted to broker; no P&L or submit button |

Safety-critical meaning cannot be hidden by changing the contextual support tool. The mature system must source each fact from its existing plan/runtime/broker owner and keep unavailable distinct from safe.

## Broker/process-safety boundary

The synthetic broker projection answers:

- connection state;
- environment and account identity;
- authorization/gate result and reason;
- risk-envelope usage;
- position and working-order state;
- staged versus submitted state.

It intentionally omits realized/unrealized P&L, flashing market colors, performance rank, account-balance stimulation, order entry and cancellation. A future broker adapter may project facts and accept authorized commands only through a separately reviewed execution-safety boundary. This prototype authorizes neither.

## AMDX and current-action boundary

Watch retains only current maintained orientation and direct active input:

- quiet ancestor path: Year → Month → Week → Trading Day;
- daily sessions together using the restrained chart-matched session palette;
- active NYAM 90-minute quartet with Q4 selected;
- direct `D`, `X(C)`, `X(R)` and unresolved `X` choices for legal Q4 input;
- no second Save, history, comparison or classifier;
- **Open AMDX lens** routes to the accepted spacious Lab relationship and preserves the Watch return anchor.

The synthetic AMDX route preview is only evidence that navigation/return stays distinct from process transition. It is not another calendar implementation.

## Monitor profiles

### TradingView left / Cockpit right on one ultrawide

The chart-facing orientation rail sits on Cockpit's left edge. The next-action verb, NY session/time, active interval and safety state should be reacquired before the eye crosses the full Cockpit.

### Cockpit above TradingView on a dedicated 16:9 monitor

The orientation rail becomes a bottom edge strip because TradingView is physically below. The same logical cues move without changing their meaning, current selection or command bindings.

These are explicit composition profiles, not arbitrary docking. A mature preference may remember one profile, but this fixture adds no persistence owner beyond browser-local prototype state.

## Goal-based operator review

Judge the composition at a normal 16:9 size before changing profiles.

1. Start in **Quiet**. Look away, then return and identify session/time, active 90-minute quarter, next action and whether broker/process attention is required.
2. Record `X(R)` on active 90-minute Q4. Confirm it is one action, remains current and exposes no history or second Save.
3. Switch through **Candidate blocked**, **Connection lost** and **Staged draft**. Confirm the changed safety fact becomes apparent without making the whole screen noisy.
4. Confirm staged versus submitted is unmistakable and that no P&L or order-submit control appears.
5. Capture a Study Find, close/reopen its draft, then save. Confirm the same Watch anchor, thesis, AMDX position and safety scenario remain.
6. Open the AMDX lens preview and return using the command in the same ribbon position. Confirm this feels like nearby context rather than a process transition.
7. Switch between **Ultrawide · TV left** and **Dedicated · TV below**. Look toward the imagined chart location and back; judge whether the moved orientation edge is useful or merely duplicative.
8. Open **Plan reference** from the chart-facing edge or press `P`. Confirm its definition, process, criteria, active target and provenance are easy to consult while moving between the imagined chart and Cockpit.
9. Choose `X(R)` from the popout. Confirm it records immediately, dismisses the reference, updates **AMDX now** and requires no second Save. Reopen the reference and confirm `X(R)` is current there too.
10. Reload and confirm profile, scenario, AMDX choice and unfinished Study Find draft are recoverable.

Record where attention goes first, what still requires deliberate reading, whether any quiet fact competes with the next action, whether the safety strip is sufficient, and which monitor profile should be the standard default.

## Acceptance boundary and next milestone

This trial may accept the complete Watch relationship and one or both orientation profiles while rejecting exact geometry, typography, labels, sample content or scenario controls.

Monitor profile buttons remain fixture controls for comparison. In the mature suite, monitor relationship and chart-facing edge belong to a remembered global Workspace & Displays profile, adjusted rarely and previewed explicitly. Unrestricted panel docking is not implied.

The bounded shared-action dock review is complete. The selected first native boundary is the chart-edge decision dock over the existing Watch and shared AMDX owners. It proves one contextual completion loop before Study Find integration, broader quiet-Watch composition or Study-first routing. Direct broker commands, execution simulation and broad shell replacement remain later milestones.
