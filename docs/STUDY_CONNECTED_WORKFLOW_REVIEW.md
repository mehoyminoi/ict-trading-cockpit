# Connected Study workflow review

2026-10-30. Operator 355 PASS on published draft PR #105. This is a documentation and integration checkpoint, not a new application release or a claim that the whole cockpit is ready. Schema remains 53. No new numbered smoke test.

## Assessment

The implemented Study path now covers stable investigation identity/resumption, retained capture destination, explicit reference correction for unlinked drafts, atomic save-to-investigation, fresh next capture, findings/questions, optional review checkpoints and read-only retrieval. These components have targeted automated checks and operator acceptance. The remaining acceptance question is whether they work together without requiring the operator to reconstruct the process.

The next step is one natural session followed by a return visit. Do not add more fields, analytics or lifecycle controls before observing a concrete blocker. Full Study/TDA/Watch integration and separately authorized stack consolidation remain subsequent gates; passing this Study journey alone does not establish them.

## Use the existing durable workspace

Use the already accepted #105 application and `~/ict-study-workspaces/study-v0`. No new pull or database migration is required for this review. Close Cockpit before any backup. Preserve the full workspace, including images, settings and the origin manifest. Never substitute the missing original `/tmp` directory or seed a new fixture for this meaningful session.

From the repository with the virtual environment active:

```bash
python tools/study_criterion_demo.py --data-dir "$HOME/ict-study-workspaces/study-v0"
```

The launcher remains a synthetic demo shell. Your saved observations are real retained work; synthetic criterion results are not market evidence. Leave that evaluator aside unless deliberately testing it.

## A natural session, not a button exercise

1. **Return to a question.** Use Resume investigation for an existing question in the current plan revision. Inspect its overview or previous review to recover your place. Use New investigation only for a different question. If an authored capture blocks switching, save it to its existing destination or deliberately discard disposable work first.
2. **Orient to the chart.** Choose Historical Reference and the relevant session in the calendar. Compare with TradingView explicitly, including New York time. Resume deliberately leaves the calendar unchanged; it does not find a chart date for you. Open Study Find and check the displayed destination and reference. If an unfinished unlinked capture has stale context, select the correct calendar reference and use Use selected calendar context. This preserves written content; it does not save the capture.
3. **Study and capture something useful.** Keep the wider chart context available. Observation can describe what price did; Notes can hold interpretation, uncertainty and HTF connections. These are aids, not a mandatory writing template. Paste an image when useful. Record relevant timeframe/event time in text where needed; Cockpit cannot detect these from TradingView. If looking at fully revealed history, distinguish hindsight from what was visible at the time.
4. **Keep useful outcomes as they arise.** A selected question can go directly through Keep question for later; no selection opens the composer. Keep finding supports an observation/insight or a partial answer with the appropriate explicit investigation destination. Neither action saves the whole capture or establishes competency. Do not manufacture a question or finding merely to exercise a control.
5. **Save and keep studying.** Save to investigation is the ordinary path for an example supporting this question. Wait for success. The next form should be fresh, with context retained. For another day/session, change the calendar and reopen through Open Study Find; verify the displayed reference again. View last saved is a temporary shortcut, while saved material remains retrievable after restart.
6. **Pause when it makes sense.** Review this investigation opens the review entry directly. Record only useful understanding, uncertainty or a next step; no requirement to fill all three. Save a worthwhile checkpoint explicitly. Keep question for later can capture a selected question here too, but does not save the review itself. An unsaved review is guarded on exit, not an autosaved recoverable review draft.
7. **Return later.** Close/reopen normally when finished. Resume the same investigation, inspect the retained capture/image and checkpoint, and decide what to study next. You need not add another capture just to finish this review. Confirm that you can recover both the question and your reasoning without reconstructing them from memory.

Stop if meaningful work disappears, changes destination unexpectedly, or cannot be saved. Report the point of failure rather than working around it repeatedly.

## Controls with similar names

| Intention | Action and consequence |
| --- | --- |
| Save this example under my question | Save to investigation: saves content/images and explicit association together. |
| Keep an independent example | Save Study Find: saves content; adds no new investigation association. Existing association is preserved. |
| Associate an unfinished capture without submitting it | Link capture only: records association, leaves capture content unfinished. Not required in the normal combined-save path. |
| Park a tangent | Keep question for later: stores a separate question and source snapshot. Does not switch investigations. |
| Keep an insight or partial answer | Keep finding: distinct retained finding; not a completed or validated answer. |
| Take stock | Review this investigation, then explicitly save a checkpoint if useful. |
| Retrieve prior material | Investigation overview for this question; Study history for cross-investigation retrieval. History does not resume an investigation. |

## Known limits and disposition

- Saved wrong-date receipts cannot be corrected by draft alignment. If real material is affected, inventory the specific records and design a provenance-preserving correction before relying on them analytically. Do not edit database rows manually.
- Resumption is current-plan-revision only. Older records remain inspectable. Full Stable/reopened lifecycle, wording revision and multiple concurrent draft editors remain deferred.
- A queued question is not automatically promoted to an investigation. For now deliberately start a new investigation with that wording when ready; do not imply an existing formal queue-to-task link.
- Review next-step text records operator intent. It is not an empirical recommendation or competency assessment.
- Source inspection found an older investigation status string recommending Link this capture. The normal route is now Save to investigation. Record this as a bounded wording correction for the next implementation pass; no code change is included here.
- The older narrative guide used temporary storage and predated the integrated save/review path. This guide supersedes its operational instructions.

## Report only what matters

- Could you regain your place after returning, including the chart context and why the observation mattered?
- Did anything interrupt study, require remembering a hidden step, or send work to the wrong place?
- Did the session help you learn or sharpen the next question? “No clear effect yet” is valid.

Operator accepted the connected journey on 2026-10-30: prior question and related material restored intent after reopening; density and hidden switch-blocker guidance remain UX findings. Individual prior PASS results are not substituted for this acceptance. Then inspect the TDA-to-Watch journey against its existing guides and actual code, prioritize observed blockers, and prepare an integration/consolidation plan without merging anything automatically.
