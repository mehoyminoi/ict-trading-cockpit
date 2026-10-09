# ICT Trading Cockpit — Current Project State

**Last handoff update:** 2026-10-08

This is the starting point for a new development chat or developer handoff. Git remains the source of truth for code; this file records the verified project checkpoint and the reasoning context needed to continue without reconstructing chat history.

## Repository state

- **Active branch:** `feature/competency-synthesis-panel-v0`
- **Main baseline:** `6420fea06cfc7792246310f3469669f770708fab` — PR #36 merged competency synthesis design + stable revision isolation
- **Competency / Proficiency v0 merge:** `98266e5f6423f91484d1ff687795f6f1b829220a` — PR #26
- **Smoke-test runner v0 merge:** `2356240fb0cd5749682e49b1f9895fe919ab8af4` — PR #27
- **Current slice:** Milestone B — competency synthesis panel v0
- **Schema:** v29
- **Trade Plan revision:** Alpha 0.7
- **Verified full test result:** 294 passed on 2026-10-09 after the competency-synthesis wording regression fix
- **Manual smoke test:** Competency Synthesis v0 acceptance PASS — compact synthesis surface, descriptive evidence coverage, revision/provenance guardrails, Development Direction refresh, existing evidence/Study routing regression checks, and full-suite status manually verified.

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

Competency Synthesis v0 is **acceptance-complete and ready for PR/merge** on `feature/competency-synthesis-panel-v0`.

Accepted behavior:

- selecting one competency turns the existing compact evidence summary into a **Competency Synthesis** view rather than adding another tall panel,
- synthesis shows competency identity and current Trade Plan revision,
- synthesis shows current human-authored Development Direction and supporting-evidence count,
- evidence coverage remains descriptive by purpose and Study Outcome,
- oldest -> newest reviewed-evidence date range is visible,
- the no-evidence state describes absence of evidence rather than implying failure,
- the surface explicitly states that coverage does not infer proficiency, Evidence Maturity, or eligibility,
- detailed evidence still preserves per-record Trade Plan revision,
- older evidence remains visible and is not silently remapped,
- no generic warning is generated merely because whole Trade Plan revisions differ,
- saving/changing Development Direction immediately refreshes the synthesis,
- evidence selection/detail, supporting-evidence linking, and **Study this competency** routing remain functional,
- Review / Development remains usable within the accepted scrollable layout.

Validation:

- first full-suite run exposed one wording regression: **293 passed / 1 failed**,
- the regression was fixed by preserving the accepted `N evidence record(s)` wording rather than weakening the pre-existing test,
- final full automated suite: **294 passed**,
- focused Competency Synthesis v0 smoke test: **fully PASS / ACCEPTED**.

No schema or Trade Plan revision change in this slice. Schema remains v29 and Trade Plan remains Alpha 0.7.

The stable-vs-candidate Trade Plan isolation requirement remains a cross-cutting architectural rule. This slice preserves revision provenance but does not yet introduce competency-definition fingerprints/revisions.

Next action:

1. inspect the complete branch diff,
2. open and merge the accepted Competency Synthesis v0 implementation PR,
3. sync `main`,
4. choose the next Milestone B slice from the remaining Review / Development synthesis work before entering Evidence Maturity/progression governance.

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
