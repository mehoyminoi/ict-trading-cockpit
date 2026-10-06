from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import RunEnvironment, TradingRun
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_adds_run_provenance_columns(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(trading_session_run)").fetchall()
    }
    version = connection.execute("PRAGMA user_version").fetchone()[0]

    assert version == CURRENT_SCHEMA_VERSION
    assert "run_environment" in columns
    assert "trade_plan_revision" in columns
    connection.close()


def test_run_environment_and_trade_plan_revision_round_trip(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    day_repository = TradingDayRepository(connection)
    process_repository = TradingDaySessionRepository(connection)
    run_repository = TradingSessionRunRepository(connection)

    blueprint = build_default_process_blueprint()
    day = TradingDay(futures_day_label="2026-09-15")
    process_session = TradingDaySession(
        blueprint_revision=blueprint.revision,
        mode_ids=[mode.id for mode in blueprint.modes],
        current_mode_id="tda",
    )
    process_repository.save(process_session)
    run = TradingRun(
        day.id,
        "Trading Run 1",
        process_session.id,
        environment=RunEnvironment.HISTORICAL_BACKTEST,
        trade_plan_revision="Alpha 0.2",
        market_time_context={
            "timezone": "America/New_York",
            "source": "Historical Reference",
            "captured_at": "2026-09-15T10:15:00-04:00",
            "session": "NYAM",
            "daily_quarter": "Q3",
            "session_quarter": "Q3",
        },
    )
    run.add_observation(
        "Historical observation",
        market_time_context=run.market_time_context,
    )
    day.activate_trading_run(run)
    day_repository.save(day)
    run_repository.save(run)

    restored = run_repository.get_by_id(run.id)

    assert restored is not None
    assert restored.environment is RunEnvironment.HISTORICAL_BACKTEST
    assert restored.trade_plan_revision == "Alpha 0.2"
    assert restored.market_time_context["timezone"] == "America/New_York"
    assert restored.market_time_context["session"] == "NYAM"
    assert restored.market_time_context["source"] == "Historical Reference"
    assert restored.evidence[0].market_time_context["captured_at"] == (
        "2026-09-15T10:15:00-04:00"
    )
    connection.close()


def test_replay_uses_same_process_blueprint_and_runtime_components_as_live() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    live_shell = TradingDayShellWidget(
        blueprint,
        run_environment=RunEnvironment.LIVE,
        trade_plan_revision="Plan R1",
    )
    replay_shell = TradingDayShellWidget(
        blueprint,
        run_environment=RunEnvironment.REPLAY,
        trade_plan_revision="Plan R1",
    )

    assert live_shell.start_trading_run() is True
    assert replay_shell.start_trading_run() is True
    assert live_shell.runtime.session.mode_ids == replay_shell.runtime.session.mode_ids
    assert live_shell.runtime.session.mode_ids == [
        "tda",
        "live-watch",
        "post-market",
    ]
    assert live_shell.runtime.tda_station_runner_widget.__class__ is (
        replay_shell.runtime.tda_station_runner_widget.__class__
    )
    assert live_shell.runtime.live_watch_widget.__class__ is (
        replay_shell.runtime.live_watch_widget.__class__
    )
    assert live_shell.runtime.post_market_review_widget.__class__ is (
        replay_shell.runtime.post_market_review_widget.__class__
    )
    assert live_shell.active_trading_run.environment is RunEnvironment.LIVE
    assert replay_shell.active_trading_run.environment is RunEnvironment.REPLAY
    assert "Replay" in replay_shell.resume_context_label.text()


def test_trade_plan_widget_stamps_live_run_with_active_plan_revision() -> None:
    get_app()
    trade_plan = build_default_trade_plan()
    widget = TradePlanWidget(trade_plan)
    shell = widget.trading_day_shell_widget

    assert shell.start_trading_run() is True
    run = shell.active_trading_run

    assert run is not None
    assert run.environment is RunEnvironment.LIVE
    assert run.trade_plan_revision == trade_plan.revision
