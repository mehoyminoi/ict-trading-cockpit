# ICT Trading Cockpit — Current Project State

**Last handoff update:** 2026-10-10

This is the starting point for a new development chat or developer handoff. Git remains the source of truth for code; this file records the verified project checkpoint and the reasoning context needed to continue without reconstructing chat history.

## Repository state

- **Active branch:** `feature/context-maturity-e3-v0`
- **Main baseline:** `cf5c67e1d5df7b0345b370f7463a2f70bb8186e4` — PR #54 merged Milestone E2 provider-neutral market-context events
- **Competency / Proficiency v0 merge:** `98266e5f6423f91484d1ff687795f6f1b829220a` — PR #26
- **Smoke-test runner v0 merge:** `2356240fb0cd5749682e49b1f9895fe919ab8af4` — PR #27
- **Implementation checkpoint:** `e965fbf9afabef1927a86227580fd436e7e8d1da` — Record E3 historical snapshot implementation checkpoint
- **Current slice:** Milestone E3 acceptance — Historical market-context snapshots
- **Schema:** v35
- **Trade Plan revision:** Alpha 0.7
- **Verified full test result:** **364 passed** on 2026-10-10 for Milestone E3 historical market-context snapshots
- **Manual smoke test:** Milestone E1 expected-vs-observed QT/AMDX acceptance **fully PASS** — schema v34 confirmed and all guided checks passed.

## Current completed slice — Competency / Proficiency substrate v0

Implemented/established in this slice:

- plan-owned competency definitions,
- competency/profile persistence,
- Study Run focus links,
- competency assessment tracking/schema support,
- mentorship Trade Plan competency coverage/tests,
- deterministic Replay context for tests that exercise timed Live Watch behavior.

The first practical competency loop is:

Trade Plan competency catalog
→ current proficiency state
→ Study Run focus links
→ future evidence against the competency

Historical Backtest / Study is therefore able to identify which plan-owned mechanics it is training and preserve that association for later Review. Replay and Forward Test can also preserve competency-only run intent when the optional Focus/question is blank.

## Accepted architecture

### Environment ladder

- Historical Backtest / Lab → **Study**
- Replay → **Rehearsal**
- Forward Test → **Validation**
- Live → **Execution**

Progression eligibility remains separate from these semantic labels.

### Competency ownership and evidence

- Competency **definitions** belong to the versioned Trade Plan.
- Competency **state** is separate mutable profile data.
- Competency **evidence** is separate from both the definition and state.
- Changing the authoritative competency catalog requires a new published plan revision.

See `docs/DECISIONS.md` for rationale.

## Intentionally deferred

Do not assume these exist merely because the competency substrate exists:

- proficiency percentages or readiness scores,
- automatic promotion/demotion,
- automatic Live eligibility lock based on proficiency,
- fixed proficiency thresholds,
- a large competency/proficiency dashboard.

These require evidence/threshold rules that have not yet been justified.

## Test-history clarification

An earlier run on this branch collected 267 tests and reported **265 passed / 2 failed** in `tests/test_structured_playbook.py`.

Those failures were time-context dependent. Pulling through implementation commit `9fa5807` changed the affected structured-playbook tests to deterministic Replay runs; the subsequent full suite was **267 passed**. Do not carry the earlier result forward as an unresolved Live Watch production regression.

## Manual acceptance status

Current operator checks completed on 2026-10-07:

- non-Live environments expose the expected five competency focus checkboxes,
- competency focus selections persist into Post-Market Review,
- competency focus selections persist after application restart as part of the Trading Run,
- launcher checkbox selections do not repopulate after restart; this is expected because the launcher represents a new run while persisted Study Context belongs to the started/restored run,
- Post-Market Review reopening at Market Review stage 1 rather than the previously viewed stage 2 is accepted transient UI behavior,
- smoke testing exposed a Replay/Forward defect where competency-only intent was discarded when the optional question was blank,
- that defect was fixed and manually re-verified in both Replay and Forward Test,
- the full automated suite after the fix is 268 passed.

See `docs/SMOKE_TEST.md` for the completed acceptance record and repeatable checklist.

## Recently completed

### Competency / Proficiency substrate v0 — merged via PR #26

- plan-owned competency definitions,
- mutable competency/profile persistence kept separate from definitions,
- Study / Replay / Forward competency-focus provenance,
- competency focus preserved into Review and restart persistence,
- deterministic Replay context for time-aware tests,
- manual smoke-test acceptance complete.

### Developer smoke-test runner v0 — merged via PR #27

- PySide6 runner for `docs/SMOKE_TEST.md`,
- PASS / FAIL / QUESTION / NOT TESTED controls,
- per-item comments/evidence,
- previous/next and next-unresolved navigation,
- live acceptance summary,
- save-back to Markdown,
- Markdown round-trip unit tests,
- manually verified that edits persist and only intended Markdown changes appear in Git diff.

