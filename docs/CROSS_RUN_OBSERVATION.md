# Cross-Run Observation — v0 Design

**Status:** Accepted for v0 implementation  
**Milestone:** B — Review / Development synthesis

## Purpose

Competency Synthesis now makes one competency understandable across its accumulated evidence, and Development Direction records the technician's explicit next-development intent.

The remaining Milestone B gap is making **recurring patterns across runs** easier to recognize and record without pretending the Cockpit has automatically diagnosed weakness, proficiency, or readiness.

This slice should answer:

> Across the evidence I have reviewed, what recurring behavior or relationship do I believe is present?

The answer remains **human-authored synthesis**.

---

## Why this belongs before Milestone C

Evidence Maturity will eventually reason about confidence in evidence.

Before introducing that governance layer, Review / Development should already let the technician:

1. inspect individual evidence,
2. see descriptive cross-run coverage,
3. identify a recurring pattern,
4. record that interpretation explicitly,
5. connect it to Development Direction.

Without that human synthesis layer, Milestone C risks forcing governance logic to infer meaning from raw counts or Study Outcomes.

So this is the final intended Milestone B synthesis slice, not an Evidence Maturity feature.

---

## New concept: Cross-Run Observation

A **Cross-Run Observation** is a human-reviewed statement about a recurring behavior across multiple reviewed runs for one competency.

It answers:

> What recurring behavior, strength, weakness, uncertainty, or context dependency do I believe is present across these reviewed records?

Examples:

- "External draw identification is usually correct, but intermediate-liquidity classification breaks down after large expansion."
- "Session context is reliable in NYAM but inconsistent in London."
- "The apparent issue only appears in older evidence; recent Replay work does not reproduce it."
- "No stable pattern yet — evidence is mixed."

A Cross-Run Observation is not:

- a competency score,
- a Development Direction,
- a Study Outcome,
- an Evidence Maturity conclusion,
- a progression rule,
- an eligibility decision,
- an automatic machine-generated diagnosis.

---

## Relationship to existing concepts

```text
Individual reviewed runs
        ↓
Competency Evidence
        ↓
Competency Synthesis
(descriptive coverage)
        ↓
Cross-Run Observation
(human interpretation across runs)
        ↓
Development Direction
(what deliberate work to do next)
        ↓
future Evidence Maturity
(confidence/governance)
```

The relationship is intentionally not automatic.

A technician may observe a recurring pattern and still decide:

- Study,
- Rehearsal,
- Validation,
- Monitor / Gather Evidence,
- No Active Focus.

The Cross-Run Observation explains **what seems to be happening**.

Development Direction records **what to do next**.

---

## Ownership and persistence

Cross-Run Observation is mutable Review / Development state, not Trade Plan-owned definition data.

Recommended v0 record:

- Trade Plan id,
- Trade Plan revision at time of synthesis,
- competency id,
- observation text,
- optional supporting evidence IDs,
- source = Review / Development,
- created_at,
- updated_at.

One current Cross-Run Observation per Trade Plan + competency is sufficient for v0.

History/versioning of Cross-Run Observation edits is deferred unless actual use shows that preserving synthesis history is important.

---

## Supporting evidence

The technician should be able to link multiple evidence records deliberately.

The Cockpit must not automatically claim that a pattern is supported merely because several records have the same Study Outcome.

For v0:

- supporting evidence links are optional,
- linked records remain individually inspectable,
- unrelated evidence remains visible,
- support is explicit rather than inferred,
- no minimum count is required.

A Cross-Run Observation with no linked evidence is permitted, but the UI should make that state clear rather than implying evidentiary support.

---

## Revision/provenance behavior

The stable-vs-candidate Trade Plan guardrail applies directly here.

A Cross-Run Observation must preserve the Trade Plan revision under which the technician authored the synthesis.

Historical evidence keeps its own original Trade Plan revision.

Important cases:

### Same competency definition, different Trade Plan revisions

Evidence may remain comparable if unrelated Trade Plan content changed.

Do not warn merely because whole-plan revision IDs differ.

### Competency definition changed

Older evidence remains valid for the earlier definition.

It must not silently be interpreted as equivalent evidence for the revised competency.

A future definition fingerprint/revision will allow the Cockpit to make this distinction explicitly.

Until then:

- show per-record Trade Plan revision,
- preserve older evidence,
- do not auto-remap,
- do not claim a cross-definition pattern automatically.

### Newly added competency

Pre-definition evidence does not automatically count toward it.

