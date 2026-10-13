from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from threading import Barrier

import pytest

from ict_cockpit.analysis.amdx import Profile, Role
from ict_cockpit.analysis.amdx_catalog import CaptureBasis
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_session_run import RunEnvironment, RunPurpose, TradingRun
from ict_cockpit.database.amdx_repository import AMDXRepository, StaleAMDXUpdate
from ict_cockpit.database.amdx_run_calendar_repository import read_run_calendar_archive
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from test_amdx_repository import saved_run


REFERENCE=datetime(1985,8,12,9,15,tzinfo=MARKET_TIMEZONE)
RECORDED=datetime(2026,10,13,12,0,tzinfo=MARKET_TIMEZONE)
TABLES=('trading_session_run','amdx_catalog_command','amdx_run_binding','amdx_run_capture','amdx_run_calendar_command','amdx_cycle_identity')


@pytest.fixture
def store(tmp_path):
    path=tmp_path/'run-calendar.db'
    connection=open_application_database(path)
    legacy=saved_run(connection)
    repo=AMDXRepository(connection)
    repo.master.ensure('MNQ',recorded_at=RECORDED)
    run=TradingRun(legacy.trading_day_id,'Synthetic new launch',legacy.process_session_id)
    run.market_context_snapshot={'reference_market_time':REFERENCE.isoformat()}
    yield connection,repo,run,legacy,path
    connection.close()


def counts(connection):
    return tuple(connection.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0] for name in TABLES)


def launch(repo,run,id='launch',capture='launch-capture',reference=REFERENCE):
    prepared=repo.run_calendar.prepare_launch(run,instrument='MNQ',reference=reference)
    result=repo.run_calendar.launch(prepared,operation_id=id,capture_id=capture,recorded_at=RECORDED)
    return prepared,result


def edit(repo,run,id='edit',role=Role.D,reference=REFERENCE,extra=None):
    prepared=repo.run_calendar.prepare_capture(run.id,reference=reference)
    target=repo.master.prepare_target('MNQ',reference=reference,level='year',position=3)
    args=dict(operation_id=id,capture_id=id+'-capture',recorded_at=RECORDED+timedelta(minutes=1),
              role=role,anchor_id='a-'+id,source_ref='synthetic chart')
    args.update(extra or {})
    return prepared,target,args,repo.run_calendar.revise(prepared,target,**args)


def test_atomic_launch_preserves_absence_and_original_metadata_after_calendar_and_run_changes(store):
    connection,repo,run,legacy,_=store
    _,initial=launch(repo,run)
    original=initial.capture.packet
    assert len(initial.capture.projection.cycles)==7 and all(r.claim is None for r in initial.capture.projection.cycles)
    assert original['binding']['instrument']=='MNQ'
    assert original['run_context']['market_context_snapshot_json']==json.dumps(run.market_context_snapshot,sort_keys=True)
    assert original['unavailable_levels']==[]
    with pytest.raises(ValueError,match='legacy ownership is unknown'):
        repo.run_calendar.get_binding(legacy.id)
    _,_,_,updated=edit(repo,run)
    assert updated.calendar_result.changed
    assert next(r.claim for r in updated.capture.projection.cycles if r.context.cycle.layer=='year').inference.candidates==(Profile.AMDX,)
    assert repo.run_calendar.get_result('launch')==initial
    run.set_qt_context({'year':'X(R)'})
    run.market_context_snapshot={'reference_market_time':'different later metadata'}
    TradingSessionRunRepository(connection).save(run)
    assert repo.run_calendar.get_result('launch').capture.packet==original
    assert not connection.execute('PRAGMA foreign_key_check').fetchall()


def test_external_lab_correction_changes_current_heads_but_not_capture_then_explicit_context_use(store):
    _,repo,run,_,_=store
    launch(repo,run)
    _,_,_,first=edit(repo,run)
    target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=3)
    repo.catalog.revise(target.target,command_id='lab',recorded_at=RECORDED+timedelta(minutes=2),
                        role=Role.M,anchor_id='lab-a',source_ref='later correction')
    assert next(r.claim for r in first.capture.projection.cycles if r.context.cycle.layer=='year').id=='edit'
    assert next(r.claim for r in repo.master.load_stack('MNQ',reference=REFERENCE).projection.cycles if r.context.cycle.layer=='year').id=='lab'
    prepared=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
    adopted=repo.run_calendar.capture(prepared,operation_id='use',capture_id='use-capture',recorded_at=RECORDED+timedelta(minutes=3))
    assert next(r.claim for r in adopted.capture.projection.cycles if r.context.cycle.layer=='year').id=='lab'
    assert repo.run_calendar.get_result('edit')==first
    binding,history=read_run_calendar_archive(repo.run_calendar.export_archive(run.id))
    assert binding['run_id']==run.id and len(history)==3


