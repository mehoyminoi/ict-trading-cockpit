from dataclasses import replace
from datetime import timedelta
import json
import sqlite3

import pytest

from ict_cockpit.analysis.amdx import Role, XSubtype
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate
from ict_cockpit.database.amdx_run_observed_repository import read_run_observed_archive
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from test_amdx_run_calendar_repository import store, launch, REFERENCE, RECORDED


def prepare(repo, run, level='session', position=3, reference=REFERENCE):
    return repo.run_observed.prepare(run.id, reference=reference, level=level, position=position)


def revise(repo, prepared, id='review', **kwargs):
    args=dict(operation_id=id, recorded_at=RECORDED+timedelta(minutes=5), role=Role.M,
        anchor_id=id+'-anchor', source_ref='synthetic Review assessment')
    args.update(kwargs)
    return repo.run_observed.revise(prepared, **args)


def count(connection):
    return tuple(connection.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for name in
        ('amdx_catalog_command','amdx_run_observed_command','amdx_claim','amdx_comparison','amdx_run_capture'))


def test_shared_observed_entry_captures_exact_assessment_without_duplicate_quartet_or_expected_baseline(store):
    connection,repo,run,_,_=store
    _,initial=launch(repo,run)
    prepared=prepare(repo,run)
    before=count(connection)
    result=revise(repo,prepared)
    assert result.changed
    row=next(r for r in result.projection.cycles if r.context.cycle.layer=='session')
    assert row.claim.inference.candidates[0].value=='XAMD'
    assert count(connection)==(before[0]+1,before[1]+1,before[2],before[3],before[4])
    assert repo.run_calendar.get_result('launch')==initial
    assert all(r.claim is None for r in repo.master.load_stack('MNQ',reference=REFERENCE).projection.cycles)
    assert repo.run_observed.latest(run.id)==result
    assert read_run_observed_archive(repo.run_observed.export_archive(run.id))==(result,)


def test_lab_correction_does_not_rewrite_receipt_and_next_assessment_uses_visible_current_calendar(store):
    connection,repo,run,_,_=store
    launch(repo,run)
    original=revise(repo,prepare(repo,run))
    target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='session',position=3,channel='Observed')
    repo.catalog.revise(target.target,command_id='lab',recorded_at=RECORDED+timedelta(minutes=6),
        role=Role.D,anchor_id='lab-anchor',source_ref='Lab correction')
    assert repo.run_observed.get_result('review')==original
    prepared=prepare(repo,run,position=4)
    after=revise(repo,prepared,id='review-after',role=Role.X,subtype=XSubtype.REVERSAL,
        recorded_at=RECORDED+timedelta(minutes=7))
    row=next(r for r in after.projection.cycles if r.context.cycle.layer=='session')
    assert row.inference.candidates[0].value=='AMDX'
    assert row.inference.roles[3].subtype is XSubtype.REVERSAL
    assert repo.run_observed.get_result('review')==original
    assert len(read_run_observed_archive(repo.run_observed.export_archive(run.id)))==2


@pytest.mark.parametrize('table',['amdx_catalog_command','amdx_run_observed_command'])
def test_failure_rolls_back_both_calendar_and_run_receipt(store,table):
    connection,repo,run,_,_=store
    launch(repo,run)
    prepared=prepare(repo,run)
    before=count(connection)
    connection.execute(f"CREATE TRIGGER injected BEFORE INSERT ON {table} BEGIN SELECT RAISE(ABORT,'injected'); END")
    with pytest.raises(sqlite3.IntegrityError,match='injected'):
        revise(repo,prepared)
    assert count(connection)==before
    assert repo.run_observed.latest(run.id) is None


