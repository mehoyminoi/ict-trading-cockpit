# AMDX domain foundation v0

**Checkpoint:** initial pure domain implementation on 2026-10-11 used schema v37. The subsequent `AMDX_PERSISTENCE_GUIDE.md` records transactional run-owned storage in schema v38; `AMDX_ENTRY_OPERATOR_GUIDE.md` records the minimal shared Watch/TDA entry surface now awaiting operator review. Published Alpha 0.7 remains unchanged; final renderers/comparison policy remain open.

## Implemented behavior

`analysis/amdx.py` defines containing quartets, four stable quarter identities, explicit role anchors, coupled AMDX/XAMD inference and immutable interpretation claims. Day/session identities and bounds use the accepted New York futures-day/session clock. These constructors only cover daily sessions and the four 90-minute children of the active session. Higher-order cycles require a separately reviewed mapping; closed weekends have no applicable active intraday quartet. Bounds are half-open. Friday's intraday quartet does not classify Friday as an ordinary weekly Q5.

One Q3=D anchor gives AMDX with implied A/M/X roles. Q3=M gives XAMD. X subtype remains unresolved until supplied; Unknown and Not Applicable remain different states. Incompatible active anchors, unsupported placements and contradictory X subtypes retain conflicts. Parent and child quartets do not inherit each other's interpretations.

`InterpretationHistory.accept(...)` is the shared domain action for a deliberate technician choice or clear. Each action returns a new history containing a new complete claim, its active anchor revisions, structural result, run/branch/channel/cycle identity, explicit recorded timestamp and market reference. The caller pins the quarter identity. Expected and Observed, alternative branches and separate runs/cycles remain isolated. Replacing a quarter's anchor preserves the preceding claim; clearing it removes that active constraint without resurrecting an old choice. There is no separate Record action in the API and no clock-based phase inference. This pure action alone does not write to disk; `TradingSessionRunRepository.amdx.accept(...)` now wraps it with a checked immediate transaction and durable append.

`analysis/amdx_rules.py` defines immutable candidate/published definition snapshots and scoped scalar evidence. Conditions explicitly identify their input scope/key, comparison, threshold/type and unit. A rule separately declares its output quarter, local-behavior versus assigned-role kind, applicable layer, rationale, priority, revision and plan revision. Publication here is provenance metadata; this module does not publish or edit a real Trade Plan. No synthetic criteria enter Alpha 0.7.

The first resolver has a named, revisioned policy: **Cycle Profile Priority**, with lower integer values taking priority. It evaluates all conditions and retains Matched / Not Matched / Unknown / Not Applicable traces. Per-target resolutions remain available as proposals. For the governing cycle profile, all matched assigned-role definitions at the best priority supply structural constraints; lower-priority results remain evidence rather than governing anchors. Equal-priority contradictions remain conflicts. An unknown assigned-role criterion that could equal or outrank the best match leaves the governing profile unresolved. Local-behavior outputs never constrain the quartet. Other policies and weighting formulas require their own defined semantics and evaluator revisions.

For example, a higher-priority London Q2=M proposal can govern AMDX while a lower-priority Asia Q1=X proposal remains visible. Equal priority between those proposals produces a conflict. A local Asia X-like description can coexist with structurally implied Q1=A. Rule priority never edits technician history; explicit technician anchors and rule hypotheses are separate inputs, and combining incompatible ones still exposes their conflict.

Inputs unavailable at the explicit reference remain Unknown. Missing availability, competing input captures, unit/type mismatches and missing facts also remain Unknown. Caller-selected facts identify their source/capture revisions. An explicit false condition can establish Not Matched in a conjunction while missing condition details remain in its trace. Boolean false is not numeric zero. The resolver has no wall-clock fallback, provider query, raw-price detection or title-based news inference.

## Archive and replay contract

History and criteria evaluations expose detached JSON-compatible payloads with explicit payload/evaluator revisions. Evaluation snapshots include their original definitions, evidence values/source/availability, market reference, every rule result, target resolution and governing policy/basis. Reload validates supported revisions and consistency with the retained basis; unsupported revisions fail explicitly instead of being interpreted under current rules. History reload validates the accepted-action transcript and active snapshots. Editing a detached payload does not mutate its original objects.

The initial foundation provided a store/reload contract. The subsequent v38 repository slice now stores these versioned payloads in separate append-only tables, with transactional append/reload, run ownership, immutable revision-content checks, stale-write detection and legacy restart protection. Existing flat QT data is not transformed into invented interval history. See `AMDX_PERSISTENCE_GUIDE.md` for actual storage/commit semantics. Payload validation detects inconsistent records; it is not a cryptographic audit guarantee.

Replaying the same facts under another definition produces a separate evaluation identity/snapshot. Earlier results continue to use their recorded definition and input basis. The engine trusts the explicitly supplied fact availability/source claims; it does not establish that a real provider supports historical as-of knowledge. News can later supply scoped features through the existing capture/coverage contract, with adequate coverage needed before an adapter asserts absence. No news adapter is added here.

## Read-only worked examples

From the repository root:

```bash
python tools/amdx_foundation_demo.py
```

The command prints Q3=M → XAMD, a subsequent Q3=D → AMDX revision with unresolved X subtype, and the synthetic London-priority example. Both history revisions and the opposing rule result remain in the archive. It validates JSON round-trip without opening an application database. `--json` prints the complete synthetic archive for inspection. No fixture is a validated trading definition.

Automated checks:

```bash
python -m pytest tests/test_amdx_foundation.py -q
python -m pytest -q
```

Focused verification: **39 passed**. Covers all eight supported single-anchor placements, stable NY/UTC identities and DST-adjacent trading days, boundaries/closed periods, conflicts, unresolved X, parent/child isolation, immutable revisions/clears, branches/channels/runs, pinned targets, save/reload and inconsistent archives, explicit criterion targets, priority/ties, cross-target profile governance, unknown higher-priority evidence, units/types/availability, replay under changed definitions and the actual read-only demo command. Full-suite results are recorded in `PROJECT_STATE.md`.

## Next integration boundary

Transactional run-owned persistence/restart and the minimal production Watch/TDA entry path are implemented. Next: hands-on review of the shared entry/orientation behavior. Legacy QT maps remain readable with their current meaning; no old interval history or synthetic published criterion is inferred. Contextual Review/Study adoption follows the shared contract; its default pairing remains open.

Actual operational classifier criteria and targets, weighting methods, plan-editing UI, Review default pairing, higher-level temporal mapping, sensors/source feeds, statistical validation and coverflow rendering remain open/downstream. This checkpoint does not change entry authorization, completion gates, competency evidence or startup behavior. Operator usability acceptance has not been requested for an unchanged screen.
