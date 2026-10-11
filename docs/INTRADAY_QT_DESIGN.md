# Intraday QT — inventory and proposed capture design

**Status:** Proposed for operator review; no production implementation or accepted trading policy.
**Baseline:** main `83d82323ca936dedf045027760d81a1cd7de76b1`, accepted E7; schema v37 / Alpha 0.7. Latest full suite: 456 passed on Python 3.12.14, clean exit; E7 operator acceptance: nine PASS.

## Problem and proposed behavior

The current run has one expected and one observed value per QT level. Recording a later interpretation replaces the earlier value. It cannot represent a different expectation for each of the day's four sessions and sixteen 90-minute intervals.

Keep active use small: four session selectors, four cycle selectors, and an editor for the selected session and cycle. Focus the current interval initially. Open other intervals only when the technician wants to forecast, inspect or review them. Preserve the underlying hierarchy and recorded changes without requiring twenty completed answers per run.

This is the remaining Milestone E intraday-depth requirement in `PROJECT_REQUIREMENTS.md` and `CONTEXT_MATURITY.md`. It does not expand Milestone F execution safety or publish automatic context effects.

## Verified inventory

| Area | Current implementation | Consequence for this slice |
| --- | --- | --- |
| Factual clock and hierarchy | `analysis/market_time.py`: NY futures-day rollover at 18:00; four six-hour sessions; active session quarter and interval bounds | Reuse the time contract; do not construct a second clock in the widget. |
| Expected interpretation | `TradingSessionRun.qt_context`, normalized by `analysis/quarter_theory.py`; `set_qt_context` replaces the flat map | A per-interval history needs a separate contract. |
| Observed interpretation | `review_observed_qt_context` plus one note; independent Review setter | Keep observation separate from expectation, including revisions and comparison identity. |
| Storage | `database/trading_session_run_repository.py` stores both flat maps in existing JSON columns | Old values lack enough interval/write-time provenance for automatic expansion. |
| TDA editing | `gui/qt_context_widget.py`: eight phase selectors; whole context emitted on a change | Preserve the higher-level stack; add only the selected intraday scope to active interaction. |
| Watch | Read-only interpretation summaries and raw factual time context | Keep existing permissions and process transitions authoritative. |
| Review | `gui/post_market_review_widget.py`: flat expected summary and eight observed selectors | New comparison must name the particular session/cycle and expectation revision. |
| Reference time | Live/Forward Test update `run.market_time_context`; Replay/Historical Backtest use the selected stored reference | Current time cannot identify when an earlier expectation was recorded. Store that provenance with each new revision. |
| Unrecorded state | The legacy phase value `N/A` also serves as Unknown in comparison | New records distinguish unrecorded/Unknown from an explicit Not Applicable choice. Do not change old semantics as part of this slice. |

The attached trading-plan example requests daily/session AMDX worksheets. *Building a Trade Plan* shows the four sessions and 90-minute cycles on pages 26–27. Its NYPM Q4 header reads 16:00–18:00 while the subrows start at 16:30. Preserve the accepted application's 16:30–18:00 interval; do not adopt the inconsistent header. The source also depicts shorter subcycles. Those are outside this first four-session/four-cycle proposal.

### Names must identify the interval

The existing raw `day` layer identifies the active six-hour session; raw `session` identifies the active 90-minute cycle. The interpretation map also exposes `macro_90m` as “90m Macro,” without a distinct factual child-quarter entry in `raw_quarters`. These existing names are not enough to reinterpret historical phase values safely.

Use explicit new display labels, for example **NYAM session · 06:00–12:00** and **NYAM cycle 3 · 09:00–10:30**. Retain the legacy stack and its labels during the first persistence slice. Do not silently rename, duplicate or map legacy `day`, `session` or `macro_90m` interpretations into new intervals.

## Time and interval identity

All windows use **America/New_York**, independent of the workstation timezone. Bounds are **start inclusive, end exclusive**. Session/cycle numbers describe clock position; they do not imply A/M/D/X phases.

