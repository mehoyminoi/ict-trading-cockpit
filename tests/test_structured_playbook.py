from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import TradingRun, WatchPointState
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


def test_default_trade_plan_exposes_declarative_playbooks() -> None:
    plan = build_default_trade_plan()

    assert plan.revision == "Alpha 0.4"
    assert [playbook.id for playbook in plan.playbooks] == [
        "2022-mentorship",
        "silver-bullet",
    ]

    silver_bullet = plan.playbook_by_id("silver-bullet")
    assert silver_bullet is not None
    assert silver_bullet.revision == "Alpha 0.2"
    assert silver_bullet.required_entry_count == 3
    assert len(silver_bullet.entry_criteria) == 3
    assert len(silver_bullet.watch_point_templates) == 3
    assert silver_bullet.watch_point_templates[0].satisfies_criterion_ids == (
        "fvg-direction",
    )
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
    assert snapshot["watch_point_templates"][0]["satisfies_criterion_ids"] == [
        "fvg-direction"
    ]


def test_schema_v20_adds_setup_candidate_storage(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(trading_session_run)").fetchall()
    }
    version = connection.execute("PRAGMA user_version").fetchone()[0]

    assert version == CURRENT_SCHEMA_VERSION
    assert "setup_candidates_json" in columns
    # v19 provenance remains readable for migration/backward compatibility.
    assert "selected_playbook_id" in columns
    assert "playbook_snapshot_json" in columns
    connection.close()


def test_multiple_setup_candidates_round_trip_with_trading_run(tmp_path) -> None:
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
    )
    run.ensure_day_specific_candidate()
    run.sync_playbook_candidates([mentorship.to_snapshot(), silver.to_snapshot()])
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
    assert restored.playbook_candidate("silver-bullet") is not None
    assert restored.playbook_candidate("silver-bullet").source_revision == "Alpha 0.2"
    connection.close()


def test_tda_models_in_play_are_multi_select_and_live_readiness_is_per_candidate() -> None:
    get_app()
    plan = build_default_trade_plan()
    shell = TradingDayShellWidget(
        plan.process_blueprint,
        playbooks=plan.playbooks,
        trade_plan_revision=plan.revision,
    )
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
    assert len(runner.session.watch_points) == 1

    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True) is True
    live = shell.runtime.live_watch_widget

    assert (silver_candidate.id, "fvg-direction") in live.candidate_entry_checkboxes
    assert (silver_candidate.id, "qualifying-fvg") in live.candidate_watch_point_combos
    assert runner.session.watch_points[0].id in live.watch_point_combos


def test_occurred_playbook_watch_point_explicitly_satisfies_linked_criterion() -> None:
    get_app()
    plan = build_default_trade_plan()
    shell = TradingDayShellWidget(
        plan.process_blueprint,
        playbooks=plan.playbooks,
        trade_plan_revision=plan.revision,
    )
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    runner = shell.runtime.tda_station_runner_widget
    runner.select_station("tda-thesis")
    editor = shell.runtime.tda_watch_point_widget
    for index in range(editor.models_list.count()):
        item = editor.models_list.item(index)
        if item.data(Qt.ItemDataRole.UserRole) == "silver-bullet":
            item.setCheckState(Qt.CheckState.Checked)
            break

    candidate = run.playbook_candidate("silver-bullet")
    assert candidate is not None
    shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    live = shell.runtime.live_watch_widget
    combo = live.candidate_watch_point_combos[(candidate.id, "qualifying-fvg")]

    combo.setCurrentText(WatchPointState.OCCURRED.value)

    assert candidate.watch_point_states["qualifying-fvg"] is WatchPointState.OCCURRED
    assert candidate.entry_condition_states["fvg-direction"] is True
    assert live.candidate_entry_checkboxes[(candidate.id, "fvg-direction")].isChecked() is True


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
