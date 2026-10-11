# E7 operator checks — practical guide

Use this guide for the same checks **236–244** in `SMOKE_TEST.md`. Keep your existing results; resume at your current check. This guide changes the instructions, not the acceptance criteria.

## What the demo is testing

The fictional Friday model requires a Monday with no high-impact event. A known Monday event blocks that model. Uncertain calendar data stays uncertain. Other setups keep their own permissions. A saved run must retain its original facts and rules when reopened. This is synthetic test policy; Alpha 0.7 is unchanged.

You only need to compare the named controls and visible results below. If the starting state or result is unclear, record **QUESTION** and stop that check. Record **FAIL** for a mismatch with a known starting state, **NOT TESTED** for a skipped check, and **PASS** only after observing its expected results.

## Setup once

Start from the repository root with an explicit sandbox path:

```bash
python tools/context_predicate_demo.py --data-dir /tmp/ict-e7-acceptance
```

The **Database** line identifies the open file. **Copy restart command** gives the command to reopen it. Running the script without `--data-dir` creates a different sandbox each time.

To reach Watch, click **Finish TDA / Enter Live Watch**. If the synthetic stations are incomplete, choose **File Incomplete Anyway**. To reach Review, click **Finish Live Watch / Enter Review**. Stop there for these checks; save before completing or concluding the run.

For candidate effects, read **Fixture Friday model** in Watch's **Setups in Play** and its candidate section under **Show context details**. The general rule summary can show Not Applicable for a rule scoped to a candidate.

## Short check cards

| Check | Set the demo to | Observe |
| --- | --- | --- |
| **236 — only the Friday setup is blocked** | **Replay**, **Monday event present**; enter Watch. | Friday model **BLOCKED** with **Not Matched / Block New Entry**. Other model and Custom fixture **AUTHORIZED**. Custom has an IF/THEN row. Clear gates do not remove Friday's context block. |
| **237 — a clear calendar does not bypass a manual gate** | **Complete Monday empty**; enter Watch. | Friday initially **AUTHORIZED**, context **Matched / Informational**. Set **Trading day permitted** to **Pending**: Friday becomes **BLOCKED**. Return it to **Clear**. |
| **238 — uncertain means uncertain** | Try **Incomplete coverage**, **Unknown timing**, **Not Configured**, then **Unknown blocks**. Each change creates a new fixture. | First three show Friday's **Unknown / Warning**; last shows **Unknown / Block New Entry** and blocks Friday only. Other/Custom keep their own authorization. |
| **239 — the calendar week matters** | **Following Monday unverified**; **Show context details**. | Friday's selected Monday is **October 12**, with **Unknown**. The source only guarantees **October 5**. |
| **240 — the rule has limited scope** | First **Other playbook only** in Replay. Then reset to **Monday event present** and try **Live**, **Forward Test**, **Historical Backtest** separately. | First: no Friday candidate and no scoped block. Each excluded environment: Friday exists but the rule is **Not Applicable**, with no context block. Return to **Replay**. |
| **241 — the explanation follows the run** | **Replay**, **Monday event present**; inspect TDA, Watch, then Review. | Friday's details keep the same fixture revision, October 5 window, event ID and **Not Matched / Block New Entry** result. |
| **242 — save and restart** | Follow the sequence below. | Same saved run ID, Review screen and blocking result after both restores. |
| **243 — existing operation still works** | **Legacy rules**; then your normal application and an earlier E6 run/capture. | Legacy fixture has no context effects. Normal capture selection, manual gates and TDA/Watch/Review still work. Record separately if you cannot inspect an earlier E6 run. |
| **244 — local automated tests** | Repository root: `python -m pytest`. | Record the exact reported result and Python version. Normal application remains schema v37 / Alpha 0.7. |

## Check 242, one step at a time

1. Select **Replay** and **Monday event present**. Enter Watch, then Review.
2. Click **Save fixture**. The message must say **Saved fixture run …**. Note that run ID.
3. Click **Copy restart command** and keep the copied command before closing.
4. Select **Legacy rules**, then click **Restore saved fixture**. Check the saved ID, Review screen and Friday's original **Not Matched / Block New Entry** details.
5. Close the demo. From the repository root, execute the command copied in step 3.
6. Compare the **Database** path with the original. Click **Restore saved fixture**. Check the same three results again.

If Restore is gray, this open database has no saved fixture. Stop and report the launch command and database path. That alone does not establish a broken restore. Do not repeat earlier tests or mark restart PASS until the saved database is identified.

Automated tests verify the detailed calendar, scope, compatibility and stored-state combinations. These operator checks verify that the actual workflow and explanations are usable. A confusing instruction or unidentifiable database is useful feedback to fix, not a reason to guess a result.
