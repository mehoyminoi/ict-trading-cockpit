# One criterion across selected days — checks 325–327

## Where this fits

You have accepted the one-question/one-result workflow. This step lets you study the same criterion on several explicitly chosen dates without repeatedly reopening the editor. Each day's observations and explanation remain separate. This is a foundation for reviewing a sample, not a success-rate calculation or evidence that a trading plan works.

## What you are judging

Does moving between days preserve the criterion while making it obvious that observations must be supplied for each date? Can you inspect an earlier result without confusing it with your current input date?

Start a new synthetic trial:

```bash
python tools/study_criterion_demo.py --data-dir /tmp/ict-study-multiday-v0
```

The demo opens the same prepared question and synthetic candidate at **2026-10-08 09:15 New York**. Click **Evaluate a criterion…** and select the candidate beginning **SYNTHETIC: London close-inside…**. No new criterion authoring or real price data is required.

## 325 — Keep the criterion, start the next day empty

Enter Observed value **True**, Source **Synthetic October 8 observation**, and leave the visible availability at **2026-10-08 09:15 EDT** for this synthetic example. Explain, then save the Matched result.

Click **Next day** near the top. Expect:

- The heading and reference controls now show **2026-10-09 09:15**.
- The same question and criterion revision remain selected.
- Observed value and Source are both empty. The availability control now belongs to October 9.
- Explain result produces **Unknown** until you supply an observation; it does not borrow October 8's True value.

Changing a date/time field alone only proposes a reference. **Use this reference** applies it. Previous day/Next day apply their new date directly. Unsaved entered observations or a preview prompt before being discarded; Cancel restores the original reference and work.

## 326 — Save a distinct second day and inspect the first

For October 9 enter **False** and Source **Synthetic October 9 observation**, leaving availability **2026-10-09 09:15 EDT**. Explain and save the Not Matched result.

The saved-results summary should show **2 saved results, 2 New York reference dates, 1 criterion revision**. Select the saved October 8 Matched result:

- The explanation retains October 8, True and its October 8 source.
- The current input heading/controls remain October 9, with False and its October 9 source.
- Select the saved October 9 result to see its own retained explanation.

The saved-result banner identifies what you are reading. Inspection does not navigate the input form or overwrite evidence. No match percentage or trading-performance statistic is implied.

## 327 — Reopen the multi-day investigation

Return, close normally, and rerun the same command/directory. Open Evaluate a criterion and inspect both saved results. Each retains its date, question, criterion revision, value, source and availability. The summary still shows two dates.

Reopening starts from the calendar's selected reference; it does not promise restoration of the last unsaved dialog date/input. The underlying AMDX calendar selection and entries were not changed by dialog-only date navigation.

Report 325–327 PASS/FAIL/QUESTION, plus whether the current-input versus saved-result distinction is clear. No need to repeat 321–324.
