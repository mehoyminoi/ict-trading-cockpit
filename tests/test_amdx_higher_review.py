from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
import sqlite3

import pytest

from ict_cockpit.analysis.amdx import Role, XSubtype, payload
from ict_cockpit.analysis.amdx_review_scope import day_bounds, orientations
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate
from ict_cockpit.database.amdx_run_observed_repository import read_run_observed_archive
from test_amdx_run_calendar_repository import store, launch, RECORDED
from test_amdx_run_observed_repository import revise, count

BOUNDARY = datetime(2027, 1, 1, 9, 15, 37, tzinfo=MARKET_TIMEZONE)


def start(repo, run, reference=BOUNDARY):
    run.market_context_snapshot = {'reference_market_time': reference.isoformat()}
    return launch(repo, run, reference=reference)[1]


def prepared(repo, run, index=0, level='year', position=None):
    choices=repo.run_observed.higher_orientations(run.id)
    ref=datetime.fromisoformat(choices[index]['reference'])
    if position is None:
        position=int(next(c for c in choices[index]['contexts'] if c['cycle']['layer']==level)['position'][1])
    return repo.run_observed.prepare(run.id, reference=ref, level=level, position=position, higher_scope=True)


@pytest.mark.parametrize('reference,expected',[
    (datetime(2026,10,9,9,15,tzinfo=MARKET_TIMEZONE),1),
    (BOUNDARY,2),
    (datetime(2026,4,1,9,15,tzinfo=MARKET_TIMEZONE),2),
    (datetime(2026,1,1,0,0,tzinfo=MARKET_TIMEZONE),2),
    (datetime(2026,12,31,18,0,tzinfo=MARKET_TIMEZONE),2)])
def test_options_are_deduplicated_full_stack_orientations_original_first(reference,expected):
    choices=orientations(reference)
    assert len(choices)==expected
    assert choices[0]['reference']==reference.isoformat()
    assert choices[0]['source']=='Original launch'
    assert len({tuple((c['cycle']['id'],c['position'],c['state']) for c in x['contexts']) for x in choices})==expected


@pytest.mark.parametrize('day,hours',[(datetime(2026,3,8,9,tzinfo=MARKET_TIMEZONE),23),
                                     (datetime(2026,11,1,9,tzinfo=MARKET_TIMEZONE),25)])
def test_day_window_uses_ny_calendar_bounds_across_dst(day,hours):
    _,start,end=day_bounds(day)
    assert (end.astimezone(timezone.utc)-start.astimezone(timezone.utc)).total_seconds()==hours*3600
    assert start.hour==end.hour==18


def test_boundary_records_two_distinct_occurrences_and_scope_proofs_without_rewriting_expected(store):
    connection,repo,run,_,_=store
    initial=start(repo,run)
    before=count(connection)
    one=revise(repo,prepared(repo,run),id='new-year',role=Role.X,subtype=XSubtype.CONTINUATION)
    two=revise(repo,prepared(repo,run,1),id='old-year',role=Role.X,subtype=XSubtype.REVERSAL)
    assert one.projection.reference==BOUNDARY
    assert one.packet['version']==two.packet['version']==2
    assert next(r for r in one.projection.cycles if r.context.cycle.layer=='year').inference.candidates[0].value=='XAMD'
    assert next(r for r in two.projection.cycles if r.context.cycle.layer=='year').inference.candidates[0].value=='AMDX'
    assert repo.run_calendar.get_result('launch')==initial
    assert count(connection)==(before[0]+2,before[1]+2,before[2],before[3],before[4])
    proof=two.packet['request']['scope_proof']
    assert proof['original_reference']==BOUNDARY.isoformat()
    assert proof['selected_reference']=='2026-12-31T18:00:00-05:00'
    assert proof['reviewed_day']=='2027-01-01'
    assert proof['window_end']=='2027-01-01T18:00:00-05:00'
    assert read_run_observed_archive(repo.run_observed.export_archive(run.id))==(one,two)


@pytest.mark.parametrize('level',['cycle_16y','quadrennial','year','month','week'])
def test_every_higher_layer_has_bounded_explicit_quarter_entry(store,level):
    _,repo,run,_,_=store
    start(repo,run)
    result=revise(repo,prepared(repo,run,1,level,1),role=Role.UNKNOWN)
    assert result.packet['request']['scope_proof']['source']=='Reviewed day start'
    assert result.packet['request']['target']['target']['cycle']['layer']==level
    assert result.projection.cycles[3].context.position==''  # no invented pre-Monday monthly position
    assert result.projection.cycles[4].context.state.value=='Distortion'


def test_quarter_boundary_retains_same_year_claim_without_copying_anchors(store):
    _,repo,run,_,_=store
    start(repo,run,datetime(2026,4,1,9,15,tzinfo=MARKET_TIMEZONE))
    first=revise(repo,prepared(repo,run,1),role=Role.A)
    second=prepared(repo,run,0)
    row=next(r for r in json.loads(second.basis_json)['projection']['cycles'] if r['context']['cycle']['layer']=='year')
    assert row['claim']['id']==first.id
    assert row['context']['position']=='Q2'
    assert row['inference']['candidates']==['AMDX']


