# Milestone E — Context maturity v0 design

**Status:** Accepted for v0 implementation  
**Milestone:** E — Context maturity: QT/AMDX, news, and distortions  
**Primary principle:** Mature the existing context substrate; do not replace it.

## Purpose

Milestone E should make market context more trustworthy, reviewable, and historically reconstructable without collapsing facts, interpretation, safety rules, or authorization into one layer.

The project already has substantial context infrastructure:

- deterministic America/New_York market time,
- 18:00 ET futures-day rollover,
- raw nested QT quarter facts,
- raw QT layer provenance,
- technician-entered AMDX/XAMD interpretation,
- derived calendar-month AMD role,
- timed model windows,
- descriptive raw-quarter alignment,
- QT context carried through TDA -> Watch -> Review,
- Trade Plan no-trade concepts that already mention red-folder news, NFP, FOMC, and other date restrictions.

Milestone E is therefore not a greenfield QT feature.

The central question is:

> Can the Cockpit distinguish what the clock/calendar/event feed says, what the technician expected, what actually unfolded, what the Trade Plan says about that context, and what later evidence should remember?

## Context layering contract

Keep these layers explicit:

```text
Raw market-time / QT facts
        +
External event / schedule facts
        ↓
Context available to technician
        ↓
AMDX / XAMD interpretation
        ↓
Expected-vs-observed review
        ↓
Model / opportunity relevance
        ↓
Trade Plan warnings / restrictions
        ↓
Setup / trade authorization
```

No lower layer silently implies a higher one.

Examples:

- Q3 alignment does not imply direction.
- CPI at 08:30 does not automatically imply No Trade.
- A holiday does not automatically imply distortion unless the system has an explicit schedule/distortion interpretation.
- An AMDX expectation does not become "correct" or "wrong" merely because the observed label differs; Review must preserve what changed and why.
- A Trade Plan news rule can restrict entry without rewriting raw event facts.
- Exit/flatten remains outside entry restrictions.

## Canonical context families

Milestone E should treat three context families separately but make them composable.

### 1. Temporal / QT facts

Already largely implemented:

- futures trading day,
- weekday,
- session,
- daily/session quarter,
- raw QT hierarchy,
- timed model windows,
- current calendar quarter/month role,
- known fifth-week Distortion representation.

These remain **derived factual context**.

### 2. Technician interpretation

Already partly implemented as `qt_context`:

- A / M / D,
- X(C),
- X(R),
- Distortion,
- unknown / N/A.

This remains **human interpretation**, except where a value is explicitly time-derived such as the current calendar-month role.

### 3. External market-context facts

New/maturing substrate:

- economic events,
- holidays,
- early closes,
- market-schedule exceptions,
- event timing/status/impact,
- source/provenance.

These are facts/context, not permission by themselves.

## E1 — Expected versus observed QT / AMDX

The first narrow Milestone E vertical slice should mature QT using the substrate already present.

### Existing problem

Today `TradingRun.qt_context` preserves the technician's interpretation, but Review does not clearly separate:

- what was expected during TDA,
- what was later observed,
- what changed,
- whether that change exposed a Study question.

### Proposed v0 model

Treat the existing TDA QT/AMDX state as the **expected / working interpretation** for that run.

Add a separate **observed QT / AMDX review state** captured during Post-Market Review.

Conceptually:

```text
TDA
Expected QT / AMDX
    ↓ preserve unchanged
Watch
working context
    ↓
Review
Observed QT / AMDX
    ↓
descriptive comparison
```

Do not overwrite the original TDA interpretation when recording observed context.

### Comparison semantics

The comparison should be descriptive, level by level:

- Matched
- Changed
- Expected Unknown
- Observed Unknown
- Not Comparable

This is not a score.

A changed interpretation should preserve both values:

```text
Session
Expected: M
Observed: D
```

Review may also capture a short human note such as:

> Manipulation resolved earlier than expected after 08:30 news.

The software should not infer why the change happened.

### Important distinction

Expected-vs-observed is **not** the same thing as competency evidence.

It may later support:

- a Study question,
- a Cross-Run Observation,
- competency evidence if explicitly reviewed/linked,
- Trade Plan refinement.

It should not create proficiency evidence automatically.

## E2 — Context event substrate

Introduce a provider-neutral structured event model before choosing a permanent economic-calendar vendor.

Recommended event identity:

