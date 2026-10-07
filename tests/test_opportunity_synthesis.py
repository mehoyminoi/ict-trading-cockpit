from datetime import datetime

from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.market_time import (
    MARKET_TIMEZONE,
    build_market_time_context,
)
from ict_cockpit.analysis.opportunity_synthesis import (
    build_opportunity_situation_brief,
    candidate_opportunity_line,
    situation_brief_summary,
)
from ict_cockpit.analysis.trading_session_run import (
    AuthorizationGateState,
    AuthorizationStatus,
    TradingRun,
)
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.live_watch_widget import LiveWatchWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def build_run_at(hour: int, minute: int) -> tuple[TradingRun, object]:
    plan = build_default_trade_plan()
    run = TradingRun(
        trading_day_id="day-1",
        session_name="Trading Run 1",
        process_session_id="process-1",
        trade_plan_revision=plan.revision,
        authorization_policy_snapshot=[
            gate.to_dict() for gate in plan.authorization_gates
        ],
        market_time_context=build_market_time_context(
            datetime(
                2026,
                10,
                6,
                hour,
                minute,
                tzinfo=MARKET_TIMEZONE,
            ),
            source="Historical Reference",
        ).to_dict(),
    )
    return run, plan


def test_synthesis_keeps_upcoming_separate_from_authorization() -> None:
    run, plan = build_run_at(9, 15)
    silver = plan.playbook_by_id("silver-bullet")
    assert silver is not None
    run.sync_playbook_candidates([silver.to_snapshot()])

    brief = build_opportunity_situation_brief(run)
    assert len(brief.candidates) == 1

    candidate = brief.candidates[0]
    assert candidate.temporal_state == "Upcoming"
    assert candidate.development_state == "Upcoming"
    assert candidate.authorization_status == AuthorizationStatus.BLOCKED.value
    assert "NYAM Silver Bullet in 45m" in candidate.temporal_detail
    assert brief.active_count == 0
    assert brief.upcoming_count == 1
    assert brief.authorized_count == 0


def test_synthesis_marks_active_partial_setup_as_developing_not_authorized() -> None:
    run, plan = build_run_at(10, 15)
    silver = plan.playbook_by_id("silver-bullet")
    mentorship = plan.playbook_by_id("2022-mentorship")
    assert silver is not None
    assert mentorship is not None
    run.sync_playbook_candidates(
        [silver.to_snapshot(), mentorship.to_snapshot()]
    )

    candidate = run.playbook_candidate("silver-bullet")
    assert candidate is not None
    run.set_candidate_entry_condition(
        candidate.id,
        "fvg-direction",
        True,
    )

    brief = build_opportunity_situation_brief(run)
    states = {item.name: item for item in brief.candidates}

    silver_state = states["Silver Bullet Model"]
    assert silver_state.temporal_state == "Active"
    assert silver_state.development_state == "Developing"
    assert silver_state.criteria_satisfied == 1
    assert silver_state.criteria_total == 3
    assert silver_state.criteria_required == 3
    assert silver_state.authorization_status == AuthorizationStatus.BLOCKED.value

    mentorship_state = states["2022 Mentorship Model"]
    assert mentorship_state.temporal_state == "Not Time-Bound"
    assert mentorship_state.development_state == "Waiting"
    assert mentorship_state.authorization_status == AuthorizationStatus.NOT_CONFIGURED.value

    assert brief.active_count == 1
    assert brief.authorized_count == 0


def test_synthesis_marks_setup_authorized_only_after_all_existing_rules_clear() -> None:
    run, plan = build_run_at(10, 15)
    silver = plan.playbook_by_id("silver-bullet")
    assert silver is not None
    run.sync_playbook_candidates([silver.to_snapshot()])
    candidate = run.playbook_candidate("silver-bullet")
    assert candidate is not None

    for criterion in silver.entry_criteria:
        run.set_candidate_entry_condition(
            candidate.id,
            criterion.id,
            True,
        )

    run.set_authorization_gate(
        "trading-day-permitted",
        AuthorizationGateState.CLEAR,
    )
    run.set_authorization_gate(
        "daily-capacity-available",
        AuthorizationGateState.CLEAR,
    )
    run.set_candidate_authorization_gate(
        candidate.id,
        "candidate-risk-within-plan",
        AuthorizationGateState.CLEAR,
    )

    brief = build_opportunity_situation_brief(run)
    candidate_state = brief.candidates[0]

    assert candidate_state.temporal_state == "Active"
    assert candidate_state.development_state == "Authorized"
    assert candidate_state.authorization_status == AuthorizationStatus.AUTHORIZED.value
    assert brief.authorized_count == 1


def test_situation_brief_line_preserves_separate_dimensions() -> None:
    run, plan = build_run_at(10, 15)
    silver = plan.playbook_by_id("silver-bullet")
    assert silver is not None
    run.sync_playbook_candidates([silver.to_snapshot()])
    candidate = run.playbook_candidate("silver-bullet")
    assert candidate is not None
    run.set_candidate_entry_condition(candidate.id, "fvg-direction", True)

    brief = build_opportunity_situation_brief(run)
    line = candidate_opportunity_line(brief.candidates[0])
    summary = situation_brief_summary(brief)

    assert "ACTIVE · Silver Bullet Model · DEVELOPING" in line
    assert "criteria 1/3 (required 3)" in line
    assert "BLOCKED" in line
    assert "NYAM" in summary
    assert "0 authorized" in summary


def test_live_watch_renders_opportunity_situation_brief() -> None:
    get_app()
    run, plan = build_run_at(10, 15)
    silver = plan.playbook_by_id("silver-bullet")
    assert silver is not None
    run.sync_playbook_candidates([silver.to_snapshot()])
    candidate = run.playbook_candidate("silver-bullet")
    assert candidate is not None
    run.set_candidate_entry_condition(candidate.id, "fvg-direction", True)

    widget = LiveWatchWidget(plan.live_watch_policy)
    widget.load_run_context(
        run,
        None,
        plan.process_blueprint,
    )

    assert "NYAM" in widget.situation_summary_label.text()
    assert "1 timed active" in widget.situation_summary_label.text()
    assert "Silver Bullet Model" in widget.situation_candidates_label.text()
    assert "DEVELOPING" in widget.situation_candidates_label.text()
    assert "BLOCKED" in widget.situation_candidates_label.text()
