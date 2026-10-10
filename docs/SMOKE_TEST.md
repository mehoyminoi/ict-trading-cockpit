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

## Current branch acceptance — Competency evidence Review / Development v0

Before merging `feature/competency-evidence-review-v0`, additionally confirm:

- [PASS] Full automated test suite is green.
  - Operator confirmed green on 2026-10-08.
- [PASS] Trade Plan -> Review / Development shows the Competency Evidence panel.
- [PASS] Newly reviewed focused competency evidence appears in the panel.
- [PASS] Evidence detail shows understandable competency, environment/purpose, outcome, Trade Plan revision, question/scope, and review note context.
- [PASS] All Competencies shows accumulated evidence across competencies.
- [PASS] Filtering to one competency limits the records correctly.
- [PASS] Summary counts are understandable.
- [PASS] The panel reads as evidence/history rather than a scorecard and does not silently change proficiency or eligibility.
- [PASS] Operator reports no current implementation/function concerns with this surface.


---

## Current branch acceptance — Evidence to targeted Study routing v0

Before merging `feature/competency-study-routing-v0`, additionally confirm:

- [PASS] Full automated test suite is green.
- [PASS] **Study this competency** stages Historical Backtest / Study rather than silently starting a run.
- [PASS] The selected competency becomes the sole competency focus.
- [PASS] An existing Study question is preserved when the routing action is clicked after entering the question.
- [PASS] With an existing Study question, the status clearly directs the technician to **Begin Process Run**.
- [PASS] With no Study question, the status clearly requires one before **Begin Process Run**.
- [PASS] **Begin Process Run** successfully starts the focused Historical Study after the staged intent is complete.
- [PASS] Progression eligibility still blocks higher environments and guides the technician back toward the permitted rung.
- [PASS] No competency score, state change, eligibility promotion, or Evidence Maturity decision is inferred by the routing action.
  - Operator manually re-verified the question-first workflow after the guidance fix on 2026-10-08.


---

## Current branch acceptance — Development Direction v0

Before merging `feature/development-direction-v0`, use this section as the primary manual checklist.

### A. Review / Development layout

- [PASS] Open **Trade Plan -> Review / Development** at the normal desktop window size.
  - Expected: the application window remains usable on-screen rather than growing taller than the display.
  - Expected: Review / Development has its own vertical scrollbar when the full content does not fit.
  - Expected: the lower **Lab / Replay** launcher and its **Competency focus** area remain reachable by scrolling and are not compressed to an unusable height.
  - Originally failed during Development Direction testing: the page's combined content made the window too tall and compressed the lower launcher/focus area.
  - Resolved and manually verified: Review / Development is scrollable and the evidence list is capped more compactly.

### B. Save a Development Direction

- [PASS] Select one competency in the **Competency Evidence** filter.
- [PASS] In **Development Direction**, choose a direction and enter a distinctive synthesis note.
- [PASS] Click **Save Development Direction**.
  - Expected immediately under the editor:
    - `Current · <direction> · <note> ...`
    - a supporting-evidence count or `no supporting evidence linked`
    - a save-status message explicitly stating that no Competency State or eligibility change was made.
- [PASS] Navigate away and return, then restart the application.
  - Operator verified on 2026-10-08 that the Development Direction and synthesis note persist.

### C. Supporting-evidence link

- [PASS] Select a specific evidence row in the evidence list.
- [PASS] Check **Link the selected evidence record as supporting evidence** and save the Development Direction.
  - Expected immediately:
    - `Current ... · supporting evidence: 1` (or a higher count if other records were already linked),
    - `Selected evidence link · linked`,
    - the checkbox remains checked while that linked evidence row is selected.
- [PASS] Navigate away and return.
  - Expected: when the same linked evidence row is selected, the checkbox is checked and `Selected evidence link · linked` is shown.
