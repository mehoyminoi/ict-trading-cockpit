from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.trade_plan import (
    TradePlanDefinition,
    TradePlanSectionDefinition,
)


def build_default_trade_plan() -> TradePlanDefinition:
    """Return the first alpha Trade Plan definition.

    This remains code-defined and read-only while the hierarchy is validated.
    The Trade Plan defines the whole system. Its Process section is the normal
    trading-day operating path; Review / Development is a parallel improvement
    area that can be entered directly for study, backtesting, or revision work.
    """

    return TradePlanDefinition(
        id="ict-trade-plan-alpha",
        name="ICT Trading Plan",
        revision="Alpha 0.2",
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
    )
