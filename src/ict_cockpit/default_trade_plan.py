from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.trade_plan import (
    TradePlanDefinition,
    TradePlanSectionDefinition,
)


def build_default_trade_plan() -> TradePlanDefinition:
    """Return the first alpha Trade Plan definition.

    This remains code-defined and read-only while the hierarchy is validated.
    The process blueprint is nested inside the plan rather than acting as the
    top-level system definition.
    """

    return TradePlanDefinition(
        id="ict-trade-plan-alpha",
        name="ICT Trading Plan",
        revision="Alpha 0.1",
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
                    "Execute the plan through ordered modes, TradingView decks, "
                    "decision stations, and explicit if-then transitions."
                ),
                topics=(
                    "Premarket / TDA",
                    "Live Watch and thesis crossroads",
                    "Entry / management flow",
                    "Post-market outcome diagnosis",
                    "Film Night / Lab study loop",
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
                    "Observe execution, diagnose outcomes, study deliberately, "
                    "and turn evidence into controlled plan revisions."
                ),
                topics=(
                    "Thesis vs outcome review",
                    "Loss / win diagnosis and process adherence",
                    "Structured Film Night / Lab questions",
                    "Feedback, study evidence, and revision proposals",
                ),
            ),
        ),
        process_blueprint=build_default_process_blueprint(),
    )
