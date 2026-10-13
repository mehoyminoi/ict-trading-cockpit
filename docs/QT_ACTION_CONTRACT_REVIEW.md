# Shared QT / AMDX behavior-contract review

**Status:** Contracts 1 (automatic interpretation recording) and 2 (in-place Watch updates) accepted on 2026-10-11. PR #61's initial entry has six functional operator checks PASS. The operator subsequently authorized the reviewed one-entry policy, now implemented on `feature/amdx-quartet-revision-v1`; its four new checks 251–254 are accepted from the completed operator smoke report on 2026-10-12. The operator accepted routine observed entry without automatic first/latest pairing on 2026-10-12, with deliberately selected optional comparison basis retained through same-cycle corrections. Comparison controls are lower priority and deferred to Study/Review need; notes remain unimplemented. The isolated explicit pairing/archive foundation in `AMDX_REVIEW_FOUNDATION_GUIDE.md` implements identified references without a default. v40 repository integration is documented in `AMDX_REVIEW_PERSISTENCE_GUIDE.md`; UI integration remains downstream.
**Scope:** shared actions and recorded meaning. The new branch uses schema v39; PR #61 uses v38 and merged main remains v37. Alpha 0.7 is unchanged. Final rendering uses the accepted primary 16:9 direction and remains open.

## 1. Automatic capture without a completion obligation

### Accepted behavior

An accepted phase choice invokes **Set interpretation**. The application saves an immutable explicit-anchor revision and corresponding versioned/reconstructable cycle-profile claim automatically, and shows quiet success/error state. No separate Save/Record action is required. Selecting a scope, focusing a control, browsing options or leaving an untouched Unknown value creates no interpretation revision. Repeating the already-recorded phase is a no-op.

Free-text notes save as recoverable drafts while being typed. A draft belongs to an explicit run, target scope, channel and, where applicable, an interpretation revision. Typing does not certify a station or repeatedly declare a new phase. Completed note edits can become timestamped annotations through the application action boundary; exact debounce/focus-exit binding can be chosen in implementation without conflating note entry with phase commitment. A note entered later must not appear to have existed when the earlier phase was selected.

Changing M to D preserves M and appends D. Clearing a recorded phase to Unknown appends an explicit clearing revision; it does not delete history or populate neighboring intervals. Correction/undo, if exposed, invokes the same revision-preserving action rather than erasing a record.

### Concrete case

| Technician action | Durable meaning | Process completion |
| --- | --- | --- |
| Inspect NYAM cycle 3 | Selection only; saved interpretation remains unchanged | Unchanged |
| At 08:55 ET, choose M for cycle 3 (09:00–10:30) | Expected revision E1=M; explicit market reference is Before interval | Unchanged |
| Type an explanation | Recoverable note draft with its own record/reference timing and target | Unchanged |
| At 09:20 ET, choose D for cycle 3 | Expected revision E2=D; E1 remains; E2 is During interval | Unchanged |
| Choose cycle 4 | Different target; no copy-forward or implicit answer | Unchanged |
| Complete a station or finish TDA | Existing deliberate certification/transition action | Changes only through that action |

The semantic input is an accepted choice, not a particular dropdown event. Mouse, keyboard and future macro-pad adapters must distinguish option browsing from an actual accepted Set interpretation command.

### Persistence and failure invariants

Persist the target identity, value/channel, revision ID/order, source and explicit market reference in one transaction before reporting saved success. The reference belongs to the action; a passive clock tick cannot move a pending edit to another interval. Recording wall time and historical market reference remain distinct.

On storage failure, preserve the pending draft, visibly report that it is not saved, and allow recovery without claiming success or completion. An idempotent command identity prevents retries from duplicating revisions. Reject a stale predecessor rather than silently overwriting a concurrent change. Exact retry presentation remains a UI choice.

Reopening restores persisted drafts and revisions without converting drafts into completed analytical work. A draft with no selected phase remains a draft, not an invented first expectation. Legacy run values keep their old meaning; migration invents neither interval history nor original write times.

**Operator decision, 2026-10-11:** accepted. A deliberate phase choice immediately becomes recorded interpretation history without waiting for station completion or a separate Save/Record click. Corrections preserve earlier values; note drafts and analytical completion remain separate.

## 2. Efficient Watch capture and expectation changes

### Accepted Watch boundary

Keep existing Watch observation/thesis capture and scope inspection available. A small working AMDX update is available directly from Watch through a deliberate, easily reached **Set working interpretation** action. It appends a scoped revision using the same shared command and automatic persistence as Analysis, retains the original interpretation, and leaves the operator in Watch. A full Return to Analysis is not required for each phase update.

The operator expects active input as at least the 90-minute cycles pass. Current interval facts/marker update automatically from market time; the phase is still technician input. An untouched quarter has no explicit manual anchor; a constrained containing quartet may expose a clearly marked rule-implied role, including unresolved X subtype. A new containing cycle gets no arbitrary copy-forward, and the clock alone does not choose AMDX/XAMD. Entry should be readily available for the current target, while a draft/active edit stays bound to its explicit interval even when the current marker moves. This does not create a mandatory per-cycle completion gate.

Broader thesis change should have an easy route to full-stack inspection or full TDA re-analysis. Full-stack inspection alone need not leave Watch or certify anything. Return to Analysis remains a deliberate shared transition when broader re-analysis is wanted, preserving the run and relevant target. The technician determines the significance of the change; do not impose a fixed number of edits or QT-level rule that automatically forces re-analysis.

The initial v38 entry implemented this boundary through per-quarter accumulation. The v39 follow-up now implements the one-entry working-quartet revision in `AMDX_WORKING_QUARTET_ACTION_REVIEW.md`, with original accumulation history preserved and all four new operator checks accepted.

