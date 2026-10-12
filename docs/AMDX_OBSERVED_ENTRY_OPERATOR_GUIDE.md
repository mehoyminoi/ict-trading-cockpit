# Observed AMDX — native Review trial

Branch `feature/amdx-observed-entry-v1` adds observed quartet entry to the normal Post-Market Review screen. Schema **v41** and Trade Plan **Alpha 0.7** are unchanged from the observed-action backend. Checks **255–259 PASS**, reported by the operator on 2026-10-12 as “All points passed” after clarification/retest guidance; this is not the final 16:9 renderer.

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

**Observed AMDX · 2026-10-08** is the entry surface. The Day row is the four-session quartet; the 90m row is the selected session's four quarters. The run’s saved starting reference supplies the reviewed date. Older runs without that reference use the saved Trading Day as an explicit legacy fallback. A malformed retained reference or absence of both sources disables capture rather than guessing today’s date; hover the heading for provenance. The separate correction trial is `AMDX_REVIEW_DATE_OPERATOR_GUIDE.md` (check 260). The session selector accesses Asia, London, NYAM and NYPM within that date. Clicking a Day quarter also brings its child session into view; it still selects the Day quarter for entry. Click the 90m row to target a child quarter.

The default starts at NYAM 90m Q3 in this fixture. Review stays on the inspected target when time advances. **A / M / D / X(?) / X(C) / X(R)** record immediately, subject to the selected quarter's legal roles. X(C) and X(R) each take one click from an active target. These direct buttons also serve working entry in TDA/Watch. The secondary menu retains Unknown, whole-quartet Not Applicable and context-sensitive clear actions.

One valid choice revises the quartet and implies its siblings; a new contradictory choice replaces incompatible active anchors without manual cleanup. Entered/implied distinctions and hover context remain visible. Repeating an identical explicit choice reports **Already current**, with no new interpretation or pairing. Unknown, unresolved X subtype and Not Applicable remain distinct. The independent working expectations are retained. Routine observed entry never automatically chooses the first or latest expectation for comparison.

Only current observed profiles occupy this panel. No AMDX comparison controls or history list are added. The older flat intraday controls and descriptive comparison list are hidden in the database-backed application; their saved values are retained. Higher observed legacy fields and the separate legacy Review note remain accessible below. The fixed higher-context line retains working legacy/derived provenance, not newly classified higher observed quartets. Normal TDA/Watch continue to show current working profiles, with no comparison option or launch route.

## Five short checks — smoke 255–259

Report PASS / FAIL / QUESTION / NOT TESTED. All five checks are now accepted from the operator’s report. These steps remain repeatable; previous accepted results 245–254 are preserved. No separate per-check logs or local runtime details were supplied.

1. **255 — Orientation and independent capture:** confirm Review, reviewed date 2026-10-08, NYAM 90m Q3, Day/90m rows and higher context. Click **M** once. The 90m profile becomes XAMD; Day remains unresolved. No Save, baseline choice or station completion is needed. There is no AMDX comparison/history panel.
2. **256 — One-entry correction and direct subtype:** click Day **NYPM/Q4**, then **X(R)** once; Day becomes AMDX with entered X(R). Click **X(C)** once to change the subtype. Click Day **NYAM/Q3**, then **M**: Day becomes XAMD with implied Asia X(?), without old-anchor cleanup or moving the C subtype to Asia. The NYAM child profile from check 255 remains XAMD.
3. **257 — Legal roles, uncertainty and no-op:** select Day Q1/Q2/Q3/Q4 and check enabled roles A/X, A/M, M/D, D/X. Direct X subtypes are available only at Q1/Q4. At Day Q3 choose **M** twice; the repeated explicit choice says Already current. Use the secondary menu for **Unknown**, **Not Applicable · whole quartet**, and **Clear Not Applicable**. Clearing does not resurrect old phases. Choose Q3=M to restore XAMD.
4. **258 — Historical targets and failure:** use the session selector to inspect all four sessions; selection records nothing. Turn simulated failure OFF. Select NYAM, then click the **90m row’s Q3 cell beginning 09:00**; confirm the heading ends in **NYAM 90m Q3**, and click **M** to establish child XAMD. Selecting Day NYAM/Q3 targets a different quartet. Use **Demo reference → Advance by 90 minutes** repeatedly until the upper **Trading Day** date differs from 2026-10-08 (the futures day changes at **18:00 ET**, not midnight); the Review date/target remain 2026-10-08. Enable **Simulate observed write failure**, choose D, and confirm Not recorded with the existing XAMD retained. Disable the failure and first confirm that XAMD remains unchanged. Choose D deliberately again; it becomes AMDX. No automatic replay occurs. The fixture fault is limited to its separate database and persists across restart until disabled.
5. **259 — Restart:** leave the fault disabled, close using the **window’s X**, then reopen with the same command. Do not click **Conclude Trading Run** for this restart check. The same run, Review mode, reviewed date and committed Day/90m profiles return. Use the session selector to inspect the earlier edited NYAM quartet if navigation defaults to another quarter. Selection itself is transient; the saved judgments are durable.

## Restart support note

The operator reported the launcher error “The saved fixture has been concluded” after a premature close. The guard also uses that message when the restored active run does not match the fixture manifest; the original cause was not established. Closing the window alone is intended to support restart. Fresh-sandbox guidance used `python tools/amdx_observed_entry_demo.py --data-dir /tmp/ict-amdx-observed-258-retest`, preserving the original directory. The subsequent “All points passed” report accepts the five functional checks without claiming recovery of that original fixture or identifying which directory/run was used. No launcher source change is made by this acceptance checkpoint.

## Developer boundary

Native tests cover immediate independent capture; valid role/subtype controls; correction/no-op/Unknown/applicability; all-session access; rollover/gesture/cancellation; run/channel ownership changes; stale observation/pair rejection without replay; atomic source/pair/receipt failure; post-commit read failure; and normal-window fixture restart. Full-suite and focused results are recorded in `PROJECT_STATE.md` and `HANDOFF.md`. This runtime's existing application minimum produced 1280×876 when requesting 1280×720; the fixed panel and scrollable Review content were visually inspected. Primary 16:9 geometry, broader Study presentation, classifiers, higher-order cycle mapping, shortcut assignments and purposeful comparison exploration remain downstream.
