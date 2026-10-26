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

## Current branch acceptance — Milestone E1 expected vs observed QT/AMDX

Before merging `feature/context-maturity-e1-v0`, use this focused acceptance pass.

### A. Migration and existing QT behavior

- [PASS] Confirm the application opens normally after migration to schema **v34**.
  - Where: launch Cockpit, then check database schema if convenient
  - Look for: normal startup; no migration/runtime error
  - Expected: `PRAGMA user_version` = **34** and existing runs still load.

- [PASS] Confirm normal TDA QT / AMDX entry still behaves as before.
  - Where: start a Process Run and open the Premarket Thesis QT / AMDX controls
  - Look for: raw QT facts, technician phase controls, time-derived month role
  - Expected: existing TDA behavior is unchanged; the time-derived month remains read-only.

### B. Expected versus observed Review

- [PASS] Confirm Post-Market Review shows a separate **QT / AMDX — expected vs observed** section.
  - Where: advance a run to **Post-Market Review > Market Review**
  - Look for: expected/TDA summary, observed phase selectors, optional context note, descriptive comparison
  - Expected: the original TDA interpretation is visible as **Expected / TDA** and is not edited from this Review surface.

- [PASS] Confirm observed values compare descriptively against expected values.
  - Where: in the expected-vs-observed section
  - Look for: set one level equal to expected, change one level, and leave another unknown
  - Expected: comparison uses **Matched / Changed / Expected Unknown / Observed Unknown / Not Comparable** as appropriate; no numeric score appears.

- [PASS] Confirm time-derived QT roles remain factual rather than becoming editable hindsight.
  - Where: observed QT selectors in Post-Market Review
  - Look for: the derived calendar-month role
  - Expected: the derived role is read-only and remains consistent with market-time context.

### C. Persistence and historical honesty

- [PASS] Confirm saving observed QT context does not rewrite the TDA expectation.
  - Where: enter observed values and a context note, then return to/reopen Review
  - Look for: expected value and observed value on a changed level
  - Expected: both remain distinct, e.g. **Expected M -> Observed D**; the expected/TDA value is unchanged.

- [PASS] Confirm observed QT review survives restart.
  - Where: save at least one observed phase plus the optional context note, close/reopen Cockpit, restore the run
  - Look for: observed selectors, note, and comparison
  - Expected: observed context and note rehydrate exactly; expected context remains the original run context.

- [PASS] Confirm Review entry does not automatically create competency evidence.
  - Where: record an observed QT/AMDX mismatch
  - Look for: competency evidence / Review Development evidence records
  - Expected: no evidence record is created merely because expected and observed QT differ.

### D. Regression

- [PASS] Confirm Market Review and Process Review still remain separate stages.
  - Where: Post-Market Review
  - Look for: interpretation classification on stage 1; process adherence/takeaway on stage 2
  - Expected: E1 adds QT comparison without collapsing or rearranging the existing review semantics.

- [PASS] Confirm the full automated suite is green.
  - Where: terminal
  - Look for: `pytest`
  - Expected: all tests pass; schema is **v34**.


---

## Current branch acceptance — E4 compact operator context surfaces

Operator reported manual testing complete and acceptance granted on **2026-10-10**. The E4 checklist below is recorded as **PASS** based on that report; developer automated and offscreen checks are separate evidence.

Run `pytest`, then use the normal application and the disposable fixture window:

```bash
python tools/context_surface_demo.py
```

The fixture window has no database or feed connection. Scenario/Mode selectors create disposable Replay runs at **2026-10-06 10:15 ET**. Event titles explicitly say Fixture; they are not an actual calendar for that date.

### A. Compact presentation and reachability

- [PASS] Confirm the card is compact with details initially hidden in TDA.
  - Where: fixture **Available / TDA**, **Market context** above Focus/Deck
  - Look for: Available; two events and one schedule fact; raw QT distinct from AMDX expectation
  - Expected: no extra input or acknowledgement required; existing station navigation remains usable.
- [PASS] Confirm all Premarket Thesis controls remain reachable at your usual window size.
  - Where: normal application or fixture, **Deck > Premarket Thesis**, then Focus
  - Look for: existing QT selectors, Models in Play, day-specific watch-point controls, station content, and fixed process actions
  - Expected: vertical scrolling can reach lower controls; expand/collapse **Show context details** without losing navigation.

### B. Availability honesty

- [PASS] Cycle the fixture through **Available empty / Not Configured / Unavailable / Legacy**.
  - Where: fixture Scenario selector
  - Look for: Available empty says the query completed with no matching events; Not Configured/Legacy and Unavailable say context is unknown
  - Expected: unknown context never reads as a normal schedule or a successful empty calendar. Unavailable details contain the deliberate fixture outage; Legacy detail has no fabricated provider/query/capture provenance.
- [PASS] Confirm normal startup without a configured provider displays **Not Configured**.
  - Where: normal application, a new Replay/Historical or Forward/Live run
  - Expected: no fixture events leak into production runs and existing launch/authorization behavior is unchanged.

### C. Quiet Watch timing

- [PASS] Select fixture **Available / Watch**.
  - Look for: next recorded **Fixture FOMC 14:00 ET**; **Fixture early close 16:00 ET** is a separate schedule fact
  - Expected: the past 08:30 CPI remains in details rather than being presented as upcoming. Times follow the fixture's historical date, not the current day. No event automatically declares stand-down or entry permission.

### D. Historical detail and Review

- [PASS] Select fixture **Available / Review**, then **Show context details**.
  - Look for: run ID/environment/Trade Plan Alpha 0.7, raw QT, expected/observed interpretation, snapshot status/provider, 18:00-to-18:00 query bounds, historical reference time, capture time, and all three events with native/source provenance
  - Expected: detail is read-only, scrollable, and bounded; existing Market Review / Process Review and expected-vs-observed controls remain intact. Event/schedule facts do not become QT distortion or restrictions.
- [PASS] Confirm restored normal-application context stays attached to the same run.
  - Where: start or restore a run in the normal application, view details, restart the application, restore that run
  - Expected: snapshot status/provider/query/reference/capture provenance and stored event records are unchanged. A legacy run remains unknown. Details may reopen collapsed; that is transient UI state.

### E. Acceptance checkpoint

- [PASS] Full automated suite is green locally; schema remains **v35**, Trade Plan **Alpha 0.7**.
- [PASS] Record PASS/FAIL/QUESTION for the checks above before E4 merge.

---

## Current branch acceptance — E5 declarative context rules

Operator acceptance is **PASS** on 2026-10-10: all eight E5 checks were marked PASS and pushed in operator commit `2e76e9dedf0dc85e059bdf94181d62a5fbc12617`. These scenarios use unpublished fixture rules; Alpha 0.7 retains its manual trading-day gate and no automatic exclusions.

Run `pytest`, then launch:

```bash
python tools/context_policy_demo.py
```