Study is an environment/purpose, not a bypass of process semantics. A spacious Study renderer uses the same scoped commands and appropriate analysis/review permissions for its own run.

### Concrete case

| Situation | Accepted action direction | Record affected |
| --- | --- | --- |
| Technician wants to inspect the weekly expectation during Watch | Inspect weekly scope | No interpretation change |
| Technician sees a material market development | Existing Capture observation / thesis-state action | Run observation/evidence, with its explicit reference |
| Technician wants to update a cycle's working interpretation M to D | Set working interpretation directly in Watch | New expected/working revision; old M retained; stay in Watch |
| Current market reference moves into the next 90-minute cycle | Update factual current marker; make explicit input easy to reach | No new interpretation until a deliberate choice; active edit retains its target |
| Technician needs broader thesis review | Inspect full stack or Return to Analysis for full TDA | Inspection alone changes no interpretation; accepted edits preserve history |
| Technician records the observed cycle phase during Market Review | Set observed interpretation | Independent observed revision with identified comparison baseline |

None of these actions silently clears authorization gates, changes the Trade Plan, advances a station or upgrades eligibility. Capturing an observation must not silently rewrite the working expectation. Working-interpretation revision and observation remain distinct commands/channels.

**Operator decision, 2026-10-11:** accepted in-place updates. Small AMDX changes/ongoing cycle input should be a button click away in Watch; broader thesis change should have easy full-stack/TDA review access. Exact controls remain unselected.

## 3. Identified comparison rather than hindsight substitution

### Proposed default for later Review only

Operator clarification on 2026-10-12: Watch needs the current working stack and current position, with limited visual clutter. Retain changes automatically for later Review/Study; do not expose first/latest comparisons or change history in normal Watch. The proposal below describes intentionally accessed Review, not another active-day obligation. Later aggregation may investigate recorded changes in relation to identified price-action events or noticed features; no statistical result or classifier is implemented. The baseline default remains open.

The first-explicit-expectation default is still a proposal. Reframe it around identified containing-cycle profile claims and their rule/anchor basis; the operator's structural clarification does not accept this default. The earlier interval-only illustration below is superseded as a complete domain model by `AMDX_CYCLE_RULE_CONTRACT.md`. Use the first explicit expected revision for the target as a candidate Review baseline. Show its identity and market timing. A deliberately selected alternate baseline must be identified and persisted with the observation. Creating or editing an expectation later cannot rewrite an existing observation's comparison pair.

### Concrete case

| Record/action | What Review retains |
| --- | --- |
| E1=M entered at 08:55 for NYAM cycle 3 | Original expected interpretation, Before interval |
| E2=D entered at 09:20 for the same cycle | Revised working interpretation, During interval |
| Observation O1=D recorded afterward | Proposed default compares E1=M with O1=D; E2 remains inspectable |
| Technician explicitly chooses E2 as an alternate comparison | A new/corrected observation revision identifies E2; the earlier O1/E1 pairing remains historical |
| Observation recorded when no expectation exists | Comparison baseline is Unknown (null); a later expectation does not retroactively attach itself |

Differences remain descriptive. They do not establish error, probability, trading permission or competency. Explanatory notes and Study questions can be captured without a correctness grade. Both Unknown sides or an explicitly Not Applicable side remain Not Comparable; original values/classifications remain inspectable.

**Updated developer recommendation, 2026-10-12:** `AMDX_REVIEW_INTERACTION_CONTRACT_REVIEW.md` proposes no automatic first/latest pairing during routine observed capture. Comparison opens deliberately; selected bases remain explicit and corrections retain a deliberate choice until changed/cleared. It also proposes independently versioned one-entry observed correction. The operator subsequently accepted both principal behaviors on 2026-10-12. Comparison is lower priority, deferred until needed in Study/Review, with no Watch entry point. Versioned observed correction and UI implementation remain downstream. The earlier automatic-first proposal above is historical context.

## 4. Independent mature-UX directions retained

The operator reviewed the whole-tool walkthrough on 2026-10-11. Bird's-eye orientation and focused detail should coexist closely; the mature experience should integrate them rather than separate them behind tabs. Current Focus/Deck tabs remain existing behavior until a reviewed presentation replaces them.

Study-first startup is proposed and subject to change: a dismissible Study this Competency / next-study suggestion should reduce the burden of choosing useful work with limited mental energy, especially while developing a validated successful Trade Plan. Candidate inputs include recorded Development Direction, competency focus and unfinished study. Suggestion ordering, settings, dismissal and active-run resume require later UX review. The opener must not create a run, alter an environment or impose a study quota automatically. These directions do not block the shared data/action contract work.

## 5. Review and implementation boundary

Contracts 1 and 2 are accepted and the initial quartet foundation/entry is implemented. One-entry working-quartet revision is now implemented and operator accepted; the comparison baseline remains independently open. `AMDX_REVIEW_COMPARISON_CONTRACT_REVIEW.md` supplies concrete cycle-profile cases for that next decision. Agreement that the walkthrough is coherent is recorded separately from agreement to these behavior choices. Exact renderer layout and startup preference remain independently revisable.

Stable daily/session identities, storage and initial entry are functionally accepted in PR #61. The reviewed one-entry command is now implemented on the v39 follow-up branch, preserving original transcripts; the four focused checks in `AMDX_QUARTET_REVISION_OPERATOR_GUIDE.md` are now accepted. The accepted next interaction contract is `AMDX_REVIEW_INTERACTION_CONTRACT_REVIEW.md`: efficient observed correction with no routine automatic comparison. Comparison UI is deferred and excluded from Watch. Review comparison policy and final renderers remain independent. This contract document adds no separate manual checklist beyond those operator-guide checks.
