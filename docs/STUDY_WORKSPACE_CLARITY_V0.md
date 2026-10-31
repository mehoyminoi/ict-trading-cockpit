# Study workspace clarity — first native UX pass

## Evidence and intent

2026-10-30: the operator completed a natural Study session and return visit with a real question. The last question and related retained work restored study intent; common threads in wording and chart markup began to emerge. Connected Study continuity is accepted. Presentation remains dense and requires sifting. This does not establish automated pattern detection, empirical prioritization or competency.

New/Resume appeared inert because an authored capture blocked switching; resolving the old capture unblocked both. This is an explanation/discoverability failure, not a request to remove the guard. Native Ctrl+Z was noticed and appreciated. Preserve familiar editing, screenshot paste, selection-based question capture, fresh next captures and direct review entry.

## Composition implemented

- Current question occupies its own prominent row with Resume and New. A separate state line explains retained read-only wording.
- Three primary actions remain exposed: Open Study Find, Investigation overview, Review this investigation. These continue to invoke the same owners and routes.
- Supporting tools are deliberately disclosed: Plan criteria (edit/evaluate) and Retained work (saved finds, questions, findings, history). This reduces the standing stack of full-width buttons. Disclosure is presentation-only, default collapsed per window; it does not adapt to usage or change data.
- A blocked switch displays an inline explanation and Return to unfinished capture directly beneath the question controls. Keyboard focus moves to that recovery action. Navigation returns to the exact existing editor without invoking default seeding, context assignment, saving or discarding. Existing return-to-investigation navigation is exposed there.
- Investigation overview offers a material-type filter over its existing explicit associations. Hidden rows retain identity; no matches clears the inspector instead of leaving unrelated detail visible. Review text and selected support survive filter changes. Criteria results, captures and findings remain distinct; review checkpoints remain in the existing review panel and questions in their existing browser.
- Outdated Link-this-capture guidance now names the combined Save to investigation route. Empty overview guidance points to capture rather than suggesting criteria evaluation as the first step.

## Boundaries and next UX work

This is the first native composition slice, not the full Lab redesign. Existing AMDX/calendar controls remain. Broader Lab identity, Study-first competency entry, quiet nested/deep calendar, chart-edge context, mapped TDA pane parity and distinct Watch operation remain governing requirements. No invented evidence gaps, progress scores or recommendations. No new schema, storage owner, background analysis or lifecycle state.

Further work should improve the overview's content hierarchy and chart/observation presentation using this accepted real-session feedback. Do not expand into automatic common-thread detection just because repeated concepts are visible. Keep current reference near capture and retain broader HTF context. Revisit full 16:9 composition as these regions mature; this bounded header is not final styling.

Tradeoff: criteria and cross-investigation browsers now require opening Supporting tools. They are secondary to current-question capture/inspection/review, remain grouped and keyboard accessible, and do not move unpredictably. The primary quick-question/finding controls inside capture and review are unchanged.

## Operator 356 — return from a blocked switch

After publication, use the existing durable workspace. Do not pull an unpublished branch.

With a disposable unfinished note in Study Find, return to the investigation and try Resume or New. Expect the explanation and Return to unfinished capture nearby. Activate that action; expect the same content and destination. Save or deliberately discard the disposable work, return and resume normally. No extra complete Study session is needed. Confirm that the primary controls and Supporting tools grouping make the next action easier to find.

## Operator 357 — narrow retained material

Open an investigation with saved material. Use Show material to narrow to captures or findings; All material restores the list. An empty category should say so. If reviewing, type a disposable thought and change the filter: the review text must remain. Cancel/resolve the unsaved review normally. No obligation to create material in every category.

Operator 356–357 pending. Publication requires explicit authorization: feature/study-workspace-clarity-v0, draft stacked on #105; do not merge. Earlier local connected-workflow documentation is included in this branch.

## Validation

19 targeted tests PASS across workspace clarity, investigation resume, direct review, overview and integrated Study. After adding notice dismissal on return from a resolved draft, the three new clarity tests passed again. Offscreen Qt rendering inspected for the ordinary and blocked headers at a 1440-pixel window. Diff check passed. This does not replace real operator layout acceptance or certify all screen sizes. No changes to capture text widgets or their native undo behavior.