Retrospective mapping remains explicit future analytical work.

---

## Proposed Review / Development presentation

Do not add another large permanent card.

When a specific competency is selected, extend the existing compact synthesis area with a short Cross-Run Observation section:

```text
Competency Synthesis · Draw on liquidity

Evidence coverage
Study: 4 · Rehearsal: 3 · Validation: 1

Current Cross-Run Observation
"Intermediate-liquidity classification is inconsistent
after large expansion."

Supporting evidence: 3 linked records

Development Direction
Study
```

Editing can live in a compact framed editor immediately adjacent to Development Direction, preferably reusing the existing evidence selection/list rather than creating a second evidence browser.

The page must remain scrollable and the lower Lab / Replay launcher must remain comfortably reachable.

---

## Cross-run / cross-day scope

"Cross-run" and "cross-day" should not become separate domain concepts.

The evidence already belongs to Trading Runs with timestamps. A Cross-Run Observation may synthesize:

- multiple runs on one day,
- runs across many days,
- runs across Study/Rehearsal/Validation,
- evidence before/after a deliberate training intervention.

The useful unit is:

> multiple evidence records for one competency

not a special "cross-day record" type.

---

## Descriptive helpers allowed in v0

The UI may help the technician inspect evidence with descriptive facts already available:

- evidence count,
- Study/Rehearsal/Validation distribution,
- Study Outcome distribution,
- oldest/newest dates,
- Trade Plan revision provenance.

It may also allow sorting/filtering to inspect the records.

It must not automatically surface statements such as:

- "recurring weakness detected,"
- "improving trend,"
- "regression detected,"
- "ready for validation,"
- "insufficient maturity,"

unless those statements are explicitly authored by the technician or later justified by formal Evidence Maturity/progression rules.

---

## Cross-Run Observation and Development Direction workflow

The intended operator loop is:

```text
Select competency
      ↓
Review synthesis + evidence history
      ↓
Inspect several relevant records
      ↓
Write/update Cross-Run Observation
      ↓
Optionally link supporting records
      ↓
Choose/update Development Direction
      ↓
If direction = Study:
stage targeted Study through existing launcher
```

Saving Cross-Run Observation must not start a run or change Development Direction automatically.

Saving Development Direction must not rewrite Cross-Run Observation automatically.

---

## v0 implementation boundary

If accepted, implement:

- one current mutable Cross-Run Observation per Trade Plan + competency,
- optional note/text,
- optional multiple supporting-evidence IDs,
- current Trade Plan revision provenance,
- compact display in Competency Synthesis,
- explicit human-authored label,
- evidence-link selection using the existing evidence list,
- persistence across navigation/restart,
- no schema coupling to competency state or eligibility,
- focused tests and smoke-test coverage.

Do not implement:

- automatic pattern detection,
- trend scoring,
- NLP/category extraction from notes,
- automatic Development Direction suggestions,
- automatic competency-state transitions,
- Evidence Maturity,
- progression policy,
- eligibility changes,
- cross-competency pattern mining,
- dashboards,
- retrospective remapping.

---

## Milestone B exit criterion

Milestone B can be considered complete when Review / Development supports the full human synthesis chain:

```text
Evidence
  ↓
Descriptive competency synthesis
  ↓
Human Cross-Run Observation
  ↓
Human Development Direction
  ↓
Targeted Study routing when needed
```

At that point Milestone C can introduce Evidence Maturity/governance over a Review layer that already distinguishes:

- raw evidence,
- descriptive aggregation,
- human interpretation,
- next-development intent.

---

## Operator confirmation questions

1. **Resolved:** use **Cross-Run Observation**. The term avoids conflating evidence-synthesis patterns with retail-style market-pattern hunting.
2. Is one current mutable observation per competency sufficient for v0?
3. Should supporting evidence be optional, as proposed?
4. Does it make sense that Cross-Run Observation says "what seems to be happening" while Development Direction says "what should I do next"?
5. Is the proposed boundary enough to close Milestone B after implementation?


## Operator acceptance

Accepted on 2026-10-09.

Confirmed:

- **Cross-Run Observation** is the preferred term.
- One current mutable observation per competency is sufficient for v0.
- Supporting evidence remains optional.
- Cross-Run Observation means **what seems to be happening**.
- Development Direction means **what should I do next**.
- This slice is sufficient to close Milestone B after successful implementation and acceptance.
- The distinction intentionally supports the operator's IF/THEN reasoning style without turning the observation into an automatic rule.
