# Reusable input scopes — checks 318–320

Start a new synthetic directory:

```bash
python tools/integrated_study_task_demo.py --data-dir /tmp/ict-amdx-reusable-scopes-v0
```

Set the AMDX Lab calendar date to **2026-10-08**, select Asia in the **Sessions** row, and open **Study criteria…**. This is the day-layer quartet, Asia → NYPM.

## 318 — Fixed versus reusable is an explicit revision

Create a synthetic candidate using the same entries as check 314 in `STUDY_CRITERIA_EDITOR_OPERATOR_GUIDE.md`: rationale “Synthetic trial: London close-inside supports Asia A,” Assigned Role, output Q1 Asia=A, priority 0; condition feature `synthetic-close-inside`, equals, Boolean, True, empty unit. For input scope choose **Fixed Q2 · London** and save.

Inspect the saved detail: the input begins **Fixed**. Click **Create candidate revision**, change only input scope to **Reusable Q2 · selected quartet**, and save. There are now two retained revisions: one Fixed and one Reusable. The reusable detail shows Q2, London and a start time on 2026-10-08. This is a definition preview, not a price-action judgment.

## 319 — Inspect the next date without rewriting the criterion

Return to the investigation, change the date to **2026-10-09**, select Asia in the Sessions row, and reopen Study criteria. Select each saved revision:

- Fixed: its input is labeled **Outside pinned quartet**, retaining the original quarter identity.
- Reusable: its preview shows selected quartet Q2, London and **2026-10-09**.

No save is needed. Both candidate revisions remain present; no new revision or AMDX phase is created merely by inspecting a different date. The input follows Q2 of the selected day; it does not substitute Q2 of another layer or silently adopt a rule.

## 320 — Reopen and retain the reusable choice

Close normally and reopen using the same command/directory. Select the Sessions quartet on 2026-10-09 and reopen Study criteria. Inspect the reusable revision, then click **Create candidate revision**: the input selector should still read **Reusable Q2 · selected quartet**. Click **Discard draft**, then Return. The two saved revisions remain, without needing a Trading Run or evaluation.

Report 318–320 PASS/FAIL/QUESTION. This trial does not ask you to approve actual trading criteria, run an empirical comparison or repeat 313–317.
