# Real chart-assisted Study — findings and next design boundary

Operator feedback following the first realistic session (2026-10-27). This is qualitative learning/workflow evidence, not a new smoke-test pass, final form approval, or proof of a market classification. The operator reports that the cockpit helped surface a new research question and a possible first conscious recognition of apparent manipulation being superseded later in the day.

## Primary acceptance question

**“Do I feel like it helped me learn something?”** Study/data collection/practice are central product responsibilities. Capture fidelity and provenance remain necessary, but successful form completion is insufficient. Real-session feedback must guide the next development slice. Do not ask the operator to suppress field/layout feedback that affects learning. The current Study Find fields are provisional.

## Immediate continuity issues

- Default instrument: a configurable workstation default, initially MNQ, should reduce repeated entry. Explicit originating context takes precedence over the default; technician input takes precedence over both. Never backfill unknown historical ownership from a preference.
- Selected context: a new capture opened from an investigation should visibly inherit its instrument, studied date and selected session when unambiguous. London selected for study should not be replaced by a session inferred only from the clock. All suggestions remain editable. Broad-layer selections may have no meaningful session; do not guess one.
- Verified current gap: MainWindow._open_investigation_capture displays/pins navigation context but intentionally retains the capture's own date and does not call apply_context_defaults. This protected existing drafts, but also left a new capture with the wrong date in this trial. A temporary status message is insufficient. Treat this as a data-context defect, not operator error.
- Distinguish a fresh capture, an unfinished draft and a saved item. Opening capture for Day 2 after saving Day 1 should make the next action obvious. Never silently clear an unfinished draft or overwrite its context. Preserve deliberate access to the prior saved find without making it masquerade as a fresh capture.
- Capture date and investigation association reference are separate existing fields. Preserve their meaning, but show discrepancies before linking/saving rather than allowing the operator to assume agreement. Correcting an existing immutable association requires an explicit supported workflow; never rewrite it silently.

## Observation, interpretation and research questions

Proposed wording distinction for discussion, not final schema:

- Observation: what price did, in chronological order, with time/timeframe and visible facts.
- Notes / interpretation: what it might mean, uncertainty, alternative explanations, questions and reflections.

Do not force every thought into rigid boxes. Stream-of-consciousness narration should remain possible, with optional later extraction into structured concepts/evidence. Preserve original text when extracting or rephrasing.

## Vocabulary and quiet concept linking — exploratory direction

A plan-related terms/definitions catalog with stable concept identities and aliases could connect typed acronyms (PDH, TS, JS), references, Study Finds and later Trilium links. Do not assume every abbreviation is unambiguous or silently expand JS. Optional IDE/spellcheck-like suggestions should be quiet, dismissible and reversible. A mention is not an adopted rule, confirmed pattern, entry confluence or measured outcome. Definition revisions must preserve meaning of historical records. New concepts can be added without redesigning capture fields. Trilium synchronization remains future integration, not implemented capability.

## Time, timeframe and broader narrative

