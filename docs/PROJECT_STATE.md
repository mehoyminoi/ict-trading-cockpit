# ICT Trading Cockpit — Current Project State

**Last handoff update:** 2026-10-09

This is the starting point for a new development chat or developer handoff. Git remains the source of truth for code; this file records the verified project checkpoint and the reasoning context needed to continue without reconstructing chat history.

## Repository state

- **Active branch:** `feature/explainable-eligibility-v0`
- **Main baseline:** `0a6eee1baac4bedf7aefa5c4c977669d00dca430` — PR #44 merged Explainable Eligibility v0 design
- **Competency / Proficiency v0 merge:** `98266e5f6423f91484d1ff687795f6f1b829220a` — PR #26
- **Smoke-test runner v0 merge:** `2356240fb0cd5749682e49b1f9895fe919ab8af4` — PR #27
- **Current slice:** Milestone C3 — Explainable Eligibility v0 implementation
- **Schema:** v32
- **Trade Plan revision:** Alpha 0.7
- **Verified full test result:** full suite green on 2026-10-09 for Explainable Eligibility v0; previous numeric checkpoint 310 passed for C2
- **Manual smoke test:** Explainable Eligibility v0 acceptance PASS — Alpha 0.7 remains NOT CONFIGURED/non-restrictive, schema v32 confirmed, learning-loop regressions checked, and configured-policy evaluator behavior covered by automated tests.

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

C1 — Evidence Maturity Profile v0 is complete and merged.

C2 — Trade Plan Progression Policy substrate v0 is complete and merged.

C3 — Explainable Eligibility v0 is **acceptance-complete and ready for PR/merge** on `feature/explainable-eligibility-v0`.

Accepted implementation:

- immutable requirement-level evaluation results,
- immutable progression-boundary eligibility results,
- AVAILABLE / NOT CONFIGURED / BLOCKED top-level semantics,
- SATISFIED / NOT SATISFIED / UNKNOWN requirement-level semantics,
- explicit reason categories:
  - Requirement Not Satisfied,
  - Insufficient Evidence,
  - Cannot Evaluate,
  - Human Certification Required,
- deterministic evaluation of all four C2 requirement kinds,
- environment-to-progression-boundary mapping,
- current-Trade-Plan-revision filtering for Evidence Purpose Present,
- older-revision Evidence Maturity -> UNKNOWN / current-plan review,
- Competency State continuity without evaluator mutation,
- dedicated `ProgressionCertification` state and repository,
- schema **v32**,
- revision-bound Human Certification persistence,
- Human Certification controls only for configured Human Certification requirements,
- launcher explanation of configured requirement results,
- configured BLOCKED results prevent only the gated upward environment from starting,
- Alpha 0.7 remains NOT CONFIGURED and non-restrictive,
- current eligibility is derived on demand rather than stored as mutable truth,
- no real readiness criteria or new Trade Plan revision.

Validation:

- full automated suite: **operator-confirmed green** on 2026-10-09,
- focused **Explainable Eligibility v0** smoke test: **fully PASS / ACCEPTED**,
- schema **v32** manually confirmed.

After merge, C3 is complete.

Next architectural slice:

**C4 — Regression / downgrade semantics**

C4 should begin as design/governance work. It must define what happens when previously satisfied progression/eligibility conditions are no longer satisfied, while preserving the distinction between:

- competency knowledge/proficiency,
- current-plan contextual validation,
- evidence maturity,
- progression eligibility,
- temporary operating restrictions,
- deliberate frictionless movement downward.

C4 must not assume that one blocked evaluation means the technician has "lost" a competency, and should distinguish true regression from temporary pause, stale/insufficient evidence, plan revision revalidation, and operator-chosen downgrade.

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
