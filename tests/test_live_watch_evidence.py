from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import (
    RunEvidenceKind,
    ThesisState,
    TradingRun,
    WatchPointState,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget
from ict_cockpit.trade_plan import EntryCriterionDefinition, LiveWatchPolicyDefinition


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def build_process_session() -> TradingDaySession:
    return TradingDaySession(
        blueprint_revision="Alpha 0.2",
        mode_ids=["tda", "live-watch", "post-market"],
        current_mode_id="tda",
    )


def build_test_live_watch_policy() -> LiveWatchPolicyDefinition:
    return LiveWatchPolicyDefinition(
        entry_criteria=(
            EntryCriterionDefinition("criterion-a", "Condition A"),
            EntryCriterionDefinition("criterion-b", "Condition B"),
            EntryCriterionDefinition("criterion-c", "Condition C"),
        ),
        required_entry_count=2,
        risk_summary="Test risk rule inherited from Trade Plan.",
    )


def test_schema_v16_preserves_live_watch_runtime_columns(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    run_columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(trading_session_run)").fetchall()
    }
    tda_columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(tda_station_session)").fetchall()
    }

    assert CURRENT_SCHEMA_VERSION == 16
    assert "current_thesis_state" in run_columns
    assert "evidence_json" in run_columns
    assert "entry_condition_states_json" in run_columns
    assert "watch_point_states_json" in run_columns
    assert "watch_points_json" in tda_columns
    connection.close()


def test_trading_run_records_observation_and_thesis_crossroads() -> None:
    run = TradingRun("day-1", "Trading Run 1", "process-1")

    observation = run.add_observation("London high swept before NYAM expansion")
    thesis = run.record_thesis_state(
        ThesisState.WEAKENED,
        "Primary draw remains, but displacement failed to hold",
    )

    assert observation.kind is RunEvidenceKind.OBSERVATION
    assert thesis.kind is RunEvidenceKind.THESIS_STATE
    assert run.current_thesis_state is ThesisState.WEAKENED
    assert len(run.evidence) == 2


def test_run_evidence_readiness_and_watch_state_round_trip(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    day_repository = TradingDayRepository(connection)
    process_repository = TradingDaySessionRepository(connection)
    run_repository = TradingSessionRunRepository(connection)

    day = TradingDay(futures_day_label="2026-10-06")
    process_session = build_process_session()
    process_repository.save(process_session)
    run = TradingRun(day.id, "Trading Run 1", process_session.id)
    run.add_observation("Price respected the morning FVG")
    run.record_thesis_state(ThesisState.SUPPORTED, "Draw remains intact")
    run.set_entry_condition("criterion-a", True)
    run.set_entry_condition("criterion-b", False)
    run.set_watch_point_state("watch-1", WatchPointState.OCCURRED)
    day.activate_trading_run(run)
    day_repository.save(day)
    run_repository.save(run)

    restored = run_repository.get_by_id(run.id)

    assert restored is not None
    assert restored.current_thesis_state is ThesisState.SUPPORTED
    assert [item.kind for item in restored.evidence] == [
        RunEvidenceKind.OBSERVATION,
        RunEvidenceKind.THESIS_STATE,
    ]
    assert restored.entry_condition_states == {
        "criterion-a": True,
        "criterion-b": False,
    }
    assert restored.watch_point_states == {
        "watch-1": WatchPointState.OCCURRED,
    }
    connection.close()


def test_live_watch_capture_updates_active_trading_run() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True) is True
    live_watch = shell.runtime.live_watch_widget

    live_watch.observation_input.setText("NYAM displacement confirmed the draw")
    live_watch.capture_observation_button.click()
    live_watch.thesis_note_input.setText("Structure still supports the morning thesis")
    live_watch.thesis_buttons[ThesisState.SUPPORTED].click()

    assert len(run.evidence) == 2
    assert run.current_thesis_state is ThesisState.SUPPORTED
    assert live_watch.observation_input.text() == ""
    assert "Supported" in live_watch.thesis_state_label.text()
    assert live_watch.evidence_list.count() == 2
    assert live_watch.evidence_list.isHidden() is True


def test_unconfigured_trade_plan_does_not_invent_entry_threshold() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    live_watch = shell.runtime.live_watch_widget

    assert live_watch.entry_checkboxes == {}
    assert live_watch.readiness_count_label.text() == "Entry criteria: Not configured"
    assert live_watch.readiness_required_label.text() == "Required for entry: Not configured"


