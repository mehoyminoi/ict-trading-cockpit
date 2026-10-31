# Study workspace composition — assessment and implementation contract

## Assessment

Operator 358–359 PASS, including independent chart Close/Escape after the modal-ownership correction. The connected real-question session already established learning value and recovery of intent; recent native improvements make individual steps easier. No further full-session exercise is required before layout development.

The remaining problem is the frame around those steps. MainWindow puts Study startup, AMDX Lab, Study Find and Study Review in separate global tabs. IntegratedStudyTaskWidget is inserted into the AMDX calendar. Capture routes back to “AMDX investigation”; overview/review live in a modal dialog. A technician must remember that a general investigation is reached through AMDX and distinguish several similarly named review destinations. The underlying identity is stable, but its visual anchor changes.

This assessment is based on current source and accepted operator feedback, not a claim that a new composition has been tested. The proposed arrangement below is the next native layout direction. Final geometry, labels and styling remain adjustable.

## Proposed composition

| Region | Responsibility | Must not become |
| --- | --- | --- |
| Persistent Study header | Active investigation, plan revision, currently selected market reference, current view and access to Resume/New | Another editable copy of investigation identity or a new mandatory form |
| Main workspace | One selected task view: orient, calendar/context, capture, retained material or take stock | Every form open simultaneously |
| Contextual support | Existing definitions, questions, findings and other supporting tools when requested | A wall of permanent docked panels |
| Local save/recovery area | Exact capture destination, unsaved state, success/failure and valid recovery action beside the work | A remote status message that leaves the operator hunting |

The persistent reference is the selected calendar reference, explicitly labeled as such. An authored capture may retain a different reference/destination; show that difference beside the capture and keep the explicit alignment action. A header must not imply silent alignment, chart synchronization or reassignment.

## Views and entry intent

These are working labels, not new domain entities or mutually exclusive analytical modes.

| View / action | What is ready immediately | Preserved while moving away |
| --- | --- | --- |
| Study start | Existing recorded competency guidance, or an honest absence of guidance; route to current investigation | Existing run routing and capture restoration |
| Investigation | Current question and a concise route to its retained work and capture | Stable task identity and selected reference |
| Calendar / context | Existing maintained AMDX calendar, nesting and reference selection | Same question and draft destination |
| Capture | Existing editor, chart paste, local save destination and capture actions | Actual widget instance, undo stack, selection and autosave |
| Retained material | Existing scoped inspection with chart-first access and checkpoint history | Selection and any unfinished capture |
| Take stock | Existing review editor immediately ready, with support nearby | Unsaved review text and explicit close/leave protection |

These views need not all become always-visible buttons. Use a compact, labeled view selector or local navigation appropriate to the task. Different view entry must remain deliberate and predictable. Changing a view does not create a run, complete a task, save an observation or change evidence status.

## Important reconciliations

- **Broader Lab, not AMDX-only.** The accepted CAD-like workbench/lens concept remains the direction. General investigation controls belong to Study; AMDX is a maintained context lens. Do not delete its quiet availability or deeper calendar exploration.
- **Bird's-eye and detail together.** The header and quiet context support orientation while the center focuses on the task. Do not relabel mutually exclusive pages “Deck/Focus” and claim the spatial overview requirement is solved. TDA's mapped chart-pane parity remains separate and unchanged.
- **Capture persistence wins over old prototype behavior.** The earlier HTML specification imagined save-and-dismiss. Operator-accepted native full captures now prepare the next example with retained context. Preserve that loop in sustained Study capture. Brief Watch capture keeps its existing save-and-return behavior. Both use the existing command/data owners.
- **Study-first is not fabricated advice.** Keep the existing explicit recorded Development Direction basis. A recent checkpoint's next-step text is operator intent, not an empirical recommendation. No inferred deficiency, proficiency percentage or automatic common-thread ranking.
- **Escape is scoped.** Inspection dialogs should support independent Close/Escape. Unsaved authoring still requires its existing guard. Escape must never silently discard a review or observation just for consistency.
- **Chart relationship remains meaningful.** Target the accepted 16:9 cockpit area and chart-facing support convention. Do not hard-code a new global monitor profile or squeeze the W/D/15m/5m chart-context intent out of capture. Native image inspection must remain usable from every modal route.

## Smallest coherent native implementation

The next implementation should establish a Study container and stable investigation/context header using existing widget instances and routes. Begin with the investigation, calendar and capture relationship; avoid reimplementing repositories or rewriting the capture form. Keep retained-work and Take stock routes visibly attached to that same question, initially reusing their accepted dialog implementation.

Before moving widgets, enumerate MainWindow checks that depend on `tabs.currentWidget()` or `setCurrentWidget()`: calendar activation, run-scoped Study restrictions, contextual Watch capture, draft restoration, save behavior, return buttons and startup routing. Replace the affected global-tab assumptions with explicit Study route helpers. Reparenting alone is insufficient. Do not create a second editor or a mirrored draft for the new container.

A second bounded step may embed retained-material and review into the workbench, but only after giving the embedded review the same leave/cancel guard that its current modal dialog owns. Merely removing the modal boundary would lose that protection. Keep the accepted dialog until this transition is explicit and tested.

Avoid broad theme work, arbitrary docking, global shortcut configuration, auto-analysis, full question lifecycle and new capture fields in this slice. These remain future work. This layout should reduce navigation and memory demand with the functions already present.

## Acceptance gates for the implementation

Developer checks should demonstrate that navigation preserves exact question identity, reference distinction, capture ID/content/images, undo history and save destination; failed/canceled actions preserve the original work; startup and active-run routes remain truthful; Watch's capture flow is unchanged. Verify the real affected routes, not superficial button-count assertions.

Visually inspect at a representative 16:9 area and a narrower window. The current question, current task and next main action should remain visible without a column of repeated context notices. Keyboard traversal and native dialogs must work after reparenting. No silent draft or review reset during view changes.

Operator review should then be a short navigation pass with existing material: can you tell where you are and move calendar → capture → prior work without remembering which global tab owns the question? Do not request another full session just to validate the same persistence contract.

## Delivery state

This is a local assessment/design checkpoint, not an application change or a claim of final UX approval. The implementation boundary above is concrete; there is nothing new to pull or smoke-test. Existing draft PR #107 remains unmerged. Publication/merge authority is not extended by this document. Next work is the bounded native Study container, followed by separate TDA-to-Watch integration review and authorized stack consolidation as required by DEPENDABLE_WORKFLOW_MILESTONE.md.
