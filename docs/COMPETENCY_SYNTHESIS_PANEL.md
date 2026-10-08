# Competency Synthesis Panel — v0 Design Candidate

**Status:** Design candidate for operator review
**Milestone:** B — Review / Development synthesis

## Purpose

Development Direction now captures the technician's explicit next-development intent. The next useful Review / Development surface should help the technician understand one competency across multiple evidence records without turning descriptive data into an automatic recommendation.

The design target is a compact **Competency Synthesis** panel that answers:

> What does the accumulated evidence say, what have I decided to work on next, and what remains unknown?

## Guardrail

The synthesis panel is descriptive first and interpretive only where the technician has explicitly recorded an interpretation.

It must not convert counts, Study Outcomes, or environment distribution into:

- proficiency scores,
- automatic Development Directions,
- automatic Competency State changes,
- Evidence Maturity conclusions,
- progression or eligibility decisions.

## Proposed panel structure

For one selected competency:

1. **Competency identity**
   - name
   - category
   - current Trade Plan revision

2. **Current Development Direction**
   - direction
   - synthesis note
   - supporting-evidence count
   - explicit human-authored status

3. **Evidence coverage**
   - total reviewed evidence count
   - count by purpose: Study / Rehearsal / Validation
   - count by Study Outcome
   - oldest/newest reviewed evidence timestamps

4. **Evidence history**
   - current human-readable record list
   - selected record detail/provenance

5. **Known / Unknown boundary**
   - explicit reminder that descriptive coverage is not Evidence Maturity
   - no claim that missing Validation evidence means failure; it means that evidence has not been recorded here

6. **Next action**
   - if Development Direction = Study, expose the accepted Study staging action
   - otherwise show the current direction descriptively
   - do not add Rehearsal/Validation launch routing in this slice

## Why this is useful

Today the operator can inspect evidence and separately save a Development Direction. The next step is to place those concepts into one competency-level reading surface so Review / Development becomes easier to reason about across runs.

Example:

```text
Draw on liquidity

Development Direction
Study
"Intermediate-liquidity classification remains inconsistent after expansion."

Evidence coverage
7 reviewed records
Study: 3
Rehearsal: 3
Validation: 1

Reviewed outcomes
Supported: 2
Refined: 3
Practice Complete: 2

Supporting evidence
3 linked records

Interpretation boundary
Coverage is descriptive. No proficiency, maturity, or eligibility conclusion is inferred.
```

## Important distinction: coverage vs maturity

Evidence coverage answers:

> What evidence do we currently have?

Evidence Maturity will later answer:

> How much confidence should we place in that evidence for a particular governance decision?

Those are not the same.

For example, seven records across three environments may still be poor evidence if they are stale, narrow, contradictory, or tied to an old Trade Plan revision. Therefore v0 must not label coverage as strong/weak/mature/immature.

## Important distinction: human synthesis vs machine suggestion

The current Development Direction remains the authoritative synthesis statement because the technician explicitly authored it.

The panel may show descriptive facts adjacent to that direction, but must not imply:

> The Cockpit recommends Study because 3 of 7 outcomes were Refined.

That kind of inference belongs later, if ever, and would require explicit rules and evidence governance.

## Revision handling

The panel should make Trade Plan revision context visible enough to prevent accidental cross-revision interpretation.

v0 recommendation:

- show the active/current Trade Plan revision for the competency definition,
- retain per-evidence revision in record detail,
- show a warning only if displayed evidence includes more than one Trade Plan revision,
- do not automatically exclude older evidence yet.

This preserves historical visibility without silently treating old and new definitions as equivalent.

## UI constraint

Recent testing showed that Review / Development can become vertically overloaded.

Therefore this slice must not add a tall new card beneath the existing evidence editor.

Recommended presentation:

- one compact competency-level synthesis header above the evidence history,
- reuse existing counts rather than duplicate them in multiple widgets,
- keep the page vertically scrollable,
- avoid expanding explanatory text by default,
- preserve the Lab / Replay launcher below without crushing its Competency Focus controls.

## Proposed v0 implementation boundary

If accepted, implement only:

- competency-specific synthesis view when a competency is selected,
- current Development Direction + note + linked-evidence count,
- descriptive evidence coverage by purpose and outcome,
- oldest/newest reviewed evidence timestamps,
- mixed-Trade-Plan-revision warning when applicable,
- explicit 'descriptive only' language,
- reuse existing evidence history and Study routing.

Do not add:

- derived scores,
- trend arrows,
- strength/weakness labels,
- automatic recommendations,
- Evidence Maturity labels,
- Competency State editing,
- progression criteria,
- Rehearsal/Validation routing.

## Operator confirmation questions

1. Does **Competency Synthesis** feel like the right name for this compact competency-level reading surface?
2. Is evidence coverage by purpose/outcome useful without feeling like a scorecard?
3. Should mixed Trade Plan revisions trigger a visible caution in v0?
4. Is it correct to leave older-revision evidence visible rather than filtering it automatically?
5. Should the panel show oldest/newest evidence dates, or is that unnecessary detail at this stage?
6. Does the proposed compact/header-style presentation feel like the right response to the recent vertical-space problem?