The fixture has no database, real calendar, or orders. It freezes historical market time in every environment. Rules apply only in fixture **Live**; that fixture setting is not inferred account policy.

### A. Clock rule and entry effect

- [PASS] In **Live / Watch**, cycle **Clock before cutoff / Clock exactly cutoff / Clock after cutoff**.
  - Expected: before/exactly 11:00 have no context effect; after 11:00 shows Matched / Block New Entry, and the Fixture setup is BLOCKED despite cleared manual gates and its satisfied criterion. Scroll or inspect the compact situation brief for the candidate status.
- [PASS] Select **Clock warning**.
  - Expected: Matched / Warning; the otherwise-clear fixture setup is AUTHORIZED. Set Trading day permitted to Pending or Blocked and confirm it becomes BLOCKED; a warning never clears another gate.

### B. Event availability and coverage

- [PASS] Cycle **Event matched / Event empty / Event unavailable / Unknown blocks**.
  - Expected: respectively Matched / Block New Entry; Not Matched / no effect; Unknown / Warning; Unknown / Block New Entry. No unavailable context is presented as a clear calendar.
- [PASS] Select **Week coverage unknown**, then expand context details.
  - Expected: Unknown / Warning with incomplete calendar-week coverage reason; the day snapshot cannot prove a clear week.

### C. Applicability, detail, and existing behavior

- [PASS] Select **Clock after cutoff**, switch from Live to Replay, Historical Backtest, and Forward Test.
  - Expected: Not Applicable / No effect in details, and the otherwise-clear fixture setup is AUTHORIZED. The fixture rule explicitly lists Live; real account applicability remains unconfigured.
- [PASS] Inspect **TDA / Watch / Review** and **Show context details** for a matching or unknown rule.
  - Expected: stable compact navigation and bounded read-only detail; plan revision E5 fixture (unpublished), rule ID/rationale/environments, matched/unknown effects, market-time reasons and event IDs. Review does not use today's wall clock or silently refresh the snapshot.
- [PASS] Select **Legacy rules**, then start/restore a normal Alpha 0.7 run.
  - Expected: no declarative rule effects; existing manual gates/criteria remain in force. Legacy runs have empty rules. Existing persisted context and Review workflows remain usable after v36 migration.
- [PASS] Full automated suite is green locally; schema **v36**, published Trade Plan **Alpha 0.7**. Record this focused pass before merge.

---

## Current branch acceptance — E6 local Forex Factory JSON captures

**Operator acceptance: PASS** on 2026-10-10. All nine results were pushed in `df4cac894f7e697bf65793c5f031265af5bdd9d4`; the operator reported **425 passed** for the local automated suite. Developer automated/offscreen validation is separate from these checks. Schema **v37**, published Trade Plan **Alpha 0.7**. Merged through PR #59 (`aaa931153f165b8ebb90c43126e00b6cd07beeeb`).

For a disposable database and synthetic export files:

```bash
python tools/context_import_demo.py
```

The terminal prints a sandbox directory and the exact restart command. It contains `fixture.json`, `revised.json`, `wrong-week.json`, and `malformed.json`; these are synthetic, not a calendar for that date. The window opens **Trade Plan > Process > Calendar captures** with Sunday **2026-10-04** selected. Replay launch is staged at **2026-10-06 10:15 ET**. Captures are never pre-imported or preselected by the demo. Reuse the printed `--data-dir` command for restart checks.

- [PASS] Preview is separate from save and selection.
  - Where: **Calendar captures > Preview JSON export…**, choose the sandbox's `fixture.json`.
  - Look for: three native records, declared UTC week October 4–10, import time, file reference, digest, mapping/adapter revisions, and explicit limitations.
  - Expected: preview has not created a saved capture or selected a provider. **Save capture** stores it; **Use selected capture for new runs** is still a separate action. Navigation does not start a run from this tab.
- [PASS] Malformed and wrong-week files are rejected atomically.
  - Where: keep week **2026-10-04**, preview `wrong-week.json`, then `malformed.json`.
  - Look for: an explicit import error; Save disabled; no extra saved capture.
  - Expected: failed import does not become an empty successful calendar or replace the source selected for new runs.
- [PASS] Explicit selection supplies the shared run loop.
  - Where: choose the saved fixture capture and click **Use selected capture for new runs**; go to **Review / Development > Practice & Launch**, select Replay at **2026-10-06 10:15**, then **Begin Process Run**.
  - Look for: TDA **Market context** shows captured records and source completeness unverified. Expand details.
  - Expected: capture ID, import time, declared week, and native rows belong to this run. Native High impact is preserved; status, precision, type, and affected-market applicability remain unknown. Manual gates remain authoritative.
- [PASS] Watch does not turn uncertain export clocks or bank holidays into exact day facts.
  - Where: follow the normal TDA transition (complete stations or record the deliberate incomplete override), then Watch; inspect details.
  - Look for: uncertain timing and source schedule applicability; native clock values remain inspectable in details.
  - Expected: no precise upcoming event or confirmed futures closure is inferred from these rows. No automatic stand-down, warning policy, entry permission, or readiness score appears.
- [PASS] Review preserves source and run provenance.
  - Where: **Finish Live Watch / Enter Review > Show context details**.
  - Look for: Replay / Rehearsal, Alpha 0.7, requested futures-day bounds, historical market reference, separate source import/capture provenance, original native rows and limitations.
  - Expected: TDA expectation and observed Review remain separate; viewing context does not refresh the source or create competency evidence.
- [PASS] A second capture does not rewrite a started run.
  - Where: return to **Calendar captures**, preview/save `revised.json`, and select it for future runs; return to the existing run's Review.
  - Look for: the earlier capture ID and earlier previous values remain in the started run; both captures remain in the dropdown.
  - Expected: later import/selection affects only future starts. Duplicate titles remain distinct capture-local rows; neither import claims provider occurrence continuity.
- [PASS] Restart restores run context and leaves new-run source selection explicit.
  - Where: close the demo; restart using the printed command with the same sandbox directory.
  - Look for: the same restorable run/source snapshot and both saved captures; new-run selection reads Not Configured.
  - Expected: restore uses saved facts without provider query. Explicitly choosing Not Configured for future starts does not remove historical context. A selected capture queried for **2026-10-13** yields Unavailable with its attempted provenance, rather than Available empty.
- [PASS] The real export format and normal application remain usable.
  - Where: optionally download Forex Factory **Weekly Export > JSON**, then use normal **Calendar captures** with that file's actual Sunday UTC week.
  - Look for: successful preview of native rows and source limitations; XML/CSV/ICS are not supported in this slice.
  - Expected: compare representative rows to the saved file; a historical calendar page does not imply a historical weekly download. Without explicit selection, normal new runs remain Not Configured. If real-source checking is skipped, retain NOT TESTED or document the limitation.
- [PASS] Full local automated suite passes; v37 and Alpha 0.7 are verified.
  - Where: `python -m pytest`, normal startup/restoration, database schema if convenient.
  - Expected: no regression in TDA/Watch/Review, progression, manual authorization, or previously saved runs. Record the exact local result and any concerns before merge.

