from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import subprocess
import pytest
from PySide6.QtWidgets import QMessageBox
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_finding_repository import StudyFindingRepository
from ict_cockpit.database.study_question_repository import StudyQuestionRepository
from ict_cockpit.gui.study_finding_dialog import StudyFindingDialog
from ict_cockpit.gui.study_investigation_overview import StudyInvestigationOverview
from ict_cockpit.database.study_criterion_repository import StudyCriterionRepository
from test_study_question_inbox import source
from test_study_investigation_repository import context
from test_study_capture_context import select
from test_study_home import cockpit


def finding(**changes):
    return dict(version=1, id='finding', plan_id='plan', plan_revision='r1',
                finding='London supported my first interpretation; later price changed it.',
                kind='Finding', original_text='Original insight', source=source(), investigation=None,
                recorded_at=datetime.now(timezone.utc).isoformat(), **changes)


def test_retention_scoping_immutability_and_no_question_or_run_creation(tmp_path):
    path = tmp_path/'study.db'
    c = open_application_database(path)
    repo = StudyFindingRepository(c)
    standalone = finding()
    linked = {**standalone, 'id':'answer', 'kind':'Partial answer', 'investigation':context()}
    repo.save(standalone); repo.save(linked)
    before = c.total_changes
    assert repo.save(linked) == linked
    assert c.total_changes == before
    assert repo.list_for_task('plan', 'task') == (linked,)
    assert repo.list_for_task('other', 'task') == ()
    assert repo.list_for_task('plan', 'other') == ()
    with pytest.raises(ValueError): repo.save({**linked, 'finding':'changed'})
    for sql in ('DELETE FROM study_finding', "UPDATE study_finding SET task_id='other'",
                'INSERT OR REPLACE INTO study_finding SELECT * FROM study_finding'):
        with pytest.raises(sqlite3.IntegrityError): c.execute(sql)
        c.rollback()
    c.execute('BEGIN')
    with pytest.raises(RuntimeError): repo.save(linked)
    assert c.in_transaction
    c.rollback()
    assert StudyQuestionRepository(c).list_for_plan('plan') == ()
    assert c.execute('SELECT count(*) FROM trading_session_run').fetchone()[0] == 0
    c.close()
    c = open_application_database(path)
    assert StudyFindingRepository(c).get('answer') == linked
    c.close()


@pytest.mark.parametrize('changes', [
    {'finding':' '}, {'kind':'Verified answer'}, {'kind':'Partial answer'},
    {'investigation':{**context(), 'plan_id':'other'}},
    {'investigation':{**context(), 'market_reference':'2026-10-08T09:15'}},
    {'investigation':{**context(), 'question':''}},
])
def test_invalid_or_unassociated_partial_answers_do_not_write(tmp_path, changes):
    c = open_application_database(tmp_path/'study.db')
    before = c.total_changes
    with pytest.raises(ValueError): StudyFindingRepository(c).save({**finding(), **changes})
    assert c.total_changes == before
    c.close()


@pytest.mark.parametrize('failure', [False, True])
def test_actual_v49_migration_preserves_question_and_rolls_back(tmp_path, failure):
    code = subprocess.check_output(['git','show',
        '6908b14e258e8b323947f932dc2394564d93f689:src/ict_cockpit/database/schema.py'],
        cwd=Path(__file__).resolve().parents[1], text=True)
    old = {}; exec(compile(code, 'v49-schema', 'exec'), old)
    c = create_connection(tmp_path/'old.db')
    old['initialize_schema'](c)
    q = finding(); q['question'] = q.pop('finding')
    StudyQuestionRepository(c).save(q)
    before = c.execute('SELECT * FROM study_question').fetchall()
    if failure:
        c.set_authorizer(lambda action,a,b,*_: sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_PRAGMA and a == 'user_version' and b == '51' else sqlite3.SQLITE_OK)
        with pytest.raises(sqlite3.DatabaseError): initialize_schema(c)
        c.set_authorizer(None)
        assert c.execute('PRAGMA user_version').fetchone()[0] == 49
        assert not c.execute("SELECT name FROM sqlite_master WHERE name='study_finding'").fetchall()
    initialize_schema(c)
    assert c.execute('SELECT * FROM study_question').fetchall() == before
    assert StudyFindingRepository(c).list_for_plan('plan') == ()
    with pytest.raises(RuntimeError, match='Unsupported database schema version: 51'):
        old['initialize_schema'](c)
    c.close()


