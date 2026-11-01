# Direct Study question capture

Operator 331–333 PASS is published at `6454e04`. Feedback: a question already written in Notes does not need a mandatory refinement screen. This slice implements select wording → Keep question for later → continue. No schema change (49).

The most recently selected Notes or Observation editor supplies the wording. Exact selection is retained as original_text; the question trims outer whitespace only. Existing source-snapshot and explicit-association semantics remain unchanged. Success appears in quiet adjacent text, with no dialog or navigation. Save errors retain the selection and report failure for deliberate retry. Repeated identical clicks within the current window reuse the same question identity while source/question remain unchanged; this is not a global duplicate-detection system.

With no nonblank selection, the existing composer remains available. Existing saved questions stay immutable; this does not add editing/refinement of saved records. Source text, current investigation and calendar are unchanged. Selection of another editor takes precedence over an older selection still highlighted elsewhere.

## Targeted operator checks 334–335

Use the existing separate `/tmp/ict-study-question-inbox-v0` fixture (schema 49); no fresh research assignment.

334. In Study Find, write and select a short question in Notes. Click **Keep question for later**. Confirm immediate **Question kept** feedback, no popout and unchanged form. Click again once: Study questions should show one new saved item, with the original wording and source snapshot. Return to continue.

335. Select different wording in Observation after selecting Notes; keep it and verify the newest selection was used. Clear the selection, click Keep question for later, and confirm the optional blank composer opens. Return without saving. Previous questions remain available after reopening.

Do not repeat 331–333. Their original guide describes the now-superseded mandatory composer for selected text. This is a small interaction correction, not acceptance of final inbox layout or new ranking/editing/assessment functionality.

## Verification

19 focused tests PASS across question inbox/direct capture, MainWindow, capture-context continuity and smoke documentation. New cases verify no-dialog save, last selected editor, failure/retry with intact selection, immediate duplicate-click prevention and blank-composer fallback. Diff check passes. Operator 334–335 pending.
