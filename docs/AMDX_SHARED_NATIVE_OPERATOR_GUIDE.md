# Shared AMDX calendar native trial

The normal MNQ Lab, new-run TDA and Watch now use one maintained calendar. This trial checks shared data behavior using the current native controls. Final cockpit rendering, Study-first startup and macropad navigation remain later work.

## Get the trial

Close any older demo window first. From your repository:

```bash
cd /home/jesse/projects/ict-trading-cockpit
git status --short
git fetch origin
git switch feature/amdx-shared-native-v0
git pull --ff-only origin feature/amdx-shared-native-v0
source .venv/bin/activate
python tools/amdx_shared_calendar_demo.py --data-dir /tmp/ict-amdx-shared-native-v0
```

If `git status --short` shows your smoke-test notes, preserve them before switching. Commit only those notes on the current branch, or use `git stash push -m 'local smoke notes' -- docs/SMOKE_TEST.md`; leave the stash saved while running this trial. Do not overwrite your notes.

The trial uses a separate database, synthetic MNQ Replay reference **2026-10-09 09:15 New York**, and a starting **Yearly AMDX** fixture. The initial Yearly Q3=D is synthetic, not a market assessment. The trial deliberately overrides incomplete TDA only when its Watch/Review menu actions are used. Your regular database is not opened.

Use the same directory when reopening; it retains the run and edits. To repeat from the beginning, use a different empty directory, for example `/tmp/ict-amdx-shared-native-v0-second`. Do not conclude the run during this trial. Closing with the window X is safe at any checkpoint.

## Five checkpoints, in order

### 265 — Historical backfill in the maintained Lab

1. Open **Shared trial → 1 · Historical Lab · 1985 Yearly Q3 · Observed**.
2. Confirm the Lab heading says **MNQ maintained calendar**, date **1985-08-12**, interpretation **Observed**, and the right heading says **Yearly · Q3 / Jul–Sep**.
3. Click **D** in the right panel.

Expected: Yearly row Profile **AMDX**, Q3 **D · entered**. No catalog destination or Save action is required. This is an older Observed occurrence, separate from the current 2026 Expected occurrence.

### 266 — Quiet Watch and one-click X(R)

1. Open **Shared trial → 2 · Watch · synthetic incomplete-TDA override**.
2. In the top Working AMDX panel, click the **90m row Q3 cell** (09:00), then **M**.
3. Confirm the 90m Profile **XAMD**, Q3 **M entered**.
4. Click the **same 90m row Q1 cell** (06:00), then **X(R)** directly.

Expected: Q1 **X(R) entered**, Q3 **M entered**, Profile **XAMD**. The quiet higher line still shows Yearly **AMDX**. No change-history/comparison list or second subtype click appears in Watch.

### 267 — Larger thesis edit from Watch

1. Click **Full AMDX stack** below the Working AMDX panel.
2. Confirm the Lab heading says **working context for run**, interpretation **Expected**, date **2026-10-09**.
3. Click the **Yearly row Q3 cell** (Jul–Sep), then **M**.
4. Click the top **Trade Plan** tab to return to Watch.

Expected: the Yearly Profile is now **XAMD** in Lab and the Watch higher line. The 90m quartet remains **XAMD** with Q1 X(R) and Q3 M. This deliberate larger edit also captures the run's working basis automatically.

### 268 — Restart keeps the shared stack and historical backfill

1. Close with the window X. Reopen using the same command and directory.
2. Confirm Watch still shows the Yearly and 90m **XAMD** profiles. If the 90m target is not selected, click its Q1 to inspect; do not enter again.
3. Open the **1 · Historical Lab** menu preset again.

Expected: 1985 Yearly still shows **AMDX / Q3 D entered**; the separate current working edit did not replace it. Reopening and navigation do not create new phase entries. Return to Watch with menu **2**.

### 269 — Review retains the original launch basis

1. Open **Shared trial → 5 · Review · captured launch context**. This is the final checkpoint.
2. Confirm the caption says **Working context captured at run launch** and reference **2026-10-09 09:15**. The quiet Yearly launch context shows **AMDX**, while the current maintained calendar was changed to XAMD in checkpoint 267.
3. Click **Full AMDX stack**.

Expected: a read-only captured stack opens. Yearly is **AMDX / Q3 D entered**; the original 90m profile is **Unresolved**, because it was absent at launch. Phase buttons and reference controls are disabled. Close the dialog normally. This captured Expected stack is separate from the editable Observed run assessment below it; no comparison baseline is selected automatically.

Report **265–269 PASS / FAIL / QUESTION / NOT TESTED**, with the checkpoint and exact visible result for anything unclear. These checks assess the shared data workflow, not final visual design.
