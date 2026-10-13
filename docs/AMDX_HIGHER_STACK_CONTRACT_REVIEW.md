# Higher-stack AMDX — architecture review

**Status:** the operator authorized proceeding on 2026-10-12. The pure resolver/read-projection foundation is now implemented separately in PR #67; persistence and native binding remain downstream. This document adds no schema, trading rules or operator smoke requirements.

## Purpose and current implementation

The quiet overview and nearby detail should refer to the same identified cycles across TDA, Watch, Market Review and future Study/Lab. The merged session/90-minute engine already has stable quartet identities, immediate one-entry revision, separate working/observed claims and durable provenance. Higher interpretation currently comes from legacy flat `qt_context` fields. Factual higher quarter positions and active-child descriptions already exist in `market_time.py`; they do not establish an AMDX profile or an entered anchor.

The next architectural step is to connect those two substrates without treating legacy labels as new recorded history. This precedes final 16:9 rendering, coverflow/hardware choices and classification research.

## Scope vocabulary

Name the containing quartet separately from the child being inspected. The existing `day` quartet contains four sessions; its `session` child quartet contains four 90-minute intervals. The smallest supported entry remains a 90-minute quarter; no additional 22.5-minute quartet is introduced.

| Containing quartet | Four children | Existing temporal basis |
| --- | --- | --- |
| 16-year | Four quadrennial blocks | Existing 2011 anchor; 2011–2014, 2015–2018, 2019–2022, 2023–2026 |
| Quadrennial | Four calendar years | Existing 2011-anchored four-year blocks |
| Yearly | Four three-month calendar quarters | Existing raw `year` quarter position |
| Monthly | Four Monday-start weeks | First Monday; fifth week is distortion; days before the first Monday remain unassigned |
| Weekly | Monday–Thursday futures trading days | 18:00 New York rollover; Friday is separate distortion context |
| Daily | Asia, London, NYAM, NYPM | Merged `day` cycle |
| Session | Four 90-minute intervals | Merged `session` cycle |

The overview may identify the active child as “90m” while the editor names its containing Session quartet. Legacy `quarter` interpretation and raw `year` position have different keys/meaning; a matching display label does not establish a migration mapping. Existing calendar-month A/M/D context is separately derived PO3 context, not a manually entered anchor in a four-week monthly quartet.

## Proposed identity and ownership contract

A cycle definition identifies its hierarchy level, calendar convention/version, New York timezone and anchor. A cycle occurrence identifies explicit half-open bounds and four ordered quarter IDs. Persist definition provenance when extending the existing registry; do not reinterpret older intraday IDs or action receipts.

Retain the existing calendar-versus-futures-date distinction. Reuse established calendar-year positions for 16-year/quadrennial/yearly levels, and established futures-day/first-Monday positions for monthly/weekly levels. Year-end and Sunday-evening examples must make the reference convention visible rather than quietly applying one rollover to every level.

The current `Cycle` requires four contiguous quarters. Weekly Friday and monthly fifth-week/pre-first-Monday states therefore live in factual context alongside the quartet; they are not Q5 anchors, synthetic X choices or automatic Not Applicable judgments. Monthly weeks can extend across calendar-month boundaries. The resolver must specify which occurrence is applicable from the existing factual mapping, and preserve full week bounds; it must not truncate a week or attach it to two contradictory active cycles.

A parent link is asserted only when its temporal containment and intended relationship are explicit. Calendar-month/weekly overlaps must not be forced into a strict tree by inventing containment. Prior-Q4 relationships are explicit references, with unavailable prior interpretations left unknown.

Claims remain owned by the identified run, channel, branch and containing cycle. The same calendar occurrence in two runs does not make their interpretations interchangeable. Future Study may reuse an explicitly selected source claim through an identified analytical action; it does not overwrite the original run or silently inherit the newest live interpretation. Study selection/ownership needs a concrete example before a Study renderer is implemented.

## Interaction and provenance

One legal anchor still selects AMDX/XAMD within its own quartet. Parent, child and adjacent cycles remain independent; no phase propagates merely because they line up. Direct X(C)/X(R), Unknown, whole-quartet applicability, clear, no-op, compatible retention and contradictory retirement use the merged shared-action semantics.

Use one read projection for cycle identity, factual position, current profile, entered/implied state, subtype, provenance and availability. TDA/Watch/Review and future Study can render this projection differently. Watch keeps quiet current orientation and immediate entry; detailed analytical work has nearby full-stack access. No history/comparison option or launch route is added to Watch.

Advancing time updates factual orientation without recording a phase. Editing pins the inspected run/channel/cycle/head and reference through the gesture. Historical Review chooses higher occurrences from the preserved run reference, as the accepted date correction does; it never substitutes today's clock. Missing/malformed references stay explicit. Failed reads or writes preserve committed meaning and require deliberate recovery.

## Compatibility and implementation sequence

Keep legacy flat values with their original provenance. Display them as legacy/derived until an explicitly new cycle entry exists; do not fabricate earlier anchors, expected/observed comparisons or definition evaluations. A schema change, if needed, is designed and tested before use; main currently remains v41 with Alpha 0.7.

1. Inventory exact existing temporal mappings and specify boundary examples, including year-end, Sunday evening, Friday, fifth week, pre-first-Monday and weeks crossing a month/quarter boundary.
2. Implement a pure higher-cycle resolver and read projection with those agreed examples, preserving intraday IDs. Keep unsupported relationships explicit.
3. Extend durable shared actions and restore/migration coverage only after the resolver contract is settled.
4. Bind quiet higher-stack orientation and adjacent editing through the shared actions. Evaluate Study-owned selection separately; final layout remains a context-specific projection.

No new smoke test is requested by this architecture document. The next review should settle temporal occurrence/relationship examples and the proposed run-owned interpretation model before committing a storage migration or new mature renderer. Actual price/news classifiers, rule priorities, empirical statistics and published Trade Plan adoption remain separate work.


## Pure foundation follow-up — 2026-10-12

`analysis/amdx_context.py` implements the higher occurrence and shared read projection foundation. The boundary examples and API are in `AMDX_HIGHER_CONTEXT_GUIDE.md`. Calendar-versus-futures time, pre-first-Monday, Friday/fifth-week, full cross-month weeks and DST bounds retain the existing raw conventions. Weekly parent identity is derived from its own Monday, so selecting another month never changes an existing week's content. Intraday IDs remain unchanged; legacy values never become inferred anchors. Projections select only the requested run/channel/branch/cycle and retain the original immutable claim. Empty history stays Unresolved.

No storage/GUI binding, historical as-of replay, Study-owned selector or migration is added. Future Review must deliberately supply its validated original reference, and retrospective Study must select its recorded information/history basis explicitly. Final development verification and publication are recorded in the project state/handoff.
