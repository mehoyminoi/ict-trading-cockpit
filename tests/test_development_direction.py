from PySide6.QtWidgets import QApplication, QScrollArea

from ict_cockpit.analysis.competency import (
    CompetencyDevelopmentDirection,
    CompetencyState,
    DevelopmentDirection,
)
from ict_cockpit.database.competency_development_direction_repository import (
    CompetencyDevelopmentDirectionRepository,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import (
    CURRENT_SCHEMA_VERSION,
    initialize_schema,
)
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_v29_adds_development_direction_storage(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    version = connection.execute("PRAGMA user_version").fetchone()[0]
    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(competency_development_direction)"
        ).fetchall()
    }

    assert version == CURRENT_SCHEMA_VERSION == 30
    assert {
        "trade_plan_id",
        "trade_plan_revision",
        "competency_id",
        "direction",
        "note",
        "supporting_evidence_ids_json",
        "source",
        "created_at",
        "updated_at",
    }.issubset(columns)
    connection.close()


def test_repository_keeps_one_current_direction_per_competency(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = CompetencyDevelopmentDirectionRepository(connection)

    first = CompetencyDevelopmentDirection(
        trade_plan_id="ict-mentorship-plan",
        trade_plan_revision="Alpha 0.7",
        competency_id="draw-on-liquidity",
        direction=DevelopmentDirection.STUDY,
        note="Isolate external versus intermediate draw.",
        supporting_evidence_ids=["run-1:draw-on-liquidity"],
    )
    repository.save(first)
    created_at = first.created_at

    second = CompetencyDevelopmentDirection(
        trade_plan_id="ict-mentorship-plan",
        trade_plan_revision="Alpha 0.7",
        competency_id="draw-on-liquidity",
        direction=DevelopmentDirection.REHEARSAL,
        note="Recognition is stable enough for integrated rehearsal.",
        supporting_evidence_ids=[],
    )
    repository.save(second)

    loaded = repository.get("ict-mentorship-plan", "draw-on-liquidity")
    assert loaded is not None
    assert loaded.direction is DevelopmentDirection.REHEARSAL
    assert loaded.note == "Recognition is stable enough for integrated rehearsal."
    assert loaded.supporting_evidence_ids == []
    assert loaded.created_at == created_at
    assert len(repository.list_for_plan("ict-mentorship-plan")) == 1
    connection.close()


def test_development_direction_does_not_mutate_competency_state(tmp_path) -> None:
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
    widget.direction_combo.setCurrentText(DevelopmentDirection.STUDY.value)
    widget.direction_note_input.setText("Review session context errors.")
    widget.save_direction_button.click()

    saved = window.competency_development_direction_repository.get(
        plan.id,
        competency_id,
    )
    assert saved is not None
    assert saved.direction is DevelopmentDirection.STUDY

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
    assert "No competency state or eligibility change" in (
        widget.development_status_label.text()
    )
    connection.close()


def test_development_direction_can_link_selected_evidence(tmp_path) -> None:
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
        "Can I distinguish the external draw from intermediate liquidity?"
    )
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
    review.study_outcome_combo.setCurrentText("Refined")
    review.study_outcome_note_input.setText(
        "Intermediate liquidity classification needs isolated practice."
    )
    review.study_outcome_note_input.editingFinished.emit()

    window.trade_plan_widget.section_list.setCurrentRow(4)
    widget = window.trade_plan_widget.competency_evidence_review_widget
    assert widget is not None
    evidence = widget._selected_evidence()
    assert evidence is not None

    widget.direction_combo.setCurrentText(DevelopmentDirection.STUDY.value)
    widget.direction_note_input.setText(
        "Return to component study before more Replay."
    )
    widget.link_selected_evidence_checkbox.setChecked(True)
    widget.save_direction_button.click()

    saved = window.competency_development_direction_repository.get(
        window.trade_plan.id,
        "draw-on-liquidity",
    )
    assert saved is not None
    assert saved.direction is DevelopmentDirection.STUDY
    assert saved.supporting_evidence_ids == [evidence.id]
    assert "selected evidence is linked" in widget.development_status_label.text()
    assert "supporting evidence: 1" in widget.current_direction_label.text()
    synthesis = widget.summary_label.text()
    assert "Competency Synthesis · Draw on liquidity" in synthesis
    assert "Development Direction · Study · supporting evidence: 1" in synthesis
    assert "Evidence coverage · 1 evidence record(s) · Study: 1" in synthesis
    assert "Reviewed outcomes · Refined: 1" in synthesis
    assert "Evidence range · " in synthesis
    assert "Descriptive coverage only" in synthesis
    assert "Evidence Maturity" in synthesis
    assert "eligibility conclusion is inferred" in synthesis
    assert widget.link_selected_evidence_checkbox.isChecked() is True
    assert "Selected evidence link · linked" == (
        widget.selected_evidence_link_label.text()
    )

    widget.refresh()
    assert widget.link_selected_evidence_checkbox.isChecked() is True
    assert "Selected evidence link · linked" == (
        widget.selected_evidence_link_label.text()
    )
    connection.close()


