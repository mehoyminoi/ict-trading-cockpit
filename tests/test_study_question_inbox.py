import sqlite3
from datetime import datetime, timezone
import pytest
from PySide6.QtWidgets import QApplication, QMessageBox
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_question_repository import StudyQuestionRepository
from ict_cockpit.gui.study_question_dialog import StudyQuestionDialog
from test_study_home import cockpit


def source():
    return dict(capture_id='capture', state='Unfinished capture', date='2026-10-08',
                instrument='MNQ', session='London', pattern='Study', observation='Original PA',
                notes='Why NYAM?', images=[], association=None)


def test_question_snapshot_reopens_and_does_not_require_or_create_run(tmp_path):
    path=tmp_path/'study.db'
    c=open_application_database(path)
    repo=StudyQuestionRepository(c)
    item=dict(version=1,id='question',plan_id='plan',plan_revision='r1',question='Refined question?',
              original_text='Why NYAM?',source=source(),recorded_at=datetime.now(timezone.utc).isoformat())
    repo.save(item)
    before=c.total_changes
    assert repo.save(item)==item
    assert c.total_changes==before
    assert repo.list_for_plan('other')==()
    with pytest.raises(ValueError):repo.save({**item,'question':'Changed'})
    for sql in ('DELETE FROM study_question', 'UPDATE study_question SET plan_id=\'other\'',
                'INSERT OR REPLACE INTO study_question SELECT * FROM study_question'):
        with pytest.raises(sqlite3.IntegrityError):c.execute(sql)
        c.rollback()
    c.execute('BEGIN')
    with pytest.raises(RuntimeError):repo.save(item)
    c.rollback()
    assert c.execute('SELECT count(*) FROM trading_session_run').fetchone()[0]==0
    c.close()
    c=open_application_database(path)
    assert StudyQuestionRepository(c).get('question')==item
    c.close()


def test_migration_rolls_back_then_upgrades_without_backfill(tmp_path):
    c=open_application_database(tmp_path/'migration.db')
    c.execute('DROP TABLE study_review')
    c.execute('DROP TABLE study_finding')
    c.execute('DROP TABLE study_question')
    c.execute('PRAGMA user_version=48');c.commit()
    c.set_authorizer(lambda action,a,b,*_: sqlite3.SQLITE_DENY
        if action==sqlite3.SQLITE_PRAGMA and a=='user_version' and b=='51' else sqlite3.SQLITE_OK)
    with pytest.raises(sqlite3.DatabaseError):initialize_schema(c)
    c.set_authorizer(None)
    assert c.execute('PRAGMA user_version').fetchone()[0]==48
    assert not c.execute("SELECT name FROM sqlite_master WHERE name='study_question'").fetchone()
    initialize_schema(c)
    assert c.execute('PRAGMA user_version').fetchone()[0]==51
    assert StudyQuestionRepository(c).list_for_plan('plan')==()
    c.close()


def test_ui_refinement_failure_and_cancel_preserve_source(cockpit, monkeypatch):
    window,c=cockpit
    repo=StudyQuestionRepository(c)
    snapshot=source()
    d=StudyQuestionDialog(repo,plan_id='plan',plan_revision='r1',source=snapshot,original_text='Why NYAM?')
    d.question.setPlainText('What changed in NYAM?')
    monkeypatch.setattr(QMessageBox,'question',lambda *a: QMessageBox.StandardButton.Cancel)
    d.reject()
    assert d.question.toPlainText()=='What changed in NYAM?'
    original=repo.save
    def fail(item):raise sqlite3.OperationalError('disk unavailable')
    monkeypatch.setattr(repo,'save',fail)
    d.save('r1')
    assert not d.saved and 'not saved' in d.status.text()
    monkeypatch.setattr(repo,'save',original)
    snapshot['notes']='later mutation'
    d.save('r1')
    assert d.saved
    item=repo.list_for_plan('plan')[0]
    assert item['original_text']=='Why NYAM?'
    assert item['source']['notes']=='Why NYAM?'
    assert item['question']=='What changed in NYAM?'
    d.reject()
    reopened=StudyQuestionDialog(repo,plan_id='plan',plan_revision='r2')
    assert 'What changed in NYAM?' in reopened.detail.toPlainText()
    reopened.reject()


def test_capture_action_preserves_work_and_reads_explicit_association_only(cockpit,monkeypatch):
    window,c=cockpit
    widget=window.study_find_widget
    widget.notes_input.setPlainText('Why did NYAM change the interpretation?')
    widget.notes_input.selectAll()
    before=widget.build_draft()
    task_id=window.integrated_study_task.task_id
    original_question=window.integrated_study_task.question.text()
    def no_dialog(d):
        raise AssertionError('Selected wording should save without opening a dialog')
    monkeypatch.setattr(StudyQuestionDialog,'exec',no_dialog)
    window.keep_study_question_button.click()
    assert widget.build_draft()==before
    assert window.integrated_study_task.task_id==task_id
    assert window.integrated_study_task.question.text()==original_question
    assert len(StudyQuestionRepository(c).list_for_plan(window.trade_plan.id))==1


def test_quick_capture_uses_latest_selection_retries_and_does_not_duplicate(cockpit, monkeypatch):
    window,c=cockpit
    w=window.study_find_widget
    w.notes_input.setPlainText('Older selection');w.notes_input.selectAll()
    w.observation_input.setPlainText('Newer selected question?');w.observation_input.selectAll()
    save=StudyQuestionRepository.save
    def fail(*args): raise sqlite3.OperationalError('disk unavailable')
    monkeypatch.setattr(StudyQuestionRepository,'save',fail)
    window.keep_study_question_button.click()
    assert 'not saved' in window.question_capture_feedback.text()
    assert w.observation_input.textCursor().selectedText()=='Newer selected question?'
    monkeypatch.setattr(StudyQuestionRepository,'save',save)
    window.keep_study_question_button.click()
    window.keep_study_question_button.click()
    records=StudyQuestionRepository(c).list_for_plan(window.trade_plan.id)
    assert len(records)==1
    assert records[0]['original_text']=='Newer selected question?'
    assert 'Question kept' in window.question_capture_feedback.text()


def test_no_selection_opens_optional_composer_without_saving(cockpit,monkeypatch):
    window,c=cockpit
    seen=[]
    def inspect(d):
        seen.append(d.source)
        assert d.original_text==''
        d.reject()
    monkeypatch.setattr(StudyQuestionDialog,'exec',inspect)
    window.keep_study_question_button.click()
    assert seen and seen[0]['capture_id']==window.study_find_widget.current_study_find_id
    assert StudyQuestionRepository(c).list_for_plan(window.trade_plan.id)==()
