# Study history — retrieval before analytical prioritization

## Purpose

The review checkpoint records learning outcomes; it does not decide what deserves study next. This small foundation makes previously retained questions, findings and review checkpoints retrievable across investigations of the current Trade Plan, including older revisions, without replacing the working task.

Open **Study history…** from the AMDX investigation area or **Browse Study history…** from Study home. Text search matches all entered words, case-insensitively, against displayed saved wording and retained context. Type filters distinguish Question, Finding, Partial answer and Review. Results show original plan revision and recording time, sorted newest recording first. Details preserve historical context and original wording. Search is literal retrieval, not semantic tagging, clustering, deficiency detection or a recommendation engine.

Only saved records are included. Standalone Study Finds remain in Review saved finds; unlinked questions and findings are included in this history. Source snapshots can repeat the same observation across multiple records, so the count is explicitly a retained-record count, not an independent evidence sample count. Market time remains distinct from recording time. Review support may mention differing revisions without implying definition equivalence.

The browser is read-only. There is no resume/change-investigation action, edit, promotion or automatic next-step creation. Returning leaves the active task, calendar and draft in place. An incomplete read fails visibly instead of displaying a misleading empty history. The current implementation loads this plan's records in memory; pagination and larger-volume retrieval are future scale work.

## Operator 348 — retrieve earlier material

Reuse `/tmp/ict-study-review-v0`; schema 51 is unchanged. Your existing 345–347 checkpoints provide material.

1. From the investigation, click Study history. Select Review in the type selector. Locate an earlier checkpoint and confirm its original question, revision and wording are visible.
2. Search for a distinctive word from that checkpoint, then try a word you know is absent. Expect matching records, then an explicit no-match message. Clear filters to restore the list.
3. If saved questions or findings are present, select their type and inspect one. An empty type is not a failure if no records of that type were saved in this fixture.
4. For an explicit cross-investigation check, save your current capture work first. Then create a new disposable investigation, enter a distinct test question and save an uncertainty-only review. Open Study history: both the earlier and new investigation's reviews should be retrievable. This step changes your working investigation deliberately; the browser itself does not switch it. There is not yet a general investigation-resume selector.

## Operator 349 — return without disturbing current work

1. In the current investigation, open a fresh Study Find and enter `Unfinished history-return test` in Notes. Do not save/discard it.
2. Return to the AMDX investigation and note its question and Historical Reference. Open Study history, filter and inspect an older record, then Return to current work.
3. Confirm the current question/reference are unchanged. Reopen Study Find: the unfinished note should remain. Opening history from Study home is the same read-only browser and should return to that surface.

This trial evaluates retrieval and context preservation, not whether a statistical insight or competency judgment has been produced. Later practical evaluation should ask whether retrieved history reveals useful candidate questions for analysis; no performance conclusion follows from repeated wording alone.

Validation: 17 targeted tests PASS across history scope/filter/order/read-only behavior, read failure, current-work preservation, review persistence, overview and MainWindow. The initial test run exposed Study home button initialization order; moving registration after home construction fixed it and the full targeted rerun passed. Browser rendered offscreen and visually inspected. Diff check passed. Published as draft PR #99, stacked on #98, at `fedd532`. Operator 348–349 PASS. No merge.

## Accepted UX follow-up

The repeated reveal click for review entry in 348 is a design refinement, not a failed retrieval check. The operator accepted task-directed entry as an important requirement: direct review opens the editor; inspection can keep it collapsed. See `UX_INTERACTION_STANDARDS.md`. This checkpoint records the decision without changing UI behavior.