---

## Current branch acceptance — E7 model/playbook context predicates

**Operator acceptance: PASS — all nine checks** on 2026-10-11. The original results are recorded in `8f1ad50c6a62c37c1b331ad0ca84a7542b33aa87`; the controlled 242 persistence retest passed in `19ecc042b1562e128799a0cc0b7c2bc1fa6edd8b`. Check 243 passed the controlled E6→E7 retest recorded in `9454414b7da5be9ad131d6683fd95b42f7aefc62`; this checkpoint reconciles its checkbox with the operator’s confirmed observations. PR #60 merged on 2026-10-11 as `f57794cff6f128830655b458e999fd8f72038280`. Schema **v37**, published Trade Plan **Alpha 0.7**. E7 was implemented on `feature/context-maturity-e7-v0` and is now on `main`; developer checks do not replace these nine operator checks. The Friday Asian Range Monday relationship and policy adoption remain open.

Launch a separate acceptance database from the repository root:

```bash
python tools/context_predicate_demo.py --data-dir /tmp/ict-e7-acceptance
```

The terminal prints the directory and restart command. The demo uses synthetic models, source facts, completeness guarantees and effects; no real calendar or published rule is installed. Default reference is Friday **2026-10-09 10:15 ET**. Offset 0 explicitly selects Monday **October 5**; the following-Monday scenario explicitly selects **October 12**. Scenario/environment changes build a new unsaved fixture. Use **Save fixture** and **Restore saved fixture** explicitly; reuse the same `--data-dir` for restart checks. Save before concluding the run.

- [PASS] Scoped effects reach only the targeted Playbook candidate.
  - Where: default **Monday event present**, follow the normal TDA transition into Watch (complete the stations or record the deliberate incomplete override).
  - Look for: **Fixture Friday model** has Not Matched / Block New Entry; **Other fixture model** and **Custom fixture** retain their own authorization results.
  - **Custom fixture** appears in Watch's **Setups in Play** with a synthetic TDA IF/THEN watch point. The reference-model summary counts only the two Playbooks. If using the earlier demo, update and select a new fixture; restoring an older saved fixture preserves its original missing watch point.
  - The earlier missing Custom card was reproduced and corrected by seeding its required TDA watch point. Operator retest is PASS in the results checkpoint above; this supersedes the earlier FAIL/pending-retest wording.
  - Expected: the absence prerequisite is contradicted by the Monday event. Clear manual gates cannot bypass the targeted block, and other candidates do not inherit it. Details show Playbook scope and capture-local/event IDs, not title-based strategy matching.
- [PASS] Proven absence grants no manual permission.
  - Where: **Complete Monday empty**; expand context details and inspect Watch authorization.
  - Look for: Matched / Informational, with the complete synthetic Monday window and explicit coverage basis.
  - Expected: the initially clear fixture gates permit its synthetic candidate. Setting **Trading day permitted** to Pending or Blocked prevents entry despite the satisfied predicate; changing back to Clear remains an operator action. No competency/readiness or model-definition state is changed.
- [PASS] Unknown is preserved, with explicit warning versus blocking behavior.
  - Where: **Incomplete coverage**, **Unknown timing**, **Not Configured**, then **Unknown blocks**.
  - Locator: keep **Replay**, click **Show context details**, then scroll inside that text box to **Candidate context: Fixture Friday model**. Read the result beneath that heading; the earlier general rule result may be Not Applicable. Scenario changes create new fixtures; do not click Restore during this comparison.
  - Look for: Unknown / Warning for the first three; Unknown / Block New Entry for the last.
  - Expected: no missing or uncertain source is called no-news. Warning adds no permission and never clears a manual gate. Unknown blocks affects only the targeted Playbook candidate; other/custom candidates retain their own gates and criteria.
- [PASS] Calendar relationship is explicit and explainable.
  - Where: **Following Monday unverified > Show context details**.
  - Locator: under **Candidate context: Fixture Friday model**, expect **Unknown / Warning** and **Event window (America/New_York)** bounds on **2026-10-12**. The separate **Source coverage bounds** line correctly remains on **2026-10-05**.
  - Look for: resolved NY bounds on October 12 and Unknown because the synthetic source only guarantees October 5.
  - Expected: current-week evidence does not prove next-week absence. The fixture's explicit offset is visible and is not adopted as the real Friday Asian Range rule.
- [PASS] Candidate/environment exclusion precedes missing data.
  - Where: **Other playbook only**, then choose **Live**, **Forward Test** or **Historical Backtest** in the demo environment selector.
  - Look for: scoped rule Not Applicable with no effect when its Playbook is absent or its fixture environment is excluded.
  - Expected: no scope leakage or blanket day block. The demo keeps its frozen synthetic timestamp; the environment selector is not a live data feed or an execution connection.
- [PASS] TDA, Watch and Review explain the same stored predicate/source.
  - Where: default **Monday event present**, inspect context in TDA, advance to Watch, then **Finish Live Watch / Enter Review > Show context details**.
  - Look for: E7 fixture plan revision, stored candidate ID/revision, October 5 bounds, rule rationale, configured effects, event ID and the same Not Matched / Block New Entry result.
  - Expected: context evaluation does not fetch a calendar, rewrite source facts, grant entry or create competency evidence. Expected-versus-observed Review stays separate.
- [PASS] Saved predicates restore through source/configuration changes and restart.
  - Where: in Review, **Save fixture**; change to **Complete Monday empty** or **Legacy rules**, then **Restore saved fixture**. Close and reopen with the same command and directory; click Restore again.
  - Look for: the original saved run ID, Review state, candidate revision, Monday event and blocking result.
  - Expected: current scenario/definition changes do not replace stored rules or facts. The label identifies restored state; scenario controls describe new fixtures. No provider query occurs during restore.
  - Controlled operator retest PASS: `/tmp/ict-e7-242-retest/demo.db`, saved run `edca6b3f-e64d-4f8a-a9fd-570b633dfa80`. Restoring after Legacy rules and again after restart retained the same ID, Review, `fixture-friday@fixture-v0`, Not Matched / Block New Entry and event `fixture-monday`. This closes the earlier unrecorded-ID QUESTION. Bare launches had opened different sandboxes, rather than demonstrating a restoration failure.
