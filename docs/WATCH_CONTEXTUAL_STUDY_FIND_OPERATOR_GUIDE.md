# Native Watch contextual Study Find trial

This focused trial verifies that contextual capture in real native Watch uses the existing Study Find draft, managed screenshot and repository paths, then returns to the same operating anchor. It does not ask for final Watch styling/layout approval or claim that exact run/time/AMDX associations are already persisted.

**Status:** Developer verification complete; operator checks 286–290 PASS from the explicit 2026-10-16 report. This accepts the bounded capture behavior, not final Watch styling/layout or future durable exact-context linkage.

## Get the trial

Close any older Cockpit/demo window first. Preserve local `docs/SMOKE_TEST.md` notes before switching branches.

```bash
cd /home/jesse/projects/ict-trading-cockpit
git status --short
git fetch origin
git switch feature/watch-contextual-study-find-v0
git pull --ff-only origin feature/watch-contextual-study-find-v0
source .venv/bin/activate
python tools/watch_contextual_study_find_demo.py --data-dir /tmp/ict-watch-contextual-study-find-v0
```

If `git status --short` shows smoke-test notes, commit them on their current branch or use:

```bash
git stash push -m 'local smoke notes before contextual Study Find trial' -- docs/SMOKE_TEST.md
```

Leave that stash saved during the trial. The demo uses a separate synthetic database, managed-media directory and fixed **MNQ Replay reference of 2026-10-09 09:15 New York**. Closing with the window X is safe. Reopen the same directory to test draft recovery; use another empty directory for a new trial.

## Five checkpoints, in order

### 286 — Exact, truthful Watch basis

1. Confirm the trial opens in **Live Watch**.
2. Click **Capture Study Find** beside **Plan reference**, or press `Ctrl+Shift+F`.
3. Read the two basis lines and the draft line.

Expected: the contextual surface shows saved Study Find fields **2026-10-09 · MNQ · NYAM**. It separately labels the run, 09:15 ET and active Working AMDX target/profile as **Current Watch context only**, explicitly stating that exact run/time/AMDX basis is not stored by the current schema. The main Watch position remains visible behind it.

### 287 — Dismissed draft resumes without reconstruction

1. Enter pattern **London high raid**.
2. Enter observation **Displacement arrived after the London high raid** and any short lesson.
3. Press `Esc` or click the main Cockpit outside the surface.
4. Reopen **Capture Study Find**.
5. Close the whole demo with X, rerun the same command/directory and reopen capture.

Expected: the same draft identity and text return both immediately and after restart. The surface says **Resumed existing draft** and does not substitute the current Watch defaults. Dismissal creates no saved Study Find and does not move the Watch process.

### 288 — Screenshot paste uses the existing managed attachment path

1. Copy any harmless chart/image screenshot to the system clipboard.
2. In the contextual surface, click **Paste chart** or press `Ctrl+V` while the surface is active.
3. Confirm the attachment count becomes **1 managed chart image attached**.
4. Dismiss and reopen once.

Expected: the attachment count remains one and the draft resumes. No path selection or extra attachment Save is required. If the clipboard has no image, the surface says so and changes nothing.

### 289 — Existing save path returns to unchanged Watch

1. With pattern, observation and the image present, note the active Watch mode and Working AMDX target/profile.
2. Click **Save & return to Watch**.
3. Open the top-level **Study Find** tab, then **Study Review**, to inspect the saved item.
4. Return to **Trade Plan → Run Trading Day**.

Expected: the contextual surface dismisses, focus returns to **Capture Study Find**, and the existing full Study Find shows **Saved** with the same text/image. Study Review lists the saved item. Watch remains the same run/mode and AMDX target/profile; no AMDX command, process transition, evidence or competency credit is created.

### 290 — Validation and existing-draft safety

1. Reopen contextual capture after the saved item; it should begin a new draft.
2. Attempt **Save & return to Watch** with pattern and observation empty.
3. Confirm it remains open with a specific required-field message.
4. Add partial pattern/observation, dismiss it, then open the top-level **Study Find** tab and change Instrument/Session to any obvious test values.
5. Return to Watch and reopen contextual capture.

Expected: invalid save never closes or creates a record. The non-empty draft retains its same identity and custom fields; current Watch MNQ/NYAM defaults are not substituted. Leaving Watch closes the temporary surface while preserving the draft.

Report **286–290 PASS / FAIL / QUESTION / NOT TESTED**. For anything unclear, include the checkpoint number, exact control used and visible result. These checks judge shared draft/save/image ownership and return continuity—not final styling, density or future durable context-link design.
