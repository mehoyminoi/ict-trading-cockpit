# UX4d — A coherent criterion Study task

Builds on operator acceptance of 318–320, published as `2b9fca5` on the reusable-scopes branch. This slice provides one question → one retained criterion → explicit observations → explained preview → deliberate save → retained result inspection.

The Study investigation offers Evaluate a criterion for the selected quartet/reference. The dialog carries the question and task identity, asks for a retained definition, and constructs observation fields from unique input scope/key pairs. Values remain unknown until supplied. Entered values require a source and an explicitly visible available-at time in New York. The existing evaluator handles typed conditions, units, scope binding, layer applicability and information availability. A result is a criterion check, not empirical validation, an adopted AMDX judgment, competency evidence or trade authorization.

Preview writes no domain data. Editing inputs invalidates the preview. Save retains the exact preview independently of Trading Runs; subsequent inputs/results do not rewrite earlier evidence. Reading a saved result leaves current input fields unchanged and identifies the saved question/reference. Return prompts before discarding unsaved observations; changing criterion also asks before dropping unsaved entered observations. Storage failure preserves inputs and preview for deliberate retry. Unsaved observation drafts are not promised across application exit.

## Storage and compatibility

Schema 48 adds `study_criterion_evaluation`, indexed by task and protected against update/delete/replace. Its envelope retains task/plan identity, question, instrument, recording time and the original Evaluation payload (definitions, cycle, facts, availability reference, outputs and trace). Reads recompute the result and verify its retained definition against the immutable registry. Saves require an already-retained definition and refuse unrelated pending transactions. Exact retries are idempotent.

The pure Evaluation model now permits `run_id=None` for independent Study. Existing run-owned repository saves still require a real saved run; they reject independent evaluations. No fake run IDs or Trading Runs are manufactured. Existing run evaluation payloads are unchanged. Older application versions reject schema 48. Migration adds no inferred study records and preserves historical tables; synthetic v47 rollback/retry and archived migration regressions cover this boundary. Use the separate demo database for operator testing.

## Boundaries and next work

This is a single-criterion, single-reference task with multiple separately saved results. It does not implement observation import, an adopted feature vocabulary, source verification, automatic classification, criterion comparison statistics or plan publication. Empty text values are treated as unknown in this bounded UI. Conflicting types/units for the same feature require criterion revision. External fixed scopes remain explicit; reusable scopes bind only within the selected quartet.

The new `study_criterion_demo.py` seeds one synthetic question/candidate on first launch only. It uses an isolated marker-protected directory; reopening retains the task and results. No sample rule enters the regular published Trade Plan.

Operator guide 321–324 starts with where the slice fits, what it enables and what the technician should judge. Further work should follow this coherent-task approach rather than requiring disconnected infrastructure approvals.

## Verification

278 focused tests pass: 112 evaluator/AMDX persistence/reusable-scope checks; 142 historical migration, Review, context and investigation checks; 11 MainWindow/integrated Study regressions; 13 new Study/bootstrap/smoke-document checks. Tests cover saved-result replay from a reopened connection, immutable records and retries, invalid/missing source recovery, failure-retained preview, absent/future inputs, original definition retention, independent-versus-run ownership, canceled criterion switching/return, seeded demo reopening, and transactional v47→48 failure/retry. Historical migration fixtures retain their original rows; version expectations and old-reader rejection checks now target 48. Python 3.10 grammar and diff checks pass. Native dialog renders inspected at 1000×800 and 720×600. Operator 321–324 pending.
