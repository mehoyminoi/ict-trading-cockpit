from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from test_study_home import cockpit


def test_connected_navigation_keeps_editor_undo_and_destination(cockpit):
    window, c = cockpit
    work = window.study_workspace
    task = window.integrated_study_task
    task.question.setText('Study continuity')
    window._open_investigation_capture()
    editor = window.study_find_widget.observation_input
    QTest.keyClicks(editor, 'Retained words')
    window.save_pending_study_find_draft()
    draft = window.study_find_widget.build_draft()
    target = window._study_save_target()
    identity = task.task_id
    changes = c.total_changes
    assert window.tabs.current_surface() is work
    for index in (0, 1, 2):
        work.selector.setCurrentIndex(index)
        assert window.tabs.current_surface() is work
        assert window.tabs.currentWidget() is work.pages[index]
        assert task.task_id == identity
        assert window.study_find_widget.build_draft() == draft
        assert window._study_save_target() == target
    assert c.total_changes == changes
    assert editor.document().isUndoAvailable()
    editor.undo()
    assert editor.toPlainText() != 'Retained words'
    editor.redo()
    assert editor.toPlainText() == 'Retained words'
    assert window.current_feedback_context()[0] == 'Study · Capture / current draft'


def test_header_reference_does_not_retarget_capture_and_global_exit(cockpit):
    window, c = cockpit
    window.integrated_study_task.question.setText('Reference distinction')
    window._open_investigation_capture()
    window.study_find_widget.notes_input.setPlainText('Keep reference')
    window.save_pending_study_find_draft()
    target = window._study_save_target()
    calendar = window.amdx_catalog_widget
    window.study_workspace.selector.setCurrentIndex(1)
    calendar.date_input.setDate(calendar.date_input.date().addDays(1))
    assert calendar.reference().isoformat() in window.study_workspace.reference.text()
    window.study_workspace.selector.setCurrentIndex(2)
    assert window._study_save_target() == target
    assert 'Capture retains its own destination' in window.study_workspace.reference.text()
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    assert window.tabs.current_surface() is window.trade_plan_widget
    window.tabs.setCurrentWidget(window.study_find_widget)
    assert window.tabs.current_surface() is window.study_workspace
    assert window._study_save_target() == target
    labels = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    assert labels.count('Study') == 1
    assert 'AMDX Lab' not in labels and 'Study Find' not in labels
