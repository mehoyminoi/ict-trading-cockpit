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

def test_review_automatically_previews_first_attachment(tmp_path):
    from PySide6.QtGui import QImage
    app = QApplication.instance() or QApplication([])
    connection = create_connection(tmp_path / 'preview.db')
    initialize_schema(connection)
    repository = StudyFindRepository(connection)
    find = StudyFind(observation_date=date(2026,10,26), instrument='MNQ',
                     session='NYAM', pattern_name='Preview', observation='Chart')
    repository.save(find)
    path = tmp_path / 'chart.png'
    image = QImage(32, 24, QImage.Format.Format_RGB32)
    image.fill(0xffffff)
    assert image.save(str(path))
    repository.add_image(find.id, str(path))
    widget = StudyFindReviewWidget(repository)
    assert widget.image_list.currentRow() == 0
    assert not widget.image_preview.pixmap().isNull()
    assert widget.open_image_button.isEnabled()
    widget.close()
    connection.close()


def test_full_size_image_is_owned_modal_and_closes_independently(tmp_path):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QScrollArea
    app = QApplication.instance() or QApplication([])
    connection = create_connection(tmp_path / 'viewer.db')
    initialize_schema(connection)
    repository = StudyFindRepository(connection)
    find = StudyFind(observation_date=date(2026,10,30), instrument='MNQ',
                     session='London', pattern_name='Viewer', observation='Retained observation')
    repository.save(find)
    path = tmp_path / 'large-chart.png'
    image = QImage(1800, 1000, QImage.Format.Format_RGB32)
    image.fill(0xffffff)
    assert image.save(str(path))
    repository.add_image(find.id, str(path))
    owner = QDialog()
    widget = StudyFindReviewWidget(repository, compact=True)
    QVBoxLayout(owner).addWidget(widget)
    owner.open()
    app.processEvents()
    before = connection.total_changes
    for close_with_escape in (True, False):
        widget.open_selected_image()
        app.processEvents()
        viewer = widget.full_size_viewer
        assert viewer.parentWidget() is owner
        assert app.activeModalWidget() is viewer
        assert viewer.findChild(QScrollArea).widget().pixmap().size() == image.size()
        if close_with_escape:
            QTest.keyClick(viewer, Qt.Key.Key_Escape)
        else:
            viewer.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Close).click()
        app.processEvents()
        assert widget.full_size_viewer is None
        assert owner.isVisible()
        assert app.activeModalWidget() is owner
        assert widget.observation_view.toPlainText() == find.observation
    assert connection.total_changes == before
    owner.reject()
    widget.close()
    connection.close()