- [PASS] Restart the application and return to the same competency/evidence record.
  - Expected: the supporting-evidence count still appears and the checkbox/link-status reflect the persisted link for that selected record.
- [PASS] Select a different evidence row for the same competency.
  - Expected: the checkbox reflects *that selected record's* link state. It may be unchecked even though the Development Direction still reports one or more other supporting-evidence links.
- [PASS] Uncheck the checkbox for a linked selected record and save.
  - Expected: that selected evidence ID is removed from the Development Direction while unrelated supporting-evidence links remain intact.

**Clarification from the first manual pass:** the supporting-evidence ID was persisted in v29 storage, but the original UI did not restore/display the checkbox state or persistent link summary after refresh/restart. That made a persisted link look lost and could also make a later save accidentally remove it. The UI/persistence handling has been corrected; the checks above verify the visible behavior and the stored relationship together.

### D. Guardrails

- [PASS] Saving/changing a Development Direction does not change the competency's broader Competency State.
- [PASS] Saving/changing a Development Direction does not promote eligibility or create an Evidence Maturity conclusion.
- [PASS] No Development Direction is inferred automatically from a Study Outcome.
- [PASS] Full automated suite is green immediately before merge.


---

## Current branch acceptance — Competency Synthesis v0

Before merging `feature/competency-synthesis-panel-v0`, use this section for the focused manual acceptance pass.

### A. Compact synthesis surface

- [PASS] Open **Trade Plan -> Review / Development** and select one specific competency.
  - Expected: the existing compact evidence summary becomes a **Competency Synthesis** summary rather than adding another tall panel.
  - Expected: Review / Development remains vertically scrollable and the lower Lab / Replay launcher remains comfortably reachable.
- [PASS] Confirm the synthesis identifies the selected competency and current Trade Plan revision.
- [PASS] Confirm it shows the current human-authored **Development Direction** and supporting-evidence count when one exists.

### B. Descriptive evidence coverage

- [PASS] For a competency with reviewed evidence, confirm the synthesis shows:
  - total reviewed evidence count,
  - descriptive count by purpose (Study / Rehearsal / Validation as actually present),
  - descriptive count by Study Outcome,
  - oldest -> newest reviewed evidence date range.
- [PASS] For a competency with no reviewed evidence, confirm it explicitly says no reviewed evidence is recorded rather than implying failure.
- [PASS] Confirm the synthesis explicitly states that coverage is descriptive only and does not infer proficiency, Evidence Maturity, or eligibility.

### C. Revision/provenance guardrail

- [PASS] Select evidence records and confirm the detailed evidence view still shows each record's Trade Plan revision.
- [PASS] Confirm the synthesis does **not** display a generic warning merely because evidence could span multiple whole Trade Plan revisions.
  - Rationale: a meaningful future caution depends on whether the competency definition itself changed, not merely whether the surrounding Trade Plan revision changed.
- [PASS] Confirm older evidence remains visible; nothing is silently remapped to the current competency definition.

### D. Regression / automation

- [PASS] Saving/changing Development Direction immediately updates the compact synthesis direction/supporting-evidence count.
- [PASS] Existing evidence selection, detail view, supporting-evidence linking, and **Study this competency** routing remain functional.
- [PASS] Full automated suite is green immediately before merge.


---

## Current branch acceptance — Cross-Run Observation v0

Before merging `feature/cross-run-observation-v0`, use this section for the focused manual acceptance pass.

### A. Cross-Run Observation editor

- [PASS] Open **Trade Plan -> Review / Development**, select one competency, and confirm a compact **Cross-Run Observation** editor is visible.
  - Expected: it is presented as human-authored interpretation of what seems to be happening across reviewed runs.
  - Expected: Review / Development remains vertically scrollable and the lower Lab / Replay launcher remains reachable.
- [PASS] Enter a distinctive Cross-Run Observation and save it.
  - Expected: the current observation display updates immediately.
  - Expected: the compact Competency Synthesis includes the saved Cross-Run Observation.
