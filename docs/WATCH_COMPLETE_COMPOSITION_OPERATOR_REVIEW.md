# Complete Watch composition operator review

**Review date:** 2026-10-14

**Artifact:** [Complete Watch composition v0](prototypes/watch-complete-composition-v0.html)

**Status:** Directionally accepted checkpoint. The chart-adjacent reference-and-decision refinement passed operator review on 2026-10-15; this is not final visual approval or native acceptance.

## Accepted direction

- The broad composition is a good start without immediate layout friction.
- Broker/process-safety information at the bottom preserves the informational priority of market and process content.
- Restrained Setup Criteria cues help the eye move between critical locations; minimal styling improves salience.
- P&L remains absent and broker information remains process support rather than a casino-like dashboard.

## Chart-adjacent reference result and bounded refinement

Manual AMDX and price-action discernment needs a low-friction reference to the applicable definition, criteria and process from the active Trade Plan. Because this work is tightly correlated with chart reading, its entry point and opened surface should follow the chart-facing edge:

- TradingView left → reference opens nearest Cockpit's left edge;
- TradingView below → reference opens nearest Cockpit's bottom edge;
- direct mouse and keyboard access;
- dismiss to the same Watch anchor;
- concise contextual aid in Watch, with full authoring/evaluation elsewhere;
- explicit provenance and no invented published rule.

This is a support popout, not another permanently visible panel.

The operator is happy with the first popout and accepts the monitor-specific placement. The remaining friction was that the primary active-quarter AMDX controls sat behind and across the screen from the open reference. The accepted refinement turns the popout into a temporary **reference-and-decision dock**:

- show the exact active target and only its legal roles;
- invoke the same shared immediate AMDX action as the main AMDX panel;
- dismiss after the selection and return to the Watch anchor;
- retain unresolved `X(?)` rather than force certainty;
- add no second Save, state owner, history or popout-specific semantics.

This deliberately duplicates a control projection only for the single point-of-discernment operation. It does not duplicate the workflow.

The operator's final result—“Two clicks, AMDX for that entire 90m quartet dealt with … smooth, snappy, lightweight”—accepts this as a cross-suite interaction exemplar. Stop standalone Watch polishing here. Carry the contextual completion loop into the [smallest native decision-dock slice](WATCH_NATIVE_DECISION_DOCK_SLICE.md), then reuse it for later contextual tools where it materially reduces hunting, memory or navigation.

The two monitor arrangements also reveal a future global-setting requirement. Monitor relationship and chart-facing edge should be retained as an infrequently changed Workspace & Displays profile rather than ordinary daily task state. Constrained named profiles are preferred over unrestricted docking.

## Cross-suite implications accepted in the same review

The discussion accepts the [Cross-suite UX Interaction Standards](UX_INTERACTION_STANDARDS.md): earned salience, change-oriented reacquisition, constraint-based error prevention, redundant encoding, distinct workspace identity within one coherent design language, future theme readiness and explicit review before any operator or developer suggestion overrides established UX guardrails.

## Acceptance boundary

This review accepts the direction, information hierarchy and shared-action interaction quality, not final geometry, typography, exact fixture language, broker integration or production behavior. The standalone prototype is now reference-only. Proceed to the bounded native decision-dock slice instead of continuing open-ended prototype polish.
