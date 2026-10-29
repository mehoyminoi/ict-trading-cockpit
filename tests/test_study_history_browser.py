import sqlite3
from ict_cockpit.database.study_question_repository import StudyQuestionRepository
from ict_cockpit.database.study_finding_repository import StudyFindingRepository
from ict_cockpit.database.study_review_repository import StudyReviewRepository
from ict_cockpit.gui.study_history_browser import StudyHistoryBrowser
from test_study_home import cockpit
from test_study_findings import finding
from test_study_review_checkpoint import review


def seed(c, plan):
    f={**finding(), 'plan_id':plan, 'id':'finding', 'finding':'London interpretation', 'plan_revision':'r1'}
    StudyFindingRepository(c).save(f)
    q={**f, 'id':'question', 'question':'Why did NYAM change?', 'recorded_at':'2026-10-29T10:00:00+00:00'}
    StudyQuestionRepository(c).save(q)
    StudyReviewRepository(c).save(review(id='review1',plan_id=plan,task_id='old-investigation',
        plan_revision='r0',question='Earlier question',uncertainty='London remains uncertain',
        recorded_at='2026-10-29T08:00:00-04:00'))
    StudyReviewRepository(c).save(review(id='review2',plan_id=plan,task_id='another-investigation',
        plan_revision='r2',question='Later question',next_step='Inspect news timing',
        recorded_at='2026-10-29T11:00:00+00:00'))
    StudyReviewRepository(c).save(review(id='foreign',plan_id='other-plan',uncertainty='Foreign private record'))


def test_history_spans_tasks_revisions_filters_and_is_read_only(cockpit):
    window,c=cockpit;plan=window.trade_plan.id;seed(c,plan)
    before=c.total_changes
    for _ in range(2):
        d=StudyHistoryBrowser(c,plan_id=plan)
        assert len(d.records)==4
        assert all(r['item']['plan_id']==plan for r in d.records)
        d.kind.setCurrentText('Review')
        assert len(d.visible_records)==2
        assert [r['item']['id'] for r in d.visible_records]==['review1','review2']
        d.search.setText('LONDON UNCERTAIN')
        assert len(d.visible_records)==1
        assert 'Earlier question' in d.detail.toPlainText()
        assert 'r0' in d.detail.toPlainText()
        d.search.setText('nothingmatches')
        assert not d.visible_records and 'No records match' in d.detail.toPlainText()
        d.clear_filters();assert len(d.visible_records)==4
        d.kind.setCurrentText('Question');assert 'Why did NYAM' in d.detail.toPlainText()
        d.reject()
    assert c.total_changes==before


def test_history_failure_is_not_reported_as_empty(cockpit,monkeypatch):
    window,c=cockpit
    def fail(*a):raise sqlite3.OperationalError('unavailable')
    monkeypatch.setattr(StudyReviewRepository,'list_for_plan',fail)
    d=StudyHistoryBrowser(c,plan_id=window.trade_plan.id)
    assert d.load_error and not d.records
    assert 'could not be loaded completely' in d.status.text()
    assert not d.search.isEnabled()
    d.reject()


def test_history_action_preserves_current_work(cockpit,monkeypatch):
    window,c=cockpit
    window.study_find_widget.notes_input.setPlainText('Keep my current draft')
    before=window.study_find_widget.build_draft()
    task=window.integrated_study_task.task_id
    question=window.integrated_study_task.question.text()
    reference=window.amdx_catalog_widget.reference()
    current_tab=window.tabs.currentWidget()
    changes=c.total_changes
    seen=[]
    def inspect(d):
        seen.append(True)
        d.search.setText('London')
        d.reject()
    monkeypatch.setattr(StudyHistoryBrowser,'exec',inspect)
    window.study_history_button.click();window.study_home_history_button.click()
    assert len(seen)==2
    assert window.study_find_widget.build_draft()==before
    assert window.integrated_study_task.task_id==task
    assert window.integrated_study_task.question.text()==question
    assert window.amdx_catalog_widget.reference()==reference
    assert window.tabs.currentWidget() is current_tab
    assert c.total_changes==changes
