from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_session_run import (
    RunEnvironment,
    StudyOutcome,
)
from ict_cockpit.database.competency_evidence_repository import (
    CompetencyEvidenceRepository,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.main_window import MainWindow


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_v28_adds_competency_evidence_storage(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    version = connection.execute("PRAGMA user_version").fetchone()[0]
    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(competency_evidence)"
        ).fetchall()
    }

    assert version == CURRENT_SCHEMA_VERSION == 31
    assert {
        "trade_plan_id",
        "trade_plan_revision",
        "competency_id",
        "competency_name",
        "trading_run_id",
        "run_environment",
        "run_purpose",
        "study_outcome",
        "study_question",
        "market_time_context_json",
        "qt_context_json",
        "recorded_at",
    }.issubset(columns)

    connection.close()


def test_reviewed_study_run_persists_human_legible_competency_evidence(
    tmp_path,
) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )
    launcher = window.trade_plan_widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(
        RunEnvironment.HISTORICAL_BACKTEST.value
    )
    launcher.study_question_input.setText(
        "Can I identify meaningful liquidity inside HTF wicks?"
    )
    launcher.study_hypothesis_input.setText(
        "Explicitly marking nested liquidity will reduce recognition misses."
    )
    launcher.study_scope_input.setText("Daily / 4H context · NYAM examples")
    launcher.competency_checkboxes[
        "htf-liquidity-recognition"
    ].setChecked(True)

    assert launcher.begin_process_run() is True

    shell = window.trade_plan_widget.trading_day_shell_widget
    run = shell.active_trading_run
    assert run is not None
    assert run.study_context is not None

    review = shell.runtime.post_market_review_widget
    review.load_state(
        run,
        shell.runtime.tda_station_runner_widget.session,
    )
    review.study_outcome_combo.setCurrentText(StudyOutcome.REFINED.value)
    review.study_outcome_note_input.setText(
        "Recognition improved, but nested wick liquidity still needs repetition."
    )
    review.study_outcome_note_input.editingFinished.emit()

    evidence = window.competency_evidence_repository.list_for_run(run.id)

    assert len(evidence) == 1
    item = evidence[0]
    assert item.trade_plan_id == build_default_trade_plan().id
    assert item.trade_plan_revision == run.trade_plan_revision
    assert item.competency_id == "htf-liquidity-recognition"
    assert item.competency_name == "HTF liquidity recognition"
    assert item.run_environment == RunEnvironment.HISTORICAL_BACKTEST.value
    assert item.run_purpose == "Study"
    assert item.study_outcome == StudyOutcome.REFINED.value
    assert item.study_question.startswith("Can I identify meaningful")
    assert "nested wick liquidity" in item.note
    assert item.source == "Study Review"
    assert item.recorded_at

    by_competency = window.competency_evidence_repository.list_for_competency(
        item.trade_plan_id,
        item.competency_id,
    )
    assert [entry.id for entry in by_competency] == [item.id]

    connection.close()


def test_re_review_replaces_run_evidence_instead_of_duplicating(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )
    launcher = window.trade_plan_widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(RunEnvironment.REPLAY.value)
    launcher.competency_checkboxes["time-session-awareness"].setChecked(True)
    assert launcher.begin_process_run() is True

    shell = window.trade_plan_widget.trading_day_shell_widget
    run = shell.active_trading_run
    assert run is not None
    assert run.study_context is not None

    review = shell.runtime.post_market_review_widget
    review.load_state(
        run,
        shell.runtime.tda_station_runner_widget.session,
    )

    review.study_outcome_combo.setCurrentText(StudyOutcome.INCONCLUSIVE.value)
    review.study_outcome_note_input.setText("Need another sample.")
    review.study_outcome_note_input.editingFinished.emit()

    first = window.competency_evidence_repository.list_for_run(run.id)
    assert len(first) == 1
    assert first[0].study_outcome == StudyOutcome.INCONCLUSIVE.value

    review.study_outcome_combo.setCurrentText(StudyOutcome.PRACTICE_COMPLETE.value)
    review.study_outcome_note_input.setText("Rehearsal focus completed.")
    review.study_outcome_note_input.editingFinished.emit()

    second = window.competency_evidence_repository.list_for_run(run.id)
    assert len(second) == 1
    assert second[0].study_outcome == StudyOutcome.PRACTICE_COMPLETE.value
    assert second[0].note == "Rehearsal focus completed."

    connection.close()