def test_trade_plan_policy_drives_live_watch_readiness_and_run_state() -> None:
    get_app()
    policy = build_test_live_watch_policy()
    shell = TradingDayShellWidget(
        build_default_process_blueprint(),
        live_watch_policy=policy,
    )
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None
    shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    live_watch = shell.runtime.live_watch_widget

    assert live_watch.readiness_count_label.text() == "0 / 3 criteria currently met"
    assert live_watch.readiness_required_label.text() == "Required for entry: 2 / 3"
    assert "Test risk rule" in live_watch.risk_status_label.text()

    live_watch.entry_checkboxes["criterion-a"].setChecked(True)
    live_watch.entry_checkboxes["criterion-b"].setChecked(True)

    assert run.entry_condition_states == {
        "criterion-a": True,
        "criterion-b": True,
    }
    assert live_watch.readiness_count_label.text() == "2 / 3 criteria currently met"
    assert "threshold satisfied" in live_watch.readiness_status_label.text().lower()


def test_tda_watch_point_is_authored_then_tracked_in_live_watch() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    runtime = shell.runtime
    runner = runtime.tda_station_runner_widget

    runner.select_station("tda-thesis")
    editor = runtime.tda_watch_point_widget
    assert editor.isHidden() is False

    editor.if_input.setText("London high is swept")
    editor.then_input.setText("Watch for bearish displacement toward PDL")
    editor.add_button.click()

    assert len(runner.session.watch_points) == 1
    watch_point = runner.session.watch_points[0]
    assert watch_point.if_condition == "London high is swept"
    assert watch_point.then_action == "Watch for bearish displacement toward PDL"

    runtime.apply_transition("finish-tda", override_incomplete=True)
    live_watch = runtime.live_watch_widget

    assert watch_point.id in live_watch.watch_point_combos
    combo = live_watch.watch_point_combos[watch_point.id]
    assert combo.currentText() == WatchPointState.WAITING.value

    combo.setCurrentText(WatchPointState.OCCURRED.value)

    run = shell.active_trading_run
    assert run is not None
    assert run.watch_point_states[watch_point.id] is WatchPointState.OCCURRED
    assert runner.session.watch_points[0].then_action == (
        "Watch for bearish displacement toward PDL"
    )


def test_live_watch_carries_forward_tda_synthesis() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    runner = shell.runtime.tda_station_runner_widget

    runner.session.observation_for("tda-primary-draw").observation = "Previous Day Low"
    runner.session.observation_for("tda-secondary-draw").observation = "London high if primary fails"
    runner.session.observation_for("tda-thesis").observation = (
        "Expect NYAM expansion lower after a buy-side liquidity sweep."
    )

    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True) is True
    live_watch = shell.runtime.live_watch_widget

    rendered = "\n".join(
        live_watch.watch_points_list.item(index).text()
        for index in range(live_watch.watch_points_list.count())
    )

    assert "Primary Draw" in rendered
    assert "Previous Day Low" in rendered
    assert "Premarket Thesis" in rendered
    assert "NYAM expansion lower" in rendered


def test_restored_active_run_rehydrates_live_watch_state() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    policy = build_test_live_watch_policy()
    shell = TradingDayShellWidget(blueprint, live_watch_policy=policy)
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    runner = shell.runtime.tda_station_runner_widget
    watch_point = runner.session.add_watch_point(
        "Price trades through London high",
        "Wait for displacement before considering entry",
    )
    shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    run.add_observation("Liquidity sweep completed")
    run.record_thesis_state(ThesisState.UNCERTAIN, "Waiting for displacement")
    run.set_entry_condition("criterion-a", True)
    run.set_watch_point_state(watch_point.id, WatchPointState.OCCURRED)

    restored_shell = TradingDayShellWidget(blueprint, live_watch_policy=policy)
    restored_shell.load_state(
        shell.trading_day,
        shell.trading_runs,
        process_session=shell.runtime.session,
        tda_session=runner.session,
    )

    restored_live_watch = restored_shell.runtime.live_watch_widget
    assert restored_shell.runtime.session.current_mode_id == "live-watch"
    assert "Uncertain" in restored_live_watch.thesis_state_label.text()
    assert restored_live_watch.evidence_list.count() == 2
    assert restored_live_watch.entry_checkboxes["criterion-a"].isChecked() is True
    assert restored_live_watch.watch_point_combos[watch_point.id].currentText() == (
        WatchPointState.OCCURRED.value
    )
