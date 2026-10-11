# E7 operator checks — practical guide

Use this guide on `feature/context-maturity-e7-v0` for the same checks **236–244** in `SMOKE_TEST.md`. Keep your existing results; resume at your current check. This guide changes the instructions, not the acceptance criteria.

## What the demo is testing

The fictional Friday model requires a Monday with no high-impact event. A known Monday event blocks that model. Uncertain calendar data stays uncertain. Other setups keep their own permissions. A saved run must retain its original facts and rules when reopened. This is synthetic test policy; Alpha 0.7 is unchanged.

You only need to compare the named controls and visible results below. If the starting state or result is unclear, record **QUESTION** and stop that check. Record **FAIL** for a mismatch with a known starting state, **NOT TESTED** for a skipped check, and **PASS** only after observing its expected results.

## Setup once

Start from the repository root with an explicit sandbox path:

```bash
python tools/context_predicate_demo.py --data-dir /tmp/ict-e7-acceptance
```

The **Database** line identifies the open file. **Copy restart command** gives the command to reopen it. Running the script without `--data-dir` creates a different sandbox each time.

Every launch starts at **Monday event present** with a new unsaved fixture, even when reopening the same database. **Restore saved fixture** explicitly loads saved state. Changing the scenario alone does not save it. If the Copy button causes difficulty, keep the printed **Restart:** command from the terminal and type that same command with its `--data-dir` path.

To reach Watch, click **Finish TDA / Enter Live Watch**. If the synthetic stations are incomplete, choose **File Incomplete Anyway**. To reach Review, click **Finish Live Watch / Enter Review**. Stop there for these checks; save before completing or concluding the run.

For candidate effects, read **Fixture Friday model** in Watch's **Setups in Play** and its candidate section under **Show context details**. The general rule summary can show Not Applicable for a rule scoped to a candidate.

For **238/239**, you can stay in TDA with **Replay** selected. Click **Show context details** and scroll **inside the text box** toward the bottom to **Candidate context: Fixture Friday model**. Its next line gives the outcome/effect. For 239, **Source coverage bounds** should say October 5, while the candidate's **Event window (America/New_York)** says October 12 and the outcome stays **Unknown / Warning**.

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
3. Keep the printed **Restart:** command, or use **Copy restart command**, before closing. It must include the same `--data-dir` path.
4. Select **Legacy rules**, then click **Restore saved fixture**. Check the saved ID, Review screen and Friday's original **Not Matched / Block New Entry** details.
5. Close the demo. From the repository root, execute the command copied in step 3.
6. Compare the **Database** path with the original. Click **Restore saved fixture**. Check the same three results again.

If Restore is gray, this open database has no saved fixture. Stop and report the launch command and database path. That alone does not establish a broken restore. Do not repeat earlier tests or mark restart PASS until the saved database is identified.

## Check 243 uses a separate application/database

Select **Legacy rules** in the E7 demo and look for **No declarative context rules recorded; existing manual Trade Plan gates remain in force.** No restart is needed for that part.

Earlier E6 data must be checked in its original sandbox or the normal application. From the repository root on Linux, launch the normal application with `PYTHONPATH=src python -m ict_cockpit.main`. Go to **Trade Plan → Process → Calendar captures** and open the saved-capture dropdown. Entries beginning **Week …** identify saved captures; **Not Configured** alone means this database has none. Normal startup or inspecting a saved capture alone does not establish restoration of an earlier run. If the earlier data is unavailable, keep 243 **NOT TESTED** and note the observed portion rather than reconstructing missing operator history.

### Controlled check when the original E6 data is unavailable

This substitutes an identifiable old-version fixture for the missing old sandbox. It does not recover your earlier data. The tool creates two synthetic captures and a Replay run using accepted E6 source at `42e3b346245de17e61a062e29fa6cd082d2527bf`, then opens the normal current application on that database. It retains `e6-original.db` and `e6-origin.json` as the original database and provenance record. Your usual application database is separate.

First, inspect **Legacy rules** in the E7 predicate demo as described above. Then close that demo and run:

```bash
python tools/e6_compatibility_demo.py --data-dir /tmp/ict-e6-e7-compatibility
```

First launch requires an empty directory. Later launches reuse the same database and do not recreate the run. If the accepted E6 commit is missing, run `git fetch origin` and retry. If a failed attempt left files, use a different empty directory; the tool refuses to replace existing files.

1. **Restored Watch:** the normal application opens in Watch with **Silver Bullet Model**, Replay and Alpha 0.7. Manual gates are Pending and the candidate is Blocked. The permanent bottom label lists the original run and capture IDs; they are also printed in the terminal.
2. **Stored context:** click **Show context details**. Compare its run/capture IDs with the bottom label. Look for **E6 compatibility release**, native previous **1%**, and unverified completeness/unknown precision and status. The rules detail says **No declarative context rules recorded; existing manual Trade Plan gates remain in force.** An uncertain export must not become a precise upcoming release or automatic calendar block.
3. **Normal TDA/Watch navigation:** click **Return to Analysis**, enter a reason if requested, and verify TDA retains the same stored context. Then **Finish TDA / Enter Live Watch**, choosing **File Incomplete Anyway** if prompted. Manual gates stay explicit; returning to Watch does not grant entry.
4. **Review and restart:** click **Finish Live Watch / Enter Review**. Check the same original IDs and context; close the window. Run the exact command above again. It restores Review automatically with the same run and original capture. There is no Restore fixture button in this normal application. Do not complete the run during this check.
5. **Two saved captures:** go to **Trade Plan → Process → Calendar captures**. The dropdown contains **Not Configured** and two **Week 2026-10-04…** entries. New-run selection starts Not Configured after restart. Inspect the two entries: the capture matching the bottom original ID has native previous **1%**; the other has **revised**. Select the revised capture and click **Use selected capture for new runs**. Return to **Process → Run Trading Day**; its stored context still shows the original capture and **1%**.

If all these observations and the Legacy scenario match, mark 243 **PASS**, noting controlled E6→E7 compatibility and the IDs. A mismatch is **FAIL** with the observed step; an unclear or incomplete check stays **QUESTION / NOT TESTED**. Developer automation separately verifies genuine E6 rule payloads with absent E7 fields retain run-wide scope and no not-matched effect; those unpublished payloads are not installed into Alpha 0.7.

Automated tests verify the detailed calendar, scope, compatibility and stored-state combinations. These operator checks verify that the actual workflow and explanations are usable. A confusing instruction or unidentifiable database is useful feedback to fix, not a reason to guess a result.
