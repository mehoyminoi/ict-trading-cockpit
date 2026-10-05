from PySide6.QtWidgets import QApplication, QDialog

from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.feedback_repository import FeedbackRepository
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.feedback import FeedbackEntry
from ict_cockpit.gui.feedback_dialog import FeedbackDialog
from ict_cockpit.gui.main_window import MainWindow


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_creates_feedback_table(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    table = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'feedback_entry'
        """
    ).fetchone()

    assert table is not None
    connection.close()


def test_feedback_repository_round_trips_entry(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = FeedbackRepository(connection)

    entry = FeedbackEntry(
        id="feedback-123",
        created_at="2026-10-04T22:45:00-06:00",
        category="Friction",
        note="Too many clicks to attach a chart.",
        context="Study Find",
        record_id="study-456",
        app_version="0.1.0",
    )

    repository.save(entry)
    loaded = repository.get_recent()

    assert len(loaded) == 1
    assert loaded[0].id == entry.id
    assert loaded[0].category == "Friction"
    assert loaded[0].note == "Too many clicks to attach a chart."
    assert loaded[0].context == "Study Find"
    assert loaded[0].record_id == "study-456"

    connection.close()


def test_feedback_digest_is_human_readable_markdown(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = FeedbackRepository(connection)

    repository.save(
        FeedbackEntry(
            created_at="2026-10-04T22:46:00-06:00",
            category="Wish",
            note="Make chart review more visual.",
            context="Study Review",
            record_id="study-789",
            app_version="0.1.0",
        )
    )

    digest = repository.render_markdown_digest()

    assert "# ICT Trading Cockpit — Alpha Feedback Digest" in digest
    assert "## 2026-10-04T22:46:00-06:00 — Wish" in digest
    assert "- Context: Study Review" in digest
    assert "- Record ID: study-789" in digest
    assert "- Note: Make chart review more visual." in digest

    connection.close()


def test_feedback_dialog_builds_entry() -> None:
    get_app()
    dialog = FeedbackDialog(
        context="Study Find",
        record_id="study-123",
        app_version="0.1.0",
    )
    dialog.category_input.setCurrentText("Bug")
    dialog.note_input.setPlainText("Preview did not update.")

    entry = dialog.build_entry()

    assert entry.category == "Bug"
    assert entry.note == "Preview did not update."
    assert entry.context == "Study Find"
    assert entry.record_id == "study-123"


def test_feedback_dialog_does_not_accept_blank_note() -> None:
    get_app()
    dialog = FeedbackDialog(
        context="Guided TDA",
        record_id="tda-123",
        app_version="0.1.0",
    )

    dialog.accept()

    assert dialog.result() != QDialog.DialogCode.Accepted


def test_main_window_feedback_context_tracks_active_tab(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection)
    feedback_repository = FeedbackRepository(connection)

    window = MainWindow(
        tda_repository,
        study_find_repository,
        feedback_repository,
    )

    window.tabs.setCurrentWidget(window.study_find_widget)
    context, record_id = window.current_feedback_context()

    assert context == "Study Find"
    assert record_id == window.study_find_widget.current_study_find_id

    connection.close()


def test_main_window_copies_feedback_digest(tmp_path) -> None:
    app = get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection)
    feedback_repository = FeedbackRepository(connection)
    feedback_repository.save(
        FeedbackEntry(
            category="Review Later",
            note="Revisit shortcut placement.",
            context="Guided TDA",
        )
    )

    window = MainWindow(
        tda_repository,
        study_find_repository,
        feedback_repository,
    )

    digest = window.copy_feedback_digest()

    assert "Revisit shortcut placement." in digest
    assert app.clipboard().text() == digest

    connection.close()
