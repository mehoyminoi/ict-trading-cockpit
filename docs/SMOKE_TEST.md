# ICT Trading Cockpit — Manual Smoke Tests

Use these checklists for human acceptance testing at major codebase events. They complement automated tests; they do not replace them.

## When to run

Run the relevant smoke test:

- before merging a substantial feature branch,
- after schema or persistence changes,
- after major workflow/navigation changes,
- after changes to authorization, risk gates, or Live behavior,
- after changes to time/session/QT logic,
- after changes that alter Trade Plan-owned definitions or revisions.

Record unexpected behavior immediately. Do not "test around" a failure.

---

## Baseline pre-merge smoke test

### 1. Startup and restoration

- Launch the application from a clean restart.
- [PASS] Confirm the main window opens normally.
- [PASS] Confirm no unexpected traceback, crash, or teardown error appears.
- [PASS] If an active Trading Day/Run existed before restart, confirm the application restores the active runtime surface rather than losing the run.
- [PASS] Confirm previously persisted run evidence/review data still appears where expected.

### 2. Trade Plan shell

- Open **Trade Plan**.
- [PASS] Confirm the expected Trade Plan revision is displayed.
- [PASS] Confirm the left-side sections render and can be selected.
- [PASS] Open **Process** and confirm both **Process Map** and **Run Trading Day** tabs render.
- [PASS] Open **Review / Development** and confirm the Lab / Replay launcher renders.

### 3. Environment launcher

[PASS] For each environment, verify the visible controls match its purpose.

#### Historical Backtest / Study
- Select **Historical Backtest**.
- [PASS] Confirm the purpose reads **Study**.
- [PASS] Confirm a historical New York market-time selector is visible.
- [PASS] Confirm Study Intent fields are visible.
- [PASS] Confirm all plan-owned competency focus checkboxes are visible.
- [PASS] Confirm a focused study question is required before the run can begin.

#### Replay / Rehearsal
- Select **Replay**.
- [PASS] Confirm the purpose reads **Rehearsal**.
- [PASS] Confirm a historical New York market-time selector is visible.
- [PASS] Confirm Run Intent and competency focus controls are visible.
- [PASS] Confirm intent is optional.

#### Forward Test / Validation
- Select **Forward Test**.
- [PASS] Confirm the purpose reads **Validation**.
- [PASS] Confirm no historical-time selector is shown.
- [PASS] Confirm Run Intent and competency focus controls are visible.

#### Live / Execution
- Select **Live**.
- [PASS] Confirm the purpose reads **Execution**.
- [PASS] Confirm historical-time and study/competency controls are hidden.
- [PASS] Confirm no competency/proficiency state is being presented as an automatic Live authorization lock unless that behavior has been explicitly implemented in a later revision.

### 4. Study competency provenance

Use Historical Backtest for this test.

- Enter a distinctive study question.
- Optionally enter a hypothesis and scope.
- Select at least two competency focus checkboxes.
- Begin the Process Run.
- Complete enough of TDA to reach the later runtime/review surfaces.
- [PASS] Confirm the run continues to use the same Trade Plan revision.
  - Process intentionally hides the parent header to maximize runtime space.
- Reach Post-Market Review.
- [PASS] Confirm the selected competency names appear under the run's competency focus.
- Restart the application while the run is still restorable.
- [PASS] Confirm Post-Market Review still shows the same competency focus.
  - Review data and competency focus persist after restart. Post-Market Review reopens at 1 of 2 · Market Review rather than restoring the previously viewed 2 of 2 · Process Review page; this is expected transient UI behavior.

**Expected launcher behavior after restart:** the Lab / Replay launcher is a doorway for a *new* Process Run. Its form selections are not a draft of the restored/previous run and are not expected to repopulate from persisted run state. The persisted source of truth is the started Trading Run's Study Context, which should restore in Review.

### 5. Shared runtime sanity

- Start one Replay or Historical Backtest run.
- [PASS] Confirm the normal TDA → Watch → Review runtime is used rather than a separate Lab-only workflow.
- [PASS] Confirm Models in Play are not auto-selected merely because the run is Replay/Backtest.
- [PASS] Confirm time-aware behavior uses the selected historical timestamp rather than the wall clock for Replay/Historical Backtest.
- [PASS] Confirm obvious navigation between TDA, Live Watch, and Post-Market Review remains functional.