```text
Market Context Event
- id
- source/provider
- source_event_id
- category
- normalized_event_type
- title
- scheduled_at
- timezone/source timezone
- impact
- affected_market/currency
- status
- actual
- forecast
- previous
- source_updated_at
- captured_at
- provenance/reference
```

Not every field is required for every event.

### Categories

Recommended v0 categories:

- Economic
- Holiday
- Early Close
- Market Schedule
- Other Context

Economic event examples:

- NFP
- CPI
- FOMC
- PCE
- GDP
- unemployment claims

Schedule examples:

- exchange holiday,
- shortened session,
- early close,
- delayed open,
- special settlement/calendar anomaly.

### Impact normalization

Provider-native values should be preserved where possible.

The Cockpit may also normalize to a small vocabulary such as:

- Low
- Medium
- High
- Unknown

But normalized impact must preserve provider provenance and must not pretend every source uses identical semantics.

"Red folder" should map to **High impact** only when the provider/source meaning is explicit.

## E3 — Historical context snapshots

Live context and historical context must behave differently but use the same domain substrate.

### Live / Forward

Use current known event/schedule context.

### Replay / Historical Backtest

Use event/schedule facts corresponding to the selected historical market time.

Never show today's event calendar merely because the operator is replaying an old date.

### Run provenance

A Trading Run should eventually preserve enough context to answer:

> What event/schedule facts did this run know or use at the time?

Recommended v0 rule:

- store normalized context snapshots or immutable links/snapshots with the run,
- preserve event source/provenance,
- preserve the Trade Plan revision that interpreted them,
- do not silently rewrite historical run context if the external provider later revises an event.

This likely justifies a schema migration when implemented.

## E4 — Distortion and schedule context

"Distortion" currently exists in the QT substrate for known temporal structure such as fifth-week monthly distortion.

Milestone E should avoid overloading one word for unrelated conditions.

Distinguish at least:

### QT structural distortion

Example:
- fifth Monday-start week outside Q1-Q4 monthly structure.

### Market schedule distortion

Example:
- holiday,
- early close,
- shortened session,
- special market schedule.

### Event-driven unusual context

Example:
- FOMC,
- NFP,
- major CPI release.

Event presence is not automatically a QT structural distortion.

The system may later study whether certain events correlate with distorted behavior, but that is an empirical question.

## E5 — Trade Plan context rules

External context becomes restrictive only through explicit Trade Plan rules.

Conceptually:

```text
Context facts
      ↓
Trade Plan context rule
      ↓
Warning / Restriction
      ↓
Authorization effect
```

Examples already present in Alpha language include:

- Monday red-folder news,
- Wednesday-or-later NFP week,
- FOMC,
- contract expiry,
- Friday after 11:00.

Milestone E should eventually convert such prose-only concepts into declarative context rules rather than infer them from text.

### v0 rule effects

Recommended effect vocabulary:

- Informational
- Warning
- Block New Entry
- Stand Down Day

Do not introduce order submission here.

Exit/flatten must remain ungated.

### Environment sensitivity

A rule may apply differently by environment.

Example:

- Live / funded execution may be blocked,
- Replay / Study may remain permitted for deliberate practice.

This behavior should be explicit in the Trade Plan rule.

## E6 — Model-specific context conditions

Context should support model/playbook-specific conditions without hardcoding each strategy into event infrastructure.

Important accepted example:

### ICT Friday Asian Range

A future configured model rule may require:

> no Monday high-impact/red-folder news

for the Friday Asian Range condition to be considered active/valid.

The event substrate should make this expressible through structured rules.

Do not hardcode "Friday Asian Range" into the generic economic-calendar service.

The reusable pattern should be:

```text
Playbook / model
    +
Context predicate
    ↓
Applicability / warning / restriction
```

## E7 — Review and evidence provenance

Review should eventually be able to show, for the completed run:

- expected QT/AMDX,
- observed QT/AMDX,
- raw QT facts,
- relevant event context,
- schedule/holiday context,
- context-derived warnings/restrictions,
- Trade Plan revision.

This enables later questions such as:

- Did the AMDX expectation usually fail around certain event classes?
- Was a model less reliable on early-close days?
- Did the operator violate a news restriction?
- Does a repeated "Unexplained / Study Needed" outcome cluster around specific context?

These are future analyses, not automatic conclusions in Milestone E v0.

## Provider architecture

