from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox
from ict_cockpit.gui.study_investigation_overview import StudyInvestigationOverview
from ict_cockpit.database.study_review_repository import StudyReviewRepository
from test_study_home import cockpit


def test_entry_routes_preserve_work_and_do_not_write(cockpit, monkeypatch):
    window, connection = cockpit
    window.study_find_widget.notes_input.setPlainText('Unfinished chart narrative')
    draft = window.study_find_widget.build_draft()
    task = window.integrated_study_task.task_id
    reference = window.amdx_catalog_widget.reference()
    tab = window.tabs.currentWidget()
    window.study_find_draft_save_timer.stop()  # Exclude unrelated delayed capture autosave.
    changes = connection.total_changes
    routes = []

    def inspect(dialog):
        dialog.show()
        QApplication.processEvents()
        opened = dialog.review_toggle.isChecked()
        routes.append(opened)
        assert dialog.review_panel.isVisible() == opened
        assert dialog.review_panel.scope['task_id'] == task
        if opened:
            assert dialog.review_toggle.text() == 'Hide review entry'
            assert dialog.focusWidget() is dialog.review_panel.fields['understanding']
        dialog.reject()

    monkeypatch.setattr(StudyInvestigationOverview, 'exec', inspect)
    window.integrated_study_task.overview_button.click()
    window.integrated_study_task.checkpoint_button.click()
    # Native keyboard button activation must use the same direct route.
    QTest.keyClick(window.integrated_study_task.checkpoint_button, Qt.Key_Space)
    window.integrated_study_task.overview_button.click()
    assert routes == [False, True, True, False]
    assert window.study_find_widget.build_draft() == draft
    assert window.integrated_study_task.task_id == task
    assert window.amdx_catalog_widget.reference() == reference
    assert window.tabs.currentWidget() is tab
    assert connection.total_changes == changes


def test_hidden_review_keeps_text_and_close_guard_then_saves_same_scope(cockpit, monkeypatch):
    window, connection = cockpit

    def inspect(dialog):
        panel = dialog.review_panel
        panel.fields['uncertainty'].setPlainText('Retain this unresolved thought')
        dialog.review_toggle.click()
        assert panel.isHidden()
        assert dialog.review_toggle.text() == 'Review this investigation…'
        finished = []
        dialog.finished.connect(finished.append)
        monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Cancel)
        dialog.reject()
        assert not finished
        dialog.review_toggle.click()
        assert panel.fields['uncertainty'].toPlainText() == 'Retain this unresolved thought'
        panel.save()
        assert panel.saved
        dialog.accept()
        assert finished

    monkeypatch.setattr(StudyInvestigationOverview, 'exec', inspect)
    window.integrated_study_task.checkpoint_button.click()
    records = StudyReviewRepository(connection).list_for_task(
        window.trade_plan.id, window.integrated_study_task.task_id)
    assert len(records) == 1
    assert records[0]['uncertainty'] == 'Retain this unresolved thought'
    assert records[0]['question'] == window.integrated_study_task.question.text()
