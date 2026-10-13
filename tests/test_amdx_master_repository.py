from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from datetime import datetime
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from threading import Barrier

import pytest

from ict_cockpit.analysis.amdx import Profile, Role
from ict_cockpit.analysis.amdx_catalog import Catalog
from ict_cockpit.analysis.amdx_master import MasterCalendar
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.database.amdx_catalog_repository import read_catalog_archive
from ict_cockpit.database.amdx_master_repository import MasterAdoptionRequired, read_master_archive
from ict_cockpit.database.amdx_repository import AMDXRepository, StaleAMDXUpdate
from ict_cockpit.database.bootstrap import open_application_database


REFERENCE = datetime(1985, 8, 12, 9, 15, tzinfo=MARKET_TIMEZONE)
RECORDED = datetime(2026, 10, 13, 10, tzinfo=MARKET_TIMEZONE)


@pytest.fixture
def store(tmp_path):
    path = tmp_path / 'master.db'
    connection = open_application_database(path)
    yield connection, AMDXRepository(connection), path
    connection.close()


def create(repo, instrument='MNQ', id='owner', binding='binding'):
    return repo.master.create(MasterCalendar(id, 'Maintained calendar', instrument),
        binding_id=binding, recorded_at=RECORDED, source_ref='explicit instrument context')


def revise(repo, prepared, id, role):
    return repo.catalog.revise(prepared.target, command_id=id, recorded_at=RECORDED,
        role=role, anchor_id='anchor-'+id, source_ref='synthetic chart')


def test_missing_read_is_inert_and_clean_ensure_is_unique_and_purpose_free(store):
    connection, repo, _ = store
    before = connection.total_changes
    with pytest.raises(ValueError, match='no canonical'):
        repo.master.load_stack('MNQ', reference=REFERENCE)
    assert connection.total_changes == before
    binding = repo.master.ensure('MNQ', recorded_at=RECORDED)
    assert repo.master.ensure('MNQ', recorded_at=RECORDED) == binding
    owner = repo.catalog.get(binding.catalog_id)
    assert isinstance(owner, MasterCalendar) and not hasattr(owner, 'purpose')
    assert repo.catalog.list_catalogs() == ()
    assert connection.execute('SELECT COUNT(*) FROM amdx_catalog').fetchone()[0] == 1
    assert connection.execute('SELECT COUNT(*) FROM amdx_master_binding').fetchone()[0] == 1
    assert not connection.execute('SELECT id FROM trading_session_run').fetchall()
    with pytest.raises(ValueError, match='canonical master creation'):
        repo.catalog.create(owner)


@pytest.mark.parametrize('instrument', ['', 'mnq', ' MNQ', 'MNQ ', None])
def test_instrument_is_never_normalized_or_guessed(store, instrument):
    connection, repo, _ = store
    with pytest.raises((ValueError, TypeError)):
        repo.master.ensure(instrument, recorded_at=RECORDED)
    assert not connection.execute('SELECT * FROM amdx_catalog').fetchall()


def test_same_owner_and_occurrence_across_shared_reads_preserves_channels_and_old_view(store):
    connection, repo, _ = store
    binding = create(repo)
    target = repo.master.prepare_target('MNQ', reference=REFERENCE, level='year', position=3)
    first = revise(repo, target, 'working-1', Role.D)
    old = repo.master.load_stack('MNQ', reference=REFERENCE)
    later = repo.master.load_stack('MNQ', reference=REFERENCE.replace(day=13))
    assert old.binding == later.binding == binding
    assert next(r.claim for r in later.projection.cycles if r.context.cycle.layer=='year') == first.claim
    observed = repo.master.prepare_target('MNQ', reference=REFERENCE, level='year', position=3, channel='Observed')
    second = revise(repo, observed, 'observed-1', Role.M)
    assert second.claim.inference.candidates == (Profile.XAMD,)
    assert next(r.claim for r in old.projection.cycles if r.context.cycle.layer=='year') == first.claim
    fresh = repo.master.prepare_target('MNQ', reference=REFERENCE, level='year', position=3)
    revise(repo, fresh, 'working-2', Role.M)
    before = connection.total_changes
    with pytest.raises(StaleAMDXUpdate, match='quartet changed'):
        repo.master.validate_target(target)
    assert connection.total_changes == before
    assert next(r.claim for r in old.projection.cycles if r.context.cycle.layer=='year').id == 'working-1'


