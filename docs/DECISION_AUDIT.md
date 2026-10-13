# ICT Trading Cockpit — Decision Audit

**Status:** Recovery audit from the reconstructed project conversation history.

**Purpose:** Resolve conflicts between historical discussions and prevent older ideas from being mistaken for current architecture or priority.

This document is a reconciliation ledger, not a feature backlog. For current requirements use `PROJECT_REQUIREMENTS.md`; for the exact checkpoint use `PROJECT_STATE.md`.

## Status vocabulary

- **CURRENT** — latest accepted architecture.
- **IMPLEMENTED** — current architecture with working substrate/code.
- **REFINED** — older decision remains partly valid but a later decision changed its shape.
- **SUPERSEDED** — do not treat the older version as current.
- **DEFERRED** — still potentially valuable, intentionally not current.
- **OPEN** — unresolved and should not be silently decided in code.

---

## Core product and process

| Area | Latest decision | Status |
|---|---|---|
| Product identity | Local-first trading-process operating system; process adherence and decision quality before P&L theatrics. | CURRENT |
| No Trade / Stand Down | Can be a successful process outcome and still produce valuable observations/evidence. | CURRENT / IMPLEMENTED |
| Trade Plan shell | Foundation + Rules/Safety define constraints; Playbooks define valid methods; Process operates; Review/Development improves. | CURRENT |
| Review/Development | Parallel improvement area, not the final sequential phase after Post-Market. | CURRENT |
| Process Blueprint | Process -> Mode -> Deck -> Station. A station is an analytical operation, not just a field. | CURRENT / IMPLEMENTED |
| Station semantics | Action -> Observe -> Carry Forward. Manual chart work is legitimate until automation replaces the implementation. | CURRENT |
| Focus / Deck | Two projections of the same station/session state; Focus for work, Deck for orientation. | CURRENT / IMPLEMENTED |
| Station completion | Explicit certification is separate from entered work and navigation. Navigation must not silently complete a station. | CURRENT / IMPLEMENTED |
| Persistence | Remember where the operator was, what was done, and what remains without forcing reconstruction after restart. | CURRENT / IMPLEMENTED |
| Return to Analysis | Deliberate, not restrictive; reason is useful evidence, not a penalty. | CURRENT / IMPLEMENTED |

## Trading Day / Trading Run

| Area | Latest decision | Status |
|---|---|---|
| Per-session Asia/London/NYAM/NYPM runs | Valuable intermediate architecture for discovering carry-forward and futures-day requirements. | SUPERSEDED as default |
| Normal run shape | Normally one Trading Run across the active decision process; market sessions are context. Additional runs are deliberate exceptions. | CURRENT |
| Futures day | Rolls at 18:00 America/New_York. | CURRENT / IMPLEMENTED |
| Closing app | Never implies completion. Active state should restore. | CURRENT / IMPLEMENTED |
| Context refresh | Analysis can remain valid, need update, or become invalid rather than being blindly recreated. | CURRENT direction |
| Terminal completion | Completion should feel final; correction of mistaken terminal state belongs to future admin/history tools rather than casual back-navigation. | CURRENT |

## Watch and Review

| Area | Latest decision | Status |
|---|---|---|
| Live Watch as journal form | Too reflective/heavy during high-attention operation. | SUPERSEDED |
| Watch direction | Quiet operational surface; meaningful state changes deliberate, ordinary capture may become nearly invisible. | CURRENT |
| Raw transition log in Review | Keep telemetry in storage but do not demand attention by default. | REFINED / IMPLEMENTED |
| Review structure | Market Review then Process Review. | CURRENT / IMPLEMENTED |
| Interpretation vs adherence | Separate dimensions. | CURRENT / IMPLEMENTED |
| Unexplained thesis change | Means “unknown to me at my current understanding; study needed,” not random/unexplainable market. | CURRENT |
| KPI direction | Process-weighted; P&L present but secondary. Collect useful categories before building dashboards. | CURRENT / DEFERRED UI |

## Playbooks, candidates, and authorization

| Area | Latest decision | Status |
|---|---|---|
| Playbooks | Declarative, revisioned Trade Plan definitions rather than GUI-embedded strategy logic. | CURRENT / IMPLEMENTED |
| Playbook snapshots | Trading Run preserves the operational rules actually used. | CURRENT / IMPLEMENTED |
| No-code editing | Long-term Cockpit configuration goal; authoritative changes require published revision boundaries. | CURRENT direction |
| Models in Play manual checkbox | Useful but insufficient as the whole relevance model. | REFINED |
| Model/candidate states | Available, contextually relevant, temporally eligible, developing, authorized, expired/not current are distinct. | CURRENT direction |
| Named models only | Named Playbooks are scaffolds, not the only valid opportunity source. | SUPERSEDED |
| Technician candidates | Manual/day-specific opportunities remain first-class. | CURRENT |
| Empirical unnamed opportunities | Future data-driven tendencies should be able to feed the same neutral attention/opportunity infrastructure. | CURRENT future architecture |
| Setup vs safety | Setup criteria and run-wide Trade Plan/safety gates are separate. | CURRENT / IMPLEMENTED |
| Pending | Blocks authorization. | CURRENT / IMPLEMENTED |
| Authorized | Means plan permission according to recorded state, not order submission. | CURRENT / IMPLEMENTED |

## Time / QT / AMDX

