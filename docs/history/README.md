# Recovered Conversation Source Index

This directory records the existence and role of historical source material used during the 2026-10-08 roadmap/handoff reconciliation.

Historical chat transcripts are **evidence**, not canonical requirements. The canonical extraction of their architectural meaning is kept in:

- `docs/PROJECT_EVOLUTION.md`
- `docs/DECISION_AUDIT.md`
- `docs/DECISIONS.md`

## Recovery sources

### `context_transcript_the_prequel.txt`

User-supplied recovery transcript covering the earlier GitHub-era development sequence through the Process Blueprint, executable TDA, Focus/Deck interaction, Trading Day runtime, process transitions, and the beginning of Session Runtime work.

Its ending overlaps the next transcript around the **148 passing tests** checkpoint, which provided a reliable chronological splice.

### `context_transcript.txt`

User-supplied continuation covering Session Runtime refinement, Watch/Post-Market work, shared runtime, structured Playbooks, authorization, Market Time/QT, opportunity synthesis/attention cues, the deliberate pivot toward Study/Lab, Study/Rehearsal/Validation/Execution semantics, eligibility, and the Competency / Proficiency substrate.

## Important precedence rule

Do not use these source transcripts as a feature queue.

Later discussion frequently refined earlier designs. In particular:

- the earlier market-session-shaped Session Run default was later simplified,
- Film Night/chart-gallery/visual polish were deliberately pushed downstream,
- further Live-Watch expansion was deliberately deprioritized,
- the center of gravity moved toward Study/Lab, competency evidence, and progression/eligibility.

If the raw transcripts are ever reintroduced into a future development chat, first read `HANDOFF.md`, `PROJECT_STATE.md`, `DECISION_AUDIT.md`, and `PROJECT_EVOLUTION.md`. Use the raw material only to investigate a specific unresolved historical question.

## Archive policy

The raw recovered transcripts were supplied by the user during the 2026-10-08 reconciliation. They are intentionally not treated as canonical source-of-truth documents. If raw archival is later desired in Git, store them under `docs/history/raw/` with a prominent historical/non-canonical warning and do not change the precedence rules above.
