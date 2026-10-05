import pytest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.tda_station_session import (
    TDAStationObservation,
    TDAStationSession,
)
from ict_cockpit.analysis.trading_day import TradingDay, TradingDayLifecycleStatus
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import (
    TradingSessionRun,
    TradingSessionRunStatus,
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


def test_schema_v12_creates_trading_day_and_session_run_tables(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    names = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    assert CURRENT_SCHEMA_VERSION == 12
    assert "trading_day" in names
    assert "trading_session_run" in names
    connection.close()


def test_trading_day_allows_only_one_active_session_run() -> None:
    day = TradingDay(futures_day_label="2026-10-06")
    first = TradingSessionRun(day.id, "NYAM", "process-1")
    second = TradingSessionRun(day.id, "NYPM", "process-2")

    day.activate_session_run(first)

    with pytest.raises(ValueError, match="already has an active session run"):
        day.activate_session_run(second)


def test_concluding_session_run_does_not_complete_trading_day() -> None:
    day = TradingDay(futures_day_label="2026-10-06")
    run = TradingSessionRun(day.id, "NYAM", "process-1")
    day.activate_session_run(run)

    day.conclude_session_run(run, "No Trade — Process Followed")

    assert run.status is TradingSessionRunStatus.CONCLUDED
    assert run.outcome == "No Trade — Process Followed"
    assert day.status is TradingDayLifecycleStatus.ACTIVE
    assert day.active_session_run_id == ""


def test_new_session_run_can_start_after_prior_run_concludes() -> None:
    day = TradingDay(futures_day_label="2026-10-06")
    nyam = TradingSessionRun(day.id, "NYAM", "process-1")
    nypm = TradingSessionRun(day.id, "NYPM", "process-2")

    day.activate_session_run(nyam)
    day.conclude_session_run(nyam)
    day.activate_session_run(nypm)

    assert nyam.status is TradingSessionRunStatus.CONCLUDED
    assert nypm.status is TradingSessionRunStatus.ACTIVE
    assert day.active_session_run_id == nypm.id


def test_trading_day_cannot_complete_with_active_session_run() -> None:
    day = TradingDay()
    run = TradingSessionRun(day.id, "Asia", "process-1")
    day.activate_session_run(run)

    with pytest.raises(ValueError, match="session run is active"):
        day.complete()

    day.conclude_session_run(run)
    day.complete()
    assert day.status is TradingDayLifecycleStatus.COMPLETE


def test_day_and_session_runs_round_trip_through_repositories(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    day_repository = TradingDayRepository(connection)
    run_repository = TradingSessionRunRepository(connection)
    process_repository = TradingDaySessionRepository(connection)

    day = TradingDay(futures_day_label="2026-10-06")
    process_session = build_process_session()
    process_repository.save(process_session)
    run = TradingSessionRun(
        trading_day_id=day.id,
        session_name="NYAM",
        process_session_id=process_session.id,
        tda_station_session_id="tda-session-1",
    )
    day.activate_session_run(run)

    day_repository.save(day)
    run_repository.save(run)

    restored_day = day_repository.get_latest_active()
    restored_run = run_repository.get_by_id(run.id)

    assert restored_day is not None
    assert restored_day.id == day.id
    assert restored_day.active_session_run_id == run.id
    assert restored_run is not None
    assert restored_run.session_name == "NYAM"
    assert restored_run.process_session_id == process_session.id
    assert restored_run.tda_station_session_id == "tda-session-1"
    connection.close()


def test_repository_keeps_multiple_runs_for_same_trading_day(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    day_repository = TradingDayRepository(connection)
    run_repository = TradingSessionRunRepository(connection)
    process_repository = TradingDaySessionRepository(connection)

    day = TradingDay(futures_day_label="2026-10-06")
    day_repository.save(day)

    created = []
    for session_name in ("NYAM", "NYPM"):
        process_session = build_process_session()
        process_repository.save(process_session)
        run = TradingSessionRun(day.id, session_name, process_session.id)
        day.activate_session_run(run)
        run_repository.save(run)
        day.conclude_session_run(run)
        run_repository.save(run)
        created.append(run)

    day_repository.save(day)
    restored = run_repository.get_for_day(day.id)

    assert [item.id for item in restored] == [item.id for item in created]
    assert [item.session_name for item in restored] == ["NYAM", "NYPM"]
    assert all(item.status is TradingSessionRunStatus.CONCLUDED for item in restored)
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


def test_shell_starts_session_run_without_completing_day() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())

    assert shell.start_session_run("NYAM") is True
    assert shell.active_session_run is not None
    assert shell.active_session_run.session_name == "NYAM"
    assert shell.trading_day.active_session_run_id == shell.active_session_run.id
    assert shell.complete_day_button.isEnabled() is False
    assert shell.runtime_frame.isVisible() is False or shell.runtime_frame.isHidden() is False


def test_shell_process_completion_concludes_run_but_leaves_day_active() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_session_run("NYAM")
    run = shell.active_session_run
    assert run is not None

    shell.runtime.apply_transition("tda-stand-down")
    shell.runtime.apply_transition("complete-day")

    assert run.status is TradingSessionRunStatus.CONCLUDED
    assert shell.active_session_run is None
    assert shell.trading_day.status is TradingDayLifecycleStatus.ACTIVE
    assert shell.start_session_button.isEnabled() is True
    assert shell.complete_day_button.isEnabled() is True


def test_shell_can_run_nyam_then_nypm_before_completing_day() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())

    shell.start_session_run("NYAM")
    shell.runtime.apply_transition("tda-stand-down")
    shell.runtime.apply_transition("complete-day")
    shell.start_session_run("NYPM")

    assert [run.session_name for run in shell.session_runs] == ["NYAM", "NYPM"]
    assert shell.active_session_run is shell.session_runs[-1]
    assert shell.trading_day.status is TradingDayLifecycleStatus.ACTIVE