| Area | Latest decision | Status |
|---|---|---|
| Canonical time | America/New_York. | CURRENT |
| Time as market state | First-class context, not decorative metadata. | CURRENT / IMPLEMENTED |
| Replay/Backtest time | Historical/deterministic, not wall clock. | CURRENT / IMPLEMENTED |
| Raw QT vs AMDX | Raw/factual quarter position is separate from interpretive A/M/D/X state. | CURRENT / IMPLEMENTED |
| Month AMD | Calendar month role inside each quarter can be derived A/M/D. | CURRENT / IMPLEMENTED |
| Raw stack alignment | Preserve independently of AMDX; useful planning/watch evidence. | CURRENT / IMPLEMENTED |
| Stack meaning | Descriptive only until evidence/Trade Plan rules justify directional/probability/authorization meaning. | CURRENT |
| Full QT hub/calendar | Valuable later renderer of shared QT state, not current priority. | DEFERRED |

## Environment / training architecture

| Area | Latest decision | Status |
|---|---|---|
| Historical Backtest | Study / drills / isolated concept practice. | CURRENT / IMPLEMENTED semantics |
| Replay | Rehearsal / scrimmage / integrated whole-process practice. | CURRENT / IMPLEMENTED semantics |
| Forward Test | Validation against live information flow without normal live-risk consequences. | CURRENT / IMPLEMENTED semantics |
| Live | Execution with real capital/risk consequences. | CURRENT / IMPLEMENTED semantics |
| Shared runtime | Common data/process substrate across environments. | CURRENT / IMPLEMENTED |
| Identical UX in every environment | Shared substrate does not require identical emphasis. Lab can be study-heavy while Replay is quieter. | REFINED |
| Environment vs intent | Environment = how information arrives; intent = why the run is being done. | CURRENT / IMPLEMENTED |
| Evidence pooling | Study, Rehearsal, Validation, and Live evidence are different types and should not be casually pooled. | CURRENT |

## Eligibility and competency

| Area | Latest decision | Status |
|---|---|---|
| Hierarchy | Eligibility level first, purpose/activity second, account/capital last. | CURRENT |
| Account taxonomy | Not a peer to environment. Forward normally Sim/Paper; Live Prop/Cash. | CURRENT |
| Moving up | Should require evidence. | CURRENT direction |
| Moving down | Should be frictionless and welcoming. | CURRENT direction |
| Restriction reasons | Eligibility regression, temporary pause, and insufficient evidence require distinct remedies. | CURRENT |
| AVAILABLE / NOT CONFIGURED / BLOCKED | Progression substrate. NOT CONFIGURED means rules do not yet exist. | CURRENT / IMPLEMENTED |
| Competency definition/state/evidence | Three separate concepts. | CURRENT / IMPLEMENTED |
| Competency definitions | Trade Plan-owned/versioned. | CURRENT / IMPLEMENTED |
| Proficiency percentages | Not justified yet. | DEFERRED |
| Automatic promotion/demotion | Not justified yet. | DEFERRED |
| Automatic competency Live lock | Directionally desired eventually but thresholds/rules do not yet exist. | DEFERRED |
| Evidence Maturity Profile | Boundary-aware, non-numeric governance profile; six dimensions accepted; human overall state is removable if too evaluative. | CURRENT design / Milestone C |

## Review / Development and analytics

| Area | Latest decision | Status |
|---|---|---|
| Film Night | Valid eventual consumption workflow, but not current frontier. | DEFERRED |
| Responsive chart gallery | Useful eventual review UX, not a roadmap driver. | DEFERRED |
| Cross-run synthesis | Implemented as Competency Synthesis + human Cross-Run Observation + Development Direction. | CURRENT / IMPLEMENTED |
| KPI dashboard | Do not build before categories/evidence are earned through use. | DEFERRED |
| Revision analytics | Performance and process adherence should eventually be analyzable by process/plan revision. | CURRENT future |
| Feedback export | Full cumulative digest is acceptable temporary workflow; incremental handoff batches are later improvement. | DEFERRED |

## TradingView / hardware / integrations

| Area | Latest decision | Status |
|---|---|---|
| TradingView role | Remains primary visual charting workstation. | CURRENT |
| Workspace parity | Conceptual chart/deck/process synchronization matters even without electronic control. | CURRENT |
| Deep TradingView embedding/replacement | Large future project; not current. | DEFERRED |
| Pine/webhook bridge | Potential narrow future integration once the process has a clear need for the data. | DEFERRED |
| Macro pad / SpaceMouse controller | Promising because mouse interaction became muscle memory; design hardware only after action vocabulary stabilizes. | DEFERRED |
| NinjaTrader | Eventual execution target after safety state machine is proven. | DEFERRED |

## Summary templates

| Area | Latest decision | Status |
|---|---|---|
| Template storage | Versioned immutable Workbench configuration separate from Trade Plan. | CURRENT / IMPLEMENTED |
| Active template | Explicit active revision per summary kind. | CURRENT / IMPLEMENTED |
| Output provenance | Generated text carries template name/revision outside editable template body. | CURRENT / IMPLEMENTED |
| Trade Plan revision placeholder | Desirable later once summary context exposes it. | DEFERRED |

---

## Current priority interpretation

Milestone B — Review / Development synthesis is complete.

Milestone C is complete. The current major roadmap frontier is Milestone E — Context maturity: QT/AMDX, news, and distortions. Milestone D remains parallel and friction-driven.

