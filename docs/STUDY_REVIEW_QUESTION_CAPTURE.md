# Keep questions from a review pause

## Purpose

A useful follow-up question can arise while reflecting, not only while capturing a chart. Review now offers Keep question for later beneath its three prompts. It uses the existing question repository, composer, inbox and Study history; it does not create another queue or replace the working investigation.

Select wording in any review prompt and click Keep question for later to save it directly. The most recently focused/selected review prompt supplies the text. No selection opens the existing optional composer. Immediate repeated clicks with unchanged wording/source reuse the same question identity; a failed save can be retried without losing review input.

The question retains a frozen snapshot of the review identity, investigation/question, plan/revision, all three prompt texts, selected field, support snapshots and whether the review was a draft or saved checkpoint at that time. A draft review ID is labeled as a snapshot, not evidence that a checkpoint exists. Keeping the question does not save the review, alter its text, complete the investigation, create a Study Find or imply a market date. Discarding the unsaved review later does not remove the saved question.

The current review editor supports this action, including its read-only state immediately after saving. Selecting an older checkpoint in the history list does not change the question action's source to that older record: the source remains the three prompt editors. Capturing directly from arbitrary historical detail is outside this slice.

## Storage compatibility

Schema 53 is a reader-version barrier for question payload v2 (review source). Existing capture-source questions remain payload v1 and unchanged. Findings remain unchanged. Inbox and history understand both. The previous application version must not open a schema-53 workspace. Close Cockpit and back up/verify the complete durable workspace before first launch; retain that pre-upgrade backup. The verifier accepts schemas 51–53.

## Operator 355 — keep a question where it arises

Use the durable workspace after backup and update. Open Review this investigation.

1. In a review prompt, write a disposable question and highlight its wording. Click Keep question for later. Expect an inline confirmation without a popup. Click again without changing anything; it should not duplicate the question.
2. Confirm the review text remains. Do not save the review solely for this check. Return to the investigation; discard only this disposable review if prompted. Open Study questions or Study history filtered to Question. Confirm the saved wording, investigation and Draft review snapshot source are visible, with one retained question from the repeated click.
3. Return to review, leave no text selected, and click Keep question for later. The familiar composer should open. You may cancel it without adding another question; your review remains unchanged.

No new full study-session trial required. Operator 354 PASS is recorded. Operator 355 PASS (operator-reported). Next return to the dependable-workflow integration priorities rather than expanding this into another authoring surface.

Publication: draft PR #105, stacked on #104, remote `f537759`; unmerged.

Validation: 237 targeted tests PASS: 33 question/review/finding/history checks and 204 migration/repository/resumption/backup checks. New checks cover selected-text snapshot capture, immediate repeat deduplication, latest selection, failed-write retry identity, saved-review labeling, no-selection composer, unchanged unsaved-review guard, both retrieval surfaces, and the actual schema-52 upgrade with rollback and old-reader rejection. Existing capture questions and findings remain covered. Diff check passed. An initial test attempted to manipulate a read-only editor and entered the composer unexpectedly; it was corrected to select actual saved wording and the complete focused batch passed.
