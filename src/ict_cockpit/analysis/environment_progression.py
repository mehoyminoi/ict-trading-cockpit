from dataclasses import dataclass
from enum import Enum

from ict_cockpit.analysis.trading_session_run import (
    RunEnvironment,
    RunPurpose,
    default_purpose_for_environment,
)


class EnvironmentEligibilityStatus(str, Enum):
    AVAILABLE = "Available"
    NOT_CONFIGURED = "Not Configured"
    BLOCKED = "Blocked"


@dataclass(frozen=True)
class EnvironmentEligibility:
    environment: RunEnvironment
    purpose: RunPurpose
    status: EnvironmentEligibilityStatus
    detail: str
    recommended_environment: RunEnvironment | None = None

    @property
    def can_launch(self) -> bool:
        """Launch remains allowed until an explicit Trade Plan gate exists."""

        return self.status is not EnvironmentEligibilityStatus.BLOCKED


def evaluate_environment_eligibility(
    environment: RunEnvironment | str,
) -> EnvironmentEligibility:
    """Describe progression readiness without inventing proficiency thresholds.

    Historical Backtest is the foundation environment and is always available.
    Higher environments remain explicitly Not Configured until the Trade Plan
    publishes progression criteria. Future policy evaluation can return Blocked
    with concrete reasons and a recommended lower rung.
    """

    environment = RunEnvironment(environment)
    purpose = default_purpose_for_environment(environment)

    if environment is RunEnvironment.HISTORICAL_BACKTEST:
        return EnvironmentEligibility(
            environment=environment,
            purpose=purpose,
            status=EnvironmentEligibilityStatus.AVAILABLE,
            detail=(
                "Foundation study environment is available for focused concept "
                "practice and evidence collection."
            ),
        )

    recommended = {
        RunEnvironment.REPLAY: RunEnvironment.HISTORICAL_BACKTEST,
        RunEnvironment.FORWARD_TEST: RunEnvironment.REPLAY,
        RunEnvironment.LIVE: RunEnvironment.FORWARD_TEST,
    }[environment]

    return EnvironmentEligibility(
        environment=environment,
        purpose=purpose,
        status=EnvironmentEligibilityStatus.NOT_CONFIGURED,
        detail=(
            "No Trade Plan progression criteria are published for this environment yet. "
            "Readiness is therefore unknown, not proven."
        ),
        recommended_environment=recommended,
    )
