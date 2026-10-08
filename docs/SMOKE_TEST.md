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
- Confirm the main window opens normally.
- Confirm no unexpected traceback, crash, or teardown error appears.
- If an active Trading Day/Run existed before restart, confirm the application restores the active runtime surface rather than losing the run.
- Confirm previously persisted run evidence/review data still appears where expected.

### 2. Trade Plan shell

- Open **Trade Plan**.
- Confirm the expected Trade Plan revision is displayed.
- Confirm the left-side sections render and can be selected.
- Open **Process** and confirm both **Process Map** and **Run Trading Day** tabs render.
- Open **Review / Development** and confirm the Lab / Replay launcher renders.

### 3. Environment launcher

For each environment, verify the visible controls match its purpose.

#### Historical Backtest / Study
- Select **Historical Backtest**.
- Confirm the purpose reads **Study**.
- Confirm a historical New York market-time selector is visible.
- Confirm Study Intent fields are visible.
- Confirm all plan-owned competency focus checkboxes are visible.
- Confirm a focused study question is required before the run can begin.

#### Replay / Rehearsal
- Select **Replay**.
- Confirm the purpose reads **Rehearsal**.
- Confirm a historical New York market-time selector is visible.
- Confirm Run Intent and competency focus controls are visible.
- Confirm intent is optional.

#### Forward Test / Validation
- Select **Forward Test**.
- Confirm the purpose reads **Validation**.
- Confirm no historical-time selector is shown.
- Confirm Run Intent and competency focus controls are visible.

#### Live / Execution
- Select **Live**.
- Confirm the purpose reads **Execution**.
- Confirm historical-time and study/competency controls are hidden.
- Confirm no competency/proficiency state is being presented as an automatic Live authorization lock unless that behavior has been explicitly implemented in a later revision.

### 4. Study competency provenance

Use Historical Backtest for this test.

- Enter a distinctive study question.
- Optionally enter a hypothesis and scope.
- Select at least two competency focus checkboxes.
- Begin the Process Run.
- Complete enough of TDA to reach the later runtime/review surfaces.
- Confirm the run continues to use the same Trade Plan revision.
- Reach Post-Market Review.
- Confirm the selected competency names appear under the run's competency focus.
- Restart the application while the run is still restorable.
- Confirm Post-Market Review still shows the same competency focus.

**Expected launcher behavior after restart:** the Lab / Replay launcher is a doorway for a *new* Process Run. Its form selections are not a draft of the restored/previous run and are not expected to repopulate from persisted run state. The persisted source of truth is the started Trading Run's Study Context, which should restore in Review.

### 5. Shared runtime sanity

- Start one Replay or Historical Backtest run.
- Confirm the normal TDA → Watch → Review runtime is used rather than a separate Lab-only workflow.
- Confirm Models in Play are not auto-selected merely because the run is Replay/Backtest.
- Confirm time-aware behavior uses the selected historical timestamp rather than the wall clock for Replay/Historical Backtest.
- Confirm obvious navigation between TDA, Live Watch, and Post-Market Review remains functional.

### 6. Persistence

- Make at least one meaningful persisted change in the active run.
- Restart the application.
- Confirm the active Trading Day/Run restores.
- Confirm the run environment, Trade Plan revision, study context, competency focus, and review data remain associated with the same run.
- Confirm no unrelated launcher defaults are mistaken for restored run state.

### 7. Regression sweep

- Open each top-level tab once:
  - Trade Plan
  - Guided TDA
  - Study Find
  - Trade Summary
  - Study Review
- Confirm each renders without obvious visual breakage.
- Exercise at least one editable control on any area touched by the feature branch.
- Confirm no duplicate runs, duplicated controls, or stale state appear after navigation.

---

## Current branch acceptance — Competency / Proficiency substrate v0

Before merging `feature/competency-proficiency-v0`, additionally confirm:

- Exactly the expected plan-owned competencies are shown in non-Live competency focus controls.
- Live does not expose competency focus selection.
- Competency selections made at run launch survive into Post-Market Review.
- Competency selections survive application restart as part of the persisted run.
- The launcher itself does **not** repopulate prior-run competency selections after restart.
- Competency focus is described as evidence provenance/training focus, not as a proficiency score.
- No readiness percentage, automatic promotion/demotion, fixed threshold, or proficiency-based Live lock has appeared accidentally.
- Full automated suite is green immediately before merge.

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