- [PASS] Legacy/manual operating behavior remains intact.
  - Where: **Legacy rules**, then normal application startup and restore of an earlier E6 run/capture.
  - The Legacy fixture check needs no restart. A demo launch starts a new unsaved Monday-event fixture; Restore is explicit. Earlier E6 captures belong to the normal application or their original E6 sandbox, rather than the E7 fixture database.
  - Look for: no declarative fixture effects in the legacy scenario; normal Alpha 0.7 gates, capture selection and existing TDA/Watch/Review behavior.
  - Expected: Alpha 0.7 has no new automatic news policy. Missing older rule fields preserve run-wide scope and no not-matched effect; source completeness/precision remain honest.
  - Normal application opened. Calendar captures contained only Not Configured, so earlier E6 capture/run restoration could not be checked.
  - Controlled replacement check: `python tools/e6_compatibility_demo.py --data-dir /tmp/ict-e6-e7-compatibility`. See `E7_OPERATOR_GUIDE.md` for the staged observations. It creates a synthetic database with accepted E6 code at `42e3b346`, keeps an untouched original backup and manifest, and opens the normal E7 application. This is explicit old-version compatibility evidence, not recovered operator history. The completed controlled retest below supersedes the earlier NOT TESTED status.
  - Controlled E6→E7 compatibility retest PASS. Original run 16b5fe86-e5d3-4f4a-b9da-432afe1be23f and capture ee87fcdd-1423-4f91-bcdc-9b69dbe904f2 preserved. Review restored after restart; selecting the revised capture for new runs left the existing snapshot at native previous 1%.
- [PASS] Full local automated suite passes; v37 and Alpha 0.7 remain unchanged.
  - Where: `python -m pytest`, normal startup/restoration, database schema if convenient.
  - Expected: exact local result recorded, no regression in stored runs, candidate gates, progression or context capture workflow. Prior developer full result after the Custom fixture correction was **453 passed** on both Python 3.10 and 3.12; later focused support verification was **33 passed** on both versions.
  - Review verification before merge: **456 passed in 273.30s** on Python 3.12.14 / PySide6 6.8.3 / pytest 9.1.1, clean exit without warnings. The merged main tree matches the reviewed/tested PR head. Operator results above remain separate.
  - Compatibility-support developer verification: **456 passed** on Python 3.10.22 and 3.12.14. After an archive-extraction warning cleanup, the final compatibility/document tests were **6 passed** on each version. These results do not change the recorded operator result or replace check 243.
  - Operator result on 2026-10-11: **Python 3.10.12, pytest 9.1.1, pluggy 1.6.0; 454 collected, 454 passed**. Recorded at `8f1ad50c6a62c37c1b331ad0ca84a7542b33aa87`, whose source/tests match parent `25ac4e5dd062fdab2539abf0c5d76317ddf5b322`. Elapsed time and PySide6 version were not supplied.

---

## AMDX — durable Watch/TDA entry v0

Use `AMDX_ENTRY_OPERATOR_GUIDE.md` and `python tools/amdx_entry_demo.py` for the separate retained Replay sandbox. All six checks 245–250 are PASS per the operator results pushed on 2026-10-11 in `17b874b2c7fb48f2b35d2e30b9e2a6affe019072`; earlier acceptance results above are preserved. Final layout and the later quartet-revision interaction changes remain separate follow-up work.

- [PASS] Working AMDX shows daily/session quartet context and nearby higher QT provenance; inspection creates no revision or station completion.
  - Where: retained AMDX entry sandbox, fixed Working AMDX panel in TDA.
  - Expected: NYAM daily Q3 and its separate 90m Q3 are distinct; higher context is visible with legacy/derived provenance.
- [PASS] One deliberate current-quarter phase choice records immediately and implies its quartet siblings without a Save/Record step.
  - Where: current NYAM 90m Q3 at the initial synthetic reference; choose M.
  - Expected: child quartet XAMD, Q3 entered, siblings implied, Day unresolved and station still incomplete.
- [PASS] Watch supports direct daily/90m updates without returning to Analysis or propagating a parent role into its child quartet.
  - Where: enter Watch, select daily NYAM/Q3 and choose D.
  - Expected: daily AMDX with unresolved X subtype; child XAMD retained; existing gates and Return to Analysis remain available.
- [PASS] X subtype and later accepted revisions remain distinct from Unknown, with earlier interpretation records retained.
  - Where: daily NYPM/Q4; select X(R), then X(?) through the direct/secondary choices.
  - Expected: explicit reversal then unresolved X subtype; no quarter-correctness score, raw active history list or automatic competency evidence.
- [PASS] Restart restores the same sandbox run and committed working profiles without fixture Save or reseeding.
  - Where: close/reopen using the same AMDX entry command/directory.
  - Expected: original run identity and daily/90m claims retained; transient navigation may follow the current reference.
- [PASS] Clock/reference advancement follows current-quarter entry but preserves a deliberately pinned edit target and creates no interpretation by itself.
  - Where: Demo reference → Advance by 90 minutes, inspect/pin a quarter, advance again, then Follow current.
  - Expected: default follows current, pinned target stays explicit, Follow current releases it, and navigation/time advancement records no phase.

### AMDX one-entry working-quartet revision — focused operator smoke

Use `AMDX_QUARTET_REVISION_OPERATOR_GUIDE.md` on `feature/amdx-quartet-revision-v1` and the fresh retained sandbox `/tmp/ict-amdx-quartet-v1`. Checks 251–254 are PASS, recorded from the operator’s 2026-10-12 message: “Smoke test complete. This feels much smoother.” This accepts the four-check functional smoke set; no separate per-check log, runtime version or elapsed time was supplied. All previous 250 identities, results and comments are preserved. Schema v39 / Alpha 0.7.

- [PASS] Normal phase and X subtype choices follow the selected quarter's legal positions across both AMDX and XAMD.
  - Where: Working AMDX Day row; inspect Q1, Q2, Q3 and Q4.
  - Expected: Q1 A/X, Q2 A/M, Q3 M/D, Q4 D/X; invalid direct/subtype choices disabled. Inspection does not record or complete anything.
- [PASS] One new valid entry changes the working quartet without old-anchor cleanup, and clearing does not reactivate retired phases.
  - Where: Day Q1=A, then Q3=M, then Clear this anchor at Q3.
  - Expected: AMDX → XAMD in one new entry → Unresolved on clear. Old Q1=A stays historical rather than returning; the 90m child and process state remain separate.
- [PASS] X subtype stays only at the same compatible X quarter, and repeating an identical explicit choice adds no interpretation revision.
  - Where: Day Q4=X(R), Q3=D, repeat D, then Q3=M.
  - Expected: AMDX retains Q4=X(R); repeat reports Already current; switching to XAMD gives Q1=X(?) rather than copying R.
- [PASS] Unknown and quartet applicability remain distinct, and the new working claims restore through normal restart.
  - Where: XAMD with explicit Q1=X(?) and Q3=M; choose Q3=Unknown, Not Applicable, Unknown, Clear Not Applicable; mark Not Applicable again and restore with Q3=M; restart using the same sandbox directory.
  - Expected: conditional Unknown / M is honest; Unknown does not undo Not Applicable; clear does not restore old phases; one valid input restores XAMD; the same run and committed profile reopen without Save or reseeding.

### AMDX observed quartet entry — native Review smoke

