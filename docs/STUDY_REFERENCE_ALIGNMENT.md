# Align an unfinished Study capture with its calendar reference

## Purpose

Repeated date mistakes showed that retaining context and warning about differences are insufficient. This slice exposes the retained capture reference and selected calendar reference together near capture entry, with explicit navigation to the existing calendar controls and an alignment action. It does not read TradingView, infer the chart date, or guarantee the selected date is correct.

Select reference in calendar returns to the existing calendar and focuses its date input. Set Historical Reference and inspect the relevant quarter/session there, then Open Study Find to return. Authored content remains pinned to its retained destination until explicitly aligned.

Use selected calendar context updates an unfinished, unlinked capture's New York calendar date, instrument, suggested session (when available), historical reference and interpretation. It retains the same investigation identity/question, capture ID, observation, notes, pattern, available move and images. The draft and opening destination commit together. It does not submit a Study Find or create an association. If the selected layer offers no session suggestion, the current entered session is retained.

Saved or already-linked captures cannot be reassigned with this action. The current investigation must match the retained opening destination; return to its investigation or resolve the capture through existing controls. Corrections to already-saved historical records remain a separate requirement. A failed update leaves both persisted draft and destination unchanged. Restart restores the aligned date/destination. Schema 52 unchanged.

## Operator 354 — explicit alignment, preserved observations

Use the existing durable workspace on the new branch. Save meaningful current work first; use a disposable capture for this check.

1. Open Study Find from a named investigation with a known calendar date/session. Enter a disposable observation and note (optionally paste an image).
2. Select reference in calendar, move Historical Reference to another day and inspect the intended session. Open Study Find again. Expect your written content and original capture date to remain, with retained and selected references visible together.
3. Compare the selected reference with your chart, then click Use selected calendar context. The capture date/instrument/suggested session and retained reference should align. Your wording/image and capture identity remain. No capture has been submitted or linked by this action.
4. Close and reopen the durable workspace normally. The unfinished capture's aligned date/destination should persist. Save or discard this disposable capture through the existing controls.

Optional protection check: for a capture already associated by Link capture only, the alignment action is disabled. No need to modify real saved material to test this.

This reduces repeated entry and makes discrepancies visible; it cannot detect the case where both Cockpit references agree but the external chart shows another date. No extra confirmation is required for the explicit alignment button. Review-time question capture remains the next separate increment.

Operator 352–353 PASS from the preceding slice. Operator 354 pending. Publish only when authorized, draft stacked on #103; do not merge.

Validation: 25 targeted tests PASS across reference alignment, capture context, fresh-next-capture behavior, atomic save-to-investigation and investigation resumption. Tests verify content/image identity preservation, persisted date/destination after restart, rollback of both writes under injected database failure, and refusal to retarget a linked capture. An initial rollback test fixture changed image paths without emitting the normal draft-change signal; the fixture was corrected and the entire targeted batch passed. Diff check passed.
