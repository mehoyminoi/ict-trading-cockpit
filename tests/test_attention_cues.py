from datetime import datetime

from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.attention_cues import (
    AttentionCueLevel,
    build_attention_cue,
)
from ict_cockpit.analysis.market_time import (
    MARKET_TIMEZONE,
    build_market_time_context,
)
from ict_cockpit.analysis.trading_session_run import TradingRun
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.live_watch_widget import LiveWatchWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def build_run_at(hour: int, minute: int, playbook_ids: tuple[str, ...]):
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
    snapshots = []
    for playbook_id in playbook_ids:
        playbook = plan.playbook_by_id(playbook_id)
        assert playbook is not None
        snapshots.append(playbook.to_snapshot())
    run.sync_playbook_candidates(snapshots)
    return run, plan


def test_attention_cue_monitors_when_next_window_is_outside_prepare_lead() -> None:
    run, _plan = build_run_at(9, 15, ("silver-bullet",))

    cue = build_attention_cue(run)

    assert cue.level is AttentionCueLevel.MONITOR
    assert cue.minutes_until_start == 45
    assert cue.window_name == "NYAM Silver Bullet"
    assert cue.headline == "MONITOR · NYAM Silver Bullet in 45m"
    assert cue.style_key == "monitor"


def test_attention_cue_prepares_inside_default_30_minute_lead() -> None:
    run, _plan = build_run_at(9, 35, ("silver-bullet",))

    cue = build_attention_cue(run)

    assert cue.level is AttentionCueLevel.PREPARE
    assert cue.minutes_until_start == 25
    assert cue.headline == "PREPARE · NYAM Silver Bullet in 25m"
    assert "30-minute attention lead" in cue.detail


def test_attention_cue_focuses_when_configured_window_is_active() -> None:
    run, _plan = build_run_at(10, 15, ("silver-bullet",))

    cue = build_attention_cue(run)

    assert cue.level is AttentionCueLevel.FOCUS
    assert cue.minutes_until_start == 0
    assert cue.headline == "FOCUS · NYAM Silver Bullet active"
    assert "not trade permission" not in cue.headline.lower()
    assert "authorization remain separate" in cue.detail


def test_attention_cue_quiet_after_last_selected_timed_window() -> None:
    run, _plan = build_run_at(15, 5, ("silver-bullet",))

    cue = build_attention_cue(run)

    assert cue.level is AttentionCueLevel.QUIET
    assert cue.minutes_until_start is None
    assert cue.headline.startswith("QUIET ·")


def test_non_time_bound_model_does_not_create_clock_attention_pressure() -> None:
    run, _plan = build_run_at(10, 15, ("2022-mentorship",))

    cue = build_attention_cue(run)

    assert cue.level is AttentionCueLevel.QUIET


def test_attention_cue_uses_configurable_prepare_lead_without_plan_change() -> None:
    run, _plan = build_run_at(9, 15, ("silver-bullet",))

    default_cue = build_attention_cue(run)
    wider_cue = build_attention_cue(run, prepare_lead_minutes=60)

    assert default_cue.level is AttentionCueLevel.MONITOR
    assert wider_cue.level is AttentionCueLevel.PREPARE
    assert wider_cue.minutes_until_start == 45


def test_live_watch_exposes_attention_level_for_future_styling() -> None:
    get_app()
    run, plan = build_run_at(9, 35, ("silver-bullet",))

    widget = LiveWatchWidget(plan.live_watch_policy)
    widget.load_run_context(
        run,
        None,
        plan.process_blueprint,
    )

    assert widget.attention_cue_label.text() == (
        "PREPARE · NYAM Silver Bullet in 25m"
    )
    assert widget.attention_cue_label.property("attentionLevel") == "prepare"
    assert "not trade permission" in widget.attention_cue_label.toolTip()
