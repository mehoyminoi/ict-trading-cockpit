from PySide6.QtWidgets import QApplication

from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.feedback_repository import FeedbackRepository
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.gui.process_blueprint_widget import ProcessBlueprintWidget
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_default_blueprint_contains_trading_day_modes_only() -> None:
    blueprint = build_default_process_blueprint()

    assert blueprint.id == "ict-process-alpha"
    assert blueprint.revision == "Alpha 0.2"
    assert [mode.id for mode in blueprint.modes] == [
        "tda",
        "live-watch",
        "post-market",
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


def test_default_blueprint_includes_thesis_crossroads_and_outcome_diagnosis() -> None:
    blueprint = build_default_process_blueprint()

    crossroads = blueprint.station_by_id("live-thesis-crossroads")
    assert crossroads is not None
    assert "pivot" in crossroads[2].question

    diagnosis = blueprint.station_by_id("review-outcome-diagnosis")
    assert diagnosis is not None
    assert "process adherence" in diagnosis[2].question


def test_process_blueprint_widget_selects_first_station() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    widget = ProcessBlueprintWidget(blueprint)

    assert widget.selected_station_id == "tda-instrument-context"
    assert "Premarket / TDA" in widget.mode_label.text()
    assert "TDA Deck 1" in widget.deck_label.text()


def test_default_trade_plan_owns_process_and_parallel_review_area() -> None:
    trade_plan = build_default_trade_plan()

    assert trade_plan.revision == "Alpha 0.2"
    assert [section.id for section in trade_plan.sections] == [
        "foundation",
        "rules-safety",
        "process",
        "playbooks",
        "review-development",
    ]
    assert trade_plan.process_blueprint.id == "ict-process-alpha"

    process = trade_plan.section_by_id("process")
    assert process is not None
    assert "trading-day" in process.purpose

    review = trade_plan.section_by_id("review-development")
    assert review is not None
    assert "directly enterable" in review.purpose
    assert "Film Night / Lab study sessions" in review.topics


def test_trade_plan_widget_exposes_process_and_review_as_peer_areas() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())

    names = [
        widget.section_list.item(index).text()
        for index in range(widget.section_list.count())
    ]
    assert names == [
        "Foundation",
        "Rules / Safety",
        "Process",
        "Playbooks",
        "Review / Development",
    ]

    widget.section_list.setCurrentRow(4)
    assert widget.selected_section_id == "review-development"
    assert widget.feedback_record_id == "review-development"

    widget.section_list.setCurrentRow(2)
    assert widget.selected_section_id == "process"
    assert widget.feedback_record_id == "tda-instrument-context"


def test_main_window_feedback_context_tracks_trade_plan_selection(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
        FeedbackRepository(connection),
    )

    window.tabs.setCurrentWidget(window.trade_plan_widget)
    context, record_id = window.current_feedback_context()

    assert context == "Trade Plan"
    assert record_id == "foundation"

    window.trade_plan_widget.section_list.setCurrentRow(2)
    context, record_id = window.current_feedback_context()
    assert context == "Trade Plan"
    assert record_id == "tda-instrument-context"

    connection.close()
