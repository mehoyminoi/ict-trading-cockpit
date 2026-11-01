# Development roadmap reference

## Purpose and scope

The operator requested a quick human-readable outline to keep the full workflow destination visible while testing individual changes. Help → Development roadmap opens a nonmodal, read-only reference with Accepted / In progress / Next / Deferred stages, the current operator check and an update marker. Close or Escape returns to existing work. No estimates, competency scores, project data entry, schema change or database access.

The single content source is `src/ict_cockpit/development_roadmap.md`, included as package data. Update it when acceptance, the active check or priorities change. It is a snapshot of the installed version, not a live remote status feed. Do not duplicate its full contents in another roadmap. The engineering history remains in the existing project documents.

Previous #109 correction: operator confirmed both review redo and Observation cue checks PASS. That bounded correction is accepted; suite-wide feedback coverage remains deferred.

## Operator check (pending)

From existing work, open Help → Development roadmap. Read/scroll the stages, close with Escape or Close, and confirm the same work remains. No full study session, new fixture or new capture required.

## Verification

Six existing connected-workspace/capture-feedback tests PASS. Native offscreen reference inspected at 760×650; resource loading, read-only display, scrolling, Escape and reopen verified. Actual MainWindow Help action checked with an existing capture: active page, draft content and database change count remain unchanged after opening/closing. Diff check passed.

## Next boundary assessment

`StudyInvestigationOverview` currently subclasses QDialog. Its `done()` calls `review_panel.can_leave()`; that panel protects unsaved text and selected support through a Cancel/Discard choice. `StudyWorkspace` currently switches pages without a leave contract, and MainWindow close currently saves geometry without consulting an embedded review. Therefore embedding retained work/review is not just reparenting.

Next slice must establish a shared leave guard for local view changes, investigation switches, global navigation and application close before removing modal protection. Cancel must retain the exact question, text, sources, selection and page. Saved reviews remain immutable. Separate reusable retained-material content from the dialog shell, reuse repositories and preserve explicit support associations. Refresh newly saved material without replacing an unfinished review. Keep full-size image ownership and Escape behavior valid. No new review fields or analytical claims are required.

This assessment does not implement embedded review. TDA → Watch integration review remains the next broader journey after the Study boundary is resolved.

## Publication

Prepared locally on `feature/development-roadmap-v0`; intended draft stacked on #109. No publication or merge claimed. Publication requires the separate authorization used for this project.
