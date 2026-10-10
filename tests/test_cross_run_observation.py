from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.competency import CompetencyCrossRunObservation
from ict_cockpit.database.competency_cross_run_observation_repository import (
    CompetencyCrossRunObservationRepository,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_v30_adds_cross_run_observation_storage(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    version = connection.execute("PRAGMA user_version").fetchone()[0]
    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(competency_cross_run_observation)"
        ).fetchall()
    }

    assert version == CURRENT_SCHEMA_VERSION == 32
    assert {
        "trade_plan_id",
        "trade_plan_revision",
        "competency_id",
        "observation",
        "supporting_evidence_ids_json",
        "source",
        "created_at",
        "updated_at",
    }.issubset(columns)
    connection.close()


def test_repository_keeps_one_current_cross_run_observation(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = CompetencyCrossRunObservationRepository(connection)

    first = CompetencyCrossRunObservation(
        trade_plan_id="ict-mentorship-plan",
        trade_plan_revision="Alpha 0.7",
        competency_id="draw-on-liquidity",
        observation="Intermediate liquidity is inconsistent after expansion.",
        supporting_evidence_ids=["run-1:draw-on-liquidity"],
    )
    repository.save(first)
    created_at = first.created_at

    second = CompetencyCrossRunObservation(
        trade_plan_id="ict-mentorship-plan",
        trade_plan_revision="Alpha 0.7",
        competency_id="draw-on-liquidity",
        observation="The issue now appears limited to post-expansion cases.",
        supporting_evidence_ids=["run-1:draw-on-liquidity", "run-2:draw-on-liquidity"],
    )
    repository.save(second)

    loaded = repository.get("ict-mentorship-plan", "draw-on-liquidity")
    assert loaded is not None
    assert loaded.observation == (
        "The issue now appears limited to post-expansion cases."
    )
    assert loaded.supporting_evidence_ids == [
        "run-1:draw-on-liquidity",
        "run-2:draw-on-liquidity",
    ]
    assert loaded.created_at == created_at
    assert len(repository.list_for_plan("ict-mentorship-plan")) == 1
    connection.close()


def test_cross_run_observation_persists_and_updates_synthesis(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )

    launcher = window.trade_plan_widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText("Historical Backtest")
    launcher.study_question_input.setText(
        "Can I distinguish external from intermediate liquidity?"
    )
    launcher.competency_checkboxes["draw-on-liquidity"].setChecked(True)
    assert launcher.begin_process_run() is True

    shell = window.trade_plan_widget.trading_day_shell_widget
    run = shell.active_trading_run
    assert run is not None
    review = shell.runtime.post_market_review_widget
    review.load_state(run, shell.runtime.tda_station_runner_widget.session)
    review.study_outcome_combo.setCurrentText("Refined")
    review.study_outcome_note_input.setText(
        "Intermediate liquidity was missed after expansion."
    )
    review.study_outcome_note_input.editingFinished.emit()

    window.trade_plan_widget.section_list.setCurrentRow(4)
    widget = window.trade_plan_widget.competency_evidence_review_widget
    assert widget is not None

    index = widget.competency_combo.findData("draw-on-liquidity")
    assert index >= 0
    widget.competency_combo.setCurrentIndex(index)

    evidence = widget._selected_evidence()
    assert evidence is not None
    widget.cross_run_observation_input.setPlainText(
        "Intermediate-liquidity classification breaks down after large expansion."
    )
    widget.cross_run_link_selected_evidence_checkbox.setChecked(True)
    widget.save_cross_run_observation_button.click()

    saved = window.competency_cross_run_observation_repository.get(
        window.trade_plan.id,
        "draw-on-liquidity",
    )
    assert saved is not None
    assert saved.observation.startswith("Intermediate-liquidity classification")
    assert saved.supporting_evidence_ids == [evidence.id]
    assert "Cross-Run Observation · Intermediate-liquidity classification" in (
        widget.summary_label.text()
    )
    assert "supporting evidence: 1" in widget.summary_label.text()
    assert (
        "No Development Direction, competency state, Evidence Maturity, "
        "or eligibility change was made."
    ) in widget.cross_run_status_label.text()
    assert window.competency_development_direction_repository.get(
        window.trade_plan.id,
        "draw-on-liquidity",
    ) is None
    connection.close()


def test_cross_run_observation_survives_restart_without_changing_direction(
    tmp_path,
) -> None:
    get_app()
    db_path = tmp_path / "test.db"
    connection = create_connection(db_path)
    initialize_schema(connection)
    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )

    window.trade_plan_widget.section_list.setCurrentRow(4)
    widget = window.trade_plan_widget.competency_evidence_review_widget
    assert widget is not None
    index = widget.competency_combo.findData("time-session-awareness")
    assert index >= 0
    widget.competency_combo.setCurrentIndex(index)

    widget.cross_run_observation_input.setPlainText(
        "Session context is reliable in NYAM but mixed in London."
    )
    widget.save_cross_run_observation_button.click()

    assert window.competency_development_direction_repository.get(
        window.trade_plan.id,
        "time-session-awareness",
    ) is None
    connection.close()

    connection = create_connection(db_path)
    initialize_schema(connection)
    restored = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )
    restored.trade_plan_widget.section_list.setCurrentRow(4)
    restored_widget = restored.trade_plan_widget.competency_evidence_review_widget
    assert restored_widget is not None
    index = restored_widget.competency_combo.findData("time-session-awareness")
    restored_widget.competency_combo.setCurrentIndex(index)

    assert restored_widget.cross_run_observation_input.toPlainText() == (
        "Session context is reliable in NYAM but mixed in London."
    )
    assert "Session context is reliable" in (
        restored_widget.current_cross_run_observation_label.text()
    )
    assert restored.competency_development_direction_repository.get(
        restored.trade_plan.id,
        "time-session-awareness",
    ) is None
    connection.close()
