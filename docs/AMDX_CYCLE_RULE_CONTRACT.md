# AMDX / XAMD cycle and rule contract

**Status:** Operator clarification recorded/reviewed on 2026-10-11; corrected architectural design. The operator authorized proceeding with the foundation. `AMDX_FOUNDATION_GUIDE.md` records the pure domain/action/archive implementation; actual price-classification criteria and production rendering remain open.
**Baseline:** accepted E7 used schema v37 / Alpha 0.7. The first domain foundation left that schema intact; the subsequent `AMDX_PERSISTENCE_GUIDE.md` implements additive v38 storage. Alpha 0.7 and existing QT surfaces remain unchanged; no legacy interval history is invented.
**Why this correction matters:** the earlier prototype treated individual quarter values too independently. A four-quarter profile is a coupled interpretation: one accepted quarter assignment constrains the other roles within that same quartet. This changes the interpretation/history unit and must be reflected before persistence/action implementation.
**Operator review:** document reviewed on 2026-10-11. `AMDX_RULE_DEFINITION_FRAMEWORK.md` extends the contract with changeable candidate definitions, explicit priority/weighting semantics, input/output targets, news interpretation and the narrow framework implementation boundary. Specific classifier criteria and the Review default remain open.

## 1. Structural rule supplied by the operator

For an applicable four-quarter cycle, use one of these orders:

| Order | Q1 | Q2 | Q3 | Q4 |
| --- | --- | --- | --- | --- |
| AMDX | A | M | D | X |
| XAMD | X | A | M | D |

X is Continuation X(C) or Reversal X(R). Inferring the location/role X does not determine its subtype. The new contract therefore needs an explicit **X with subtype unresolved**, distinct from entirely Unknown or Not Applicable. The legacy enum/storage currently has only X(C)/X(R); do not silently map an unresolved X into either or rewrite old data.

Q3=D constrains the quartet to AMDX and yields Q1=A, Q2=M, Q4=X with subtype still unresolved. Q3=M instead constrains it to XAMD. Changing the accepted Q3 anchor from M to D revises the whole profile, not merely one unrelated field.

The clock supplies quarter identity. A technician assignment or an explicit classification rule supplies the role anchor. Time position alone does not choose AMDX versus XAMD. Derived context is conditional on the accepted anchor and selected structural rule; it does not independently prove price behaved that way.

## 2. Concrete intraday example and scope boundary

In the daily quartet, Asia, London, NYAM and NYPM are Q1 through Q4. Recording **NYAM = D** implies **Asia=A, London=M, NYAM=D, NYPM=X(?)** under the AMDX ordering rule. Only NYAM's anchor was explicitly entered. The other roles are marked rule-implied; earlier roles are not fabricated observations and the future role is not a guaranteed outcome.

Within NYAM, its own quartet comprises four 90-minute intervals. Recording **NYAM cycle 3 = M** implies XAMD for that separate quartet. A parent NYAM role D does not make all four child intervals D or automatically choose their profile. This distinguishes **within-quartet structural inference** from **cross-layer inheritance**. The earlier blanket no-inference proposal is superseded within a quartet; cross-layer propagation still requires an explicit, applicable rule.

Use canonical time bounds and a stable containing-cycle identity, plus stable identities/bounds for its four quarters. Interpretations remain run-owned. Friday's special weekly context, structural distortions and shorter subcycles are not forced into an ordinary quartet; rule applicability must be explicit. Existing accepted calendar-month derivations retain their legacy provenance until a reviewed mapping/migration is defined.

## 3. Separate four kinds of information

| Kind | Example | What the system can claim |
| --- | --- | --- |
| Raw market/time fact | NYAM cycle 3 is 09:00–10:30 ET | Factual position/bounds under the time contract |
| Explicit technician anchor | Technician enters Q3=D | Recorded judgment with its reference/source; not necessarily objective classification |
| Rule-implied profile context | Q3=D supports AMDX; Q4=X(?) | Conditional structural consequence with rule/anchor provenance |
| Evidence-based phase classification | A versioned plan criterion matches explicitly recorded price evidence | Result of those declared criteria and inputs, with reasons/unknowns |