@pytest.mark.parametrize('table',['amdx_run_binding','amdx_run_capture','amdx_run_calendar_command'])
def test_launch_failure_rolls_back_new_run_binding_and_capture(store,table):
    connection,repo,run,_,_=store
    prepared=repo.run_calendar.prepare_launch(run,instrument='MNQ',reference=REFERENCE)
    before=counts(connection)
    connection.execute(f"CREATE TRIGGER injected BEFORE INSERT ON {table} BEGIN SELECT RAISE(ABORT,'injected'); END")
    with pytest.raises(sqlite3.IntegrityError,match='injected'):
        repo.run_calendar.launch(prepared,operation_id='launch',capture_id='capture',recorded_at=RECORDED)
    assert counts(connection)==before
    assert TradingSessionRunRepository(connection).get_by_id(run.id) is None


@pytest.mark.parametrize('table',['amdx_run_capture','amdx_run_calendar_command'])
def test_edit_failure_rolls_back_phase_command_and_capture_as_one_operation(store,table):
    connection,repo,run,_,_=store
    launch(repo,run)
    prepared=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
    target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=3)
    before=counts(connection)
    connection.execute(f"CREATE TRIGGER injected BEFORE INSERT ON {table} BEGIN SELECT RAISE(ABORT,'injected'); END")
    with pytest.raises(sqlite3.IntegrityError,match='injected'):
        repo.run_calendar.revise(prepared,target,operation_id='edit',capture_id='capture',recorded_at=RECORDED,
            role=Role.D,anchor_id='a',source_ref='chart')
    assert counts(connection)==before
    assert all(r.claim is None for r in repo.master.load_stack('MNQ',reference=REFERENCE).projection.cycles)


def test_exact_launch_and_edit_retries_use_original_result_after_newer_data_and_resolver_change(store,monkeypatch):
    _,repo,run,_,_=store
    prepared,original=launch(repo,run)
    target_before,target,args,first=edit(repo,run)
    edit(repo,run,id='later',role=Role.M)
    repo.run_calendar.capture(repo.run_calendar.prepare_capture(run.id,reference=REFERENCE),
        operation_id='consume',capture_id='consume-capture',recorded_at=RECORDED+timedelta(minutes=4))
    def changed(*args,**kwargs):
        raise AssertionError('Old exact retry must not call current resolver')
    monkeypatch.setattr('ict_cockpit.analysis.amdx_context.resolve_stack_cycles',changed)
    assert repo.run_calendar.launch(prepared,operation_id='launch',capture_id='launch-capture',recorded_at=RECORDED)==original
    assert repo.run_calendar.revise(target_before,target,**args)==first
    assert read_run_calendar_archive(repo.run_calendar.export_archive(run.id))[1][0]==original


def test_drifted_launch_edit_and_cross_action_ids_reject_without_writes(store):
    connection,repo,run,_,_=store
    prepared,_=launch(repo,run)
    before=counts(connection)
    with pytest.raises(ValueError,match='identity cannot'):
        repo.run_calendar.launch(prepared,operation_id='launch',capture_id='different',recorded_at=RECORDED)
    capture=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
    with pytest.raises(ValueError,match='identity cannot'):
        repo.run_calendar.capture(capture,operation_id='launch',capture_id='another',recorded_at=RECORDED)
    with pytest.raises(ValueError,match='reserved'):
        repo.run_calendar.capture(capture,operation_id='new',capture_id='launch',recorded_at=RECORDED)
    assert counts(connection)==before


