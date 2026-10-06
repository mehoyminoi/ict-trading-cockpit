from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import (
    AuthorizationGateState,
    AuthorizationStatus,
    TradingRun,
    WatchPointState,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget
from ict_cockpit.trade_plan import PlaybookDefinition


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def build_shell_with_plan() -> tuple:
    plan = build_default_trade_plan()
    shell = TradingDayShellWidget(
        plan.process_blueprint,
        playbooks=plan.playbooks,
        authorization_gates=plan.authorization_gates,
        trade_plan_revision=plan.revision,
    )
    return plan, shell


def select_silver_bullet(shell: TradingDayShellWidget):
    runner = shell.runtime.tda_station_runner_widget
    runner.select_station("tda-thesis")
    editor = shell.runtime.tda_watch_point_widget
    for index in range(editor.models_list.count()):
        item = editor.models_list.item(index)
        if item.data(Qt.ItemDataRole.UserRole) == "silver-bullet":
            item.setCheckState(Qt.CheckState.Checked)
            break
    run = shell.active_trading_run
    assert run is not None
    candidate = run.playbook_candidate("silver-bullet")
    assert candidate is not None
    return candidate


def test_default_trade_plan_exposes_declarative_playbooks() -> None:
    plan = build_default_trade_plan()
    assert plan.revision == "Alpha 0.5"
    assert [playbook.id for playbook in plan.playbooks] == ["2022-mentorship", "silver-bullet"]
    assert [gate.id for gate in plan.authorization_gates] == [
        "trading-day-permitted",
        "daily-capacity-available",
        "candidate-risk-within-plan",
    ]
    silver_bullet = plan.playbook_by_id("silver-bullet")
    assert silver_bullet is not None
    assert silver_bullet.revision == "Alpha 0.2"
    assert silver_bullet.required_entry_count == 3
    assert len(silver_bullet.entry_criteria) == 3
    assert silver_bullet.watch_point_templates[0].satisfies_criterion_ids == ("fvg-direction",)
    assert "79%" in silver_bullet.risk_summary


def test_playbook_snapshot_round_trip_is_data_only() -> None:
    plan = build_default_trade_plan()
    original = plan.playbook_by_id("silver-bullet")
    assert original is not None
    snapshot = original.to_snapshot()
    restored = PlaybookDefinition.from_snapshot(snapshot)
    assert restored == original
    assert isinstance(snapshot["entry_criteria"], list)
    assert isinstance(snapshot["watch_point_templates"], list)
    assert snapshot["watch_point_templates"][0]["satisfies_criterion_ids"] == ["fvg-direction"]


def test_schema_v22_adds_authorization_and_market_time_storage(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(trading_session_run)").fetchall()
    }
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    assert version == CURRENT_SCHEMA_VERSION == 22
    assert "setup_candidates_json" in columns
    assert "authorization_policy_snapshot_json" in columns
    assert "authorization_gate_states_json" in columns
    assert "market_time_context_json" in columns
    assert "selected_playbook_id" in columns
    connection.close()


def test_multiple_setup_candidates_and_authorization_round_trip(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    day_repository = TradingDayRepository(connection)
    process_repository = TradingDaySessionRepository(connection)
    run_repository = TradingSessionRunRepository(connection)

    plan = build_default_trade_plan()
    mentorship = plan.playbook_by_id("2022-mentorship")
    silver = plan.playbook_by_id("silver-bullet")
    assert mentorship is not None and silver is not None

    day = TradingDay(futures_day_label="2026-10-06")
    process_session = TradingDaySession(
        blueprint_revision=plan.process_blueprint.revision,
        mode_ids=[mode.id for mode in plan.process_blueprint.modes],
        current_mode_id="tda",
    )
    process_repository.save(process_session)
    run = TradingRun(
        day.id,
        "Trading Run 1",
        process_session.id,
        trade_plan_revision=plan.revision,
        authorization_policy_snapshot=plan.authorization_snapshot(),
    )
    run.ensure_day_specific_candidate()
    run.sync_playbook_candidates([mentorship.to_snapshot(), silver.to_snapshot()])
    run.set_authorization_gate("trading-day-permitted", AuthorizationGateState.CLEAR)
    silver_candidate = run.playbook_candidate("silver-bullet")
    assert silver_candidate is not None
    run.set_candidate_authorization_gate(
        silver_candidate.id,
        "candidate-risk-within-plan",
        AuthorizationGateState.CLEAR,
    )
    day.activate_trading_run(run)
    day_repository.save(day)
    run_repository.save(run)

    restored = run_repository.get_by_id(run.id)
    assert restored is not None
    assert {item.source_id for item in restored.setup_candidates} == {
        "day-specific",
        "2022-mentorship",
        "silver-bullet",
    }
    assert restored.authorization_gate_states["trading-day-permitted"] is AuthorizationGateState.CLEAR
    restored_silver = restored.playbook_candidate("silver-bullet")
    assert restored_silver is not None
    assert restored_silver.authorization_gate_states["candidate-risk-within-plan"] is AuthorizationGateState.CLEAR
    connection.close()


def test_tda_models_in_play_are_multi_select_and_live_readiness_is_per_candidate() -> None:
    get_app()
    plan, shell = build_shell_with_plan()
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None
    runner = shell.runtime.tda_station_runner_widget
    runner.select_station("tda-thesis")
    editor = shell.runtime.tda_watch_point_widget

    for index in range(editor.models_list.count()):
        item = editor.models_list.item(index)
        if item.data(Qt.ItemDataRole.UserRole) in {"2022-mentorship", "silver-bullet"}:
            item.setCheckState(Qt.CheckState.Checked)

    assert run.playbook_candidate("2022-mentorship") is not None
    silver_candidate = run.playbook_candidate("silver-bullet")
    assert silver_candidate is not None
    assert len([item for item in run.setup_candidates if item.source_type == "Playbook"]) == 2

    editor.if_input.setText("PDH trades before the setup window")
    editor.then_input.setText("Return to analysis and reassess the primary draw")
    editor.add_button.click()
    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True) is True
    live = shell.runtime.live_watch_widget
    assert (silver_candidate.id, "fvg-direction") in live.candidate_entry_checkboxes
    assert (silver_candidate.id, "qualifying-fvg") in live.candidate_watch_point_combos
    assert runner.session.watch_points[0].id in live.watch_point_combos
    assert set(live.run_gate_combos) == {"trading-day-permitted", "daily-capacity-available"}


def test_occurred_watch_point_updates_criterion_but_global_gates_still_block() -> None:
    get_app()
    _plan, shell = build_shell_with_plan()
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None
    candidate = select_silver_bullet(shell)
    shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    live = shell.runtime.live_watch_widget

    live.candidate_watch_point_combos[(candidate.id, "qualifying-fvg")].setCurrentText(
        WatchPointState.OCCURRED.value
    )

    assert candidate.entry_condition_states["fvg-direction"] is True
    result = run.candidate_authorization(candidate.id)
    assert result.status is AuthorizationStatus.BLOCKED
    assert any("Trading day permitted" in item for item in result.blockers)


def test_candidate_becomes_authorized_only_after_setup_and_plan_gates_clear() -> None:
    get_app()
    _plan, shell = build_shell_with_plan()
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None
    candidate = select_silver_bullet(shell)
    shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    live = shell.runtime.live_watch_widget

    live.run_gate_combos["trading-day-permitted"].setCurrentText(AuthorizationGateState.CLEAR.value)
    live.run_gate_combos["daily-capacity-available"].setCurrentText(AuthorizationGateState.CLEAR.value)
    live.candidate_gate_combos[(candidate.id, "candidate-risk-within-plan")].setCurrentText(
        AuthorizationGateState.CLEAR.value
    )
    for watch_id in ("qualifying-fvg", "delivery-distance", "retracement-entry"):
        live = shell.runtime.live_watch_widget
        live.candidate_watch_point_combos[(candidate.id, watch_id)].setCurrentText(
            WatchPointState.OCCURRED.value
        )

    result = run.candidate_authorization(candidate.id)
    assert result.status is AuthorizationStatus.AUTHORIZED
    assert result.blockers == []
    assert "all Trade Plan gates are clear" in result.detail


def test_blocked_plan_gate_overrides_complete_setup() -> None:
    get_app()
    _plan, shell = build_shell_with_plan()
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None
    candidate = select_silver_bullet(shell)
    for criterion in ("fvg-direction", "delivery-distance", "fvg-retracement"):
        run.set_candidate_entry_condition(candidate.id, criterion, True)
    run.set_authorization_gate("trading-day-permitted", AuthorizationGateState.BLOCKED)
    run.set_authorization_gate("daily-capacity-available", AuthorizationGateState.CLEAR)
    run.set_candidate_authorization_gate(candidate.id, "candidate-risk-within-plan", AuthorizationGateState.CLEAR)

    result = run.candidate_authorization(candidate.id)
    assert result.status is AuthorizationStatus.BLOCKED
    assert any("Trading day permitted: blocked" == item for item in result.blockers)


def test_run_keeps_snapshot_when_current_definition_changes() -> None:
    plan = build_default_trade_plan()
    original = plan.playbook_by_id("silver-bullet")
    assert original is not None
    run = TradingRun("day-1", "Trading Run 1", "process-1")
    run.sync_playbook_candidates([original.to_snapshot()])
    candidate = run.playbook_candidate(original.id)
    assert candidate is not None
    changed_payload = original.to_snapshot()
    changed_payload["risk_summary"] = "A later revision changed this rule."
    changed_payload["revision"] = "Alpha 0.3"
    changed = PlaybookDefinition.from_snapshot(changed_payload)
    assert changed.revision == "Alpha 0.3"
    assert candidate.source_revision == "Alpha 0.2"
    assert "79%" in candidate.definition_snapshot["risk_summary"]