Use `AMDX_OBSERVED_ENTRY_OPERATOR_GUIDE.md`, branch `feature/amdx-observed-entry-v1` and `python tools/amdx_observed_entry_demo.py --data-dir /tmp/ict-amdx-observed-v1`. Checks 255–259 are PASS from the operator’s 2026-10-12 report, “All points passed,” following clarification of check 258 and fresh-sandbox restart guidance. No separate per-check log, fixture/run ID, local runtime version or elapsed time was supplied. The original premature-close error’s cause remains unconfirmed; the report accepts the functional retest, not a diagnosis of that original fixture. All previous 254 identities/statuses/comments are preserved. Schema v41 / Alpha 0.7; comparison controls remain deferred.

- [PASS] Review shows the saved reviewed-day quartet and records an independent observed phase immediately without Save, baseline choice or station completion.
  - Where: synthetic Review fixture, NYAM 90m Q3; choose M.
  - Expected: child XAMD, Day unresolved, entered/implied distinctions and quiet higher context; no AMDX comparison/history panel.
- [PASS] Observed quartet correction needs one new valid entry, with one-click X(C)/X(R) and no subtype transfer to a different X quarter.
  - Where: Day NYPM/Q4; choose X(R), then X(C), then Day NYAM/Q3=M.
  - Expected: AMDX with R then C; new Q3=M gives XAMD and Asia X(?), with child profile unchanged and prior judgments retained.
- [PASS] Review enforces structural positions and distinguishes repeated explicit no-op, Unknown, whole-quartet applicability and clear.
  - Where: inspect Day Q1–Q4; repeat Q3=M; choose Unknown, Not Applicable, Clear Not Applicable, then Q3=M.
  - Expected: roles A/X, A/M, M/D, D/X; repeated explicit choice reports Already current; clear never revives retired anchors; one valid choice restores XAMD.
- [PASS] Reviewed-day/session targets survive clock rollover and failed observed writes preserve committed meaning until deliberate retry.
  - Where: inspect all sessions, select NYAM 90m Q3, advance Demo reference into another trading day; enable simulated observed write failure and choose D, disable it and choose D again.
  - Expected: reviewed date remains 2026-10-08; navigation records nothing; failure says Not recorded and retains XAMD; deliberate retry gives AMDX with no partial/automatic action.
- [PASS] Restart restores the same Review run and committed observed quartets after rollover without Save or reseeding.
  - Where: disable fixture fault; close/reopen the same observed demo directory and inspect edited NYAM if necessary.
  - Expected: same run, Review mode, saved reviewed date and Day/90m judgments; transient navigation is not mistaken for interpretation history.

### AMDX Review date provenance — focused correction smoke

Use `AMDX_REVIEW_DATE_OPERATOR_GUIDE.md` and `python tools/amdx_review_date_demo.py --data-dir /tmp/ict-amdx-review-date-v1`. Check 260 is PASS from the guided operator reports on 2026-10-12. All previous 259 identities/statuses/comments are preserved; schema v41 / Alpha 0.7 are unchanged.

- [PASS] Review uses its run's preserved original date despite older container labeling, survives clock rollover/restart, and rejects a different-date additional run before resetting process state.
  - Where: separate retained date-provenance sandbox, synthetic container 2026-10-08 / run reference 2026-10-09; follow the four numbered guide checkpoints.
  - Expected: Observed date 2026-10-09; enter NYAM 90m Q3=M for XAMD; advance clock to Trading Day 2026-10-10 without moving the target/recording; reopen the same run/profile, inspecting NYAM if needed; after concluding, a different-date additional launch says Run not started with the explicit new-day path and no reset/new run.
  - Operator guided report, 2026-10-12 (America/Denver): upper Trading Day advanced to October 10 while Observed AMDX remained October 9; NYAM 90m Q3=M was entered and the profile was XAMD. After window-X close and same-directory reopen, the date remained October 9; selecting NYAM restored XAMD and Q3 entered without another phase choice. After Conclude Trading Run, Start Another Trading Run created no second run and displayed: "Run not started - selected reference belongs to Trading Day 2026-10-13. Complete the current Trading Day, then choose Start New Trading Day". The October 13 request is the live reference after restart, not a change to the saved Review date. The heading-tooltip inspection was not separately reported; no operator hover acceptance is inferred.

## AMDX Lab historical catalog — focused native trial

Use `AMDX_CATALOG_LAB_OPERATOR_GUIDE.md` and `python tools/amdx_catalog_lab_demo.py --data-dir /tmp/ict-amdx-catalog-lab-v1`. The retained 16:9 frame hosts the same native widget as the normal application's AMDX Lab tab. Close/reopen at any point with the same directory; there is no run to conclude. Schema v42 / Alpha 0.7 remain unchanged from the catalog foundation; earlier 260 records retain their identities/results/comments. Operator checks 261–264 are PASS from the explicit 2026-10-13 report: "Smoke test 261-264 passed. Saved locally but not yet committed or pushed". The local file/any additional notes have not been inspected or imported; this checkpoint records the reported result.

- [PASS] 1998 NYAM 90-minute Q3=M records immediately as XAMD without a run or Save action.
  - Where: Study references → Initial 1998 example · NYAM 90m Q3; right heading 90-minute Q3 / 90m 3 Observed; click M.
  - Expected: bottom 90-minute row Profile XAMD and Q3 M entered; Recorded or valid unchanged-meaning status on a repeated trial.
- [PASS] X(R) is available directly in one click at the same 90-minute quartet's Q1.
  - Where: bottom 90-minute row Q1; right heading 90-minute Q1; click X(R).
  - Expected: Q1 X(R) entered, XAMD, and retained Q3 M entered; no subtype menu or separate Save.
- [PASS] The older 1985 Yearly Q3=D entry records a separate higher occurrence as AMDX.
  - Where: Study references → Older 1985 example · Yearly Q3; date 1985-08-12 09:15; right heading Yearly Q3 / Jul–Sep Observed; click D.
  - Expected: Yearly Profile AMDX and Q3 D entered, without overwriting the 1998 90-minute interpretation.
- [PASS] Closing/reopening restores the catalog, historical reference, selected quarter and both independent profiles.
  - Where: close while 1985 Yearly Q3 is selected; reopen with the same command/directory, then choose the Initial 1998 preset.
  - Expected: 1985-08-12 / Yearly Q3 / D entered / AMDX restore without entry; 1998 NYAM 90-minute remains XAMD with Q1 X(R) and Q3 M entered. Preset navigation records no phase.

## Shared maintained AMDX calendar — native trial

Use `AMDX_SHARED_NATIVE_OPERATOR_GUIDE.md` and `python tools/amdx_shared_calendar_demo.py --data-dir /tmp/ict-amdx-shared-native-v0`. The separate retained synthetic MNQ Replay fixture starts with Yearly AMDX; final rendering remains deferred. Existing 264 records are preserved. Checks 265–269 are PASS from the explicit 2026-10-13 operator report.

Operator report, 2026-10-13 (America/Denver): “All checks passed. The step by step guide was helpful.” Checks 265–269 are PASS from that explicit report. No separate additional observations, local note commit or user-side push are inferred.