The runner remains a convenience layer over Markdown, not a second acceptance-data format.

## Current architectural frontier

The recovered development trajectory is now explicit:

`targeted Study -> competency evidence -> Replay integration -> Forward validation -> progression/eligibility -> Live Execution`

Competency / Proficiency v0 is complete. The project had already deliberately shifted away from additional Live-Watch embellishment toward the Study/Lab learning and progression loop.

Review / Development synthesis and an Evidence Maturity Profile remain important future consumers/governors, but they should be built only after the competency-evidence substrate is trustworthy.

Older Film Night, responsive-gallery, visual-polish, broad TradingView-integration, hardware-controller, and Live-Watch enhancement discussions are downstream ideas unless actual use makes one blocking.

## Current task

Milestone C — Evidence Maturity and progression governance is complete and merged.

Milestone E v0 architecture is accepted and merged.

E1 — Expected vs observed QT/AMDX review loop is complete and merged.

E2 — Provider-neutral market-context event model is complete and merged.

**E3 — Historical context snapshots and deterministic Replay/Historical event context** is acceptance-complete and ready for merge on `feature/context-maturity-e3-v0`.

Implemented E3 behavior:

- run-level `MarketContextSnapshot` is captured once when a Trading Run starts,
- snapshot state distinguishes:
  - Available,
  - Not Configured,
  - Unavailable,
- Available with zero events remains distinct from provider failure/unavailability,
- snapshot preserves:
  - provider,
  - query bounds,
  - reference market timestamp,
  - market-time source,
  - capture timestamp,
  - normalized events,
  - event/provider provenance,
- query window uses the Cockpit futures day from 18:00 ET to the next 18:00 ET,
- Replay/Historical use the selected historical run timestamp to choose that futures-day event window,
- present-day events are not substituted into historical runs,
- restored runs read the stored snapshot rather than silently re-querying the provider,
- later provider revisions therefore do not rewrite historical run context,
- existing/legacy runs without captured context remain honestly Not Configured rather than being fabricated as an empty successful query,
- Live/Forward use the same run-start snapshot contract,
- no warning/restriction/authorization semantics are introduced,
- schema advances to **v35** with `market_context_snapshot_json`.

Focused tests cover:

- 18:00-to-18:00 futures-day query boundaries,
- Not Configured vs Available-empty distinction,
- provider failure -> Unavailable,
- historical Replay date selection,
- no silent provider revision rewrite,
- repository round-trip/provenance,
- legacy/missing snapshot semantics,
- schema v35 storage.

Validation:

- full automated suite: **364 passed**,
- operator independently reported a green local full suite,
- no new manual UI smoke pass required; E3 adds no operator-facing event surface,
- schema **v35**, Trade Plan **Alpha 0.7**.

Next action: merge E3, then start **E4 — compact operator context surfaces** from the merged main baseline. E4 exposes the stored context in TDA, Watch, and Review while preserving availability, timing, and provenance semantics. It requires focused operator acceptance before merge.

## System guide maintenance

`docs/SYSTEM_GUIDE.md` is now part of the maintained handoff package.

Update it when terminology, subsystem relationships, ownership boundaries, or major system loops materially change. Do not update it for ordinary bug fixes or minor UI changes.

The guide is explanatory and must not supersede `PROJECT_REQUIREMENTS.md`, `DECISIONS.md`, `PROJECT_STATE.md`, the decision audit, or verified implementation.

## Continuity protocol

For every substantial feature slice, update this file before the slice is considered complete.

At minimum update:

- branch,
- implementation baseline SHA/message,
- test count/status,
- schema,
- Trade Plan revision,
- completed work,
- current task,
- unresolved issues,
- intentionally deferred behavior.

Append durable design decisions to `docs/DECISIONS.md`.

See `docs/HANDOFF.md` for the complete handoff procedure.


## E1 operator note — intraday QT depth

**Intraday QT depth requirement recorded.**

The E1 QT/AMDX surface is sufficient for current testing, but the future working version must preserve and expose the full intraday hierarchy—including four sessions per futures day and four 90-minute cycles per session—without forcing the operator through a large repetitive form.

The durable requirement is now in `PROJECT_REQUIREMENTS.md`, with Milestone E design guidance in `CONTEXT_MATURITY.md`.

Preferred future direction: derive factual state automatically, focus the active layer, progressively disclose deeper hierarchy, use compact visual/nested views, and allow edit-by-exception. Completeness in the data model must not require simultaneous exposure of every intraday field.

Current E1 validation status:

- full automated suite: **348 passed**,
- guided smoke test: **fully PASS and committed/pushed**,
- future intraday QT depth remains a documented Milestone E requirement, not a blocker to E1 acceptance.
