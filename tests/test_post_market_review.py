from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import (
    ProcessAdherence,
    ThesisState,
    TradingRun,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
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


def test_schema_v14_adds_post_market_review_columns(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(trading_session_run)").fetchall()
    }

    assert CURRENT_SCHEMA_VERSION == 14
    assert "review_process_adherence" in columns
    assert "review_takeaway" in columns
    assert "review_film_night" in columns
    connection.close()


def test_trading_run_review_judgments_are_independent_of_market_outcome() -> None:
    run = TradingRun("day-1", "Trading Run 1", "process-1")
    run.record_thesis_state(ThesisState.INVALIDATED, "Morning thesis failed")

    run.update_post_market_review(
        process_adherence=ProcessAdherence.FOLLOWED,
        takeaway="Invalidation was respected without forcing a replacement trade.",
        film_night=True,
    )

    assert run.current_thesis_state is ThesisState.INVALIDATED
    assert run.review_process_adherence is ProcessAdherence.FOLLOWED
    assert "Invalidation was respected" in run.review_takeaway
    assert run.review_film_night is True


def test_post_market_review_round_trips_through_repository(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    day_repository = TradingDayRepository(connection)
    process_repository = TradingDaySessionRepository(connection)
    run_repository = TradingSessionRunRepository(connection)

    day = TradingDay(futures_day_label="2026-10-06")
    process_session = build_process_session()
    process_repository.save(process_session)
    run = TradingRun(day.id, "Trading Run 1", process_session.id)
    run.update_post_market_review(
        process_adherence=ProcessAdherence.MIXED,
        takeaway="Entry patience was good; management became reactive.",
        film_night=True,
    )
    day.activate_trading_run(run)
    day_repository.save(day)
    run_repository.save(run)

    restored = run_repository.get_by_id(run.id)

    assert restored is not None
    assert restored.review_process_adherence is ProcessAdherence.MIXED
    assert restored.review_takeaway == "Entry patience was good; management became reactive."
    assert restored.review_film_night is True
    connection.close()


def test_post_market_surface_reconstructs_run_and_updates_review() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    run.add_observation("NYAM swept London high and displaced lower")
    run.record_thesis_state(ThesisState.SUPPORTED, "Primary draw remained valid")
    shell.runtime.load_trading_run(run)

    assert shell.runtime.apply_transition(
        "live-finish",
        reason="Participation window complete",
    ) is True
    assert shell.runtime.session.current_mode_id == "post-market"

    review = shell.runtime.post_market_review_widget
    assert review.timeline_list.count() >= 4
    assert "Supported" in review.run_summary_label.text()

    review.adherence_buttons[ProcessAdherence.FOLLOWED].click()
    review.takeaway_input.setText("Waited for the planned condition and respected the exit.")
    review.takeaway_input.editingFinished.emit()
    review.film_night_checkbox.setChecked(True)

    assert run.review_process_adherence is ProcessAdherence.FOLLOWED
    assert run.review_takeaway == "Waited for the planned condition and respected the exit."
    assert run.review_film_night is True


def test_restored_post_market_run_rehydrates_review_surface() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    shell = TradingDayShellWidget(blueprint)
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    shell.runtime.apply_transition("tda-stand-down", reason="No valid setup developed")
    run.update_post_market_review(
        process_adherence=ProcessAdherence.FOLLOWED,
        takeaway="No trade was the correct process outcome.",
        film_night=False,
    )
    shell.runtime.load_trading_run(run)

    restored_shell = TradingDayShellWidget(blueprint)
    restored_shell.load_state(
        shell.trading_day,
        shell.trading_runs,
        process_session=shell.runtime.session,
        tda_session=shell.runtime.tda_station_runner_widget.session,
    )

    review = restored_shell.runtime.post_market_review_widget
    assert restored_shell.runtime.session.current_mode_id == "post-market"
    assert review.adherence_buttons[ProcessAdherence.FOLLOWED].isChecked() is True
    assert review.takeaway_input.text() == "No trade was the correct process outcome."
    assert review.film_night_checkbox.isChecked() is False
    assert review.timeline_list.count() >= 1
