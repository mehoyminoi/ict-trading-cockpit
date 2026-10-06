# Cockpit UX Storyboard

This document captures broad information hierarchy and flow decisions before detailed styling/layout work. It is intentionally a room-level contract rather than a pixel specification.

## Viewport targets

The cockpit must remain comfortable on both primary workstation classes:

- **Compact:** 1920 × 1080
- **Wide:** 3440 × 1440

The workflow, vocabulary, and decision hierarchy are identical on both. Wide layouts may expose more simultaneous context; compact layouts use progressive disclosure and tighter grouping rather than a different workflow.

## Global operating rule

**Persist broadly; render selectively.**

The application may retain telemetry, evidence, transitions, and detailed history without demanding that the operator look at all of it during normal work.

Primary controls should remain anchored and reachable. Mouse-wheel / mouse-button workflow navigation should not compete with ordinary page scrolling in operating surfaces designed around those inputs.

---

## TDA — Focus

### Purpose
Work one analysis station at a time and deliberately certify completion.

### Always visible
- Trading Run + current mode + station/progress orientation.
- Current station name/question.
- Current station actions.
- Observation/work area.
- Previous / Complete & Continue controls.
- Process-level exit/advance controls.

### Secondary / collapsible
- Repeated app/process descriptions.
- Full prior-station history.
- Telemetry.
- Extended explanatory copy.

### Compact
- Bounded working surface where normal station work does not require vertical scrolling.
- Wheel remains reserved for station navigation.
- Explanatory chrome collapsed while operating.

### Wide
- Same focus hierarchy.
- More observation/context space may remain visible.
- Do not add permanent panels merely because width is available.

---

## TDA — Deck

### Purpose
Act as the spatial index / overview of TDA station state.

### Always visible
- All station identities and completion state.
- Current station distinction.
- Enough observation summary to recognize prior work.

### Compact
- Reflow/compact cards to fit the viewport rather than treating Deck like a long document.
- Scrolling is UX debt to resolve when Deck receives its dedicated responsive-layout pass.

### Wide
- Show more/all cards simultaneously when possible.
- Preserve the same deck grouping and spatial logic as Compact.

---

## Live Watch — Primary Operating Room

### Purpose
Wait, watch, and know at a glance where current market conditions stand relative to the active Trade Plan and the TDA.

Live Watch should answer:

1. What did TDA establish?
2. What am I waiting for?
3. Which Trade Plan entry conditions are currently satisfied?
4. Is the entry threshold satisfied?
5. What risk envelope applies?
6. Has the thesis materially changed?
7. What is the next valid process action?

### Always visible
- Primary TDA thesis/draw/watch context.
- Plan-owned entry-readiness state.
- Required entry threshold when configured.
- Plan-owned risk envelope when configured.
- Material If/Then watch points.
- Current thesis state.
- Return to Analysis / Stand Down / other valid process actions.

### Secondary / quiet
- Raw evidence log.
- Process-transition telemetry.
- Detailed historical TDA text.
- Explanatory text once the operator understands the room.

### Compact
- One primary dashboard.
- Secondary evidence/details progressively disclosed.
- Avoid routine scrolling for the core wait/watch loop.

### Wide
- TDA carry-forward, readiness, risk, and watch-point context may remain simultaneously visible.
- Extra width is used for context, not for additional mandatory inputs.

### Policy ownership
Live Watch does **not** define trading rules. Entry criteria, thresholds, and risk constraints belong to the active Trade Plan revision and are inherited by the runtime.

If a rule is not configured, Live Watch must say **Not configured** rather than invent a default.

---

## Post-Market Review

### Purpose
Hand the run back to the trader in a calm way, separate market interpretation from process behavior, and identify what deserves further study.

### Stage 1 — Market Review
- What TDA expected.
- What materially changed during Live Watch.
- Whether the interpretation remained materially accurate.
- If changed, why (later structured classification).

### Stage 2 — Process Review
- Process adherence.
- Short takeaway.
- Film Night / Lab flag.

### Do not foreground
- Chronological button/navigation logs.
- Raw transition telemetry unless specifically investigating workflow habits.

---

## Live / Lab parity principle

The live cockpit and study/backtesting cockpit should share the same Trade Plan definitions, process vocabulary, decision structures, and readiness rules.

The lab may add replay-specific controls (research question, reveal-next-bar, historical timestamp, sample tags), but it should not teach or collect a different operating process.

Useful repetition should remain deliberate; redundant data entry should be automated away.
