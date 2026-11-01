# Resume Study investigations

This first continuity slice provides a database-owned question registry and retained capture-opening destinations. Schema 52 adds two tables; migration does not rewrite historical captures, associations, findings or reviews. It is not the full proposed In work/Stable/reopen lifecycle.

## Behavior

- New investigation retains a named outgoing investigation. Resume investigation lists registered tasks and explicit historical question variants in the current plan revision. Identical wording never merges distinct IDs. Legacy conflicting variants are separate labeled choices; selecting one establishes registry wording, without changing source receipts. Older revisions remain accessible through Study history, not editable through this selector.
- Named questions become read-only when retained or opened for capture. Use New investigation for a different question. Deliberate refinement/revision of a retained question remains future work.
- Authored capture content (pattern, observation, notes, move or images) blocks New/Resume until saved or explicitly discarded through existing controls. It is not silently saved or reassigned. Context-only defaults do not block switching. This bounded version does not offer several concurrent capture editors.
- Resume leaves the calendar reference unchanged. Open Study Find from the selected investigation to establish the next capture's context. Always check the visible destination; switching the question alone does not retarget a capture already open elsewhere.
- A capture's opening destination is persisted by capture ID. An authored capture keeps that destination through calendar reentry/restart. Saved associations remain authoritative. A legacy authored capture without retained context prompts for deliberate destination confirmation; Cancel leaves it unassigned and plain save remains available.
- New captures after successful save retain the existing opening destination. Merely opening the selector/history or changing the calendar does not create an association or competency evidence. The latest-draft restoration model remains; full multi-draft recovery and answer baselines are deferred.

## Before operator trial

Close Cockpit and archive the entire durable directory, including its origin manifest. Use a unique filename. Keep the archive and originals; schema 52 cannot be opened by the prior application version. Test a copied workspace first if uncertain. Do not use the original missing `/tmp` path or an older archive as if it contained today's work. The backup verifier accepts both schema 51 and 52.

## Operator 352 — retain and resume a question

1. Save any meaningful unfinished capture, or deliberately discard only disposable work. From the investigation area, note the current question and calendar reference.
2. Click New investigation. Enter a distinct disposable question. Click Resume investigation and select the earlier question/ID. Confirm its wording returns, calendar reference stays unchanged, and its overview still shows its original associated material.
3. Resume the disposable question, then return to the earlier one. Close/reopen the durable workspace and confirm the selected investigation remains. Read-only wording is intentional; selecting an older question is not making a new copy of it.

## Operator 353 — protect unfinished context

1. From the selected investigation, Open Study Find. Check its destination, then enter a disposable note. Return to the investigation area and try New investigation or Resume investigation. Expect a message to save/discard the current capture first; the active investigation and note must stay intact.
2. Close/reopen normally. Inspect the unfinished capture and its save destination. They should retain the same question/context. If the draft predates this feature and had no retained destination, expect explicit confirmation rather than a guessed association.
3. Save the disposable capture or use the existing discard control. Switching should then work. Do not change meaningful legacy capture associations for the sake of testing.

No requirement to repeat a natural Study session. Subsequent work will address reference reliability and keeping questions directly from review. Operator 352–353 pending. Publication requires explicit authorization, draft stacked on #102; no merge.

## Validation

Migration/repository regression suite: 179 PASS. Focused Study suites: 30 PASS covering resume, direct review, next capture, criteria and findings; 22 PASS covering integrated Study, atomic save/link behavior and all six resume checks. Earlier backup/restore checks and unaffected review/history/question/association checks also passed. Legacy capture-context checks exercised explicit confirmation/cancellation. These batches overlap and are not a distinct-test total.

The schema-51 upgrade is tested against the actual prior schema, including an injected failure at the schema-version barrier, unchanged old rows, rollback of new tables and rejection by the old reader after successful upgrade. Resume checks cover repeated A/B identity selection, unchanged calendar, restart, explicit legacy association, conflicting historical wording, distinct IDs with identical questions, cancellation and database write failure. Earlier tests were adjusted for deliberate metadata retention, read-only resumed wording and the existing fresh-capture-after-save behavior. A direct-review check now stops unrelated autosave before asserting that review entry itself performs no writes. Diff check passed.
