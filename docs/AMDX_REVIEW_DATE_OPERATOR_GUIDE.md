# Review date correction — focused trial

The reviewed date now comes from the run's preserved starting reference in its saved market-context snapshot. A later advancing clock and an older containing Trading Day label do not replace it. The target heading's hover explains the date source and any container-label discrepancy.

Older runs with no retained starting reference use the saved Trading Day date as an explicit legacy fallback. A malformed retained reference does not fall back to another date. If neither source is usable, Review disables capture. Working/observed claims, policies, comparison selection, schema v41 and Alpha 0.7 are unchanged.

The launch path now rejects a different-date run in an existing Trading Day before resetting the process, TDA or creating a run. It explains how to complete the current day and use **Start New Trading Day**. Same-date additional runs remain allowed. Existing older misgrouped runs restore using their own valid original reference; no records or containing-day labels are rewritten by production code.

## Open the retained trial

After syncing `feature/amdx-observed-entry-v1`, with the usual Python environment active:

```bash
python tools/amdx_review_date_demo.py --data-dir /tmp/ict-amdx-review-date-v1
```

Use a new empty directory. The fixture deliberately constructs a **synthetic older grouping discrepancy**: its containing Trading Day says **2026-10-08**, while the run's preserved starting reference is **2026-10-09 09:15 ET**. That construction happens only in this new isolated sandbox; it is not a migration, recovered operator history or production repair. Normal process transitions use the explicitly declared synthetic incomplete-TDA override. No price/news classifier or trading rule is added.

The footer identifies both dates and the separate database. The same command restores the same run and judgments. Existing observed-entry/working fixtures are not changed. This date fixture has its own kind and refuses unrelated/other fixture directories.

## Check 260 — date provenance, rollover and restart

This is one new focused smoke check, **PASS** from the guided operator reports on 2026-10-12. Previous checks 245–259 remain accepted.

1. **Original date:** confirm the panel says **Observed AMDX · 2026-10-09 · NYAM 90m Q3**, despite the footer's containing-day date being 2026-10-08. Hover the heading: it should explain the run-start reference and differing container label. Click **M**; the 90m Profile becomes **XAMD**, with Q3 entered and siblings implied.
2. **Rollover:** choose **Demo reference → Advance by 90 minutes** seven times from the fresh 09:15 reference. The upper clock reaches 19:45 ET and its Trading Day becomes **2026-10-10**. The Observed date and selected target stay **2026-10-09 · NYAM 90m Q3**; the child profile remains XAMD. Advancing time records no phase.
3. **Restart:** close with the window **X**, then reopen with the same command. Observed date remains **2026-10-09**. If navigation defaults to Asia, select **NYAM** in the session selector to inspect the saved child: its Profile remains XAMD. You need not enter M again. Transient navigation and committed interpretation are separate.
4. **Launch guard, after the restart check:** conclude this synthetic Trading Run, then click **Start Another Trading Run**. The different-date request must say **Run not started**, explain **Complete the current Trading Day → Start New Trading Day**, and create no second run/reset. The requested date may be the current live date after restart; the check is that it differs from the old 2026-10-08 container and is rejected. Do not attempt to restart this concluded fixture afterward; retain its directory and use a new empty directory for another trial.

Report PASS / FAIL / QUESTION / NOT TESTED for 260, naming the numbered checkpoint if something differs. The original premature-close report remains undiagnosed; this trial follows explicit window-close/conclude steps and does not claim to recover that original fixture.

## Recorded operator result

Operator guided report, 2026-10-12 (America/Denver): upper Trading Day advanced to October 10 while Observed AMDX remained October 9; NYAM 90m Q3=M was entered and the profile was XAMD. After window-X close and same-directory reopen, the date remained October 9; selecting NYAM restored XAMD and Q3 entered without another phase choice. After Conclude Trading Run, Start Another Trading Run created no second run and displayed: "Run not started - selected reference belongs to Trading Day 2026-10-13. Complete the current Trading Day, then choose Start New Trading Day". The October 13 request is the live reference after restart, not a change to the saved Review date. The heading-tooltip inspection was not separately reported; no operator hover acceptance is inferred.

## Developer verification

Native regressions cover different-date rejection before reset, the existing new-day path, same-date additional runs, saved older mismatched grouping, rollover gestures, actual MainWindow reopen, legacy/malformed/missing reference handling, stale in-flight date rejection and retained-fixture restart. Pure date cases cover timezone-aware local/UTC references and the 18:00 ET futures-day boundary. Final source/test counts and runtime evidence are recorded in `PROJECT_STATE.md` and `HANDOFF.md`.
