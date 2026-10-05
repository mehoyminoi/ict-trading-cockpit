from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.tda_station_session import (
    TDAStationObservation,
    TDAStationSession,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.tda_station_session_repository import (
    TDAStationSessionRepository,
)
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.tda_station_runner_widget import TDAStationRunnerWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_creates_tda_station_session_table(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    table = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='tda_station_session'"
    ).fetchone()

    assert table is not None
    connection.close()


def test_tda_station_session_repository_round_trip(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = TDAStationSessionRepository(connection)

    session = TDAStationSession(
        blueprint_revision="Alpha 0.1",
        current_station_id="station-2",
        observations=[
            TDAStationObservation("station-1", "Discount", True),
            TDAStationObservation("station-2", "Monthly CE overhead", False),
        ],
    )
    repository.save(session)

    restored = repository.get_latest()

    assert restored is not None
    assert restored.id == session.id
    assert restored.current_station_id == "station-2"
    assert restored.observation_for("station-1").completed is True
    assert restored.observation_for("station-2").observation == "Monthly CE overhead"
    connection.close()


def test_tda_runner_advances_and_marks_station_complete() -> None:
    get_app()
    blueprint = build_default_trade_plan().process_blueprint
    widget = TDAStationRunnerWidget(blueprint)

    first_station_id = widget.current_station_id
    widget.observation_input.setPlainText("MNQ NYAM")
    widget.complete_and_continue()

    assert widget.session.observation_for(first_station_id).completed is True
    assert widget.session.observation_for(first_station_id).observation == "MNQ NYAM"
    assert widget.current_station_id != first_station_id


def test_tda_runner_restores_saved_progress() -> None:
    get_app()
    blueprint = build_default_trade_plan().process_blueprint
    widget = TDAStationRunnerWidget(blueprint)

    station_ids = widget.session.station_ids
    session = TDAStationSession(
        blueprint_revision=blueprint.revision,
        current_station_id=station_ids[1],
        observations=[
            TDAStationObservation(
                station_id=station_id,
                observation="Saved observation" if index == 1 else "",
                completed=index == 0,
            )
            for index, station_id in enumerate(station_ids)
        ],
    )

    widget.load_session(session)

    assert widget.current_station_id == station_ids[1]
    assert widget.observation_input.toPlainText() == "Saved observation"
    assert widget.session.completed_count() == 1


def test_trade_plan_embeds_tda_runner_under_trading_day_runtime() -> None:
    get_app()
    trade_plan = build_default_trade_plan()
    from ict_cockpit.gui.trade_plan_widget import TradePlanWidget

    widget = TradePlanWidget(trade_plan)
    process_index = [section.id for section in trade_plan.sections].index("process")
    widget.section_list.setCurrentRow(process_index)

    assert widget.stack.currentWidget() is widget.process_tabs
    assert widget.process_tabs.tabText(1) == "Run Trading Day"
    assert (
        widget.trading_day_runtime_widget.tda_station_runner_widget
        is widget.tda_station_runner_widget
    )
    assert widget.tda_station_runner_widget.current_station_id.startswith("tda-")
