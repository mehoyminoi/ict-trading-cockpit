# Discard current Study Find draft

Operator 334–335 PASS. Retain selected-text direct save and blank-selection composer behavior; its discoverability remains a later optimization after repeated use, not an immediate interaction redesign.

The next bounded capture-lifecycle action is **Discard current draft…** at the bottom of Study Find. Confirmation defaults to Cancel. Confirming removes only the current unfinished draft record and starts a new capture identity with empty pattern, observation, notes, move value and attachment list. Date, instrument and session are retained as editable starting context; unrelated navigation does not supply replacement values.

Saved Study Finds are rejected by this action. Saved questions and their source snapshots remain unchanged. Immutable investigation association receipts remain; an abandoned capture can therefore be shown as unavailable rather than erased from provenance. Managed chart files are retained because existing question/source references may still use them. This is not a file cleanup operation.

Cancel preserves the draft. Delete failure leaves the form and pending autosave intact and reports failure. Confirmed deletion stops the old autosave and clears its pending payload before the form changes. The replacement is emitted only after it is fully constructed, so projections/autosave see the new identity. The modal confirmation rechecks identity and saved state before deletion. No schema change (49), question deletion, saved-find deletion or automatic task transition.

## Targeted checks 336–337

Use the existing separate `/tmp/ict-study-question-inbox-v0` fixture.

336. Open an unfinished Study Find, enter a recognizable note, optionally keep a selected question, and click **Discard current draft…**. Choose Cancel first; the note must remain. Repeat and confirm Discard. Content/attachment list should clear, while date/instrument/session stay. The kept question must still be available in Study questions with its original source snapshot. Do not discard real notes you still need.

337. Close normally and reopen the same fixture. The discarded text must not return. Confirm an earlier saved find is still in Review. On a saved find still displayed in the capture form, Discard must report that it is saved and leave it intact; Start New Study Find remains the appropriate action there.

No repeat of 334–335. This is a draft lifecycle correction; final button placement and broader discard/undo semantics remain open.

## Verification

22 distinct focused tests PASS across draft discard, capture-context, question inbox, MainWindow and smoke documentation. Discard tests were repeated after suppressing intermediate projection signals. Coverage checks cancel, failed deletion with retained autosave, removal of the old identity despite pending edits, retained source assets/associations/questions, and protection of saved finds. Diff check passes. Operator 336–337 pending.
