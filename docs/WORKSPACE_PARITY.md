# Workspace Parity — Core UX Principle

Workspace parity is a foundational design principle for ICT Trading Cockpit.

The cockpit and the user's TradingView workspace should behave as two coordinated halves of one trading process. A cockpit mode, phase, or module should correspond intentionally to a TradingView chart layout, chart cell, or chart "deck" used for that same analytical task. The user should be able to move through both systems with the same mental and physical rhythm: inspect the chart, interpret what is present, record the conclusion, then advance.

## Core idea

The application should support a workflow like:

```text
TradingView chart/deck 1  <->  Cockpit module/phase 1
TradingView chart/deck 2  <->  Cockpit module/phase 2
TradingView chart/deck 3  <->  Cockpit module/phase 3
```

For TDA, this can mean a dedicated TradingView chart or chart cell for each focused analytical question and a matching cockpit module in the same order. Example:

1. IPDA 20/40/60 premium/discount chart -> record the IPDA conclusion in the matching cockpit module.
2. Monthly wick CEs/highs/lows chart -> record the nearest relevant monthly levels in the next module.
3. Weekly or daily PD-array / liquidity chart -> record the next layer of context in the next module.

The goal is not to duplicate TradingView inside the cockpit. TradingView remains the visual market-analysis surface; the cockpit supplies process structure, prompts, conclusions, persistence, and trade-plan context.

## Four-pane TDA parity contract

For a four-pane TradingView TDA layout, parity is spatial as well as sequential. Each chart pane can be assigned to the corresponding cockpit station pane in the same position:

| Physical position | TradingView | Cockpit Deck |
| --- | --- | --- |
| Top left | Chart pane 1 | Station pane 1 |
| Top right | Chart pane 2 | Station pane 2 |
| Bottom left | Chart pane 3 | Station pane 3 |
| Bottom right | Chart pane 4 | Station pane 4 |

The technician should be able to read the two monitors like facing pages: inspect the top-left chart, perform the station's chart action, record the relevant conclusion in the top-left cockpit pane, then continue through the same spatial order. The mapped cockpit pane supplies the criteria, points of interest, action, observation and carry-forward meaning for its chart pane. This is a foundational TDA behavior, not merely an organizational convenience or a generic overview grid.

The mapping belongs to the revisioned deck/station definition. Reordering the analytical process can deliberately update both the chart-role mapping and the cockpit layout. Ordinary navigation, window resizing or switching between Focus and Deck must not silently remap panes.

Focus and Deck remain projections of the same station state:

- Deck preserves the complete mapped spatial layout and makes current/completed/pending state legible.
- Selecting a mapped Deck pane opens that same station in Focus for detailed work.
- Returning to Deck restores the same spatial map and selected position.
- Only the active pane needs full editing detail; inactive panes can remain quiet status/conclusion cards.
- Work entered through either projection appears through the other without copying or re-entry.

The mature access mechanism may evolve beyond the current tabs, but it must preserve this positional correspondence. A list that loses the chart-cell relationship, a generic dashboard unrelated to the TradingView arrangement, or permanently expanded competing forms does not satisfy TDA layout parity.

## Current architecture fit

The mature architecture can carry this requirement without rebuilding the process engine. A Station already has a chart role and grid position metadata; a Deck has an ordered station collection and grid columns; Focus and Deck read and write one `TDAStationSession`; Deck selection opens the same station in Focus. Those are the important ownership and state boundaries for layout parity.

The current default definitions express the chart counterpart mainly through descriptive chart-role text plus row/column placement. A later renderer may benefit from an explicit stable chart-slot identifier or revisioned TradingView layout reference. That would be additive definition metadata, not a second session, copied observation store or electronic chart-control dependency. Confirm the smallest useful identity during the parity prototype rather than infer it from display labels prematurely.

## Decks and mode transitions

A TradingView layout may contain more charts than are useful at one time. The user may therefore organize the process into chart "decks" or tabs.

When one TDA phase or deck is complete, the next TradingView tab/deck should correspond naturally to the next cockpit phase or mode. For example:

```text
TDA deck -> Guided TDA
setup / execution deck -> Trade workflow
review deck -> Review / Film Night / Lab
```

The exact phases are configurable and should evolve with the user's process revisions.

## Gridfinity / Kanban character

Future workspace layout should support Gridfinity-like modularity:

- Analysis modules are discrete, understandable blocks.
- Modules can be reordered, resized, grouped, collapsed, or replaced.
- TradingView layout order and cockpit workflow order should be able to evolve together.
- A process revision may eventually describe both the logical workflow sequence and its preferred workspace arrangement.
- The layout should encourage a deliberate left-to-right or top-to-bottom flow similar to reading a page or moving through a Kanban board.
- The application should guide the user toward focused charts and focused questions instead of one overloaded chart containing every possible indicator.

Parity is therefore not a fixed hard-coded layout. The principle is that the chart environment and cockpit environment should remain intentionally synchronized in meaning and sequence.

## Trade-plan context

Relevant TDA and trade-plan context should remain easily accessible throughout later phases without competing with the current task.

The preferred design is contextual and visually subordinate: a compact reference pane, expandable module, or nearby summary rather than a permanently dominant form. The user should be able to consult prior conclusions quickly while keeping attention on the current chart/module pair.

## Design implications

Future TDA, Trade, Review, Film Night, and Lab work should be evaluated against these questions:

- Does this cockpit module have a clear visual-analysis counterpart?
- For a multi-pane TDA deck, does each cockpit pane retain the corresponding TradingView pane's physical position and chart role?
- Can the technician traverse both monitors in the same reading order without translating between unrelated layouts?
- Can the user move through the cockpit and charts in the same sequence?
- Does the layout reduce context switching and indicator clutter?
- Can the workflow and chart layout change together with intent?
- Is prior trade-plan context available without becoming distracting?
- Does the design support modular rearrangement rather than assume a permanent monolithic screen?

This principle should guide the future TDA redesign, modular workspace/Gridfinity architecture, configurable process revisions, and cross-mode navigation.
