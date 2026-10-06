from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import (
    InterpretationOutcome,
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


def test_schema_preserves_post_market_review_columns(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(trading_session_run)").fetchall()
    }
    version = connection.execute("PRAGMA user_version").fetchone()[0]

    assert version == CURRENT_SCHEMA_VERSION
    assert "review_interpretation_outcome" in columns
    assert "review_process_adherence" in columns
    assert "review_takeaway" in columns
    assert "review_film_night" in columns
    connection.close()


def test_interpretation_and_process_judgments_remain_independent() -> None:
    run = TradingRun("day-1", "Trading Run 1", "process-1")
    run.record_thesis_state(ThesisState.INVALIDATED, "Morning thesis failed")

    run.update_post_market_review(
        interpretation_outcome=InterpretationOutcome.MISSED_CRITICAL_INFORMATION,
        process_adherence=ProcessAdherence.FOLLOWED,
        takeaway="Invalidation was respected without forcing a replacement trade.",
        film_night=True,
    )

    assert run.current_thesis_state is ThesisState.INVALIDATED
    assert run.review_interpretation_outcome is (
        InterpretationOutcome.MISSED_CRITICAL_INFORMATION
    )
    assert run.review_process_adherence is ProcessAdherence.FOLLOWED
    assert "Invalidation was respected" in run.review_takeaway
    assert run.review_film_night is True


def test_unexplained_means_study_needed_not_randomness() -> None:
    assert InterpretationOutcome.UNEXPLAINED_STUDY_NEEDED.value == (
        "Changed — Unexplained / Study Needed"
    )
    assert "Study Needed" in InterpretationOutcome.UNEXPLAINED_STUDY_NEEDED.value


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
        interpretation_outcome=InterpretationOutcome.UNEXPLAINED_STUDY_NEEDED,
        process_adherence=ProcessAdherence.MIXED,
        takeaway="Entry patience was good; management became reactive.",
        film_night=True,
    )
    day.activate_trading_run(run)
    day_repository.save(day)
    run_repository.save(run)

    restored = run_repository.get_by_id(run.id)

    assert restored is not None
    assert restored.review_interpretation_outcome is (
        InterpretationOutcome.UNEXPLAINED_STUDY_NEEDED
    )
    assert restored.review_process_adherence is ProcessAdherence.MIXED
    assert restored.review_takeaway == "Entry patience was good; management became reactive."
    assert restored.review_film_night is True
    connection.close()


def test_market_review_contrasts_tda_with_live_watch_without_process_click_log() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    tda_session = shell.runtime.tda_station_runner_widget.session
    tda_session.observations[-1].observation = (
        "Expect lower prices if NYAM rejects the morning premium array."
    )

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
    assert review.stage_stack.currentWidget() is review.market_review_page
    assert review.tda_snapshot_list.count() == 1
    assert "Premarket Thesis" in review.tda_snapshot_list.item(0).text()
    assert review.live_changes_list.count() == 2
    assert "Supported" in review.live_changes_list.item(1).text()
    assert "Supported" in review.run_summary_label.text()
    assert not hasattr(review, "timeline_list")


def test_market_review_records_interpretation_before_process_review() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    shell.runtime.apply_transition("tda-stand-down", reason="No valid setup developed")
    review = shell.runtime.post_market_review_widget

    assert review.stage_stack.currentWidget() is review.market_review_page
    review.interpretation_buttons[
        InterpretationOutcome.MATERIALLY_ACCURATE
    ].click()

    assert run.review_interpretation_outcome is InterpretationOutcome.MATERIALLY_ACCURATE
    assert run.review_process_adherence is ProcessAdherence.NOT_REVIEWED


def test_process_adherence_is_a_separate_review_stage() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    shell.runtime.apply_transition("tda-stand-down", reason="No valid setup developed")
    review = shell.runtime.post_market_review_widget

    assert review.stage_stack.currentWidget() is review.market_review_page
    review.to_process_review_button.click()
    assert review.stage_stack.currentWidget() is review.process_review_page
    assert "2 of 2" in review.stage_label.text()

    review.adherence_buttons[ProcessAdherence.FOLLOWED].click()
    review.takeaway_input.setText("No trade was the correct process outcome.")
    review.takeaway_input.editingFinished.emit()
    review.film_night_checkbox.setChecked(True)

    assert run.review_interpretation_outcome is InterpretationOutcome.NOT_REVIEWED
    assert run.review_process_adherence is ProcessAdherence.FOLLOWED
    assert run.review_takeaway == "No trade was the correct process outcome."
    assert run.review_film_night is True

    review.back_to_market_button.click()
    assert review.stage_stack.currentWidget() is review.market_review_page


def test_restored_post_market_run_rehydrates_both_review_stages() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    shell = TradingDayShellWidget(blueprint)
    shell.start_trading_run()
    run = shell.active_trading_run
    assert run is not None

    shell.runtime.tda_station_runner_widget.session.observations[-1].observation = (
        "Primary draw is prior-day low."
    )
    shell.runtime.apply_transition("tda-stand-down", reason="No valid setup developed")
    run.update_post_market_review(
        interpretation_outcome=InterpretationOutcome.EXOGENOUS_EVENT,
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
    assert review.tda_snapshot_list.count() == 1
    assert "prior-day low" in review.tda_snapshot_list.item(0).text()
    assert review.interpretation_buttons[
        InterpretationOutcome.EXOGENOUS_EVENT
    ].isChecked() is True
    assert review.adherence_buttons[ProcessAdherence.FOLLOWED].isChecked() is True
    assert review.takeaway_input.text() == "No trade was the correct process outcome."
    assert review.film_night_checkbox.isChecked() is False
