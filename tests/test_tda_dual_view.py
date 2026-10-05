from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.tda_station_session import TDAStationSession
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.tda_station_session_repository import (
    TDAStationSessionRepository,
)
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.tda_station_runner_widget import TDAStationRunnerWidget
from ict_cockpit.process_blueprint import StationDefinition


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_station_definition_has_generic_actions_and_layout_metadata() -> None:
    station = StationDefinition(
        id="test",
        name="Test Station",
        question="What do I see?",
    )

    assert len(station.action_items) == 3
    assert "TradingView" in station.action_items[0]
    assert station.layout_row == -1
    assert station.layout_column == -1


def test_station_action_completion_round_trips(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = TDAStationSessionRepository(connection)

    blueprint = build_default_process_blueprint()
    widget = TDAStationRunnerWidget(blueprint)
    widget.session.observations[0].completed_actions = [0, 2]
    repository.save(widget.session)

    restored = repository.get_latest()
    assert restored is not None
    assert restored.observations[0].completed_actions == [0, 2]

    connection.close()


def test_focus_and_deck_views_share_current_station() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = TDAStationRunnerWidget(blueprint)

    second_station_id = widget.session.station_ids[1]
    widget.select_station(second_station_id)
    widget.view_tabs.setCurrentWidget(widget.deck_page)

    assert widget.current_station_id == second_station_id
    assert widget.session.current_station_id == second_station_id
    assert widget._current_deck().id == "tda-context"


def test_deck_station_opens_directly_in_focus_view() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = TDAStationRunnerWidget(blueprint)

    second_station_id = widget.session.station_ids[1]
    widget.view_tabs.setCurrentWidget(widget.deck_page)
    widget.open_station_from_deck(second_station_id)

    assert widget.current_station_id == second_station_id
    assert widget.view_tabs.currentWidget() is widget.focus_page


def test_action_checkbox_updates_shared_session_state() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = TDAStationRunnerWidget(blueprint)

    assert widget.session.observations[0].completed_actions == []
    widget._action_checkboxes[0].setChecked(True)

    assert widget.session.observations[0].completed_actions == [0]
    assert isinstance(widget.session, TDAStationSession)