- [PASS] Navigate away and return, then restart the application.
  - Expected: the saved observation persists.

### B. Supporting evidence

- [PASS] Select one evidence record, check the Cross-Run Observation supporting-evidence checkbox, and save.
  - Expected: the selected record is reported as linked.
  - Expected: supporting-evidence count increases.
- [PASS] Link a second evidence record for the same competency.
  - Expected: both links are preserved; adding one record does not remove the previous link.
- [PASS] Unlink one selected supporting record and save.
  - Expected: only that record is removed; unrelated supporting links remain.
- [PASS] Restart and confirm the observation and supporting-evidence relationship persist.

### C. Semantic separation

- [PASS] Save/change a Cross-Run Observation and confirm **Development Direction does not change automatically**.
- [PASS] Save/change Development Direction and confirm the Cross-Run Observation is not rewritten automatically.
- [PASS] Confirm the UI describes Cross-Run Observation as **what seems to be happening** and Development Direction as **what should happen next**.
- [PASS] Confirm no automatic recurring-pattern/weakness detection, trend score, competency-state change, Evidence Maturity conclusion, progression decision, or eligibility change appears.

### D. Revision / regression guardrails

- [PASS] Confirm individual evidence detail still shows its original Trade Plan revision.
- [PASS] Confirm older evidence remains visible and is not silently remapped to a newer competency meaning.
- [PASS] Confirm existing Competency Synthesis counts/date range, evidence selection/detail, Development Direction linking, and **Study this competency** routing still work.
- [PASS] Full automated suite is green immediately before merge.


---

## Current branch acceptance — Evidence Maturity Profile v0

Before merging `feature/evidence-maturity-profile-v0`, use this section for the focused C1 acceptance pass.

### A. Boundary-aware profile

- [PASS] Open **Trade Plan -> Review / Development**, select one specific competency, and confirm an **Evidence Maturity Profile** editor is visible.
  - Expected: the editor clearly describes maturity as whether evidence can support a trustworthy decision, not whether the technician is proficient or eligible.
  - Expected: Review / Development remains vertically scrollable and existing Cross-Run Observation, Development Direction, and Lab / Replay controls remain reachable.
- [PASS] Confirm the progression-boundary selector offers exactly:
  - Study -> Rehearsal,
  - Rehearsal -> Validation,
  - Validation -> Execution.
- [PASS] Save different maturity states/notes for two different boundaries on the same competency.
  - Expected: switching boundaries restores each boundary's own saved state and notes.
  - Expected: one boundary does not overwrite another.

### B. Human maturity state and removability guardrail

- [PASS] Confirm the maturity-state choices are:
  - Not Assessed,
  - Insufficient Evidence,
  - Developing Evidence,
  - Decision-Usable Evidence.
- [PASS] Save a distinctive maturity state and note.
  - Expected: the current Evidence Maturity display and compact Competency Synthesis update immediately.
  - Expected: the state is presented as human-authored governance, not a calculated readiness score.
- [PASS] Confirm the six-dimensional profile remains visible and understandable even when the state is **Not Assessed**.
  - Expected: descriptive evidence facts and human notes do not depend on choosing an evaluative state.
  - This verifies that the overall maturity label remains removable/non-load-bearing.

### C. Six-dimensional profile

- [PASS] For a competency with reviewed evidence, confirm the profile shows all six accepted dimensions:
  - Volume / Sample Depth,
  - Environment Relevance,
  - Recency,
  - Consistency,
  - Context Coverage,
  - Revision Relevance.
- [PASS] Confirm Volume / Sample Depth is descriptive (record/run counts) rather than a pass/fail threshold.
- [PASS] Confirm Environment Relevance reports the actual Study/Rehearsal/Validation evidence distribution rather than automatically declaring relevance sufficient.
- [PASS] Confirm Recency reports evidence dates without automatically declaring evidence stale.
- [PASS] Enter a distinctive **Consistency** note and **Known gap / Context Coverage** note, save, navigate away/return, and restart.
  - Expected: both human-reviewed notes persist for the selected competency + boundary.
