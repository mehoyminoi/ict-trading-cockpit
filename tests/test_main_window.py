from PySide6.QtWidgets import QApplication

from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.analysis.tda import TDAStatus


def test_main_window_saves_ready_tda(tmp_path) -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    window = MainWindow(repository)

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
    window = MainWindow(repository)

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