| Session | Session bounds | Cycle 1 | Cycle 2 | Cycle 3 | Cycle 4 |
| --- | --- | --- | --- | --- | --- |
| Asia | Previous civil day 18:00–00:00 | 18:00–19:30 | 19:30–21:00 | 21:00–22:30 | 22:30–00:00 |
| London | 00:00–06:00 | 00:00–01:30 | 01:30–03:00 | 03:00–04:30 | 04:30–06:00 |
| NYAM | 06:00–12:00 | 06:00–07:30 | 07:30–09:00 | 09:00–10:30 | 10:30–12:00 |
| NYPM | 12:00–18:00 | 12:00–13:30 | 13:30–15:00 | 15:00–16:30 | 16:30–18:00 |

For futures trading day 2026-10-06, Asia begins 2026-10-05 at 18:00. At exactly 10:30, NYAM cycle 4 becomes current; cycle 3 retains its identity and records. At 18:00, the trading-day identity changes. The existing coarse futures-week availability remains in force; these QT windows do not certify exchange opening, maintenance, holidays or tradability. When the existing clock reports Closed, there is no current QT interval. Historical browsing remains separate from the current marker.

Proposed stable key: `(run_id, futures_trading_day, session_id, scope, cycle_index)`, with `scope` Session or Cycle and no cycle index for a session. Persist NY start/end timestamps with UTC offsets, timezone and a time-contract revision. Reconstruct from the saved bounds/version, not a later time-definition change. Derive dates with civil-calendar arithmetic; never assume an arbitrary local day has 24 elapsed hours.

The run owns its interpretations. Two runs on the same trading day have distinct records; this first slice does not synchronize them or carry values between runs.

## Compact interaction proposal

1. **TDA:** open at the current session/cycle. Show the selected interval's two expectation fields: session and 90-minute cycle. Show the higher-level stack behind a collapsed disclosure. Record only changed fields in one action. Untouched intervals stay Unknown.
2. **Watch:** show the current cycle's saved expectation and its session context. Inspection can select an earlier/future interval without moving the clock or modifying records. Changes use the existing return-to-analysis transition; Watch does not introduce another authorization or editing path.
3. **Review:** choose a session/cycle and record an observed phase. Display the identified expectation alongside it, with Matched / Changed / Expected Unknown / Observed Unknown / Not Comparable. A collapsed day history reveals the other sessions/cycles. It is a browsing surface, not a completion checklist.

Session and cycle phases remain independent. A session phase does not populate its four cycles. A cycle change does not replace the session phase. Entering cycle 4 does not copy cycle 3. There is no automatic A/M/D/X schedule or carry-forward.

Selection and editing must stay distinct. Clicking a session/cycle never saves a record. Changing a field creates a draft; **Record expectation** commits only changed scope values atomically. Leaving a dirty editor requires a visible save/discard choice. A passive clock tick never retargets a draft: keep the selected interval pinned and mark the new current interval separately. On reopening, restore saved data; discard transient unsaved editor state. Initial focus follows the stored market reference, with no wall-clock fallback for Replay/Historical Backtest or completed-run Review.

Proposed phase choices: Unknown, Not Applicable, A, M, D, X(C), X(R), Distortion. Full names can appear beside the selected field or in a tooltip. Unknown is the default, not a required confirmation. There is no completion percentage, new gate, entry effect or automatic competency evidence.

## Proposed record and comparison contract

Each explicit save appends an immutable revision with:

- revision ID and the stable interval key/bounds;
- channel: Expected or Observed;
- value state: Unknown, Not Applicable or Interpreted; phase only when Interpreted;
- technician source, application record time, explicit market reference and environment;
- optional note, predecessor revision ID and, for an observation, the compared expectation revision ID.

No record means unrecorded Unknown. Clearing a previously recorded value to Unknown appends an Unknown revision and preserves earlier history. Not Applicable is an explicit technician classification, not missing information or proof of a closed market. A later correction appends a revision; it does not erase the earlier value.

The working view can show the latest explicit expectation. Review defaults to the **first explicit expected revision for that interval**, visibly labeled with its recorded market time; it never silently substitutes the newest expectation. If a different baseline is selected, save its ID with the observation. A newer expectation or observation cannot rewrite an existing comparison pairing. Returning to TDA after Review does not let a later expectation masquerade as the original forecast.

Distinguish Before interval / During interval / After interval using the expectation's explicit market reference and target bounds. During/After expectations remain visible with that timing label. A retrospectively entered expectation is never advertised as an advance forecast. Recording wall time is separate from historical market time: neither proves provider knowledge “as of” that historical date. No score or competency evidence is derived from these comparisons.