@pytest.mark.parametrize('what',['selected-head','other-head','run','parent'])
def test_stale_inspected_basis_rejects_without_writes(store,what):
    connection,repo,run,_,_=store
    launch(repo,run)
    prepared=prepare(repo,run)
    if what.endswith('head'):
        target=repo.master.prepare_target('MNQ',reference=REFERENCE,
            level='session' if what=='selected-head' else 'year',position=3,channel='Observed')
        repo.catalog.revise(target.target,command_id='outside',recorded_at=RECORDED,
            role=Role.D,anchor_id='out-a',source_ref='outside')
    elif what=='run':
        run.review_takeaway='changed by another writer'
        TradingSessionRunRepository(connection).save(run)
    else:
        revise(repo,prepared,id='first',role=None,anchor_id=None,source_ref='')
    before=count(connection)
    with pytest.raises(StaleAMDXUpdate):
        revise(repo,prepared)
    assert count(connection)==before


def test_exact_retry_is_original_after_source_metadata_and_resolver_changes(store,monkeypatch):
    connection,repo,run,_,_=store
    launch(repo,run)
    prepared=prepare(repo,run)
    original=revise(repo,prepared)
    revise(repo,prepare(repo,run),id='later',role=Role.D,recorded_at=RECORDED+timedelta(minutes=6))
    run.market_context_snapshot={'reference_market_time':'later malformed source'}
    TradingSessionRunRepository(connection).save(run)
    def changed(*args,**kwargs):
        raise AssertionError('Original retry/archive must not use current resolver')
    monkeypatch.setattr('ict_cockpit.analysis.amdx_context.resolve_stack_cycles',changed)
    assert revise(repo,prepared)==original
    assert len(read_run_observed_archive(repo.run_observed.export_archive(run.id)))==2
    with pytest.raises(ValueError,match='identity cannot'):
        revise(repo,prepared,role=Role.D)


@pytest.mark.parametrize('kind',['empty-clear','same-entry','unknown','not-applicable','clear-applicability'])
def test_noops_uncertainty_and_applicability_are_retained_not_invented(store,kind):
    connection,repo,run,_,_=store
    launch(repo,run)
    args={}
    if kind in ('same-entry','clear-applicability'):
        revise(repo,prepare(repo,run),id='first',role=Role.M if kind=='same-entry' else Role.NOT_APPLICABLE)
    if kind in ('empty-clear','clear-applicability'):
        args=dict(role=None,anchor_id=None,source_ref='',clear_applicability=kind=='clear-applicability')
    elif kind=='unknown':
        args=dict(role=Role.UNKNOWN)
    elif kind=='not-applicable':
        args=dict(role=Role.NOT_APPLICABLE)
    result=revise(repo,prepare(repo,run),**args)
    assert result.changed==(kind not in ('empty-clear','same-entry'))
    assert repo.run_observed.latest(run.id)==result
    assert read_run_observed_archive(repo.run_observed.export_archive(run.id))[-1]==result


@pytest.mark.parametrize('position',[1,2,3,4])
def test_all_review_sessions_resolve_their_selected_occurrence_with_original_day_guard(store,position):
    _,repo,run,_,_=store
    launch(repo,run)
    day=repo.master.load_stack('MNQ',reference=REFERENCE,channel='Observed').projection.cycles[-2].context.cycle
    reference=day.quarters[position-1].start
    result=revise(repo,prepare(repo,run,reference=reference))
    assert result.projection.reference==reference


def test_legacy_unknown_next_day_and_higher_nonoriginal_reference_reject(store):
    connection,repo,run,legacy,_=store
    launch(repo,run)
    before=count(connection)
    with pytest.raises(ValueError,match='legacy ownership'):
        prepare(repo,legacy)
    with pytest.raises(ValueError,match='outside'):
        prepare(repo,run,reference=REFERENCE+timedelta(days=1))
    with pytest.raises(ValueError,match='limited to the original'):
        prepare(repo,run,level='year',reference=REFERENCE+timedelta(minutes=1))
    result=revise(repo,prepare(repo,run,level='year'),role=Role.D)
    assert result.changed and count(connection)[1]==before[1]+1


