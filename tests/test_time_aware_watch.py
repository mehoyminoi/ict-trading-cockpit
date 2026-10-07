from datetime import datetime

from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, build_market_time_context
from ict_cockpit.analysis.trading_session_run import (
    AuthorizationGateState,
    AuthorizationStatus,
    TradingRun,
)
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.live_watch_widget import LiveWatchWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def build_silver_run(hour: int, minute: int):
    plan = build_default_trade_plan()
    silver = plan.playbook_by_id("silver-bullet")
    assert silver is not None

    context = build_market_time_context(
        datetime(2026, 10, 6, hour, minute, tzinfo=MARKET_TIMEZONE),
        source="Historical Reference",
    ).to_dict()
    run = TradingRun(
        "day-1",
        "Trading Run 1",
        "process-1",
        trade_plan_revision=plan.revision,
        authorization_policy_snapshot=plan.authorization_snapshot(),
        market_time_context=context,
    )
    run.sync_playbook_candidates([silver.to_snapshot()])
    candidate = run.playbook_candidate("silver-bullet")
    assert candidate is not None
    return plan, run, candidate


def clear_all_non_time_gates(run: TradingRun, candidate_id: str) -> None:
    run.set_authorization_gate(
        "trading-day-permitted",
        AuthorizationGateState.CLEAR,
    )
    run.set_authorization_gate(
        "daily-capacity-available",
        AuthorizationGateState.CLEAR,
    )
    run.set_candidate_authorization_gate(
        candidate_id,
        "candidate-risk-within-plan",
        AuthorizationGateState.CLEAR,
    )
    for criterion_id in (
        "fvg-direction",
        "delivery-distance",
        "fvg-retracement",
    ):
        run.set_candidate_entry_condition(candidate_id, criterion_id, True)


def test_upcoming_timed_model_is_blocked_until_window_is_active() -> None:
    _plan, run, candidate = build_silver_run(9, 15)
    clear_all_non_time_gates(run, candidate.id)

    result = run.candidate_authorization(candidate.id)

    assert result.status is AuthorizationStatus.BLOCKED
    assert any("upcoming in 45m" in blocker for blocker in result.blockers)


def test_active_timed_model_can_authorize_when_other_rules_clear() -> None:
    _plan, run, candidate = build_silver_run(10, 15)
    clear_all_non_time_gates(run, candidate.id)

    result = run.candidate_authorization(candidate.id)

    assert result.status is AuthorizationStatus.AUTHORIZED
    assert result.blockers == []


def test_closed_timed_model_remains_blocked_even_when_other_rules_clear() -> None:
    _plan, run, candidate = build_silver_run(15, 5)
    clear_all_non_time_gates(run, candidate.id)

    result = run.candidate_authorization(candidate.id)

    assert result.status is AuthorizationStatus.BLOCKED
    assert any("closed for the current market time" in blocker for blocker in result.blockers)


def test_old_silver_bullet_snapshot_does_not_gain_new_time_gate() -> None:
    plan, run, candidate = build_silver_run(9, 15)
    old_snapshot = dict(candidate.definition_snapshot)
    old_snapshot["revision"] = "Alpha 0.2"
    old_snapshot.pop("timed_window_ids", None)
    run.sync_playbook_candidates([])
    run.sync_playbook_candidates([old_snapshot])
    old_candidate = run.playbook_candidate("silver-bullet")
    assert old_candidate is not None
    clear_all_non_time_gates(run, old_candidate.id)

    result = run.candidate_authorization(old_candidate.id)

    assert result.status is AuthorizationStatus.AUTHORIZED


def test_watch_surfaces_upcoming_timed_candidate_with_countdown() -> None:
    get_app()
    _plan, run, candidate = build_silver_run(9, 15)
    widget = LiveWatchWidget()
    widget.load_run_context(
        run,
        None,
        build_default_process_blueprint(),
    )

    relevance = widget.candidate_temporal_relevance[candidate.id]
    assert relevance["state"] == "Upcoming"
    assert relevance["window_id"] == "nyam-silver-bullet"
    assert (candidate.id, "fvg-direction") in widget.candidate_entry_checkboxes


def test_watch_quiets_closed_timed_candidate_controls() -> None:
    get_app()
    _plan, run, candidate = build_silver_run(15, 5)
    widget = LiveWatchWidget()
    widget.load_run_context(
        run,
        None,
        build_default_process_blueprint(),
    )

    relevance = widget.candidate_temporal_relevance[candidate.id]
    assert relevance["state"] == "Closed"
    assert (candidate.id, "fvg-direction") not in widget.candidate_entry_checkboxes
    assert (candidate.id, "qualifying-fvg") not in widget.candidate_watch_point_combos
