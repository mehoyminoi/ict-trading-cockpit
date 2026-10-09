# ICT Trading Cockpit — Current Project State

**Last handoff update:** 2026-10-09

This is the starting point for a new development chat or developer handoff. Git remains the source of truth for code; this file records the verified project checkpoint and the reasoning context needed to continue without reconstructing chat history.

## Repository state

- **Active branch:** `feature/evidence-maturity-profile-v0`
- **Main baseline:** `a078ef167c5d5db8a064aea09068eb6c1b226d4b` — PR #40 merged Evidence Maturity Profile v0 design
- **Competency / Proficiency v0 merge:** `98266e5f6423f91484d1ff687795f6f1b829220a` — PR #26
- **Smoke-test runner v0 merge:** `2356240fb0cd5749682e49b1f9895fe919ab8af4` — PR #27
- **Current slice:** Milestone C1 — Evidence Maturity Profile v0 implementation
- **Schema:** v31
- **Trade Plan revision:** Alpha 0.7
- **Verified full test result:** 303 passed on 2026-10-09 for Evidence Maturity Profile v0
- **Manual smoke test:** Evidence Maturity Profile v0 acceptance PASS — boundary-aware persistence, four human maturity states, six-dimensional profile, restart persistence, removability guardrail, governance separation, and regression checks manually verified.

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

Milestone B — Review / Development synthesis is complete. The active frontier is **Milestone C — Evidence Maturity and progression governance**.

C1 — Evidence Maturity Profile v0 is **acceptance-complete and ready for PR/merge** on `feature/evidence-maturity-profile-v0`.

Accepted behavior:

- Evidence Maturity remains separate from Competency State, Progression Policy, and Eligibility.
- Profile identity is **Trade Plan + competency + progression boundary**.
- Boundaries are:
  - Study -> Rehearsal,
  - Rehearsal -> Validation,
  - Validation -> Execution.
- Human maturity states are:
  - Not Assessed,
  - Insufficient Evidence,
  - Developing Evidence,
  - Decision-Usable Evidence.
- The overall maturity-state label remains deliberately non-load-bearing/removable.
- The six-dimensional profile remains meaningful independently of the overall state:
  - Volume / Sample Depth,
  - Environment Relevance,
  - Recency,
  - Consistency,
  - Context Coverage,
  - Revision Relevance.
- Separate maturity profiles persist independently by progression boundary.
- Human maturity, consistency, and known-gap/context notes persist across navigation and restart.
- descriptive evidence facts remain derived from evidence rather than duplicated into stored profile state,
- revision provenance is visible while competency-definition equivalence remains explicitly not machine-verifiable,
- saving Evidence Maturity does not automatically change Competency State, Development Direction, progression, eligibility, or Live access,
- no numeric readiness percentage, weighted score, traffic-light verdict, or machine-inferred maturity state is introduced.

Validation:

- final full automated suite: **303 passed**,
- focused **Evidence Maturity Profile v0** smoke test: **fully PASS / ACCEPTED**.

Schema is **v31**. Trade Plan remains **Alpha 0.7** because C1 adds mutable evidence/governance state only; no Trade Plan progression policy exists yet.

After merge, C1 is complete.

Next architectural slice:

**C2 — Trade Plan-owned Progression Policy model**

C2 should begin with design/governance. It must define explicit, explainable progression requirements without turning C1's maturity state into a hidden readiness score or inventing arbitrary thresholds.

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