Expected/working and observed/review channels stay separate for anchors and profile claims. An inferred role must not be persisted as if the technician manually entered it or independently observed it. Observation capture does not rewrite the earlier expected profile. A later rule revision must not recompute historical claims under a new definition without an explicit provenance-bearing analytical action.

## 4. Fluidity and competing interpretations

Allow unresolved order, unresolved X subtype, competing hypotheses, conflicting active anchors and explicitly recorded exceptions/manual judgment. Do not force a label simply to complete a form. Distinguish a profile resolved structurally from a classification verified by evidence.

The implemented anchor-accumulation action keeps the latest non-cleared anchor for each quarter active. Earlier revisions remain history rather than simultaneous active constraints. Competing hypotheses are explicitly separate claims/branches, not an accidental mixture of historical edits. The subsequent native-trial feedback below refines the preferred ordinary working-quartet edit flow; the existing action is not yet changed.

In the existing accumulation action, if current Q1=A and Q2=A are both asserted, neither listed profile fits. Preserve both inputs and show the conflict; do not silently erase one or choose the latest quarter as the winner. The technician may correct an anchor, retain uncertainty, record a competing hypothesis or identify a rule exception. No new authorization/completion gate is introduced by this uncertainty alone.

If the technician is unsure whether Q3 is M or D, preserve the competing XAMD and AMDX interpretations with their basis, rather than invent a confidence percentage. A rule result can say which evidence supports, contradicts or is missing for each. Recording a manual judgment/exception remains inspectable with source/reason; it is not hidden as a rule-derived result.

### Native-trial refinement — 2026-10-11

The operator prefers a new valid entry to revise the working quartet directly, without searching for an earlier anchor to overwrite or clear. This refines the ordinary entry-action target rather than removing domain support for conflicting evidence, alternatives or immutable earlier claims. For example, after Q1=A has selected AMDX, a later deliberate Q3=M choice should be able to select XAMD as the new working interpretation while retaining the earlier AMDX claim in history. It should not require finding and clearing Q1 first.

Ordinary input must exclude structurally impossible placements. Across both supplied orders, Q1 permits A/X, Q2 A/M, Q3 M/D and Q4 D/X. Restrict by quarter position across both orders, not by the currently resolved order, so a deliberate revision remains possible. X subtype choices apply only to the valid X positions. Unknown, Not Applicable and clear are separate actions.

This is recorded entry-direction feedback, not an implemented replacement command or approval to discard all other current anchors. Before coding, make explicit how a new quartet claim retires incompatible supporting anchors, treats compatible anchors/X subtype, handles uncertainty/clear and identifies any deliberately retained alternative. Preserve stale-head checks, immutable history, original target/reference and separate parent/child scopes. Analytical rule conflicts and explicit exceptions remain traceable. Existing persisted transcripts keep their original accumulation semantics; a new action must identify its own basis rather than reinterpret old records.

`AMDX_WORKING_QUARTET_ACTION_REVIEW.md` makes those choices concrete with ten worked cases. The operator authorized the follow-up implementation: `revise-working-v1` now retains compatible anchors, retires incompatible ones, keeps subtype only at the same compatible X quarter and never reactivates retired anchors after clear. Original stored Accept/Clear actions keep their accumulation meaning on replay. Four follow-up operator checks are pending; this does not accept a final renderer or publish classification criteria.

## 5. Trade Plan rules should carry the interpretive burden

The desired system is a plan-defined cycle interpretation engine, not merely a sensor that notices phase changes. Live classification/sensing may be useful later, but is not a prerequisite for the current architecture and is not implemented by this design.

The structural order rule is now explicit. The next missing content is operational classification: what observable evidence makes a quarter A, M, D, X(C) or X(R), which cycle/context the rule applies to, and what to do when the evidence is insufficient or contradictory. Do not invent thresholds, detection logic or trading probabilities to fill that gap.

| Rule-definition item | Required meaning |
| --- | --- |
| Identity/revision and applicability | Which plan definition, hierarchy/cycle and context governed the result |
| Inputs/source/reference | Which recorded facts were available, and when; avoid future-data leakage in historical work |
| Conditions and exceptions | Observable, inspectable criteria; deterministic where defined; preserve ambiguity where not defined |
| Result and explanation | Role/order/subtype supported, evidence matched/missing/conflicting, and reasoning trace |
| Override/alternative handling | Explicit technician judgment, reason and relationship to the rule result |
| Evaluation scope | What sample/environment and rule revision are being assessed, separately from process adherence or P&L |

