# ICT Trading Cockpit — Current Project State

**Last handoff update:** 2026-10-08

This is the starting point for a new development chat or developer handoff. Git remains the source of truth for code; this file records the verified project checkpoint and the reasoning context needed to continue without reconstructing chat history.

## Repository state

- **Active branch:** `feature/competency-evidence-review-v0`
- **Main baseline:** `c190b037dd994d21e01b260328c41c1787f1eaea` — PR #30 merged competency evidence substrate v0
- **Competency / Proficiency v0 merge:** `98266e5f6423f91484d1ff687795f6f1b829220a` — PR #26
- **Smoke-test runner v0 merge:** `2356240fb0cd5749682e49b1f9895fe919ab8af4` — PR #27
- **Current slice:** Milestone A — competency evidence Review / Development surface v0
- **Schema:** v28
- **Trade Plan revision:** Alpha 0.7
- **Verified full test result:** full v28 competency-evidence suite green on 2026-10-08 (exact count not separately recorded)
- **Manual smoke test:** competency evidence Review / Development v0 acceptance PASS — evidence panel, details, all-competency view, filtering, summary counts, and non-scorecard semantics manually verified.

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

Milestone A — competency evidence Review / Development v0 is **acceptance-complete and ready for PR/merge**.

Accepted behavior:

- Review / Development surfaces accumulated competency evidence in a read-only human-legible panel,
- evidence can be viewed across all competencies or filtered to one plan-owned competency,
- compact counts summarize environment purpose and reviewed outcome without asserting proficiency,
- selected evidence preserves useful context such as Trade Plan revision, Study question/hypothesis/scope, review note, and Trading Run identity,
- entering Review / Development refreshes the evidence view,
- no competency score, automatic state change, eligibility decision, or maturity threshold is introduced,
- full automated suite is green,
- operator manual acceptance passed with no current implementation/function concerns.

Next action:

1. inspect the branch diff,
2. open and merge the accepted Review / Development evidence slice,
3. sync `main`,
4. use the now-convenient documentation checkpoint to create `docs/SYSTEM_GUIDE.md`,
5. after the guide is reviewed, return to Milestone A and decide the first active evidence-consumption behavior (likely a lightweight route from a competency/evidence view back into targeted Study, still without automatic proficiency interpretation).

## Accepted upcoming documentation slice

At the next convenient documentation checkpoint after the current competency-evidence review slice, create a human-readable `docs/SYSTEM_GUIDE.md`.

Its purpose is to explain the Cockpit as a coherent system rather than as a backlog or implementation log. It should include:

- canonical terminology and definitions,
- subsystem purposes and ownership boundaries,
- whole-system architecture diagrams,
- daily operating-loop diagrams,
- Study/Rehearsal/Validation/Execution progression loops,
- competency Definition / State / Evidence relationships,
- environment vs eligibility vs account-context distinctions,
- Playbook / opportunity / authorization relationships,
- revision/provenance concepts,
- current paper-doll UI controls versus the underlying domain concepts,
- examples showing how newly adopted concepts can be added to later Trade Plan revisions and begin accumulating new evidence.

The guide should be maintained when terminology, ownership boundaries, or major system loops materially change. It should remain explanatory and must not supersede `PROJECT_REQUIREMENTS.md`, `DECISIONS.md`, `PROJECT_STATE.md`, or verified implementation.

This is intentionally scheduled for the next convenient documentation opportunity rather than interrupting the current evidence-review validation slice.

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
