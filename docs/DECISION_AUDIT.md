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