1. build a boundary-aware Evidence Maturity Profile without numeric readiness scoring,
2. define Trade Plan-owned progression policy separately,
3. evaluate eligibility explainably from that policy,
4. model regression/downgrade semantics,
5. integrate the governance loop into operator workflow with clear guardrails.

The accepted Evidence Maturity identity is:

`Trade Plan + competency + progression boundary`

The four human maturity states are accepted for v0 but remain removable if they prove too evaluative. The dimensional evidence profile must not depend on them.

Do not move priority back toward Film Night polish, additional Live-Watch widgets, chart galleries, broad integrations, hardware, or broker execution merely because those areas are older or richly discussed.

## Rule for future handoffs

If an old source conflicts with this audit:

1. check `DECISIONS.md` for a later explicit accepted decision,
2. check current implementation/tests,
3. prefer the later accepted architecture,
4. treat the historical source as context, not current instruction,
5. record any newly discovered conflict here before changing code or roadmap.


## 2026-10-10 — Milestone C completion audit

| Decision area | Current interpretation | Status |
|---|---|---|
| Evidence Maturity | Boundary-aware, non-numeric evidence decision-usability governance. | CURRENT / IMPLEMENTED |
| Progression Policy | Trade Plan-owned, revisioned, explicit requirements; no implicit thresholds. | CURRENT / IMPLEMENTED substrate |
| Explainable Eligibility | AVAILABLE / NOT CONFIGURED / BLOCKED derived on demand with requirement-level reasons. | CURRENT / IMPLEMENTED |
| Regression / downgrade | Current eligibility, historical attainment, revalidation, and human-confirmed regression remain distinct. | CURRENT / IMPLEMENTED |
| Operator-loop progression guardrails | Upward new-run transitions are gated; active runs are not continuously policed; lower-rung staging remains frictionless. | CURRENT / IMPLEMENTED |
| Alpha 0.7 real progression policy | Still intentionally absent. | DEFERRED |
| Temporary operating/safety restriction engine | Separate from progression governance. E5 now evaluates explicitly configured context restrictions; other safety rules remain manual. | REFINED / E5 substrate implemented |
| Numeric readiness score / automatic promotion-demotion | Not justified by current architecture. | DEFERRED |

Milestone C is complete without publishing real progression thresholds in Alpha 0.7.


## 2026-10-10 — Milestone E continuation audit

| Area | Current interpretation | Status |
|---|---|---|
| E3 snapshot checkpoint | Schema v35 historical run context is accepted and merged through PR #55. | IMPLEMENTED |
| E4 naming | The implementation sequence's compact operator context surface is current. The former narrative E4 heading described cross-cutting distortion/schedule boundaries; those distinctions remain intact. | REFINED / implemented and operator accepted 2026-10-10 |
| Snapshot presentation | Read stored context and use explicit run time. E5 derives effects only through explicit snapshotted rules; facts alone never become restrictions. | REFINED / IMPLEMENTED |
| Later E6/E7 labels | E6 is real provider integration; E7 is model predicates. Review/evidence provenance is cross-cutting. Narrative headings are reconciled to the accepted sequence at the E6 planning boundary. | REFINED / numbering resolved |

Older Requirements/Guide passages describing Milestone A-C as future work are historical inventory language. Verified implementation and the current Project State establish that A-C are complete and Milestone E is active.


## 2026-10-10 — E5 policy boundary

| Area | Current interpretation | Status |
|---|---|---|
| Context policy substrate | Plan-owned rules, explicit environment/unknown effects, read-only evaluation, run snapshots in v36, explanatory surfaces and candidate entry blockers. | IMPLEMENTED / operator accepted 2026-10-10 |
| Alpha 0.7 automatic exclusions | No declarative rules are published; manual gates remain authoritative. Account applicability cannot be inferred from run environment. | DEFERRED pending explicit account semantics and new plan revision |
| Weekly event absence | Requires complete week coverage; day-only snapshots yield Unknown when no matching event is recorded. | CURRENT |
| Real provider / model-specific predicates | E6 local JSON capture/import is implemented with honest source claims; E7 model predicates remain downstream. | IMPLEMENTED / E6 operator accepted 2026-10-10; merged through PR #59 |


## 2026-10-10 — E6 preferred source assessment

| Area | Current interpretation | Status |
|---|---|---|
| Economic-calendar source | Forex Factory is preferred; alternatives accepted for easier/safer implementation. Trading Economics's earlier API recommendation is superseded by the rejected ~$200/month cost. Free Forex Factory import is implemented after operator go-ahead; FMP remains a possible paid candidate. No subscription is purchased. | REFINED / cost constraint CURRENT |
| Supported access | Official Weekly Export links are verified. JSON and operator-supplied XML are inspected; XML detail URLs repeat, timezone is unlabeled, and both formats lose observed All Day precision. ICS/CSV remain uninspected. | VERIFIED limited assessment |
| Historical export | Last Week's JSON link still returned this week's data. No arbitrary-date or historical as-of API is verified. | OPEN |
| First vertical slice | Operator authorized the recommended free import direction. E6 v0 implements source claims, immutable capture storage, JSON preview/import/selection, and run integration. | IMPLEMENTED / operator accepted 2026-10-10; merged through PR #59 |
| Negative event conclusions | A successful export fetch is not sufficient to assert complete requested coverage. Missing status/timing/source scope remains honest. | CURRENT boundary / contract refinement open |

See `E6_PROVIDER_ASSESSMENT.md`. At the assessment stage, preference alone did not authorize implementation or trading restrictions. The later go-ahead authorizes the free importer; automatic trading restrictions remain deferred.

