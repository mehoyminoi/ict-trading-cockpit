# Higher Observed Review — six checkpoints

This trial checks higher-stack Review within one run's reviewed futures day. It uses a **separate synthetic MNQ Replay database** with an original reference of **2027-01-01 09:15:37 New York**. The future date is solely a calendar-boundary fixture; no market observations or predictions are seeded. All Expected and Observed profiles begin unresolved. Incomplete TDA is deliberately overridden in this fixture.

Published code checkpoint: `310c4747d208ebb6a5852ca30008d0fd4d790390`. The branch also includes its guide/checkpoint documentation.

## Get the trial

Close older demo windows. Preserve local smoke notes on their current branch before switching. Leave earlier saved stashes intact; do not apply them over this branch during the trial.

```bash
cd /home/jesse/projects/ict-trading-cockpit
git status --short
```

If `docs/SMOKE_TEST.md` has uncommitted changes, preserve them:

```bash
git stash push -m 'local smoke notes before higher Review' -- docs/SMOKE_TEST.md
```

Then:

```bash
git fetch origin
git switch feature/amdx-higher-review-v1
git pull --ff-only origin feature/amdx-higher-review-v1
git log -1 --oneline
source .venv/bin/activate
python tools/amdx_higher_review_demo.py --data-dir /tmp/ict-amdx-higher-review-v1
```

Use this same command/directory to reopen. To repeat from the beginning use a different **empty directory**, for example `/tmp/ict-amdx-higher-review-v1-second`. Do not conclude the run. The window X retains it. This branch uses **schema v46 / Alpha 0.7**; older applications reject migrated databases. The trial does not open your regular database.

There are two types of windows: the **main cockpit**, and the **higher editor** opened by **Review full AMDX stack**. Use the editor's **Close** button to return to the cockpit; use the main cockpit's window X only for checkpoint 280.

### 275 — Default context and immediate new-year entry

1. In Review's top AMDX panel, click **Review full AMDX stack**.
2. Confirm the heading is **AMDX Review · MNQ maintained Observed**.
3. Confirm the context selector at upper right says **Original launch · 2027-01-01T09:15:37-05:00**.
4. The reference text should show reviewed Trading Day **2027-01-01**, bounds **2026-12-31 18:00 → 2027-01-01 18:00**, and the original and selected reference separately.
5. Click **Yearly row Q1**. Confirm the right heading says **Yearly · Q1 / Jan–Mar · Observed**. Click **X(C)** once.

Expected: Yearly occurrence **2027**, Profile **XAMD**, **Q1 X(C) entered**. The choice records immediately; no Save or comparison selection is needed.

### 276 — The preceding evening is another context, without inherited phases

1. In the upper-right context selector choose **Reviewed day start · 2026-12-31T18:00:00-05:00**.
2. Inspect the **Yearly**, **Quadrennial** and **16-year** rows.

Expected: Yearly occurrence **2026**, Yearly temporal marker at **Q4**, Profile **Unresolved**. Quadrennial and 16-year occurrences start at **2023** and **2011** respectively and remain Unresolved. The original reference stays January 1 while selected context is December 31. Choosing context records no phase and does not copy the new-year X(C). The reviewed Trading Day remains January 1.

### 277 — One-click old-year entry preserves both profiles

1. In this preceding-evening context click **Yearly row Q4**.
2. Confirm **Yearly · Q4 / Oct–Dec · Observed**, then click **X(R)** once.
3. Confirm old-year Profile **AMDX / Q4 X(R) entered**.
4. Switch the selector to **Original launch**: confirm **2027 XAMD / Q1 X(C) entered**.
5. Switch back to **Reviewed day start**: confirm **2026 AMDX / Q4 X(R) entered**.

Expected: both independent profiles remain; switching contexts adds no entries. Close the editor and confirm Review's intraday **NYAM** selection remains unchanged. Its sessions/90-minute input remains independent.

### 278 — Inactive factual positions do not invent an input quarter

1. Reopen **Review full AMDX stack**. If needed choose **Reviewed day start**.
2. Click the **Monthly row's left Level / occurrence cell**, rather than Q1–Q4.
3. Confirm Monthly **Unassigned** and no active quarter is selected; phase buttons are disabled.
4. Click the **Weekly row's left Level / occurrence cell**.
5. Confirm Weekly **Distortion** and no active quarter is selected; phase buttons are disabled.
6. Click **Yearly Q4** again before closing the editor.

Expected: these are temporal position states, not AMDX phase judgments. Explicit Q1–Q4 inspection is available; no Q5 or automatic Not Applicable entry is created. The Yearly profile remains AMDX.

### 279 — A failed assessment cannot leave a partial calendar change

1. Close the higher editor. In the main cockpit menu choose **Higher Review trial → Simulate assessment write failure**; confirm it is checked.
2. Reopen **Review full AMDX stack**, choose **Reviewed day start** if necessary, then click **Yearly Q4**.
3. Attempt **X(C)** once.
4. Confirm the bottom status says **Entry not recorded** with the synthetic failure and **Use Reload**. The visible Yearly profile remains **AMDX / Q4 X(R) entered**, and phase buttons are disabled. Do not try to force another entry.
5. Close the editor. Uncheck **Higher Review trial → Simulate assessment write failure** in the main cockpit.
6. Reopen the editor and click **Reload**. Inspect **Yearly Q4** without entering again.

Expected: **X(R) entered / AMDX** remains. Neither the calendar nor the run assessment accepted the failed X(C); reopening/Reload does not replay it. Close the editor.

### 280 — Restart and the retained assessment keep their original scope

1. Close the main cockpit with its window X. Reopen using the same terminal command/directory.
2. Click **Review full AMDX stack**.
3. Confirm **Reviewed day start / December 31** restores with **Yearly Q4 X(R) entered / AMDX**.
4. Switch to **Original launch** and confirm **2027 Yearly Q1 X(C) entered / XAMD**. No re-entry is needed.
5. Close the editor. Click **Captured run assessment** in the main Review panel.
6. Confirm the read-only dialog shows reviewed Trading Day **2027-01-01**, original reference **January 1 09:15:37**, selected reference **December 31 18:00**, and old-year **AMDX / Q4 X(R) entered**. Phase/reference controls are disabled.

Expected: the assessment retains the scope of the last successful entry from checkpoint 277. Later navigation and the failed attempt did not replace it. **Captured launch stack** remains the separate original Expected stack, with its originally unresolved profiles intact.

Report **275–280 PASS / FAIL / QUESTION / NOT TESTED**, with the checkpoint and exact visible outcome for anything unclear. Automated tests do not mark these operator checks PASS. Final cockpit/Lab rendering is a later milestone.
