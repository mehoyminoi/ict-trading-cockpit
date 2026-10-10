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
| Temporary operating/safety restriction engine | Separate from progression governance. | DEFERRED |
| Numeric readiness score / automatic promotion-demotion | Not justified by current architecture. | DEFERRED |

Milestone C is complete without publishing real progression thresholds in Alpha 0.7.
