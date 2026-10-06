from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import (
    RunEvidenceKind,
    ThesisState,
    TradingRun,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


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


def test_schema_v14_preserves_run_evidence_columns(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(trading_session_run)").fetchall()
    }

    assert CURRENT_SCHEMA_VERSION == 14
    assert "current_thesis_state" in columns
    assert "evidence_json" in columns
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


def test_run_evidence_round_trips_through_repository(tmp_path) -> None:
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
    assert restored.evidence[0].note == "Price respected the morning FVG"
    assert restored.evidence[1].note == "Draw remains intact"
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


def test_restored_active_run_rehydrates_live_watch_evidence() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    shell = TradingDayShellWidget(blueprint)
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    run.add_observation("Liquidity sweep completed")
    run.record_thesis_state(ThesisState.UNCERTAIN, "Waiting for displacement")

    restored_shell = TradingDayShellWidget(blueprint)
    restored_shell.load_state(
        shell.trading_day,
        shell.trading_runs,
        process_session=shell.runtime.session,
        tda_session=shell.runtime.tda_station_runner_widget.session,
    )

    assert restored_shell.runtime.session.current_mode_id == "live-watch"
    assert "Uncertain" in restored_shell.runtime.live_watch_widget.thesis_state_label.text()
    assert restored_shell.runtime.live_watch_widget.evidence_list.count() == 2
