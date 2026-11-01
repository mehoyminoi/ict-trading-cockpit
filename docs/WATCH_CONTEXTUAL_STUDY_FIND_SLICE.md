# Native contextual Study Find vertical slice

**Status:** Implemented, developer verified and operator accepted through checks 286–290 on `feature/watch-contextual-study-find-v0`, 2026-10-16. No merge or final Watch-layout acceptance is implied.

**Purpose:** Reuse the accepted contextual-completion grammar for Study Find capture inside active Watch without replacing the Watch shell, duplicating Study Find persistence or presenting transient Watch context as a durable association that the current schema does not store.

Read with [Quiet Watch and support return](WATCH_QUIET_SUPPORT_INTERACTION_SPEC.md), its [operator review](WATCH_QUIET_SUPPORT_OPERATOR_REVIEW.md), the [complete Watch composition](WATCH_COMPLETE_COMPOSITION_INTERACTION_SPEC.md), the accepted [native decision-dock slice](WATCH_NATIVE_DECISION_DOCK_SLICE.md) and [cross-suite interaction standards](UX_INTERACTION_STANDARDS.md).

## Accepted interaction to prove

1. open Study Find from the active Watch anchor in one action;
2. see the exact current Watch basis and any existing unfinished draft;
3. capture an observation, optional pattern/lesson and managed chart screenshot;
4. preserve the draft across dismissal/reopen/restart;
5. save through the existing Study Find command and repository;
6. dismiss and return to the same Watch anchor without changing process or AMDX state.

This is the second deliberate use of the open / act / return-anchor grammar. It does not establish a generic popout framework.

## Ownership and truthfulness

`StudyFindWidget` remains the single editable draft owner. The contextual surface projects a small subset of its fields and writes back through those existing controls. The existing `MainWindow` debounce and `StudyFindRepository` remain the only draft/save paths. Managed clipboard images use the existing media helper and are attached by the existing final-save path.

For an empty draft, the surface may seed the current futures Trading Day date, instrument and named session because those fields already exist on `StudyFind`. It must not overwrite a non-empty/restored draft. The active run label, exact market time and AMDX target/profile are shown as **current Watch context only**: the present Study Find schema does not retain those exact associations, so the surface must not claim that it saved them.

## Included behavior

- a Watch-only **Capture Study Find** launcher beside the chart-facing support controls;
- one modified shortcut that cannot be confused with ordinary text entry;
- a temporary chart-edge surface using the same constrained `tv-left` / `tv-below` relationship as the decision dock;
- current Watch basis plus explicit persisted-versus-display-only wording;
- pattern, observation and notes projections synchronized with the existing full Study Find widget;
- managed clipboard-image paste and visible attachment count;
- existing draft recovery, including images, without context overwrite;
- immediate draft flush on Escape, outside-click or explicit close;
- existing final save, followed by dismissal and focus return;
- local validation/failure text without process transition or automatic replay;
- automatic dismissal if Watch is no longer the active operating context.

## Explicit exclusions

- a new Study Find record, repository, table or schema migration;
- durable run/time/AMDX/competency association not already represented by `StudyFind`;
- evidence creation, competency credit or automatic Review interpretation;
- full Study Find summary/review/criteria authoring inside the contextual surface;
- Watch layout recomposition, arbitrary pinning/docking or multiple floating panels;
- broker/order behavior, P&L or chart embedding;
- final shortcut configuration, macropad bindings, styling or global settings UI.

## Verification boundary

Automated and operator checks must prove:

1. the launcher exists only in active Watch and carries the exact visible basis;
2. an empty draft receives only supported date/instrument/session defaults;
3. a non-empty/restored draft is never overwritten by the current Watch basis;
4. contextual edits and the full Study Find tab are the same draft identity/state;
5. Escape, outside-click and restart preserve the unfinished draft and images;
6. clipboard image paste uses managed storage and final save attaches it once;
7. invalid final save stays open with an actionable explanation;
8. successful save uses the existing repository, dismisses and restores the anchor;
9. opening, dismissing and saving do not change Watch mode, thesis, AMDX target/value or run identity;
10. leaving Watch or switching away closes the temporary surface without discarding its draft.

The operator review asks whether capture feels immediately available and safely resumable in the real native shell. It is not a final Watch-density or visual-design approval.

## Following milestones

1. broader quiet-Watch composition around changed facts and process-safety priority;
2. Study-first doorway and safe active-run routing;
3. integrated Lab/criteria work, including future explicit Study Find context associations;
4. global Workspace & Displays and input-binding configuration after repeated native use supplies evidence.

## Implementation checkpoint

`ContextualStudyFindDock` is a temporary projection of the existing `StudyFindWidget`. Its pattern, observation and notes edit that source directly; clipboard images use the established managed-media path; final save emits the existing Study Find command handled by `MainWindow`. Dismissal flushes the existing debounced draft owner immediately, while successful save dismisses only after the repository path completes.

`TradingDayShellWidget` supplies the Watch-only launcher, exact immutable opening basis and modified shortcut. Empty drafts receive only the supported date/instrument/session defaults. Existing drafts retain their identity and fields. Current run/time/AMDX context is visibly marked display-only because the present schema does not retain that exact association. Leaving Watch or the Trade Plan workspace closes the surface without discarding the draft.

Focused developer verification covers shared draft identity, safe defaults, no-overwrite behavior, dismissal/restart recovery, managed clipboard images, repository save, validation failure, focus return and unchanged run/mode/AMDX state. The retained demo and exact operator procedure are documented in [the operator guide](WATCH_CONTEXTUAL_STUDY_FIND_OPERATOR_GUIDE.md). The explicit 2026-10-16 operator report marks checks 286–290 PASS, accepting this bounded behavior without approving final Watch styling/layout or a future durable run/time/AMDX association.
