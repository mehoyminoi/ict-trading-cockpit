from datetime import date
from PySide6.QtGui import QImage, QColor
from ict_cockpit.analysis.study_find import StudyFind
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.study_investigation_repository import StudyInvestigationRepository
from ict_cockpit.database.study_review_repository import StudyReviewRepository
from ict_cockpit.gui.study_investigation_overview import StudyInvestigationOverview
from test_study_criterion import study
from test_study_investigation_repository import context
from test_study_review_checkpoint import review


def test_reading_context_images_and_checkpoint_browsing(study, tmp_path):
    c, amdx, criteria, original, definition = study
    finds, links = StudyFindRepository(c), StudyInvestigationRepository(c)
    find = StudyFind(observation_date=date(2026,10,9), instrument='MNQ', session='London',
                     pattern_name='<b>Literal pattern</b>', observation='A repeated chart structure', notes='HTF narrative')
    finds.save(find)
    image = QImage(80, 40, QImage.Format.Format_RGB32)
    image.fill(QColor('gray'))
    path = tmp_path / 'chart.png'
    image.save(str(path))
    finds.add_image(find.id, str(path))
    links.link(find.id, **context())
    reviews = StudyReviewRepository(c)
    reviews.save(review())
    reviews.save(review(id='other', task_id='other'))
    before = c.total_changes
    dialog = StudyInvestigationOverview(links, criteria, finds, task_id='task', plan_id='plan', question='Question')
    assert len(dialog.entries) == 2
    assert 'Literal pattern' in dialog.items.item(0).text()
    assert 'A repeated chart structure' in dialog.items.item(0).text()
    reader = dialog.find_review
    assert reader.details_label.isHidden()
    assert '<b>Literal pattern</b>' in reader.capture_heading.text()
    assert reader.image_list.currentRow() == 0
    assert not reader.image_preview.pixmap().isNull()
    assert reader.open_image_button.isEnabled()
    reader.provenance_toggle.click()
    assert not reader.details_label.isHidden()
    assert context()['question'] in reader.details_label.text()
    dialog.material_filter.setCurrentIndex(4)
    assert dialog.entries[dialog.items.currentRow()][0] == 'review'
    assert 'What was knowable then?' in dialog.detail.toPlainText()
    assert dialog.review_panel.isHidden()
    dialog.review_toggle.click()
    dialog.review_panel.fields['understanding'].setPlainText('New reflection stays separate')
    dialog.use_selected_support()
    assert dialog.review_panel.sources == []
    assert 'reflection' in dialog.review_panel.status.text()
    dialog.material_filter.setCurrentIndex(1)
    assert dialog.review_panel.fields['understanding'].toPlainText() == 'New reflection stays separate'
    assert reader.observation_view.toPlainText() == find.observation
    assert c.total_changes == before
    dialog.review_panel.fields['understanding'].clear()
    dialog.reject()
