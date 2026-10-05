from PySide6.QtWidgets import QApplication

from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.feedback_repository import FeedbackRepository
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.gui.process_blueprint_widget import ProcessBlueprintWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_default_blueprint_contains_expected_modes() -> None:
    blueprint = build_default_process_blueprint()

    assert blueprint.id == "ict-process-alpha"
    assert blueprint.revision == "Alpha 0.1"
    assert [mode.id for mode in blueprint.modes] == [
        "tda",
        "live-watch",
        "post-market",
        "lab",
    ]


def test_default_blueprint_models_tda_as_multiple_decks() -> None:
    blueprint = build_default_process_blueprint()
    tda_mode = blueprint.modes[0]

    assert tda_mode.name == "Premarket / TDA"
    assert len(tda_mode.decks) == 2
    assert tda_mode.decks[0].id == "tda-context"
    assert tda_mode.decks[1].id == "tda-thesis"

    found = blueprint.station_by_id("tda-ipda-premium-discount")
    assert found is not None
    mode, deck, station = found
    assert mode.id == "tda"
    assert deck.id == "tda-context"
    assert "20 / 40 / 60" in station.question


def test_process_blueprint_widget_selects_first_station() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = ProcessBlueprintWidget(blueprint)

    assert widget.selected_station_id == "tda-instrument-context"
    assert "Premarket / TDA" in widget.mode_label.text()
    assert "TDA Deck 1" in widget.deck_label.text()


def test_main_window_feedback_context_tracks_process_station(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
        FeedbackRepository(connection),
    )

    window.tabs.setCurrentWidget(window.process_blueprint_widget)
    context, record_id = window.current_feedback_context()

    assert context == "Process Map"
    assert record_id == "tda-instrument-context"

    connection.close()
