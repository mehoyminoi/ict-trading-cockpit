# AMDX Lab catalog — four-check hands-on trial

This is the first functional historical-entry workspace: all seven identified layers remain visible beside the selected quarter's editor. The same native widget is available in the normal application's **AMDX Lab** tab. The trial wraps it in a 16:9 window with a separate synthetic database and two exact reference presets. It does not start a trading run or change trading authorization.

## Fetch the branch and open the retained trial

From your normal project directory:

```bash
cd /home/jesse/projects/ict-trading-cockpit
git fetch origin
git switch feature/amdx-catalog-lab-v1
git pull --ff-only origin feature/amdx-catalog-lab-v1
source .venv/bin/activate
python tools/amdx_catalog_lab_demo.py --data-dir /tmp/ict-amdx-catalog-lab-v1
```

Fetch comes before switching, so Git can discover the new branch. If Git reports local smoke-test edits would be overwritten, preserve those edits with the existing commit-first workflow before retrying the switch/pull; do not replace that file. The trial retains its own `demo.db`, manifest and navigation preferences under the exact directory above. Use this same command to reopen it at any time. No Conclude, Save or fresh-directory step is needed after closing it normally.

The first launch creates an empty **MNQ historical trial** catalog and starts at **1998-05-12, 09:15 New York**, Observed. Nothing has been entered yet. If you have already used this trial, the last inspected place and recorded profiles return; repeating an unchanged choice is valid. It records capture provenance without duplicating the interpretation.

## What the screen means

- The table shows 16-year, quadrennial, yearly, monthly, weekly, the daily sessions, and the inspected session's 90-minute quartet.
- **•** marks the quarter at the selected historical reference. The highlighted cell is the quarter being inspected/edited; these can differ when deliberately reviewing another quarter.
- **Entered** is your explicit choice. **Implied** follows from the coupled AMDX/XAMD order. **Unresolved** is not a phase entry.
- The right-hand **Selected quarter** heading tells you exactly which layer/quarter/channel the buttons will change. Only structurally legal phases are enabled. X(C)/X(R) are direct buttons where X is legal.
- Selecting a date/time, session, level or quarter records no AMDX judgment. A phase click records immediately. Earlier revisions stay saved without a history list on this workspace.
- Entry provenance is optional detail; its drafts recover automatically. Actual entry time and historical market time stay separate. Historical/forward labels are declared capture basis, not a grading system or proof of no look-ahead.

## 261 — Enter the initial 90-minute quartet

Use the top menu **Study references → Initial 1998 example · NYAM 90m Q3**. This selects the bottom **90-minute** row, Q3, at the exact first reference.

The right heading should say **MNQ · 90-minute · Q3**, **90m 3 · Observed**. Click **M** once.

**Expected:** that bottom row's Profile is **XAMD**, and Q3 shows **M · entered**. The status says **Recorded**, or unchanged meaning if repeated. No trading run, station completion or separate Save is needed. This is check **261**.

## 262 — One-click X reversal

In that same bottom **90-minute** row, click its **Q1** cell. Confirm the right heading now says **90-minute · Q1**. Click **X(R)** once, directly from the editor.

**Expected:** Q1 shows **X(R) · entered**, the profile remains **XAMD**, and Q3 remains **M · entered**. This is check **262**. Do not use the daily Sessions row's Q1 for this point.

## 263 — Enter an older higher layer

Use **Study references → Older 1985 example · Yearly Q3**. The date/time moves to **1985-08-12, 09:15 New York**, and the highlighted cell is in the **Yearly** row, Q3.

Confirm the right heading says **MNQ · Yearly · Q3**, **Jul–Sep · Observed**. Click **D** once.

**Expected:** the **Yearly** Profile is **AMDX**, and Q3 shows **D · entered**. This is a separate 1985 occurrence; it does not overwrite the 1998 90-minute data. This is check **263**.

## 264 — Restart and return to the earlier entry

While the 1985 Yearly Q3 is still selected, close the window with **X**. Reopen with exactly:

```bash
python tools/amdx_catalog_lab_demo.py --data-dir /tmp/ict-amdx-catalog-lab-v1
```

**Expected:** the same catalog, **1985-08-12** reference, **Yearly Q3**, **D · entered**, and **AMDX** profile return without entering D again.

Then use **Study references → Initial 1998 example · NYAM 90m Q3**. The bottom row should still show **XAMD**, with **Q1 X(R) entered** and **Q3 M entered**. Choosing this preset records nothing. This is check **264**.

You can report simply:

```text
261 PASS
262 PASS
263 PASS
264 PASS
```

If a point is unclear or different, stop there and report its number, the **Selected quarter** heading and what the relevant Profile/cell shows. Earlier successful points remain useful; no need to reset the whole trial or guess the intended result.

## Scope and next work

This trial checks entry, independent historical occurrences, direct subtype input and restoration. Exact control/layout refinement remains open to hands-on feedback. Current global application geometry, bulk import, automatic linkage of trading-run captures, higher run Review selection, historical as-of reconstruction and statistics are separate work. This slice adds no Watch history/comparison route, automatic classifier, startup policy or Trade Plan rule adoption. Schema remains v42 / Alpha 0.7 on this unmerged stack. Operator checks 261–264 are PASS from the explicit 2026-10-13 report; all previous 260 records retain their results. This accepts the focused functional behaviors, not the final renderer.


## Developer checkpoint

Source `678e9a0835a442f1de42ec6761bfcd7116fc6bad`, draft PR #70. Final focused **97 PASS in 23.81s**, including **32 new native/trial cases**; complete **936 PASS across 77 isolated module processes in 581.68s**, collection-matched counts, clean exits and no failures/errors/skips or pytest warnings. All regression work finished. Mouse/keyboard gestures, all levels, scope/metadata changes, stale/write/read recovery, exact reference/capture restore and retained presets/reopen are covered. Native standalone layout inspected at 1344×756 and 1280×720. Python 3.10 grammar passes; execution is Python 3.12. Developer verification is separate from the four pending operator results; keep draft until that review. Schema v42 / Alpha 0.7 unchanged, main untouched and no merge.


## Operator result — 2026-10-13

Checks **261–264 PASS**, explicitly reported by the operator. The operator saved the results locally but had not committed/pushed them at the time of reporting. This repository checkpoint records that report; it does not import or claim inspection of the local file or unseen notes. PR #70 is ready for review and remains unmerged. The developer evidence above is unchanged; no new full run is claimed. Final renderer/topology and broader integrations remain separate.
