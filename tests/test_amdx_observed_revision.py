"""Observed corrections share structural behavior, never working ownership."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from threading import Barrier

import pytest

from ict_cockpit.analysis.amdx import (
    Anchor, InterpretationHistory, OBSERVED_POLICY, Profile, Role, XSubtype, intraday_cycles,
)
from ict_cockpit.analysis.amdx_review import StaleComparison
from ict_cockpit.database.amdx_repository import AMDXRepository, StaleAMDXUpdate
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from test_amdx_repository import REFERENCE, choice, saved_run
from test_amdx_review_repository import store, observed, pairing


ROOT = Path(__file__).resolve().parents[1]
DAY, SESSION = intraday_cycles(REFERENCE)


def revise(repo, run, number, role, *, position=3, subtype=None, head=None, pair_head=None,
           clear_applicability=False, cycle=DAY):
    args = choice(run, revision=str(number), role=role, position=position, cycle=cycle)
    args.pop("channel")
    args.pop("expected_head_id")
    if args["anchor"] is not None and subtype is not None:
        args["anchor"] = Anchor(args["anchor"].id, args["quarter_id"], role, "synthetic-technician", subtype)
    return repo.review.revise_observed(**args, comparison_id=f"P{number}",
                                       expected_observed_head_id=head, expected_comparison_head_id=pair_head,
                                       clear_applicability=clear_applicability)


@pytest.mark.parametrize("position", [1,2,3,4])
@pytest.mark.parametrize("role", [Role.A,Role.M,Role.D,Role.X])
def test_observed_action_enforces_all_position_role_pairs(position, role):
    history = InterpretationHistory()
    valid = {1:(Role.A,Role.X),2:(Role.A,Role.M),3:(Role.M,Role.D),4:(Role.D,Role.X)}
    args=dict(claim_id="O1",run_id="run",branch_id="working",channel="Observed",cycle=DAY,
              quarter_id=DAY.quarters[position-1].id,
              anchor=Anchor("a1",DAY.quarters[position-1].id,role,"technician"),
              recorded_at=REFERENCE,market_reference=REFERENCE)
    if role not in valid[position]:
        with pytest.raises(ValueError,match="structurally valid"):
            history.revise_observed(**args)
    else:
        result=history.revise_observed(**args).claims[-1]
        assert result.action_policy == OBSERVED_POLICY and result.channel == "Observed"
        assert result.inference.state == "Resolved"


def test_one_entry_observed_order_change_does_not_touch_working_or_restore_retired_anchors(store):
    connection, repo, run = store
    original = repo.get_history(run.id).claims[0]
    first = revise(repo,run,2,Role.A,position=1)
    second = revise(repo,run,3,Role.M,head=first.claim.id,pair_head=first.comparison.id)
    assert second.claim.inference.candidates == (Profile.XAMD,)
    assert second.claim.retired_anchor_ids == (first.claim.anchors[0].id,)
    cleared = revise(repo,run,4,None,head=second.claim.id,pair_head=second.comparison.id)
    assert cleared.claim.inference.state == "Unresolved" and cleared.claim.anchors == ()
    assert repo.get_history(run.id).claims[0] == original
    assert all(c.channel == "Observed" for c in repo.get_history(run.id).claims[1:])
    assert all(p.expected_claim_id is None for p in repo.review.get_history(run.id).comparisons)


def test_x_subtype_unknown_and_applicability_follow_independent_observed_semantics(store):
    connection, repo, run = store
    a=revise(repo,run,2,Role.X,position=4,subtype=XSubtype.REVERSAL)
    b=revise(repo,run,3,Role.D,head=a.claim.id,pair_head=a.comparison.id)
    assert b.claim.inference.roles[3].subtype is XSubtype.REVERSAL
    c=revise(repo,run,4,Role.M,head=b.claim.id,pair_head=b.comparison.id)
    assert c.claim.inference.roles[0].subtype is None
    d=revise(repo,run,5,Role.UNKNOWN,position=1,head=c.claim.id,pair_head=c.comparison.id)
    assert d.claim.inference.roles[0].role is Role.X
    e=revise(repo,run,6,Role.NOT_APPLICABLE,head=d.claim.id,pair_head=d.comparison.id)
    f=revise(repo,run,7,Role.UNKNOWN,head=e.claim.id,pair_head=e.comparison.id)
    assert f.claim.inference.state == "Not Applicable"
    g=revise(repo,run,8,None,head=f.claim.id,pair_head=f.comparison.id,clear_applicability=True)
    assert g.claim.inference.state == "Unresolved"
    assert g.claim.anchors[0].role is Role.UNKNOWN
    h=revise(repo,run,9,Role.M,head=g.claim.id,pair_head=g.comparison.id)
    assert h.claim.inference.candidates == (Profile.XAMD,)


def test_no_op_receipt_reserves_both_ids_and_returns_original_after_later_changes(store):
    connection, repo, run = store
    first=revise(repo,run,2,Role.D)
    repeat=revise(repo,run,3,Role.D,head=first.claim.id,pair_head=first.comparison.id)
    assert not repeat.changed and repeat.claim == first.claim and repeat.comparison == first.comparison
    assert connection.execute("SELECT COUNT(*) FROM amdx_comparison").fetchone()[0] == 1
    later=revise(repo,run,4,Role.M,head=first.claim.id,pair_head=first.comparison.id)
    assert revise(repo,run,3,Role.D,head=first.claim.id,pair_head=first.comparison.id) == repeat
    assert revise(repo,run,2,Role.D) == first
    assert repo.review.get_history(run.id).comparisons[-1] == later.comparison
    for id in ("claim-3","P3"):
        with pytest.raises(ValueError,match="identity"):
            repo.accept(**{**choice(run,revision="5"),"claim_id":id})
        with pytest.raises(ValueError,match="identity"):
            repo.review.record_comparison(**pairing(run,id=id,observed="claim-2",head=later.comparison.id))
    with pytest.raises(ValueError,match="identity"):
        revise(repo,run,3,Role.M,head=first.claim.id,pair_head=first.comparison.id)


def test_empty_clear_has_no_observation_or_pair_and_still_survives_restart(store,tmp_path):
    connection, repo, run = store
    empty=revise(repo,run,2,None,cycle=SESSION)
    assert not empty.changed and empty.claim is None and empty.comparison is None
    assert connection.execute("SELECT COUNT(*) FROM amdx_comparison").fetchone()[0] == 0
    reopened=open_application_database(tmp_path/'review.db')
    assert revise(AMDXRepository(reopened),run,2,None,cycle=SESSION) == empty
    reopened.close()


def test_explicit_basis_is_carried_through_correction_and_clear_without_latest_fallback(store):
    connection, repo, run = store
    first=revise(repo,run,2,Role.D)
    selected=repo.review.record_comparison(**pairing(run,id="selected",observed=first.claim.id,
                                                    head=first.comparison.id,minutes=3))
    repo.revise_working(**choice(run,revision="4",role=Role.M,head="claim-1"))
    corrected=revise(repo,run,5,Role.M,head=first.claim.id,pair_head=selected.id)
    assert corrected.comparison.expected_claim_id == "claim-1"
    unselected=repo.review.record_comparison(**pairing(run,id="unselected",basis=None,
                                                      observed=corrected.claim.id,head=corrected.comparison.id,minutes=6))
    next_choice=revise(repo,run,7,Role.D,head=corrected.claim.id,pair_head=unselected.id)
    assert next_choice.comparison.expected_claim_id is None
    assert repo.review.get_history(run.id).comparisons[0].expected_claim_id is None


def test_legacy_observed_conflict_can_be_revised_without_reinterpreting_original_records(store):
    connection, repo, run = store
    one=repo.accept(**choice(run,revision="2",channel="Observed",role=Role.A,position=1))
    two=repo.accept(**choice(run,revision="3",channel="Observed",role=Role.A,position=2,head=one.id))
    original=connection.execute("SELECT * FROM amdx_claim ORDER BY sequence").fetchall()
    assert two.inference.state == "Conflict"
    result=revise(repo,run,4,Role.M,head=two.id)
    assert result.claim.inference.candidates == (Profile.XAMD,)
    assert connection.execute("SELECT * FROM amdx_claim ORDER BY sequence LIMIT 3").fetchall() == original
    with pytest.raises(ValueError,match="Legacy accumulation"):
        repo.accept(**choice(run,revision="5",channel="Observed",head=result.claim.id))
    assert repo.accept(**choice(run,revision="2",channel="Observed",role=Role.A,position=1)) == one


def test_v1_v2_v3_archives_keep_original_policies_and_reject_reinterpreted_observed_record(store):
    connection, repo, run = store
    repo.accept(**choice(run,revision="2",channel="Observed",role=Role.D))
    before=repo.get_history(run.id).to_payload()
    assert before['version'] == 2
    revise(repo,run,3,Role.M,head="claim-2")
    archive=repo.get_history(run.id).to_payload()
    assert archive['version'] == 3 and archive['claims'][:2] == before['claims']
    assert InterpretationHistory.from_payload(json.loads(json.dumps(archive))) == repo.get_history(run.id)
    bad=deepcopy(archive);bad['version']=2
    with pytest.raises(ValueError,match="policy/history"):
        InterpretationHistory.from_payload(bad)
    bad=deepcopy(archive);bad['claims'][-1]['action_policy']='revise-working-v1'
    with pytest.raises(ValueError):
        InterpretationHistory.from_payload(bad)


@pytest.mark.parametrize("failure", ["amdx_claim","amdx_comparison","amdx_observed_command"])
def test_failed_revision_rolls_back_source_cycle_pair_and_receipt(store,failure):
    connection, repo, run = store
    def counts():
        return tuple(connection.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
                     for t in ('amdx_claim','amdx_comparison','amdx_observed_command','amdx_cycle_identity'))
    before=counts()
    connection.execute(f"CREATE TRIGGER injected BEFORE INSERT ON {failure} BEGIN SELECT RAISE(ABORT,'injected'); END")
    with pytest.raises(sqlite3.IntegrityError,match='injected'):
        revise(repo,run,2,Role.D,cycle=SESSION)
    assert counts() == before
    connection.execute('DROP TRIGGER injected')
    assert revise(repo,run,2,Role.D,cycle=SESSION).changed


def test_stale_heads_reject_even_semantically_identical_input(store):
    connection, repo, run = store
    first=revise(repo,run,2,Role.D)
    with pytest.raises(StaleAMDXUpdate):
        revise(repo,run,3,Role.D,pair_head=first.comparison.id)
    with pytest.raises(StaleComparison):
        revise(repo,run,3,Role.D,head=first.claim.id)
    assert len(repo.review.get_history(run.id).comparisons) == 1


@pytest.mark.parametrize('operation',['UPDATE','DELETE','REPLACE'])
def test_observed_receipts_are_sql_immutable_including_no_ops(store,operation):
    connection,repo,run=store
    revise(repo,run,2,None)
    with pytest.raises(sqlite3.IntegrityError,match='immutable'):
        with connection:
            sql={'UPDATE':"UPDATE amdx_observed_command SET changed=1",
                 'DELETE':"DELETE FROM amdx_observed_command",
                 'REPLACE':"INSERT OR REPLACE INTO amdx_observed_command SELECT * FROM amdx_observed_command"}[operation]
            connection.execute(sql)
    assert not revise(repo,run,2,None).changed


@pytest.mark.parametrize('field,value',[('changed',1),('basis_count',0),('result_claim_id',None)])
def test_forged_no_op_result_or_snapshot_is_rejected_on_read(store,field,value):
    connection,repo,run=store
    first=revise(repo,run,2,Role.D)
    revise(repo,run,3,Role.D,head=first.claim.id,pair_head=first.comparison.id)
    connection.execute('DROP TRIGGER amdx_observed_command_no_update')
    with connection:
        connection.execute(f'UPDATE amdx_observed_command SET {field}=? WHERE id=?',(value,'claim-3'))
    with pytest.raises(ValueError):
        repo.review.get_history(run.id)


@pytest.mark.parametrize('same_command',[False,True])
def test_observed_writer_contention_preserves_original_heads_or_exact_retry(store,tmp_path,same_command):
    connection,repo,run=store
    barrier=Barrier(2)
    def writer(number):
        local=open_application_database(tmp_path/'review.db')
        try:
            barrier.wait(timeout=5)
            return revise(AMDXRepository(local),run,2 if same_command else number,Role.D)
        except (StaleAMDXUpdate,StaleComparison) as error:
            return error
        finally:
            local.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(writer,(2,3)))
    if same_command:
        assert results[0] == results[1]
    else:
        assert sum(isinstance(r,(StaleAMDXUpdate,StaleComparison)) for r in results) == 1
    assert len(repo.review.get_history(run.id).comparisons) == 1
    assert connection.execute('SELECT COUNT(*) FROM amdx_observed_command').fetchone()[0] == 1


def test_source_and_original_no_op_results_survive_separate_process(store,tmp_path):
    connection,repo,run=store
    first=revise(repo,run,2,Role.D)
    revise(repo,run,3,Role.D,head=first.claim.id,pair_head=first.comparison.id)
    revise(repo,run,4,Role.M,head=first.claim.id,pair_head=first.comparison.id)
    code=('from pathlib import Path; from ict_cockpit.database.bootstrap import open_application_database; '
          'from ict_cockpit.database.amdx_repository import AMDXRepository; '
          f'c=open_application_database(Path({str(tmp_path/"review.db")!r})); '
          f'h=AMDXRepository(c).review.get_history({run.id!r}); '
          'print(h.interpretations.to_payload()["version"],h.claim("claim-2").inference.candidates[0].value, '
          'h.claim("claim-4").inference.candidates[0].value,len(h.comparisons));c.close()')
    result=subprocess.run([sys.executable,'-c',code],check=True,capture_output=True,text=True,
                          env={**os.environ,'PYTHONPATH':str(ROOT/'src')})
    assert result.stdout.strip() == '3 AMDX XAMD 2'


@pytest.mark.parametrize('channel,branch',[('Expected','working'),('Observed','alternative')])
def test_observed_revision_cannot_mutate_working_or_analytical_scopes(channel,branch):
    args=dict(claim_id='O1',run_id='run',branch_id=branch,channel=channel,cycle=DAY,
              quarter_id=DAY.quarters[2].id,anchor=Anchor('a',DAY.quarters[2].id,Role.D,'technician'),
              recorded_at=REFERENCE,market_reference=REFERENCE)
    with pytest.raises(ValueError,match='Observed/working scope'):
        InterpretationHistory().revise_observed(**args)


def test_clear_no_op_receipt_checks_registered_cycle_bounds_even_without_a_profile(store):
    connection,repo,run=store
    revise(repo,run,2,None,cycle=SESSION)
    raw=json.loads(connection.execute('SELECT payload_json FROM amdx_observed_command').fetchone()[0])
    cycle=raw['arguments']['cycle']
    for q in cycle['quarters']:
        from datetime import datetime
        q['start']=(datetime.fromisoformat(q['start'])+timedelta(days=1)).isoformat()
        q['end']=(datetime.fromisoformat(q['end'])+timedelta(days=1)).isoformat()
    connection.execute('DROP TRIGGER amdx_observed_command_no_update')
    with connection:
        connection.execute('UPDATE amdx_observed_command SET payload_json=?',(json.dumps(raw),))
    with pytest.raises(ValueError,match='stable cycle'):
        repo.review.get_history(run.id)


def test_v40_actual_schema_and_repositories_migrate_without_rewriting_original_rows(tmp_path,monkeypatch):
    import ict_cockpit.database.amdx_review_repository as adapter
    old_schema={};old_core={};old_review={}
    for filename,namespace in [('schema.py',old_schema),('amdx_repository.py',old_core),('amdx_review_repository.py',old_review)]:
        code=subprocess.check_output(['git','show',f'1bf3933:src/ict_cockpit/database/{filename}'],cwd=ROOT,text=True)
        exec(compile(code,f'archived-v40-{filename}','exec'),namespace)
    connection=create_connection(tmp_path/'old-v40.db')
    old_schema['initialize_schema'](connection)
    run=saved_run(connection)
    with monkeypatch.context() as patch:
        patch.setattr(adapter,'AMDXReviewRepository',old_review['AMDXReviewRepository'])
        old=old_core['AMDXRepository'](connection)
        old.revise_working(**choice(run,role=Role.D))
        original=old.review.record_observation(**observed(run,role=Role.A,number=2))
    tables=('trading_session_run','amdx_claim','amdx_comparison','amdx_review_command','amdx_working_command','amdx_cycle_identity')
    before={t:connection.execute(f'SELECT * FROM {t}').fetchall() for t in tables}
    connection.set_authorizer(lambda action,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_CREATE_TRIGGER else sqlite3.SQLITE_OK)
    with pytest.raises(sqlite3.DatabaseError):initialize_schema(connection)
    connection.set_authorizer(None)
    assert connection.execute('PRAGMA user_version').fetchone()[0] == 40
    assert not connection.execute("SELECT name FROM sqlite_master WHERE name LIKE 'amdx_observed_%'").fetchall()
    initialize_schema(connection)
    assert connection.execute('PRAGMA user_version').fetchone()[0] == CURRENT_SCHEMA_VERSION == 46
    for t in tables:assert connection.execute(f'SELECT * FROM {t}').fetchall() == before[t]
    with pytest.raises(RuntimeError,match='Unsupported database schema version: 46'):
        old_schema['initialize_schema'](connection)
    current=AMDXRepository(connection)
    assert current.review.record_observation(**observed(run,role=Role.A,number=2)) == original
    corrected=revise(current,run,3,Role.M,head='claim-2',pair_head='P1')
    assert corrected.claim.inference.candidates == (Profile.XAMD,)
    assert connection.execute('SELECT * FROM amdx_claim ORDER BY sequence LIMIT 2').fetchall() == before['amdx_claim']
    assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
    connection.close()


def test_disposable_observed_demo_verifies_one_entry_no_op_and_reopen():
    result=subprocess.run([sys.executable,str(ROOT/'tools/amdx_observed_revision_demo.py')],
                          check=True,capture_output=True,text=True)
    assert f'schema v{CURRENT_SCHEMA_VERSION}' in result.stdout
    assert 'database reopen: PASS' in result.stdout