Do not couple the domain model to one data vendor.

Recommended boundary:

```text
External provider
      ↓
Provider adapter
      ↓
Normalized Market Context Event
      ↓
Run/context service
      ↓
TDA / Watch / Review / Trade Plan rules
```

A provider adapter may later be:

- API-based,
- imported file/calendar,
- manually entered fallback,
- test fixture/replay dataset.

### Why provider-neutral first

This protects the Cockpit from:

- vendor changes,
- rate limits,
- licensing changes,
- inconsistent event taxonomies,
- historical-data availability differences.

Provider selection can occur after the domain contract is accepted.

## Freshness and uncertainty

Context should preserve uncertainty rather than invent certainty.

Examples:

- event time tentative,
- event postponed,
- source unavailable,
- impact unknown,
- holiday schedule not loaded,
- historical event record missing.

Unknown external context is not equivalent to "no event."

Trade Plan rules should be able to distinguish:

- no matching event,
- matching event,
- context unavailable/unknown.

A future high-risk Live rule may choose to fail closed when required context is unavailable, but that behavior must be explicit in the Trade Plan.

## Operator presentation

The operator should not face another giant calendar dashboard.

Preferred active-run presentation:

### TDA

Compact context card:

```text
Context
Market time: NYAM · Q3
QT raw: Q4/Q4/Q4/Q1/Q2/Q3/Q3
AMDX expectation: ...
Events: CPI 08:30 High · FOMC 14:00 High
Schedule: Normal
Trade Plan: 1 warning
```

Details available on demand.

### Watch

Only context that is now/upcoming and operationally relevant.

### Review

Full historical context/provenance and expected-vs-observed comparison.

This follows the existing principle:

> preserve depth; reduce simultaneous exposure.

## Data ownership

Recommended ownership boundaries:

### Market-time / QT raw facts
Derived runtime context.

### Expected / observed AMDX interpretation
Trading Run / Review state.

### External event records
Provider-neutral context records with provenance.

### Event snapshot used by a run
Run provenance/history.

### Trade Plan event/schedule rules
Versioned Trade Plan definitions.

### Warnings/restrictions
Derived on demand from run context + Trade Plan rule.

Do not persist a generic "market is dangerous" boolean.

## Proposed implementation sequence

### E1 — Expected vs observed QT/AMDX review loop

Smallest useful slice.

- preserve existing TDA expectation,
- add observed review state,
- descriptive level-by-level comparison,
- Review presentation,
- restart persistence,
- no automatic evidence creation.

### E2 — Provider-neutral market-context event model

- domain types,
- normalized event structure,
- in-memory/test provider interface,
- deterministic fixture data,
- no external API dependency yet.

### E3 — Run context snapshot and historical determinism

- attach relevant event/schedule context to run,
- preserve source/provenance,
- Historical/Replay use selected historical date,
- schema migration if needed.

### E4 — Operator context surface

- compact TDA context card,
- quiet Watch relevance,
- Review provenance/detail,
- progressive disclosure.

### E5 — Declarative Trade Plan context rules

- structured news/schedule conditions,
- warnings/restrictions,
- environment-sensitive applicability,
- unknown-context semantics,
- no hardcoded provider assumptions.

### E6 — Real provider integration

Only after E2-E5 contracts are stable.

- select provider,
- implement adapter,
- cache responsibly,
- support historical retrieval where available,
- define failure/offline behavior.

### E7 — Model-specific context predicates

- playbook/model applicability conditions,
- include Friday Asian Range "no Monday high-impact news" as one validation use case,
- keep predicates generic/reusable.

## Schema expectation

E1 likely requires persistence for observed QT/AMDX review state unless it can safely fit an existing run JSON structure.

E2 domain design itself need not migrate schema.

E3 likely requires a migration for run event-context snapshots/provenance.

Do not avoid a justified migration merely to preserve v33.

Schema changes must preserve restart/historical reconstruction and be tested explicitly.

## Explicit non-goals

Milestone E v0 should not:

- assign directional meaning from raw QT alignment,
- derive trade probability from QT stack,
- auto-authorize entries from AMDX,
- treat every high-impact event as an automatic no-trade condition,
- hardcode one economic-calendar vendor into domain objects,
- build a full news terminal,
- scrape arbitrary websites,
- infer competency evidence automatically from context mismatch,
- make event presence equal "distortion,"
- replace TradingView charting,
- submit NinjaTrader orders,
- build Milestone F execution safety early.

