from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_day_session import (
    TradingDaySession,
    TradingDayStatus,
    TransitionOutcome,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
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


def test_blueprint_declares_legitimate_transitions_per_mode() -> None:
    blueprint = build_default_process_blueprint()

    assert [item.id for item in blueprint.mode_by_id("tda").transitions] == [
        "finish-tda",
        "tda-stand-down",
    ]
    assert [item.id for item in blueprint.mode_by_id("live-watch").transitions] == [
        "live-finish",
        "live-return-analysis",
        "live-stand-down",
    ]
    assert [item.id for item in blueprint.mode_by_id("post-market").transitions] == [
        "complete-day"
    ]


def test_incomplete_tda_cannot_silently_advance() -> None:
    get_app()
    widget = TradingDayRuntimeWidget(build_default_process_blueprint())

    assert widget.incomplete_tda_station_ids
    assert widget.apply_transition("finish-tda") is False
    assert widget.session.current_mode_id == "tda"
    assert widget.session.transitions == []


def test_return_to_tda_focuses_first_incomplete_station() -> None:
    get_app()
    widget = TradingDayRuntimeWidget(build_default_process_blueprint())
    runner = widget.tda_station_runner_widget

    first_station_id = runner.session.station_ids[0]
    for observation in runner.session.observations[1:]:
        observation.completed = True
    runner.session.current_station_id = runner.session.station_ids[1]
    runner._update_view()
    runner.view_tabs.setCurrentWidget(runner.deck_page)

    assert widget.incomplete_tda_station_ids == [first_station_id]

    widget._focus_first_incomplete_tda_station()

    assert runner.current_station_id == first_station_id
    assert runner.view_tabs.currentWidget() is runner.focus_page


def test_completed_tda_stations_point_to_process_gate() -> None:
    get_app()
    widget = TradingDayRuntimeWidget(build_default_process_blueprint())
    runner = widget.tda_station_runner_widget

    for observation in runner.session.observations:
        observation.completed = True
    runner.session.current_station_id = runner.session.station_ids[-1]
    runner._update_view()

    assert runner.completion_guidance_label.isVisible() is False or (
        "Finish TDA / Enter Live Watch" in runner.completion_guidance_label.text()
    )
    assert "Finish TDA / Enter Live Watch" in runner.completion_guidance_label.text()
    assert runner.next_button.text() == "Station Complete"
    assert runner.next_button.isEnabled() is False


def test_incomplete_tda_override_is_explicitly_recorded() -> None:
    get_app()
    widget = TradingDayRuntimeWidget(build_default_process_blueprint())

    assert widget.apply_transition(
        "finish-tda",
        reason="Premarket window ended",
        override_incomplete=True,
    ) is True

    assert widget.session.current_mode_id == "live-watch"
    transition = widget.session.transitions[-1]
    assert transition.outcome is TransitionOutcome.ADVANCE
    assert transition.override_incomplete is True
    assert transition.reason == "Premarket window ended"


def test_stand_down_is_valid_process_outcome() -> None:
    get_app()
    widget = TradingDayRuntimeWidget(build_default_process_blueprint())

    assert widget.apply_transition(
        "tda-stand-down",
        reason="Conditions do not support participation",
    ) is True

    assert widget.session.current_mode_id == "post-market"
    assert widget.session.day_outcome == TransitionOutcome.STAND_DOWN.value
    assert widget.session.transitions[-1].outcome is TransitionOutcome.STAND_DOWN


def test_live_watch_can_deliberately_return_to_analysis() -> None:
    get_app()
    widget = TradingDayRuntimeWidget(build_default_process_blueprint())
    widget.apply_transition("finish-tda", override_incomplete=True)

    assert "tda" in widget.session.completed_mode_ids
    assert widget.apply_transition(
        "live-return-analysis",
        reason="New information invalidated the active thesis",
    ) is True

    assert widget.session.current_mode_id == "tda"
    assert "tda" not in widget.session.completed_mode_ids
    assert widget.session.transitions[-1].outcome is TransitionOutcome.RETURN_TO_ANALYSIS


def test_complete_day_is_terminal() -> None:
    get_app()
    widget = TradingDayRuntimeWidget(build_default_process_blueprint())
    widget.apply_transition("tda-stand-down")

    assert widget.apply_transition("complete-day", reason="Review complete") is True
    assert widget.session.status is TradingDayStatus.COMPLETE
    assert widget.session.transitions[-1].outcome is TransitionOutcome.COMPLETE_DAY
    assert widget.apply_transition("complete-day") is False


def test_completed_day_can_start_fresh_day_and_tda_sessions() -> None:
    get_app()
    widget = TradingDayRuntimeWidget(build_default_process_blueprint())
    old_day_id = widget.session.id
    old_tda_id = widget.tda_station_runner_widget.session.id

    widget.apply_transition("tda-stand-down")
    widget.apply_transition("complete-day")

    assert widget.session.status is TradingDayStatus.COMPLETE
    assert "start-new-day" in widget.transition_buttons

    widget.start_new()

    assert widget.session.id != old_day_id
    assert widget.tda_station_runner_widget.session.id != old_tda_id
    assert widget.session.status is TradingDayStatus.ACTIVE
    assert widget.session.current_mode_id == "tda"
    assert widget.session.completed_mode_ids == []
    assert widget.session.transitions == []
    assert widget.tda_station_runner_widget.session.completed_count() == 0


def test_transition_history_round_trips_with_session(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION
    repository = TradingDaySessionRepository(connection)

    session = TradingDaySession(
        blueprint_revision="Alpha 0.2",
        mode_ids=["tda", "live-watch", "post-market"],
        current_mode_id="tda",
    )
    session.transition_to(
        "live-watch",
        TransitionOutcome.ADVANCE,
        reason="TDA complete",
    )
    session.stand_down("post-market", reason="No valid setup developed")
    session.complete_day(reason="Post-market review complete")
    repository.save(session)

    restored = repository.get_latest()

    assert restored is not None
    assert restored.status is TradingDayStatus.COMPLETE
    assert restored.day_outcome == TransitionOutcome.STAND_DOWN.value
    assert [item.outcome for item in restored.transitions] == [
        TransitionOutcome.ADVANCE,
        TransitionOutcome.STAND_DOWN,
        TransitionOutcome.COMPLETE_DAY,
    ]
    assert restored.transitions[1].reason == "No valid setup developed"
    connection.close()
