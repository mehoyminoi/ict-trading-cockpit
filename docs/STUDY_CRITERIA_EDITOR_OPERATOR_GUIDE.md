# Study criteria browser/editor — checks 313–317

Use a fresh synthetic trial directory. This is the native Python cockpit, not an HTML prototype. No real trading rule, run or evaluation is required.

```bash
python tools/integrated_study_task_demo.py --data-dir /tmp/ict-study-criteria-editor-v0
```

The demo opens AMDX Lab. Set the calendar date to **2026-10-08**, find the **day/session quartet** row containing Asia, London, NYAM and NYPM, and click its Asia cell. Click **Study criteria…** beside the investigation controls. If instructed to select a quarter, click the Asia cell and try again. The dialog heading should identify the day layer and Asia → NYPM. Its reference stays pinned until you return and reopen it.

## 313 — Inspect without changing the calendar

Initially the definition selector has no retained criterion. Read the context and explanation, then choose **Return to investigation**. The selected calendar quarter and its AMDX values should be unchanged. Reopen **Study criteria…**.

## 314 — Save a synthetic candidate with distinct input/output

Click **New candidate**, then enter:

| Field | Value |
| --- | --- |
| Criterion / rationale | Synthetic trial: London close-inside supports Asia A |
| Output meaning | Assigned Role |
| Output quarter | Q1 · Asia |
| Proposed role / behavior | A |
| Priority | 0 |
| Input quarter (first condition row) | Q2 · London |
| Feature name | synthetic-close-inside |
| Comparison | equals |
| Value type | Boolean |
| Value | True |
| Unit | Leave empty |

Click **Save candidate revision**. Expect a saved-candidate message, a selected Candidate record, and read-only detail showing **output Q1** with **input Q2**. This defines a hypothetical criterion; it does not record that London actually closed inside anything, classify price or change calendar AMDX.

## 315 — Retain both revisions

Click **Create candidate revision**. Change **Priority** to **2** and save. The selector should now contain two Candidate revisions with the same rationale. Select each: the detail should show priority 0 for one and 2 for the other. Neither has disappeared. No candidate has become Published.

## 316 — Constraints, validation and draft return

Select either saved revision and click **Create candidate revision**. With output meaning **Assigned Role**, select **Q3**: the role choices should be M and D. Select **Q4**: D, X, X(C), X(R) should be available. Change output meaning to **Local Behavior**: all A/M/D/X behavior choices become available because local description is distinct from an assigned quartet role.

Change the Boolean condition value from True to **perhaps** and click Save. Expect **Not saved**, with your draft still present. Click **Return to investigation** and choose **Cancel** in the unsaved-draft prompt: the editor should remain open. Then click **Discard draft**, followed by **Return to investigation**. Calendar values remain unchanged; only the two previously saved candidates exist.

## 317 — Reopen retained candidates

Close the cockpit normally and rerun the exact command above using the same directory. Select the same day/session row for 2026-10-08, open **Study criteria…**, and inspect both saved revisions. Both priorities remain readable. No Trading Run was needed. Unsaved drafts are not promised to survive application exit; the editor prompts before discarding them.

Report 313–317 PASS/FAIL/QUESTION. This accepts the bounded browser/editor behavior, not final styling, reusable recurring scope definitions, automatic classification or the full empirical evaluation workflow.
