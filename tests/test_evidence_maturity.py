from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.competency import (
    CompetencyEvidenceMaturityProfile,
    CompetencyState,
    EvidenceMaturityState,
    ProgressionBoundary,
)
from ict_cockpit.database.competency_evidence_maturity_repository import (
    CompetencyEvidenceMaturityRepository,
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


def test_schema_v31_adds_boundary_aware_evidence_maturity_storage(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    version = connection.execute("PRAGMA user_version").fetchone()[0]
    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(competency_evidence_maturity)"
        ).fetchall()
    }

    assert version == CURRENT_SCHEMA_VERSION == 33
    assert {
        "trade_plan_id",
        "trade_plan_revision",
        "competency_id",
        "progression_boundary",
        "maturity_state",
        "maturity_note",
        "consistency_note",
        "known_gap_note",
        "source",
        "created_at",
        "updated_at",
    }.issubset(columns)
    connection.close()


def test_repository_keeps_separate_profile_per_progression_boundary(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = CompetencyEvidenceMaturityRepository(connection)

    first = CompetencyEvidenceMaturityProfile(
        trade_plan_id="ict-mentorship-plan",
        trade_plan_revision="Alpha 0.7",
        competency_id="draw-on-liquidity",
        progression_boundary=ProgressionBoundary.STUDY_TO_REHEARSAL,
        maturity_state=EvidenceMaturityState.DEVELOPING,
        maturity_note="Study evidence is coherent but still narrow.",
    )
    repository.save(first)
    created_at = first.created_at

    updated = CompetencyEvidenceMaturityProfile(
        trade_plan_id="ict-mentorship-plan",
        trade_plan_revision="Alpha 0.7",
        competency_id="draw-on-liquidity",
        progression_boundary=ProgressionBoundary.STUDY_TO_REHEARSAL,
        maturity_state=EvidenceMaturityState.DECISION_USABLE,
        maturity_note="Enough reviewed Study evidence to decide on Rehearsal.",
    )
    repository.save(updated)

    second_boundary = CompetencyEvidenceMaturityProfile(
        trade_plan_id="ict-mentorship-plan",
        trade_plan_revision="Alpha 0.7",
        competency_id="draw-on-liquidity",
        progression_boundary=ProgressionBoundary.REHEARSAL_TO_VALIDATION,
        maturity_state=EvidenceMaturityState.INSUFFICIENT,
        maturity_note="Replay integration evidence is still sparse.",
    )
    repository.save(second_boundary)

    loaded = repository.get(
        "ict-mentorship-plan",
        "draw-on-liquidity",
        ProgressionBoundary.STUDY_TO_REHEARSAL.value,
    )
    assert loaded is not None
    assert loaded.maturity_state is EvidenceMaturityState.DECISION_USABLE
    assert loaded.created_at == created_at

    profiles = repository.list_for_competency(
        "ict-mentorship-plan",
        "draw-on-liquidity",
    )
    assert len(profiles) == 2
    assert {
        item.progression_boundary for item in profiles
    } == {
        ProgressionBoundary.STUDY_TO_REHEARSAL,
        ProgressionBoundary.REHEARSAL_TO_VALIDATION,
    }
    connection.close()


def test_maturity_profile_is_human_authored_and_does_not_mutate_other_layers(
    tmp_path,
) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )

    plan = window.trade_plan
    competency_id = "time-session-awareness"
    assessment = window.competency_assessment_repository.get(
        plan.id,
        competency_id,
    )
    original_state = (
        assessment.state
        if assessment is not None
        else CompetencyState.NOT_ASSESSED
    )

    window.trade_plan_widget.section_list.setCurrentRow(4)
    widget = window.trade_plan_widget.competency_evidence_review_widget
    assert widget is not None
    index = widget.competency_combo.findData(competency_id)
    assert index >= 0
    widget.competency_combo.setCurrentIndex(index)

    widget.maturity_boundary_combo.setCurrentText(
        ProgressionBoundary.STUDY_TO_REHEARSAL.value
    )
    widget.maturity_state_combo.setCurrentText(
        EvidenceMaturityState.DEVELOPING.value
    )
    widget.maturity_note_input.setText(
        "Enough evidence to understand the issue, but not yet enough "
        "to trust the next-boundary decision."
    )
    widget.consistency_note_input.setText("Evidence is mixed across sessions.")
    widget.known_gap_note_input.setText("London coverage remains sparse.")
    widget.save_maturity_button.click()

    saved = window.competency_evidence_maturity_repository.get(
        plan.id,
        competency_id,
        ProgressionBoundary.STUDY_TO_REHEARSAL.value,
    )
    assert saved is not None
    assert saved.maturity_state is EvidenceMaturityState.DEVELOPING
    assert saved.consistency_note == "Evidence is mixed across sessions."
    assert saved.known_gap_note == "London coverage remains sparse."

    assessment_after = window.competency_assessment_repository.get(
        plan.id,
        competency_id,
    )
    state_after = (
        assessment_after.state
        if assessment_after is not None
        else CompetencyState.NOT_ASSESSED
    )
    assert state_after is original_state
    assert window.competency_development_direction_repository.get(
        plan.id,
        competency_id,
    ) is None
    assert "No Competency State" in widget.maturity_status_label.text()
    assert "progression" in widget.maturity_status_label.text()
    assert "eligibility" in widget.maturity_status_label.text()
    connection.close()


