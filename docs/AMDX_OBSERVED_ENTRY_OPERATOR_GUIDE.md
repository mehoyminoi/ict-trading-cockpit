# Observed AMDX — native Review trial

Branch `feature/amdx-observed-entry-v1` adds observed quartet entry to the normal Post-Market Review screen. Schema **v41** and Trade Plan **Alpha 0.7** are unchanged from the observed-action backend. Functional operator acceptance is pending; this is not the final 16:9 renderer.

## Sync and open

From your repository, with the usual Python environment active:

```bash
cd /home/jesse/projects/ict-trading-cockpit
git status --short
git fetch origin
git switch feature/amdx-observed-entry-v1
git pull --ff-only origin feature/amdx-observed-entry-v1
python tools/amdx_observed_entry_demo.py --data-dir /tmp/ict-amdx-observed-v1
```

If `docs/SMOKE_TEST.md` has local comments, preserve them before switching/pulling:

```bash
git stash push -m "Local AMDX smoke results" -- docs/SMOKE_TEST.md
```

After syncing, use `git stash apply` to restore those comments; keep the stash until any conflict is resolved. Do not discard local results or stash unrelated work silently.

This opens the normal MainWindow in a separate retained synthetic Replay database. It starts directly in **Post-Market Review** at **2026-10-08 09:15 ET**, using the normal TDA-to-Watch-to-Review transitions with an explicitly synthetic incomplete-TDA override. It does not manufacture completed analysis, trade setup, competency evidence or a published trading rule. Do not conclude the run until the restart check is complete. The same command restores the same fixture, run, reference and committed profiles. An unrelated directory, missing saved database or wrong fixture kind is refused.

## What the panel means

**Observed AMDX · 2026-10-08** is the entry surface. The Day row is the four-session quartet; the 90m row is the selected session's four quarters. The saved Trading Day supplies the review date. A missing/invalid saved date disables entry rather than guessing today's date. The session selector accesses Asia, London, NYAM and NYPM within that date. Clicking a Day quarter also brings its child session into view; it still selects the Day quarter for entry. Click the 90m row to target a child quarter.

The default starts at NYAM 90m Q3 in this fixture. Review stays on the inspected target when time advances. **A / M / D / X(?) / X(C) / X(R)** record immediately, subject to the selected quarter's legal roles. X(C) and X(R) each take one click from an active target. These direct buttons also serve working entry in TDA/Watch. The secondary menu retains Unknown, whole-quartet Not Applicable and context-sensitive clear actions.

One valid choice revises the quartet and implies its siblings; a new contradictory choice replaces incompatible active anchors without manual cleanup. Entered/implied distinctions and hover context remain visible. Repeating an identical explicit choice reports **Already current**, with no new interpretation or pairing. Unknown, unresolved X subtype and Not Applicable remain distinct. The independent working expectations are retained. Routine observed entry never automatically chooses the first or latest expectation for comparison.

Only current observed profiles occupy this panel. No AMDX comparison controls or history list are added. The older flat intraday controls and descriptive comparison list are hidden in the database-backed application; their saved values are retained. Higher observed legacy fields and the separate legacy Review note remain accessible below. The fixed higher-context line retains working legacy/derived provenance, not newly classified higher observed quartets. Normal TDA/Watch continue to show current working profiles, with no comparison option or launch route.

## Five short checks — smoke 255–259

Report PASS / FAIL / QUESTION / NOT TESTED. These are new checks; previous accepted results 245–254 are preserved.

1. **255 — Orientation and independent capture:** confirm Review, reviewed date 2026-10-08, NYAM 90m Q3, Day/90m rows and higher context. Click **M** once. The 90m profile becomes XAMD; Day remains unresolved. No Save, baseline choice or station completion is needed. There is no AMDX comparison/history panel.
2. **256 — One-entry correction and direct subtype:** click Day **NYPM/Q4**, then **X(R)** once; Day becomes AMDX with entered X(R). Click **X(C)** once to change the subtype. Click Day **NYAM/Q3**, then **M**: Day becomes XAMD with implied Asia X(?), without old-anchor cleanup or moving the C subtype to Asia. The NYAM child profile from check 255 remains XAMD.
3. **257 — Legal roles, uncertainty and no-op:** select Day Q1/Q2/Q3/Q4 and check enabled roles A/X, A/M, M/D, D/X. Direct X subtypes are available only at Q1/Q4. At Day Q3 choose **M** twice; the repeated explicit choice says Already current. Use the secondary menu for **Unknown**, **Not Applicable · whole quartet**, and **Clear Not Applicable**. Clearing does not resurrect old phases. Choose Q3=M to restore XAMD.
4. **258 — Historical targets and failure:** use the session selector to inspect all four sessions; selection records nothing. Return to NYAM 90m Q3. Use **Demo reference → Advance by 90 minutes** repeatedly until the clock shows another trading day; the Review date/target remain 2026-10-08. Enable **Simulate observed write failure**, choose D, and confirm Not recorded with the existing XAMD retained. Disable the failure and choose D deliberately again; it becomes AMDX. No automatic replay occurs. The fixture fault is limited to its separate database and persists across restart until disabled.
5. **259 — Restart:** leave the fault disabled, close and reopen with the same command. The same run, Review mode, reviewed date and committed Day/90m profiles return. Use the session selector to inspect the earlier edited NYAM quartet if navigation defaults to another quarter. Selection itself is transient; the saved judgments are durable.

## Developer boundary

Native tests cover immediate independent capture; valid role/subtype controls; correction/no-op/Unknown/applicability; all-session access; rollover/gesture/cancellation; run/channel ownership changes; stale observation/pair rejection without replay; atomic source/pair/receipt failure; post-commit read failure; and normal-window fixture restart. Full-suite and focused results are recorded in `PROJECT_STATE.md` and `HANDOFF.md`. This runtime's existing application minimum produced 1280×876 when requesting 1280×720; the fixed panel and scrollable Review content were visually inspected. Primary 16:9 geometry, broader Study presentation, classifiers, higher-order cycle mapping, shortcut assignments and purposeful comparison exploration remain downstream.