def test_cross_asset_and_binding_target_drift_reject_without_writes(store):
    connection, repo, _ = store
    create(repo)
    nano = create(repo, 'NNQ', 'nano-owner', 'nano-binding')
    original = repo.master.prepare_target('MNQ', reference=REFERENCE, level='year', position=3)
    before = connection.total_changes
    with pytest.raises(ValueError, match='ownership'):
        repo.master.validate_target(replace(original, binding=nano))
    with pytest.raises(StaleAMDXUpdate, match='binding changed'):
        repo.master.validate_target(replace(original, binding=replace(original.binding, id='changed')))
    assert connection.total_changes == before
    assert all(r.claim is None for r in repo.master.load_stack('NNQ', reference=REFERENCE).projection.cycles)


@pytest.mark.parametrize('level', ['cycle_16y','quadrennial','year','month','week','day','session'])
def test_shared_targets_cover_all_supported_layers_and_reads_do_not_mutate(store, level):
    connection, repo, _ = store
    create(repo)
    before = connection.total_changes
    target = repo.master.prepare_target('MNQ', reference=REFERENCE, level=level, position=3)
    assert repo.master.validate_target(target) == target
    assert target.target.expected_head_id is None
    assert connection.total_changes == before and not connection.in_transaction


def test_closed_reference_retains_five_identified_layers_without_fake_intraday(store):
    _, repo, _ = store
    create(repo)
    view = repo.master.load_stack('MNQ', reference=REFERENCE.replace(day=17))
    assert not view.projection.market_open and len(view.projection.cycles)==5
    with pytest.raises(ValueError, match='identified AMDX level'):
        repo.master.prepare_target('MNQ', reference=REFERENCE.replace(day=17), level='session')


def test_deliberate_adoption_preserves_conflicting_collections_and_legacy_archive_bytes(store):
    connection, repo, _ = store
    first = repo.catalog.create(Catalog('first', 'First study'))
    second = repo.catalog.create(Catalog('second', 'Another approach', purpose='ForwardTest'))
    for id, catalog, role in [('c1',first,Role.M),('c2',second,Role.D)]:
        target = repo.catalog.prepare_target(catalog.id, reference=REFERENCE, level='year', position=3)
        repo.catalog.revise(target,command_id=id,recorded_at=RECORDED,role=role,
                            anchor_id='a'+id,source_ref='chart')
    raw = connection.execute('SELECT * FROM amdx_catalog').fetchall()
    commands = connection.execute('SELECT * FROM amdx_catalog_command').fetchall()
    archives = [repo.catalog.export_archive(c.id) for c in (first,second)]
    with pytest.raises(MasterAdoptionRequired):
        repo.master.ensure('MNQ', recorded_at=RECORDED)
    with pytest.raises(MasterAdoptionRequired):
        create(repo)
    binding = repo.master.adopt('MNQ', second.id,binding_id='adopt',recorded_at=RECORDED,source_ref='operator choice')
    assert repo.master.resolve('MNQ') == binding
    assert connection.execute('SELECT * FROM amdx_catalog').fetchall() == raw
    assert connection.execute('SELECT * FROM amdx_catalog_command').fetchall() == commands
    assert [repo.catalog.export_archive(c.id) for c in (first,second)] == archives
    assert archives[0]['version'] == archives[1]['version'] == 1
    assert read_master_archive(repo.master.export_archive('MNQ'))[1] == second
    assert next(r.claim for r in repo.master.load_stack('MNQ',reference=REFERENCE,channel='Observed').projection.cycles if r.context.cycle.layer=='year').id == 'c2'
    with pytest.raises(ValueError,match='already has'):
        repo.master.adopt('MNQ',first.id,binding_id='other',recorded_at=RECORDED,source_ref='new choice')


