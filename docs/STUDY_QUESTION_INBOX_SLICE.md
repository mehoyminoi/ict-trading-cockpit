# Study follow-up question inbox — first increment

Capture-context operator rechecks all PASS. The operator endorses the context mismatch notice as quiet, metered guidance; keep it persistent without adding modal warnings or decorative urgency.

The next concrete need comes from the London → NYAM research question: retain a useful tangent while continuing the current investigation. This first increment provides **Keep question for later…** in Study Find and **Study questions…** beside the investigation. The inbox lists saved questions for the current Trade Plan across investigations and plan revisions. It is not AMDX-specific.

Select wording in Notes or Observation, then open the capture action. The composer starts with selected text (Notes selection takes precedence if both editors retain selections); no selection opens a blank question. The operator can refine it while the exact original wording is retained separately. Saving snapshots the capture identity, draft/saved state, date, instrument, session, pattern, observation, notes, chart paths and existing explicit investigation association. An unlinked capture stays explicitly unlinked; date similarity and navigation do not invent an association. Source edits made later do not rewrite the question. Chart paths remain references to existing managed files, not duplicate image copies or guaranteed permanent external links.

Saving keeps the dialog open with confirmation and the retained question visible. Return/Escape preserves the source form, active investigation and current calendar. An unsaved nonempty question asks before discarding; save failures preserve text for explicit retry. The inbox is readable after restart. This increment does not automatically select a new investigation, launch a run, mark questions completed, edit saved questions, rank work or award evidence/competency. Retrieval and return are the bounded first step; deliberate task promotion can follow actual use.

## Storage

Schema 49 adds an immutable `study_question` snapshot table keyed by question identity and indexed by plan identity. UPDATE/DELETE/REPLACE are rejected; identical save retry is a no-op. No run or saved capture is required because an unfinished source can be snapshotted independently. Source association, when present, retains its saved question/reference. New question recording time is aware actual time, not the historical reference. No historical questions are backfilled. The upgrade remains in the existing all-migration rollback boundary; old schema-48 readers reject 49.

Use a new separate demo directory for the trial. Do not upgrade the operator's regular database for this test. Reopening this new fixture needs the schema-49 branch; earlier branches cannot open it.

## Verification

Focused tests cover immutable save/reopen and plan filtering, migration failure rollback, unsaved cancel, save failure/retry, original versus refined wording, source snapshot independence and native routing that preserves the current capture/question. 224 distinct focused tests PASS across the new inbox, database/migration, Study and MainWindow checks. Eight older migration assertions initially expected schema 48; after updating those terminal-version assertions, all eight pass at 49 while retaining their preservation/rollback checks. The four inbox and four smoke-document checks were repeated after the retry handling change. Native rendering inspected at 850×700 and 760×600; Python 3.10 syntax and diff checks pass. Operator 331–333 pending; see the guide.
