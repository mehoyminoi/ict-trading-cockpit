# Maintained Observed Review and captured run assessments

Bound MNQ Review now reads and revises the maintained Observed calendar directly. A phase choice commits its canonical calendar command and an immutable assessment receipt for the run in one owned transaction. Lab and Review therefore show the same current judgment; the run retains the exact revision it assessed even after later Lab or other-run corrections. There is no second copied run-owned quartet to drift from the calendar.

## Storage and preserved meaning

Schema v45 adds `amdx_run_observed_command`, append-only run assessment receipts with a per-run parent chain and composite foreign keys to the original run binding and calendar command. The catalog command and receipt share one operation identity deliberately; update/delete/replacement guards preserve history. The actual v44 migration retains every old table row, including bound runs and old run-only Observed claims/pairs, and imports no assessments automatically. Failed migration rolls back schema and source rows. Older applications require an unmigrated copy; v44's schema reader rejects v45.

`AMDXRepository.run_observed` exposes `prepare(run_id, reference=..., level=..., position=...)`, `revise(prepared, ...)`, `get_result(operation_id)`, `latest(run_id)` and `export_archive(run_id)`. `read_run_observed_archive` validates portable receipt chains without the current resolver/database. Requests retain immutable run/master binding, exact raw run context, original launch packet, inspected full Observed projection/archive, selected target, parent assessment and full calendar request. Results retain the complete resulting Observed projection/archive and original command, including nullable heads, no-op receipts, uncertainty/applicability and declared evidence/definition/unknown availability. Actual recording time remains distinct from the studied quarter reference.

A new assessment validates its displayed source/archive, run metadata, parent, canonical target and original run-start provenance under `BEGIN IMMEDIATE`. Stale source, competing writers, changed ownership/reference or invalid targets reject without either new record. Existing exact retries return the original assessment before current source/resolver checks. Caller transactions are not committed or rolled back by this facade. Corrupt or missing sources disable entry until explicit Reload AMDX. A post-commit read failure reports the assessment as recorded with refresh unavailable.

Observed is an interpretation, not certified correctness. This operation creates no run-owned Expected claim, automatic comparison baseline or new working-context capture. Original launch/decision Expected packets and existing comparisons remain unchanged. Lab-only backfill still creates no run. The current receipt captures the observed stack at this operation; it does not update older receipts or attach today's record to an earlier decision.

## Native workflow

The panel says **Maintained Observed AMDX**. Session/day navigation is read-only; legal phase choices and direct X(C)/X(R) record immediately. Review can inspect all four sessions in its preserved reviewed day. The run's original launch reference supplies initial session selection on reopen, including after the display clock advances. A chosen quarter supplies an explicit derived orientation reference; that does not claim evidence was available at that historical instant.

**Captured run assessment** opens the most recent receipt for this run as a read-only seven-layer stack. That inspection is separate from **Full AMDX stack**, which in Review continues to inspect the original captured Expected launch basis. Both labels retain their distinct meanings. Later Lab corrections update current Review orientation while the captured assessment remains unchanged. No assessment history/comparison route is added to Watch.

The earlier flat QT entry frame is hidden for bound runs so it cannot create a competing Observed source. Unassigned legacy runs retain their accepted run-owned workflow and forms. Existing run-only assessments are preserved as independent legacy records; this slice does not import, merge or delete them. Their original APIs/archives remain available, and deliberate legacy adoption is separate work.

## Boundary and next milestone

This slice connects currently permitted native session/day Observed input. The backend also permits the existing original-reference higher target scope. Selecting another higher orientation within the reviewed day still requires the separately specified bounded Review-period proof/selector; it is not enabled here. Capturing a full stack after an intraday assessment is inspection evidence, not permission to edit additional higher periods.

Final rendering, broader historical as-of reconstruction, legacy import, large-history performance, mutable criterion authoring/classifiers and Study-first startup remain separate. Alpha 0.7 is unchanged. `AMDX_REVIEW_CALENDAR_OPERATOR_GUIDE.md` provides five numbered checks in a retained separate synthetic fixture; earlier checks 1–269 remain unchanged.


## Operator acceptance

Checks 270–274 are PASS from the explicit 2026-10-13 report. The accepted scope is the five documented functional behaviors, not expanded higher-period entry, legacy import or final rendering. The user reports that the smoke-test file is saved locally but uncommitted/unpushed; its additional contents were not inspected or imported. No further operator trial is required for this documentation-only acceptance.
