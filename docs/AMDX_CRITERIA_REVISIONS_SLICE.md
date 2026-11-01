# UX4a — Independent candidate definition revisions

This bounded prerequisite to native criteria authoring removes an existing storage dependency: previously a definition was retained only while recording a run-owned evaluation. A candidate can now be saved and reopened without creating a process run, judgment, calendar entry or evaluation.

## Contract

`AMDXRepository.definitions` provides `save_candidate`, explicit-key `get`, and plan-scoped `list_revisions`. Candidate records reuse the existing immutable `amdx_definition_revision` table. Identity includes plan revision, rule identity, rule revision and Candidate/Published status. An exact retry is idempotent; changed content under an existing identity is rejected. Edits require a new revision identity. Listing is deterministic identity order, not chronology or a selected/latest definition.

The existing evaluation transaction shares the registry insertion path. Evaluations continue retaining the exact definitions, facts, information reference and outcomes; later candidate saves cannot rewrite earlier results. Published definitions already retained through evaluations remain readable. The authoring API cannot publish, adopt or select a definition for Watch or the calendar. It does not certify that the supplied plan revision is an adopted plan.

There is no schema migration (47), GUI change, classifier, risk-policy change or automatic plan adoption. Caller-owned transactions are refused rather than committed or rolled back. The existing database's insert-only protections remain in force.

## Deliberate remaining boundary

Native form editing and a contextual definition browser are next. Existing condition scopes are explicit identity references, including cycle-specific quarter IDs; they are not yet reusable expressions such as “prior Asia range.” Do not silently bind one cycle's criterion to another. The editor must separate input scope from output quarter and local behavior from assigned role. Retain unknown/conflict semantics rather than inventing criteria or interpreting prose as executable rules.

Evaluation/evidence selection and empirical comparison are subsequent UX4 work. This slice provides no automatic classifier or claim of trading validity. Its synthetic verification demonstrates two revisions against the same explicit evidence while retaining the original evaluation; it is not a recommended trading criterion. Source trade-plan examples need not be reinterpreted to establish this storage boundary.

Operator 311–312 acceptance is recorded. No additional operator smoke test is required for this non-visual slice. Companion-window requirements are included as future direction without expanding this implementation.

## Developer verification

49 focused tests pass: 45 AMDX definition/persistence checks and four smoke-document checks. The four new definition tests also pass after final refactoring. Existing persistence coverage includes immutable evaluation identity and transactional failure behavior. No GUI or full-suite result is claimed for this storage-only change.
