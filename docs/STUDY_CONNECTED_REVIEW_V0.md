# Connected investigation review

## What this milestone does

Retained investigation material and Take stock are now a local Study view beneath the existing question and selected-reference header. Investigation overview opens inspection; Review this investigation opens the same view with its existing review fields ready. Return to investigation returns to Calendar. The current capture remains a separate existing editor with its own identity and destination.

The shared content supports the earlier standalone dialog shell, without duplicating domain operations. The embedded view removes the duplicate question heading and duplicate saved-checkpoint history: prior checkpoints remain in the central retained-material list and its filter. Saving a checkpoint refreshes that list immediately. Full-size charts retain their independent window/Close/Escape behavior. The underlying question is temporarily read-only while viewing retained material so editing a new question cannot silently change a review's scope.

## Protection and limits

An unfinished review (text or explicitly selected support) requires Cancel or Discard before leaving through the local selector, Return, global tabs, New/Resume investigation, capture entry or application close. Cancel retains the same review instance, text, support and identity; it does not notify downstream navigation consumers of a successful transition. Discard clears only that unsaved review. Saved captures, questions, findings and checkpoints remain. Failed saves keep the review available.

Hiding review entry or inspecting/filtering material stays inside the same view and does not discard it. Saved reviews remain read-only; Start a later checkpoint is the existing action for another entry. New/Resume still honors the separate unfinished-capture protection. No new fields, automatic evidence promotion, competency scoring, schema change (53), review autosave or crash recovery for unsaved review text are claimed. Normal close is protected; a killed process is not a saved checkpoint.

This is a connected-workspace slice, not final styling. The view scrolls at smaller sizes. Cross-investigation history and the global saved-find browser remain separate supporting tools. TDA → Watch integration review is the next broader milestone.

## Operator checks — after publication only

Use the existing durable workspace. No new fixture or full study session is needed. If you have a meaningful unfinished review, save it before trying disposable text.

### 364 — retained work belongs to the current Study view

1. Open Study and resume an existing investigation with material, if one is not already current. If an unfinished capture blocks switching, use its provided return action and save or deliberately discard it as appropriate.
2. Click **Investigation overview…**. Retained material should appear inside Study, beneath the same question/reference header, rather than in a separate overview window.
3. Inspect an existing capture or checkpoint. If an image is available, open it full size and close that image with Escape or Close; return to the embedded material view.
4. Click **Review this investigation…**. The review prompts should be immediately available in that same view. Use **Return to investigation** or select Calendar to return when the review is empty/saved. Existing capture content and the selected calendar reference must remain unchanged.

### 365 — an unfinished review cannot disappear silently

1. Open **Review this investigation…**. In **What remains uncertain or conflicts?**, type `Disposable navigation check — do not save` (use only this disposable thought for this check).
2. Select Calendar in the Study view selector. Choose **Cancel** in the unsaved-review prompt. The same review and wording should remain.
3. Click a different global tab, such as Guided TDA. Again choose **Cancel**. You should remain in Study with the same wording.
4. Try closing the Cockpit window; choose **Cancel**. The window should remain open with the review intact.
5. Select Calendar again and this time choose **Discard**, intentionally discarding only the disposable review thought. Reopen Review this investigation: that discarded text should be absent. Existing saved material must remain.

Saving review checkpoints and their immediate list refresh are covered by developer tests. If you naturally have a useful reflection, you may save one and see it appear; no artificial saved checkpoint is required for acceptance.

## Developer verification

Validation: 51 targeted tests PASS across connected review/navigation, retained-material reading, review checkpoints/question capture, capture feedback, investigation resumption, startup, Watch context/composition and media storage. Ten affected checks rerun PASS after embedded layout/question-lock adjustments. Native 1600×900 and 1120×800 views inspected; smaller layout scrolls. Embedded chart Escape, support-only cancellation and failed-save retry verified. Diff check passed.

## Delivery

Roadmap reference #110 accepted by operator. This branch updates that single roadmap source to this milestone. Prepared locally on `feature/study-connected-review-v0`, intended draft stacked on #110; no publication or merge claimed. Validation results are recorded in PROJECT_STATE.md.
