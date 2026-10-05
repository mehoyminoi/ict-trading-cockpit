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


def test_deck_view_shows_all_tda_decks_at_once() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = TDAStationRunnerWidget(blueprint)

    headings = [label.text() for label in widget.deck_section_headings]

    assert len(headings) == 2
    assert any("TDA Deck 1" in text for text in headings)
    assert any("TDA Deck 2" in text for text in headings)


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


def test_station_state_distinguishes_work_from_explicit_completion() -> None:
    get_app()
    widget = TDAStationRunnerWidget(build_default_process_blueprint())
    observation = widget.session.observations[0]

    assert widget.station_state(observation) == "pending"
    assert widget.station_state_label.text() == "○ Pending"

    widget.observation_input.setPlainText("Price is in discount.")

    assert widget.station_state(observation) == "in_progress"
    assert "In Progress" in widget.station_state_label.text()
    assert observation.completed is False

    widget.complete_and_continue()

    assert observation.completed is True
    assert widget.station_state(observation) == "complete"


def test_completion_button_makes_explicit_station_contract_clear() -> None:
    get_app()
    widget = TDAStationRunnerWidget(build_default_process_blueprint())

    assert widget.next_button.text() == "Mark Station Complete & Continue →"

    widget.observation_input.setPlainText("Work entered but not certified.")
    widget.go_next_station()

    first = widget.session.observations[0]
    assert first.observation == "Work entered but not certified."
    assert first.completed is False
    assert widget.station_state(first) == "in_progress"


def test_wheel_navigation_requires_more_deliberate_scroll() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = TDAStationRunnerWidget(blueprint)

    first_station_id = widget.session.station_ids[0]
    second_station_id = widget.session.station_ids[1]

    for _ in range(3):
        assert widget._accumulate_wheel_navigation(-120) is False
        assert widget.current_station_id == first_station_id

    assert widget._accumulate_wheel_navigation(-120) is True
    assert widget.current_station_id == second_station_id


def test_wheel_direction_change_resets_partial_accumulation() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = TDAStationRunnerWidget(blueprint)

    first_station_id = widget.session.station_ids[0]

    assert widget._accumulate_wheel_navigation(-120) is False
    assert widget._accumulate_wheel_navigation(120) is False
    assert widget.current_station_id == first_station_id


def test_scrolling_before_first_station_opens_deck_view() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = TDAStationRunnerWidget(blueprint)

    assert widget.current_station_index == 0
    assert widget.view_tabs.currentWidget() is widget.focus_page

    assert widget._accumulate_wheel_navigation(480) is True
    assert widget.current_station_index == 0
    assert widget.view_tabs.currentWidget() is widget.deck_page


def test_scrolling_after_last_station_opens_deck_view() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = TDAStationRunnerWidget(blueprint)

    last_station_id = widget.session.station_ids[-1]
    widget.select_station(last_station_id)

    assert widget.view_tabs.currentWidget() is widget.focus_page
    assert widget._accumulate_wheel_navigation(-480) is True
    assert widget.current_station_id == last_station_id
    assert widget.view_tabs.currentWidget() is widget.deck_page
