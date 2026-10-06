import pytest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.tda_station_session import (
    TDAStationObservation,
    TDAStationSession,
)
from ict_cockpit.analysis.trading_day import TradingDay, TradingDayLifecycleStatus
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import (
    TradingRun,
    TradingRunStatus,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.tda_station_session_repository import TDAStationSessionRepository
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


def test_schema_preserves_trading_day_and_run_storage(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    names = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    version = connection.execute("PRAGMA user_version").fetchone()[0]

    assert version == CURRENT_SCHEMA_VERSION
    assert "trading_day" in names
    assert "trading_session_run" in names
    connection.close()


def test_trading_day_allows_only_one_active_trading_run() -> None:
    day = TradingDay(futures_day_label="2026-10-06")
    first = TradingRun(day.id, "Trading Run 1", "process-1")
    second = TradingRun(day.id, "Trading Run 2", "process-2")

    day.activate_trading_run(first)

    with pytest.raises(ValueError, match="already has an active trading run"):
        day.activate_trading_run(second)


def test_concluding_trading_run_does_not_complete_trading_day() -> None:
    day = TradingDay(futures_day_label="2026-10-06")
    run = TradingRun(day.id, "Trading Run 1", "process-1")
    day.activate_trading_run(run)

    day.conclude_trading_run(run, "No Trade — Process Followed")

    assert run.status is TradingRunStatus.CONCLUDED
    assert run.outcome == "No Trade — Process Followed"
    assert day.status is TradingDayLifecycleStatus.ACTIVE
    assert day.active_trading_run_id == ""


def test_new_trading_run_can_start_after_prior_run_concludes() -> None:
    day = TradingDay(futures_day_label="2026-10-06")
    morning = TradingRun(day.id, "Trading Run 1", "process-1")
    later = TradingRun(day.id, "Trading Run 2", "process-2")

    day.activate_trading_run(morning)
    day.conclude_trading_run(morning)
    day.activate_trading_run(later)

    assert morning.status is TradingRunStatus.CONCLUDED
    assert later.status is TradingRunStatus.ACTIVE
    assert day.active_trading_run_id == later.id


def test_trading_day_cannot_complete_with_active_trading_run() -> None:
    day = TradingDay()
    run = TradingRun(day.id, "Trading Run 1", "process-1")
    day.activate_trading_run(run)

    with pytest.raises(ValueError, match="trading run is active"):
        day.complete()

    day.conclude_trading_run(run)
    day.complete()
    assert day.status is TradingDayLifecycleStatus.COMPLETE


def test_day_and_trading_runs_round_trip_through_repositories(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    day_repository = TradingDayRepository(connection)
    run_repository = TradingSessionRunRepository(connection)
    process_repository = TradingDaySessionRepository(connection)

    day = TradingDay(futures_day_label="2026-10-06")
    process_session = build_process_session()
    process_repository.save(process_session)
    run = TradingRun(
        trading_day_id=day.id,
        session_name="Trading Run 1",
        process_session_id=process_session.id,
        tda_station_session_id="tda-session-1",
    )
    day.activate_trading_run(run)

    day_repository.save(day)
    run_repository.save(run)

    restored_day = day_repository.get_latest_active()
    restored_run = run_repository.get_by_id(run.id)

    assert restored_day is not None
    assert restored_day.id == day.id
    assert restored_day.active_trading_run_id == run.id
    assert restored_run is not None
    assert restored_run.run_label == "Trading Run 1"
    assert restored_run.process_session_id == process_session.id
    assert restored_run.tda_station_session_id == "tda-session-1"
    connection.close()


def test_repository_keeps_multiple_trading_runs_for_same_day(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    day_repository = TradingDayRepository(connection)
    run_repository = TradingSessionRunRepository(connection)
    process_repository = TradingDaySessionRepository(connection)

    day = TradingDay(futures_day_label="2026-10-06")
    day_repository.save(day)

    created = []
    for run_number in (1, 2):
        process_session = build_process_session()
        process_repository.save(process_session)
        run = TradingRun(day.id, f"Trading Run {run_number}", process_session.id)
        day.activate_trading_run(run)
        run_repository.save(run)
        day.conclude_trading_run(run)
        run_repository.save(run)
        created.append(run)

    day_repository.save(day)
    restored = run_repository.get_for_day(day.id)

    assert [item.id for item in restored] == [item.id for item in created]
    assert [item.run_label for item in restored] == ["Trading Run 1", "Trading Run 2"]
    assert all(item.status is TradingRunStatus.CONCLUDED for item in restored)
    connection.close()


def test_exact_process_and_tda_sessions_can_be_restored_by_id(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    process_repository = TradingDaySessionRepository(connection)
    tda_repository = TDAStationSessionRepository(connection)

    older_process = build_process_session()
    wanted_process = build_process_session()
    process_repository.save(older_process)
    process_repository.save(wanted_process)

    tda = TDAStationSession(
        blueprint_revision="Alpha 0.2",
        current_station_id="tda-one",
        observations=[TDAStationObservation("tda-one", "saved state", True)],
    )
    tda_repository.save(tda)

    assert process_repository.get_by_id(wanted_process.id).id == wanted_process.id
    assert tda_repository.get_by_id(tda.id).observation_for("tda-one").observation == "saved state"
    connection.close()


def test_shell_starts_neutral_trading_run_without_market_session_choice() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())

    assert shell.start_trading_run() is True
    assert shell.active_trading_run is not None
    assert shell.active_trading_run.run_label == "Trading Run 1"
    assert shell.trading_day.active_trading_run_id == shell.active_trading_run.id
    assert shell.complete_day_button.isEnabled() is False
    assert shell.runtime_scroll.widget() is shell.runtime_frame


def test_shell_process_completion_concludes_run_but_leaves_day_active() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    shell.runtime.apply_transition("tda-stand-down")
    shell.runtime.apply_transition("complete-day")

    assert run.status is TradingRunStatus.CONCLUDED
    assert shell.active_trading_run is None
    assert shell.trading_day.status is TradingDayLifecycleStatus.ACTIVE
    assert shell.start_run_button.isEnabled() is True
    assert shell.complete_day_button.isEnabled() is True


def test_shell_can_use_one_run_across_market_sessions_and_optionally_start_another() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())

    shell.start_trading_run()
    first = shell.active_trading_run
    assert first is not None
    assert first.run_label == "Trading Run 1"

    shell.runtime.apply_transition("tda-stand-down")
    shell.runtime.apply_transition("complete-day")
    shell.start_trading_run()

    assert [run.run_label for run in shell.trading_runs] == [
        "Trading Run 1",
        "Trading Run 2",
    ]
    assert shell.active_trading_run is shell.trading_runs[-1]
    assert shell.trading_day.status is TradingDayLifecycleStatus.ACTIVE


def test_completed_day_starts_fresh_day_directly_in_trading_run_one() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    old_day_id = shell.trading_day.id

    assert shell.complete_trading_day() is True
    assert shell.trading_day.status is TradingDayLifecycleStatus.COMPLETE
    assert shell.start_new_day_button.isEnabled() is True

    shell.start_new_trading_day()

    assert shell.trading_day.id != old_day_id
    assert shell.trading_day.status is TradingDayLifecycleStatus.ACTIVE
    assert len(shell.trading_runs) == 1
    assert shell.active_trading_run is shell.trading_runs[0]
    assert shell.active_trading_run.run_label == "Trading Run 1"
    assert shell.runtime.session.current_mode_id == "tda"


def test_active_runtime_uses_compact_scrollable_viewport() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())

    shell.start_trading_run()

    assert shell.runtime_scroll.widgetResizable() is True
    assert shell.runtime_scroll.widget() is shell.runtime_frame
    assert shell.run_history.maximumHeight() <= 72
    assert shell.run_history.isHidden() is True