## 2026-10-10 — E6 implementation boundary

| Area | Current interpretation | Status |
|---|---|---|
| Source format | Weekly JSON is the first implemented format because it retains offsets. XML's unlabeled timezone remains unresolved; it is not silently interpreted as UTC. | IMPLEMENTED / XML deferred |
| Query versus coverage | Requested bounds are distinct from explicit provider completeness and selector scope. Legacy tuple success cannot prove absence; absent legacy precision/coverage reads Unknown. | REFINED / IMPLEMENTED |
| Forex Factory timing / status | Clock values retain their native representation; precision and lifecycle status remain Unknown. Entire declared source-week rows are preserved with uncertain day applicability. | CURRENT / IMPLEMENTED |
| Identity / revision | Capture-local row IDs, immutable raw JSON/digest, import provenance, and adapter/mapping revisions; no occurrence continuity or historical as-of assertion. | CURRENT / IMPLEMENTED |
| Operator selection | Preview/save/explicit selection is outside runtime. Selection configures only future runs and resets at restart; historical restore reads stored snapshots. | CURRENT / IMPLEMENTED |
| Automatic policy | Alpha 0.7 remains unchanged. E6 supplies honest source context, not normalized model/news restrictions or progression criteria. | DEFERRED / E7 downstream |

The earlier proposed-only importer wording is superseded by the operator's go-ahead and this implementation. Manual acceptance is PASS on 2026-10-10: all nine checks are recorded in `df4cac894f7e697bf65793c5f031265af5bdd9d4`, with the local automated suite reported as 425 passed. Merged through PR #59 (`aaa931153f165b8ebb90c43126e00b6cd07beeeb`) after assessment PR #58. Acceptance does not certify source completeness, timing precision, historical as-of knowledge, or automatic trading policy.

## 2026-10-10 — E7 model predicate boundary

| Area | Current interpretation | Status |
|---|---|---|
| Model/playbook scope | Explicit plan-owned playbook IDs; candidate effects use stored Playbook identity. Other models and Custom setups do not inherit scoped effects. | IMPLEMENTED / operator accepted 2026-10-11; merged through PR #60 |
| Presence versus absence | Event Absent inverts known outcomes only; complete coverage must include every selected day and selector scope. Unknown remains Unknown. | REFINED / IMPLEMENTED |
| Calendar relationship | NY civil weekday windows and explicit relative calendar-week offset; no model-name inference. | IMPLEMENTED / adopted Monday relationship OPEN |
| Effects | Matched, not-matched and Unknown effects are explicit; legacy not-matched effect is None. Scoped Stand Down Day is invalid. | REFINED / IMPLEMENTED |
| Historical ownership | Existing v37 rule/candidate/source snapshots preserve semantics through database reopen and Review; current definitions never replace them. | CURRENT / IMPLEMENTED |
| Friday Asian Range adoption | A generic validation fixture; preceding/following Monday and policy effects are not settled trading rules. Alpha 0.7 remains unchanged. | DEFERRED pending explicit Trade Plan decisions |

Earlier E7-downstream wording describes the E6 checkpoint. E7 v0 is implemented, operator accepted and merged through PR #60 (`f57794cff6f128830655b458e999fd8f72038280`). All nine checks PASS after controlled persistence and E6→E7 compatibility retests, with the latter recorded in `9454414`. Milestone E remains the major frontier; no roadmap priority is moved.

## 2026-10-11 — AMDX foundation boundary

| Area | Current interpretation | Status |
|---|---|---|
| Independent quarter values | Coupled AMDX/XAMD profile within one quartet, separate parent/child context, explicit anchors and unresolved X subtype. Legacy flat storage is preserved until integration. | REFINED / pure domain foundation implemented |
| Separate Record action | A deliberate accepted choice appends a new immutable claim through the shared domain action. Durable app writes follow transactional repository integration. | SUPERSEDED target / domain action implemented |
| Criterion priority | Versioned Cycle Profile Priority governs the cycle using best-priority assigned-role matches; contrary/local outputs remain traced. No weights/probabilities are assumed. | IMPLEMENTED framework policy / specific trading definitions OPEN |
| Persistence | Versioned history/evaluation JSON archive and validated reload are verified. No production run fields/migration exist yet. | IMPLEMENTED contract / database integration NEXT |
| Renderer and Review baseline | Context-specific screens and comparison default remain open. Coverflow is a later revisable experiment. | DEFERRED / no UI acceptance inferred |

See `AMDX_FOUNDATION_GUIDE.md`. The operator authorized proceeding after reviewing the cycle/definition direction; this does not adopt a synthetic price/news classifier or alter Alpha 0.7.

## 2026-10-11 — AMDX persistence implementation

| Area | Current interpretation | Status |
|---|---|---|
| Persistence NEXT in the foundation checkpoint | Schema v38 separate append-only tables and the normal run repository's shared AMDX actions now commit/reload claims and evaluations. | SUPERSEDED / persistence implemented |
| Existing run snapshot ownership | Ordinary run saves retain old fields and cannot truncate AMDX history; legacy runs have empty new history. | IMPLEMENTED / v37 and actual E6 compatibility verified |
| Revision content and simultaneous edits | Stable cycle/definition content is protected; exact retries are idempotent and stale scoped heads are rejected. | IMPLEMENTED / writer and rollback tests |
| Review comparison | Optional explicit evaluation basis is stored; no first/latest default is selected. | OPEN presentation policy |
| Desktop entry path | Backend is ready for minimal Watch/TDA action binding and restored-record presentation. No new phase-entry surface exists yet. | NEXT / final layout still deferred |

