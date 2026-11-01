# TDA layout parity operator review

**Review date:** 2026-10-13, America/Denver.  
**Artifact:** `prototypes/tda-layout-parity-v0.html` at source commit `f4a5472`.  
**Result:** Successful focused UX trial. The relationship and flow are accepted as a strong direction; exact styling, bindings, station content and native composition remain iterative.

## Operator findings

- Four-pane TradingView-to-Cockpit mapping works as intended and feels like a meaningful improvement in flow.
- TDA can contain as many revision-defined Decks as the full analysis requires. Each Deck can correspond to a four-pane TradingView layout and preserve the same positional mapping.
- The earlier executable runner's scrolling and mouse-button navigation remain valuable.
- Direct `1`–`4` mapped-station selection became useful quickly. It should remain in the input vocabulary trial rather than displacing the mouse behavior prematurely.
- A future macro pad or CAD-mouse equivalent is especially promising for this section once the command vocabulary stabilizes.
- Subtle complete-state colors and selected-pane borders made current position legible without focused reading.
- Peripheral orientation matters because the technician repeatedly looks away to TradingView and must reacquire the Cockpit position on return.
- The combination of focused scope, mapped spatial structure, restrained inactive panes, borders and state cues produced a notably more mature feeling than the earlier whole-cockpit walkthrough.

## Accepted interaction direction

1. **Multi-deck parity:** the process definition owns the number and order of TDA Decks. A Deck identifies its paired TradingView layout and contains the position-mapped stations required for that analytical pass. Do not impose a two-deck product limit because the alpha default currently has two.
2. **Four-pane mapping:** within each standard four-pane Deck, chart and station positions correspond directly. Alternate layout shapes can be introduced only through explicit revisioned definitions.
3. **Mapped Focus:** selecting a Deck pane opens the corresponding station operation. Returning restores the Deck, selected pane and recorded work.
4. **Shared input vocabulary:** visible mouse controls, established scrolling/back-forward navigation, number selection, keyboard shortcuts and later hardware bindings should invoke the same scoped navigation/actions. Navigation never certifies completion.
5. **Peripheral reacquisition:** selection border, current marker and state cue are functional orientation signals. They should remain distinguishable at a glance without relying on text or color alone.
6. **Quiet inactive panes:** inactive panes retain spatial identity, state and a short conclusion without competing with the active operation.

## Open design choices

- exact method for changing TradingView/Cockpit Decks together;
- whether `1`–`4` always address physical positions within the current Deck or can be remapped by user preference;
- wheel behavior when a scrollable editor has focus versus when the Deck/Focus shell has focus;
- final mouse back/forward, keyboard and macro-pad bindings;
- exact colors, border weight, icons and animation;
- explicit chart-slot identity versus existing position and chart-role metadata;
- responsive behavior outside the primary 16:9 workspace;
- final TDA station definitions, deck count and TradingView layouts.

## Design consequence

At-a-glance styling is part of task performance, not cosmetic cleanup. The next native design must treat departure to the chart monitor and rapid return as a normal interaction loop:

`Cockpit prompt → mapped TradingView pane → chart work/inspection → same Cockpit pane → retained conclusion`

Evaluation should include repeated gaze/context shifts rather than only continuous use inside the Cockpit. A later trial should place the actual TradingView layout beside the prototype/native view and check whether the technician can resume without reading headings to reconstruct position.

## Evidence boundary

This review accepts the focused relationship and interaction direction. It does not accept the prototype as final visual design, publish TDA content, choose hardware, change the native application or prove usability across other Cockpit areas. Quiet Watch/support return and Lab calendar investigation remain separate journeys.
