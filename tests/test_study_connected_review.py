from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox
from test_study_home import cockpit


def test_cancel_preserves_review_across_local_global_switch_and_close(cockpit, monkeypatch):
    window, connection = cockpit
    window.show()
    task = window.integrated_study_task
    task.question.setText('Narrative across sessions')
    task.checkpoint_button.click()
    content = window.investigation_content
    panel = content.review_panel
    QTest.keyClicks(panel.fields['understanding'], 'Keep this thought')
    identity = panel.identity
    scope = dict(panel.scope)
    changes = connection.total_changes
    observed = []
    window.tabs.navigation_changed.connect(observed.append)
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Cancel)
    window.study_workspace.selector.setCurrentIndex(1)
    assert window.study_workspace.selector.currentIndex() == 3
    bar = window.tabs.tabBar()
    QTest.mouseClick(bar, Qt.MouseButton.LeftButton, pos=bar.tabRect(0).center())
    assert window.tabs.current_surface() is window.study_workspace
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    assert window.tabs.current_surface() is window.study_workspace
    task.new_task_button.click()
    assert task.task_id == scope['task_id']
    window._open_investigation_capture()
    assert window.tabs.currentWidget() is window.investigation_material_page
    assert not window.close()
    assert window.isVisible()
    assert not observed
    assert window.investigation_content is content
    assert panel.identity == identity and panel.scope == scope
    assert panel.fields['understanding'].toPlainText() == 'Keep this thought'
    assert connection.total_changes == changes
    # Explicit discard permits leaving; re-entry cannot resurrect discarded text.
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Discard)
    window.study_workspace.selector.setCurrentIndex(1)
    assert window.tabs.currentWidget() is window.amdx_catalog_widget
    task.checkpoint_button.click()
    assert not window.investigation_content.review_panel.fields['understanding'].toPlainText()


def test_saved_review_refresh_return_and_question_switch(cockpit):
    window, connection = cockpit
    task = window.integrated_study_task
    task.question.setText('First investigation')
    task.checkpoint_button.click()
    content = window.investigation_content
    panel = content.review_panel
    panel.fields['understanding'].setPlainText('Tentative answer')
    panel.save()
    identity = panel.identity
    assert panel.fields['understanding'].isReadOnly()
    assert any(kind == 'review' and record['id'] == identity for kind, record in content.entries)
    task.new_task_button.click()
    task.question.setText('Second investigation')
    task.checkpoint_button.click()
    assert window.investigation_content.review_panel.scope['question'] == 'Second investigation'
    assert not window.investigation_content.entries
    assert connection.execute('SELECT count(*) FROM study_review').fetchone()[0] == 1


def test_embedded_chart_escape_and_support_cancel(cockpit, tmp_path, monkeypatch):
    from datetime import date
    from PySide6.QtGui import QImage, QColor
    from ict_cockpit.analysis.study_find import StudyFind
    window, connection = cockpit
    task = window.integrated_study_task
    task.question.setText('Chart context')
    find = StudyFind(observation_date=date(2026, 10, 9), instrument='MNQ', session='London',
                     pattern_name='Example', observation='Retained price action')
    window.study_find_repository.save(find)
    image = QImage(80, 40, QImage.Format.Format_RGB32)
    image.fill(QColor('gray'))
    path = tmp_path / 'chart.png'
    image.save(str(path))
    window.study_find_repository.add_image(find.id, str(path))
    window.investigation_repository.link(find.id, task_id=task.task_id, plan_id=window.trade_plan.id,
        plan_revision=window.trade_plan.revision, question=task.question.text(), instrument='MNQ',
        market_reference='2026-10-09T09:15:00-04:00', interpretation='Observed')
    window.show()
    task.checkpoint_button.click()
    content = window.investigation_content
    content.use_selected_support()
    sources = list(content.review_panel.sources)
    assert len(sources) == 1
    reader = content.find_review
    reader.open_image_button.click()
    QApplication.processEvents()
    viewer = reader.full_size_viewer
    assert viewer.parentWidget() is window and viewer.isVisible()
    QTest.keyClick(viewer, Qt.Key.Key_Escape)
    assert reader.full_size_viewer is None
    assert window.tabs.currentWidget() is window.investigation_material_page
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Cancel)
    task.resume_button.click()
    assert window.investigation_content is content
    assert content.review_panel.sources == sources
    assert content.items.currentRow() == 0
    # Save failure preserves the same working review; retry does not duplicate it.
    import sqlite3
    repo = content.review_panel.repository
    save = repo.save
    content.review_panel.fields['understanding'].setPlainText('Image supports this thought')
    def fail(item):
        raise sqlite3.OperationalError('storage unavailable')
    monkeypatch.setattr(repo, 'save', fail)
    content.review_panel.save()
    assert not content.review_panel.saved
    assert content.review_panel.sources == sources
    monkeypatch.setattr(repo, 'save', save)
    content.review_panel.save()
    assert content.review_panel.saved
    assert len(repo.list_for_task(window.trade_plan.id, task.task_id)) == 1
