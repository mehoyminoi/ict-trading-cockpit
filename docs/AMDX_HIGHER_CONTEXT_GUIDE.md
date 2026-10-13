# Higher AMDX context foundation

The pure resolver identifies 16-year, quadrennial, yearly, monthly and weekly quartets from an explicit aware market reference. The shared read projection adds unchanged day/session identities when the market is open and selects only the requested run/channel/branch/cycle heads. It carries the original claim, anchors, applicability, inference and references rather than reconstructing a flat answer.

This is a foundation on `feature/amdx-higher-context-v0`, based on merged main `6dd43c8`. The native UI, database, schema v41, Alpha 0.7 and all 260 smoke records are unchanged. No new operator smoke trial or local fixture is needed for this slice.

## Boundary examples

All clocks below are America/New_York. The conventions reuse the existing raw time API.

| Reference | Factual orientation | Resolver behavior |
| --- | --- | --- |
| Dec 31, 2026, 19:00 | Futures day Jan 1, 2027; calendar still 2026 | Yearly/16-year Q4; monthly January occurrence is unassigned before its first Monday |
| Jan 1, 2027, 00:00 | New calendar year/anchored cycle | Yearly/16-year/quadrennial Q1; this change records no AMDX phase |
| Oct 1, 2026, 09:15 | Weekly Thursday Q4; October before first Monday | Weekly occurrence stays Sep 28 with its September Q4 parent; October has no active monthly quarter |
| June 29, 2026, 09:15 | Fifth Monday week | Monthly Distortion, no Q5; weekly Monday Q1 has no invented monthly-quarter parent |
| Oct 9, 2026, 09:15 | Friday trading day | Weekly Distortion, no active weekly quarter; ordinary day/session quartets still available |
| Nov 1, 2026, 17:59 → 18:00 | Sunday closed → Monday futures day | Weekly Closed → Q1; monthly pre-first-Monday → Q1; existing intraday identities resume |

Cycles have four explicit, contiguous half-open intervals. Calendar quarters begin at New York midnight. Monthly Monday weeks and weekly Monday–Thursday days begin at the preceding 18:00 futures-day boundary. Across DST, full weeks keep New York wall-clock bounds and can span 167 or 169 elapsed hours. Monthly weeks retain their full bounds even when extending into the next calendar month.

A relationship comes from the occurrence itself, not the currently displayed month. A weekly quartet that crosses September/October keeps its September parent in both views; October does not silently adopt that week. A fifth week has no monthly Q5 parent. Calendar-year/quadrennial relationships are explicit; no monthly-to-three-month parent is inferred. Prior-Q4 IDs identify the previous occurrence only and supply no interpretation by themselves.

## Pure API

```python
from datetime import datetime
from ict_cockpit.analysis.amdx import InterpretationHistory
from ict_cockpit.analysis.amdx_context import project_stack
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE

view = project_stack(
    run_id="synthetic-example",
    reference=datetime(2026, 10, 1, 9, 15, tzinfo=MARKET_TIMEZONE),
    history=InterpretationHistory(),
    legacy_context={"quarter": "D"},
)
```

An empty history gives Unresolved AMDX profiles despite known factual Q positions. The legacy `quarter=D` value is carried separately with legacy/derived provenance; it creates no Yearly anchor or expected/observed pairing. Missing legacy keys stay missing, and supplied values retain their exact meaning rather than being defaulted to Not Applicable.

`resolve_higher_cycles(reference)` returns the five higher occurrences with factual position/state, temporal-definition revision, parent links and prior-Q4 identities. `resolve_stack_cycles(reference)` appends the existing intraday cycles without altering their IDs or parent content. `project_stack(...)` selects current retained interpretation heads for the explicit ownership scope. Other runs, channels, branches and prior cycles never supply a fallback head. An inconsistent cycle ID or claim inference is rejected. The output and its retained claims are immutable; the projection writes nothing.

The caller selects the reference. Future Review binding must use its validated preserved run reference; the pure module does not look up a run, choose a fallback date or read today's clock. Projection reads the supplied current heads; it is not an as-of historical replay query. Future Study research must identify the retained information/history basis explicitly to avoid future-data leakage.

## Verification and next step

45 new cases cover existing raw-position equivalence, UTC normalization, calendar/futures year-end distinction, full weeks and cross-month stable identities, Friday/fifth-week/pre-Monday/closed states, DST elapsed lengths, independent scopes, exact claim/entered/implied/subtype/uncertainty/applicability provenance, unchanged intraday identities, legacy preservation, malformed references/scopes and corrupt identity/inference rejection. Focused group: **134 passed in 0.91s**. Complete suite: **789 passed in 452.22s** across all 71 isolated module processes, clean exits with no failures/errors/skips or pytest warnings. Every JUnit count matched collection; this is the complete suite under module isolation, not one combined process. All test processes exited. The same source is recorded in `PROJECT_STATE.md` and `HANDOFF.md`. Python 3.10 syntax is checked; execution uses Python 3.12.

Next is deliberate higher-cycle persistence/binding design using this identity/projection contract. Do not treat the pure module as already migrated higher history or an implemented new UI. Study-owned selection, final 16:9 geometry, shortcuts/coverflow, comparison exploration and actual classifiers remain separate downstream work.
