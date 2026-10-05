from datetime import date

from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.study_find import StudyFindDraft
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.gui.study_find_widget import StudyFindWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_creates_study_find_draft_table(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    table = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'study_find_draft'
        """
    ).fetchone()

    assert table is not None
    connection.close()


def test_repository_round_trips_and_deletes_draft(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = StudyFindRepository(connection)

    draft = StudyFindDraft(
        id="draft-123",
        observation_date=date(2026, 10, 5),
        instrument="mnq",
        session="NYAM",
        pattern_name="London low raid",
        observation="Partial observation",
        available_move_handles=42.5,
        notes="Partial notes",
        image_paths=[
            "/tmp/chart-1.png",
            "/tmp/chart-3.png",
        ],
    )

    repository.save_draft(draft)
    loaded = repository.get_latest_draft()

    assert loaded is not None
    assert loaded.id == draft.id
    assert loaded.instrument == "mnq"
    assert loaded.observation == "Partial observation"
    assert loaded.image_paths == draft.image_paths

    repository.delete_draft(draft.id)
    assert repository.get_latest_draft() is None

    connection.close()


def test_widget_loads_draft_and_restores_image_numbering() -> None:
    get_app()
    widget = StudyFindWidget()

    draft = StudyFindDraft(
        id="draft-456",
        observation_date=date(2026, 10, 5),
        instrument="MNQ",
        session="NYPM",
        pattern_name="FVG continuation",
        observation="Restore this text",
        available_move_handles=75.0,
        notes="Restore notes",
        image_paths=[
            "/tmp/chart-1.png",
            "/tmp/chart-3.png",
        ],
    )

    widget.load_draft(draft)

    assert widget.current_study_find_id == "draft-456"
    assert widget.instrument_input.text() == "MNQ"
    assert widget.session_input.text() == "NYPM"
    assert widget.pattern_input.text() == "FVG continuation"
    assert widget.observation_input.toPlainText() == "Restore this text"
    assert widget.available_move_input.value() == 75.0
    assert widget.notes_input.toPlainText() == "Restore notes"
    assert widget.image_paths == draft.image_paths
    assert widget.next_image_number == 4


def test_main_window_saves_and_restores_study_find_draft(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection)

    first_window = MainWindow(tda_repository, study_find_repository)
    widget = first_window.study_find_widget
    widget.instrument_input.setText("MNQ")
    widget.session_input.setText("NYAM")
    widget.observation_input.setPlainText("Work in progress")
    widget.image_paths = ["/tmp/chart-1.png"]

    draft = widget.build_draft()
    first_window.schedule_study_find_draft_save(draft)
    first_window.save_pending_study_find_draft()

    second_window = MainWindow(tda_repository, study_find_repository)
    restored = second_window.study_find_widget

    assert restored.current_study_find_id == draft.id
    assert restored.instrument_input.text() == "MNQ"
    assert restored.session_input.text() == "NYAM"
    assert restored.observation_input.toPlainText() == "Work in progress"
    assert restored.image_paths == ["/tmp/chart-1.png"]

    connection.close()


def test_final_save_clears_study_find_draft(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection)
    window = MainWindow(tda_repository, study_find_repository)
    widget = window.study_find_widget

    widget.instrument_input.setText("MNQ")
    widget.session_input.setText("NYAM")
    widget.pattern_input.setText("Liquidity raid")
    widget.observation_input.setPlainText("Completed observation")

    draft = widget.build_draft()
    study_find_repository.save_draft(draft)
    assert study_find_repository.get_latest_draft() is not None

    window.save_study_find(widget.build_study_find())

    assert study_find_repository.get_latest_draft() is None
    connection.close()