### 6. Persistence

- [PASS] Make at least one meaningful persisted change in the active run.
- Restart the application.
- [PASS] Confirm the active Trading Day/Run restores.
- [PASS] Confirm the run environment, Trade Plan revision, study context, competency focus, and review data remain associated with the same run.
- [PASS] Confirm no unrelated launcher defaults are mistaken for restored run state.

### 7. Regression sweep

- Open each top-level tab once:
  - Trade Plan
  - Guided TDA
  - Study Find
  - Trade Summary
  - Study Review
- [PASS] Confirm each renders without obvious visual breakage.
- [PASS] Exercise at least one editable control on any area touched by the feature branch.
- [PASS] Confirm no duplicate runs, duplicated controls, or stale state appear after navigation.

---

## Current branch acceptance — Competency / Proficiency substrate v0

Before merging `feature/competency-proficiency-v0`, additionally confirm:

- [PASS] Exactly the expected plan-owned competencies are shown in non-Live competency focus controls.
- [PASS] Live does not expose competency focus selection.
- [PASS] Competency selections made at run launch survive into Post-Market Review.
  - Originally failed: Study Review section is missing from Post-Market Process Review for the environments that don't require a Focus question (Forward Test, Replay)
  - Resolved: Competency-only run intent is now persisted; verified in Replay and Forward Test with a blank question.
- [PASS] Competency selections survive application restart as part of the persisted run.
- [PASS] The launcher itself does **not** repopulate prior-run competency selections after restart.
- [PASS] Competency focus is described as evidence provenance/training focus, not as a proficiency score.
- [PASS] No readiness percentage, automatic promotion/demotion, fixed threshold, or proficiency-based Live lock has appeared accidentally.
- [PASS] Full automated suite is green immediately before merge.

---

## Current branch acceptance — Configurable summary templates v0

Before merging `feature/configurable-summary-templates-v0`, additionally confirm:

- [PASS] Workbench exposes both Study Find and Trade Summary template kinds.
- [PASS] Publishing a valid edit creates a new immutable template revision.
- [PASS] The newly published Study Find revision is used by generated Study Find output.
- [PASS] The newly published Trade Summary revision is used by generated Trade Summary output.
- [PASS] Active template revisions persist after application restart.
- [PASS] Generated Study Find output includes the active template name/revision provenance footer.
- [PASS] Generated Trade Summary output includes the active template name/revision provenance footer.
- [PASS] An unknown field such as `{does_not_exist}` is rejected rather than publishing a broken revision.
- [PASS] Full automated suite is green immediately before merge.
  - Verified: 277 passed in 106.21s before the final provenance regression test was added; final rerun after the provenance change reported 278 green.

---

## Current branch acceptance — Competency evidence v0

Before merging `feature/competency-evidence-v0`, additionally confirm:

- [PASS] Full automated test suite is green.
  - Operator confirmed full suite green on 2026-10-08.
- [PASS] A focused Historical Backtest / Study run with competency focus still follows the normal Review workflow without visible regression.
  - Operator manually verified the flow on 2026-10-08.
- [PASS] Competency evidence is created through the existing Study Review path rather than requiring a second scoring form.
- [PASS] No proficiency percentage, automatic competency-state change, promotion/demotion, eligibility change, or evidence-maturity threshold appears in the operator workflow.
- [PASS] Schema migration to v28 does not prevent normal application startup/use in the tested workflow.


---

## Reporting results

Report results as:

- **PASS** — behavior matches the checklist.
- **FAIL** — behavior does not match the checklist; include exact steps and observed result.
- **QUESTION** — behavior is consistent but its intended semantics are unclear.
- **NOT TESTED** — explicitly skipped.

For a failure, capture:

1. environment,
2. exact sequence of actions,
3. expected result,
4. observed result,
5. whether it survives restart,
6. terminal traceback/log if any.

The goal is reproducibility, not speed.