def test_maturity_ui_keeps_boundary_judgments_separate(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )

    window.trade_plan_widget.section_list.setCurrentRow(4)
    widget = window.trade_plan_widget.competency_evidence_review_widget
    assert widget is not None
    competency_id = "premium-discount-context"
    index = widget.competency_combo.findData(competency_id)
    assert index >= 0
    widget.competency_combo.setCurrentIndex(index)

    widget.maturity_boundary_combo.setCurrentText(
        ProgressionBoundary.STUDY_TO_REHEARSAL.value
    )
    widget.maturity_state_combo.setCurrentText(
        EvidenceMaturityState.DECISION_USABLE.value
    )
    widget.maturity_note_input.setText("Study evidence is decision-usable.")
    widget.save_maturity_button.click()

    widget.maturity_boundary_combo.setCurrentText(
        ProgressionBoundary.VALIDATION_TO_EXECUTION.value
    )
    widget.maturity_state_combo.setCurrentText(
        EvidenceMaturityState.INSUFFICIENT.value
    )
    widget.maturity_note_input.setText("No live-flow validation evidence yet.")
    widget.save_maturity_button.click()

    widget.maturity_boundary_combo.setCurrentText(
        ProgressionBoundary.STUDY_TO_REHEARSAL.value
    )
    assert widget.maturity_state_combo.currentText() == (
        EvidenceMaturityState.DECISION_USABLE.value
    )
    assert widget.maturity_note_input.text() == "Study evidence is decision-usable."

    widget.maturity_boundary_combo.setCurrentText(
        ProgressionBoundary.VALIDATION_TO_EXECUTION.value
    )
    assert widget.maturity_state_combo.currentText() == (
        EvidenceMaturityState.INSUFFICIENT.value
    )
    assert widget.maturity_note_input.text() == (
        "No live-flow validation evidence yet."
    )
    connection.close()


def test_maturity_profile_shows_dimensions_without_numeric_readiness_score(
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
    launcher.environment_combo.setCurrentText("Historical Backtest")
    launcher.study_question_input.setText(
        "Can I identify the external draw consistently?"
    )
    launcher.competency_checkboxes["draw-on-liquidity"].setChecked(True)
    assert launcher.begin_process_run() is True

    shell = window.trade_plan_widget.trading_day_shell_widget
    run = shell.active_trading_run
    assert run is not None
    review = shell.runtime.post_market_review_widget
    review.load_state(run, shell.runtime.tda_station_runner_widget.session)
    review.study_outcome_combo.setCurrentText("Supported")

    window.trade_plan_widget.section_list.setCurrentRow(4)
    widget = window.trade_plan_widget.competency_evidence_review_widget
    assert widget is not None
    index = widget.competency_combo.findData("draw-on-liquidity")
    assert index >= 0
    widget.competency_combo.setCurrentIndex(index)

    dimensions = widget.maturity_dimensions_label.text()
    assert "Volume / Sample Depth · 1 reviewed record(s) across 1 run(s)" in dimensions
    assert "Environment Relevance · Study: 1" in dimensions
    assert "Recency · " in dimensions
    assert "Consistency · Not assessed by technician" in dimensions
    assert "Context Coverage · No human coverage/gap note recorded" in dimensions
    assert "Revision Relevance · evidence Trade Plan revision(s):" in dimensions
    assert "competency-definition equivalence is not yet machine-verifiable" in dimensions
    assert "%" not in dimensions
    assert "score" not in dimensions.lower()
    connection.close()