def test_review_development_page_is_scrollable(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )

    trade_plan_widget = window.trade_plan_widget
    review_row = trade_plan_widget._section_ids.index("review-development")
    review_page = trade_plan_widget.stack.widget(review_row)

    assert isinstance(review_page, QScrollArea)
    assert review_page.widgetResizable() is True
    connection.close()


def test_development_direction_link_state_survives_widget_recreation(
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

    launcher = window.trade_plan_widget.process_run_launcher_widget
    launcher.environment_combo.setCurrentText("Historical Backtest")
    launcher.study_question_input.setText("Can I identify session context?")
    launcher.competency_checkboxes["time-session-awareness"].setChecked(True)
    assert launcher.begin_process_run() is True

    shell = window.trade_plan_widget.trading_day_shell_widget
    run = shell.active_trading_run
    assert run is not None
    review = shell.runtime.post_market_review_widget
    review.load_state(
        run,
        shell.runtime.tda_station_runner_widget.session,
    )
    review.study_outcome_combo.setCurrentText("Practice Complete")

    window.trade_plan_widget.section_list.setCurrentRow(4)
    widget = window.trade_plan_widget.competency_evidence_review_widget
    assert widget is not None
    evidence = widget._selected_evidence()
    assert evidence is not None

    widget.direction_combo.setCurrentText(DevelopmentDirection.STUDY.value)
    widget.link_selected_evidence_checkbox.setChecked(True)
    widget.save_direction_button.click()
    connection.close()

    connection = create_connection(db_path)
    initialize_schema(connection)
    restored = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )
    restored.trade_plan_widget.section_list.setCurrentRow(4)
    restored_widget = (
        restored.trade_plan_widget.competency_evidence_review_widget
    )
    assert restored_widget is not None
    restored_evidence = restored_widget._selected_evidence()
    assert restored_evidence is not None
    assert restored_evidence.id == evidence.id
    assert restored_widget.link_selected_evidence_checkbox.isChecked() is True
    assert restored_widget.selected_evidence_link_label.text() == (
        "Selected evidence link · linked"
    )
    assert "supporting evidence: 1" in (
        restored_widget.current_direction_label.text()
    )
    connection.close()


def test_competency_synthesis_without_evidence_is_descriptive(tmp_path) -> None:
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

    synthesis = widget.summary_label.text()
    assert "Competency Synthesis · Premium / discount context" in synthesis
    assert f"Trade Plan {window.trade_plan.revision}" in synthesis
    assert "Development Direction · Not recorded" in synthesis
    assert "Evidence coverage · no reviewed evidence recorded" in synthesis
    assert "Descriptive coverage only" in synthesis
    assert "proficiency" in synthesis
    assert "Evidence Maturity" in synthesis
    assert "eligibility conclusion is inferred" in synthesis
    connection.close()
