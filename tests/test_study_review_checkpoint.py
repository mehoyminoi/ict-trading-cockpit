from datetime import date, datetime, timezone
from pathlib import Path
import sqlite3
import subprocess
import pytest
from PySide6.QtWidgets import QMessageBox
from ict_cockpit.analysis.study_find import StudyFind, StudyFindDraft
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.study_investigation_repository import StudyInvestigationRepository
from ict_cockpit.database.study_review_repository import StudyReviewRepository, describe_review
from ict_cockpit.gui.study_review_panel import StudyReviewPanel
from ict_cockpit.gui.study_investigation_overview import StudyInvestigationOverview
from test_study_home import cockpit
from test_study_criterion import study, record
from test_study_investigation_repository import context


def review(**updates):
    item=dict(version=1,id='review',plan_id='plan',plan_revision='r1',task_id='task',question='Original question',
        understanding='',uncertainty='What was knowable then?',next_step='',sources=[],
        recorded_at=datetime.now(timezone.utc).isoformat())
    return {**item, **updates}


def test_review_is_append_only_retry_safe_scoped_and_reopens(tmp_path):
    path=tmp_path/'review.db';c=open_application_database(path);r=StudyReviewRepository(c)
    one=review();r.save(one)
    changes=c.total_changes;r.save(one);assert c.total_changes==changes
    with pytest.raises(ValueError):r.save({**one,'uncertainty':'Changed'})
    two=review(id='later',understanding='Tentative understanding',next_step='Test a counterexample');r.save(two)
    assert len(r.list_for_task('plan','task'))==2
    assert r.list_for_task('other','task')==()
    assert r.list_for_task('plan','other')==()
    for sql in ('DELETE FROM study_review',"UPDATE study_review SET task_id='other'",'INSERT OR REPLACE INTO study_review SELECT * FROM study_review'):
        with pytest.raises(sqlite3.IntegrityError):c.execute(sql)
        c.rollback()
    c.execute('BEGIN')
    with pytest.raises(RuntimeError):r.save(two)
    assert c.in_transaction;c.rollback()
    assert c.execute('SELECT count(*) FROM competency_evidence').fetchone()[0]==0
    assert c.execute('SELECT count(*) FROM trading_session_run').fetchone()[0]==0
    c.close();c=open_application_database(path)
    assert StudyReviewRepository(c).get('review')==one;c.close()


def test_source_scope_drafts_and_frozen_capture_basis(tmp_path):
    c=open_application_database(tmp_path/'review.db');r=StudyReviewRepository(c)
    finds=StudyFindRepository(c);links=StudyInvestigationRepository(c)
    draft=StudyFindDraft(observation_date=date(2026,10,9),notes='Unsaved')
    finds.save_draft(draft);links.link(draft.id,**context())
    with pytest.raises(ValueError,match='Save the linked'):r.source('capture',draft.id,'plan','task')
    saved=StudyFind(observation_date=date(2026,10,9),instrument='MNQ',session='London',pattern_name='Test',observation='Original PA')
    finds.save(saved);links.link(saved.id,**context())
    with pytest.raises(ValueError,match='another investigation'):r.source('capture',saved.id,'plan','other')
    source=r.source('capture',saved.id,'plan','task')
    r.save(review(sources=[source]))
    finds.add_image(saved.id,'later.png')
    assert r.get('review')['sources']==[source]
    assert 'Original PA' in describe_review(r.get('review'))
    with pytest.raises(ValueError,match='changed'):r.save(review(id='stale',sources=[source]))
    assert r.get('stale') is None
    c.close()


def test_criterion_source_and_finding_source_are_explicit(study):
    from ict_cockpit.database.study_finding_repository import StudyFindingRepository
    from test_study_findings import finding
    c,amdx,criteria,original,d=study
    saved=record(original,d);criteria.save(saved)
    r=StudyReviewRepository(c)
    criterion=r.source('result',saved.evaluation.id,'plan','task')
    f={**finding(),'investigation':context()};StudyFindingRepository(c).save(f)
    fs=r.source('finding',f['id'],'plan','task')
    r.save(review(sources=[criterion,fs]))
    assert 'Criterion' in describe_review(r.get('review'))
    assert f['finding'] in describe_review(r.get('review'))


