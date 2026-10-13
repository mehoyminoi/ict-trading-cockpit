# Shared Observed Review — five checkpoints

This trial checks that Review and Lab maintain one Observed judgment while earlier run assessments remain immutable. It uses a separate synthetic MNQ database with Review dated **2026-10-09**, NYAM **09:15 New York**. The fixture deliberately overrides incomplete TDA; its starting Expected Yearly AMDX is synthetic, not a market assessment.

Operator acceptance, 2026-10-13 (America/Denver): checks 270–274 passed. The operator saved the smoke test locally but had not committed or pushed it; this records the report without importing uninspected notes. The instructions below are retained for repeat trials.

## Get the trial

Close older demo windows. From your repository, preserve any local smoke-test notes before switching branches:

```bash
cd /home/jesse/projects/ict-trading-cockpit
git status --short
git fetch origin
git switch feature/amdx-review-calendar-v0
git pull --ff-only origin feature/amdx-review-calendar-v0
source .venv/bin/activate
python tools/amdx_review_calendar_demo.py --data-dir /tmp/ict-amdx-review-calendar-v0
```

If your notes are uncommitted, commit them on their current branch or use `git stash push -m 'local smoke notes' -- docs/SMOKE_TEST.md`, leaving the stash saved during this trial. Do not overwrite them.

Use the same directory to reopen. To repeat from the beginning, choose a different empty directory such as `/tmp/ict-amdx-review-calendar-v0-second`. Do not conclude the run during these checks; closing with the window X retains it. The regular application database is not opened. This branch uses schema v45; the migration is forward-only, and an older application requires an unmigrated database copy.

### 270 — Review entry appears in the same maintained Lab calendar

1. Confirm the top panel says **Maintained Observed AMDX · 2026-10-09**, with **NYAM** in its session selector. If necessary select NYAM explicitly.
2. Click the **90m row Q3 cell** (09:00), then **M**.
3. Confirm **XAMD** in the 90m Profile and **M entered** at Q3.
4. Open **Review trial → Lab · same NYAM 90-minute Observed quartet**.

Expected: the Lab interpretation is **Observed**, date **2026-10-09**, bottom 90-minute Profile **XAMD / Q3 M entered**. No second entry, collection destination or Save action is needed. Return with **Review trial → Return to Review**.

### 271 — Direct X(R) also becomes part of the shared assessment

1. In Review's **90m row**, click **Q1** (06:00).
2. Click **X(R)** directly.

Expected: **Q1 X(R) entered**, **Q3 M entered**, Profile **XAMD**. The **Captured run assessment** button is available below the panel. No second subtype click or Expected comparison selection is required.

### 272 — A later Lab correction changes current Review orientation

1. Open **Review trial → Lab · same NYAM 90-minute Observed quartet** again.
2. Confirm the right heading says **90-minute · Q3 / 90m 3 · Observed**. Click **D**.
3. Confirm the Lab Profile changes to **AMDX / Q3 D entered**.
4. Choose **Review trial → Return to Review**.

Expected: Review now shows the same current **AMDX / Q3 D entered**. The **Captured run assessment** button remains available. This correction does not rewrite the assessment recorded in checkpoint 271.

### 273 — The captured run assessment preserves the earlier judgment

1. Click **Captured run assessment** below Review's top panel.
2. Inspect the dialog's bottom **90-minute** row.

Expected: the captured Observed stack still shows **XAMD**, **Q1 X(R) entered**, **Q3 M entered**, despite current Review/Lab now showing AMDX. Phase/reference controls are disabled; inspection records no new judgment. Close the dialog. **Full AMDX stack** remains the separate original Expected launch inspection, not an automatically selected comparison baseline.

### 274 — Clock advancement and restart retain the correct day and both meanings

1. Open **Review trial → Advance display to next Trading Day**.
2. Confirm the upper trading-time display advances but **Maintained Observed AMDX remains 2026-10-09**.
3. Close with the window X and reopen with the same command/directory.
4. Confirm Review is still dated October 9, NYAM is selected, and current 90m Profile is **AMDX / Q3 D entered**.
5. Open **Captured run assessment** again.

Expected: the retained assessment remains **XAMD / Q1 X(R) and Q3 M entered**, without entering again. Close the dialog normally. No new phase entry is caused by clock movement or restart.

Report **270–274 PASS / FAIL / QUESTION / NOT TESTED**, with the checkpoint and exact visible result for anything unclear. These are functional checks; final spacious rendering and higher-period Review editing remain later milestones.
