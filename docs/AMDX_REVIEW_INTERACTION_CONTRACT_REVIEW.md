# AMDX Review interaction — concrete cases

**Status:** the operator accepted both principal behaviors on 2026-10-12: independently versioned one-entry observed correction and optional comparison with no automatic first/latest pairing during routine capture. Comparison is lower priority and deferred until a concrete Study/Review need arises. It has no entry point in Watch. These are accepted behavioral directions. The v41 action in `AMDX_OBSERVED_REVISION_GUIDE.md` now implements observed revision and durable no-op/retry behavior; native Review binding remains downstream.

**Verified baseline:** `dfb5effb0fb185fe156f2e63a3392eed8975c53b`, source `e61c1aa5d27d20880adc476ef007328c89771001`, 658 automated PASS, schema v40, Alpha 0.7. Draft PR #64 is stacked on unmerged #63. The coupled AMDX panel is read-only in Market Review; legacy flat observed fields retain their existing action. Explicit pairing storage exists, but no coupled observed editor/comparison view is wired into the application.

## 1. Routine observed entry

Review answers “How do I interpret this quartet after examining it?” The observed interpretation stays independent of the working expectation. It is still technician judgment, with source/rule context; it is not an objective price fact or a correctness grade.

Recommend selecting the containing cycle and making one valid phase/subtype choice. The whole observed quartet changes immediately and saves automatically, without a separate Save, confirmation or requirement to fill every sibling quarter. A correction uses another valid choice, preserving earlier observations rather than locating/clearing an old contradictory anchor. Use the same structural limits and subtype/Unknown/applicability/clear/no-op effects accepted for working entry, within an independently versioned Observed action.

Inspection is explicitly about the run/cycle being reviewed. It must not follow today's live clock into a different day or retarget an open gesture. Child quartets remain independent. Existing working context is available for orientation, clearly distinguished from the observed judgment; it does not prefill or certify an observation automatically. Unsupported higher-order cycle identities remain legacy context until mapping is defined.

## 2. Comparison is purposeful exploration

Recommend **no automatic first/latest comparison for initial observed capture**. Record the observation with no expectation selected. Comparisons are available when deliberately opened in Review/Study, rather than occupying the normal Watch surface or becoming a required Review task.

“No comparison selected” means no basis was chosen; it does not mean no expectation exists. A missing expectation and an available-but-unselected expectation can both have a null saved basis, while the UI explains the actual available context. Later expectations do not attach retroactively.

An intentionally opened comparison offers identified expectations, including first recorded and latest working, with timing and rule/input basis visible in that detail. Browsing previews a candidate without creating a pairing. Deliberately choosing a basis saves an explicit comparison revision automatically. No separate Save/confirmation step. Selecting another basis preserves the original pairing and the same observed claim.

For corrections to the same observed cycle, retain its last deliberately selected comparison basis, if one exists. Do not silently switch to a newer expectation. If no basis was chosen, keep it unselected. An intentional clear of comparison selection records a new null-basis pairing; subsequent corrections retain that unselected state. A new cycle inherits neither the observed profile nor a comparison choice from another cycle.

The operator’s subsequent acceptance supersedes the earlier automatic-first pairing proposal: routine capture uses no automatically selected expectation. Optional comparison remains lower priority and belongs only in Study/Review when needed. First/latest remains an optional identified research choice, with no routine default proposed here.

## 3. Before/action/after cases

| Situation / action | Proposed result |
| --- | --- |
| Open Review for the run's Day quartet; only a working expectation exists. | Working context remains available; Observed is not recorded. Opening/navigation creates no observation or comparison. |
| Choose observed Day Q3=D. | Observed AMDX with X(?) records immediately. Working stack is unchanged. No comparison selected; no extra click is required. |
| Correct observed Q3 to M. | Observed becomes XAMD in one entry. Earlier AMDX remains historical; no anchor-cleanup step and no change to working expectation. |
| Choose X(R) at the observed quartet's valid X position. | One deliberate subtype entry updates that observed quartet. Identical already-explicit entry is a no-op; parent/child quartets and process completion stay separate. |
| Open Compare and browse E1 / E2 without accepting either. | Preview only; original observation, pairing and selection are unchanged. |
| Deliberately choose E1, then later choose E2. | P1 identifies E1/O1; P2 identifies E2/the same O1. P1 and both expectations remain retained. No observation re-entry or Save is needed. |
| Correct O1 to O2 after selecting E2. | New observation and pairing commit together, retaining the deliberate E2 basis. E1/O1 and E2/O1 remain historical. Later E3 does not retarget them. |
| Clear comparison selection, then correct the observed profile. | New null-basis comparison preserves earlier selections; the correction remains unselected, without a first/latest fallback. |
| Choose Unknown / Not Applicable / clear. | Preserve the working-policy distinctions within the separate Observed action. Conditional implied roles remain explicit; clearing does not resurrect retired anchors. Comparison limits remain honest. |
| Database failure or a stale observed/comparison head occurs. | No partial observation/pair is accepted. Keep the attempted target/choice visible for deliberate recovery; no false success, automatic replay or process completion. |

## 4. Implementation boundary

The v40 backend can already retain explicit and null pairings, alternate selections, exact retries and atomic observed-claim/pair writes. It currently accepts Observed `accumulate-v1` actions. The later v41 action now implements the accepted one-entry observed replacement/no-op/applicability flow; see `AMDX_OBSERVED_REVISION_GUIDE.md`. Existing v40 accumulation records retain their original policy.

Implement the accepted behavior through a named versioned Observed action with preserved original accumulation replay and migration/receipt compatibility before connecting controls. Current Expected `revise-working-v1` remains separate. No existing observation is reinterpreted as having used the new policy.

**Native follow-up implemented:** `feature/amdx-observed-entry-v1` now binds the accepted action in Post-Market Review with saved reviewed-day targets, all-session access, immediate capture, direct X(C)/X(R), stale/failure/read recovery and restart. See `AMDX_OBSERVED_ENTRY_OPERATOR_GUIDE.md`; new checks 255–259 await operator acceptance. This adds no comparison controls or Watch route and changes neither schema v41 nor Alpha 0.7.

Application binding must respect existing run/process permissions, save only deliberate accepted actions, pin cycle/reference/basis through a gesture, and restore committed meaning after restart. Observation/pair transactions never certify Review or update competency/authorization state. Free-text note drafts remain separate unimplemented work; phase entry must not wait for a note.

Final primary 16:9 rendering, quiet whole-stack orientation, direct one-click X(C)/X(R) and future keyboard/macro-pad adapters remain shared requirements. This contract chooses behavior, not a final control arrangement. Event/change aggregation remains later research with defined context and samples.

## 5. Two decisions

1. **Observed revision:** use the same efficient one-entry quartet correction semantics as Watch, independently versioned and preserving earlier observed history.
2. **Comparison:** routine observed entry has no automatic first/latest pairing; explicitly opened comparison is optional, and a deliberately selected basis carries through corrections of that same cycle until cleared/changed.

Both principal behaviors are accepted. Comparison controls and further comparison-focused work are deferred until Study/Review use demonstrates a need. Do not add a Watch comparison option, history panel or launch route. Prioritize efficient AMDX entry and current-stack orientation. No new source, schema, UI or smoke status is changed by this acceptance record.
