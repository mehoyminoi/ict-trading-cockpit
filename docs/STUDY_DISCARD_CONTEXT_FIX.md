# Untouched discarded capture follows selected context

Narrative-session feedback reproduced a handoff gap after discard. The retained date/instrument/session were interpreted as existing draft content, blocking the next calendar-context suggestion.

The fix stores the complete fresh post-discard form fingerprint (including identity) in the existing per-database workspace settings. Opening capture from the investigation can replace suggested context only while the form still matches that fingerprint exactly. After any actual draft/context edit, the current preservation/mismatch behavior applies. Each successful suggestion refreshes the seed. Saved capture identity changes invalidate the old seed. Restart restores the same comparison without a new schema or source-record mutation.

9 focused tests PASS across discard and context continuity, including new-context inheritance after discard, preservation after authoring begins, and restart seed recognition/manual-override protection. No automatic repair of old incorrectly dated captures. Schema 49 unchanged. Local only; targeted operator recheck is discard → choose another calendar date/session → Open Study Find, followed by editing a note and confirming subsequent navigation preserves it.

## Short operator recheck after publication

Use your existing synthetic Study fixture. Do not discard notes you want to keep.

1. Open Study Find, enter disposable text, and choose Discard current draft. Confirm discard.
2. Return to the AMDX Lab, choose a different Historical Reference date and explicitly select a different session. Open Study Find from the investigation.
3. Check that the capture date and session match that selection. No separate historical-time input is expected in Study Find.
4. Enter a short note. Return to the Lab, choose another date/session, and reopen Study Find. Your note and its original capture date/session should remain; the differing-context notice should explain the discrepancy.

These checks validate context handoff and draft protection, not AMDX interpretation or final Study field design. No need to repeat the full narrative exercise for this correction.
