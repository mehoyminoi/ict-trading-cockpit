from ict_cockpit.process_blueprint import (
    DeckDefinition,
    ModeDefinition,
    ProcessBlueprint,
    StationDefinition,
)


def build_default_process_blueprint() -> ProcessBlueprint:
    """Return the first explicit process map used to shape alpha workflows.

    This is intentionally a code-defined alpha blueprint rather than a permanent
    workflow editor format. The goal is to validate the Process -> Mode -> Deck
    -> Station hierarchy before making definitions persistent/configurable.
    """

    tda_deck_1 = DeckDefinition(
        id="tda-context",
        name="TDA Deck 1 — Higher-Timeframe Context",
        tradingview_layout="TDA / Higher-Timeframe Context",
        stations=(
            StationDefinition(
                id="tda-instrument-context",
                name="Instrument / Session Context",
                question="What market and analysis session am I preparing for?",
                tradingview_role="Orient the chart deck to the instrument and date under review.",
                reference="Cockpit context should remain available without competing with chart reading.",
            ),
            StationDefinition(
                id="tda-ipda-premium-discount",
                name="IPDA Premium / Discount",
                question="Where is price within the relevant 20 / 40 / 60 day IPDA ranges?",
                tradingview_role="Dedicated chart cell with the custom 20/40/60 IPDA premium/discount view.",
                reference="Read the chart first, then record the observed location/state.",
            ),
            StationDefinition(
                id="tda-monthly-liquidity",
                name="Monthly Liquidity / Wick CE",
                question="Which nearby monthly highs, lows, and wick consequent encroachments matter now?",
                tradingview_role="Dedicated chart cell showing the nearest monthly wick CEs, highs, and lows.",
                reference="Keep unrelated arrays off this chart so the station answers one question clearly.",
            ),
            StationDefinition(
                id="tda-weekly-context",
                name="Weekly Context",
                question="What is the weekly directional context and what is price drawing toward?",
                tradingview_role="Weekly-context chart cell with only the indicators required for this decision.",
            ),
            StationDefinition(
                id="tda-daily-context",
                name="Daily Context",
                question="What is the daily directional context and primary draw on liquidity?",
                tradingview_role="Daily-context chart cell paired with the matching cockpit decision station.",
            ),
        ),
    )

    tda_deck_2 = DeckDefinition(
        id="tda-thesis",
        name="TDA Deck 2 — Thesis / Execution Context",
        tradingview_layout="TDA / Thesis and Execution Context",
        stations=(
            StationDefinition(
                id="tda-primary-draw",
                name="Primary Draw",
                question="What is the highest-conviction draw on price after completing higher-timeframe context?",
                tradingview_role="Synthesis chart/deck view used only after the prior context stations are complete.",
            ),
            StationDefinition(
                id="tda-secondary-draw",
                name="Secondary / Alternate Draw",
                question="What secondary draw or alternate path should remain visible if the primary thesis fails?",
                tradingview_role="Use the same synthesis deck without adding unrelated decision clutter.",
            ),
            StationDefinition(
                id="tda-thesis",
                name="Premarket Thesis",
                question="What do I expect, what would invalidate it, and what would make no-trade the correct outcome?",
                tradingview_role="Final TDA chart state before transitioning to live-watch mode.",
                reference="The thesis should later be compared with what actually occurred, not judged only by P&L.",
            ),
        ),
    )

    live_deck = DeckDefinition(
        id="live-watch",
        name="Live Watch Deck",
        tradingview_layout="Live Watch / Execution Context",
        stations=(
            StationDefinition(
                id="live-thesis-reference",
                name="Carry Forward TDA",
                question="What parts of the active TDA thesis matter most right now?",
                tradingview_role="Live chart deck with TDA context available as subordinate reference.",
            ),
            StationDefinition(
                id="live-thesis-crossroads",
                name="Thesis Crossroads",
                question=(
                    "Is current price action still supporting the thesis, weakening it, "
                    "invalidating it, or providing enough new evidence to deliberately pivot?"
                ),
                tradingview_role="Pause at meaningful new information; compare live evidence with the saved thesis and invalidation.",
                reference=(
                    "Changing the thesis is not failure. A pivot should be an explicit process result, "
                    "with uncertainty allowed to resolve to no-trade or a return to analysis."
                ),
            ),
            StationDefinition(
                id="live-setup-state",
                name="Setup State",
                question="Is an allowed setup developing, absent, or invalidated?",
                tradingview_role="Execution-context charts; avoid turning the cockpit into an additional charting surface.",
            ),
        ),
    )

    review_deck = DeckDefinition(
        id="post-market-review",
        name="Post-Market Review Deck",
        tradingview_layout="Review / Outcome",
        stations=(
            StationDefinition(
                id="review-thesis-outcome",
                name="Thesis vs Outcome",
                question="What matched the premarket thesis, what differed, and why?",
                tradingview_role="Review chart deck showing the completed day beside the saved premarket analysis.",
            ),
            StationDefinition(
                id="review-outcome-diagnosis",
                name="Outcome Diagnosis",
                question=(
                    "What explains the outcome: market information, thesis quality, execution, "
                    "process adherence, or a combination of these?"
                ),
                tradingview_role="Use the full trade/day as evidence without reducing the diagnosis to win or loss.",
                reference=(
                    "After a losing trade, explicitly ask what was missed, what changed after entry, "
                    "whether process broke down, and what should be tested or adjusted next time."
                ),
            ),
            StationDefinition(
                id="review-process",
                name="Process Review",
                question="Was the process followed regardless of the trade outcome?",
                tradingview_role="Use charts as evidence; process adherence remains separate from P&L.",
            ),
        ),
    )

    lab_deck = DeckDefinition(
        id="film-night-lab",
        name="Film Night / Lab Deck",
        tradingview_layout="Film Night / Lab",
        stations=(
            StationDefinition(
                id="lab-study-question",
                name="Study Question",
                question="What concept, lecture idea, or market behavior am I testing?",
                tradingview_role="Replay/backtest deck arranged specifically for the research question.",
            ),
            StationDefinition(
                id="lab-capture-find",
                name="Capture Find",
                question="What observation is worth preserving as structured evidence?",
                tradingview_role="Capture charts into Study Find without interrupting the research sequence.",
            ),
        ),
    )

    return ProcessBlueprint(
        id="ict-process-alpha",
        name="ICT Trading Process",
        revision="Alpha 0.1",
        modes=(
            ModeDefinition(
                id="tda",
                name="Premarket / TDA",
                purpose="Build market context and an explicit thesis before live observation.",
                decks=(tda_deck_1, tda_deck_2),
            ),
            ModeDefinition(
                id="live-watch",
                name="Live Watch",
                purpose="Observe price through the active thesis without losing process context.",
                decks=(live_deck,),
            ),
            ModeDefinition(
                id="post-market",
                name="Post-Market Review",
                purpose="Compare thesis, outcome, adherence, and learning after the session.",
                decks=(review_deck,),
            ),
            ModeDefinition(
                id="lab",
                name="Film Night / Lab",
                purpose="Study concepts, replay examples, and accumulate structured evidence.",
                decks=(lab_deck,),
            ),
        ),
    )