@pytest.mark.parametrize('injected',[False,True])
def test_actual_v50_upgrade_preserves_existing_rows_and_rolls_back(tmp_path,injected):
    code=subprocess.check_output(['git','show','c36c5916d832ecf4a692345cd6827d7e2f4c0215:src/ict_cockpit/database/schema.py'],text=True,cwd=Path(__file__).resolve().parents[1])
    old={};exec(compile(code,'old-schema','exec'),old)
    c=create_connection(tmp_path/'old.db');old['initialize_schema'](c)
    tables=[row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    before={t:c.execute('SELECT * FROM '+t).fetchall() for t in tables}
    if injected:
        c.set_authorizer(lambda action,a,b,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_PRAGMA and a=='user_version' and b=='52' else sqlite3.SQLITE_OK)
        with pytest.raises(sqlite3.DatabaseError):initialize_schema(c)
        c.set_authorizer(None)
        assert c.execute('PRAGMA user_version').fetchone()[0]==50
        assert not c.execute("SELECT name FROM sqlite_master WHERE name='study_review'").fetchall()
    initialize_schema(c)
    assert {t:c.execute('SELECT * FROM '+t).fetchall() for t in tables}==before
    with pytest.raises(RuntimeError,match='Unsupported database schema version: 52'):old['initialize_schema'](c)
    c.close()


def test_optional_prompts_failure_cancel_and_later_checkpoint(cockpit,monkeypatch):
    window,c=cockpit;r=StudyReviewRepository(c)
    p=StudyReviewPanel(r,plan_id='plan',plan_revision='r1',task_id='task',question='Question')
    p.save();assert 'at least one thought' in p.status.text()
    p.fields['uncertainty'].setPlainText('Only an open question so far')
    monkeypatch.setattr(QMessageBox,'question',lambda *a:QMessageBox.StandardButton.Cancel)
    assert not p.can_leave()
    save=r.save
    def fail(item):raise sqlite3.OperationalError('disk unavailable')
    monkeypatch.setattr(r,'save',fail);p.save()
    assert not p.saved and p.fields['uncertainty'].toPlainText()
    stamp=p.pending['recorded_at']
    monkeypatch.setattr(r,'save',save);p.save();p.save()
    assert len(r.list_for_task('plan','task'))==1
    assert r.list_for_task('plan','task')[0]['recorded_at']==stamp
    p.start_new();p.fields['understanding'].setPlainText('Tentative insight');p.fields['next_step'].setPlainText('Study next day');p.save()
    assert len(r.list_for_task('plan','task'))==2
    assert p.can_leave()


def test_overview_review_close_guard_and_support_snapshot(study,monkeypatch):
    from PySide6.QtWidgets import QApplication
    app=QApplication.instance() or QApplication([])
    c,amdx,criteria,original,d=study;criteria.save(record(original,d))
    dialog=StudyInvestigationOverview(StudyInvestigationRepository(c),criteria,StudyFindRepository(c),
        task_id='task',plan_id='plan',plan_revision='r1',question='Question')
    dialog.review_toggle.click();dialog.use_selected_support()
    assert len(dialog.review_panel.sources)==1
    dialog.review_panel.fields['uncertainty'].setPlainText('Unresolved')
    monkeypatch.setattr(QMessageBox,'question',lambda *a:QMessageBox.StandardButton.Cancel)
    closed=[];dialog.finished.connect(closed.append)
    dialog.reject();assert not closed
    dialog.review_panel.save();dialog.accept();assert closed
    item=StudyReviewRepository(c).list_for_task('plan','task')[0]
    assert item['sources'][0]['id']==record(original,d).evaluation.id