@pytest.mark.parametrize('what',['head','run','parent'])
def test_changed_prepared_basis_rejects_and_does_not_partially_save(store,what):
    connection,repo,run,_,_=store
    launch(repo,run)
    prepared=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
    if what=='head':
        target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=3)
        repo.catalog.revise(target.target,command_id='outside',recorded_at=RECORDED,role=Role.M,anchor_id='out',source_ref='other writer')
    elif what=='run':
        run.review_takeaway='changed after inspection'
        TradingSessionRunRepository(connection).save(run)
    else:
        repo.run_calendar.capture(prepared,operation_id='first',capture_id='first-capture',recorded_at=RECORDED)
    before=counts(connection)
    with pytest.raises(StaleAMDXUpdate):
        repo.run_calendar.capture(prepared,operation_id='stale',capture_id='stale-capture',recorded_at=RECORDED)
    assert counts(connection)==before


def test_stale_tda_basis_is_not_silently_replaced_at_launch(store):
    connection,repo,run,_,_=store
    tda=repo.master.load_stack('MNQ',reference=REFERENCE)
    prepared=repo.run_calendar.prepare_launch(run,instrument='MNQ',reference=REFERENCE,snapshot=tda)
    target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=3)
    repo.catalog.revise(target.target,command_id='outside',recorded_at=RECORDED,role=Role.D,anchor_id='a',source_ref='new thesis')
    before=counts(connection)
    with pytest.raises(StaleAMDXUpdate,match='master stack'):
        repo.run_calendar.launch(prepared,operation_id='launch',capture_id='capture',recorded_at=RECORDED)
    assert counts(connection)==before


@pytest.mark.parametrize('mode',['same-entry','empty-clear','unresolved-x'])
def test_noops_and_unresolved_x_keep_original_receipts_and_capture_basis(store,mode):
    _,repo,run,_,_=store
    launch(repo,run)
    if mode=='same-entry':
        edit(repo,run,id='first')
        _,_,_,result=edit(repo,run,id='same')
        assert not result.calendar_result.changed and result.calendar_result.claim.id=='first'
    else:
        prepared=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
        position=4 if mode=='unresolved-x' else 3
        target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=position)
        options=dict(role=Role.X,anchor_id='x',source_ref='chart') if mode=='unresolved-x' else {}
        result=repo.run_calendar.revise(prepared,target,operation_id='entry',capture_id='entry-capture',recorded_at=RECORDED,**options)
        if mode=='empty-clear':
            assert not result.calendar_result.changed and result.calendar_result.claim is None
        else:
            assert result.calendar_result.claim.anchors[0].subtype is None
    binding,results=read_run_calendar_archive(repo.run_calendar.export_archive(run.id))
    assert results[-1]==result and binding['instrument']=='MNQ'
    last=result.capture.packet['master']['ledger']['commands'][-1]
    assert last['request']['capture']['information_available_at'] is None


def test_closed_reference_keeps_unavailable_intraday_rows_and_higher_capture(store):
    _,repo,run,_,_=store
    run.market_context_snapshot={'reference_market_time':REFERENCE.replace(day=17).isoformat()}
    _,result=launch(repo,run,reference=REFERENCE.replace(day=17))
    assert len(result.capture.projection.cycles)==5
    assert result.capture.packet['unavailable_levels']==[{'level':'day','reason':'Closed'},{'level':'session','reason':'Closed'}]
    assert read_run_calendar_archive(repo.run_calendar.export_archive(run.id))[1][0]==result


@pytest.mark.parametrize('drift',['binding','channel','reference'])
def test_edit_target_drift_rejects_before_calendar_write(store,drift):
    connection,repo,run,_,_=store
    launch(repo,run)
    prepared=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
    target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=3)
    if drift=='binding':
        target=replace(target,binding=replace(target.binding,id='different'))
    else:
        target=replace(target,target=replace(target.target,**({'channel':'Observed'} if drift=='channel' else {'market_reference':REFERENCE+timedelta(days=1)})))
    before=counts(connection)
    with pytest.raises(ValueError):
        repo.run_calendar.revise(prepared,target,operation_id='bad',capture_id='bad-capture',recorded_at=RECORDED,
            role=Role.D,anchor_id='a',source_ref='chart')
    assert counts(connection)==before


