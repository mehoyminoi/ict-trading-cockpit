from datetime import date
from PySide6.QtWidgets import QApplication

from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.analysis.tda import Bias, TDARecord, TDAStatus
from ict_cockpit.database.study_find_repository import StudyFindRepository


def test_main_window_saves_ready_tda(tmp_path) -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection)

    window = MainWindow(
        tda_repository,
        study_find_repository,
    )

    workflow = window.tda_workflow

    workflow.context_step.instrument_input.setText("MNQ")
    workflow.bias_step.weekly_buttons[0].setChecked(True)
    workflow.bias_step.daily_buttons[0].setChecked(True)
    workflow.draw_thesis_step.primary_draw_input.setText(
        "Previous Week High"
    )

    emitted = []
    workflow.tda_ready.connect(emitted.append)

    workflow.attempt_completion()

    assert len(emitted) == 1

    saved = repository.get_by_id(emitted[0].id)

    assert saved is not None
    assert saved.instrument == "MNQ"

    connection.close()

def test_main_window_saves_pending_draft(tmp_path) -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)
    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection)

    window = MainWindow(
        tda_repository,
        study_find_repository,
    )

    workflow = window.tda_workflow

    workflow.context_step.instrument_input.setText("MNQ")

    draft = workflow.build_tda_record()

    window.schedule_draft_save(draft)
    window.save_pending_draft()

    saved = repository.get_by_id(draft.id)

    assert saved is not None
    assert saved.instrument == "MNQ"
    assert saved.status == TDAStatus.DRAFT

    connection.close()

def test_main_window_restores_latest_draft(tmp_path) -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection)

    draft = TDARecord(
        analysis_date=date(2026, 10, 4),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.BEARISH,
        primary_draw="Previous Week High",
        narrative="Restore me.",
        status=TDAStatus.DRAFT,
    )

    repository.save_draft(draft)

    window = MainWindow(
    tda_repository,
    study_find_repository,
    )

    workflow = window.tda_workflow

    assert workflow.current_tda_id == draft.id
    assert workflow.context_step.instrument_input.text() == "MNQ"
    assert workflow.bias_step.weekly_bias() == Bias.BULLISH
    assert workflow.bias_step.daily_bias() == Bias.BEARISH
    assert workflow.draw_thesis_step.primary_draw() == "Previous Week High"
    assert workflow.draw_thesis_step.narrative() == "Restore me."

    connection.close()

def test_main_window_saves_study_find(tmp_path) -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection)

    window = MainWindow(
        tda_repository,
        study_find_repository,
    )

    widget = window.study_find_widget

    widget.instrument_input.setText("MNQ")
    widget.session_input.setText("NYAM")
    widget.pattern_input.setText("London low raid")
    widget.observation_input.setPlainText(
        "Bullish displacement followed the sweep."
    )
    widget.available_move_input.setValue(74.5)

    emitted = []
    widget.study_find_ready.connect(emitted.append)

    widget.submit()

    assert len(emitted) == 1

    saved = study_find_repository.get_by_id(
        emitted[0].id
    )

    assert saved is not None
    assert saved.instrument == "MNQ"
    assert saved.pattern_name == "London low raid"
    assert saved.available_move_handles == 74.5

    connection.close()