- [PASS] Confirm Revision Relevance shows evidence Trade Plan revision provenance and explicitly states that competency-definition equivalence is not yet machine-verifiable.
  - Expected: no generic warning appears merely because whole Trade Plan revisions differ.

### D. Governance separation / regressions

- [PASS] Save/change Evidence Maturity and confirm **Competency State does not change automatically**.
- [PASS] Save/change Evidence Maturity and confirm **Development Direction does not change automatically**.
- [PASS] Confirm saving Evidence Maturity does not promote/demote progression, change eligibility, or create a Live lock.
- [PASS] Confirm there is no numeric readiness percentage, weighted score, traffic-light readiness verdict, or machine-inferred maturity state.
- [PASS] Confirm existing Competency Synthesis, Cross-Run Observation, Development Direction, evidence detail/provenance, and **Study this competency** routing still work.
- [PASS] Restart the application and confirm the selected competency's saved profiles persist separately by progression boundary.
- [PASS] Full automated suite is green immediately before merge.


---

## Current branch acceptance — Progression Policy substrate v0

Before merging `feature/progression-policy-model-v0`, use this section for the focused C2 acceptance pass.

### A. Alpha 0.7 remains unconfigured

- [PASS] Open **Trade Plan -> Rules / Safety**.
  - Expected: a read-only **Progression Policy** section is visible.
  - Expected: Trade Plan **Alpha 0.7** reports **NOT CONFIGURED** for Progression Policy.
  - Expected: the UI explicitly says no readiness rule is inferred.
- [PASS] Confirm no Study/Rehearsal/Validation/Execution launcher behavior changes merely because the policy substrate exists.
  - Expected: C2 defines policy data only; it does not evaluate or enforce eligibility.

### B. Policy substrate guardrails

- [PASS] Confirm the current application still opens normally with schema **v31**.
  - Expected: C2 adds no database schema migration.
- [PASS] Confirm the current Trade Plan revision remains **Alpha 0.7**.
  - Expected: the first real configured progression policy has not been smuggled into the current published plan.
- [PASS] Confirm there is no numeric readiness score, percentage, traffic-light verdict, automatic promotion/demotion, or manual progression override.
- [PASS] Confirm existing Evidence Maturity, Cross-Run Observation, Development Direction, competency evidence, and targeted Study routing still work.

### C. Read-only policy representation

This branch intentionally ships with no configured Alpha 0.7 policy. Automated tests exercise synthetic configured policies.

- [PASS] Confirm the Rules / Safety Progression Policy text clearly separates:
  - Trade Plan policy definition,
  - later eligibility evaluation.
- [PASS] Confirm the operator-facing text does not imply that NOT CONFIGURED means approved or available.

### D. Regression

- [PASS] Confirm existing Trade Plan sections remain navigable and render normally.
- [PASS] Full automated suite is green immediately before merge.


---

## Current branch acceptance — Explainable Eligibility v0

Before merging `feature/explainable-eligibility-v0`, use this section for the focused C3 acceptance pass.

### A. Alpha 0.7 behavior remains unchanged

- [PASS] Open the Lab / Replay launcher and cycle through Replay, Forward Test, and Live.
  - Expected: each still reports **NOT CONFIGURED** under Trade Plan Alpha 0.7.
  - Expected: NOT CONFIGURED remains non-restrictive; no new progression lock appears.
- [PASS] Confirm Historical Backtest / Study remains **AVAILABLE** as the foundation environment.
- [PASS] Confirm Trade Plan revision remains **Alpha 0.7** and no actual progression criteria were added.

### B. Eligibility explanation semantics

