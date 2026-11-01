from PySide6.QtWidgets import QInputDialog
from test_study_home import cockpit
from test_study_criterion import study, record
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.study_investigation_repository import StudyInvestigationRepository
from ict_cockpit.gui.study_investigation_overview import StudyInvestigationOverview


def test_blocked_switch_routes_to_exact_draft_without_rebinding(cockpit, monkeypatch):
    window, c = cockpit
    task = window.integrated_study_task
    task.question.setText('Retained question')
    window._open_investigation_capture()
    source = window.study_find_widget
    source.observation_input.setPlainText('Meaningful unfinished observation')
    window.save_pending_study_find_draft()
    draft, target, identity = source.build_draft(), window._study_save_target(), task.task_id
    reference = window.amdx_catalog_widget.reference()
    window.tabs.setCurrentWidget(window.amdx_catalog_widget)
    changes = c.total_changes
    monkeypatch.setattr(QInputDialog, 'getItem', lambda *a: (_ for _ in ()).throw(AssertionError('Blocked selector opened')))
    for button in (task.new_task_button, task.resume_button):
        button.click()
        assert not task.switch_notice.isHidden()
        assert task.task_id == identity
        task.return_to_draft_button.click()
        assert window.tabs.currentWidget() is source
        assert source.build_draft() == draft
        assert window._study_save_target() == target
        assert window.amdx_catalog_widget.reference() == reference
        assert c.total_changes == changes
        window.investigation_return_buttons[0].click()
    source.observation_input.clear()
    window.tabs.setCurrentWidget(source)
    window.investigation_return_buttons[0].click()
    assert task.switch_notice.isHidden()
    task.new_task_button.click()
    assert task.task_id != identity
    assert task.switch_notice.isHidden()


def test_support_disclosure_preserves_question_and_capture(cockpit):
    window, c = cockpit
    task = window.integrated_study_task
    draft = window.study_find_widget.build_draft()
    identity = task.task_id
    changes = c.total_changes
    assert task.supporting_tools.isHidden()
    task.tools_toggle.click()
    assert not task.supporting_tools.isHidden()
    assert task.library_actions.indexOf(window.study_questions_button) >= 0
    task.tools_toggle.click()
    assert task.supporting_tools.isHidden()
    assert task.task_id == identity
    assert window.study_find_widget.build_draft() == draft
    assert c.total_changes == changes


def test_filter_does_not_change_support_or_unsaved_review(study):
    c, amdx, criteria, original, definition = study
    criteria.save(record(original, definition))
    dialog = StudyInvestigationOverview(StudyInvestigationRepository(c), criteria, StudyFindRepository(c),
        task_id='task', plan_id='plan', question='Question', review_open=True)
    panel = dialog.review_panel
    panel.fields['understanding'].setPlainText('An emerging thread')
    dialog.use_selected_support()
    support = list(panel.sources)
    before = c.total_changes
    dialog.material_filter.setCurrentIndex(1)  # No captures, but retained result exists.
    assert dialog.items.currentRow() == -1
    assert 'No material of this type' in dialog.detail.toPlainText()
    dialog.use_selected_support()
    assert panel.sources == support
    dialog.material_filter.setCurrentIndex(3)
    assert dialog.items.currentRow() == 0
    assert panel.fields['understanding'].toPlainText() == 'An emerging thread'
    assert panel.sources == support
    assert c.total_changes == before
    panel.fields['understanding'].clear()
    panel.sources.clear()
    dialog.reject()
