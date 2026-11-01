# Integrated Study task — retained intent and explicit capture association

Local implementation on `feature/integrated-study-task-v0`, following startup operator acceptance (296–300 PASS). This is a bounded native UX2 trial, not final Lab layout or criteria-authoring acceptance.

## Ownership and behavior

- The existing maintained AMDX calendar retains all-layer entry, selection, historical reference, interpretation channel and draft ownership. Question/identity are per-database, per-plan/revision workspace drafts. New investigation creates a new identity and clears only the question; linked captures retain their prior context. No navigation creates a run or certifies process completion.
- Open Study Find preserves an existing draft and shows the investigation context. **Link this capture to investigation** is a separate explicit action. It retains capture content through the existing draft repository and records the displayed question/reference, instrument, interpretation, plan/revision, task ID and actual recording time. The context is pinned when opening capture, so a hidden calendar/question change cannot redirect the link.
- Associations are immutable snapshots, one per capture ID. Repeating an identical link is a no-op; a different association is rejected rather than overwriting provenance. A draft and its saved Study Find retain the same ID. No automatic reassignment, proficiency/evidence creation, prospective-knowledge claim or run association occurs.
- Study Review shows the selected capture's stored association, separately from temporary navigation context. Unlinked captures show a truthful empty state. Explicit return routes preserve the current calendar and investigation. Capture details still belong to the capture; linking does not change its date or instrument.
- The published-AMDX-definition area reports the current unconfigured state, matching the existing Watch reference. Structural AMDX/XAMD legality is clearly separated from price-action classification. Definition authoring and richer published rule content remain UX4; no rules are invented here.
- The shell uses a scroll viewport so existing forms stay reachable at reduced heights. This is a native accessibility fallback, not final layout approval. Original tabs, widgets, shared commands and active-runtime startup routing remain intact.

## Storage and migration

Schema **47** adds `study_investigation_capture`, an immutable association snapshot keyed by capture ID and indexed by task ID. Capture IDs may refer to either an existing draft or saved capture; the repository validates that union at explicit association time. There is deliberately no misleading FK to only one of those lifecycle tables. An abandoned draft may leave its immutable association receipt; no automatic receipt deletion is introduced.

There is no backfill of links for existing data. Existing captures/AMDX receipts are unchanged. The migration now begins a transaction before version-only barriers as well as DDL: a failure during the new migration must roll back the whole upgrade, including the earlier version-only v45→46 step. Older applications reject schema 47. Use only the separate demo for this trial; no operator regular database has been opened or migrated.

The workspace question is an editable draft; immutable association receipts are its durable historical snapshots. This is not a multi-task library or a task-completion/assessment engine. A link confirms the operator's association, not the correctness of its content.

## Review boundaries

The [operator guide](INTEGRATED_STUDY_TASK_OPERATOR_GUIDE.md) covers question/reference continuity, explicit capture association, immutable context, saved Review, restart and reduced-height access. Full calendar/tree rendering, classifier authoring, automatic recommendation ranking and evidence interpretation remain separate work. No publication or merge is implied by the local implementation.

## Developer validation

223 focused tests PASS across 19 isolated modules on the final source: investigation/capture association, native task and demo, database initialization, startup, main window, capture/review/drafts, contextual Watch, AMDX repositories and historical migrations. Failure injection verifies rollback including the version-only barrier. Python 3.10 grammar and diff checks pass. Native Lab and capture rendered/inspected at 1440×810; automated 1280×720 check verifies scrolling rather than forced window growth. No full-suite rerun or operator acceptance claimed.
