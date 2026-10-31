# TDA → Watch integration journey

## Why this is the next milestone

Study connected-review checks 364–365 passed. The next dependable-workflow gate is the operating journey: retain chart-derived context, enter Watch without transcribing it, use contextual tools, return to analysis and recover the same work after restart.

The earlier mapped Focus demo deliberately had no Trading Run. The earlier quiet-Watch demo explicitly bypassed incomplete TDA to reach the surface under review. Their passing checks do not certify this handoff. This trial starts a synthetic Replay run in the real mapped TDA runtime, with all eight stations initially incomplete and no automatic completion or mode override. Production behavior is unchanged.

## What actually carries through

| Information | Existing owner / behavior | Limit |
| --- | --- | --- |
| Station notes, selected station, completion | The active run's TDA station session, retained by ID | The first Deck has five stations, not a finalized four-chart assignment |
| Primary draw, alternate draw, thesis | Watch's TDA Carry-Forward reads the same station session | Prioritizes these three; falls back to recent populated notes; excerpts are capped at 180 characters |
| Day-specific IF/THEN point | Same TDA session, rendered among Watch criteria | Adding a point does not assert that its condition occurred |
| AMDX | Existing run-bound maintained calendar and commands | Manual interpretation; no inferred price classification |
| Watch capture | Existing Study Find editor/storage, seeded with supported date/instrument/session | Displayed run/time/AMDX context is not an exact persisted evidence link |
| Return to analysis | Existing process transition in the same run | Editing a completed station does not automatically clear its completion marker |
| Restart | Run references restore its process and station sessions | This does not certify backup restoration, migration or the whole daily workflow |

Native inspection also shows remaining layout work: TDA observations can be below the fold, and Watch currently reserves more vertical space than its operating canvas uses. This slice verifies handoff continuity; it does not certify final density or space efficiency. Report if either prevents locating the required information.

Completing TDA or entering Watch is not trading authorization. Broker facts remain unavailable; this trial cannot place orders. “Live Watch” is the process-mode name even though the environment is **Replay**. No models need to be selected for this bounded journey; model/candidate adoption and broker integration are not under review.

## Open the separate trial — only after publication

Close the other Cockpit window. Keep real Study work in its existing durable directory. This new directory is for synthetic trial material only:

```bash
python tools/tda_watch_journey_demo.py \
  --data-dir "$HOME/ict-cockpit-trials/tda-watch-journey-v0"
```

Use this same command to resume. The tool refuses an unrelated nonempty directory, starts only one run, and does not silently reset a completed or out-of-scope trial. If you deliberately finish the run, choose a new empty trial directory for another trial; do not delete the earlier one.

It opens **Trade Plan → process → Run Trading Day**, at **Premarket / TDA**, with MNQ Replay fixed to **2026-10-09 09:15 New York**. Use the mapped station runner here, **not the separate global Guided TDA tab**. The Focus/map area has its own scrollbar: scroll inside it to reach Observation and the thesis watch-point inputs. Process transition buttons are below that area. The clock is fixed for repeatability. No TradingView connection or matching historical chart is needed: this checks information continuity, not the quality of market analysis.

## 366 — build context and carry it into Watch

1. Start from the mapped TDA view. On a fresh trial, all eight stations should be incomplete. If you close midway, reopening should retain your selected station and notes without marking them complete.
2. For the first five stations (Instrument/Session Context, IPDA Premium/Discount, Monthly Liquidity, Weekly Context and Daily Context), use a short placeholder such as `Synthetic context check`, then **Mark Station Complete & Continue**. This is intentionally synthetic; the completion marker is not a competency result.
3. In **Primary Draw**, enter `Synthetic primary draw: prior day high`. In **Secondary / Alternate Draw**, enter `Synthetic alternate: prior day low`. Mark each complete and continue.
4. In **Premarket Thesis**, enter `Synthetic thesis: wait for a retracement before considering displacement`.
5. In **Models in Play & Live Watch Points → Technician / Day-Specific Additions**, enter IF `Price returns to the marked area`, THEN `Observe displacement; no automatic entry`, and click **Add Watch Point**. Leave model selection unchanged.
6. Mark the thesis station complete. Click **Finish TDA / Enter Live Watch** (scroll down to the process transition controls if necessary). If warned about missing stations, choose **Return to TDA** and complete the missing work; do not use File Incomplete Anyway for this check.
7. In Watch, find **TDA Carry-Forward** in the operating area: expect 8/8 stations complete and the primary/alternate/thesis wording. Find your IF/THEN point among the criteria (the operating area can scroll). Confirm broker facts remain unavailable. Nothing should require copying the TDA text into Watch.

## 367 — use support, then revise analysis without losing the run

1. In **AMDX now**, select the NYAM 90m Q3 cell and choose **D**. Expect its interval/value to include D; there is no second Save. This is a synthetic interpretation, not a claim about the historical market.
2. Open **Capture Study Find** from the Watch edge. Use Pattern `Synthetic handoff example` and Observation `Context visible without transcription`; confirm the seeded date is October 9, instrument MNQ and session NYAM. Click **Save & return to Watch**. Stay in the same Watch run; this saves a capture, not a trade.
3. Use the process transition **Return to Analysis**. Open **Premarket Thesis** through the map or full Deck overview. The earlier notes and IF/THEN point should remain.
4. Change the thesis to `Revised synthetic thesis: wait for clearer displacement`. Return via **Finish TDA / Enter Live Watch**. Expect the revised wording in Carry-Forward, the same IF/THEN point and the retained AMDX entry. Do not choose Finish Live Watch or Stand Down for this trial.

## 368 — reopen at the same operational anchor

1. Close normally while in Watch and reopen with the same command/directory.
2. Expect Watch in the same Replay run, with the revised thesis, IF/THEN point and D entry still present. Reopening must not create another run or repeat capture saving.
3. Optionally inspect the saved `Synthetic handoff example` through the saved-find browser, then return through **Trade Plan → Run Trading Day**. Its existence is covered by developer checks; no extra capture is required.

Report 366–368 PASS / FAIL / QUESTION, plus one usability observation if useful: **Could you recognize what you had concluded in TDA and resume Watch without reconstructing it?** This is the remaining operator question; passing automated continuity checks alone cannot answer it.

## Validation and delivery

Two end-to-end tests PASS: normal (non-override) completion/transition, carried notes and watch-point ID, AMDX update, capture save/return, analysis revision, same run/process/TDA IDs after reopening; plus unfinished-TDA restoration and refusal of an unrelated directory. Native TDA and Watch views inspected at 1600×900. Initial test expected a bare D, but the UI correctly includes interval and entered-state text; the assertion now checks that displayed value within its context. No production-code fix was necessary.

The developer check does not establish operator acceptance or full daily/backup readiness. This local branch is intended as a draft stacked on #111; no merge is authorized. After operator review, resolve concrete handoff gaps if found, then proceed to cross-suite daily continuity and authorized stack consolidation.