def test_concluded_run_rejects_new_context_but_exact_retries_and_review_archives_work(store):
    connection,repo,run,_,_=store
    prepared,initial=launch(repo,run)
    run.conclude('Synthetic complete')
    TradingSessionRunRepository(connection).save(run)
    target=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
    with pytest.raises(ValueError,match='Concluded'):
        repo.run_calendar.capture(target,operation_id='late',capture_id='late-capture',recorded_at=RECORDED)
    assert repo.run_calendar.launch(prepared,operation_id='launch',capture_id='launch-capture',recorded_at=RECORDED)==initial
    assert read_run_calendar_archive(repo.run_calendar.export_archive(run.id))[1][0]==initial


@pytest.mark.parametrize('table',['amdx_run_binding','amdx_run_capture','amdx_run_calendar_command'])
@pytest.mark.parametrize('action',['UPDATE','DELETE','REPLACE'])
def test_sql_immutability_for_every_run_calendar_record(store,table,action):
    connection,repo,run,_,_=store
    launch(repo,run)
    column='run_id' if table=='amdx_run_binding' else 'id'
    sql=(f'UPDATE {table} SET {column}={column}' if action=='UPDATE' else f'DELETE FROM {table}' if action=='DELETE' else f'INSERT OR REPLACE INTO {table} SELECT * FROM {table}')
    with pytest.raises(sqlite3.IntegrityError,match='immutable'):
        connection.execute(sql)
    connection.rollback()
    assert len(read_run_calendar_archive(repo.run_calendar.export_archive(run.id))[1])==1


def test_caller_transaction_is_not_committed_and_archive_navigation_is_read_only(store):
    connection,repo,run,_,_=store
    prepared,_=launch(repo,run)
    before=counts(connection)
    connection.execute('BEGIN')
    with pytest.raises(RuntimeError,match='pending transaction'):
        repo.run_calendar.launch(prepared,operation_id='other',capture_id='other-capture',recorded_at=RECORDED)
    assert connection.in_transaction
    repo.run_calendar.export_archive(run.id)
    assert connection.in_transaction and counts(connection)==before
    connection.rollback()


def test_competing_context_consumers_and_exact_retries_use_one_parent_chain(store):
    connection,repo,run,_,path=store
    prepared,original=launch(repo,run)
    barrier=Barrier(2)
    def retry(_):
        own=open_application_database(path)
        try:
            barrier.wait(timeout=10)
            return AMDXRepository(own).run_calendar.launch(prepared,operation_id='launch',capture_id='launch-capture',recorded_at=RECORDED)
        finally:
            own.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(retry,range(2)))==[original,original]
    current=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
    barrier=Barrier(2)
    def use(id):
        own=open_application_database(path)
        try:
            barrier.wait(timeout=10)
            return AMDXRepository(own).run_calendar.capture(current,operation_id=id,capture_id=id+'-capture',recorded_at=RECORDED)
        except StaleAMDXUpdate:
            return None
        finally:
            own.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(use,('one','two')))
    assert sum(r is not None for r in results)==1
    assert connection.execute('SELECT COUNT(*) FROM amdx_run_capture WHERE run_id=?',(run.id,)).fetchone()[0]==2


def test_separate_process_reopen_and_standalone_archive_reconstruct_original_basis(store):
    _,repo,run,_,path=store
    launch(repo,run)
    edit(repo,run)
    archive=repo.run_calendar.export_archive(run.id)
    env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[1]/'src'))
    output=subprocess.check_output([sys.executable,'-c',
        'import sys,json; from pathlib import Path; from ict_cockpit.database.bootstrap import open_application_database; from ict_cockpit.database.amdx_repository import AMDXRepository; c=open_application_database(Path(sys.argv[1])); print(json.dumps(AMDXRepository(c).run_calendar.export_archive(sys.argv[2]))); c.close()',str(path),run.id],env=env,text=True)
    assert json.loads(output)==archive
    other=open_application_database(path)
    try:
        assert AMDXRepository(other).run_calendar.get_result('edit')==repo.run_calendar.get_result('edit')
    finally:
        other.close()
    binding,history=read_run_calendar_archive(json.loads(json.dumps(archive)))
    assert binding['run_id']==run.id and len(history)==2


