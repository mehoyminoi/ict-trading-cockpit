# UX4b — Contextual Study criteria browser/editor

The native AMDX Lab investigation now offers **Study criteria…** for the selected quartet. A modal dialog pins its cycle/reference, while the retained browser lists definitions for the current plan revision and selected layer. Published records and candidates are explicitly labeled; a retained Published record alone does not prove active plan adoption. Empty state remains truthful.

New candidates and new revisions use the UX4a immutable registry. The form separates input quarter(s), typed features/conditions, output quarter, local behavior versus assigned role, X subtype, rationale and priority. All conditions are conjunctive; lower numeric priority wins under the existing policy. Assigned-role options reuse structural domain constraints. Local descriptive behavior can differ from final quartet role. No prose classifier or weighting method is introduced.

Inspection creates no domain writes. Candidate saves do not change calendar judgments, create runs/evaluations or publish/adopt definitions. Editing a published record creates a Candidate revision. Existing revision IDs and evaluated evidence remain unchanged. A storage/validation failure retains the open draft. Return/Escape/window close asks before discarding an active draft; explicit Discard is available. Unsaved drafts are not persisted across process exit.

Existing scopes outside the pinned quartet are labeled and preserved when revising. The browser filters by plan revision and layer, not by assumed temporal applicability. Explicit quarter identity scopes are still not recurring expressions; users must not infer that a saved criterion applies automatically to another date or instrument. Current integration remains the configured MNQ calendar. Historical/current facts are not entered or evaluated by this form.

No schema change (47), broker behavior, classifier, active-run route or published plan change. Reuses the integrated-study demo with a separate directory; operator guide covers 313–317. Next UX4 work is reusable contextual scope semantics and deliberate evaluation/evidence selection, with retained information availability and comparison basis. Final layout remains revisable.

## Verification

25 focused tests pass: six editor/routing checks, six integrated Study regressions, five MainWindow regressions, four immutable definition repository checks and four smoke-document checks. Coverage includes input/output separation, candidate revision retention, published-record preservation, outside-scope preservation, validation/storage failure with draft retention, structural choices and cancel/discard return. Python 3.10 grammar and `git diff --check` pass. Native offscreen renders were visually inspected at 1000×720 and 720×500; the smaller form scrolls while Save/Discard/Return remain available. Physical workstation/operator checks 313–317 remain pending.