- [PASS] Confirm the launcher still clearly labels progression eligibility separately from trade/setup authorization.
- [PASS] Confirm no readiness percentage, weighted score, traffic-light score, automatic Competency State mutation, automatic Evidence Maturity mutation, or automatic Development Direction mutation appears.
- [PASS] Confirm the operator-facing language preserves:
  - AVAILABLE,
  - NOT CONFIGURED,
  - BLOCKED,
  without treating NOT CONFIGURED as approval.

### C. Human Certification substrate

- [PASS] Confirm the application opens normally after migration to schema **v32**.
  - Expected: the new progression-certification persistence does not disrupt existing data.
- [PASS] Confirm Alpha 0.7 does not show a Human Certification editor because it has no configured progression-policy requirements.
  - Expected: certification controls only exist when an actual Human Certification requirement is present in a configured policy.

### D. Existing learning loop regression

- [PASS] Confirm Evidence Maturity still loads/saves by competency + boundary.
- [PASS] Confirm Cross-Run Observation and Development Direction remain usable.
- [PASS] Confirm targeted **Study this competency** routing still stages Historical Backtest / Study correctly.
- [PASS] Confirm existing Trade Plan sections and Process runtime remain navigable.

### E. Automated evaluator coverage

Synthetic policies are exercised by automated tests because Alpha 0.7 intentionally has no real progression policy.

- [PASS] Full automated suite is green immediately before merge.
  - Expected focused coverage includes:
    - configured AVAILABLE when every requirement is satisfied,
    - configured BLOCKED for missing evidence,
    - current-Trade-Plan-revision evidence scoping,
    - older-revision Evidence Maturity -> UNKNOWN / current-plan review,
    - Human Certification persistence and blocking semantics,
    - configured BLOCKED launcher prevention,
    - Alpha 0.7 NOT CONFIGURED non-restrictive behavior.


---

## Current branch acceptance — Regression / downgrade semantics v0

Before merging `feature/regression-downgrade-semantics-v0`, use this section for the focused C4 acceptance pass.

### A. Alpha 0.7 remains behaviorally unchanged

- [PASS] Confirm the application opens normally after migration to schema **v33**.
- [PASS] Confirm Trade Plan remains **Alpha 0.7** with no real progression policy.
- [PASS] Confirm Replay, Forward Test, and Live still report **NOT CONFIGURED** and remain non-restrictive under Alpha 0.7.
- [PASS] Confirm no Progression Attainment is created merely by viewing/cycling launcher environments.

### B. Historical attainment semantics

The current Alpha 0.7 plan cannot manually exercise a real configured crossing; synthetic configured policies are covered by automated tests.

- [PASS] Confirm operator-facing language does not imply that current eligibility rewrites historical attainment.
- [PASS] Confirm the system continues to distinguish:
  - Competency State,
  - current Eligibility,
  - historical Progression Attainment,
  - Development Direction.
- [PASS] Confirm no automatic Competency State, Evidence Maturity, or Development Direction mutation appears.

### C. Regression / revalidation semantics

- [PASS] Confirm Review / Development remains usable and no regression/revalidation controls appear under Alpha 0.7 when there is no configured progression policy.
- [PASS] Confirm terminology does not equate a generic BLOCKED result with competency regression.
- [PASS] Confirm temporary news/risk/personal/account restrictions are not presented as progression regression.
- [PASS] Confirm no time-based skill decay, severity score, readiness percentage, or automatic demotion has appeared.

### D. Existing learning loop regression

- [PASS] Confirm Evidence Maturity still loads/saves by competency + boundary.
- [PASS] Confirm Cross-Run Observation and Development Direction remain usable.
- [PASS] Confirm targeted **Study this competency** routing still stages Historical Backtest / Study.
- [PASS] Confirm existing Trade Plan sections and Process runtime remain navigable.
  - Technically functional but quite taxing to actually interact with.

### E. Automated C4 coverage

