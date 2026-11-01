# Study capture-context continuity

Based on operator 328–330 PASS and the accepted save-feedback correction, plus real-session feedback in STUDY_REAL_SESSION_FINDINGS.md. This bounded slice fixes new-capture context while preserving existing drafts and saved records. Schema 48 unchanged.

Opening Study Find from independent AMDX investigation seeds a fresh form with the selected New York calendar date, calendar instrument and selected named session. A daily quartet's inspected quarter supplies the session; a 90m quartet supplies its parent session. Higher-layer selection leaves session empty. The selected calendar date is a civil reference date, not a derived futures trading-day label; the visible notice states that distinction. No silent clock-based session substitute.

An unfinished capture retains every field and its identity. Persistent guidance compares its date, instrument and session with the pinned opening context and updates as fields are edited. Differences are permitted, not automatically corrected or forbidden: the technician can deliberately study a related context. Existing explicit association receipts remain immutable and separate from capture fields. No retrospective repair of the operator's incorrect Day 1 record is attempted.

After a saved capture, reopening through the investigation starts a new identity and empty content with the new context suggestions. Prior saved finds/links remain in Review and the overview. Navigation away and back while unfinished does not clear the draft. Existing explicit link/save actions remain unchanged. Invalid references/read failures or run-scoped inspection do not seed an independent capture.

MNQ is inherited from the existing maintained calendar; configurable global instrument preferences are still deferred. Follow-up-question inbox and broader field design remain subsequent work. No automatic evidence, plan adoption or run creation.

## Operator recheck

Use the separate chart-session fixture, preserving any unfinished real notes.

1. With the previous capture saved, return to AMDX Lab. Choose a historical date and select London in the Sessions/day row, even if the reference clock is in NYAM. Open Study Find. Confirm a fresh form with that date, MNQ and London. Fields remain editable.
2. Enter an unfinished note. Return to the calendar, change the date/session and reopen. Confirm the note and original capture fields are retained, with a persistent notice explaining the differences. Restore matching fields manually if appropriate; notice should update.
3. Complete required fields and save. Return to the calendar, select another date and reopen. Confirm a new capture with empty pattern/observation and the new suggested context. The prior saved find remains in the investigation overview if explicitly linked, and in general Study Review regardless.

These are targeted correction checks, not a repeat of 328–330 or a new research assignment. Report the date used and any mismatch. Do not overwrite historical records merely to make this test pass.

## Developer verification

32 focused tests PASS across capture-context, integrated Study, Study Find, investigation overview and MainWindow. Coverage includes inspected London versus clock NYAM, parent session for 90m, higher-layer unknown session, preserved draft mismatch, and new identity after save with original capture/association intact. Native 1280×720 rendering inspected; diff check passes. Operator recheck remains pending.
