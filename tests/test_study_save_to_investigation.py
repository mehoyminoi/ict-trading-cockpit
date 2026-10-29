from dataclasses import replace
from datetime import date
import sqlite3
import pytest
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox
from ict_cockpit.analysis.study_find import StudyFind, StudyFindDraft
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.study_investigation_repository import StudyInvestigationRepository
from test_study_investigation_repository import context
from test_study_capture_context import select
from test_study_home import cockpit


def capture():
    return StudyFind(observation_date=date(2026,10,9), instrument='MNQ', session='London',
                     pattern_name='Test', observation='Original observation', image_path='first.png')


@pytest.mark.parametrize('table,event', [
    ('study_find', 'INSERT'), ('study_find_image', 'INSERT'),
    ('study_investigation_capture', 'INSERT'), ('study_find_draft', 'DELETE'),
])
def test_every_write_failure_rolls_back_content_images_link_and_draft(tmp_path, table, event):
    c = open_application_database(tmp_path/'study.db')
    repo, links = StudyFindRepository(c), StudyInvestigationRepository(c)
    saved = capture()
    draft = StudyFindDraft(id=saved.id, observation_date=saved.observation_date,
                          notes='Unfinished original', image_paths=['first.png','second.png'])
    repo.save_draft(draft)
    c.execute(f"CREATE TRIGGER inject_failure BEFORE {event} ON {table} "
              "BEGIN SELECT RAISE(ABORT, 'injected failure'); END")
    with pytest.raises(sqlite3.IntegrityError):
        repo.save_capture(saved, draft.image_paths, investigation=context())
    assert repo.get_by_id(saved.id) is None
    assert repo.get_images(saved.id) == []
    assert links.get(saved.id) is None
    assert repo.get_latest_draft() == draft
    assert not c.in_transaction
    c.execute('DROP TRIGGER inject_failure')
    repo.save_capture(saved, draft.image_paths, investigation=context())
    assert repo.get_by_id(saved.id) == saved
    assert repo.get_images(saved.id) == draft.image_paths
    assert repo.get_latest_draft() is None
    assert links.get(saved.id)['task_id'] == 'task'
    c.close()
    c = open_application_database(tmp_path/'study.db')
    assert StudyFindRepository(c).get_by_id(saved.id) == saved
    assert StudyInvestigationRepository(c).get(saved.id)['question'] == context()['question']
    c.close()


def test_existing_association_cannot_be_reassigned_and_external_transaction_not_committed(tmp_path):
    c = open_application_database(tmp_path/'study.db')
    repo, links = StudyFindRepository(c), StudyInvestigationRepository(c)
    saved = capture()
    draft = StudyFindDraft(id=saved.id, observation_date=saved.observation_date, notes='Retain')
    repo.save_draft(draft)
    original = links.link(saved.id, **context())
    with pytest.raises(ValueError, match='reassigned'):
        repo.save_capture(saved, ['first.png'], investigation={**context(), 'task_id':'other'})
    assert repo.get_by_id(saved.id) is None and repo.get_latest_draft() == draft
    assert links.get(saved.id) == original
    c.execute('BEGIN')
    with pytest.raises(RuntimeError): repo.save_capture(saved, [], investigation=context())
    assert c.in_transaction
    c.rollback()
    repo.save_capture(saved, ['first.png'], investigation=context())
    assert links.get(saved.id) == original
    with pytest.raises(sqlite3.IntegrityError): repo.save_capture(saved, ['first.png'], investigation=context())
    assert repo.get_images(saved.id) == ['first.png']
    c.close()


def prepare(window):
    select(window)
    window.integrated_study_task.question.setText('Study the London interpretation')
    window.integrated_study_task.capture_button.click()
    w = window.study_find_widget
    w.pattern_input.setText('Test pattern')
    w.observation_input.setPlainText('Observed price')
    return w