- [PASS] Historical Observed backfill uses the maintained MNQ Lab with immediate Yearly Q3=D entry and no collection destination or run creation.
  - Where: guide checkpoint 265, Shared trial historical 1985 preset.
  - Expected: 1985 Yearly AMDX / Q3 D entered; maintained-calendar heading.
- [PASS] Bound Watch shows the quiet shared current stack and records 90m Q3=M plus direct one-click Q1 X(R).
  - Where: guide checkpoint 266, Shared trial Watch preset, top Working AMDX 90m row.
  - Expected: 90m XAMD / M and X(R) entered; higher Yearly AMDX; no history/comparison list.
- [PASS] Full stack from Watch records a larger Expected Yearly thesis edit and returns the same current profile to Watch.
  - Where: guide checkpoint 267, Full AMDX stack, Yearly Q3=M, return Trade Plan tab.
  - Expected: Yearly XAMD in both views; 90m entry unchanged; no separate Save.
- [PASS] Same-directory restart retains the shared current stack and independent older Observed backfill without re-entry.
  - Where: guide checkpoint 268, window-X close/reopen and historical preset inspection.
  - Expected: current Yearly/90m XAMD; 1985 Observed Yearly AMDX/Q3 D remains.
- [PASS] Review opens the immutable original launch stack read-only after later current-calendar corrections.
  - Where: guide checkpoint 269, Review preset, Working context captured at run launch, Full AMDX stack.
  - Expected: retained launch Yearly AMDX and absent 90m Unresolved; disabled phase/reference controls; current correction does not replace captured basis.

## Maintained Observed Review — native trial

Use `AMDX_REVIEW_CALENDAR_OPERATOR_GUIDE.md` and `python tools/amdx_review_calendar_demo.py --data-dir /tmp/ict-amdx-review-calendar-v0`. This separate retained synthetic fixture opens Review for 2026-10-09. Schema v45 / Alpha 0.7; the prior 269 identities/results/comments remain unchanged. Checks 270–274 are PASS from the explicit 2026-10-13 operator report.

Operator report, 2026-10-13 (America/Denver): checks 270–274 passed; smoke-test notes saved locally but not committed or pushed. This checkpoint records the reported result; the local file and any additional notes have not been inspected or imported.

- [PASS] A legal Observed Review phase entry immediately appears in the same maintained Lab calendar without a second entry or Save.
  - Where: guide checkpoint 270, Review NYAM 90m Q3=M, then same-quartet Observed Lab preset.
  - Expected: both current views show XAMD / Q3 M entered.
- [PASS] Direct one-click X(R) records the shared Observed judgment and makes a captured run assessment available without selecting an Expected baseline.
  - Where: guide checkpoint 271, Review 90m Q1, X(R).
  - Expected: XAMD / Q1 X(R) entered / Q3 M entered; Captured run assessment available.
- [PASS] A subsequent Lab correction updates current Review orientation while preserving its prior assessment.
  - Where: guide checkpoint 272, same-quartet Observed Lab Q3=D, return Review.
  - Expected: current Lab and Review AMDX / Q3 D entered; captured assessment still available.
- [PASS] Read-only captured run assessment reconstructs its original Observed revision after later calendar corrections.
  - Where: guide checkpoint 273, Captured run assessment.
  - Expected: retained XAMD / Q1 X(R) and Q3 M; disabled phase/reference controls; distinct from original Expected launch inspection.
- [PASS] Clock advancement and same-directory restart retain the original reviewed day, current judgment and immutable captured assessment without re-entry.
  - Where: guide checkpoint 274, advance display, window-X close/reopen, inspect assessment.
  - Expected: October 9 Review/NYAM current AMDX; captured XAMD with X(R)/M unchanged.

## Bounded higher Observed Review — native trial

Use `AMDX_HIGHER_REVIEW_OPERATOR_GUIDE.md` and `python tools/amdx_higher_review_demo.py --data-dir /tmp/ict-amdx-higher-review-v1`. This separate retained synthetic MNQ fixture uses the 2026/2027 calendar boundary; its future reference is not market data or a prediction. Schema v46 / Alpha 0.7. Earlier 274 identities/results/comments remain exact; checks 275–280 are PASS from the explicit 2026-10-13 operator report.

Operator report, 2026-10-13 (America/Denver): “275-280 passed”. This records the reported functional result. Local notes and their commit/push status were not supplied or inspected.

- [PASS] Higher Review defaults to the exact original launch context and records Yearly Q1 X(C) immediately.
  - Where: guide checkpoint 275, Review full AMDX stack, Original launch / 2027 Yearly Q1.
  - Expected: reviewed day January 1, explicit original/selected references and whole-day bounds, XAMD / Q1 X(C) entered without Save.
- [PASS] Selecting the preceding evening exposes separate higher occurrences without inheriting phase judgments.
  - Where: guide checkpoint 276, Reviewed day start / December 31 context.
  - Expected: 2026 yearly Q4, 2023 quadrennial and 2011 16-year occurrences all Unresolved; original reference and reviewed day remain January 1.
- [PASS] Direct X(R) records the old-year AMDX profile while navigation preserves the independent new-year XAMD and intraday selection.
  - Where: guide checkpoint 277, December 31 Yearly Q4 X(R), switch between contexts, close editor.
  - Expected: old-year AMDX / X(R), new-year XAMD / X(C), no navigation entries or retargeted NYAM.
- [PASS] Inactive monthly and weekly positions remain inspectable without an automatically selected input quarter.
  - Where: guide checkpoint 278, Monthly and Weekly left occurrence cells.
  - Expected: monthly Unassigned / weekly Distortion, disabled phase buttons until explicit Q1–Q4; no Q5 or automatic Not Applicable.
- [PASS] A failed higher assessment rolls back the calendar judgment and requires deliberate recovery without replay.
  - Where: guide checkpoint 279, fixture failure menu, attempt old-year Q4 X(C), remove fault and Reload.
  - Expected: Entry not recorded / disabled controls, old-year X(R) / AMDX retained; no partial command or automatic retry.
- [PASS] Restart restores valid higher navigation and both independent profiles while the captured assessment retains its original scope read-only.
  - Where: guide checkpoint 280, same-directory window-X restart, higher editor, Captured run assessment.
  - Expected: old-year Q4 X(R) / AMDX and new-year Q1 X(C) / XAMD; retained proof distinguishes January 1 launch from December 31 selection; original Expected launch remains unresolved.

## Native Watch decision dock — focused trial

Use `WATCH_NATIVE_DECISION_DOCK_OPERATOR_GUIDE.md` and `python tools/watch_decision_dock_demo.py --data-dir /tmp/ict-watch-decision-dock-v0`. This retained synthetic MNQ Replay fixture verifies one native contextual-completion loop over the existing maintained AMDX command. Schema v46 / Alpha 0.7; all earlier 280 identities/results/comments remain exact. Checks 281–285 are PASS from the explicit 2026-10-15 operator report.

