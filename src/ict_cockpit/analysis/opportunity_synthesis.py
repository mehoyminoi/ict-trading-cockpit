from dataclasses import dataclass, field

from ict_cockpit.analysis.market_time import temporal_relevance_for
from ict_cockpit.analysis.quarter_theory import raw_quarter_stack_relevance
from ict_cockpit.analysis.tda_station_session import TDAStationSession
from ict_cockpit.analysis.trading_session_run import (
    AuthorizationStatus,
    SetupCandidate,
    TradingRun,
    WatchPointState,
)


@dataclass(frozen=True)
class CandidateOpportunityState:
    candidate_id: str
    name: str
    source_type: str
    temporal_state: str
    temporal_detail: str
    development_state: str
    criteria_satisfied: int = 0
    criteria_total: int = 0
    criteria_required: int | None = None
    watch_points_occurred: int = 0
    watch_points_total: int = 0
    authorization_status: str = ""
    authorization_blockers: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OpportunitySituationBrief:
    session: str
    daily_quarter: str
    session_quarter: str
    thesis_state: str
    qt_alignments: tuple[dict, ...]
    candidates: tuple[CandidateOpportunityState, ...]
    authorized_count: int
    active_count: int
    upcoming_count: int
    tda_completed: int = 0
    tda_total: int = 0


def _temporal_detail(relevance: dict) -> str:
    state = str(relevance.get("state", "Not Configured"))
    window_name = str(relevance.get("window_name", "")).strip()
    minutes = relevance.get("minutes_until_start")
    if state == "Active":
        return window_name or "Configured model window active"
    if state == "Upcoming":
        return (
            (window_name or "Configured model window")
            + (f" in {minutes}m" if minutes is not None else "")
        )
    if state == "Closed":
        return "No configured model window remains at the current market time"
    if state == "Not Time-Bound":
        return "No executable time window is attached to this candidate"
    return "Temporal eligibility is not configured"


def synthesize_candidate(
    trading_run: TradingRun,
    candidate: SetupCandidate,
    tda_session: TDAStationSession | None = None,
) -> CandidateOpportunityState:
    timed_window_ids = list(
        candidate.definition_snapshot.get("timed_window_ids", []) or []
    )
    temporal = temporal_relevance_for(
        trading_run.market_time_context,
        timed_window_ids,
    )
    temporal_state = str(temporal.get("state", "Not Configured"))

    criteria = list(candidate.definition_snapshot.get("entry_criteria", []) or [])
    required = candidate.definition_snapshot.get("required_entry_count")
    criteria_satisfied = sum(
        1
        for item in criteria
        if candidate.entry_condition_states.get(str(item.get("id", "")), False)
    )

    watch_templates = list(
        candidate.definition_snapshot.get("watch_point_templates", []) or []
    )
    if (
        candidate.source_type == "Custom"
        and tda_session is not None
    ):
        watch_templates = [
            {"id": point.id}
            for point in tda_session.watch_points
        ]

    watch_points_occurred = sum(
        1
        for item in watch_templates
        if candidate.watch_point_states.get(
            str(item.get("id", "")),
            WatchPointState.WAITING,
        )
        is WatchPointState.OCCURRED
    )

    authorization = trading_run.candidate_authorization(candidate.id)
    developing = criteria_satisfied > 0 or watch_points_occurred > 0

    if temporal_state == "Closed":
        development_state = "Closed"
    elif authorization.status is AuthorizationStatus.AUTHORIZED:
        development_state = "Authorized"
    elif developing:
        development_state = "Developing"
    elif temporal_state == "Upcoming":
        development_state = "Upcoming"
    elif criteria or watch_templates:
        development_state = "Waiting"
    else:
        development_state = "Not Configured"

    return CandidateOpportunityState(
        candidate_id=candidate.id,
        name=candidate.name,
        source_type=candidate.source_type,
        temporal_state=temporal_state,
        temporal_detail=_temporal_detail(temporal),
        development_state=development_state,
        criteria_satisfied=criteria_satisfied,
        criteria_total=len(criteria),
        criteria_required=int(required) if required is not None else None,
        watch_points_occurred=watch_points_occurred,
        watch_points_total=len(watch_templates),
        authorization_status=authorization.status.value,
        authorization_blockers=tuple(authorization.blockers),
    )


def build_opportunity_situation_brief(
    trading_run: TradingRun,
    tda_session: TDAStationSession | None = None,
) -> OpportunitySituationBrief:
    included = []
    for candidate in trading_run.setup_candidates:
        if (
            candidate.source_type == "Custom"
            and not (tda_session and tda_session.watch_points)
        ):
            continue
        included.append(
            synthesize_candidate(
                trading_run,
                candidate,
                tda_session,
            )
        )
    candidates = tuple(included)
    return OpportunitySituationBrief(
        session=str(trading_run.market_time_context.get("session", "Closed")),
        daily_quarter=str(
            trading_run.market_time_context.get("daily_quarter", "")
        ),
        session_quarter=str(
            trading_run.market_time_context.get("session_quarter", "")
        ),
        thesis_state=trading_run.current_thesis_state.value,
        qt_alignments=raw_quarter_stack_relevance(
            trading_run.market_time_context,
        ),
        candidates=candidates,
        authorized_count=sum(
            1
            for item in candidates
            if item.authorization_status == AuthorizationStatus.AUTHORIZED.value
        ),
        active_count=sum(
            1 for item in candidates if item.temporal_state == "Active"
        ),
        upcoming_count=sum(
            1 for item in candidates if item.temporal_state == "Upcoming"
        ),
        tda_completed=(
            tda_session.completed_count()
            if tda_session is not None
            else 0
        ),
        tda_total=(
            len(tda_session.station_ids)
            if tda_session is not None
            else 0
        ),
    )


def candidate_opportunity_line(item: CandidateOpportunityState) -> str:
    temporal = item.temporal_state.upper()
    if item.temporal_state in {"Active", "Upcoming"} and item.temporal_detail:
        temporal += " · " + item.temporal_detail

    progress = ""
    if item.criteria_total:
        progress = (
            f" · criteria {item.criteria_satisfied}/{item.criteria_total}"
        )
        if item.criteria_required is not None:
            progress += f" (required {item.criteria_required})"
    if item.watch_points_total:
        progress += (
            f" · watch {item.watch_points_occurred}/{item.watch_points_total}"
        )

    return (
        f"{temporal} · {item.name} · {item.development_state.upper()}"
        f"{progress} · {item.authorization_status.upper()}"
    )


def situation_brief_summary(brief: OpportunitySituationBrief) -> str:
    qt = " / ".join(
        item
        for item in (brief.daily_quarter, brief.session_quarter)
        if item
    )
    context = brief.session + (f" · QT {qt}" if qt else "")
    if brief.tda_total:
        context += f" · TDA {brief.tda_completed}/{brief.tda_total}"
    context += f" · Thesis {brief.thesis_state}"

    alignments = " · ".join(
        f"{item['quarter']}×{item['count']}"
        for item in brief.qt_alignments
    )
    if alignments:
        context += f" · Stack {alignments}"

    context += (
        f" · {brief.active_count} active"
        f" · {brief.upcoming_count} upcoming"
        f" · {brief.authorized_count} authorized"
    )
    return context
