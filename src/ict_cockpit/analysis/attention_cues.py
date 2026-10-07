from dataclasses import dataclass
from enum import Enum

from ict_cockpit.analysis.market_time import temporal_relevance_for
from ict_cockpit.analysis.trading_session_run import TradingRun


DEFAULT_PREPARE_LEAD_MINUTES = 30


class AttentionCueLevel(str, Enum):
    QUIET = "Quiet"
    MONITOR = "Monitor"
    PREPARE = "Prepare"
    FOCUS = "Focus"


@dataclass(frozen=True)
class AttentionCue:
    level: AttentionCueLevel
    headline: str
    detail: str = ""
    candidate_id: str = ""
    candidate_name: str = ""
    window_id: str = ""
    window_name: str = ""
    minutes_until_start: int | None = None

    @property
    def style_key(self) -> str:
        """Stable semantic hook for future visual/peripheral styling."""

        return self.level.value.lower()


def build_attention_cue(
    trading_run: TradingRun,
    *,
    prepare_lead_minutes: int = DEFAULT_PREPARE_LEAD_MINUTES,
) -> AttentionCue:
    """Return the most time-urgent cue without assigning setup potency.

    Attention answers *when to look*. It does not answer whether a setup is
    high quality, directional, probable, or authorized.
    """

    lead = max(int(prepare_lead_minutes), 0)
    active = []
    upcoming = []

    for candidate in trading_run.setup_candidates:
        timed_window_ids = list(
            candidate.definition_snapshot.get("timed_window_ids", []) or []
        )
        if not timed_window_ids:
            continue

        relevance = temporal_relevance_for(
            trading_run.market_time_context,
            timed_window_ids,
        )
        state = str(relevance.get("state", ""))
        item = (candidate, relevance)

        if state == "Active":
            active.append(item)
        elif state == "Upcoming":
            upcoming.append(item)

    if active:
        candidate, relevance = sorted(
            active,
            key=lambda item: item[0].name,
        )[0]
        window_name = str(relevance.get("window_name", "")).strip()
        return AttentionCue(
            level=AttentionCueLevel.FOCUS,
            headline=f"FOCUS · {window_name or candidate.name} active",
            detail=(
                "A configured model window is active. Attention cue only; "
                "setup development and authorization remain separate."
            ),
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            window_id=str(relevance.get("window_id", "")),
            window_name=window_name,
            minutes_until_start=0,
        )

    if upcoming:
        candidate, relevance = min(
            upcoming,
            key=lambda item: (
                int(item[1].get("minutes_until_start", 10**9)),
                item[0].name,
            ),
        )
        minutes = relevance.get("minutes_until_start")
        minutes = int(minutes) if minutes is not None else None
        window_name = str(relevance.get("window_name", "")).strip()
        display_name = window_name or candidate.name

        if minutes is not None and minutes <= lead:
            return AttentionCue(
                level=AttentionCueLevel.PREPARE,
                headline=f"PREPARE · {display_name} in {minutes}m",
                detail=(
                    f"Inside the {lead}-minute attention lead. "
                    "Consider shifting attention toward the chart; this is not trade permission."
                ),
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                window_id=str(relevance.get("window_id", "")),
                window_name=window_name,
                minutes_until_start=minutes,
            )

        timing = f" in {minutes}m" if minutes is not None else ""
        return AttentionCue(
            level=AttentionCueLevel.MONITOR,
            headline=f"MONITOR · {display_name}{timing}",
            detail=(
                f"Next configured timed opportunity is outside the {lead}-minute "
                "prepare lead."
            ),
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            window_id=str(relevance.get("window_id", "")),
            window_name=window_name,
            minutes_until_start=minutes,
        )

    return AttentionCue(
        level=AttentionCueLevel.QUIET,
        headline="QUIET · no configured timed opportunity needs immediate attention",
        detail=(
            "No selected time-bound setup currently has an active or upcoming "
            "window today. Non-time-bound analysis remains available."
        ),
    )
