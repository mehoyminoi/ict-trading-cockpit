import sqlite3
from PySide6.QtWidgets import QMessageBox
from test_study_home import cockpit
from ict_cockpit.database.study_question_repository import StudyQuestionRepository


def fill(window):
    w=window.study_find_widget
    w.instrument_input.setText('MNQ');w.session_input.setText('London')
    w.pattern_input.setText('Draft pattern');w.observation_input.setPlainText('Keep unless confirmed')
    return w


def test_cancel_and_failure_preserve_draft(cockpit,monkeypatch):
    window,c=cockpit;w=fill(window)
    before=w.build_draft()
    monkeypatch.setattr(QMessageBox,'question',lambda *a: QMessageBox.StandardButton.Cancel)
    window.discard_study_draft_button.click()
    assert w.build_draft()==before
    monkeypatch.setattr(QMessageBox,'question',lambda *a: QMessageBox.StandardButton.Discard)
    def fail(identity): raise sqlite3.OperationalError('disk unavailable')
    monkeypatch.setattr(window.study_find_repository,'delete_draft',fail)
    window.discard_study_draft_button.click()
    assert w.build_draft()==before
    assert 'not discarded' in w.save_feedback.text()
    assert window.study_find_draft_save_timer.isActive()


def test_discard_removes_only_current_draft_and_cannot_autosave_old_identity(cockpit,monkeypatch,tmp_path):
    window,c=cockpit;w=fill(window)
    window.integrated_study_task.question.setText('Current investigation')
    window._open_investigation_capture()
    window.link_investigation_button.click()
    original=w.build_draft();old_id=original.id
    w.notes_input.setPlainText('Question to retain?');w.notes_input.selectAll()
    window.keep_study_question_button.click()
    queued=StudyQuestionRepository(c).list_for_plan(window.trade_plan.id)
    path=tmp_path/'chart.png';path.write_bytes(b'keep source asset')
    w.image_paths.append(str(path));w.emit_draft_changed()
    window.save_pending_study_find_draft()
    w.observation_input.setPlainText('Latest pending text')
    assert window.pending_study_find_draft.id==old_id
    monkeypatch.setattr(QMessageBox,'question',lambda *a: QMessageBox.StandardButton.Discard)
    window.discard_study_draft_button.click()
    assert w.current_study_find_id!=old_id
    assert w.pattern_input.text()=='' and w.observation_input.toPlainText()==''
    assert w.notes_input.toPlainText()=='' and w.image_paths==[]
    assert w.instrument_input.text()=='MNQ' and w.session_input.text()=='London'
    assert w.build_draft().observation_date==original.observation_date
    window.save_pending_study_find_draft()
    assert not c.execute('SELECT id FROM study_find_draft WHERE id=?',(old_id,)).fetchone()
    assert window.study_find_repository.get_latest_draft().id==w.current_study_find_id
    assert window.investigation_repository.get(old_id)
    assert StudyQuestionRepository(c).list_for_plan(window.trade_plan.id)==queued
    assert path.exists()


def test_saved_find_is_never_discarded(cockpit,monkeypatch):
    window,c=cockpit;w=fill(window)
    assert w.submit()
    identity=w.current_study_find_id
    def no_confirm(*args):raise AssertionError('Saved records must not offer discard')
    monkeypatch.setattr(QMessageBox,'question',no_confirm)
    window.discard_study_draft_button.click()
    assert window.study_find_repository.get_by_id(identity)
    assert w.current_study_find_id==identity
    assert 'saved' in w.save_feedback.text()
