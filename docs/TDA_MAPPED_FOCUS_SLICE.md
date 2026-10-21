# Native mapped TDA Focus — bounded UX3 trial

Local branch `feature/tda-mapped-focus-v0` starts from integrated Study operator acceptance `6b04866`. The existing runner now keeps the current Deck's spatial map beside the Focus editor in a non-collapsing QSplitter. The full multi-Deck overview remains reachable. Split width persists through the existing per-database workspace settings; there is no new schema, process or Trade Plan revision.

## Contract

- One TDAStationSession owns all work. Map text is derived from observations; it is not a new carry-forward field or a second editor.
- Station selection and return are navigation, never completion. Existing Mark Station Complete & Continue remains the certification action and moves the map when it crosses a Deck boundary.
- The map uses published row/column coordinates, with the same fallback as the existing full Deck renderer. The selected pane has a border plus explicit Current text; pending/in progress/complete remain textual.
- Focus names the mapped position and TradingView role. Alt+1–4 opens unique positions in the top-left 2×2 of a two-column Deck, scoped to the runner. Bare numbers remain editable text. Missing/ambiguous slots and other grid widths have no shortcut assignment.
- Existing wheel/mouse navigation is retained. Final bindings, renderer styling and hardware mapping remain open.

## Important content boundary

The current published first Deck has five stations: Instrument / Session Context, IPDA Premium / Discount, Monthly Liquidity / Wick CE, Weekly Context, and Daily Context. It is not the earlier four-station HTML prototype. This implementation preserves all five and displays the fifth at row 3. Final four-chart assignment requires a deliberate plan-definition review; neither a hidden fifth pane nor a silent station reorder is acceptable. This trial validates adjacent overview/detail mechanics, not final four-pane content parity.

## Trial

`tools/tda_mapped_focus_demo.py` uses a new separate directory and existing station-session repository. It creates no Trading Run. The guide specifies restart, selection, typing, explicit completion and resizing. Schema stays 47. No merge is authorized; operator checks remain pending.

## Developer verification

47 focused tests PASS: five mapped-Focus/demo cases plus existing dual-view/executable TDA (22 together), and runtime orientation, trading-day runtime, main-window, startup and smoke-document regression modules (25 in isolated processes). Native rendering inspected at 1440×810 and 1280×720. Python 3.10 grammar and diff checks pass. No fresh complete-suite result or operator acceptance claimed.
