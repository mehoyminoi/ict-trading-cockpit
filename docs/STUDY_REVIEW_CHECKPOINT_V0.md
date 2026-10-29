# Investigation review checkpoint — proposed next slice

Prepared 2026-10-29 after operator acceptance of capture checks 343–344. This is a design/inventory checkpoint; no review UI or persistence is implemented by this document.

## Purpose and practical workflow

At a natural pause in an investigation, open the existing investigation overview. Inspect the linked captures, criterion results and findings, then retain a concise review:

1. **Current understanding** — What did I learn, or how did my interpretation change?
2. **Uncertainty / counterexamples** — What remains unexplained or conflicts with that interpretation?
3. **Next study step** — What concrete observation or practice would help resolve the gap?

These are working prompts, not a mandatory three-field questionnaire. Require some review content to save, but allow uncertainty or a next question without an asserted conclusion. A checkpoint does not finish the investigation. The technician can return to studying immediately, preserving the current question, reference and unfinished capture.

## Existing architecture and missing capability

- `StudyInvestigationOverview` already composes explicitly associated saved captures, linked drafts/unavailable-capture receipts, criterion results and findings. Extend this surface rather than create a competing dashboard.
- `StudyFindingRepository` retains individual interpretations and optional partial answers. A review synthesizes across material; it must not silently edit or reclassify those records.
- `IntegratedStudyTaskWidget` retains the current investigation identity/question in workspace settings. It is not a multi-investigation registry. The first slice must not claim a general historical investigation browser.
- `CompetencyEvidence` requires `trading_run_id`. Independent calendar investigations must not manufacture a run to satisfy that contract.
- `CompetencyDevelopmentDirection` and competency assessments concern a selected competency and reviewed evidence. An investigation's next-step note is not an automatic competency Development Direction or state change.

## Proposed first implementation contract

Add an investigation-owned review record, separate from competency evidence. Retain stable review identity, task/plan identity, plan revision, the question as reviewed, recording time, the three optional narrative fields and explicitly selected supporting material.

Saving a review does not make every item in the investigation support the conclusion. Selected references need source type and identity; retain enough source detail/revision to reconstruct the reviewed basis. Saved Study Finds, finding snapshots and criterion receipts can be cited. Linked unfinished drafts remain inspectable but should not silently become stable support: require saving the capture first or explicitly snapshotting draft state in a separately specified future extension. Unavailable records must be labeled unavailable, not treated as evidence of absence.

First slice: saved review checkpoints are immutable; later reviews append a new checkpoint rather than overwrite the old interpretation. Load latest/history by exact plan and task identity, show original reviewed question/revision, and keep source references inspectable. Editing a review before save is a local draft with cancellation protection; storage failures preserve input. Duplicate-click/retry handling must not append duplicate checkpoints.

Place review writing beside inspectable investigation material, with optional supporting-item selection. Avoid forcing the technician to reconstruct context from memory or use a second disconnected form. Saving should confirm quietly and leave a clear return to work. Exact pane arrangement and prompt wording remain provisional.

## Example (illustrative, not a market conclusion)

Current understanding: “The London interpretation was plausible from what I had seen then, but NYAM forced a revision.”

Uncertainty: “I have not established which distinguishing information was available before NYAM.”

Next study step: “Inspect another comparable day in chronological replay and record the London interpretation before revealing NYAM.”

The review may explicitly cite a capture and partial answer. It does not declare either interpretation objectively correct or claim competency improvement from one example.

## Relationship to the longer learning loop

The first checkpoint closes capture → inspect → synthesize → resume. A later explicit handoff can associate relevant competency/definition revisions and reviewed performance with the existing evidence machinery. That handoff requires its own provenance and run-independent evidence design; it is not a hidden side effect of Save review.

Rule usefulness and operator proficiency stay distinct. Evidence maturity, Trade Plan progression policy and eligibility remain separate. No automatic readiness score, completion, promotion, policy adoption or new run is introduced.

## Acceptance criteria for implementation

- A technician can inspect selected source material while recording a tentative understanding and remaining uncertainty.
- Saving/reopening retains exact review content, question/revision and selected source basis.
- Later source additions or a changed working question do not rewrite older reviews.
- A later checkpoint preserves the earlier one; retries do not duplicate it.
- Cancel/save failure protects input; returning preserves calendar, task and unfinished capture.
- No competency state, evidence, eligibility, run or source association is created implicitly.

No new operator smoke test is requested at this design checkpoint. After implementing this bounded review loop, use one brief real-study review to assess whether it helps decide what to do next before adding further fields or analytics.

## Implementation follow-up

Operator accepted this direction with emphasis on optional prompts and simultaneous outcomes. First local implementation and trial scope are documented in `STUDY_REVIEW_OPERATOR_GUIDE.md`. The above design remains the rationale; the operator guide states implemented limitations.