def test_concluded_run_can_be_assessed_without_reopening_or_replacing_launch(store):
    connection,repo,run,_,_=store
    _,initial=launch(repo,run)
    run.conclude('Review')
    TradingSessionRunRepository(connection).save(run)
    original=connection.execute('SELECT * FROM trading_session_run WHERE id=?',(run.id,)).fetchone()
    result=revise(repo,prepare(repo,run))
    assert result.changed
    assert connection.execute('SELECT * FROM trading_session_run WHERE id=?',(run.id,)).fetchone()==original
    assert repo.run_calendar.get_result('launch')==initial


@pytest.mark.parametrize('operation',['UPDATE amdx_run_observed_command SET payload_json=payload_json',
    'DELETE FROM amdx_run_observed_command',
    'INSERT OR REPLACE INTO amdx_run_observed_command SELECT * FROM amdx_run_observed_command'])
def test_assessment_sql_update_delete_and_replace_reject(store,operation):
    connection,repo,run,_,_=store
    launch(repo,run)
    result=revise(repo,prepare(repo,run))
    with pytest.raises(sqlite3.IntegrityError,match='immutable'):
        connection.execute(operation)
    assert repo.run_observed.latest(run.id)==result


@pytest.mark.parametrize('field',['run_id','parent_id','projection','command'])
def test_standalone_archive_rejects_changed_ownership_basis_or_transcript(store,field):
    _,repo,run,_,_=store
    launch(repo,run)
    revise(repo,prepare(repo,run))
    archive=repo.run_observed.export_archive(run.id)
    command=archive['commands'][0]
    if field=='run_id': archive['run_id']='different-run'
    elif field=='parent_id': command['request']['basis']['parent_id']='missing-parent'
    elif field=='projection': command['result']['projection']['cycles'][-1]['claim']=None
    else: command['result']['calendar_command']['request']['anchor']['role']='D'
    with pytest.raises(ValueError): read_run_observed_archive(archive)


def test_caller_transaction_is_preserved_and_not_committed_or_rolled_back(store):
    connection,repo,run,_,_=store
    launch(repo,run)
    prepared=prepare(repo,run)
    connection.execute('BEGIN')
    connection.execute("UPDATE trading_session_run SET review_takeaway='pending unrelated work' WHERE id=?",(run.id,))
    with pytest.raises(RuntimeError,match='pending transaction'):
        revise(repo,prepared)
    assert connection.in_transaction
    assert connection.execute('SELECT review_takeaway FROM trading_session_run WHERE id=?',(run.id,)).fetchone()[0]=='pending unrelated work'
    connection.rollback()


def test_two_connections_cannot_both_commit_the_same_inspected_observed_basis(store):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from ict_cockpit.database.bootstrap import open_application_database
    from ict_cockpit.database.amdx_repository import AMDXRepository
    connection,repo,run,_,path=store
    launch(repo,run)
    barrier=Barrier(2)
    def writer(id):
        c=open_application_database(path)
        r=AMDXRepository(c)
        try:
            prepared=prepare(r,run)
            barrier.wait(timeout=10)
            try:
                revise(r,prepared,id=id)
                return 'committed'
            except StaleAMDXUpdate:
                return 'stale'
        finally:
            c.close()
    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(writer,['one','two']))==['committed','stale']
    assert count(connection)[:2]==(1,1)


def test_portable_archive_keeps_declared_definition_evidence_and_unknown_asof(store):
    from ict_cockpit.analysis.amdx_catalog import CaptureBasis
    _,repo,run,_,_=store
    launch(repo,run)
    capture=CaptureBasis(kind='HistoricalEntry',evidence_ref='synthetic chart',definition_ref='candidate:r1')
    original=revise(repo,prepare(repo,run),capture=capture)
    archived=repo.run_observed.export_archive(run.id)
    assert archived['commands'][0]['request']['calendar_request']['capture']=={
        'kind':'HistoricalEntry','information_available_at':None,'evidence_ref':'synthetic chart','definition_ref':'candidate:r1'}
    assert read_run_observed_archive(archived)==(original,)
