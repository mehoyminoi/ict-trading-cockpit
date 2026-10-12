# AMDX rule-definition framework and implementation boundary

**Status:** Architecture response to operator clarification on 2026-10-11. The cycle/rule contract document is reviewed. Specific classifier definitions, their weights, the meaning of the illustrative rule targets and the Review default remain open.
**Decision direction:** enough is known to build the structural/rule-definition foundation without completing every AMDX rule or renderer. Keep unfinished criteria explicit; do not fill them with guessed trading conditions.
**Baseline:** accepted E7, v37 / Alpha 0.7. This checkpoint is documentation only.

## 1. Changeable definitions with protected historical revisions

AMDX criteria should be editable working definitions owned by the Trade Plan, with identifiable candidate and published revisions like other authoritative criteria. Candidate changes can alter conditions, applicability, priority, an explicitly defined weighting method or resolution policy. A published revision remains immutable; changing the finished plan publishes a new revision rather than mutating historical runs.

Compare alternative definitions against the same explicitly scoped evidence in Study. Each evaluation identifies its plan/rule revision, inputs and information reference. A later evaluation under another definition is a new comparison record, not a rewrite of the original expected/observed claim. Rules can be actionable shared domain definitions without waiting for a general-purpose Workbench editor; that UI remains downstream.

## 2. Observation, local behavior, assigned role and profile

| Layer | Example | Responsibility |
| --- | --- | --- |
| Recorded feature/fact | London excursion beyond Asia; London closes inside Asia | Explicit evidence, scope, timing, source, units/precision and availability |
| Local descriptive behavior | A definition describes an excursion as X-like | A rule result or technician interpretation, not necessarily the final quartet role |
| Assigned quartet role | London is Q2=M because the selected definition prioritizes manipulation location | Explicit classification target and selected rule/policy; conditional evidence trace |
| Coupled profile | Q2=M implies AMDX, so Q1=A and Q3=D, Q4=X(?) | Structural inference within the selected quartet; sibling roles are marked implied |

Keep these layers distinct so price behavior that looks X-like does not silently become an impossible cycle assignment or force an arbitrary profile.

The operator's two London examples describe common behavior but different proposed interpretations. Their phrase "consider it A/X" does not yet specify whether London behavior classifies **Asia/Q1**, **London/Q2**, a local behavior label, or the containing profile. Do not guess the target. If it classifies Asia/Q1, A versus X supports AMDX versus XAMD. If it assigns London/Q2=X, neither strict order fits; preserve the exception/conflict rather than silently rotate the pattern. This target detail is needed before making that example executable, but does not block the generic identity/definition/result model.

## 3. Definition shape

| Definition item | Meaning required by the framework |
| --- | --- |
| Identity, plan revision and rule revision | Exact definition used, including candidate versus published status |
| Applicable cycle/context | Hierarchy, containing quartet, target quarter/profile, relevant instrument/context and declared exclusions |
| Input scopes and dependencies | Which current/prior session, quarter, range, price-action feature or event snapshot is examined; separate input from output target |
| Conditions/parameters | Typed comparisons and conditions with units, boundary conventions and timing; no prose interpreted as executable logic |
| Output kind and target | Local behavior, assigned role, profile support/contradiction, X subtype or contextual expectation; no implicit conversion between kinds |
| Priority/resolution policy | Explicit ordering or named strategy deciding which applicable rule supplies the governing role/profile |
| Weighting method, if used | Declared scale, combination, tie and missing-input handling; weight is not automatically probability/confidence |
| Explanation/exception policy | Why a rule matched, failed, remained unknown or conflicted; what alternative/manual judgment means |
| Provenance | Rule inputs and source references, available-at/market/record times, and derived claim identity |

A minimal first resolver can support explicit rule priority and unresolved ties. Reserve weighting as a versioned method with defined semantics; do not invent a universal formula or numerical scale just because the definition can store a weight. Unknown input is not false or zero support. Preserve lower-priority matched results and contrary evidence in the trace even when the selected policy prefers another result.

Explicit technician anchors, rule-derived outputs and profile hypotheses have separate provenance. Priority can resolve competing rule outputs according to a chosen definition; it must not erase a contradictory explicit technician record. Revised/overridden judgments remain revisions or separate claims.

## 4. How the examples fit

**Excursion versus return-inside.** One candidate definition gives close-back-inside behavior priority; another gives any excursion outside the prior range priority. The same evidence can therefore produce different role/behavior/profile results, according to the declared target. Retain both definitions and evaluations for empirical comparison.

Before executing either criterion, specify the source/target quartet, which session close/bar is meant, inside-boundary convention, excursion precision, and when that fact becomes known. A final London close is unavailable before London finishes; an anticipatory expectation must not borrow the later close. The incomplete trailing phrase in the first example is not completed by assumption.