See `AMDX_PERSISTENCE_GUIDE.md`. Earlier v37/no-migration and database-NEXT statements record the foundation checkpoint; this v38 slice supersedes that implementation status while preserving the accepted policy/legacy boundaries.

## 2026-10-11 — AMDX application entry boundary

| Area | Current interpretation | Status |
|---|---|---|
| Watch/TDA binding NEXT | Shared fixed Working AMDX panel now commits/restores Expected working-cycle actions in the normal application. | IMPLEMENTED / operator checks 245–250 PASS; PR #61 ready for review |
| Current versus inspected target | Default follows current after accepted input; inspected targets and open gestures stay pinned. Navigation/time alone never records. | IMPLEMENTED / mouse/menu/keyboard and boundary tests |
| Legacy intraday flat entry | Retained as read-only earlier context in the application-backed path; higher legacy/derived fields keep provenance/behavior. | REFINED / no invented history or cross-layer inheritance |
| Compact Focus wheel behavior | With fixed AMDX orientation, application runtime content can scroll and wheel scrolls content; Back/Forward and station controls remain. Standalone legacy runner behavior is preserved. | REFINED developer fit choice / final UX OPEN |
| Review / Study | Shared working context is read-only in Market Review; no observed-cycle or comparison default is adopted. Spacious Study renderers remain downstream. | OPEN separate contracts |

See `AMDX_ENTRY_OPERATOR_GUIDE.md`. This functional surface is reviewable; backend tests and earlier document review do not imply operator usability acceptance or settled component geometry.

## 2026-10-11 — Native AMDX feedback and primary workspace override

| Earlier interpretation | Latest direction | Status |
|---|---|---|
| Undefined small / compact desktop companion | Plan around a primary 16:9 workspace occupying most of an ultrawide, or a full conventional display; charts/journals arranged around the Cockpit. | SUPERSEDED footprint / accepted target, geometry not implemented |
| Any A/M/D/X button at any quarter | Normal entry permits Q1 A/X, Q2 A/M, Q3 M/D, Q4 D/X across both legal orders. Invalid placements should not be normal choices. | REFINED entry requirement / not implemented |
| Find/clear an old anchor to change order | Prefer one new valid entry revising the working quartet while retaining the earlier claim as history. Compatible anchors, subtype and uncertainty effects need explicit shared-action semantics. | REFINED interaction direction / action contract pending |
| Conflicts and alternatives | Preserve analytical conflicts, original transcripts and explicit alternatives; ordinary revision need not expose stale-anchor cleanup. | CURRENT provenance requirement |
| Session/day plus active 90m visibility and hover | Operator likes these relationships; retain them in more visual future renderers within the larger workspace. | POSITIVE feedback / final rendering open |
| Locally saved smoke results | Pushed in `17b874b2c7fb48f2b35d2e30b9e2a6affe019072`: all six checks 245–250 PASS; all item identities/comments and prior 244 statuses preserved. PR #61 ready for review. | SYNC COMPLETE / current functional surface accepted; follow-up action/layout open |

See `PROJECT_REQUIREMENTS.md` §15.2 and native-trial subsection, `AMDX_CYCLE_RULE_CONTRACT.md` §4 and the new decision entries. This checkpoint records feedback only; source/tests, schema v38 and Alpha 0.7 remain unchanged.

## 2026-10-11 — Working-quartet revision action review

| Topic | Concrete recommendation | Status |
|---|---|---|
| Ordinary phase entry | One valid position/phase selects the new working order; retain compatible anchors and retire incompatible ones in a single immutable claim. | PROPOSED / review cases prepared |
| X subtype | Retain C/R only at the same compatible X quarter; an order switch moves X and leaves its new subtype unresolved unless explicitly supplied. | PROPOSED / no subtype copy-forward |
| Unknown and clear | Affect the selected phase anchor; other compatible anchors can still imply the order. Retired anchors never reactivate. Not Applicable is an explicitly separate quartet-applicability judgment in the proposed policy. | PROPOSED / current stored semantics unchanged |
| Repeat input | Honor the older declared no-op when an already explicit identical choice produces no active-basis change and the head is current. Existing UI currently appends. | EXISTING implementation gap / proposed new command coverage |
| Historical replay | New action-policy identity and replay basis; original Accept/Clear records keep accumulation semantics. | REQUIRED compatibility boundary / payload and migration implementation pending |

See `AMDX_WORKING_QUARTET_ACTION_REVIEW.md` for ten cases. Readiness to continue authorized this contract refinement, not acceptance of every newly recommended uncertainty/applicability detail. PR #61's six PASS results cover the existing functional surface. No implementation, schema, Trade Plan or smoke-status change is made here.

## 2026-10-11 — Working-quartet follow-up implementation

