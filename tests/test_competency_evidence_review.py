from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_session_run import (
    RunEnvironment,
    StudyOutcome,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def build_window(tmp_path):
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    return (
        connection,
        MainWindow(
            TDARepository(connection),
            StudyFindRepository(connection),
        ),
    )


def test_review_development_surfaces_accumulated_competency_evidence(
    tmp_path,
) -> None:
    get_app()
    connection, window = build_window(tmp_path)

    launcher = window.trade_plan_widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(
        RunEnvironment.HISTORICAL_BACKTEST.value
    )
    launcher.study_question_input.setText(
        "Can I consistently identify the draw on liquidity?"
    )
    launcher.study_scope_input.setText("Historical NYAM examples")
    launcher.competency_checkboxes["draw-on-liquidity"].setChecked(True)

    assert launcher.begin_process_run() is True

    shell = window.trade_plan_widget.trading_day_shell_widget
    run = shell.active_trading_run
    assert run is not None

    review = shell.runtime.post_market_review_widget
    review.load_state(
        run,
        shell.runtime.tda_station_runner_widget.session,
    )
    review.study_outcome_combo.setCurrentText(StudyOutcome.SUPPORTED.value)
    review.study_outcome_note_input.setText(
        "The draw was identified before lower-timeframe displacement."
    )
    review.study_outcome_note_input.editingFinished.emit()

    window.trade_plan_widget.section_list.setCurrentRow(4)

    evidence_widget = (
        window.trade_plan_widget.competency_evidence_review_widget
    )
    assert evidence_widget is not None
    assert "1 evidence record" in evidence_widget.summary_label.text()
    assert "Study: 1" in evidence_widget.summary_label.text()
    assert "Supported: 1" in evidence_widget.summary_label.text()
    assert evidence_widget.evidence_list.count() == 1
    assert "Draw on liquidity" in evidence_widget.evidence_list.item(0).text()
    assert "Can I consistently identify" in evidence_widget.detail_label.text()
    assert "The draw was identified" in evidence_widget.detail_label.text()
    assert run.trade_plan_revision in evidence_widget.detail_label.text()

    connection.close()


def test_review_development_filters_evidence_by_competency(tmp_path) -> None:
    get_app()
    connection, window = build_window(tmp_path)

    launcher = window.trade_plan_widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText(RunEnvironment.REPLAY.value)
    launcher.competency_checkboxes["time-session-awareness"].setChecked(True)
    launcher.competency_checkboxes[
        "displacement-fvg-recognition"
    ].setChecked(True)
    assert launcher.begin_process_run() is True

    shell = window.trade_plan_widget.trading_day_shell_widget
    run = shell.active_trading_run
    assert run is not None

    review = shell.runtime.post_market_review_widget
    review.load_state(
        run,
        shell.runtime.tda_station_runner_widget.session,
    )
    review.study_outcome_combo.setCurrentText(
        StudyOutcome.PRACTICE_COMPLETE.value
    )

    window.trade_plan_widget.section_list.setCurrentRow(4)
    evidence_widget = (
        window.trade_plan_widget.competency_evidence_review_widget
    )
    assert evidence_widget is not None
    assert "2 evidence record" in evidence_widget.summary_label.text()

    index = evidence_widget.competency_combo.findData(
        "time-session-awareness"
    )
    assert index >= 0
    evidence_widget.competency_combo.setCurrentIndex(index)

    assert "1 evidence record" in evidence_widget.summary_label.text()
    assert evidence_widget.evidence_list.count() == 1
    assert "Time / session awareness" in (
        evidence_widget.evidence_list.item(0).text()
    )
    assert "Displacement" not in evidence_widget.evidence_list.item(0).text()

    connection.close()


def test_review_development_does_not_present_evidence_as_score(tmp_path) -> None:
    get_app()
    connection, window = build_window(tmp_path)

    window.trade_plan_widget.section_list.setCurrentRow(4)
    evidence_widget = (
        window.trade_plan_widget.competency_evidence_review_widget
    )
    assert evidence_widget is not None

    combined = " ".join(
        [
            evidence_widget.summary_label.text(),
            evidence_widget.detail_label.text(),
        ]
    ).lower()
    assert "score" not in combined
    assert "proficiency" in evidence_widget.detail_label.text().lower()

    connection.close()
