from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.trade_plan import (
    EntryCriterionDefinition,
    PlaybookDefinition,
    TradePlanDefinition,
    TradePlanSectionDefinition,
    WatchPointTemplateDefinition,
)


def _build_2022_mentorship_playbook() -> PlaybookDefinition:
    return PlaybookDefinition(
        id="2022-mentorship",
        name="2022 Mentorship Model",
        revision="Alpha 0.1",
        purpose=(
            "Top-down ICT model using liquidity, premium/discount, PO3/AMD, "
            "displacement, FVGs, market structure, and lower-timeframe execution."
        ),
        sessions=("London", "NYAM", "NYPM"),
        preparation=(
            "Review previous 3 weeks high/low liquidity and weekly FVG/imbalance/NWOG context.",
            "Mark previous 3 days high/low liquidity, Monday open/close, and Asia/London highs and lows.",
            "Identify bias, premium/discount state, equilibrium, and session AMD/PO3.",
            "Mark relevant session starts, killzones, opens, and recent liquidity sweeps.",
        ),
        watch_point_templates=(
            WatchPointTemplateDefinition(
                id="liquidity-displacement",
                if_condition="A relevant liquidity run develops",
                then_action="Watch for displacement, FVG formation, and market structure shift.",
            ),
            WatchPointTemplateDefinition(
                id="lower-timeframe-entry",
                if_condition="Higher-timeframe thesis and lower-timeframe displacement align",
                then_action="Wait for the lower-timeframe entry model rather than anticipating it.",
            ),
        ),
        entry_rules=(
            "Use lower-timeframe displacement/FVG and supporting order-block, breaker, or mitigation-block context.",
            "Form the thesis and rough entry/target before execution.",
        ),
        target_rules=(
            "Use 50% PD range, FVG, order block, or short-term high/low liquidity as contextual targets.",
        ),
        management_rules=("Manage according to the active Trade Plan risk and exit rules.",),
        risk_summary=(
            "No model-specific numeric stop rule is encoded here yet; account-level Trade Plan risk rules remain authoritative."
        ),
    )


def _build_silver_bullet_playbook() -> PlaybookDefinition:
    return PlaybookDefinition(
        id="silver-bullet",
        name="Silver Bullet Model",
        revision="Alpha 0.1",
        purpose=(
            "ICT Silver Bullet execution model inside defined killzones, aligned with "
            "the active draw on liquidity and broader TDA context."
        ),
        sessions=("London 03:00-04:00", "NYAM 10:00-11:00", "NYPM 14:00-15:00"),
        preparation=(
            "Complete AMDX/XAMD analysis and identify sessions/times that may correlate with the killzone.",
            "Review premium/discount and relevant premium SIBIs / discount BISIs.",
            "Identify previous week/day/session high-low draw-on-liquidity levels.",
            "Review expansion away from or return to current/old NWOG context.",
        ),
        watch_point_templates=(
            WatchPointTemplateDefinition(
                id="qualifying-fvg",
                if_condition="Price is inside an allowed Silver Bullet killzone",
                then_action="Wait for an FVG created in the killzone and in the direction of the active draw on liquidity.",
            ),
            WatchPointTemplateDefinition(
                id="delivery-distance",
                if_condition="A qualifying killzone FVG forms",
                then_action="Verify more than 10 handles of expected delivery and watch for retracement into the FVG.",
            ),
            WatchPointTemplateDefinition(
                id="retracement-entry",
                if_condition="Price retraces into the qualifying FVG",
                then_action="Evaluate the planned Fib/FVG entry and stop rule before authorization.",
            ),
        ),
        entry_criteria=(
            EntryCriterionDefinition(
                id="fvg-direction",
                name="Killzone FVG aligned with DOL",
                description="FVG was created inside the Silver Bullet killzone and in the direction of the active draw on liquidity.",
            ),
            EntryCriterionDefinition(
                id="delivery-distance",
                name=">10 handles expected delivery",
                description="The expected delivery from the setup exceeds 10 handles.",
            ),
            EntryCriterionDefinition(
                id="fvg-retracement",
                name="Retracement into qualifying FVG",
                description="Price retraced into the displacement FVG used for the planned entry.",
            ),
        ),
        required_entry_count=3,
        entry_rules=(
            "Use Fib retracement into the FVG created by displacement in the direction of the draw on liquidity.",
            "Entry reference is FVG CE or the leg 62% level.",
            "Potential confluence with the 2022 Mentorship model is supportive but is not encoded as a mandatory criterion here.",
        ),
        target_rules=(
            "Target 0.5σ, 1σ, 1.5σ, or 2σ with supporting confluence such as BISI/SIBI or NWOG.",
        ),
        management_rules=("Walk away after the planned trade process is complete.",),
        risk_summary=(
            "Model stop reference: 79% retracement or the first candle creating the FVG. Account-level Trade Plan risk limits remain authoritative."
        ),
    )


