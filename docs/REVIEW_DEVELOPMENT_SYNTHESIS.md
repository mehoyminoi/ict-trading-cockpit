# Review / Development Synthesis — v0 Design Candidate

**Status:** Accepted for v0 implementation
**Milestone:** B — Review / Development synthesis

## Purpose

Milestone A now closes the first operator-facing loop: competency focus -> deliberate run -> reviewed evidence -> inspect evidence -> route back to targeted Study.

The next problem is synthesis: how should the Cockpit help the technician identify a recurring development need across multiple evidence records without silently turning Study outcomes into proficiency scores?

## Key guardrail

Do not infer weakness from Study Outcome alone. Refined, Inconclusive, Supported, or Rejected describe what happened in one inquiry; none of them is a hidden competency score.

## Proposed concept: Development Direction

A Development Direction is an explicit human-reviewed statement answering: What deliberate work should I do next for this competency, based on the evidence I have reviewed?

It is separate from:
- Competency Definition — what skill matters
- Competency State — where the skill currently sits in the training ladder
- Competency Evidence — the underlying reviewed observations
- Evidence Maturity — future confidence/governance over the evidence
- Eligibility — whether the Trade Plan permits a higher operating level

## Candidate directions

- Study
- Rehearsal
- Validation
- Monitor / Gather Evidence
- No Active Focus

These are action-oriented development directions, not proficiency levels.

## Minimal candidate record

- trade_plan_id
- trade_plan_revision
- competency_id
- direction
- note
- optional supporting_evidence_ids
- created_at
- updated_at

## Proposed workflow

Review / Development -> select competency -> inspect evidence across runs -> operator sets Development Direction -> optional note/supporting evidence -> persist -> offer an appropriate explicit staging action.

For v0, only Study needs an active routing behavior because Study this competency already exists. Rehearsal and Validation can remain descriptive until their routing semantics are deliberately implemented.

## Why this is separate from Competency State

Example: Competency State may be Rehearsal Needed while a new Replay error reveals a component problem that should be isolated in Historical Study. The Development Direction can therefore be Study without automatically rewriting the broader competency state.

## Recurring weakness

Initially, recurring weakness remains a human interpretation boundary:

multiple evidence records -> human notices pattern -> human records Development Direction + note.

Later analytics may surface candidate patterns, but v0 should not claim the machine discovered a weakness.

## Revision semantics

Development Direction is mutable technician/review state, not Trade Plan-owned definition data. It should still preserve the Trade Plan revision under which the synthesis was made so later definition changes do not rewrite history.

## Recommended v0 boundary

If accepted, implement only:
- one current mutable Development Direction per Trade Plan + competency
- optional human note
- optional supporting evidence links
- Review / Development editor/display
- no automatic derivation
- no automatic competency-state transition
- no eligibility change
- no Evidence Maturity logic
- reuse Study this competency when direction = Study

## Operator confirmation questions

1. Does Development Direction describe the concept clearly enough?
2. Are Study, Rehearsal, Validation, Monitor / Gather Evidence, and No Active Focus the right initial directions?
3. Should a direction be allowed without linking specific evidence records?
4. Should v0 keep one current mutable direction per competency, with direction history deferred?
5. Does this separation feel correct: Study Outcome = what this run taught us; Development Direction = what to work on next; Competency State = broader training-ladder state; Evidence Maturity = future confidence/governance layer?


## Acceptance

Accepted by the operator on 2026-10-08.

The distinctions and guardrails in this note are intentional and should be preserved during implementation. In particular:

- Development Direction is human-reviewed synthesis, not machine inference.
- Study Outcome must not be repurposed as a hidden proficiency score.
- Development Direction must not automatically mutate Competency State.
- Development Direction must not make an Evidence Maturity or eligibility decision.
- One current mutable direction per competency is sufficient for v0; historical direction changes are deferred.
- Supporting evidence links are optional in v0.
