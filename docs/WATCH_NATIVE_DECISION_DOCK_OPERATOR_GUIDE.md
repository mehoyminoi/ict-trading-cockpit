# Native Watch decision-dock trial

This focused trial verifies that the accepted reference-and-decision interaction now uses the real native Watch, maintained MNQ calendar and existing AMDX command. It does not ask for final Watch-layout approval.

**Status:** Developer verification complete; operator checks 281–285 PASS from the explicit 2026-10-15 report. This accepts the bounded native interaction, not final Watch styling or layout.

## Get the trial

Close any older Cockpit/demo window first. Preserve any local `docs/SMOKE_TEST.md` notes before switching branches.

```bash
cd /home/jesse/projects/ict-trading-cockpit
git status --short
git fetch origin
git switch feature/watch-native-decision-dock-v0
git pull --ff-only origin feature/watch-native-decision-dock-v0
source .venv/bin/activate
python tools/watch_decision_dock_demo.py --data-dir /tmp/ict-watch-decision-dock-v0
```

If `git status --short` shows your smoke-test notes, either commit them on their current branch or use:

```bash
git stash push -m 'local smoke notes before Watch decision-dock trial' -- docs/SMOKE_TEST.md
```

Leave that stash saved during the trial. The demo uses a separate synthetic database and a fixed **MNQ Replay reference of 2026-10-09 09:15 New York**. It does not open your regular database. Closing with the window X is safe. Reopening the same directory retains AMDX entries and the display profile. Use another empty directory to repeat from the beginning.

## Five checkpoints, in order

### 281 — Truthful chart-edge reference

1. Confirm the trial opens directly in **Live Watch**.
2. Click **Plan reference** above the Working AMDX panel, or press `P` while no text field is active.
3. Read the provenance, definition message, active target and current quartet line.

Expected: a temporary native reference opens nearest the configured chart-facing edge. It says **Trade Plan · Alpha 0.7** and **No published AMDX definition is configured for Trade Plan Alpha 0.7**. It shows the same active 90-minute target and profile as the Working AMDX panel. No fixture rule is presented as policy.

### 282 — Legal Q3 choice uses the shared command

1. At the fixed 09:15 reference, confirm the active 90-minute target is **Q3**.
2. In the open reference, confirm only **M** and **D** are offered—no A or X choice.
3. Click **D**.

Expected: the reference dismisses immediately, focus returns to **Plan reference**, and the main Working AMDX 90-minute row shows **Q3 D entered** with profile **AMDX**. There is no Save action and only one maintained-calendar command is produced.

### 283 — Direct one-click X(R) at Q4

1. In the main Working AMDX 90-minute row, click the **Q4 / 10:30** cell. This changes the inspected target only.
2. Open **Plan reference** again.
3. Confirm **D**, **X(?)**, **X(C)** and **X(R)** are available, while A and M are absent.
4. Click **X(R)** once.

Expected: the reference dismisses; the main row shows **Q4 X(R) entered**, retains **Q3 D entered**, and remains profile **AMDX**. X(R) takes one decision click after opening the contextual reference; no subtype menu or second Save appears.

### 284 — Dismissal and text entry do not create side effects

1. Open the reference and press `Esc`. Open it again and click in the main Cockpit outside the popup.
2. Confirm the reference closes and **Plan reference** remains the return anchor.
3. Click the Watch observation field and type a sentence containing several lowercase `p` characters.

Expected: `Esc` and outside-click dismissal record nothing. Every typed `p` remains in the observation field and does not open the reference. Pressing `P` outside text entry still opens it.

### 285 — Constrained monitor profile persists

1. Use **Workspace profile → Cockpit above · TradingView below**, then open the reference.
2. Confirm it opens along the lower chart-facing edge. Close the window with X.
3. Reopen using the same command and directory; open the reference again.
4. Use **Workspace profile → TradingView left · Cockpit right** and open it once more.

Expected: the below profile survives restart, and the left profile deliberately moves the same logical surface to the left chart-facing edge. Target, legal controls and AMDX data do not change when the display profile changes. No arbitrary docking controls appear.

Report **281–285 PASS / FAIL / QUESTION / NOT TESTED**. For anything unclear, include the checkpoint number, exact control used and visible result. These checks judge the native shared-action loop and return behavior—not typography, final Watch density or real AMDX definition content.