Operator report, 2026-10-15 (America/Denver): “281-285 pass”. This records the reported functional result without inferring final Watch styling/layout approval.

- [PASS] The chart-edge reference opens in native Watch with exact active target, Alpha 0.7 provenance and truthful unavailable-definition state.
  - Where: guide checkpoint 281, Plan reference button or P outside text entry.
  - Expected: same active 90-minute target/profile as Working AMDX; no fixture rule presented as published policy.
- [PASS] Active 90-minute Q3 exposes only legal M/D choices and one D selection updates the shared maintained quartet before dismissing.
  - Where: guide checkpoint 282, decision dock at fixed 09:15 reference.
  - Expected: main row Q3 D entered / AMDX, focus returned, no A/X, duplicate command or Save.
- [PASS] Selected 90-minute Q4 exposes direct X(?) / X(C) / X(R), and one X(R) decision synchronizes the main projection.
  - Where: guide checkpoint 283, main Q4 target then decision dock X(R).
  - Expected: Q4 X(R) plus retained Q3 D / AMDX, immediate dismissal and no subtype menu or second Save.
- [PASS] Escape, outside-click and text-entry paths restore context without recording or stealing lowercase p from Watch observations.
  - Where: guide checkpoint 284, popup dismissal and observation field.
  - Expected: no AMDX side effects; Plan reference remains the anchor; P shortcut works only outside text editing.
- [PASS] The two constrained chart relationships move the same dock and the chosen profile survives same-directory restart.
  - Where: guide checkpoint 285, Workspace profile menu, reopen same directory.
  - Expected: bottom/left placement changes only presentation; AMDX target/data remain; no unrestricted docking.

## Native Watch contextual Study Find — focused trial

Use `WATCH_CONTEXTUAL_STUDY_FIND_OPERATOR_GUIDE.md` and `python tools/watch_contextual_study_find_demo.py --data-dir /tmp/ict-watch-contextual-study-find-v0`. This retained synthetic MNQ Replay fixture verifies the existing Study Find draft/save/managed-image path through a temporary Watch projection. Schema v46 / Alpha 0.7; all earlier 285 identities/results/comments remain exact. Checks 286–290 are PASS from the explicit 2026-10-16 operator report.

- [PASS] Contextual capture opens only in active Watch with supported saved fields and explicitly display-only run/time/AMDX basis.
  - Where: guide checkpoint 286, Capture Study Find or Ctrl+Shift+F.
  - Expected: 2026-10-09 / MNQ / NYAM saved fields; exact Watch basis labeled current-context-only; no process movement.
- [PASS] Escape/outside dismissal and same-directory restart restore one existing Study Find draft without reconstruction or default substitution.
  - Where: guide checkpoint 287, partial contextual draft, dismiss/reopen/restart.
  - Expected: same draft identity/text; Resumed existing draft; no final Study Find or Watch transition.
- [PASS] Clipboard screenshot paste uses the managed Study Find attachment path and survives contextual dismissal/reopen.
  - Where: guide checkpoint 288, Paste chart or Ctrl+V with an image clipboard.
  - Expected: one managed attachment retained; empty clipboard changes nothing.
- [PASS] Save & return uses the existing repository/image association and restores unchanged Watch context.
  - Where: guide checkpoint 289, completed contextual capture, full Study Find and Study Review inspection.
  - Expected: one saved item/image; same run/mode/AMDX; no process, evidence or competency side effect.
- [PASS] Invalid save remains local and a non-empty custom draft is never overwritten by current Watch defaults.
  - Where: guide checkpoint 290, required-field failure, custom full-tab draft, contextual reopen/leave Watch.
  - Expected: actionable validation; same draft/custom fields; leaving Watch closes support and retains draft.

Operator report, 2026-10-16 (America/Denver): “286–290 PASS”. This records the functional result without inferring final Watch styling/layout or future durable context-link acceptance.

## Native quiet-Watch composition — focused trial

Use `WATCH_QUIET_COMPOSITION_OPERATOR_GUIDE.md` and `python tools/watch_quiet_composition_demo.py --data-dir /tmp/ict-watch-quiet-composition-v0`. This retained synthetic MNQ Replay fixture composes the existing Live Watch, maintained AMDX command, accepted contextual tools and truthful process-safety projection. Schema v46 / Alpha 0.7; all earlier 290 identities/results/comments remain exact. Operator checks 291 and 293–295 PASS; 292 FAIL pending correction retest.

- [PASS] Active Watch presents one simultaneous chart-facing edge, operating canvas, compact AMDX now and always-visible safety strip without duplicating the full AMDX editor.
  - Where: guide checkpoint 291, default tv-left profile and normal 16:9 view.
  - Expected: current cues are quickly reacquired; only the operating canvas scrolls; quiet state does not demand attention.
- [PASS] AMDX now selects the maintained target and records legal roles/X subtypes through the same immediate command with no second Save or Watch history route.
  - Where: guide checkpoint 292, 90m Q4, X(R), then Plan reference.
  - Expected: one command updates both projections and quartet profile; illegal choices remain unavailable.
- [PASS] Safety keeps unavailable distinct from safe and gives changed authorization facts earned salience without adding P&L or broker actions.
  - Where: guide checkpoint 293, default state and Trial safety state gate toggle.
  - Expected: unavailable broker/account/risk/position/orders remain explicit; blocked gate is locally apparent; no invented broker change.
- [PASS] Plan reference and contextual Study Find retain their accepted owner, recovery/save and focus-return behavior from the chart-facing edge.
  - Where: guide checkpoint 294, dismiss/reopen/save both support surfaces.
  - Expected: same Watch/run/AMDX/safety anchor; no process transition or duplicate draft/command owner.
- [PASS] Named tv-left/tv-below profiles move one orientation edge and survive restart without changing run, process or AMDX state.
  - Where: guide checkpoint 295, Workspace profile, restart and optional full AMDX lens route.
  - Expected: placement only changes; no arbitrary docking; Lab inspection does not transition the Trading Run.

Operator report, 2026-10-17 (America/Denver): 291 and 293–295 PASS; 292 FAIL. Choosing 90m Q4 X(R) left both compact Watch and Plan reference Unknown / Unresolved. Developer reproduction after a workspace round trip found a retained cancelled-gesture flag rejecting the new decision. The correction starts a fresh gesture only after exact token/legality validation and retains command errors across compact refreshes. Check 292 remains FAIL until the operator retest; preserve the retained trial directory.

Operator retest, 2026-10-17 (America/Denver): “292 passed” after published correction `6561f2c`. All checks 291–295 now PASS. The initial failure record above is historical; this accepts bounded native composition behavior, not final styling or merge.

## Study-first startup — focused trial

Use `STUDY_FIRST_STARTUP_OPERATOR_GUIDE.md` and the retained separate `tools/study_startup_demo.py`. Checks 296–300 PASS; operator results published in `953c812`.