| Earlier status | Current implementation | Status |
|---|---|---|
| Ten-case action proposal | Operator authorized the next implementation. `revise-working-v1` retains compatible anchors and explicitly retires contradictions in one new claim. | IMPLEMENTED / four follow-up checks pending |
| Unrestricted roles | UI choices and shared action enforce the valid union of AMDX/XAMD roles at each position. | IMPLEMENTED / no classifier adoption |
| X / Unknown / applicability | Same-quarter compatible subtype retention, no subtype copying on order switch, conditional Unknown display and separate quartet applicability. | IMPLEMENTED / operator checks 253–254 pending |
| Repeated input gap | Identical explicit meaning is a no-op; immutable receipts reserve command identity without adding a profile revision. | RESOLVED implementation gap / targeted developer checks |
| Existing history | Original v1 actions replay as accumulation; new v2 actions retain their own policy and retirement basis. | IMPLEMENTED / mixed replay and preserved bytes verified |
| v38 storage | v39 adds receipts and forward-version guard; migration preserves existing claims and rollback is atomic. | REFINED / old v38 reader explicitly rejects v39 |
| Earlier six PASS | Checks 245–250 remain PASS for PR #61. New 251–254 are NOT TESTED on the follow-up branch. | PRESERVED acceptance / no inferred follow-up PASS |

See `AMDX_QUARTET_REVISION_OPERATOR_GUIDE.md`. This is the semantic/input follow-up to the reviewed initial surface, not final 16:9 rendering or an adopted price/news method. PR #61 remains ready for review and unmerged; the new branch is based on that accepted source for a separate reviewable slice.

## 2026-10-12 — Quartet acceptance and mature subtype access

| Earlier status | Current direction | Status |
| --- | --- | --- |
| Four follow-up checks pending | Operator reports the smoke complete and smoother; 251–254 recorded PASS from that report. | ACCEPTED functional flow / no per-check logs supplied |
| X(C)/X(R) behind a secondary menu | Each subtype directly available in one click from the active entry target; reuse shared actions for keyboard/macro-pad. | ACCEPTED mature interaction requirement / renderer not implemented |
| First expectation comparison default | Concrete cycle-profile pairing cases prepared; default and broader observed-input contract still require review. | OPEN / not accepted by the smoke completion |

This entry supersedes earlier pending-check wording for the follow-up. The original 250 checklist records, source, schema v39 and Alpha 0.7 are preserved. PR #62 is ready for review and remains stacked on unmerged PR #61.

## 2026-10-12 — Scope of AMDX history/comparison

| Potential interpretation | Operator clarification | Status |
| --- | --- | --- |
| First/latest comparison near the active stack in Watch | Watch needs current working stack and current position with minimal clutter; no visible change history or stack-change comparison. | EXCLUDED from normal Watch presentation |
| Retain revisions | Continue automatic immutable retention for purposeful later Review/Study. | PRESERVED storage/provenance requirement |
| Later event/change insights | Investigate associations with recorded price-action events or noticed features when samples/context support them. | FUTURE research direction / no aggregation implemented |
| First-versus-latest default | Clarification selects where history belongs, not the specific Review pairing default. | OPEN / not inferred acceptance |

## 2026-10-12 — Explicit Review pairing foundation boundary

| Topic | New implementation | Status |
| --- | --- | --- |
| Identified Expected/Observed cycle basis | Supplied claim IDs or explicit missing expected basis; same run/branch/quartet and proper channels validated. | IMPLEMENTED pure domain |
| Alternate comparison | Immutable comparison revision and retained predecessor; observations/old pairings unchanged. | IMPLEMENTED pure action |
| Replay | Self-contained archive retains original claim policies and validates comparison ownership, chronology and chain. | IMPLEMENTED archive / app database integration NEXT |
| First/latest default | No automatic selection; placement clarification remains distinct from baseline adoption. | OPEN policy |
| Watch | Current stack and position; no new history/comparison surface. | PRESERVED |
| Event-associated insights | Requires recorded context and scoped samples; no aggregation added. | FUTURE research |

See `AMDX_REVIEW_FOUNDATION_GUIDE.md`. No schema/plan change or new manual acceptance result is introduced.

## 2026-10-12 — Review repository integration

| Earlier boundary | Current implementation | Status |
| --- | --- | --- |
| Pure explicit pairing archive | Saved-run-owned comparison rows and original receipts, with validated source/basis replay. | IMPLEMENTED backend / v40 |
| Observation plus pair transaction NEXT | One owned action commits new observed claim, cycle if needed, comparison and receipt atomically. | IMPLEMENTED / rollback and stale-head protection |
| Concurrent reload | Read snapshot prevents mixing pre-commit claims with post-commit comparisons. | IMPLEMENTED / writer-overlap regression |
| v39 | Additive atomic migration preserves old bytes and retry semantics; older bootstrap rejects v40. | REFINED compatibility boundary |
| Defaults and presentation | No first/latest selection, new observed replacement semantics, Review controls or Watch history display. | OPEN / existing presentation preserved |

See `AMDX_REVIEW_PERSISTENCE_GUIDE.md`. No new classifier, event likelihood, competency evidence or published Trade Plan policy is introduced.

## 2026-10-12 — Review interaction cases prepared

`AMDX_REVIEW_INTERACTION_CONTRACT_REVIEW.md` recommends independently versioned one-entry observed correction and optional deliberately opened comparison. Routine observation would store no selected expectation; an explicitly selected basis would remain pinned through same-cycle corrections until changed/cleared. This supersedes automatic-first pairing as the developer recommendation, not as an accepted operator decision. v40 Observed accumulation and all existing source/UI behavior remain unchanged. Both decisions are OPEN.

## 2026-10-12 — Review behavior acceptance and priority

