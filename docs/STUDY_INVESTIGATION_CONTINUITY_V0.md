# Investigation continuity — bounded implementation contract

Prepared 2026-10-30 from accepted natural-session feedback. Design checkpoint only; no schema or behavior change yet.

## Current verified constraints

`IntegratedStudyTaskWidget` retains the current task UUID/question in per-database workspace settings, keyed by plan/revision. New investigation replaces that working identity. Saved capture associations, criterion records, findings and review snapshots preserve task identity and original wording, but there is no durable multi-investigation registry/resume selector. Question text is not the identity key.

`StudyFindRepository.get_latest_draft` restores a latest capture draft. MainWindow's pending investigation context and opening defaults are separate in-memory state. A registry alone therefore does not make switching safe: a retained capture must not acquire the newly selected investigation merely because it was reopened there.

## First slice

Create a database-owned registry of stable investigation IDs, owning plan and original plan revision, retained question and update provenance. Keep the active-selection pointer in workspace settings; do not make settings a competing owner of question identity. Provide New and Resume from a small selector, displaying enough question/revision context to choose intentionally. Inspection of history remains read-only and must not implicitly switch tasks.

Register existing current work without changing its task UUID. Discover older task IDs from explicit stored associations/results/reviews/findings; preserve all original source snapshots. Show conflicting or missing historical question wording explicitly and require deliberate selection/confirmation before establishing a registry question. Do not guess identity by matching text, fabricate missing historical questions, or infer links from navigation-only snapshots. First-slice resumption may restrict editing to the current plan revision; older-revision material must stay inspectable with an explicit explanation rather than silently rebinding criteria.

Switching must preserve the outgoing task, authored draft and its opening destination. Persist enough draft-context provenance to recover that binding after restart, or block the transition with an explicit save/keep/discard/cancel choice. Prefer retaining work; no automatic capture save, source reassignment or unrelated draft deletion. If a legacy draft lacks a destination, identify that uncertainty and request deliberate association when needed. Context-only defaults are not equivalent to authored work.

Opening an investigation must not invent a market reference from its most recent record: a question can span many dates. Clearly retain the present reference or restore an explicitly stored workspace reference, with the choice visible and consistent. Reference restoration and investigation association are distinct operations. Do not imply external chart synchronization.

Question refinement must be explicit and retain prior wording/provenance; no rewriting old receipts. Whether the first slice allows refinement or initially requires a new investigation for a materially different question must be resolved in implementation design. Do not retain unrestricted question editing that silently disguises identity changes.

## Deferred

Stable/reopen states, frozen answer baselines, review approval gates, ranking/competency inference, multiple concurrent capture editors, and chart reconstruction are separate increments. No required checkout for ordinary notes. New observations must eventually be addable without rewriting a settled baseline.

## Verification gate

Use an isolated copy/fixture before real data. Verify A → B → A and restart preserve identity, source associations, drafts/images and historical wording; canceled/failed switches leave outgoing work intact; same wording does not merge different IDs; historical conflicts remain visible; older revisions are not silently reinterpreted; migration failure rolls back cleanly. Verify real workspace backup recovery separately, including actual image availability, before directing the operator to upgrade or relocate the only working copy.

Next: implement the registry and draft-context transition together as a coherent bounded slice after resolving the explicit legacy/reference/refinement choices above. Publish only with authorization; no new operator test requested at this design checkpoint.