def test_utc_equivalent_candidate_allowed_other_in_day_instants_not_arbitrary(store):
    _,repo,run,_,_=store
    start(repo,run)
    p=repo.run_observed.prepare(run.id,reference=BOUNDARY.astimezone(timezone.utc),level='year',position=1,higher_scope=True)
    assert revise(repo,p,role=Role.X).packet['request']['scope_proof']['selected_reference']==BOUNDARY.isoformat()
    for ref in (BOUNDARY+timedelta(minutes=1),BOUNDARY+timedelta(days=1),datetime(2027,1,1,18,tzinfo=MARKET_TIMEZONE)):
        with pytest.raises(ValueError,match='available higher context'):
            repo.run_observed.prepare(run.id,reference=ref,level='year',position=1,higher_scope=True)
    with pytest.raises(ValueError,match='cannot authorize intraday'):
        repo.run_observed.prepare(run.id,reference=BOUNDARY,level='session',position=1,higher_scope=True)


@pytest.mark.parametrize('table',['amdx_catalog_command','amdx_run_observed_command'])
def test_proof_write_failure_rolls_back_calendar_and_assessment_together(store,table):
    c,repo,run,_,_=store
    start(repo,run)
    p=prepared(repo,run,1)
    before=count(c)
    c.execute(f"CREATE TRIGGER fail_proof BEFORE INSERT ON {table} BEGIN SELECT RAISE(ABORT,'injected scope failure'); END")
    with pytest.raises(sqlite3.IntegrityError):revise(repo,p,role=Role.X)
    assert count(c)==before
    assert repo.run_observed.latest(run.id) is None


def test_mixed_receipts_and_exact_retries_survive_new_head_and_resolver_changes(store,monkeypatch):
    _,repo,run,_,_=store
    start(repo,run)
    oldp=repo.run_observed.prepare(run.id,reference=BOUNDARY,level='year',position=1)
    old=revise(repo,oldp,id='old-v1',role=Role.X)
    newp=prepared(repo,run,1)
    new=revise(repo,newp,id='new-v2',role=Role.X)
    def fail(*args,**kwargs):raise AssertionError('archive/retry must not use resolver')
    monkeypatch.setattr('ict_cockpit.analysis.amdx_context.resolve_higher_cycles',fail)
    assert revise(repo,oldp,id='old-v1',role=Role.X)==old
    assert revise(repo,newp,id='new-v2',role=Role.X)==new
    archive=repo.run_observed.export_archive(run.id)
    assert archive['version']==2
    assert read_run_observed_archive(archive)==(old,new)
    archive['version']=1
    with pytest.raises(ValueError):read_run_observed_archive(archive)


@pytest.mark.parametrize('field',['original_reference','selected_reference','window_start','window_end','reviewed_day','run_id','source','selected_contexts','candidates'])
def test_archive_rejects_tampered_scope_proof(store,field):
    _,repo,run,_,_=store
    start(repo,run)
    revise(repo,prepared(repo,run,1),role=Role.X)
    archive=repo.run_observed.export_archive(run.id)
    proof=archive['commands'][0]['request']['scope_proof']
    proof[field]=[] if field in ('selected_contexts','candidates') else 'altered'
    with pytest.raises((ValueError,TypeError)):read_run_observed_archive(archive)


def test_new_scope_write_detects_temporal_policy_changes_before_any_commit(store,monkeypatch):
    c,repo,run,_,_=store
    start(repo,run)
    p=prepared(repo,run,1)
    choices=deepcopy(orientations(BOUNDARY))
    choices[1]['contexts'][0]['prior_q4_id']='changed-rule'
    monkeypatch.setattr('ict_cockpit.analysis.amdx_review_scope.orientations',lambda ref:choices)
    before=count(c)
    with pytest.raises(ValueError):revise(repo,p,role=Role.X)
    assert count(c)==before


@pytest.mark.parametrize('fold',[0,1])
def test_repeated_original_hour_retains_exact_offset_and_does_not_accept_other_occurrence(store,fold):
    _,repo,run,_,_=store
    reference=datetime(2026,11,1,1,30,tzinfo=MARKET_TIMEZONE,fold=fold)
    start(repo,run,reference)
    p=prepared(repo,run,0,position=4)
    result=revise(repo,p,role=Role.X)
    assert result.packet['request']['scope_proof']['original_reference']==reference.isoformat()
    other=reference.replace(fold=1-fold)
    with pytest.raises(ValueError,match='available higher context'):
        repo.run_observed.prepare(run.id,reference=other,level='year',position=4,higher_scope=True)


def test_null_proof_cannot_be_used_as_a_version_two_receipt(store):
    _,repo,run,_,_=store
    start(repo,run)
    revise(repo,prepared(repo,run),role=Role.X)
    archive=repo.run_observed.export_archive(run.id)
    archive['commands'][0]['request']['scope_proof']=None
    with pytest.raises(ValueError,match='explicit scope proof'):read_run_observed_archive(archive)