## Acceptance target

A successful Milestone E should make this statement true:

> The Cockpit can reconstruct the temporal/QT/event context that existed around a run, preserve what the technician expected versus what was later observed, apply only explicit Trade Plan context rules, and carry that context into Review without turning raw facts into hidden direction, probability, or authorization logic.

## Operator confirmation questions

1. Start Milestone E with **expected-vs-observed QT/AMDX** before external news ingestion?
2. Treat the existing TDA `qt_context` as the run's expected/working interpretation and add a separate observed Review state rather than renaming/replacing the existing field immediately?
3. Keep expected-vs-observed comparison descriptive only, with no score or automatic competency evidence?
4. Use the level-level comparison states **Matched / Changed / Expected Unknown / Observed Unknown / Not Comparable** for v0?
5. Introduce a provider-neutral **Market Context Event** model before selecting a real economic-calendar API?
6. Keep economic events, holidays/early closes, and QT structural distortion distinct even though they can appear together in one operator context view?
7. Normalize impact to Low / Medium / High / Unknown while preserving the provider-native value/provenance?
8. Treat "red folder" as High impact only where the source explicitly supports that mapping?
9. Require Replay/Historical context to use the selected historical market date rather than current-day events?
10. Preserve run-specific event/schedule context so later provider revisions do not silently rewrite historical context?
11. Make Trade Plan context rules the only layer that can turn event/schedule facts into warnings or entry restrictions?
12. Use v0 rule effects **Informational / Warning / Block New Entry / Stand Down Day**?
13. Allow rules to be environment-sensitive so Live can be restricted while Replay/Study remains available?
14. Keep unknown/unavailable event context distinct from "no event," with fail-open/fail-closed behavior owned by the Trade Plan rule?
15. Keep Human/technician AMDX interpretation separate from raw QT facts and external event facts in storage and UI?
16. Keep the event provider adapter generic so API, imported calendar, manual fallback, and deterministic test fixtures can share the same normalized event contract?
17. Defer real provider selection/integration until the normalized event model, snapshots, UI, and Trade Plan rule semantics are stable?
18. Use the Friday Asian Range "no Monday high-impact/red-folder news" condition as a validation case for generic model-specific context predicates, not as hardcoded event-service logic?
19. Permit schema migrations in Milestone E when required for honest historical snapshots instead of artificially preserving v33?
20. Keep the active UI compact: context summary in TDA, only relevant/upcoming items in Watch, full comparison/provenance in Review?


## Accepted operator decisions

All twenty Milestone E design points were accepted on 2026-10-10.

1. Start with expected-vs-observed QT/AMDX before external news ingestion.
2. Treat existing TDA `qt_context` as expected/working interpretation and add separate observed Review state.
3. Keep expected-vs-observed comparison descriptive only, with no score or automatic competency evidence.
4. Use Matched / Changed / Expected Unknown / Observed Unknown / Not Comparable comparison states.
5. Introduce a provider-neutral Market Context Event model before choosing a real economic-calendar API.
6. Keep economic events, holidays/early closes, and QT structural distortion distinct.
7. Normalize impact to Low / Medium / High / Unknown while preserving provider-native value/provenance.
8. Treat red-folder as High impact only when explicitly supported by the source.
9. Replay/Historical context uses the selected historical market date rather than current-day events.
10. Preserve run-specific event/schedule context so later provider revisions do not silently rewrite history.
11. Only explicit Trade Plan context rules may convert event/schedule facts into warnings or entry restrictions.
12. Use Informational / Warning / Block New Entry / Stand Down Day as v0 rule effects.
13. Allow environment-sensitive context-rule applicability.
14. Keep unknown/unavailable event context distinct from no event; fail-open/fail-closed behavior belongs to the Trade Plan rule.
15. Keep technician AMDX interpretation separate from raw QT facts and external event facts.
16. Keep the provider adapter generic across API, imported calendar, manual fallback, and deterministic fixtures.
17. Defer real provider selection until event model, snapshots, UI, and Trade Plan rule semantics stabilize.
18. Use Friday Asian Range no-Monday-high-impact-news as a validation case for generic model-specific context predicates.
19. Permit schema migrations when required for honest historical snapshots.
20. Keep active UI compact: summary in TDA, relevant/upcoming in Watch, full comparison/provenance in Review.