Time is a first-class study dimension: studied market date/time, selected session, named window (e.g. operator's 1am macro), chart timeframe and higher-timeframe narrative should be retained where explicitly known. A named window needs a defined timezone and boundaries; never infer an exact range from a shorthand name. Separate event time, information-available time and recording time. TradingView timeframe cannot be silently detected without an actual integration.

Small-pattern inspection must remain adjacent to HTF/TDA, market-maker narrative and whole-stack orientation: how does this session's price action fit the broader narrative, and what changes that interpretation? Avoid a form that rewards filling detail while losing the larger question. Optional context should not become a mandatory checklist for every Study Find.

## Available moves and hypothetical entry sequences — exploratory direction

Keep none/one/multiple move measurements possible in the mature model: low-hanging fruit, TP1, TP2, terminus or operator-defined labels. Each useful measurement needs a reference/entry basis, direction, units, timeframe and availability/measurement meaning; do not make incomparable distances look statistically equivalent. An optional hypothetical confluence sequence (TS, OB formation, displacement, confirmation, return, OTE, breakaway gap) can support pattern-recognition practice. Preserve ordering and uncertainty. These are study annotations, not executed trades or realized P&L. Seasonal/session/news/model comparisons require explicit context and sampling definitions; no performance claim follows from two hand-picked examples.

## Capture the next question without derailing the current one

The concrete uncovered need is a quiet Study inbox: select text or use a nearby action to retain a follow-up question, realization, uncertainty or confidence reflection while continuing the present investigation. Retain originating capture/investigation, chart/reference, exact original wording and any separately edited question. Support retrieval and deliberate later selection; no automatic competency advancement from confidence or an aha moment.

Operator's question: “Why, if reading price chronologically, did London look like Q2 Manipulation starting the daily move, but then NYAM ended up turning into the main manipulation move?”

Possible research phrasing: “What information available during London supported the initial manipulation interpretation, and what later NYAM evidence supported revising it?” Preserve the original. Do not label this confirmed fake manipulation or invent a governing definition. A later inquiry can ask which distinguishing signals were available before NYAM, with hindsight separated from contemporaneous knowledge.

## Interaction details to preserve

Natural Tab traversal, nearby Generate Summary, automatic primary chart preview and popup date selection were positively noted. Preserve keyboard order through changes. Summary presentation may become compact/popout later; do not hide a useful action prematurely. Repetition costs and small friction matter, but isolated styling should not displace learning workflows.

## Recommended sequence

1. Fix capture-context continuity (instrument/date/selected session and fresh/draft/saved distinctions), with targeted regression checks and a short operator retry. This prevents corrupted study context.
2. Design and implement the smallest durable follow-up-question inbox/return action using the concrete London → NYAM example. Inspect existing owners before choosing storage; do not assume a generic task library exists.
3. Use another real session to shape Observation/Notes guidance and optional narrative/time/context fields.
4. Develop concept vocabulary, multiple move measurements, confluence sequences and external note links as separate informed slices. Avoid committing to a large tagging/schema system from this one session.

The scope remains broader Study, with AMDX as the first case. No implementation, publication, merge or final field-schema acceptance is claimed by this document.

## Narrative session follow-up — 2026-10-28

- Confirmed post-discard handoff defect: retained context-only defaults caused the draft-content check to prevent subsequent date/session suggestions. Local correction remembers an exact discarded-form seed in per-database workspace settings. Only an untouched matching capture can be reseeded from the new selection, including after restart. Authored text or edited context stays protected. No schema migration.
- Clarification: Study Find has a date and session, not a standalone historical-time field. Full reference time is retained in an explicit investigation association. The differing-context notice is advisory, not a universal save veto; do not describe it as a mismatch-prevention guarantee.
- New blocking learning need: retain an aha/realization as a **Finding**, optionally identify it as a **partial answer to the investigation**, without phrasing it as a question. Preserve capture/reference/HTF context, original wording, uncertainty and explicit investigation association. A finding is a technician interpretation, not automatic proof, plan adoption or competency advancement. Prioritize this before another full narrative test. Build on existing retention machinery after inspecting its semantic constraints; do not silently relabel immutable question records.
- Link vs Save confusion: Link creates the immutable investigation association, Save persists the Study Find content/images. Those are distinct data operations, but the UI need not require two distant actions. Design a coherent save area with visible investigation destination and an explicit combined Save to investigation action where context is valid. Existing drafts from other contexts must not be silently reassigned. Preserve standalone saving and transparent mismatch handling. This is a design direction, not implemented automatic linking.
- Screenshot friction is part of the actual Study workflow. Operator uses Ksnip with Win+Shift+S but it is effective only after starting the app. Investigate a desktop-owned launch-and-capture shortcut after confirming Linux desktop/session and installation type. Do not assume autostart or app-internal global shortcuts work on Wayland. Official Ksnip README documents command-line support and Windows/X11-only global hotkeys: https://github.com/ksnip/ksnip/blob/master/README.md .
- Calendar orientation dots delivered useful immediate value when correlating chart price action with manually chosen date/time. Preserve this accepted cue. Future optimization should reduce repeated focus switching, manual temporal alignment and reorientation without allowing navigation to advance process state or infer AMDX classifications.
- Use **interaction cost** as the established UX term for physical and mental effort required to operate the interface (NN/g: https://www.nngroup.com/articles/interaction-cost-definition/). The project can describe the specific burden as **study overhead**: navigation, copying, selecting references, chart pairing and data entry needed to enable the actual research. This is a working project label, not a standardized measurement. Measure specific operations/reacquisition time rather than setting an arbitrary minimum-click target.

## Screenshot workflow accepted — 2026-10-28

Operator confirmed KDE/X11 with `/usr/bin/ksnip` 1.9.2. A desktop-owned Win+Shift+S shortcut invoking `/usr/bin/ksnip -r` worked without issues, and screenshot paste into Cockpit is functional without meaningful friction. Treat this workflow as accepted; defer screenshot refinements. This acceptance does not imply an application code change or acceptance of the pending post-discard context fix.

## Review checkpoint acceptance and analytical direction — 2026-10-29

345–347 PASS. The deliberate opportunity to take stock and retain simultaneous outcomes is accepted. It is a recording step that should fit a natural pause without interrupting a study groove. This is not acceptance of final layout or proof that it chooses the next useful study target.

The Next study step prompt records a technician-authored intention; it does not implement analytical prioritization. Later cross-session analysis should make recurring questions, uncertainties, reviewed errors and performance patterns inspectable with appropriate filters and visualizations. Repeated mentions may reflect interest or exposure, not deficiency. Distinguish questions raised, practice attempted and reviewed performance. Never turn record counts into independent sample counts, proficiency or a readiness score.

Immediate foundation: read-only retrieval across independent investigations for the current Trade Plan, preserving original questions/revisions and current working context. No additional checkpoint polish or repeated scripted navigation is required beyond validating the new retrieval path. Revisit review utility during a natural real-study pause later; preserve the accepted recording role while assessing whether analysis actually helps choose the next task.