@pytest.mark.parametrize('part',['absence','run-asset','parent','count','receipt','reason','version'])
def test_archive_rejects_changed_identity_basis_and_receipts(store,part):
    _,repo,run,_,_=store
    launch(repo,run)
    edit(repo,run)
    archive=deepcopy(repo.run_calendar.export_archive(run.id))
    if part=='absence':
        archive['commands'][1]['result']['capture']['projection']['cycles'][2]['claim']=None
    elif part=='run-asset':
        archive['binding']['instrument']='NNQ'
    elif part=='parent':
        archive['commands'][1]['request']['parent_capture_id']='other'
    elif part=='count':
        archive['commands'].pop(0)
    elif part=='receipt':
        archive['commands'][1]['result']['capture']['master']['ledger']['commands'][-1]['result']['changed']=False
    elif part=='reason':
        archive['commands'][1]['request']['reason']='ContextUse'
    else:
        archive['version']=True
    with pytest.raises(ValueError):
        read_run_calendar_archive(archive)


def test_invalid_clock_and_information_basis_reject_without_writes(store):
    connection,repo,run,_,_=store
    prepared=repo.run_calendar.prepare_launch(run,instrument='MNQ',reference=REFERENCE)
    before=counts(connection)
    with pytest.raises(ValueError,match='timezone-aware'):
        repo.run_calendar.launch(prepared,operation_id='launch',capture_id='capture',recorded_at=RECORDED.replace(tzinfo=None))
    assert counts(connection)==before
    launch(repo,run)
    prepared=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
    with pytest.raises(ValueError,match='predate'):
        repo.run_calendar.capture(prepared,operation_id='old',capture_id='old-capture',recorded_at=RECORDED-timedelta(minutes=1))
    target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=3)
    with pytest.raises(ValueError,match='availability cannot follow'):
        repo.run_calendar.revise(prepared,target,operation_id='future',capture_id='future-capture',recorded_at=RECORDED,
            capture=CaptureBasis(information_available_at=RECORDED+timedelta(days=1)),role=Role.D,anchor_id='a',source_ref='chart')


@pytest.mark.parametrize('environment,kind',[(RunEnvironment.LIVE,'ForwardEntry'),
    (RunEnvironment.FORWARD_TEST,'ForwardEntry'),(RunEnvironment.REPLAY,'HistoricalEntry'),
    (RunEnvironment.HISTORICAL_BACKTEST,'HistoricalEntry')])
def test_default_capture_basis_uses_preserved_environment_without_certifying_prediction(store,environment,kind):
    _,repo,run,_,_=store
    run.environment=environment
    run.purpose=RunPurpose.STUDY
    launch(repo,run)
    _,_,_,result=edit(repo,run)
    assert result.capture.packet['run_context']['run_environment']==environment.value
    basis=result.capture.packet['master']['ledger']['commands'][-1]['request']['capture']
    assert basis['kind']==kind and basis['information_available_at'] is None


def test_extracted_run_writer_keeps_actual_old_serialization_byte_for_byte(store):
    connection,_,run,_,_=store
    namespace={}
    root=Path(__file__).resolve().parents[1]
    code=subprocess.check_output(['git','show','6c7362b9d267f920164cbf13dff0415bfc27d3c2:src/ict_cockpit/database/trading_session_run_repository.py'],cwd=root,text=True)
    exec(compile(code,'actual-previous-run-writer','exec'),namespace)
    namespace['TradingSessionRunRepository'](connection).save(run)
    before=connection.execute('SELECT * FROM trading_session_run WHERE id=?',(run.id,)).fetchone()
    TradingSessionRunRepository(connection).save(run)
    assert connection.execute('SELECT * FROM trading_session_run WHERE id=?',(run.id,)).fetchone()==before


def test_two_runs_share_calendar_but_keep_independent_launch_and_update_chains(store):
    _,repo,run,_,_=store
    launch(repo,run)
    edit(repo,run)
    second=TradingRun(run.trading_day_id,'Second run',run.process_session_id)
    _,initial=launch(repo,second,id='second-launch',capture='second-launch-capture')
    edit(repo,second,id='second-edit',role=Role.M)
    assert next(r.claim for r in initial.capture.projection.cycles if r.context.cycle.layer=='year').id=='edit'
    assert len(read_run_calendar_archive(repo.run_calendar.export_archive(run.id))[1])==2
    assert len(read_run_calendar_archive(repo.run_calendar.export_archive(second.id))[1])==2


