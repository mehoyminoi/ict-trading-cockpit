# Operator-loop friction reduction — v0 design candidate

**Status:** Design candidate for operator review  
**Scope:** Pre-C5 usability hardening; no domain-model changes

## Purpose

Review / Development has accumulated legitimate capability, but the current presentation exposes too much of it at once. The result is high scanning cost, weak orientation, and growing temptation to shortcut manual acceptance testing.

This is now a product/workflow defect, not merely cosmetic polish.

The goal of this slice is to reduce cognitive load without changing the underlying competency, evidence, progression, regression, or Trade Plan architecture.

## Design principle

> **Preserve depth; reduce simultaneous exposure.**

The operator should not have to visually parse every available control in order to understand the current state or perform one task.

The surface should answer, in order:

1. Where am I?
2. What is the current state?
3. What needs attention now?
4. What can I do next?
5. Where is the deeper detail if I need it?

## Recommended Review / Development hierarchy

Instead of one continuous wall of controls, use a small set of top-level work areas:

- **Overview**
- **Evidence**
- **Interpretation**
- **Progression**
- **Practice / Launch**

These are presentation groupings only. They do not create new domain objects.

### Overview

Compact orientation surface.

Show:
- selected competency,
- current Trade Plan revision,
- Development Direction,
- Cross-Run Observation summary,
- Evidence Maturity boundary/state,
- current progression standing,
- evidence count/purpose coverage,
- one concise "Next useful action" line when one is explicitly known.

Do not infer a recommendation where architecture does not support one.

### Evidence

Contain:
- evidence list/filter,
- selected evidence detail,
- supporting-evidence relationships.

### Interpretation

Contain:
- Cross-Run Observation,
- Development Direction,
- human synthesis controls.

### Progression

Contain:
- Evidence Maturity,
- current Eligibility,
- historical Attainment,
- Regression / Revalidation Review when applicable.

### Practice / Launch

Contain:
- targeted Study routing,
- Lab / Replay / Forward launcher.

## Progressive disclosure

Each top-level area should be collapsible or independently selectable.

Default behavior recommendation:

- Overview open by default.
- One task area open at a time.
- Dense edit controls collapsed until requested.
- Current saved state remains visible even while editor controls are collapsed.
- Opening one area should not erase unsaved work in another.

Avoid nested collapse controls deeper than necessary.

## Compact state cards

For dense governance concepts, prefer a repeatable card pattern:

```text
Evidence Maturity
Current: Developing Evidence
Boundary: Rehearsal -> Validation

Why this matters:
Can the evidence support a trustworthy decision?

[Review / edit]
```

and:

```text
Progression
Current: BLOCKED

Why:
Validation evidence missing

Next:
Gather required Validation evidence

[Show details]
```

The "Next" line must come from explicit known requirements or existing Development Direction, not hidden inference.

## Quiet definitions

Technical terms should be explainable without leaving the task.

Recommended mechanisms:
- tooltip on term headings,
- small info icon or "?" action,
- one-line definition under uncommon terms,
- expandable "What does this mean?" text for complex concepts.

Definitions should distinguish neighboring concepts explicitly, e.g.:

```text
Evidence Maturity
= can this evidence support a trustworthy decision?

Eligibility
= does the current Trade Plan permit the boundary now?
```

## Stable UI anchors

Major operator-visible concepts should receive stable presentation identifiers so both future guided testing and navigation can target them.

Examples:

- review.overview
- review.evidence
- review.cross_run_observation
- review.development_direction
- review.evidence_maturity
- review.progression_standing
- review.practice_launcher

These IDs are UI/navigation anchors, not domain identities.

This gives later smoke-test tooling a reliable target without coupling tests to incidental label wording.

## Smoke-test runner friction reduction

The existing runner already provides one-step navigation through checklist items. The next useful improvement is to make each item answer:

- **Where:** exact Cockpit location
- **Look for:** target concept/control
- **Expected:** concise outcome
- **Why:** optional rationale

Candidate checklist metadata in Markdown:

```md
- [NOT TESTED] Confirm Evidence Maturity still loads/saves by competency + boundary.
  - Where: Trade Plan > Review / Development > Progression > Evidence Maturity
  - Look for: saved boundary-specific state and notes
  - Expected: switching boundaries restores each saved profile
```

This remains ordinary Markdown and does not create a second test-definition system.

## Guided test mode

Later, if stable UI anchors exist, the smoke runner or Cockpit may support a lightweight handoff:

```text
Current smoke item
        ↓
target UI anchor
        ↓
Open / focus target area
        ↓
brief highlight
```

For v0 friction reduction, do **not** build cross-process IPC or a complex testing framework.

First make the production information architecture navigable and the Markdown test instructions precise enough that the operator does not have to search visually.

## Search / filter

A simple Review / Development filter may later help with concepts such as:

```text
maturity
direction
regression
attainment
draw on liquidity
```

For the immediate slice, section navigation and progressive disclosure are higher-value and lower-risk than full-text search.

## Visual process map

The previously accepted PDM-like interactive process/state map remains a later UI maturity goal.

This pre-C5 slice should not attempt that full design.

Instead, it should create the foundations the later map needs:
- clear state groupings,
- stable UI anchors,
- explicit current state,
- explicit blocked reasons,
- explicit next-action text,
- explainable transitions.

## Recommended implementation sequence

### F1 — Review / Development sectioning

Introduce a compact local navigator or tabs for:

- Overview
- Evidence
- Interpretation
- Progression
- Practice / Launch

Reuse existing widgets and repositories. No schema change.

### F2 — Overview summary

Add one compact read-only orientation surface assembled entirely from existing state.

No new scoring or inference.

### F3 — Progressive disclosure

Collapse or hide dense edit controls until the corresponding area is active.

Preserve saved state and existing workflows.

### F4 — Smoke-test guidance

Refactor the current branch acceptance checklist style so each manual item names a stable location and expected visible result.

Optionally add support in the smoke-test runner for displaying a dedicated **Where / Look for / Expected** guidance block if this can be done without changing Markdown semantics.

### F5 — Stable UI anchors

Assign stable identifiers/properties to major Review / Development areas for future guided navigation and testing.

Do not yet implement automatic cross-window jumping unless trivial and robust.

## Explicit non-goals

This slice must not:

- change progression policy semantics,
- change evidence or competency ownership,
- change Trade Plan revision behavior,
- introduce readiness scores,
- introduce automatic recommendations,
- redesign the entire application,
- build the final visual process map,
- build a media player,
- replace Trilium,
- create a second smoke-test data format,
- add schema migrations unless unexpectedly required.

## Acceptance target

A successful v0 should make this true:

> A tired operator can open Review / Development, understand the major areas in seconds, find the exact control needed for a smoke-test item without scanning the full page, and return to the overall state without losing orientation.

## Operator confirmation questions

1. Use five presentation areas: Overview / Evidence / Interpretation / Progression / Practice & Launch?
2. Keep Overview compact and read-only, showing existing state only?
3. Default to Overview plus one active work area rather than all editors visible simultaneously?
4. Keep saved state summaries visible even when detailed editors are collapsed/hidden?
5. Add quiet definitions/tooltips for technical governance terms?
6. Add stable UI anchor IDs now to support later guided testing/navigation?
7. Update smoke-test wording to include Where / Look for / Expected guidance?
8. Defer full-text Review / Development search until after the simpler sectioning/navigation is tested?
9. Defer automatic smoke-runner -> Cockpit deep-link/highlight plumbing until stable anchors exist and basic layout is proven?
10. Treat this as a small pre-C5 usability slice with no schema/domain changes, then return to C5 operator-loop integration?
