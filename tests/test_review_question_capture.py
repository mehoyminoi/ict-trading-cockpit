import sqlite3
import subprocess
import pytest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QMessageBox
from ict_cockpit.database.study_review_repository import StudyReviewRepository
from ict_cockpit.database.study_question_repository import StudyQuestionRepository
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.gui.study_review_panel import StudyReviewPanel
from ict_cockpit.gui.study_question_dialog import StudyQuestionDialog
from ict_cockpit.gui.study_history_browser import StudyHistoryBrowser
from test_study_home import cockpit


def panel(window, c):
    return StudyReviewPanel(StudyReviewRepository(c), plan_id=window.trade_plan.id,
        plan_revision=window.trade_plan.revision, task_id='task', question='Current inquiry')


def select(editor, text):
    editor.setPlainText(text)
    cursor = editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    editor.setTextCursor(cursor)


def test_selected_review_question_retains_snapshot_without_saving_review(cockpit, monkeypatch):
    window,c = cockpit;p = panel(window,c)
    select(p.fields['uncertainty'], 'Why did London reverse?')
    p.keep_question_button.click();p.keep_question_button.click()
    questions = StudyQuestionRepository(c).list_for_plan(window.trade_plan.id)
    assert len(questions) == 1
    item = questions[0]
    assert item['version'] == 2
    assert item['source']['state'] == 'Draft review snapshot'
    assert item['source']['selected_field'] == 'uncertainty'
    assert item['source']['task_id'] == 'task'
    assert 'capture_id' not in item['source']
    assert not p.repository.list_for_task(window.trade_plan.id, 'task')
    assert not p.saved
    p.fields['uncertainty'].setPlainText('Changed later')
    assert StudyQuestionRepository(c).get(item['id']) == item
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Cancel)
    assert not p.can_leave()
    browser = StudyHistoryBrowser(c,plan_id=window.trade_plan.id)
    browser.kind.setCurrentText('Question')
    assert 'Draft review snapshot' in browser.detail.toPlainText()
    inbox = StudyQuestionDialog(StudyQuestionRepository(c),plan_id=window.trade_plan.id,plan_revision=window.trade_plan.revision)
    assert 'Current inquiry' in inbox.detail.toPlainText()


def test_latest_selection_retry_and_saved_review_source(cockpit, monkeypatch):
    window,c = cockpit;p=panel(window,c)
    select(p.fields['understanding'], 'First selected question')
    select(p.fields['next_step'], 'Second selected question')
    original = StudyQuestionRepository.save
    def fail(*a):raise sqlite3.OperationalError('unavailable')
    monkeypatch.setattr(StudyQuestionRepository,'save',fail)
    p.keep_question_button.click()
    pending = p._pending_question.copy()
    assert 'not saved' in p.question_feedback.text()
    monkeypatch.setattr(StudyQuestionRepository,'save',original)
    p.keep_question_button.click()
    assert StudyQuestionRepository(c).get(pending['id']) == pending
    p.save()
    # Select retained text in the now-read-only saved editor.
    editor=p.fields['next_step'];cursor=editor.textCursor();cursor.select(QTextCursor.SelectionType.Document);editor.setTextCursor(cursor)
    p.keep_question_button.click()
    item=StudyQuestionRepository(c).list_for_plan(window.trade_plan.id)[0]
    assert item['source']['state']=='Saved review snapshot'
    assert item['source']['review_id']==p.identity


def test_no_selection_uses_existing_composer_and_does_not_save_review(cockpit, monkeypatch):
    window,c=cockpit;p=panel(window,c)
    p.fields['next_step'].setPlainText('Consider profiles')
    def compose(dialog):
        assert dialog.source['kind']=='review'
        dialog.question.setPlainText('Which profile should I study?')
        dialog.save(window.trade_plan.revision)
    monkeypatch.setattr(StudyQuestionDialog,'exec',compose)
    p.keep_question_button.click()
    assert len(StudyQuestionRepository(c).list_for_plan(window.trade_plan.id))==1
    assert not p.saved
    assert p.fields['next_step'].toPlainText()=='Consider profiles'


def test_actual_v52_reader_barrier_and_rollback(tmp_path):
    namespace={}
    exec(subprocess.check_output(['git','show','590e31c:src/ict_cockpit/database/schema.py'],text=True),namespace)
    c=sqlite3.connect(tmp_path/'migration.db');namespace['initialize_schema'](c)
    c.execute("INSERT INTO study_question VALUES ('q','p','{}')");c.commit()
    c.set_authorizer(lambda action,a,b,*_: sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_PRAGMA and a=='user_version' and b=='53' else sqlite3.SQLITE_OK)
    with pytest.raises(sqlite3.DatabaseError):initialize_schema(c)
    c.set_authorizer(None)
    assert c.execute('PRAGMA user_version').fetchone()[0]==52
    initialize_schema(c)
    assert c.execute('SELECT * FROM study_question').fetchall()==[('q','p','{}')]
    with pytest.raises(RuntimeError):namespace['initialize_schema'](c)
    c.close()
