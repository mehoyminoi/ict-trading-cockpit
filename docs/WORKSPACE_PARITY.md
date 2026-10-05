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
- Can the user move through the cockpit and charts in the same sequence?
- Does the layout reduce context switching and indicator clutter?
- Can the workflow and chart layout change together with intent?
- Is prior trade-plan context available without becoming distracting?
- Does the design support modular rearrangement rather than assume a permanent monolithic screen?

This principle should guide the future TDA redesign, modular workspace/Gridfinity architecture, configurable process revisions, and cross-mode navigation.