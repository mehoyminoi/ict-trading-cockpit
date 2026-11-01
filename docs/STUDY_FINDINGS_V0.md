# Study findings and partial answers — first functional slice

## Why this matters

Real Study produced an insight that was relevant to the investigation but was not a question. The technician should be able to retain that learning without changing its meaning or abandoning the current capture. The acceptance question remains: “Do I feel like it helped me learn something?”

## Implemented behavior

- **Keep finding…** beside the existing question action prefills selected Notes/Observation wording. With no selection, it opens an empty editor. The existing selected-question direct-save behavior is unchanged.
- A Finding may remain standalone. The optional association is unchecked initially and names the destination question, instrument, historical reference and Expected/Observed interpretation. Capture date/session are shown alongside it for context checking.
- **Partial answer** requires explicitly checking the association. This retains a technician interpretation; it does not validate the answer, complete the investigation, adopt a rule or award competency evidence.
- A saved capture association takes precedence over later navigation context. Otherwise the capture-open investigation context is offered. Neither route creates or changes the source Study Find's own association. Blank investigation questions do not offer an association.
- **Study findings…** retrieves findings for this Trade Plan. Explicitly associated items also appear in the existing investigation overview. Standalone findings do not silently appear in that overview.
- Records preserve original selected wording, retained interpretation, source capture snapshot, chart paths, recording time and optional explicit investigation destination. Capture-open navigation is retained separately from saved association. Subsequent capture edits/discard do not rewrite findings. Chart paths reference files; this does not copy images into a new archive.
- Save failures retain text; unchanged retries use the same identity/timestamp. Successful save disables another save in that composer. Cancel defaults to preserving unsaved wording. No cross-dialog semantic duplicate detection, editing, reassignment or deletion is introduced.

Schema 50 adds independent immutable `study_finding` records. Existing question records remain byte-identical and are not relabeled. A transaction failure rolls back migration. Older application branches cannot open a schema-50 database; use a separate fixture for this trial.

This is a functional learning checkpoint, not final field/layout approval. The small composer deliberately exposes destination/type together before saving. The established one-click selected-question action remains unchanged. Later refinement may reduce finding capture actions once the semantics have been evaluated. Unified Study Find Save/Link controls and richer time/HTF fields remain separate work.

## Operator guide — 338–340

After publication, launch a new separate fixture (do not reuse your narrative fixture):

```bash
source .venv/bin/activate
python tools/study_criterion_demo.py --data-dir /tmp/ict-study-findings-v0
```

If that directory was already used for this slice, reopening it is fine. Do not use a directory from an older test for this trial.

### 338 — Keep a partial answer without changing the source capture

1. In AMDX Lab, keep the seeded synthetic investigation question (or replace it with a clearly labeled test question). Set Historical Reference to October 8, 2026, 09:15; select London in the daily row.
2. Click Open Study Find. In Notes, type: `Test insight: London supported my initial interpretation, but later NYAM price action changed it.` Highlight that sentence.
3. Click **Keep finding…**. The wording should already be present. Confirm the investigation shown is the intended question and reference. Association should initially be unchecked.
4. Select **Partial answer**, check **Associate this finding with the investigation shown below**, and click **Keep finding**. Expect `Finding kept`.
5. Return to current work. Your capture text and context should remain. Return to the investigation and open its overview. The partial answer should be listed and inspectable, with its original wording/source snapshot. Saving it does not automatically link or save the whole Study Find.

### 339 — Standalone finding stays separate; questions still behave as before

1. Return to Study Find. Replace or append Notes with another disposable insight. Highlight it and choose **Keep finding…**.
2. Leave type **Finding** and association unchecked. Save and return. In **Study findings…**, both records should be available. In the investigation overview, only the associated partial answer should appear.
3. Return to Study Find, highlight a test follow-up question, and click **Keep question for later**. It should save directly without a composer, and remain retrievable through **Study questions…**.

### 340 — Retained learning survives source discard and restart

1. Using only disposable draft text, choose Discard current draft and confirm.
2. Open Study findings. Both saved items and their original source notes should remain available.
3. Close and reopen the same demo directory. Open Study findings and the investigation overview again. The standalone finding should remain in Study findings; the partial answer should remain associated with the original investigation.

Report PASS, FAIL or QUESTION per checkpoint. No market interpretation is being graded. Also note whether the composer interrupts the learning moment or whether its visible destination makes the extra step worthwhile; that qualitative feedback remains welcome.

## Local validation

230 distinct focused checks passed across the finding/question/overview UI, MainWindow, smoke-document parser, discard/context protection, criterion/repository checks and historical migration suites (overlapping tests were rerun after the final UI changes). The findings composer was rendered offscreen and visually inspected. `git diff --check` passed. Operator 338–340 remain pending; no publication or merge is claimed by this local checkpoint.