- [PASS] Full automated suite is green immediately before merge.
  - Expected focused coverage includes:
    - schema v33 storage,
    - immutable attainment recorded once per plan revision + boundary + policy,
    - never-attained BLOCKED is not regression,
    - same-policy attained -> BLOCKED yields Eligibility Loss Detected,
    - cross-revision attained -> BLOCKED yields Revalidation Required,
    - Regression Review persistence,
    - no automatic Competency State mutation,
    - attainment recorded only when an AVAILABLE boundary is deliberately crossed,
    - Alpha 0.7 NOT CONFIGURED launch creates no attainment,
    - Review / Development distinguishes historical attainment from current BLOCKED eligibility.


---

## Current branch acceptance — Operator-loop friction reduction v0

Before merging `feature/operator-loop-friction-v0`, use this short acceptance pass.

### A. Orientation

- [PASS] Confirm Review / Development opens with a compact Overview and focused work-area tabs rather than one continuous wall of editors.
  - Where: **Trade Plan > Review / Development**
  - Look for: **Overview** plus **Evidence / Interpretation / Progression / Practice & Launch**
  - Expected: Overview remains visible while only one detailed work area is active at a time.

- [PASS] Confirm the selected competency remains the shared context across work areas.
  - Where: **Trade Plan > Review / Development**, competency selector above Overview
  - Look for: select one competency, then switch among the four work-area tabs
  - Expected: the selected competency does not reset merely because you change work areas.

### B. Evidence and Interpretation

- [PASS] Confirm Evidence is easy to locate without scanning Interpretation or Progression controls.
  - Where: **Review / Development > Evidence**
  - Look for: evidence list and selected evidence detail
  - Expected: Cross-Run Observation, Development Direction, and Evidence Maturity editors are not simultaneously visible in this area.

- [PASS] Confirm human synthesis controls are grouped together.
  - Where: **Review / Development > Interpretation**
  - Look for: **Cross-Run Observation** and **Development Direction**
  - Expected: both existing editors remain functional and their saved summaries still appear in Overview.

### C. Progression

- [PASS] Confirm Evidence Maturity is isolated in the Progression work area.
  - Where: **Review / Development > Progression**
  - Look for: **Evidence Maturity Profile**
  - Expected: saved boundary/state/notes still load correctly and no progression/eligibility action is implied by editing maturity.

- [PASS] Confirm Alpha 0.7 remains quiet because no real progression policy is configured.
  - Where: **Review / Development > Progression**
  - Look for: no synthetic progression-standing/regression controls under the normal Alpha 0.7 plan
  - Expected: the UI does not invent readiness criteria, attainment, or regression state.

### D. Practice / Launch

- [PASS] Confirm targeted practice and the Process Run launcher are now in the same focused area.
  - Where: **Review / Development > Practice & Launch**
  - Look for: **Study this competency** and **New Process Run**
  - Expected: the launcher is reachable without scrolling through Evidence/Interpretation/Progression editors.

- [PASS] Confirm targeted **Study this competency** still prepares Historical Backtest / Study correctly.
  - Where: select a competency, then **Practice & Launch > Study this competency**
  - Look for: Historical Backtest selected, competency focus checked, study question ready for entry
  - Expected: existing targeted Study routing behavior is unchanged.

### E. Quiet guidance and regression

- [PASS] Confirm technical headings expose quiet explanatory tooltips.
  - Where: hover **Cross-Run Observation**, **Development Direction**, and **Evidence Maturity Profile**
  - Look for: concise definitions that distinguish what each concept means
  - Expected: definitions provide context without adding another permanent wall of text.

- [PASS] Confirm the full automated suite is green and schema remains **v33**.
  - Where: terminal / database check
  - Look for: pytest green; `PRAGMA user_version` = 33
  - Expected: this usability slice introduces no schema/domain/Trade Plan changes.


---

## Current branch acceptance — C5 operator-loop integration and guardrails v0