def build_default_trade_plan() -> TradePlanDefinition:
    """Return the first alpha Trade Plan definition.

    The definition is still code-seeded while the hierarchy is validated, but its
    strategy content is declarative. A future no-code editor should create the same
    PlaybookDefinition data and publish it only through an explicit Trade Plan
    revision workflow.
    """

    return TradePlanDefinition(
        id="ict-trade-plan-alpha",
        name="ICT Trading Plan",
        revision="Alpha 0.3",
        sections=(
            TradePlanSectionDefinition(
                id="foundation",
                name="Foundation",
                purpose=(
                    "Define who the trader is, what is being traded, why the "
                    "system exists, and the conditions required to operate it well."
                ),
                topics=(
                    "Objectives and motivation",
                    "Markets, instruments, sessions, and timeframes",
                    "Strengths, weaknesses, and soft-skill constraints",
                    "Physical / mental readiness and pause conditions",
                ),
            ),
            TradePlanSectionDefinition(
                id="rules-safety",
                name="Rules / Safety",
                purpose=(
                    "Define the non-negotiable boundaries that protect capital, "
                    "attention, and process integrity."
                ),
                topics=(
                    "Account and per-trade risk",
                    "Daily loss and trade-count limits",
                    "No-trade days and news restrictions",
                    "Entry authorization, exits, and lockout conditions",
                ),
            ),
            TradePlanSectionDefinition(
                id="process",
                name="Process",
                purpose=(
                    "Operate the current Trade Plan through the normal trading-day "
                    "sequence of modes, TradingView decks, decision stations, and "
                    "explicit if-then transitions."
                ),
                topics=(
                    "Premarket / TDA",
                    "Live Watch and thesis crossroads",
                    "Entry / management flow",
                    "Post-market outcome diagnosis and process review",
                ),
            ),
            TradePlanSectionDefinition(
                id="playbooks",
                name="Playbooks",
                purpose=(
                    "Define the valid models, their setup conditions, triggers, "
                    "management rules, and examples."
                ),
                topics=(
                    "2022 Mentorship model",
                    "Silver Bullet",
                    "Friday Asian Range / TGIF",
                    "Future models unlocked through evidence and mastery",
                ),
            ),
            TradePlanSectionDefinition(
                id="review-development",
                name="Review / Development",
                purpose=(
                    "Improve the Trade Plan through deliberate study, evidence review, "
                    "feedback, and controlled revision. This area is directly enterable "
                    "and does not require completing the trading-day Process first."
                ),
                topics=(
                    "Film Night / Lab study sessions",
                    "Backtesting with an explicit study question",
                    "Cross-trade and cross-day pattern review",
                    "Feedback and friction review",
                    "Revision proposals backed by evidence",
                ),
            ),
        ),
        process_blueprint=build_default_process_blueprint(),
        playbooks=(
            _build_2022_mentorship_playbook(),
            _build_silver_bullet_playbook(),
        ),
    )
