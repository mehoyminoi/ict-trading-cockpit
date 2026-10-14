# Lab AMDX calendar and feature-tree operator review

**Reviewed:** 2026-10-14 (America/Denver)  
**Artifact reviewed:** `prototypes/lab-amdx-calendar-tree-v0.html`, first and second iterations; the same file now contains the unreviewed third iteration
**Disposition:** Successful direction with continuing multiscale refinement. The three-pane relationship and Quiet/Nested/Deep configuration are retained; exact hierarchy encoding and temporal zoom remain open.

## Directional successes

- The feature tree, central workspace and right detail rail feel coherent together.
- **Follow Current** is useful and should remain explicit.
- Missing entries are handled correctly when they remain visibly unavailable rather than borrowing or guessing data.
- The October month view is a strong direction: a real month calendar makes temporal structure and restrained news cues easier to understand.
- The overall trial is a meaningful step toward the spacious Lab experience.

## Missing calendar behavior

The month workspace needs familiar calendar movement rather than requiring tree-only navigation:

- previous/next month;
- direct month and year selection;
- a clear route back to the current reference;
- visible week Q1–Q4 identities and explicit distortion-week treatment.

True year, month, week and day opens are important adjacent context. The technician should be reminded when an applicable true open needs marking. The UI should distinguish **needs marking**, **recorded** and **unavailable** without guessing a price. True opens are instrument/time/price facts with provenance; they should appear cohesively with AMDX while remaining a separate ownership concept from AMDX interpretation.

## Multiscale context requirement

The first iteration changes the selected temporal level but still compresses most higher layers into one generic row. That does not use the spacious canvas or show enough of what lies inside the selection.

Two independent positions are required:

1. **Temporal selection** — which period is the working level.
2. **Context depth** — how many ancestor and descendant levels are visible without changing that selection.

For example, a selected month may retain its position inside the yearly quarter/year/quadrennial/16-year chain, display week structure and daily roles, and optionally expose compact session quartets inside each day. A deeper selected-day treatment may reveal the relevant 90-minute structure. This is an experiment, not a decision to display every descendant permanently.

The next prototype should test Quiet, Nested and Deep context modes. Compact descendants should use an ordered visual grammar—session slots, role letters where space permits, selection and entered/implied cues—rather than paragraphs inside calendar cells.

## Level-specific workspace requirement

Higher levels should use the center area according to their natural child structure:

| Selected level | Expected spatial content |
| --- | --- |
| 16-year | Four quadrennials and the selected descendant route |
| Quadrennial | Four years and their retained stack-up |
| Year | Twelve months grouped into four yearly quarters |
| Month | Real calendar, week quartet/distortion, news and true opens; optional day/session depth |
| Week | Trading Days, their quartet identities and true week open |
| Trading Day | Four sessions and true day open |
| Session | Four 90-minute cycles |
| 90-minute | Quartet detail, definitions, provenance and entry |

This replaces the idea that one generic four-card row can represent every higher level.

## Lab scope guardrail

Lab must not become an AMDX-only application. **AMDX Calendar** is the first foundational analytical lens, not Lab's identity. Mature Lab remains the broader Study workspace for questions and competencies, chart/screenshot evidence, news and true opens, price-action/model context, criteria and definition research, historical/forward samples, Study Finds, aggregation, Review and Development Direction.

The lens should therefore be named in the shell. Future lenses can share the tree/workspace/support-rail grammar without being forced into AMDX ownership.

## Acceptance boundary

This review accepts the three-pane relationship, Follow Current, truthful missing-state behavior and real month-calendar direction. It does not accept final density, calendar controls, tree width, higher-level rendering, true-open workflow, descendant encoding, styling or native implementation.

The next trial may test the refinements above without creating production persistence, a true-open repository, a market-data feed, new news acquisition or a final Lab navigation system.

## Second-iteration operator review

The Quiet/Nested/Deep distinction is a good configuration even though the content at each depth still needs refinement. Month/year controls and the higher-timeframe breadcrumb/context spine are useful. The following corrections govern the third iteration.

### Meaning before color

The colored Q1–Q4 borders across every day in a monthly row add ordinal color without adding enough analytical meaning. They are removed from the month projection. Month weeks should instead be divided spatially with a light neutral rail at the left:

- **Quiet:** physical week grouping only; no weekly or daily AMDX labels;
- **Nested:** neutral week heading with its actual quartet value plus compact daily quartet values;
- **Deep:** the same semantic values plus interval and session detail.

This correction narrows the earlier request for yellow/red/green/blue quarter color. Those colors remain available where they encode a session identity or other useful distinction, but are not a requirement on every Q1–Q4 occurrence. Text, order, grouping and shape should carry the hierarchy before color is introduced.

### True-open placement and reminder ownership

True year/month/week/day opens should appear at the period's actual calendar position rather than as a prominent generic banner. Lab may inspect and edit the fact. When Cockpit knows a true open needs attention at the current time, the process reminder belongs in TDA. Mature display policy may allow individual cues, colors and reminders to be hidden or shown without creating separate data ownership.

### Workbench/lens navigation hypothesis

The **AMDX Calendar** selector suggests a useful Fusion 360–like workbench model: TDA, Watch, Lab and Review can retain a coherent shell while exposing tools appropriate to the current operation, and Lab can contain analytical lenses such as AMDX Calendar. This is a promising navigation motif to preserve lightly, not a final taxonomy or control decision.

### Remaining open interaction

Temporal zoom feels better when it is independent from context depth, but it still does not feel settled. Do not infer acceptance of the current Zoom In/Out controls, labels, direction, selection-following behavior or gesture. More experimentation is expected because full-stack AMDX movement is both complicated and foundational.

The third iteration may test these corrections while retaining the accepted three-pane relationship, Follow Current behavior, truthful missing state and broader-Lab scope guardrail.