**Manipulation-location priority.** A candidate definition can treat the major manipulation in London as primary evidence for Q2=M. That supports AMDX and implies Q1 Asia=A even if a separate local-behavior criterion calls Asia's excursion X-like. Retain that local description/contrary evidence; do not overwrite it as if Asia's price never left the prior NYPM range. "Major manipulation" and "way outside" still need operational criteria or explicit manually supplied features before automatic classification is possible.

If the rule's outputs actually assign conflicting final roles, show the conflict or apply an explicitly declared exception/resolution policy. If the interpretation is X-like locally but A in the overall cycle, show that distinction. This is the shared framework's job; the specific preferred trading definition is empirical/plan work.

## 5. News is an interpretive and research input

High-impact/red-folder event context should be a first-class input for weekly and session anticipation in TDA and Study, not only a safety-warning panel. Versioned definitions can express relationships between event type/timing, prior-quarter behavior, price-action evidence and a candidate profile/narrative. Their applicability and priority remain explicit.

Reuse recorded calendar captures, normalized/native classifications, run snapshots and existing unknown/coverage semantics. For historical evaluation, retain what was knowable at the reference; later actual/revised event data must not silently enter an earlier prediction. Event absence requires adequate coverage; unavailable data is not a no-news conclusion.

Correlations can be investigated across rule revisions and scoped samples. Do not assume the relationship's strength or causality, invent probabilities, or automatically turn profile support into entry permission. Any actual news restriction still requires an explicit Trade Plan policy. Define result dependencies so a profile and narrative do not circularly justify each other using their own derived values as independent evidence.

No new provider/network feed, live phase sensor or price-action classifier is implied by this framework. Begin with explicitly recorded features/manual evidence where necessary, preserving source quality and unknowns.

## 6. Structural foundation versus unfinished criteria

| Build first | Keep configurable / later |
| --- | --- |
| Stable containing-cycle and four-quarter identities/bounds | Final rendering, including coverflow experiments |
| Roles A/M/D/X with optional X subtype; AMDX/XAMD profile candidates | Operational A/M/D/X classification conditions and preferred approach |
| Explicit anchors, local behavior/results, profile claims and uncertainty/exception state | Whether a particular illustrative rule targets Q1, Q2 or local behavior |
| Versioned definition/input/result/provenance contracts | Domain-specific weighting scale/formula; broad criterion catalog |
| Pure structural inference and explicit priority-resolution interfaces | Live sensing, automatic raw-price feature extraction and broad analytics |
| Shared automatic revision-preserving actions and store/reload contracts | Default contextual Review baseline and detailed UI layout |

The unresolved Review default does not require blocking storage of explicit comparison/profile IDs. Do not hardcode first/latest baseline as part of the data model; select the eventual default through a policy/view contract before enabling an automatic Review presentation.

Start the first implementation as a narrow domain foundation plus meaningful verification. Validate structural consequences, unsupported targets, uncertainty, unknowns/ties, rule-version reproducibility and historical isolation. Use explicit illustrative rule definitions in developer fixtures and label them synthetic; do not publish them into Alpha 0.7 or claim trading validity. Introduce a migration only when the persistence contract is sufficiently concrete, with legacy protection. Integrate production Watch/Analysis/Review renderers after the shared contract is verified.

## 7. Parked coverflow-style exploration

The operator proposes an iPod-coverflow-style AMDX feature, subject to comparison with other approaches. Scrolling/wheel and hotkeys could select focus and progressively reveal relevant detail. Preserve quiet bird's-eye orientation near the selected detail; do not require serial scrolling through every level to discover the whole stack.

Keep navigation and interpretation input separate: scrolling to inspect a level/cycle is not an accepted phase choice, cannot create history and cannot silently retarget a pending edit. Reuse shared navigation actions so mouse/hotkeys/later macro-pad controls have the same meaning. Exact geometry, animation and navigation mapping remain later UX experiments; no coverflow prototype is built in this checkpoint.

## 8. Current review status

The operator reviewed `AMDX_CYCLE_RULE_CONTRACT.md` on 2026-10-11. Structural coupling, fluidity/provenance and prominent versioned rule definitions are retained. Automatic phase recording and in-place Watch updates remain accepted. The examples above clarify why definition mutability, priority and empirical comparison need a common contract; they are not yet adopted executable classifiers or a published Trade Plan revision.

Enough is known to build the framework foundation. A complete AMDX rulebook is unnecessary before that work; only the criteria actually made executable need fully specified targets, inputs, conditions and resolution semantics. Continue discussing/refining the rule content alongside architectural implementation rather than stopping all work until every interpretation method is settled.
