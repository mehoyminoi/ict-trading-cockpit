import pytest

from ict_cockpit.analysis.trading_day import TradingDay, TradingDayLifecycleStatus
from ict_cockpit.analysis.trading_session_run import (
    TradingSessionRun,
    TradingSessionRunStatus,
)
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository


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