def test_cross_asset_adoption_and_exact_retry_request_drift(store):
    _, repo, _ = store
    legacy = repo.catalog.create(Catalog('legacy','Nano study',instrument='NNQ'))
    with pytest.raises(ValueError,match='different instrument'):
        repo.master.adopt('MNQ',legacy.id,binding_id='bad',recorded_at=RECORDED,source_ref='choice')
    binding = repo.master.adopt('NNQ',legacy.id,binding_id='ok',recorded_at=RECORDED,source_ref='choice')
    assert repo.master.adopt('NNQ',legacy.id,binding_id='ok',recorded_at=RECORDED,source_ref='choice') == binding
    with pytest.raises(ValueError,match='identity cannot'):
        repo.master.adopt('NNQ',legacy.id,binding_id='ok',recorded_at=RECORDED,source_ref='different choice')


def test_create_retries_original_after_new_commands_and_blocks_request_drift(store):
    _, repo, _ = store
    binding = create(repo)
    target = repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=3)
    revise(repo,target,'new',Role.D)
    assert create(repo) == binding
    with pytest.raises(ValueError,match='identity cannot'):
        repo.master.create(MasterCalendar('owner','Different title','MNQ'),binding_id='binding',
                           recorded_at=RECORDED,source_ref='explicit instrument context')


@pytest.mark.parametrize('action', ['UPDATE amdx_master_binding SET instrument="NNQ"',
    'DELETE FROM amdx_master_binding',
    'INSERT OR REPLACE INTO amdx_master_binding SELECT * FROM amdx_master_binding'])
def test_binding_sql_immutability(store, action):
    connection, repo, _ = store
    binding = create(repo)
    with pytest.raises(sqlite3.IntegrityError,match='immutable'):
        connection.execute(action)
    connection.rollback()
    assert repo.master.resolve('MNQ') == binding


def test_sql_cross_asset_binding_is_rejected(store):
    connection, repo, _ = store
    repo.catalog.create(Catalog('old','Original'))
    with pytest.raises(sqlite3.IntegrityError, match='FOREIGN KEY'):
        connection.execute('INSERT INTO amdx_master_binding VALUES (?,?,?,?)',('bad','NNQ','old','{}'))
    connection.rollback()


def test_binding_insert_failure_rolls_back_new_owner_and_caller_transaction_is_retained(store):
    connection, repo, _ = store
    connection.execute("CREATE TRIGGER fail_binding BEFORE INSERT ON amdx_master_binding BEGIN SELECT RAISE(ABORT,'injected'); END")
    with pytest.raises(sqlite3.IntegrityError, match='injected'):
        create(repo)
    assert not connection.execute('SELECT * FROM amdx_catalog').fetchall()
    connection.execute('DROP TRIGGER fail_binding')
    connection.execute('BEGIN')
    with pytest.raises(RuntimeError, match='pending transaction'):
        create(repo)
    assert connection.in_transaction
    connection.rollback()
    create(repo)
    connection.execute('BEGIN')
    repo.master.load_stack('MNQ',reference=REFERENCE)
    assert connection.in_transaction
    connection.rollback()


def test_concurrent_clean_ensure_and_competing_adoption_have_one_winner(store):
    connection, repo, path = store
    barrier = Barrier(2)
    def ensure():
        own=open_application_database(path)
        try:
            barrier.wait(timeout=10)
            return AMDXRepository(own).master.ensure('MNQ',recorded_at=RECORDED)
        finally:
            own.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:ensure(),range(2)))
    assert results[0]==results[1]
    assert connection.execute('SELECT COUNT(*) FROM amdx_catalog').fetchone()[0]==1
    repo.catalog.create(Catalog('nano-1','Nano 1',instrument='NNQ'))
    repo.catalog.create(Catalog('nano-2','Nano 2',instrument='NNQ'))
    barrier=Barrier(2)
    def adopt(id):
        own=open_application_database(path)
        try:
            barrier.wait(timeout=10)
            return AMDXRepository(own).master.adopt('NNQ',id,binding_id='bind-'+id,
                recorded_at=RECORDED,source_ref='explicit choice')
        except ValueError as error:
            return str(error)
        finally:
            own.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(adopt,('nano-1','nano-2')))
    assert sum(not isinstance(r,str) for r in results)==1
    assert connection.execute('SELECT COUNT(*) FROM amdx_master_binding WHERE instrument="NNQ"').fetchone()[0]==1


