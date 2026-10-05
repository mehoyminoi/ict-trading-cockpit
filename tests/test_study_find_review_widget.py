from datetime import date

from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.study_find import StudyFind
from ict_cockpit.database.connection import (
    create_connection,
)
from ict_cockpit.database.schema import (
    initialize_schema,
)
from ict_cockpit.database.study_find_repository import (
    StudyFindRepository,
)
from ict_cockpit.gui.study_find_review_widget import (
    StudyFindReviewWidget,
)


def test_review_widget_lists_saved_study_finds(
    tmp_path,
) -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    connection = create_connection(
        tmp_path / "test.db"
    )
    initialize_schema(connection)

    repository = StudyFindRepository(connection)

    study_find = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="MNQ",
        session="NYAM",
        pattern_name="London low raid",
        observation="Bullish displacement.",
    )

    repository.save(study_find)

    widget = StudyFindReviewWidget(
        repository
    )

    assert widget.study_list.count() == 1

    assert "MNQ" in (
        widget.study_list.item(0).text()
    )

    connection.close()

def test_review_widget_selects_newest_study_find(
    tmp_path,
) -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    connection = create_connection(
        tmp_path / "test.db"
    )
    initialize_schema(connection)

    repository = StudyFindRepository(connection)

    older = StudyFind(
        observation_date=date(2026, 10, 1),
        instrument="MNQ",
        session="NYAM",
        pattern_name="Older",
        observation="Older observation.",
    )

    newer = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="MNQ",
        session="NYPM",
        pattern_name="Newer",
        observation="Newer observation.",
    )

    repository.save(older)
    repository.save(newer)

    widget = StudyFindReviewWidget(
        repository
    )

    assert widget.study_list.currentRow() == 0

    assert (
        widget.observation_view.toPlainText()
        == "Newer observation."
    )

    connection.close()