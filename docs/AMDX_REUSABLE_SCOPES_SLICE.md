# UX4c — Reusable quarter input scopes

Builds on operator acceptance of checks 313–317 at `cf9f660` (draft #85). The Study condition scope selector now distinguishes **Fixed Q1–Q4** (exact original quarter identity) from **Reusable Q1–Q4 · selected quartet** (position within the explicitly selected/evaluated quartet).

## Ownership and compatibility

A reusable scope is a typed, versioned descriptor (`selected-quartet-quarter-v1` with position 1–4) inside a condition. Existing string scope identities remain fixed, byte-for-byte in serialized definitions. No reserved string is reinterpreted and no historical definition is converted. Editing a fixed input to reusable creates a new candidate revision through the existing immutable registry.

The definition layer still controls applicability: for the day layer Q2 is London; for the session/90-minute layer Q2 is that session's second quarter. The browser shows the reusable position's current concrete label and start time, but inspection never changes its saved descriptor or facts. Fixed inputs outside the pinned quartet remain explicitly labeled. Scope expressions do not fetch facts or imply that a condition matches.

Evaluation binds descriptors only after matching the definition layer. Facts still require exact bound scope/key, compatible types/units and availability at the explicit information reference. Missing, future, competing or mismatched inputs keep the existing unknown semantics. Results retain the original reusable definition, evaluated cycle, facts, reference and binding identity in the reason trace. Each new evaluation is separately saved; older evaluation bases remain immutable.

Fixed-only evaluations retain `amdx-priority-v1` and their existing payloads. Evaluations containing reusable scopes use `amdx-priority-scoped-v2`; reconstruction verifies binding/result reproducibility and rejects tampering or revision relabeling. The existing schema remains 47. Older application versions do not understand the new scope descriptors/evaluator revision; no backward-reading claim is made for newly authored records.

## Bounded scope

No automatic adoption, classification from price, evaluation UI, news feed, broker action or plan publication. A saved candidate is not automatically selected for another date. This supports positions within one selected quartet; prior-day/prior-session relationships, cross-layer ranges and other temporal expressions remain later work with explicit semantics. Current configured instrument remains MNQ; this does not implement an instrument-general criterion catalog.

Use `AMDX_REUSABLE_SCOPES_OPERATOR_GUIDE.md` for 318–320. Do not repeat all accepted editor checks. Next substantive work is deliberate fact/evidence selection and saved evaluation in Study, rather than adding more expression types without an actual study use case.

## Verification

127 focused tests pass: 116 domain/repository checks across reusable scopes, AMDX foundation, persistence and candidate storage; seven editor/routing checks; four smoke-document checks. New coverage includes two-date saved evaluation replay, unchanged fixed-only v1 round trips, unavailable inputs, wrong-layer rejection, malformed descriptors, tampered bindings/revision tags, and editor reopen on another date. Native scope selector and bound preview were visually inspected. Python 3.10 syntax and diff checks pass. Operator 318–320 remains pending.
