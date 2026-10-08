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