def test_dialog_explicit_link_retry_cancel_and_frozen_source(cockpit, monkeypatch):
    window, c = cockpit
    repo = StudyFindingRepository(c)
    snapshot, target = source(), context()
    d = StudyFindingDialog(repo, plan_id='plan', plan_revision='r1', source=snapshot,
                           original_text='An insight', destination=target)
    assert not d.associate.isChecked()
    d.kind.setCurrentText('Partial answer')
    d.save()
    assert not d.saved and 'explicit investigation' in d.status.text()
    monkeypatch.setattr(QMessageBox,'question',lambda *a: QMessageBox.StandardButton.Cancel)
    d.reject()
    assert d.text.toPlainText() == 'An insight'
    d.associate.setChecked(True)
    save = repo.save
    def fail(item): raise sqlite3.OperationalError('disk unavailable')
    monkeypatch.setattr(repo,'save',fail)
    d.save()
    assert not d.saved and 'not saved' in d.status.text()
    identity, stamp = d.pending_item['id'], d.pending_item['recorded_at']
    snapshot['notes'] = 'modified'; target['question'] = 'different'
    monkeypatch.setattr(repo,'save',save)
    d.save(); d.save()
    assert d.saved and len(repo.list_for_plan('plan')) == 1
    item = repo.get(identity)
    assert item['recorded_at'] == stamp
    assert item['source']['notes'] == 'Why NYAM?'
    assert item['investigation']['question'] == 'Where was manipulation?'
    d.reject()


def test_selected_capture_and_overview_preserve_work_and_associate_only_finding(cockpit, monkeypatch):
    window, c = cockpit
    pane = select(window)
    task = window.integrated_study_task
    task.question.setText('What changed after London?')
    task.capture_button.click()
    w = window.study_find_widget
    w.notes_input.setPlainText('A tentative insight, not a question.'); w.notes_input.selectAll()
    before = w.build_draft()
    reference, task_id = pane.reference(), task.task_id
    def save_and_return(d):
        assert d.text.toPlainText() == before.notes
        assert not d.associate.isChecked()
        assert d.destination['task_id'] == task_id
        d.kind.setCurrentText('Partial answer'); d.associate.setChecked(True)
        d.save(); assert d.saved; d.reject()
    monkeypatch.setattr(StudyFindingDialog, 'exec', save_and_return)
    window.keep_study_finding_button.click()
    assert w.build_draft() == before
    assert pane.reference() == reference and task.task_id == task_id
    assert window.investigation_repository.get(before.id) is None
    repo = StudyFindingRepository(c)
    item = repo.list_for_task(window.trade_plan.id, task_id)[0]
    assert item['original_text'] == before.notes
    assert item['source']['navigation_context']['market_reference'] == reference.isoformat()
    # Discard does not erase the retained interpretation or infer a saved capture link.
    monkeypatch.setattr(QMessageBox,'question',lambda *a: QMessageBox.StandardButton.Discard)
    window.discard_study_draft_button.click()
    assert repo.get(item['id']) == item
    before_changes = c.total_changes
    d = StudyInvestigationOverview(window.investigation_repository,
        StudyCriterionRepository(window.trading_session_run_repository.amdx),
        window.study_find_repository, task_id=task_id, plan_id=window.trade_plan.id,
        question=task.question.text())
    assert len(d.entries) == 1 and d.entries[0][0] == 'finding'
    assert 'Partial answer:' in d.detail.toPlainText()
    assert before.notes in d.detail.toPlainText()
    assert c.total_changes == before_changes
    d.reject()


def test_saved_capture_association_wins_over_unrelated_navigation(cockpit, monkeypatch):
    window, c = cockpit
    select(window)
    window.integrated_study_task.question.setText('Original investigation')
    window.integrated_study_task.capture_button.click()
    w = window.study_find_widget
    w.notes_input.setPlainText('Insight')
    window.link_investigation_action.trigger()
    linked = window.investigation_repository.get(w.current_study_find_id)
    window.pending_investigation_context = {**linked, 'task_id':'other', 'question':'Other investigation'}
    def inspect(d):
        assert d.destination == linked
        d.text.clear(); d.reject()
    monkeypatch.setattr(StudyFindingDialog, 'exec', inspect)
    window.keep_study_finding_button.click()
    assert StudyFindingRepository(c).list_for_plan(window.trade_plan.id) == ()


def test_overview_read_failure_is_visible_and_does_not_retry_or_write(cockpit, monkeypatch):
    window, c = cockpit
    before = c.total_changes
    def fail(*args): raise sqlite3.OperationalError('unavailable')
    monkeypatch.setattr(StudyFindingRepository, 'list_for_task', fail)
    d = StudyInvestigationOverview(window.investigation_repository,
        StudyCriterionRepository(window.trading_session_run_repository.amdx),
        window.study_find_repository, task_id='task', plan_id=window.trade_plan.id, question='Study')
    assert not d.entries
    assert 'could not be loaded' in d.summary.text()
    assert 'unavailable' in d.detail.toPlainText()
    assert c.total_changes == before
    d.reject()
