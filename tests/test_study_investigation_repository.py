from datetime import date
import sqlite3
import pytest
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.study_investigation_repository import StudyInvestigationRepository
from ict_cockpit.analysis.study_find import StudyFindDraft


def context():
    return dict(task_id='task', plan_id='plan', plan_revision='Alpha 0.7',
        question='Where was manipulation?', instrument='MNQ',
        market_reference='2026-10-09T09:15:00-04:00', interpretation='Observed')


def test_link_retains_snapshot_rejects_reassignment_and_sql_replacement(tmp_path):
    db = tmp_path / 'study.db'
    c = open_application_database(db)
    draft = StudyFindDraft(observation_date=date(2026,10,9), pattern_name='Existing draft')
    StudyFindRepository(c).save_draft(draft)
    repo = StudyInvestigationRepository(c)
    saved = repo.link(draft.id, **context())
    assert repo.link(draft.id, **context()) == saved
    assert saved['recorded_at'] != saved['market_reference']
    with pytest.raises(ValueError, match='reassigned'):
        repo.link(draft.id, **{**context(), 'question':'Changed question'})
    for sql in ['UPDATE study_investigation_capture SET question=\'changed\'',
                'DELETE FROM study_investigation_capture',
                'INSERT OR REPLACE INTO study_investigation_capture SELECT * FROM study_investigation_capture']:
        with pytest.raises(sqlite3.IntegrityError):
            c.execute(sql)
        c.rollback()
    c.close()
    c = open_application_database(db)
    assert StudyInvestigationRepository(c).get(draft.id) == saved
    c.close()


def test_missing_capture_and_naive_reference_do_not_write(tmp_path):
    c = open_application_database(tmp_path/'study.db')
    repo = StudyInvestigationRepository(c)
    before = c.total_changes
    with pytest.raises(ValueError, match='content'):
        repo.link('missing', **context())
    with pytest.raises(ValueError, match='timezone'):
        repo.link('missing', **{**context(), 'market_reference':'2026-10-09T09:15'})
    assert c.total_changes == before
    c.close()


@pytest.mark.parametrize("injected", [False, True])
def test_v46_upgrade_retains_capture_and_has_no_inferred_links(tmp_path, injected):
    c = open_application_database(tmp_path/'old.db')
    draft = StudyFindDraft(observation_date=date(2026,10,9), pattern_name='Pre-migration draft')
    StudyFindRepository(c).save_draft(draft)
    c.execute('DROP TABLE study_review')
    c.execute('DROP TABLE study_finding')
    c.execute('DROP TABLE study_question')
    c.execute('DROP TABLE study_criterion_evaluation')
    c.execute('DROP TABLE study_investigation_capture')
    c.execute('PRAGMA user_version=46')
    c.commit()
    if injected:
        c.set_authorizer(lambda action,*_: sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_CREATE_TRIGGER else sqlite3.SQLITE_OK)
        with pytest.raises(sqlite3.DatabaseError):
            initialize_schema(c)
        c.set_authorizer(None)
        assert c.execute('PRAGMA user_version').fetchone()[0] == 46
        assert not c.execute("SELECT name FROM sqlite_master WHERE name='study_investigation_capture'").fetchall()
        assert StudyFindRepository(c).get_latest_draft().pattern_name == 'Pre-migration draft'
    initialize_schema(c)
    assert c.execute('PRAGMA user_version').fetchone()[0] == 51
    assert StudyFindRepository(c).get_latest_draft().pattern_name == 'Pre-migration draft'
    assert c.execute('SELECT count(*) FROM study_investigation_capture').fetchone()[0] == 0
    initialize_schema(c)
    c.close()
