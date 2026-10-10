# ICT Trading Cockpit — Current Project State

**Last handoff update:** 2026-10-10

This is the starting point for a new development chat or developer handoff. Git remains the source of truth for code; this file records the verified project checkpoint and the reasoning context needed to continue without reconstructing chat history.

## Repository state

- **Active branch:** `feature/operator-loop-integration-guardrails-v0`
- **Main baseline:** `a73b916ab61ffc98a2dcd7d2659b570214913660` — PR #50 merged C5 operator-loop integration and guardrails v0 design
- **Competency / Proficiency v0 merge:** `98266e5f6423f91484d1ff687795f6f1b829220a` — PR #26
- **Smoke-test runner v0 merge:** `2356240fb0cd5749682e49b1f9895fe919ab8af4` — PR #27
- **Current slice:** C5 implementation — Operator-loop integration and guardrails v0
- **Schema:** v33
- **Trade Plan revision:** Alpha 0.7
- **Verified full test result:** **340 passed** on 2026-10-10 for C5 operator-loop integration and guardrails v0
- **Manual smoke test:** C5 operator-loop integration and guardrails v0 acceptance **fully PASS** — schema v33 confirmed and all guided checks passed.

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

C3 — Explainable Eligibility v0 is complete and merged.

C4 — Regression / downgrade semantics v0 is complete and merged.

C5 — Operator-loop integration and guardrails v0 is **acceptance-complete and ready for merge**.

Milestone C — **Evidence Maturity and progression governance** is therefore complete as an architectural milestone.

C5 accepted implementation:

- derived `OperatorProgressionStatus` composes environment, purpose, boundary, eligibility, standing, lower-rung recommendation, deterministic guidance, and navigation target without persisting mutable current truth,
- launcher shows concise progression status, governing boundary, blocker names, and progressively disclosed requirement detail,
- configured BLOCKED can stage the normal lower environment without auto-starting,
- lower-rung staging preserves semantically valid intent and creates no attainment/regression/demotion event,
- blocked launcher state can navigate directly to **Review / Development > Progression**,
- Progression shows current eligibility, requirement results, Evidence Maturity, historical attainment/standing, and deterministic Next guidance,
- Human Certification remains authoritatively edited only under Rules / Safety,
- legitimately started runs are not silently terminated/demoted if progression support later changes,
- deliberate configured AVAILABLE boundary crossing remains the only attainment-creation point,
- restore/browse/staging do not create duplicate attainment,
- progression remains separate from setup/trade authorization and cannot block exit/flatten,
- temporary operating/safety restrictions remain a separate future layer,
- Alpha 0.7 remains **NOT CONFIGURED** and non-restrictive,
- schema remains **v33**.

Validation:

- full automated suite: **340 passed**,
- guided C5 smoke test: **fully PASS**,
- schema **v33** manually confirmed,
- no real Alpha 0.7 progression policy or readiness threshold was introduced.

After merge, the next major roadmap milestone is **Milestone E — Context maturity: QT/AMDX, news, and distortions**. Milestone D — continuous operator-loop hardening remains parallel and should interrupt only for friction proven through actual use.

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
