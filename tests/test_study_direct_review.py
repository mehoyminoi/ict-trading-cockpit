from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox
from ict_cockpit.database.study_review_repository import StudyReviewRepository
from test_study_home import cockpit


def test_entry_routes_preserve_work_and_do_not_write(cockpit):
    window, connection = cockpit
    window.show()
    window.study_find_widget.notes_input.setPlainText('Unfinished chart narrative')
    draft = window.study_find_widget.build_draft()
    task = window.integrated_study_task.task_id
    reference = window.amdx_catalog_widget.reference()
    window.study_find_draft_save_timer.stop()
    changes = connection.total_changes
    window.integrated_study_task.overview_button.click()
    content = window.investigation_content
    assert window.tabs.currentWidget() is window.investigation_material_page
    assert not content.review_toggle.isChecked()
    window.integrated_study_task.checkpoint_button.click()
    QApplication.processEvents()
    assert window.investigation_content is content
    assert content.review_panel.isVisible()
    assert content.review_panel.scope['task_id'] == task
    QTest.keyClick(window.integrated_study_task.checkpoint_button, Qt.Key_Space)
    assert content.review_toggle.isChecked()
    content.return_requested.emit()
    assert window.tabs.currentWidget() is window.amdx_catalog_widget
    assert window.study_find_widget.build_draft() == draft
    assert window.integrated_study_task.task_id == task
    assert window.amdx_catalog_widget.reference() == reference
    assert connection.total_changes == changes


def test_hidden_review_keeps_text_and_close_guard_then_saves_same_scope(cockpit, monkeypatch):
    window, connection = cockpit
    window.integrated_study_task.checkpoint_button.click()
    content = window.investigation_content
    panel = content.review_panel
    panel.fields['uncertainty'].setPlainText('Retain this unresolved thought')
    content.review_toggle.click()
    assert panel.isHidden()
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Cancel)
    content.return_requested.emit()
    assert window.tabs.currentWidget() is window.investigation_material_page
    content.review_toggle.click()
    assert panel.fields['uncertainty'].toPlainText() == 'Retain this unresolved thought'
    panel.save()
    assert panel.saved
    assert any(kind == 'review' for kind, _ in content.entries)
    content.return_requested.emit()
    assert window.tabs.currentWidget() is window.amdx_catalog_widget
    records = StudyReviewRepository(connection).list_for_task(
        window.trade_plan.id, window.integrated_study_task.task_id)
    assert len(records) == 1
    assert records[0]['uncertainty'] == 'Retain this unresolved thought'
    assert records[0]['question'] == window.integrated_study_task.question.text()
