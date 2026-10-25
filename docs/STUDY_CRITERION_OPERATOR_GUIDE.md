# Integrated criterion Study — checks 321–324

## Where this fits

The cockpit's eventual rulebook should support a complete learning loop: ask a question, define a criterion, examine observations, retain the explanation, then refine the plan deliberately. This trial connects the criterion tools you already accepted to that observation/result step. It does not adopt a trading rule or demonstrate profitability.

## What you are judging

Can you tell why a criterion matched, failed to match, or remained unknown? Can you distinguish an unsaved preview from a retained result, and recover the original evidence after reopening?

The demo supplies one clearly **synthetic** question and candidate. You do not need to recreate the earlier criteria examples or gather real market data. It opens a separate database and creates no Trading Run.

```bash
python tools/study_criterion_demo.py --data-dir /tmp/ict-study-criterion-v0
```

On the first launch, AMDX Lab is selected, with the Sessions quartet for **2026-10-08 at 09:15 New York**, and a synthetic Study question. Click **Evaluate a criterion…** below the investigation controls. In the criterion dropdown choose the one beginning **Candidate · SYNTHETIC: London close-inside…**.

## 321 — A question with no observations remains Unknown

Leave Observed value blank. Click **Explain result**.

Expect **UNSAVED PREVIEW**, **Result: Unknown**, and an explanation that information is insufficient at the reference. This is not a False observation and no saved result should appear yet.

## 322 — Supply one observation, explain it, then save

Enter:

- **Observed value:** `True`
- **Source / reference:** `Synthetic trial observation; not market data`
- **Became available (New York):** leave the visible **2026-10-08 09:15 EDT** value for this synthetic trial. In real study this is an explicit assertion you must supply accurately, not an inferred timestamp.

Click **Explain result**. Expect **Result: Matched** and a proposed assigned role **Q1 = A**. The explanation should show the Q2 London condition, the supplied True observation, source, and availability time. Calendar AMDX remains unchanged.

Click **Save this Study result**. Expect **SAVED STUDY RESULT** and an entry in the saved-results dropdown. Saving records the study basis; it does not adopt the candidate or certify trading validity.

## 323 — Different observations produce explained, separate results

Change Observed value to **False**. The old preview clears and Save disables until you click **Explain result** again. Expect **Not Matched**: this criterion's True condition was not satisfied. Save that result.

Now set Observed value back to **True**. In **Became available**, click the hour portion (`09`) and change it to `10`, keeping the date and minutes unchanged. It should read **2026-10-08 10:15 EDT**. Explain again.

Expect **Unknown** because this observation was unavailable at the pinned **09:15** information reference. Save that result. You should now have three saved results: Matched, Not Matched, and Unknown, each with its own evidence. No success percentage or “best rule” is implied.

## 324 — Recover the original meaning after reopening

Return to investigation, close normally, and rerun the same command with the same directory. Click Evaluate a criterion again. You can inspect the saved results without re-entering observations or selecting a current criterion.

Select the saved **Matched** result. Expect the original question, criterion revision, True value, synthetic source, and **09:15** availability. Select the saved Unknown result: its observation remains True but its availability is **10:15**. The earlier saved record has not been rewritten by later inputs.

Report 321–324 PASS/FAIL/QUESTION, plus whether you can connect the result to the question without hunting through the details. Unsaved observation drafts are not restart-persistent; returning prompts before discarding them. These checks accept the bounded workflow, not final styling or the full multi-day empirical research workspace.
