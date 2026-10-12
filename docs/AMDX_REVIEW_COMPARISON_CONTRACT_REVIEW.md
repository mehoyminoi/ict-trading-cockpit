# AMDX Review — containing-cycle comparison contract

**Status:** concrete recommendation for operator review, prepared 2026-10-12 after acceptance of working-quartet checks 251–254. Operator clarification on 2026-10-12 confirms that comparison/history belongs in later purposeful Review/Study. Watch shows the current working stack and position, without a visible revision history or comparison of stack changes. The first-versus-latest default remains a proposal; this placement clarification does not select it or authorize observed-entry implementation.

**Implementation boundary:** `AMDX_REVIEW_FOUNDATION_GUIDE.md` documents the new pure explicit-pair/archive action. It requires a supplied expected basis or explicit None; it adopts no baseline default. Database integration is now implemented in `AMDX_REVIEW_PERSISTENCE_GUIDE.md` at schema v40; UI integration remains downstream. The earlier proposed flow below remains historical context. `AMDX_REVIEW_INTERACTION_CONTRACT_REVIEW.md` is the current concrete recommendation: routine observed entry has no automatic first/latest pairing, and an explicitly opened comparison is optional. That recommendation and one-entry observed correction remain unaccepted until operator review.

**Verified initial application baseline:** source `84167e9bec21189a6bca08e2206a191665df0caa`, 587 automated PASS, schema v39, Alpha 0.7. PR #61 and stacked PR #62 are ready for review and unmerged. The existing Market Review AMDX panel is read-only. Immutable claims, separate channels and explicitly based criteria evaluations exist; an evaluation basis is not an implemented Review comparison pair.

## 1. Proposed later Review flow

Review should retain the technician's observed interpretation of an identified containing quartet separately from the working expectation. Observed AMDX is still a judgment with a rule/input basis, not an objective price fact or a correctness verdict.

Within an intentionally opened Review comparison, recommend showing the **first explicit expected profile** as the initial comparison baseline, with the latest working profile nearby as context. These historical views do not belong on the normal Watch surface and need not be permanently visible in Review either. When the technician records an observed profile, capture the identified baseline automatically with that action. No additional Save, confirmation or obligatory baseline-selection step. Selecting an alternate baseline is optional and remains easy to reach.

The baseline identifies the entire cycle-profile claim, not only the quarter used to enter it. The view can explain the entered anchor, implied quartet and X subtype. Unknown or Not Applicable is not silently skipped to choose a more convenient baseline. The first explicit expected claim may be unresolved or inapplicable; retain that meaning and show why it is not comparable.

The first claim is not necessarily a prediction made before the cycle. Display its explicit market reference as before, during or after the containing cycle; retain recording time separately. Missing legacy timing remains unknown. No percentage, correct/incorrect badge or automatic competency evidence follows from the comparison.

## 2. Concrete cases

Use one Day quartet for the examples. E1/E2 identify immutable expected claims; O1 identifies a separately accepted observed claim.

| Recorded history / action | Proposed Review meaning |
| --- | --- |
| Before the day, E1 uses Q3=D: AMDX with X(?). During the day, E2 uses Q3=M: XAMD with X(?). Afterward, O1 is XAMD. | First comparison is E1 AMDX versus O1 XAMD. E2 remains adjacent as the revised working expectation; neither claim is overwritten or graded. |
| Technician chooses E2 as an alternate comparison. | Persist a new comparison revision identifying E2 and O1. Preserve the earlier E1/O1 pair; changing the comparison does not require re-entering O1 or invent a new observation. |
| A later working claim E3 is accepted after O1. | E3 does not silently change either saved comparison. Inspecting E3 alone creates no new claim or pair. |
| No expectation exists when O1 is recorded. E1 is entered later. | O1 initially has no expectation baseline. E1 does not attach retroactively; an intentional later comparison must show that the expectation was recorded later. |
| The first expectation is entered during the day. | It can be the first baseline, but is labeled During cycle. Do not present it as pre-cycle anticipation or imply an earlier known forecast. |
| Expected and observed order match, but expected X is X(?) and observed X is X(R). | Order agreement is descriptive; expected subtype was unresolved. Do not report a predicted reversal or a fully matched quartet. |
| Either profile is unresolved, conflicting or Not Applicable. | Preserve each state and basis; report the applicable comparison limits. No forced winner, completed classification or correctness score. |

## 3. Shared-action and ownership boundaries

- Persist run, cycle, expected-claim ID (nullable), observed-claim ID, comparison revision, rule/input basis and action/reference timing. Expectation and observation must identify the same containing cycle and an explicitly compatible scope; do not pair unrelated days, levels, branches or runs by label alone.
- An observed interpretation never retires or rewrites expected anchors. Original claims and immutable structural-policy semantics remain reconstructable.
- Initial observation plus its initial comparison selection commit atomically. A later comparison revision references existing profiles rather than changing their payloads. Preserve command identity, exact retries, stale-head protection and visible failure handling.
- Inspection, clock movement and default-candidate display create no observation or comparison record. Accepted input saves immediately; navigation cannot retarget an active edit.
- Watch presents the current working stack and current temporal position. Earlier expectations, change comparisons and historical lists belong in intentionally accessed contextual Review/Study detail. A latest-versus-first display is a proposed Review view only, not a Watch obligation.
- Study may inspect alternate pairings with their recorded basis. This contract adds no sensor, phase classifier, P&L attribution, gate, completion rule or published Trade Plan definition.

## 4. Earlier default proposal — superseded recommendation

**Recommendation for an intentionally opened Review comparison:** first explicit expected profile is the default baseline; latest working expectation can appear beside it within that comparison. An observed entry records that pairing automatically, and optional alternate comparisons preserve the original.

**Open choice:** does that preserve the distinction you want between initial anticipation, an adapted working hypothesis and the eventual observed interpretation? The alternative is to default to the latest expected profile available when observation is entered, while keeping the first beside it. Neither default is adopted until reviewed.

Exact observed-entry gestures, comparison layout and the persistence implementation follow this decision. Final rendering must retain the accepted primary 16:9 orientation/detail relationship and direct one-click X(C)/X(R) input; no new mandatory baseline click is introduced.

## 5. Later research on why interpretations change

The operator’s example is an investigation such as “AMDX changes tend to follow this price-action event, or the technician noticing this feature.” Preserve the underlying revisions now; do not add a live change-history display to support that future question.

Later aggregation should connect identified interpretation changes with explicitly recorded event/observation context and the applicable rule/Trade Plan revision. Event time, when the technician noticed it, the revision’s market reference and recording time are different facts; do not invent any missing timing or assume temporal proximity is an explanation.

Feature definitions, sample selection, comparison groups and treatment of missing records must be specified before displaying a frequency or likelihood. Results describe evidence-backed associations; they do not assert causation or automatically become a trading rule. The current slice implements neither these links nor the aggregation. Capturing research context must not impose a new explanation, confirmation or checklist step on routine Watch entry.