- [PASS] Idle startup opens Study with truthful empty-state and ordinary navigation away.
  - Where: guide checkpoint 296.
  - Expected: no invented recommendation or active run; direct capture and calendar routes.
- [PASS] Study this competency stages the existing launcher without creating a run or governance record.
  - Where: guide checkpoint 297.
  - Expected: selected competency and Historical Backtest; explicit question/reference and Begin Process Run remain required.
- [PASS] Active-run restart restores its runtime and Study offers safe resume without a conflicting launch.
  - Where: guide checkpoint 298.
  - Expected: same run, environment and mode; Study staging disabled while active.
- [PASS] Study Find draft resumes unchanged through doorway navigation and restart.
  - Where: guide checkpoint 299.
  - Expected: same capture text; capture draft is not called an active process run.
- [PASS] Recorded Study suggestions disclose current-revision basis and retain manual selection.
  - Where: guide checkpoint 300.
  - Expected: recorded note and timestamp, no invented skill ranking or old-revision adoption.

## Integrated Study task — focused trial

Use `INTEGRATED_STUDY_TASK_OPERATOR_GUIDE.md` with the separate `tools/integrated_study_task_demo.py`. Checks 301–305 PASS; operator results published in `6b04866`.

- [PASS] Investigation question stays beside the maintained calendar and historical reference.
  - Where: guide checkpoint 301.
  - Expected: retained question, shared legal entry, truthful unconfigured definitions, no implicit run.
- [PASS] Explicit capture association preserves displayed investigation context without replacing capture fields.
  - Where: guide checkpoint 302.
  - Expected: immutable question/reference/plan snapshot and actual recording time; draft retained; no competency evidence.
- [PASS] Later investigation edits cannot reassign an already linked capture.
  - Where: guide checkpoint 303.
  - Expected: original association remains; different relink rejected with an explanation.
- [PASS] Saved Review and restart retain original association and current editable investigation separately.
  - Where: guide checkpoint 304.
  - Expected: saved find shows original question; current question restores; New investigation preserves existing captures.
- [PASS] Reduced-height access uses scrolling and investigation navigation preserves active-run ownership.
  - Where: guide checkpoint 305.
  - Expected: controls reachable around 1280×720; no run replacement or automatic completion.

## Native mapped TDA Focus — focused trial

Use `TDA_MAPPED_FOCUS_OPERATOR_GUIDE.md` and the separate `tools/tda_mapped_focus_demo.py`. Operator checks 306–310 PASS, published in `bbf44f8`. The actual first Deck has five stations; final four-chart assignment is not accepted by this trial.

- [PASS] Adjacent map and Focus share observation/selection without navigation marking complete.
  - Where: guide checkpoint 306.
  - Expected: correct chart position and role, shared summary, preserved work.
- [PASS] Splitter resizing retains both panes and Alt+1–4 preserves ordinary numeric typing.
  - Where: guide checkpoint 307.
  - Expected: resize is layout only; shortcuts select spatial slots without completion.
- [PASS] Full Deck overview opens the chosen station beside the matching current-Deck map.
  - Where: guide checkpoint 308.
  - Expected: unchanged multi-Deck layout and no automatic certification.
- [PASS] Explicit completion updates only the selected station and advances the map across the Deck boundary.
  - Where: guide checkpoint 309.
  - Expected: next Deck map matches Focus and previous work remains.
- [PASS] Restart restores station work, selection, completion and split width in the separate trial.
  - Where: guide checkpoint 310.
  - Expected: unfinished work remains unfinished; no Trading Run is created.

Historical operator note: 310 needed a resized-window restart correction. The correction was retested and all 306–310 checks now PASS.

## Shared workspace restoration — focused trial

Use `WORKSPACE_RESTORATION_OPERATOR_GUIDE.md` with the existing startup demo and a new separate directory. Operator reports checks 311–312 PASS (2026-10-21).

- [PASS] Normal cockpit close/reopen restores main-window size and position while preserving startup routing.
  - Where: guide checkpoint 311.
  - Expected: idle Study remains the starting workspace; geometry restores without process writes.
- [PASS] Study Review divider restores even after closing from another workspace.
  - Where: guide checkpoint 312.
  - Expected: prior proportions remain when Review is reopened; hidden panes do not overwrite preferences.

## Study criteria browser/editor — focused trial

Use `STUDY_CRITERIA_EDITOR_OPERATOR_GUIDE.md` with a new separate directory. All examples are synthetic.

- [PASS] Criteria inspection preserves calendar selection and AMDX values.
  - Where: guide checkpoint 313.
- [PASS] Explicit Q2 input and Q1 output save as a Candidate without adoption or evaluation.
  - Where: guide checkpoint 314.
- [PASS] Candidate editing creates a new retained revision, preserving the original priority.
  - Where: guide checkpoint 315.
- [PASS] Role constraints, invalid-value recovery and unsaved-draft return behave as explained.
  - Where: guide checkpoint 316.
- [PASS] Both saved criterion revisions reopen without creating a Trading Run.
  - Where: guide checkpoint 317.

## Reusable criteria scopes — focused trial

Use `AMDX_REUSABLE_SCOPES_OPERATOR_GUIDE.md` with a new synthetic directory.

- [PASS] Changing Fixed Q2 to Reusable Q2 saves a separate candidate revision.
  - Where: guide checkpoint 318.
- [PASS] Next-date inspection preserves fixed input identity while previewing reusable Q2 on the selected date.
  - Where: guide checkpoint 319.
- [PASS] Reopening and editing preserve the reusable descriptor without automatic adoption or evaluation.
  - Where: guide checkpoint 320.

## Integrated criterion Study — focused trial

Use `STUDY_CRITERION_OPERATOR_GUIDE.md` and the seeded synthetic demo. This tests a coherent question/observation/result workflow, not trading validity.

- [PASS] No observations produces an unsaved Unknown explanation without creating a run.
  - Where: guide checkpoint 321.
- [PASS] A sourced synthetic observation produces a Matched preview and saves only on explicit action.
  - Where: guide checkpoint 322.
- [PASS] False and later-available observations yield distinct Not Matched and Unknown results; changed inputs invalidate previews.
  - Where: guide checkpoint 323.
- [PASS] Reopening recovers the original question, criterion and observations for each separate saved result.
  - Where: guide checkpoint 324.

## Multi-day criterion Study — focused trial

Use `STUDY_MULTIDAY_OPERATOR_GUIDE.md` and a new seeded synthetic directory.

- [NOT TESTED] Next-day Study retains the criterion/question but starts with empty observations and an Unknown preview.
  - Where: guide checkpoint 325.
- [NOT TESTED] Separately saved days retain their own evidence; inspecting the first does not retarget the second day's inputs.
  - Where: guide checkpoint 326.
- [NOT TESTED] Reopening recovers both dated results and truthful coverage counts without calendar changes.
  - Where: guide checkpoint 327.

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