def test_numeric_offsets_preserve_repeated_hour_reference_as_distinct_capture_basis(store):
    _,repo,run,_,_=store
    first=datetime(2026,11,1,1,30,tzinfo=MARKET_TIMEZONE,fold=0)
    second=first.replace(fold=1)
    run.market_context_snapshot={'reference_market_time':first.isoformat()}
    _,original=launch(repo,run,reference=first)
    prepared=repo.run_calendar.prepare_capture(run.id,reference=second)
    result=repo.run_calendar.capture(prepared,operation_id='fold-second',capture_id='fold-capture',recorded_at=RECORDED)
    assert original.capture.packet['projection']['reference'].endswith('-04:00')
    assert result.capture.packet['projection']['reference'].endswith('-05:00')
    assert read_run_calendar_archive(repo.run_calendar.export_archive(run.id))[1][-1]==result


def test_concurrent_launches_with_different_operation_ids_do_not_double_bind_one_run(store):
    connection,repo,run,_,path=store
    prepared=repo.run_calendar.prepare_launch(run,instrument='MNQ',reference=REFERENCE)
    barrier=Barrier(2)
    def writer(id):
        own=open_application_database(path)
        try:
            barrier.wait(timeout=10)
            return AMDXRepository(own).run_calendar.launch(prepared,operation_id=id,capture_id=id+'-capture',recorded_at=RECORDED)
        except ValueError:
            return None
        finally:
            own.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(writer,('one','two')))
    assert sum(r is not None for r in results)==1
    assert connection.execute('SELECT COUNT(*) FROM amdx_run_binding WHERE run_id=?',(run.id,)).fetchone()[0]==1


def test_cross_asset_run_capture_and_identity_reuse_with_manual_command_reject(store):
    connection,repo,run,_,_=store
    launch(repo,run)
    repo.master.ensure('NNQ',recorded_at=RECORDED)
    prepared=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
    nano=repo.master.load_stack('NNQ',reference=REFERENCE)
    before=counts(connection)
    with pytest.raises(ValueError,match='ownership differ'):
        repo.run_calendar.capture(replace(prepared,snapshot=nano),operation_id='wrong-asset',capture_id='wrong-capture',recorded_at=RECORDED)
    assert counts(connection)==before
    target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=3)
    repo.catalog.revise(target.target,command_id='manual',recorded_at=RECORDED,role=Role.D,anchor_id='manual-a',source_ref='chart')
    prepared=repo.run_calendar.prepare_capture(run.id,reference=REFERENCE)
    with pytest.raises(ValueError,match='reserved'):
        repo.run_calendar.capture(prepared,operation_id='manual',capture_id='unrelated',recorded_at=RECORDED)


@pytest.mark.parametrize('saved',['different','2026-10-13T09:15:00','1985-08-13T09:15:00-04:00'])
def test_known_malformed_or_different_launch_reference_is_not_overridden(store,saved):
    connection,repo,run,_,_=store
    run.market_context_snapshot={'reference_market_time':saved}
    prepared=repo.run_calendar.prepare_launch(run,instrument='MNQ',reference=REFERENCE)
    before=counts(connection)
    with pytest.raises(ValueError):
        repo.run_calendar.launch(prepared,operation_id='launch',capture_id='capture',recorded_at=RECORDED)
    assert counts(connection)==before


def test_launch_missing_original_reference_keeps_explicit_reference_without_invented_saved_basis(store):
    _,repo,run,_,_=store
    run.market_context_snapshot={}
    _,result=launch(repo,run)
    assert result.capture.packet['binding']['run_basis']['market_context_snapshot_json']=='{}'
    assert result.capture.packet['projection']['reference']==REFERENCE.isoformat()


@pytest.mark.parametrize('context',[None,[]])
def test_malformed_launch_context_object_fails_before_any_write(store,context):
    connection,repo,run,_,_=store
    run.market_context_snapshot=context
    prepared=repo.run_calendar.prepare_launch(run,instrument='MNQ',reference=REFERENCE)
    before=counts(connection)
    with pytest.raises(ValueError,match='must be an object'):
        repo.run_calendar.launch(prepared,operation_id='bad',capture_id='bad-capture',recorded_at=RECORDED)
    assert counts(connection)==before