Unknown and Not Applicable semantics are explicit: both Interpreted values compare for equality; an Unknown side yields Expected Unknown or Observed Unknown, and two Unknown sides are Not Comparable. If either side is explicitly Not Applicable, the pair is Not Comparable and the side's classification stays visible. Legacy comparisons retain their existing E1 behavior.

## Persistence and legacy proposal

Prefer a dedicated **versioned intraday JSON payload on TradingSessionRun**, alongside the existing flat expected/observed maps. A new column and migration (likely v38) are justified if needed; this design does not require squeezing new history into an unrelated v37 field. Choose the final migration only after the domain contract is reviewed. Persist changed session/cycle revisions in one transaction and reload from the repository before presenting success.

Old runs open with their original flat stack and **No interval history recorded**. Migration does not invent twenty scoped answers, infer expectation timing from the run's latest market timestamp, or alter an old comparison. The first implementation should leave legacy editing/reading intact and add the new contract independently. Consolidating redundant legacy intraday controls is a later reviewed compatibility decision.

Changing current time definitions, selecting a different source capture or reopening the database does not change saved interval bounds, phases, revision IDs or comparison pairs. Raw time-derived facts and human interpretations remain separate. The existing calendar/rule, candidate authorization and evidence stores are untouched by this proposed data addition.

## First implementation slice after design review

Implement stable interval identity and versioned run persistence first, with a disposable focused editor for the selected interval. Defer replacing all production QT controls until identity, historical defaults and comparison pairing are proven. The preview is interaction exploration, not an implementation or persistence test.

Developer verification should cover exact 00:00/06:00/10:30/12:00/18:00 transitions, Asia's preceding date, weekend/closed references, NY offset changes, stable saved identity after definition changes, no retargeting of a dirty editor, no copy-forward, atomic saves/revision ordering, immutable comparison pairing, run isolation, v37 restoration without invented history, and restart. Existing E1/E3/E4/E5/E6/E7 gates and context tests remain regression requirements.

The later operator pass should use an explicit persistent sandbox and three short checks: record two different cycles; pair an observation and inspect the visible comparison; restart and confirm the same IDs and values. Explain one action and result at a time. Do not append a dense acceptance list during this design-only slice.

## Design checkpoint verification

The synthetic preview passed twelve browser interaction assertions: separate cycle defaults, guarded draft navigation/discard, appended working revisions, first-expectation comparison, observation without an expectation, preservation of a null comparison baseline after a later expectation, read-only Watch, retained neighboring cycles, and twenty independent history scopes. Light/dark desktop and 320px layouts were inspected; the expanded history also fit without horizontal overflow. Qt WebEngine's older Chromium lacks `light-dark` support, so screenshot inspection resolved the exact specified palette pairs in the test harness; native host theme switching remains unverified.

Smoke-document checks: **4 passed in 0.50s** on Python 3.12.14. All 244 smoke identities/statuses remain unchanged from main. `git diff --check` passed. This checkpoint changes only this design document and `PROJECT_STATE.md`; production source, tests, schema and published plan match accepted main. The existing 456-pass full suite was not repeated for documentation-only changes. Preview assertions are not production persistence or operator acceptance evidence.

## Decisions for operator review

- **Provisional operator feedback, 2026-10-11:** the pertinent-cycle/context direction is promising, but the PNG suggests too many buttons/clicks and too much effort interpreting the form. The embedded visualization failed, so layout and disclosure feedback remain inconclusive without hands-on use. Independent session/cycle interpretation received tentative assent; first-expectation comparison remains tentative. The separate Record action raised a clear motion/memory concern: forgetting it could leave missing data. Test automatic draft persistence with visible save/error state and no extra save obligation, while keeping persistence distinct from analytical completion. These are directions for a subsequent trial, not final requirements, design acceptance or production authorization. Retain the current preview as a baseline for comparison.

- Does focusing one session/cycle with expandable day history support the technician's working sequence?
- Is **first recorded expectation** a useful default Review baseline, with later revisions available explicitly?
- Keep session-level and cycle-level interpretations independent, with no inheritance in the first slice?

These are proposed interaction/ownership choices. Alpha 0.7 trading policy, the real Friday Asian Range Monday relationship, shorter subcycles, day-wide shared interpretation, and automated scoring/entry effects remain outside this slice.
