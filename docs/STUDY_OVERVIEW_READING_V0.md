# Investigation overview — reading retained work

## Purpose

The connected Study exercise established that retained material restores reasoning, but the operator must sift through dense presentation. This slice improves recognition of saved examples and direct inspection of prior reflections. It preserves existing data owners, associations, native editing and image resolution.

## Changes

- A stronger question heading anchors the dialog. The initial window is 1280 × 800 with a resizable list/detail split; this is not a new global display profile.
- Capture rows show saved/draft/unavailable state, a short pattern-or-observation title, original association reference, instrument, saved session when present, and an observation excerpt. Excerpts normalize whitespace and truncate for display only; the inspector retains full text. Rows wrap within the list.
- The overview's capture reader keeps pattern, saved date, instrument, session and available move together above Observation and Notes. Full saved context and association remain available through a disclosure. This reader mode is limited to the overview; the standalone saved-find browser keeps its existing presentation.
- The first chart remains selected automatically, with Copy and Open Full Size unchanged. A one-image capture needs no extra attachment-list selection. Multiple images retain the list. An empty image area uses less space. Missing images still report load failure.
- Review checkpoints are explicit read-only entries and have their own filter. Selecting one does not open a new review editor, overwrite the current review, switch investigations or establish competency. Checkpoints cannot be added as support to another checkpoint; the action explains that actual captures/findings/criterion results are required instead.
- The existing direct Review this investigation route still opens the editor immediately. Material filtering and inspection preserve unsaved text, selected support and exit guards.

The main list is the opening snapshot of investigation material. Checkpoints saved during the dialog appear immediately in the existing review-panel history; reopening includes them in the main material list. No automatic reordering is introduced while the operator reads. Existing results/captures/findings order is preserved, with checkpoint history appended. No cross-type chronology or importance ranking is claimed. Questions remain in their existing browser, not inferred into this list.

## Operator 358 — recognize and recover an example

After publication, use the existing durable workspace and an investigation with a saved capture. Open Investigation overview. Can the list preview help you recognize an example before opening it? Select it and check full Observation/Notes, compact context, and first chart when attached. Show saved context and association; check the retained provenance. Multi-image selection and full-size viewing remain available. No need to create a new example solely for this check.

## Operator 359 — read a prior checkpoint without starting another

With a previously saved checkpoint in this investigation, choose Review checkpoints in Show material. Inspect the saved reflection with the review editor still hidden. Open Review this investigation if useful, type a disposable thought, and switch between a capture and a prior checkpoint: the new thought must remain separate. Trying to use a checkpoint as support must explain the restriction and add nothing. Resolve/discard the disposable review normally. Do not manufacture or overwrite meaningful work.

Operator 358–359 pending. No migration or new full Study-session exercise. Schema remains 53. Local branch `feature/study-overview-reading-v0`; publish as draft stacked on #106 only when authorized. Do not merge.

## Validation

21 focused tests PASS across overview reading, existing overview, workspace clarity, direct review, checkpoint persistence/guards and saved-find media. After adjusting row wrapping and empty/single-image space, seven reading/media checks passed again. Tests cover literal text, immutable association inspection, first-image selection, task scoping, read-only checkpoints, rejection as support, preservation of unsaved review and no database writes from inspection. One initial assertion incorrectly named the fixture question; corrected to check its actual retained question. Native offscreen overview render inspected at 1280 × 800. Diff check passed. Operator judgment of density remains pending.
