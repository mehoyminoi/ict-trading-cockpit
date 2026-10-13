# Bounded higher Observed Review

`feature/amdx-higher-review-v1` implements higher-stack Review on top of the maintained Observed calendar. The run's original launch reference determines its entire New York futures-day window: previous-date 18:00 inclusive to reviewed-date 18:00 exclusive. Bounds use calendar dates, so daylight-saving windows may span 23 or 25 elapsed hours.

Original launch is the default. Candidate points are original launch, reviewed day start and calendar midnight, deduplicated by the five higher occurrence/position/state fingerprints. Ordinary days expose one orientation without an extra selector. Boundary days offer both contexts. Same-year quarter changes share a yearly head; year/quadrennial/16-year occurrence changes do not inherit judgments. Selection is read-only and does not retarget the existing sessions/90-minute Review editor.

## Storage and portable proof

`AMDXRunObservedRepository.higher_orientations(run_id)` reads the original bound launch and returns deterministic candidates. `prepare(..., higher_scope=True)` freezes the selected canonical target, complete current Observed projection/ledger, run/parent basis and bounded scope proof. UTC-equivalent candidates are accepted; arbitrary other instants, other reviewed days and the exclusive endpoint are rejected. Repeated local hours retain distinct offsets and are compared as UTC instants.

The proof preserves original/selected references, reviewed date/bounds/timezone, policy/temporal revision, source kind and the full retained five-layer candidate/selected/original contexts. The existing target/calendar request freezes channel, branch, cycle, quarter, head, capture metadata and result. New writes regenerate/validate scope under the owned transaction, reject changed sources/heads/policy and append the calendar command plus assessment receipt atomically.

Proof lives **inside the immutable version-2 assessment receipt**, rather than a redundant table. Existing SQL immutability protects it; failed receipt insertion rolls back the calendar command. Schema **v46** is a format barrier only: no old rows or tables are rewritten, no legacy assignment/proof is invented. An older v45 reader rejects the database before writing. This refines the earlier contract's proposed additive metadata table while preserving its atomicity and provenance requirements.

Original version-1 commands retain their original-reference restriction and exact request/result bytes. Mixed assessment archives use top-level version 2; version-1-only archives remain version 1. Exact retries return retained results before checking today's source or resolver. Portable readers validate retained contexts/boundaries/ledger and ownership without calling today's higher-cycle resolver. Retained packets do not establish evidence availability or prospective prediction validity.

## Native operation

Bound Review offers **Review full AMDX stack**, an adjacent higher overview/quarter editor, immediate legal phase choices and direct X(C)/X(R). It edits maintained Observed only; comparison baselines are not selected. Monthly Unassigned/Distortion and weekly Distortion/Closed retain inspectable Q1–Q4 with no automatically selected inactive quarter.

Context/quarter/provenance changes cancel an open gesture. Mode/run/tab permission, frozen source/head/parent and target are checked before writing. Source, stale and write failures disable input until deliberate Reload; a successful write followed by read failure is reported as committed. Reopening makes a fresh read and does not replay failed input.

Valid per-run context/quarter navigation restores automatically in a separate QSettings key. It neither changes Lab preferences nor writes an interpretation receipt. Invalid preferences show the original launch reference with input disabled until Reload. **Captured run assessment** displays the retained proof and exact Observed stack read-only; **Captured launch stack** displays the original Expected capture separately.

`tools/amdx_higher_review_demo.py` retains a separate synthetic January 1, 2027 MNQ Replay fixture and a deliberate failure injection. The future reference tests calendar behavior only. Follow `AMDX_HIGHER_REVIEW_OPERATOR_GUIDE.md` for six checkpoints, 275–280.

## Limits and next checkpoint

Unbound legacy runs keep their existing paths; missing ownership is not guessed. This bounded Review selection does not limit broad historical Lab backfill. Original Expected captures stay immutable; no classifier, Watch history/comparison path, new information-availability policy or final UX is adopted.

With operator checks 275–280 accepted, the immediate next milestone is a stable consolidation checkpoint and separately authorized merge. Intermediate work remains full-cockpit 16:9 rendering, quiet Watch/analytical TDA/spacious Lab, the Study loop and dismissible Study-first doorway, versioned criteria/evidence evaluation and deliberate legacy/history import/performance. Coverflow/macropad remain later rendering work.

Verified source: `310c4747d208ebb6a5852ca30008d0fd4d790390`. Full regression: 1,134 PASS across 88 isolated modules in 332.64s, no failures/errors/skips or pytest warnings; 45 new cases. Actual v45 migration preserves every source row and v1 receipt; rollback and old-reader rejection pass. Native offscreen mouse/dialog/restart verification is distinct from operator checks 275–280, now reported PASS on 2026-10-13 (America/Denver).

Operator acceptance records the six documented functional behaviors; final renderer acceptance and merge remain separate. PR #75 is ready for review after its acceptance checkpoint. Local user notes were not inspected or imported. Source/tests/tools, schema v46, Alpha 0.7 and the completed 1,134-test regression remain unchanged.
