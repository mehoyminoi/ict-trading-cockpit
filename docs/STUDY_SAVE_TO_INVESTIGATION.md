# Save Study Find to investigation

This slice addresses the operator's confusion between distant Link and Save controls. The save area now names the destination and offers **Save to investigation** alongside plain **Save Study Find**. The combined action saves content, ordered image references, association and draft removal atomically. A failed write leaves the original draft and form available for retry.

Plain save creates no new association; an existing association remains intact. Existing capture associations take precedence over navigation context. **More… → Link capture only (do not save content)** retains the previous optional workflow. The combined action asks for confirmation when capture date/instrument or a known inspected-session suggestion differs; Cancel is the default. This confirmation does not rewrite entered context. The existing general context notice remains advisory for other actions.

This does not promote findings to competency evidence, complete an investigation or change the Trade Plan. Popup placement for finding capture remains provisional. Schema 50 is unchanged.

## 341 — One coherent save action

Use the existing `/tmp/ict-study-findings-v0` demo fixture after publication.

1. Open Study Find from the AMDX Lab investigation. If an unfinished draft contains material you need, save it before starting a disposable trial. For a saved capture, reopening from the investigation starts a fresh one.
2. Check date/instrument/session. Enter Pattern `Combined save trial` and Observation `Disposable workflow test`.
3. At the save controls, verify the displayed investigation destination. Click **Save to investigation**, without using the optional link-only action first. Expect `Study Find saved to investigation`.
4. Return to the investigation and open its overview. The capture should appear as a saved linked Study Find, not only a linked draft.
5. Open a fresh capture, enter another disposable Pattern/Observation, and use plain **Save Study Find**. It should appear in Review saved finds but not be newly associated with the investigation.

## 342 — Differing context and retained association

1. Open a fresh capture from the investigation, enter disposable Pattern/Observation, then change its Date to the preceding day.
2. Click **Save to investigation**. Expect a dialog showing the difference. Choose Cancel. Input should remain and no saved capture/link should have been created by this attempt.
3. Restore Date to the intended selected day and click **Save to investigation**. It should save without a mismatch dialog.
4. Close and reopen the same demo fixture. The investigation overview should retain the saved linked capture and its original association.

Report PASS/FAIL/QUESTION for 341–342. This tests capture organization and preservation, not the correctness of a market interpretation.

## Validation

67 targeted tests passed across atomic save, injected failures at each write stage, existing association protection, mismatch cancellation, modal-change recheck, pending autosave preservation, standalone save, source repositories, contextual Watch capture, findings, integrated Study, discard/context and MainWindow. `git diff --check` passed. Operator checks remain pending. Publication and merge are not claimed.
