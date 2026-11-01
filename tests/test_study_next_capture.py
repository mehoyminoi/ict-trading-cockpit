from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDialog
from test_study_home import cockpit
from test_study_save_to_investigation import prepare


def test_plain_save_starts_clean_context_and_last_saved_review_preserves_next_draft(cockpit, monkeypatch):
    window,c = cockpit
    w = prepare(window)
    original = w.build_draft()
    w.save_button.click()
    fresh = w.build_draft()
    assert fresh.id != original.id
    assert (fresh.observation_date, fresh.instrument, fresh.session) == (original.observation_date, original.instrument, original.session)
    assert not fresh.observation and not fresh.notes and not fresh.pattern_name and not fresh.image_paths
    assert window.investigation_repository.get(original.id) is None
    assert window.pending_investigation_context['task_id'] == window.integrated_study_task.task_id
    w.notes_input.setPlainText('Next observation underway')
    before = w.build_draft()
    seen=[]
    def inspect(dialog):
        from ict_cockpit.gui.study_find_review_widget import StudyFindReviewWidget
        review=dialog.findChild(StudyFindReviewWidget)
        assert review.study_finds[0].id == original.id
        seen.append(True)
        dialog.accept()
    monkeypatch.setattr(QDialog,'exec',inspect)
    window.view_last_saved_button.click()
    assert seen and w.build_draft() == before


def test_link_only_does_not_clear_and_untouched_next_capture_follows_new_selection(cockpit):
    window,c = cockpit
    w = prepare(window)
    before = w.build_draft()
    window.link_investigation_action.trigger()
    assert w.build_draft() == before
    window.save_to_investigation_button.click()
    fresh_id=w.current_study_find_id
    pane=window.amdx_catalog_widget
    window.tabs.setCurrentWidget(pane)
    pane.date_input.setDate(QDate(2026,10,9))
    window.integrated_study_task.capture_button.click()
    assert w.current_study_find_id == fresh_id
    assert w.date_input.date() == QDate(2026,10,9)
    w.notes_input.setPlainText('Do not move this draft')
    window.tabs.setCurrentWidget(pane)
    pane.date_input.setDate(QDate(2026,10,10))
    window.integrated_study_task.capture_button.click()
    assert w.date_input.date() == QDate(2026,10,9)
    assert w.notes_input.toPlainText() == 'Do not move this draft'
