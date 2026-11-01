# TDA layout parity interaction specification

**Status:** Focused relationship/flow accepted by operator review on 2026-10-13. The disposable standalone prototype remains an interaction study rather than final styling or native implementation. See [the operator review](TDA_LAYOUT_PARITY_OPERATOR_REVIEW.md).

Read with [Workspace Parity](WORKSPACE_PARITY.md), [UX Design Touchstones](UX_DESIGN_TOUCHSTONES.md) and [UX Friction Research](UX_FRICTION_RESEARCH.md).

## Review question

Can one TradingView TDA deck and one Cockpit TDA Deck behave as two facing pages of the same analytical workspace, while Focus gives the selected station enough room to work?

This review is about spatial correspondence, attention, state sharing and return behavior. Station wording is representative rather than a proposed Rev0 TDA definition.

## Prototype scope

The prototype represents one four-pane higher-timeframe TDA deck:

| Position | Chart role | Cockpit station |
| --- | --- | --- |
| Top left / 1 | IPDA 20/40/60 premium-discount | Range Position |
| Top right / 2 | Monthly highs, lows and wick CE | Monthly Liquidity |
| Bottom left / 3 | Weekly context and draw | Weekly Context |
| Bottom right / 4 | Daily context and draw | Daily Context |

The chart side is schematic. It demonstrates identity, spatial order and attention correspondence without embedding, controlling or reproducing TradingView.

The mature TDA may contain however many revision-defined Decks are required to gather the full analysis. Each standard Deck can pair with its own four-pane TradingView layout while reusing this positional and Focus-return contract. The prototype's single Deck is a bounded interaction sample, not a product limit.

## Proposed interaction

### Deck orientation

- Deck is the starting state for this prototype.
- The TradingView schematic and Cockpit Deck use the same 2×2 layout.
- Each pair carries a stable slot number, position name and chart/station role.
- Current, in-progress, complete and pending are station states. Selection is a separate cue.
- An inactive station shows a short conclusion when one exists; it does not expose a second full editor.

### Deck to Focus

- Clicking a cockpit pane selects that station and opens Focus in one action.
- The mapped chart pane stays highlighted as the external visual-analysis target.
- Focus states the chart position and chart role before the analytical prompts.
- The station separates Action, Observe and Carry Forward.
- Editing updates the same shared state used by Deck. There is no secondary draft or copy step.

### Focus to Deck

- **Return to mapped Deck** returns to the same four-pane arrangement and selected slot.
- The station's recorded work appears as a short conclusion/status in that same pane.
- Returning is navigation. It does not mark the station complete.
- **Mark complete & next** is deliberate certification, then selects the next mapped position in reading order.

### Efficient access

The prototype supplies visible controls plus provisional keys:

- `D` returns to Deck,
- `1`–`4` open the mapped station,
- `[` and `]` move to the prior/next station without completing it,
- `Ctrl+Enter` marks the current station complete and advances.

These keys test action vocabulary for later keyboard/macro-pad use. They are not accepted final bindings.

Operator review found the `1`–`4` mapping promising and retained the earlier executable runner's scrolling and mouse-button behavior as valuable. Mature input design should test them together as routes to the same actions. A macro pad or CAD-mouse equivalent remains a later binding surface after the command vocabulary stabilizes.

### Persistence for review

The standalone prototype stores its disposable state in browser local storage so reload can demonstrate reacquaintance. **Reset prototype** clears only this HTML prototype's local state.

## Information hierarchy

Always visible in this focused proposal:

- current deck and its TradingView layout name,
- current mapped position,
- four chart/station relationships while in Deck,
- a compact progress count,
- direct Deck access.

Visible in Focus:

- mapped chart position and role,
- current station state,
- Actions,
- Observation,
- Carry Forward,
- explicit completion and return controls.

Deferred from this focused prototype:

- whole-cockpit navigation,
- AMDX stack and calendar,
- Study Find capture,
- TDA Deck 2 and deck-to-deck transition,
- editing the Trade Plan/deck definition,
- actual TradingView communication,
- final colors, icons, typography and macro-pad bindings.

Those omissions keep the parity question observable. They are not removals from the whole-cockpit requirements.

## Architecture mapping

| Prototype concept | Existing native substrate | Possible additive follow-up |
| --- | --- | --- |
| Deck identity | `DeckDefinition.id`, name and `tradingview_layout` | Stable external layout reference if real use needs one |
| Slot position | Station `layout_row`, `layout_column`, spans; deck grid columns | Explicit `chart_slot_id` if position and chart-role text are insufficient |
| Chart role | `StationDefinition.tradingview_role` | Structured chart-role metadata only after prototype evidence |
| Shared work | One `TDAStationSession` used by Focus and Deck | Separate Carry Forward field may be warranted by workflow review |
| Deck → Focus | Existing `open_station_from_deck()` | Presentation replacement can reuse the same action semantics |
| Completion | Existing explicit station completion | No change implied |

The data architecture therefore supports the proposal. The main unresolved work is native composition and whether chart-slot identity needs to become more explicit than position plus chart-role text.

## Goal-based review tasks

1. From Deck, identify which cockpit pane corresponds to the bottom-left TradingView chart and open it.
2. In Focus, complete one chart Action, enter an Observation and a Carry Forward conclusion, then return without completing the station.
3. Confirm the bottom-left Deck pane remains selected, shows in-progress state and exposes the retained conclusion without showing the full form.
4. Reopen that pane, mark it complete and advance. Confirm the next mapped chart/station pair becomes current.
5. Reload the file. Confirm the selected deck position, work and states are understandable without reconstructing them.
6. Use `1`–`4` and `D` once. Judge whether the visible mapping remains understandable without knowing the keys in advance.

Record whether the operator hunted for the chart/station relationship, lost spatial orientation, confused return with completion, or needed to re-enter work. The visual styling and specific TDA content can receive notes without being treated as accepted design.

## Acceptance boundary

This proposal is useful if it makes layout parity tangible and gives us evidence about Deck/Focus movement. Operator review may accept the relationship while rejecting the exact split, styling, labels or controls. Native implementation begins only after the interaction contract is reviewed against the real multi-monitor workflow.

The 2026-10-13 trial succeeded on that boundary. Positional mapping, Deck/Focus flow, shared work, quiet inactive panes and at-a-glance orientation are accepted directions. Exact controls, styling and native implementation remain open.