| Earlier status | Operator decision | Current status |
| --- | --- | --- |
| One-entry observed correction proposed | Accepted independently of working expectation, preserving earlier judgments. | ACCEPTED behavior / versioned action not implemented |
| Routine no-auto-comparison proposed | Accepted; deliberately selected same-cycle basis persists through corrections until changed/cleared. | ACCEPTED behavior / optional later UI |
| Comparison as immediate next UI task | Lower priority; explore in Study/Review when a concrete need arises. | DEFERRED / storage preserved |
| Watch comparison access | No option or launch route needed from Watch. | EXCLUDED from Watch |

This supersedes earlier OPEN/proposed decision wording, without claiming new implementation or UI acceptance. See `AMDX_REVIEW_INTERACTION_CONTRACT_REVIEW.md`.

## 2026-10-12 — Observed entry action implemented

| Accepted behavior | Implementation | Status |
| --- | --- | --- |
| One-entry observed correction | Independent observed policy shares structural rules and preserves earlier claims. | IMPLEMENTED domain/action |
| Unchanged input | No source or pair revision; original nullable results and both IDs retained in immutable receipts. | IMPLEMENTED / v41 |
| Historical meaning | Legacy v1 and Expected v2 retain original replay/serialization; observed revision uses v3. | PRESERVED / named policy boundary |
| Comparison priority | No automatic expected selection; existing explicit/null basis is preserved. No controls or Watch access added. | PRESERVED / UI deferred |
| Native observed editor | Backend is ready for a permitted Review adapter and gesture/restart verification. | NEXT / not implemented |

See `AMDX_OBSERVED_REVISION_GUIDE.md`. No classifier, published plan, gate or operator smoke result is introduced.

## 2026-10-12 — Native observed entry supersedes read-only Review panel

The accepted one-entry observed behavior is now bound in `feature/amdx-observed-entry-v1`. Earlier descriptions of the fixed AMDX panel as read-only in Market Review and subtype entry as submenu-only are historical implementation states. The panel now records separate Observed/working quartets in Review and has direct one-click X(C)/X(R) controls in both channels. Review date comes from the saved Trading Day, with all-session inspection and clock-independent selection. The database-backed path hides earlier flat intraday observed controls/descriptive comparison without rewriting their data. This does not expand comparison priority: no AMDX comparison/history controls or Watch route are added, and no first/latest baseline default is adopted. Checks 255–259 are now operator PASS from “All points passed” on 2026-10-12; schema v41, Alpha 0.7 and earlier 254 records remain unchanged. Final 16:9 geometry remains separate.


## 2026-10-12 — Saved container date refined to run-start provenance

The initial #66 binding used the containing Trading Day label exclusively. Stack review found that a later run with a different preserved reference could thereby get the older date's observation scope. The correction resolves valid run-start snapshot provenance first, explains old grouping discrepancies, retains an explicit legacy Day fallback only when original reference is absent, and blocks malformed/unavailable date capture. New different-date launch is rejected before reset rather than relabeling old data. The original finding and correction evidence are in `AMDX_STACK_REVIEW.md`; developer verification is complete (77 focused / 744 across the complete module-isolated suite) and operator check 260 is PASS from the guided 2026-10-12 date/rollover/restart/launch-guard reports; heading hover was not separately reported. Accepted 245–259 results remain valid for their covered cases. No change to comparison priority, schema v41, Alpha 0.7 or recorded claim policies is inferred.


## 2026-10-12 — Reviewed AMDX stack merged; higher-stack contract proposed

The operator explicitly authorized merge and continuation. All six PRs were freshly checked against the rehearsed heads, merged with merge commits in #61 → #62 → #63 → #64 → #65 → #66 order, and retargeted to main only after the preceding parent actually merged. Each merge's two parents and exact tree were verified against GitHub. All PRs are closed/merged into main; original feature branches are retained. Earlier unmerged/pending integration statements are historical.

| PR | Merge commit | Reviewed head |
| --- | --- | --- |
| #61 | `c29506eceb36e9c55416ab0a081f3cfaa840499d` | `4346c88` |
| #62 | `26de0d06ea245c7192cbb48ec853e28cee8ea3f5` | `eb822bc` |
| #63 | `7fb664ed20c72ef5c75a6acff293df9f8dcb9d10` | `d940138` |
| #64 | `b2d1741b751881d0799e0edb053c9308412945b3` | `1bf3933` |
| #65 | `fdfb2424bd94580bb4bf44ad33e2c18ad02b2949` | `d058215` |
| #66 | `d092ac7516f585b03c74276d3936201c9aab9117` | `c851e9a` |

Final merge tree exactly equals `c851e9a`; source/tests/tools byte-match tested correction `e12a2d4c4d4767f32dd13c3ea795ffab18531f78`. Retain focused 77 PASS and complete 744 PASS across 70 isolated module processes; these are completed prior runs, not new merge-checkpoint executions. Smoke identities/statuses/comments, v41 and Alpha 0.7 are unchanged. Check 260 operator reports and its unreported-tooltip limitation remain authoritative.

Milestone E remains current. `AMDX_HIGHER_STACK_CONTRACT_REVIEW.md` inventories existing raw higher positions versus legacy flat interpretation, proposes shared cycle/projection ownership and makes boundary examples explicit before persistence or renderer changes. This is the next architecture proposal, not a new accepted trading rule or implementation. Final 16:9 presentation, comparison exploration, classifiers and Study-first startup remain downstream. No new smoke trial is required for this documentation checkpoint.


## 2026-10-12 — Higher temporal facts gain a pure identity/projection adapter

