from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.trading_day_session_repository import (
    TradingDaySessionRepository,
)
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.trading_day_runtime_widget import TradingDayRuntimeWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_creates_trading_day_session_table(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    table = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='trading_day_session'"
    ).fetchone()

    assert table is not None
    connection.close()


def test_trading_day_session_repository_round_trip(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = TradingDaySessionRepository(connection)

    session = TradingDaySession(
        blueprint_revision="Alpha 0.2",
        mode_ids=["tda", "live-watch", "post-market"],
        current_mode_id="live-watch",
        completed_mode_ids=["tda"],
    )
    repository.save(session)

    restored = repository.get_latest()

    assert restored is not None
    assert restored.id == session.id
    assert restored.current_mode_id == "live-watch"
    assert restored.completed_mode_ids == ["tda"]
    assert restored.mode_ids == ["tda", "live-watch", "post-market"]
    connection.close()


def test_trading_day_session_moves_forward_and_back() -> None:
    session = TradingDaySession(
        blueprint_revision="Alpha 0.2",
        mode_ids=["tda", "live-watch", "post-market"],
        current_mode_id="tda",
    )

    assert session.move_next() is True
    assert session.current_mode_id == "live-watch"
    assert session.completed_mode_ids == ["tda"]

    assert session.move_previous() is True
    assert session.current_mode_id == "tda"


def test_runtime_embeds_tda_and_advances_to_live_watch() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = TradingDayRuntimeWidget(blueprint)

    assert widget.session.current_mode_id == "tda"
    assert widget.mode_stack.currentWidget() is widget.tda_station_runner_widget

    widget.go_next_mode()

    assert widget.session.current_mode_id == "live-watch"
    assert "tda" in widget.session.completed_mode_ids
    assert widget.mode_stack.currentWidget() is widget.mode_pages["live-watch"]


def test_runtime_restores_active_mode() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = TradingDayRuntimeWidget(blueprint)
    session = TradingDaySession(
        blueprint_revision=blueprint.revision,
        mode_ids=[mode.id for mode in blueprint.modes],
        current_mode_id="post-market",
        completed_mode_ids=["tda", "live-watch"],
    )

    widget.load_session(session)

    assert widget.session.current_mode_id == "post-market"
    assert widget.current_mode.name == "Post-Market Review"
    assert widget.mode_stack.currentWidget() is widget.mode_pages["post-market"]