def test_master_archive_and_reopen_preserve_unknowns_noops_and_original_policy(store):
    connection, repo, path = store
    create(repo)
    target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=3)
    first=revise(repo,target,'working',Role.D)
    missing=repo.master.prepare_target('MNQ',reference=REFERENCE,level='week',position=1,channel='Observed')
    result=repo.catalog.revise(missing.target,command_id='noop',recorded_at=RECORDED)
    assert not result.changed and result.claim is None
    archive=json.loads(json.dumps(repo.master.export_archive('MNQ')))
    assert archive['ledger']['version']==2
    binding,owner,history=read_master_archive(archive)
    assert history.claims==(first.claim,) and isinstance(owner,MasterCalendar)
    assert read_catalog_archive(archive['ledger'])[1]==history
    assert archive['ledger']['commands'][-1]['request']['capture']['information_available_at'] is None
    before=connection.total_changes
    assert repo.master.export_archive('MNQ')==archive and connection.total_changes==before
    other=open_application_database(path)
    try:
        restored=AMDXRepository(other)
        assert restored.master.resolve('MNQ')==binding
        assert restored.master.export_archive('MNQ')==archive
    finally:
        other.close()
    for field in ('instrument','catalog_id'):
        broken=deepcopy(archive)
        broken['binding']['binding'][field]='different'
        with pytest.raises(ValueError):
            read_master_archive(broken)
    broken=deepcopy(archive)
    broken['ledger']['commands'][0]['result']['changed']=False
    with pytest.raises(ValueError,match='disagrees'):
        read_master_archive(broken)


def test_read_fails_for_invalid_binding_payload_without_creating_replacement(store):
    connection, repo, _ = store
    repo.catalog.create(Catalog('old','Original'))
    connection.execute('INSERT INTO amdx_master_binding VALUES (?,?,?,?)',('bad','MNQ','old','{}'))
    connection.commit()
    before=connection.total_changes
    with pytest.raises(ValueError,match='envelope'):
        repo.master.ensure('MNQ',recorded_at=RECORDED)
    assert connection.total_changes==before


def test_shared_read_uses_one_snapshot_when_another_writer_commits_between_reads(store,monkeypatch):
    _, repo, path = store
    create(repo)
    target=repo.master.prepare_target('MNQ',reference=REFERENCE,level='year',position=3)
    original=repo.catalog.load_stack
    writer=open_application_database(path)
    def interleave(*args,**kwargs):
        AMDXRepository(writer).catalog.revise(target.target,command_id='external',recorded_at=RECORDED,
            role=Role.D,anchor_id='external-anchor',source_ref='other writer')
        return original(*args,**kwargs)
    monkeypatch.setattr(repo.catalog,'load_stack',interleave)
    try:
        old=repo.master.load_stack('MNQ',reference=REFERENCE)
        assert all(r.claim is None for r in old.projection.cycles)
        monkeypatch.setattr(repo.catalog,'load_stack',original)
        current=repo.master.load_stack('MNQ',reference=REFERENCE)
        assert next(r.claim for r in current.projection.cycles if r.context.cycle.layer=='year').id=='external'
    finally:
        writer.close()


def test_independent_process_reopen_reconstructs_same_master_archive(store):
    _, repo, path = store
    create(repo)
    archive=repo.master.export_archive('MNQ')
    env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[1]/'src'))
    output=subprocess.check_output([sys.executable,'-c',
        'import json,sys; from pathlib import Path; from ict_cockpit.database.bootstrap import open_application_database; from ict_cockpit.database.amdx_repository import AMDXRepository; c=open_application_database(Path(sys.argv[1])); print(json.dumps(AMDXRepository(c).master.export_archive("MNQ"))); c.close()',
        str(path)],env=env,text=True)
    assert json.loads(output)==archive


@pytest.mark.parametrize('kind',['naive','missing-source','boolean-version'])
def test_invalid_binding_basis_never_becomes_master(store,kind):
    connection,repo,_=store
    if kind=='boolean-version':
        create(repo)
        bad=repo.master.export_archive('MNQ')
        bad['binding']['version']=True
        with pytest.raises(ValueError,match='envelope'):
            read_master_archive(bad)
    else:
        with pytest.raises(ValueError):
            repo.master.create(MasterCalendar('owner','Calendar','MNQ'),binding_id='binding',
                recorded_at=RECORDED.replace(tzinfo=None) if kind=='naive' else RECORDED,
                source_ref='' if kind=='missing-source' else 'source')
        assert not connection.execute('SELECT * FROM amdx_master_binding').fetchall()