The higher-stack proposal now has a pure resolver/projection implementation in PR #67. Existing raw quarter facts retain their calendar-versus-futures conventions. Legacy `quarter` versus raw `year`, and calendar-month PO3 versus a monthly four-week quartet, remain separate meanings. Full week bounds and static occurrence-derived parent identity avoid silently changing a crossing week's provenance. Friday/fifth-week/pre-first-Monday do not become Q5 anchors or automatic Not Applicable judgments. Existing intraday cycle payloads and all smoke results remain unchanged.

This supersedes “higher mapping wholly unimplemented” only for the pure occurrence/read layer. Durable higher entry, native overview/editor binding, historical as-of querying and Study-owned selection are not implemented by it. No comparison-priority, final-layout, classifier, schema or Alpha 0.7 decision changes. The implementation and boundary cases are in `AMDX_HIGHER_CONTEXT_GUIDE.md`; completed validation/readiness is recorded in project state/handoff.


## 2026-10-12 — Higher persistence no longer deferred as a backend capability

PR #68 supplies the higher entry/restore adapter over v41; earlier “pure-only/no durable higher entry” statements remain historical for #67. Existing action policies, registry content, receipts and retry meaning are reused. New observed entry checks the actual original run timestamp under the owned write lock; a date-only legacy Day cannot supply invented higher provenance. The accepted intraday fallback and native surfaces remain unchanged. Missing/malformed higher reference is explicit availability, not an inferred phase or default Not Applicable answer.

No new schema, legacy conversion, action policy, Watch history/comparison route, renderer acceptance or Alpha 0.7 rule follows. Native binding and Study-owned/as-of selection remain downstream. The focused/full evidence is in state/handoff and the API in `AMDX_HIGHER_PERSISTENCE_GUIDE.md`.


## 2026-10-13 — Source instant equality corrected; selection proposal remains pending

Higher saved-source equality now compares actual instants, not repeated local wall labels. Domain timestamps preserve serialized numeric offsets for exact repeated-hour replay. This supersedes the erroneous same-ZoneInfo equality in the earlier PR #68 source, while preserving existing payloads/policies and schema v41. Final corrected source `9c476df520efec8a7e50a04c015e0de4da78d850 passed 313 focused and 844 complete tests across 72 isolated modules; all test work exited.

The next Review-period contract is now written in `AMDX_HIGHER_REVIEW_PERIOD_CONTRACT.md` with 18 verified temporal assertions. Its whole-day additional orientation, separate source proof and navigation-memory recommendations are proposed only. They do not supersede the current implemented v0 run-start scope until accepted and implemented. No additional reference selector, metadata migration, native higher editor or spacious Lab renderer is present. The existing planned spacious Lab/quiet Watch direction remains intact; no Watch comparison/history route is introduced.


## 2026-10-12 — Broad historical catalog precedes run-bound higher controls

The new operator requirement refines the prior sequence: comprehensive all-layer historical and forward-test data must have first-class ownership early. The one-futures-day higher Review proposal is still appropriate for a particular run, but must not become a global historical-entry restriction. Build independent instrument-scoped catalog ownership before native higher binding. MNQ is the current default; other instrument identities remain separable without a required asset picker.

PR #69 source `d9ccb4422cf9f2f517e38869acb8f57e143e344f` adds catalog domain/storage/archive capability with schema v42. It supersedes “all AMDX capture must be run-owned” only for independent catalog interpretation. Existing run history is neither moved nor relabeled, and the catalog is not a second working copy of a run. Native catalog UI, ingestion/linkage, bulk imports and statistics remain unimplemented. Declared HistoricalEntry/ForwardEntry is retained provenance, not proof of no look-ahead. Main remains v41; the earlier #68 DST result remains valid for its source.


## 2026-10-13 — Catalog manual entry gains its first native Lab surface

PR #70 supersedes “catalog is backend-only/native input wholly pending” for manual catalog entry and navigation. It does not imply mature Lab/final visual acceptance, automatic ingestion of trading-run captures, broader as-of reconstruction or completed analytics. Independent catalog ownership and exact instrument/capture provenance remain unchanged. The full-stack table and adjacent inspector coexist on one workspace; overview/detail are not separated into tabs. The outer AMDX Lab tab is a current navigation doorway, not an adopted final cockpit topology or Study-first startup policy.

Per-database recovered view/provenance preferences are mutable navigation/drafts, distinct from immutable catalog commands. Invalid/unavailable source disables entry; a missing restored catalog requires deliberate selection. Prepared head/reference/capture scope survives only the original gesture, with no automatic replay on failure. The retained 16:9 native-widget trial requests checks 261–264, all NOT TESTED initially. Earlier 260 records remain unchanged. Source `678e9a0835a442f1de42ec6761bfcd7116fc6bad`; #70 remains draft for operator trial review. Schema v42 / Alpha 0.7 and Watch's no-history/comparison direction are unchanged.


## 2026-10-13 — Native AMDX Lab focused behavior accepted

The explicit operator report marks checks 261–264 PASS, covering immediate 90-minute input, direct X(R), an independent older yearly occurrence and retained restart context/profiles. Earlier draft/pending-trial statements describe historical checkpoints. PR #70 is now ready for review, without a merge. The local result file was saved but not yet committed/pushed when reported; no unseen notes or local-file inspection is inferred. Source `678e9a0`, completed 97-focused/936-complete developer evidence, schema v42 and Alpha 0.7 are unchanged. This accepts the covered functional behaviors, not the final renderer/topology or broader catalog linkage/analytics. No Watch history/comparison route is adopted.
