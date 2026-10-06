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

    assert plan.revision == "Alpha 0.3"
    assert [playbook.id for playbook in plan.playbooks] == [
        "2022-mentorship",
        "silver-bullet",
    ]

    silver_bullet = plan.playbook_by_id("silver-bullet")
    assert silver_bullet is not None
    assert silver_bullet.required_entry_count == 3
    assert len(silver_bullet.entry_criteria) == 3
    assert len(silver_bullet.watch_point_templates) == 3
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


def test_schema_v19_adds_playbook_provenance_columns(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(trading_session_run)").fetchall()
    }
    version = connection.execute("PRAGMA user_version").fetchone()[0]

    assert version == CURRENT_SCHEMA_VERSION
    assert "selected_playbook_id" in columns
    assert "selected_playbook_revision" in columns
    assert "playbook_snapshot_json" in columns
    connection.close()


def test_playbook_snapshot_round_trips_with_trading_run(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    day_repository = TradingDayRepository(connection)
    process_repository = TradingDaySessionRepository(connection)
    run_repository = TradingSessionRunRepository(connection)

    plan = build_default_trade_plan()
    playbook = plan.playbook_by_id("silver-bullet")
    assert playbook is not None

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
    run.select_playbook(playbook.id, playbook.revision, playbook.to_snapshot())
    day.activate_trading_run(run)
    day_repository.save(day)
    run_repository.save(run)

    restored = run_repository.get_by_id(run.id)

    assert restored is not None
    assert restored.selected_playbook_id == "silver-bullet"
    assert restored.selected_playbook_revision == playbook.revision
    assert PlaybookDefinition.from_snapshot(restored.playbook_snapshot) == playbook
    connection.close()


def test_tda_playbook_selection_inherits_watch_points_and_live_readiness() -> None:
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

    silver_index = editor.playbook_combo.findData("silver-bullet")
    assert silver_index >= 0
    editor.playbook_combo.setCurrentIndex(silver_index)

    assert run.selected_playbook_id == "silver-bullet"
    assert run.selected_playbook_revision == "Alpha 0.1"
    assert editor.inherited_list.count() == 3
    assert "killzone" in editor.inherited_list.item(0).text().lower()

    editor.if_input.setText("PDH trades before the setup window")
    editor.then_input.setText("Return to analysis and reassess the primary draw")
    editor.add_button.click()
    assert len(runner.session.watch_points) == 1

    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True) is True
    live = shell.runtime.live_watch_widget

    assert len(live.entry_checkboxes) == 3
    assert live.readiness_required_label.text() == "Required for entry: 3 / 3"
    assert len(live.watch_point_combos) == 4

    inherited_id = "playbook:silver-bullet:qualifying-fvg"
    assert inherited_id in live.watch_point_combos
    live.watch_point_combos[inherited_id].setCurrentText(WatchPointState.OCCURRED.value)
    assert run.watch_point_states[inherited_id] is WatchPointState.OCCURRED


def test_run_keeps_snapshot_when_current_definition_changes() -> None:
    plan = build_default_trade_plan()
    original = plan.playbook_by_id("silver-bullet")
    assert original is not None

    run = TradingRun("day-1", "Trading Run 1", "process-1")
    run.select_playbook(original.id, original.revision, original.to_snapshot())

    changed_payload = original.to_snapshot()
    changed_payload["risk_summary"] = "A later revision changed this rule."
    changed_payload["revision"] = "Alpha 0.2"
    changed = PlaybookDefinition.from_snapshot(changed_payload)

    assert changed.revision == "Alpha 0.2"
    assert run.selected_playbook_revision == "Alpha 0.1"
    assert "79%" in run.playbook_snapshot["risk_summary"]
