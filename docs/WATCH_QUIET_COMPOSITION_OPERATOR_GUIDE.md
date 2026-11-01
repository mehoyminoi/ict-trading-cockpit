# Native quiet-Watch composition trial

**Acceptance update, 2026-10-17:** operator retest “292 passed” on correction `6561f2c` completes all checks 291–295. Earlier failure/retest instructions below document the resolved issue. No further Watch trial or merge is implied; Study-first startup is the next milestone.

This focused trial checks whether the real native Watch surface now reads as one quiet operating composition while preserving the accepted AMDX decision and Study Find paths. It does not ask for final styling approval and does not simulate or connect a broker.

**Status:** Original implementation verification: **1,155 PASS across 95 isolated module processes**. Operator report on 2026-10-17: **291 and 293–295 PASS; 292 FAIL**. The Q4 entry correction requires the focused retest below; the earlier complete-suite result is not a fresh validation of that correction.

## Focused 292 retest after updating

Keep the existing trial directory. Open the same demo, visit the Study Find tab, then return to Trade Plan → Run Trading Day. Click the **90m Q4** cell and then **X(R)**. Expect Q4 to read X(R), the quartet to read AMDX, and Plan reference to show the same selected target/value. Close the window and reopen the same directory to confirm the entry survives. No additional Save is needed. Report 292 PASS or the exact visible failure message; the four already-passing checkpoints need not be repeated.

## Get the trial

Close any older Cockpit/demo window first. Preserve local `docs/SMOKE_TEST.md` notes before switching branches.

```bash
cd /home/jesse/projects/ict-trading-cockpit
git status --short
git fetch origin
git switch feature/watch-quiet-composition-v0
git pull --ff-only origin feature/watch-quiet-composition-v0
source .venv/bin/activate
python tools/watch_quiet_composition_demo.py --data-dir /tmp/ict-watch-quiet-composition-v0
```

If `git status --short` shows smoke-test notes, commit them on their current branch or use:

```bash
git stash push -m 'local smoke notes before quiet Watch trial' -- docs/SMOKE_TEST.md
```

Leave that stash saved during the trial. The demo uses a separate synthetic database, managed-media directory and fixed **MNQ Replay reference of 2026-10-09 09:15 New York**. Closing with the window X is safe. Reopen the same directory to test retained state; use another empty directory for a fresh trial.

## Five checkpoints, in order

### 291 — One quiet composition and fast reacquisition

1. Start in the default **TradingView left · Cockpit right** profile.
2. Look away, then return to Watch.
3. Locate mode/session, New York time, active AMDX interval, next attention cue and whether process/broker attention is required.
4. Confirm **Operating Context**, **AMDX now** and **Broker & process safety** are visible together.

Expected: one left chart-facing edge, operating canvas, compact AMDX now and bottom safety strip form one composition. The main page does not repeat the full AMDX editor or top market-context blocks. The operating canvas may scroll internally; the safety strip remains visible. Quiet state does not use a positive green demand for attention.

### 292 — Compact AMDX remains the same immediate command

1. In **AMDX now**, click the 90m Q4 cell.
2. Click **X(R)** once.
3. Open **Plan reference** and inspect its active target/current value.

Expected: Q4 becomes `X(R)` immediately, the quartet profile updates, the Plan reference shows the same target/value, and there is no second Save or Watch history/comparison route. Legal choices change with the selected quarter; unavailable roles cannot be chosen.

### 293 — Safety truth and earned salience

1. Read every safety cell in the default state.
2. Confirm broker, account identity, numeric risk envelope, position and order facts are visibly unavailable—not silently connected, flat or safe.
3. Confirm P&L is absent.
4. From **Trial safety state**, choose **Block trading-day permission gate**.
5. Return it to **Pending** afterward.

Expected: the blocked authorization fact and summary become apparent without restyling the whole screen. Broker unavailability remains distinct from authorization. No order action appears and no fake broker fact changes.

### 294 — Accepted contextual support still returns to the edge

1. Open and dismiss **Plan reference**; confirm focus returns to its edge button.
2. Open **Capture Study Find**, enter a partial draft and dismiss it.
3. Reopen and confirm the draft resumes, then complete **Save & return to Watch**.

Expected: both surfaces use their existing owners and return to the same Watch composition. The run, process mode, AMDX target and safety state remain unchanged. Exact Study Find run/time/AMDX linkage remains labeled display-only.

### 295 — Constrained monitor profile and restart continuity

1. From **Workspace profile**, choose **Cockpit above · TradingView below**.
2. Confirm the same orientation edge moves to the bottom and still contains the same cues/launchers.
3. Close and reopen the same command/directory.
4. Optionally open **Open full AMDX lens**, then return through **Trade Plan → Run Trading Day**.

Expected: the bottom-edge profile survives restart; there is still only one orientation edge. Run/process/AMDX and unfinished Study state remain intact. Opening the full AMDX Lab changes workspace only—it does not transition the Trading Run. No arbitrary docking is offered.

Report **291–295 PASS / FAIL / QUESTION / NOT TESTED**. For anything unclear, include the checkpoint number, exact control used and visible result. Also note what your eye finds first after returning from TradingView and which parts still require deliberate reading.
