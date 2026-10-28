# Keep a Study question without losing the current thread — 331–333

## Purpose

This tests whether a research tangent can be retained with enough context to be useful later, without interrupting the investigation that produced it. You are judging low effort, trustworthy source context and easy return. The full vocabulary/tagging system and automatic task promotion are not part of this increment.

Launch a **new separate fixture**:

```bash
python tools/study_criterion_demo.py --data-dir /tmp/ict-study-question-inbox-v0
```

This branch uses schema 49. Keep your earlier chart-session fixture untouched; an older branch cannot reopen a schema-49 database. The seeded synthetic criterion is not needed here.

## 331 — Park the question

1. In AMDX Lab, enter a working question, choose a reference date and select London in the day/session row. Open Study Find.
2. Enter a short observation and put this in Notes: `Why did London initially look like manipulation, but NYAM later change that interpretation?`
3. Select that sentence in Notes. Click **Keep question for later…**.
4. Refine the question if useful, then click **Keep question for later**. You should see explicit confirmation and the question in the saved list.
5. Inspect its detail: original selected wording, refined question, capture date/instrument/session and original observation/notes are retained separately. An unlinked source should say no explicit saved investigation association. If you deliberately linked the capture before opening, that saved association should instead appear.
6. Click **Return to current work**. Your capture and investigation question should remain unchanged. The source need not be saved as a Study Find just to park a question.

## 332 — Remain in control of unfinished text

1. Change the current Notes text. Reopen the question action; if nothing is selected, enter a new short question.
2. Press Escape. Choose Cancel when asked to discard. Your unsaved question should remain.
3. Return again and deliberately discard this second question. Your source Notes must remain unchanged.
4. Return to the investigation and open **Study questions…**. The first saved question should retain its original source snapshot, not your later Notes edits. Inspecting it does not replace the current investigation question or move the calendar.

## 333 — Find it later

1. Close normally and reopen the same new fixture.
2. Open **Study questions…** beside the investigation.
3. Locate the saved question and inspect the original wording/context. Return to continue current work.

No need to repeat previous tests or supply a confident market conclusion. Tell us whether parking and retrieving the question felt lighter than recording it somewhere else, and whether the retained detail would let you resume that line of inquiry. This version has no completion/archive controls or automatic launch from a queued question.