def test_one_action_saves_capture_and_link_and_clears_pending_autosave(cockpit):
    window,c = cockpit
    w = prepare(window)
    identity = w.current_study_find_id
    assert window.investigation_repository.get(identity) is None
    assert 'Study the London interpretation' in window.study_save_destination.text()
    window.save_to_investigation_button.click()
    assert window.study_find_repository.get_by_id(identity)
    assert window.investigation_repository.get(identity)['task_id'] == window.integrated_study_task.task_id
    assert 'saved to investigation' in w.save_feedback.text()
    assert not w.save_button.isEnabled() and not window.save_to_investigation_button.isEnabled()
    assert window.pending_study_find_draft is None
    assert not window.study_find_draft_save_timer.isActive()
    window.save_pending_study_find_draft()
    assert window.study_find_repository.get_latest_draft() is None


def test_plain_save_does_not_create_an_association(cockpit):
    window,c = cockpit
    w = prepare(window)
    identity = w.current_study_find_id
    w.save_button.click()
    assert window.study_find_repository.get_by_id(identity)
    assert window.investigation_repository.get(identity) is None


def test_mismatch_cancel_retains_input_and_explicit_save_keeps_both_contexts(cockpit, monkeypatch):
    window,c = cockpit
    w = prepare(window)
    w.date_input.setDate(QDate(2026,10,7))
    before = w.build_draft()
    seen = []
    def cancel(*args):
        seen.append(args[2]); assert args[-1] == QMessageBox.StandardButton.Cancel
        return QMessageBox.StandardButton.Cancel
    monkeypatch.setattr(QMessageBox,'question',cancel)
    window.save_to_investigation_button.click()
    assert 'capture 2026-10-07 / destination 2026-10-08' in seen[0]
    assert w.build_draft() == before
    assert window.study_find_repository.get_by_id(before.id) is None
    assert window.investigation_repository.get(before.id) is None
    monkeypatch.setattr(QMessageBox,'question',lambda *a: QMessageBox.StandardButton.Save)
    window.save_to_investigation_button.click()
    assert window.study_find_repository.get_by_id(before.id).observation_date == date(2026,10,7)
    assert window.investigation_repository.get(before.id)['market_reference'].startswith('2026-10-08')


def test_failed_save_keeps_form_pending_draft_and_retry_available(cockpit, monkeypatch):
    window,c = cockpit
    w = prepare(window)
    before = w.build_draft()
    pending = window.pending_study_find_draft
    save = window.study_find_repository.save_capture
    def fail(*a,**kw): raise sqlite3.OperationalError('disk unavailable')
    monkeypatch.setattr(window.study_find_repository, 'save_capture', fail)
    window.save_to_investigation_button.click()
    assert w.build_draft() == before
    assert 'Not saved' in w.save_feedback.text()
    assert window.pending_study_find_draft == pending
    assert window.study_find_draft_save_timer.isActive()
    assert w.save_button.isEnabled()
    monkeypatch.setattr(window.study_find_repository, 'save_capture', save)
    window.save_to_investigation_button.click()
    assert not w.save_button.isEnabled()


def test_existing_destination_wins_and_modal_change_requires_another_review(cockpit, monkeypatch):
    window,c = cockpit
    w = prepare(window)
    window.link_investigation_action.trigger()
    original = window.investigation_repository.get(w.current_study_find_id)
    window.pending_investigation_context = {**window.pending_investigation_context,
                                            'task_id':'other', 'question':'Other investigation'}
    window._refresh_capture_association()
    assert 'Existing association (preserved)' in window.study_save_destination.text()
    assert 'Other investigation' not in window.study_save_destination.text()
    w.date_input.setDate(QDate(2026,10,7))
    def change(*args):
        w.notes_input.setPlainText('Changed while confirming')
        return QMessageBox.StandardButton.Save
    monkeypatch.setattr(QMessageBox,'question',change)
    window.save_to_investigation_button.click()
    assert 'changed while confirming' in w.save_feedback.text()
    assert window.study_find_repository.get_by_id(w.current_study_find_id) is None
    monkeypatch.setattr(QMessageBox,'question',lambda *a: QMessageBox.StandardButton.Save)
    window.save_to_investigation_button.click()
    assert window.investigation_repository.get(w.current_study_find_id) == original
