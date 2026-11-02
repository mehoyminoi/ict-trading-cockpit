# Manual Replay reference — Trial B prerequisite

Status: implemented on `feature/replay-reference-v0`, from main `0a10928b3200490848816f1653920446b31db250`. Operator acceptance pending. Schema 53 / Trade Plan Alpha 0.7 unchanged. This is an isolated rehearsal prerequisite, not a Silver Bullet strategy or routine TDA/Watch readiness claim. Draft documentation PR #116 is independent and unchanged.

## Contract and owners

- `analysis/replay_reference.py`: strict America/New_York local-time resolution, explicit repeated-hour occurrence, nonexistent-time rejection, UTC ordering and original 18:00 futures-day bounds. Same instant is a no-op. Rewinds and another trading day reject.
- Original `market_context_snapshot.reference_market_time`, immutable run binding and launch capture retain their meaning. Current `market_time_context.captured_at` is the selected market instant, not actual recording time. Actual evidence `created_at` and command `recorded_at` remain wall-clock timestamps.
- `database/replay_reference.py`: validates active Replay ownership and the displayed run basis, then uses existing shared-calendar `prepare_capture` / `consume`. One transaction saves current context, a manual administrative receipt and an exact AMDX context-use capture. Existing AMDX claims and earlier captures are unchanged. Duplicate operation IDs return the saved result without duplicate evidence; changed input under the same ID rejects. Stale run/master/capture and write failures do not partially advance.
- The receipt uses the existing evidence envelope with explicit `manual_replay_reference_receipt_v1` metadata; Review labels it administrative. It does not assert observation, a skipped interval, a market event or a thesis change. The enclosing legacy Observation enum is retained for reader compatibility; the versioned discriminator and note distinguish administrative meaning. Ordinary observations carry the current selected reference and actual creation time separately.
- `TradingRun.candidate_authorization` enforces a persistent, Replay-only hold after advancement. Existing criteria/gates remain retained assessments, not fresh verification. Watch cards, counts, opportunity summary and safety strip expose that distinction. Changing criteria does not remove the hold. Interactive requalification is outside this slice; a simulated decision can be written as an observation.
- The shell provides **Set Replay reference…** in active TDA/Watch, refreshes projections after commit, and preserves editor text. An intentionally pinned AMDX target stays pinned; current clock/raw QT advance, and **Follow current** returns the editor to the current target. An in-flight gesture cannot silently follow the new reference. A Study Find draft keeps its prior capture basis.
- The launcher still chooses only the initial reference. Review day ownership and original economic-calendar coverage remain unchanged. Live/Forward Test clocks and Historical Backtest behavior are unchanged.

No new SQL schema, tables, columns, migrations, strategy criteria or trading permissions. JSON metadata is additive. Older readers may preserve but ignore the freshness marker: do not use older code to continue this advanced trial. No safe downgrade is claimed. The coarse existing calendar is not exchange maintenance/holiday verification.

## Isolated operator guide

Do not use your authentic Study workspace. In the repository on this branch, activate your normal Python environment, then run:

```bash
python tools/tda_watch_journey_demo.py --data-dir "$HOME/ict-cockpit-trials/replay-reference-v0"
```

Use this **new, dedicated** directory. The launcher starts one synthetic MNQ Replay at 2026-10-09 09:15 New York. Later invocations resume it. If that directory already contains a concluded or unrelated trial, use another new directory name; do not delete or reset it. The bottom banner describes the launch reference, not the advancing clock.

### 371 — advance one run and preserve earlier context

1. In TDA, enter a short synthetic expectation in a station. Complete the placeholder stations, or use the existing explicit incomplete-TDA override for this fixture. Enter Watch. This is not a test of adopted TDA content.
2. In Watch's observation input, record `Initial expectation at 09:15 — synthetic rehearsal; no trading permission.` Use the existing capture action. Note the Trading Run identity.
3. Advance TradingView Replay independently to 10:15 on the same historical day, if available. Cockpit must not follow automatically. For a mechanics-only check, simply use the stated reference; report that TradingView coordination was not exercised.
4. Click **Set Replay reference…**, enter `2026-10-09 10:15:00`, and Apply. No note or second confirmation is required. Confirm the same run, manual 10:15 NY time and NYAM orientation. The repeated-hour selector can stay unchanged for this date.
5. Record `Second observation at 10:15 — operator-attested.` No FVG, criteria or AMDX phase should have been assigned by changing the clock.
6. Advance to `2026-10-09 10:45:00`. The current 90m target should now be NYAM Q4 (use **Follow current** if you intentionally pinned another quarter). Qualification remains withheld; existing assessments are retained.

### 372 — resume and reject unsupported movement

1. Close the fixture normally and run the same command again. Confirm the same run and 10:45 reference. Do not complete the run before this restart check.
2. Try `2026-10-09 10:00:00`: it must reject the rewind without changing the current reference. Cancel or correct the editor.
3. Try `2026-10-09 18:00:00`: it must reject the next trading day without changing the run. Cancel.
4. Apply exactly `2026-10-09 10:45:00`: this is a no-op, not another change receipt.

### 373 — interruption and evidence review

1. Simulate being away while TradingView advances to 11:05. Manually set Cockpit to `2026-10-09 11:05:00`. Record `Away 10:45–11:05; intervening price action not observed. Wait / stand down for this exercise.` The clock command itself must not invent that observation.
2. Choose the existing **Stand Down / No Trade** transition and inspect Market Review. Verify the initial and later observations remain, with their respective market references and actual recording timestamps. Reference-change entries must say administrative. No earlier entry should have been rewritten to 11:05.
3. Confirm the earlier expectation and your explanation are still understandable. A No Trade result is a valid outcome; do not create a trade record to complete this test.

Report 371–373 individually. These checks establish this bounded behavior, not strategy validity or complete Trial B readiness. Do not rerun the entire historical smoke campaign.

## Verification boundary

Focused automated tests cover forward/no-op/rejected movement, DST and midnight, immutable original context and earlier evidence, atomic failure, stale writers, retry identity, independent timestamps, retained qualification and other-environment behavior, pinned gestures, open capture content, native Review rendering and restart. Adjacent owner regressions cover shared-calendar transactions/migration, time rules, Watch qualification/composition, contextual Study capture, Review and launcher/journey behavior. Exact executed results are recorded in PROJECT_STATE.md; operator checks remain NOT TESTED until reported.

No TradingView connection, price-data feed, unattended observation, interactive requalification, new plan revision, automatic news refresh, cross-day progression or rewind. Watch-to-Study still does not persist exact run/time/AMDX linkage; this command does not strengthen that association.

After acceptance, the next activity is the manual-first NYAM Silver Bullet Trial B rehearsal, with candidate analytical conditions and evidence limits explicit.
