# Quiet Watch and support-return interaction specification

**Status:** Proposed focused journey for operator review. This disposable standalone prototype is not final styling or native implementation.

Read with [UX Context Reconciliation](UX_CONTEXT_RECONCILIATION.md), [UX Friction Research](UX_FRICTION_RESEARCH.md), [UX Design Touchstones](UX_DESIGN_TOUCHSTONES.md) and the accepted [TDA layout-parity review](TDA_LAYOUT_PARITY_OPERATOR_REVIEW.md).

## Review question

Can Watch keep the current thesis, next relevant action and AMDX position legible with low visual competition, while allowing either a direct active-cycle update or a contextual Study capture and then returning the technician to exactly the same operating place?

This review is about selective attention, direct permitted entry, support-tool access, context preservation and return behavior. It does not publish a Watch layout, define a classifier, create a new Study record type or change runtime permissions.

## Prototype fixture

The prototype uses a synthetic active MNQ run at **10:42 ET / NYAM**. It shows:

- a quiet attention state;
- one current thesis and one next relevant action;
- two carried TDA conclusions and a compact authorization statement;
- one consolidated AMDX area containing quiet higher context, the session quartet and the active 90-minute quartet;
- a Q4 active 90-minute target so `D`, `X(C)`, `X(R)` and `X(?)` can be tested as direct legal choices;
- a contextual Study Find support surface;
- a larger AMDX inspection surface with an explicit return to Watch.

All data is disposable browser-local fixture state. The prototype does not use the operator database.

## Proposed interaction

### Quiet Watch

- Watch opens on the current operating state rather than history, comparison or a dashboard of every stored field.
- The central attention surface answers: **What matters now? What am I waiting for?**
- TDA carry-forward, thesis and authorization remain visible but compressed.
- AMDX information is consolidated in one adjacent region rather than split across the screen.
- Quiet higher-order context remains visible as an orientation rail; current session and active 90-minute context receive more detail.
- State and selection use borders, markers, labels and restrained color together. Color is not the only carrier of meaning.

### Direct active-cycle update

- Selecting `D`, `X(C)`, `X(R)` or `X(?)` on the active Q4 target records the new working interpretation immediately in this prototype.
- There is no second Save action.
- The selected target stays pinned if the simulated clock advances.
- `X(C)` and `X(R)` are separate one-action choices.
- The prototype preserves an earlier value only as a local revision count; it exposes no Watch history or comparison route.
- This is a renderer trial over the already accepted shared-action semantics. It does not propose automatic phase classification.

### Contextual Study capture

- **Capture Study Find** opens a support surface in one action without replacing the operating anchor.
- Instrument, Trading Day, session, time and active AMDX reference are visibly inherited from Watch.
- The technician supplies the observation and an optional pattern/lesson.
- The draft is locally recoverable if the support surface is closed.
- **Save & return to Watch** returns to the same selected interval, thesis and next action. It does not complete Watch, change the thesis or create a process transition.

The mature implementation may stage an existing `StudyFindDraft` and route through the existing Study Find save boundary. The prototype does not settle whether the support surface is a drawer, popover, task pane or dedicated workspace projection.

### Larger-context inspection

- **Inspect full stack** opens a spacious read/selection surface for the same maintained calendar state.
- It retains the Watch return anchor and current interval.
- Inspection alone records nothing, changes no thesis and does not return the process to TDA.
- A separate **Return to Analysis** process command remains available for a genuine thesis-level reassessment, but that transition is not exercised in this prototype.

## Information hierarchy

Always visible in Watch:

- current mode, instrument, Trading Day, session and market time;
- quiet/attention cue;
- current thesis and next relevant action;
- compact TDA carry-forward and authorization state;
- whole-stack AMDX orientation, current session and active 90-minute target;
- one-action support commands.

Visible only during contextual capture:

- inherited capture basis;
- observation and optional pattern/lesson fields;
- draft state and explicit save/return controls.

Visible only during larger inspection:

- spacious all-layer stack;
- selected-level detail;
- explicit unchanged return target.

Purposefully absent from Watch:

- AMDX revision history or before/after comparison;
- a raw evidence feed;
- completed-day history;
- correctness scoring;
- automatic readiness percentages;
- an embedded chart;
- full Study Find review or criteria authoring;
- a second mandatory Save for direct phase entry.

## Architecture mapping

| Prototype concept | Existing substrate | Possible additive follow-up |
| --- | --- | --- |
| Watch operating anchor | `TradingDayRuntimeWidget`, `LiveWatchWidget`, active `TradingRun` | Presentation composition only |
| Current thesis / evidence | `TradingRun.current_thesis_state`, run evidence | Quieter current-state projection |
| TDA carry-forward | `TDAStationSession` summaries and watch points | No new ownership |
| AMDX now | Shared master calendar binding, run capture and `AMDXContextWidget` | Context-specific Watch renderer over shared actions |
| Immediate active-cycle revision | Accepted `revise-working-v1` action and legal-position controls | Direct button/shortcut composition |
| Study support capture | Existing `StudyFindDraft`, `StudyFindWidget` and draft persistence | Context-seeding/routing adapter if accepted |
| Full-stack support inspection | Existing AMDX catalog/full-stack route and run scope | Explicit return anchor and quieter Watch handoff |
| Return to Analysis | Existing `live-return-analysis` transition | Keep separate from inspection/navigation |

The architecture supports the journey without a new database owner or duplicate AMDX catalog. Exact composition and any contextual Study-draft adapter remain open until review.

## Goal-based operator review

Use the prototype at a normal 16:9 window. The interface is under test; these are goals, not button-by-button instructions.

1. Orient yourself: identify the active session, current thesis, next relevant action and where the active 90-minute cycle sits in the stack.
2. Change the active 90-minute interpretation to `X(R)` in one deliberate action. Confirm there is no extra Save and no history panel appears.
3. Capture the observation **“Displacement arrived after the London high raid”** as something worth studying. Add any short pattern label, save it and continue watching.
4. Confirm the same Watch location, interval, thesis and next action remain current after return.
5. Open the full AMDX context, inspect a higher level, then return. Confirm inspection did not alter the Watch interpretation or process state.
6. Start another Study capture, type part of a note, close it, reopen it and confirm the draft is recoverable.
7. Reload the file. Confirm the operating position and unfinished support draft can be reacquired without reconstructing them.

Record whether the operator hunted for the current action, confused support access with process navigation, lost the active interval, expected a second Save, or felt that inactive information competed for attention. Comments on density, labels, borders, colors and input-device mapping remain useful without becoming final styling decisions.

## Acceptance boundary

This trial can accept the **quiet hierarchy and support-return relationship** while rejecting its exact columns, labels, typography, palette, buttons or task-pane form. Success does not authorize native implementation by itself.

The trial must not be reported as evidence that:

- the sample thesis or AMDX values are correct;
- the sample Watch content is a published Trade Plan;
- a new Study Find was saved to the real repository;
- a native return anchor already exists;
- final keyboard, mouse or macro-pad bindings have been chosen.