Before merging `feature/operator-loop-integration-guardrails-v0`, use this focused acceptance pass.

### A. Alpha 0.7 remains unchanged

- [PASS] Confirm normal Alpha 0.7 Replay, Forward Test, and Live remain **NOT CONFIGURED** and launchable.
  - Where: **Trade Plan > Review / Development > Practice & Launch**
  - Look for: select Replay, Forward Test, and Live in the Process Run launcher
  - Expected: each says **NOT CONFIGURED**; no Stage lower / Review Progression action appears; no real progression threshold has been introduced.

- [PASS] Confirm Historical Backtest remains the foundation Study environment.
  - Where: **Practice & Launch**, select Historical Backtest
  - Look for: boundary text
  - Expected: **Foundation / no boundary required** and the normal focused Study-question requirement remains.

### B. Configured BLOCKED behavior is covered without changing Alpha 0.7

Synthetic configured-policy behavior is primarily covered by automated tests because Alpha 0.7 deliberately publishes no real progression policy.

- [PASS] Confirm operator-facing language remains conceptually clear.
  - Where: **Practice & Launch** progression status
  - Look for: progression eligibility, boundary, concise Next guidance, optional requirement details
  - Expected: progression is described as environment-transition permission, not trade/setup authorization or a readiness score.

- [PASS] Confirm requirement detail is progressive disclosure rather than another permanent wall of text.
  - Where: configured-policy automated/UI test coverage
  - Look for: **Show requirement details**
  - Expected: concise blocker names remain visible; detailed requirement reasoning is hidden until requested.

### C. Lower-rung routing

- [PASS] Confirm blocked progression can stage the normal lower environment without starting a run.
  - Where: configured-policy automated coverage
  - Look for: **Stage recommended lower environment**
  - Expected: Replay blocked -> Study, Forward blocked -> Replay, Live blocked -> Forward; environment is preselected only.

- [PASS] Confirm staging downward preserves semantically valid run intent.
  - Where: configured-policy automated coverage
  - Look for: Study question / competency focus before and after staging
  - Expected: valid intent remains; no Progression Attainment, regression/demotion, or automatic Process Run is created.

### D. Focused Progression explanation

- [PASS] Confirm the launcher can route a blocked operator directly to the Progression work area.
  - Where: configured-policy automated coverage
  - Look for: **Review Progression**
  - Expected: navigation lands at **Trade Plan > Review / Development > Progression**.

- [PASS] Confirm Progression keeps historical and current concepts separate.
  - Where: **Review / Development > Progression**
  - Look for: Evidence Maturity, current eligibility, requirement results, historical attainment/standing where applicable
  - Expected: Eligibility Loss / Revalidation remains distinct from Competency State and does not imply automatic competency regression.

- [PASS] Confirm Human Certification remains authored only under Rules / Safety.
  - Where: configured Human Certification coverage
  - Look for: Progression explains the requirement and points to **Rules / Safety > Progression Policy**
  - Expected: no duplicate editable certification control appears in Review / Development.

### E. Runtime and persistence guardrails

- [PASS] Confirm a legitimately started run is not silently terminated or demoted if progression support later changes.
  - Where: automated C5 coverage
  - Look for: active Forward run after synthetic assessment changes from passing to blocked
  - Expected: the same run remains active with its original environment/provenance; the changed eligibility governs the next upward transition.

- [PASS] Confirm progression gating does not create duplicate attainment by browsing or staging.
  - Where: automated C4/C5 coverage
  - Look for: attainment repository before/after browsing/staging
  - Expected: attainment is created only by a deliberate configured AVAILABLE boundary crossing.

- [PASS] Confirm full automated suite is green and schema remains **v33**.
  - Where: terminal / database check
  - Look for: pytest green; `PRAGMA user_version` = 33
  - Expected: C5 adds integration/presentation wiring only; no new mutable current-status persistence.


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
