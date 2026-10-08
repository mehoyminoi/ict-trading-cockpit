# ICT Trading Cockpit — Architectural Decisions

This file records durable project decisions and the rationale behind them. It is not a task list. Add a new entry when a decision would be expensive or confusing to rediscover from chat history.

## 2026-10-07 — Training environment semantics

**Status:** Accepted

The environment ladder is:

- Historical Backtest / Lab → **Study**
- Replay → **Rehearsal**
- Forward Test → **Validation**
- Live → **Execution**

Progression eligibility is a separate concern. Environment labels describe what the environment is for; they do not themselves certify readiness to advance.

## 2026-10-07 — Competency model separation

**Status:** Accepted

Keep three concepts separate:

1. **Competency definition** — the skill or mechanic the Trade Plan cares about.
2. **Competency state** — where that skill currently sits in the training ladder.
3. **Evidence** — observations that may later justify changing that state.

Do not collapse these into a single score.

Initial competency/proficiency v0 deliberately does **not** add:

- proficiency percentages,
- automatic promotion/demotion,
- a Live lock based on proficiency,
- a large proficiency dashboard.

Those behaviors require evidence rules and thresholds that have not yet been justified.

## 2026-10-07 — Competency definitions are plan-owned

**Status:** Accepted

The competency catalog is authoritative Trade Plan data. Adding or changing competency definitions therefore creates a new published Trade Plan revision.

Current proficiency state and accumulated evidence are mutable profile/evidence data and remain separate from the versioned Trade Plan.

This decision moved the default Trade Plan from Alpha 0.6 to Alpha 0.7.

## 2026-10-07 — First practical use of competencies

**Status:** Accepted

The first user-facing competency workflow is:

Trade Plan competency catalog
→ current proficiency state
→ Study Run focus links
→ future evidence accumulated against the competency

A Historical Backtest / Study Run can explicitly state which plan-owned competencies it is training, and those links should survive into Review.

## 2026-10-07 — Deterministic tests for time-aware Live Watch behavior

**Status:** Accepted

Tests that depend on timed Live Watch behavior should use explicit deterministic Replay market-time context rather than the wall clock.

The earlier 265-passed / 2-failed result on `feature/competency-proficiency-v0` was resolved by making the affected structured-playbook tests deterministic Replay runs. Production Live Watch code did not require a corresponding fix for that result.

## Decision-recording rule

For future substantial decisions, append an entry containing:

- date,
- short decision title,
- status,
- decision,
- rationale,
- important consequences or intentionally deferred behavior.

Prefer recording the reason a choice was made, not just the final implementation.


## 2026-10-08 — Summary templates are versioned Workbench configuration

**Status:** Accepted

Generated Trade Summary and Study Find text should not depend on hardcoded GUI strings.

Summary template definitions are separate configuration from the Trade Plan. Published template revisions are immutable, previous revisions remain available for provenance/history, and each summary kind has an explicit active revision used for new generated output.

Editing/publishing belongs in Workbench rather than the focused daily capture surfaces. Study Find and Trade Summary consume the active definition and remain responsible for structured record data, not template design.

The first slice intentionally supports revisioning of the existing default template families rather than a broad template-library/catalog UX. Expand that only when repeated use justifies it.


## 2026-10-08 — Canonical handoff package and decision precedence

**Status:** Accepted

Long-running project continuity must not depend on recovering a prior ChatGPT conversation.

The canonical handoff package is:

1. `PROJECT_STATE.md` — exact checkpoint,
2. `PROJECT_REQUIREMENTS.md` — current intended architecture/roadmap,
3. `DECISION_AUDIT.md` — conflict and supersession status,
4. `DECISIONS.md` — durable accepted rationale,
5. `PROJECT_EVOLUTION.md` — chronological architecture history,
6. current code/tests,
7. historical transcripts only when clarification remains necessary.

When sources conflict, prefer verified current implementation/tests, then accepted current requirements, then later explicit decisions and the decision-audit supersession record. Do not promote an older idea merely because it was discussed in more detail.

Every handoff must state the project's **current architectural frontier** in addition to the next concrete task.

**Rationale:** Recovery of the prior long conversation showed that an old feature can remain richly documented even after later work deliberately demoted or superseded it. A chronological history plus an explicit supersession ledger prevents future chats from mistaking historical detail for current priority.