Rules and their explanation should be prominent in context: show the active profile/order, the anchor(s), which roles follow structurally, why a classifier matched or remains unresolved, and why X(C)/X(R) is or is not known. Detailed criteria can expand nearby; rule basis should not disappear into an opaque score.

The attached Trade Plan example describes weekly anticipation from opens/bias/London/news and progression across Monday–Thursday. It also uses qualified language and mentions possible alternatives. It is not a complete mechanical classifier specification. Its wording uses both Continuation/Reversal and Consolidation/Reversal; retain that source terminology discrepancy rather than silently claiming they are identical. The operator's current clarification uses Continuation/Reversal. Do not adopt prose probabilities or news assumptions as validated algorithmic rules. Alpha 0.7 policy remains unchanged; authoritative adoption of new phase-classification definitions requires the appropriate published Trade Plan revision.

## 6. History and comparison need cycle-profile provenance

Retain immutable explicit-anchor revisions and immutable/reconstructable profile claims at each interpretation action. A profile claim identifies the containing cycle, four target quarters, channel, active supporting anchors, structural/classification rule revision, candidate orders, implied roles, X-subtype state, conflicts/alternatives, source and explicit market reference. The exact versioned payload remains design work; the old interval-only record proposal is insufficient by itself.

Previously accepted automatic recording and in-place Watch changes still apply: an accepted input updates the corresponding working cycle claim through shared actions, without a Save/Record obligation or forced return to Analysis. Rules can supply derived context without requiring four manual confirmations. Full-stack/TDA access remains available for a broader thesis change.

The Review-baseline question is **still open**. The operator's clarification is not approval of first recorded expectation. Reframe comparison around identified cycle-profile claims and their rule/input basis, with quarter detail when useful. Changing Q3=M to Q3=D can change XAMD to AMDX; a flat M→D row omits that meaning. Any eventual default must preserve earlier claims and distinguish later input, later evidence and later rule definitions.

## 7. Empirical investigation without fabricated certainty

Study/Lab should support replaying explicitly scoped samples under a named rule revision and inspecting why a result matched, remained unresolved or conflicted. Preserve the information available at each decision, distinguish prospective/profile-implied context from later observation, and retain corrections/alternative technician judgments.

Useful later analyses may examine classification coverage, unresolved/conflict cases, disagreement between judgments, rule stability across examples and how interpretations evolve. Statistical definitions and samples need explicit design before publishing results. These are rule/profile evaluation tools, not a new live quarter-correctness checklist or automatic competency/P&L/entry score. They do not promise that subjective disagreement disappears; they make the plan's claims and uncertainty explicit and empirically reviewable.

## 8. Immediate architecture sequence

1. Correct the shared domain unit to a containing four-quarter cycle with explicit anchors, rule-implied context and unresolved X subtype.
2. Define versioned structural inference/profile provenance and conflict/alternative representation; retain legacy meaning and accepted action contracts.
3. Build the structural/definition/provenance foundation without waiting for a full rulebook. Operationalize only explicitly specified classification examples; unfinished targets/conditions/weights remain undefined. See `AMDX_RULE_DEFINITION_FRAMEWORK.md`.
4. Store explicit comparison/profile identities without hardcoding a default. Revisit contextual Review policy before automatic presentation, while the narrow domain/persistence/action foundation can progress. Final rendering, source feeds/live sensors and broad analytics remain separate later work.

## 9. Design verification

Twelve structural worked-case assertions passed in a disposable analysis harness: Q3=D → AMDX/all implied roles; unresolved X subtype; explicit X(R) resolution; Q3=M → XAMD; consistent anchors; conflicting/unsupported placements; untouched Unknown retaining candidates; untyped X constraining order; changed anchor revising the profile without erasing earlier input; and separate quartet independence. These check consequences of the supplied ordering rule, not correctness of price classification or production persistence. The source-plan excerpts above were inspected locally. Documentation-only checkpoint; production source/tests/schema/plan/smoke statuses remain unchanged.