**Consequence:** `PROJECT_REQUIREMENTS.md` should remain current-state oriented rather than becoming a diary. Historical evolution and supersession belong in their dedicated documents.


## 2026-10-08 — Reconciled roadmap and learning frontier accepted

**Status:** Accepted

The recovered project trajectory is now authoritative for forward planning.

The current architectural frontier is:

`targeted Study -> competency evidence -> Replay integration -> Forward validation -> progression/eligibility -> Live Execution`

The accepted milestone order is:

1. Competency evidence loop
2. Review / Development synthesis
3. Evidence Maturity and progression governance
4. Continuous operator-loop hardening in parallel
5. Context maturity: QT/AMDX, news, and distortions
6. Execution-safety simulation
7. NinjaTrader execution integration
8. Shared / multi-device operation

Revision/provenance is a cross-cutting requirement that each slice must preserve; it is not the next standalone milestone.

**Supersedes:** the earlier reconciliation draft that placed abstract process/revision architecture first, and any older roadmap ordering that would elevate Film Night, visual-polish, broad Live-Watch expansion, hardware controls, or deep integrations ahead of the learning/progression loop.

**Rationale:** recovery of the full conversation history showed that the project had already deliberately pivoted from operating-surface expansion toward Study/Lab, competency evidence, and progression semantics before the previous chat ended.


## 2026-10-08 — Competency evidence is provenance, not competency state

**Status:** Accepted

Competency evidence is a first-class persisted record separate from both the Trade Plan-owned competency definition and the operator's mutable competency state.

The v0 evidence loop is:

`focused Study/Rehearsal/Validation run -> reviewed outcome -> persisted evidence for each focused competency`

Evidence should preserve enough provenance to understand where it came from, including the Trading Run, environment/purpose, Trade Plan revision, study intent/outcome, and relevant market-time/QT context.

Re-reviewing the same run+competency updates/replaces that evidence rather than manufacturing duplicate samples from one run.

**Rationale:** the project needs trustworthy observations before it can justify proficiency scoring, state transitions, or progression rules.

**Consequence / deferred behavior:** evidence creation does not automatically change `CompetencyState`, proficiency, eligibility, or Evidence Maturity. Those interpretations remain later work.


## 2026-10-08 — Human-readable system guide will accompany canonical project docs

**Status:** Accepted

Create `docs/SYSTEM_GUIDE.md` at the next convenient documentation checkpoint.

Its role is explanatory: give the operator a coherent mental model of the Cockpit using definitions, system-purpose descriptions, architecture diagrams, operating loops, learning/progression loops, sub-loop flowcharts, source-of-truth relationships, and examples of current paper-doll controls versus the underlying domain model.

The guide should help prevent accidental scope drift caused by imprecise terminology as the architecture grows.

A key example it should explain is competency extensibility:

- competency definitions are Trade Plan-owned and revisioned,
- a newly adopted ICT concept can become a new competency in a later Trade Plan revision,
- from that revision forward the shared competency catalog can expose it to Study/Rehearsal/Validation focus and evidence capture,
- historical records are not silently retrofitted unless an explicit migration/mapping rule is created,
- evidence and derived metrics may later support progression decisions, but the Cockpit must not invent readiness rules merely because a competency exists.

**Rationale:** the full architecture is now large enough that requirements, state, decisions, and evolution documents are individually correct but do not provide a single human-readable conceptual map.

**Consequence:** `SYSTEM_GUIDE.md` will be maintained when terminology, subsystem relationships, ownership boundaries, or major system loops materially change. It will remain explanatory and will not replace canonical requirements, decisions, current state, or implementation.


## 2026-10-08 — Competency evidence is surfaced before it is scored

**Status:** Accepted

Review / Development should first present accumulated competency evidence as human-legible history before the Cockpit attempts to derive proficiency, Evidence Maturity, or eligibility conclusions.

The accepted v0 surface supports:

- all-competency evidence review,
- filtering by plan-owned competency,
- compact counts by environment purpose and reviewed outcome,
- detailed provenance for an individual evidence record.

**Rationale:** the operator should be able to inspect and challenge the underlying observations before later aggregation or progression rules are trusted.

**Consequence / deferred behavior:** evidence counts and outcomes are descriptive. They do not yet constitute a score, competency-state transition, Evidence Maturity judgment, or progression decision.
