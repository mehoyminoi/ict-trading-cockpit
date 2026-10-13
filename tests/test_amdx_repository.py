from concurrent.futures import ThreadPoolExecutor
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

from ict_cockpit.analysis.amdx import Anchor, Profile, Role, intraday_cycles
from ict_cockpit.analysis.amdx_rules import Condition, Definition, Fact, Operator, OutputKind, evaluate
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import TradingRun
from ict_cockpit.database.amdx_repository import AMDXRepository, StaleAMDXUpdate
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = datetime(2026, 10, 8, 9, 15, tzinfo=MARKET_TIMEZONE)
TABLES = ("amdx_cycle_identity", "amdx_definition_revision", "amdx_claim", "amdx_evaluation")


def saved_run(connection):
    day = TradingDay(futures_day_label="2026-10-08")
    process = TradingDaySession(blueprint_revision="synthetic-v1", mode_ids=["tda", "live-watch", "post-market"], current_mode_id="tda")
    TradingDaySessionRepository(connection).save(process)
    TradingDayRepository(connection).save(day)
    run = TradingRun(day.id, "Synthetic AMDX persistence", process.id)
    run.set_qt_context({"day": "D", "session": "M"})
    run.set_review_observed_qt_context({"day": "X(R)"}, "Legacy note")
    TradingSessionRunRepository(connection).save(run)
    return run


@pytest.fixture
def store(tmp_path):
    connection = open_application_database(tmp_path / "amdx database.db")
    run = saved_run(connection)
    yield connection, TradingSessionRunRepository(connection).amdx, run
    connection.close()


def choice(run, *, revision="1", role=Role.M, branch="working", channel="Expected", cycle=None, position=3, head=None):
    cycle = cycle or intraday_cycles(REFERENCE)[0]
    return dict(claim_id=f"claim-{revision}", run_id=run.id, branch_id=branch, channel=channel,
                cycle=cycle, quarter_id=cycle.quarters[position - 1].id,
                anchor=Anchor(f"anchor-{revision}", cycle.quarters[position - 1].id, role, "synthetic-technician") if role else None,
                recorded_at=REFERENCE + timedelta(minutes=int(revision)), market_reference=REFERENCE,
                expected_head_id=head)


def assessment(run, *, id="evaluation", revision="v1", role=Role.A, cycle=None, extra=()):
    cycle = cycle or intraday_cycles(REFERENCE)[0]
    condition = Condition(cycle.quarters[1].id, "synthetic-close-inside", Operator.EQ, True)
    rule = Definition("synthetic-rule", revision, "synthetic-plan", "Candidate", cycle.layer, 1,
                      OutputKind.ASSIGNED_ROLE, role, 0, (condition,), "Synthetic developer criterion")
    fact = Fact("synthetic-input", cycle.quarters[1].id, condition.key, True, "", REFERENCE, "synthetic-capture")
    return evaluate(evaluation_id=id, run_id=run.id, cycle=cycle, market_reference=REFERENCE,
                    definitions=tuple(extra) + (rule,), facts=(fact,))


def counts(connection):
    return tuple(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in TABLES)


def test_append_revisions_clear_and_reload_survive_connection_and_process_restart(store, tmp_path):
    connection, repo, run = store
    first = repo.accept(**choice(run))
    second = repo.accept(**choice(run, revision="2", role=Role.D, head=first.id))
    third = repo.accept(**choice(run, revision="3", role=None, head=second.id))
    stored = repo.save_evaluation(assessment(run), recorded_at=REFERENCE, basis_claim_id=second.id)
    before = repo.get_history(run.id)
    assert [c.inference.candidates for c in before.claims] == [
        (Profile.XAMD,), (Profile.AMDX,), (Profile.AMDX, Profile.XAMD),
    ]
    assert third.anchors == ()
    database = tmp_path / "amdx database.db"
    second_connection = open_application_database(database)
    try:
        second_repo = TradingSessionRunRepository(second_connection).amdx
        assert second_repo.get_history(run.id) == before
        assert second_repo.get_evaluation(stored.evaluation.id) == stored
    finally:
        second_connection.close()
    code = """import json,sys
from pathlib import Path
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
c = open_application_database(Path(sys.argv[1])); r = TradingSessionRunRepository(c).amdx
print(json.dumps({'history': r.get_history(sys.argv[2]).to_payload(), 'evaluation': r.get_evaluation('evaluation').evaluation.to_payload()})); c.close()
"""
    result = subprocess.run([sys.executable, "-c", code, str(database), run.id], cwd=ROOT,
                            env={**os.environ, "PYTHONPATH": str(ROOT / "src")}, capture_output=True, text=True, check=True)
    restored = json.loads(result.stdout)
    assert restored["history"] == before.to_payload()
    assert restored["evaluation"] == stored.evaluation.to_payload()


def test_identical_action_and_evaluation_retries_are_idempotent_but_identity_drift_rejects(store):
    connection, repo, run = store
    action = choice(run)
    first = repo.accept(**action)
    repo.accept(**choice(run, revision="2", role=Role.D, head=first.id))
    assert repo.accept(**action) == first  # retry after a newer revision cannot revise the head
    assert len(repo.get_history(run.id).claims) == 2
    with pytest.raises(ValueError, match="overwritten"):
        repo.accept(**{**action, "anchor": replace(action["anchor"], role=Role.D)})
    evaluation = assessment(run)
    stored = repo.save_evaluation(evaluation, recorded_at=REFERENCE)
    assert repo.save_evaluation(evaluation, recorded_at=REFERENCE) == stored
    with pytest.raises(ValueError, match="overwritten"):
        repo.save_evaluation(evaluation, recorded_at=REFERENCE + timedelta(seconds=1))
    assert len(repo.get_evaluations(run.id)) == 1


def test_scope_heads_isolate_channels_branches_cycles_and_runs_and_preserve_conflicts(store):
    connection, repo, run = store
    first = repo.accept(**choice(run, role=Role.A, position=1))
    conflict = repo.accept(**choice(run, revision="2", role=Role.A, position=2, head=first.id))
    assert conflict.inference.state == "Conflict"
    for i, kwargs in enumerate(({"channel": "Observed"}, {"branch": "alternative"},
                                {"cycle": intraday_cycles(REFERENCE)[1]}), 3):
        assert repo.accept(**choice(run, revision=str(i), **kwargs)).inference.candidates == (Profile.XAMD,)
    other = saved_run(connection)
    assert repo.get_history(other.id).claims == ()
    repo.accept(**choice(other, revision="6"))
    assert len(repo.get_history(run.id).claims) == 5
    assert len(repo.get_history(other.id).claims) == 1


def test_ordinary_stale_run_save_does_not_truncate_amdx_history(store):
    connection, repo, run = store
    legacy_before = connection.execute("SELECT * FROM trading_session_run WHERE id = ?", (run.id,)).fetchone()
    accepted = repo.accept(**choice(run))
    repo.save_evaluation(assessment(run), recorded_at=REFERENCE)
    assert connection.execute("SELECT * FROM trading_session_run WHERE id = ?", (run.id,)).fetchone() == legacy_before
    TradingSessionRunRepository(connection).save(run)
    assert repo.get_history(run.id).claims == (accepted,)
    assert len(repo.get_evaluations(run.id)) == 1


def test_missing_run_cross_owned_claim_and_wrong_evaluation_basis_reject_without_partial_writes(store):
    connection, repo, run = store
    with pytest.raises(ValueError, match="existing saved"):
        repo.accept(**{**choice(run), "run_id": "missing"})
    assert counts(connection) == (0, 0, 0, 0)
    first = repo.accept(**choice(run))
    other = saved_run(connection)
    with pytest.raises(ValueError, match="overwritten"):
        repo.accept(**choice(other))
    with pytest.raises(ValueError, match="this run and quartet"):
        repo.save_evaluation(assessment(other), recorded_at=REFERENCE, basis_claim_id=first.id)
    with pytest.raises(ValueError, match="this run and quartet"):
        repo.save_evaluation(assessment(run, cycle=intraday_cycles(REFERENCE)[1]), recorded_at=REFERENCE, basis_claim_id=first.id)
    assert counts(connection) == (1, 0, 1, 0)


def test_stale_writes_and_concurrent_connections_cannot_lose_an_accepted_revision(store, tmp_path):
    connection, repo, run = store
    barrier = Barrier(2)
    database = tmp_path / "amdx database.db"
    def worker(revision, role):
        c = open_application_database(database)
        try:
            r = AMDXRepository(c)
            assert r.get_history(run.id).claims == ()
            barrier.wait(timeout=10)
            try:
                return r.accept(**choice(run, revision=revision, role=role)).id
            except StaleAMDXUpdate:
                return "stale"
        finally:
            c.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [f.result(timeout=20) for f in (pool.submit(worker, "1", Role.M), pool.submit(worker, "2", Role.D))]
    assert results.count("stale") == 1
    first = repo.get_history(run.id).claims[0]
    with pytest.raises(StaleAMDXUpdate):
        repo.accept(**choice(run, revision="3"))
    assert repo.accept(**choice(run, revision="4", role=Role.D, head=first.id)).inference.candidates == (Profile.AMDX,)
    assert len(repo.get_history(run.id).claims) == 2


def test_definition_revision_content_is_protected_and_changed_methods_are_separate_evaluations(store):
    connection, repo, run = store
    original = assessment(run)
    repo.save_evaluation(original, recorded_at=REFERENCE)
    with pytest.raises(ValueError, match="new revision"):
        repo.save_evaluation(assessment(run, id="drift", role=Role.X), recorded_at=REFERENCE)
    newer = assessment(run, id="newer", revision="v2", role=Role.X)
    repo.save_evaluation(newer, recorded_at=REFERENCE)
    restored = repo.get_evaluations(run.id)
    assert [s.evaluation.profile().candidates for s in restored] == [(Profile.AMDX,), (Profile.XAMD,)]
    assert restored[0].evaluation.definitions == original.definitions
    assert counts(connection) == (1, 2, 0, 2)


@pytest.mark.parametrize("operation", ["claim", "evaluation", "definition-drift"])
def test_failed_append_rolls_back_cycle_definition_and_result_together(store, operation):
    connection, repo, run = store
    if operation == "definition-drift":
        original = assessment(run)
        repo.save_evaluation(original, recorded_at=REFERENCE)
        extra = replace(original.definitions[0], id="new-uncommitted")
        before = counts(connection)
        with pytest.raises(ValueError, match="new revision"):
            repo.save_evaluation(assessment(run, id="drift", role=Role.X, extra=(extra,)), recorded_at=REFERENCE)
    else:
        table = "amdx_claim" if operation == "claim" else "amdx_evaluation"
        connection.execute(f"CREATE TRIGGER injected_failure BEFORE INSERT ON {table} BEGIN SELECT RAISE(ABORT, 'injected failure'); END")
        before = counts(connection)
        with pytest.raises(sqlite3.IntegrityError, match="injected failure"):
            if operation == "claim":
                repo.accept(**choice(run))
            else:
                repo.save_evaluation(assessment(run), recorded_at=REFERENCE)
    assert counts(connection) == before
    assert not connection.in_transaction


def test_pending_caller_transaction_is_neither_committed_nor_rolled_back(store, tmp_path):
    connection, repo, run = store
    connection.execute("CREATE TABLE pending_marker (value TEXT)")
    connection.execute("INSERT INTO pending_marker VALUES ('caller work')")
    with pytest.raises(RuntimeError, match="pending transaction"):
        repo.accept(**choice(run))
    assert connection.in_transaction
    other = create_connection(tmp_path / "amdx database.db")
    assert other.execute("SELECT COUNT(*) FROM pending_marker").fetchone()[0] == 0
    other.close()
    connection.rollback()
    assert counts(connection) == (0, 0, 0, 0)


@pytest.mark.parametrize("table", TABLES)
@pytest.mark.parametrize("operation", ["UPDATE", "DELETE"])
def test_sql_updates_and_deletes_cannot_rewrite_history(store, table, operation):
    connection, repo, run = store
    repo.accept(**choice(run))
    repo.save_evaluation(assessment(run), recorded_at=REFERENCE)
    before = counts(connection)
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        with connection:
            connection.execute(f"{operation} {table} SET payload_json = '{{}}'" if operation == "UPDATE" else f"DELETE FROM {table}")
    assert counts(connection) == before
    with pytest.raises(sqlite3.IntegrityError):
        with connection:
            connection.execute("DELETE FROM trading_session_run WHERE id = ?", (run.id,))


@pytest.mark.parametrize("table", TABLES)
def test_sql_replace_cannot_bypass_append_only_guards(store, table):
    connection, repo, run = store
    repo.accept(**choice(run))
    repo.save_evaluation(assessment(run), recorded_at=REFERENCE)
    assert connection.execute("PRAGMA recursive_triggers").fetchone()[0] == 0
    before = connection.execute(f"SELECT * FROM {table}").fetchall()
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        with connection:
            connection.execute(f"INSERT OR REPLACE INTO {table} SELECT * FROM {table}")
    assert connection.execute(f"SELECT * FROM {table}").fetchall() == before


@pytest.mark.parametrize("table", ("amdx_claim", "amdx_evaluation"))
def test_replace_using_existing_sequence_with_a_new_identity_is_rejected(store, table):
    connection, repo, run = store
    repo.accept(**choice(run))
    repo.save_evaluation(assessment(run), recorded_at=REFERENCE)
    row = list(connection.execute(f"SELECT * FROM {table}").fetchone())
    row[1] = "new-id-same-sequence"
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        with connection:
            connection.execute(f"INSERT OR REPLACE INTO {table} VALUES ({','.join('?' for _ in row)})", row)


def test_foreign_key_and_read_validation_reject_cross_owned_and_broken_claim_chains(store):
    connection, repo, run = store
    first = repo.accept(**choice(run))
    other = saved_run(connection)
    proposal = repo.get_history(run.id).accept(**{k: v for k, v in choice(run, revision="2", head=first.id).items() if k != "expected_head_id"}).claims[-1]
    from ict_cockpit.analysis.amdx import payload
    encoded = json.dumps({"version": 1, "claim": payload(proposal)})
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        with connection:
            connection.execute("INSERT INTO amdx_claim (id, run_id, branch_id, channel, cycle_id, parent_claim_id, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (proposal.id, other.id, "working", "Expected", proposal.cycle.id, first.id, encoded))
    # External malformed inserts cannot silently become a valid working history.
    with connection:
        connection.execute("INSERT INTO amdx_claim (id, run_id, branch_id, channel, cycle_id, parent_claim_id, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (proposal.id, run.id, "working", "Expected", proposal.cycle.id, None, encoded))
    with pytest.raises(ValueError, match="revision chain"):
        repo.get_history(run.id)
    with pytest.raises(ValueError, match="revision chain"):
        repo.accept(**choice(run, revision="3", head=proposal.id))
    assert counts(connection)[2] == 2


def legacy_schema(connection):
    code = subprocess.check_output(["git", "show", "1b9ad6d9b7a882209f78f22ba6b6c737ea339dc1:src/ict_cockpit/database/schema.py"], cwd=ROOT, text=True)
    namespace = {}
    exec(compile(code, "accepted_v37_schema", "exec"), namespace)
    namespace["initialize_schema"](connection)


def test_actual_v37_schema_migrates_without_rewriting_legacy_rows_or_inventing_history(tmp_path):
    database = tmp_path / "legacy.db"
    connection = create_connection(database)
    legacy_schema(connection)
    run = saved_run(connection)
    before = connection.execute("SELECT * FROM trading_session_run WHERE id = ?", (run.id,)).fetchone()
    connection.close()
    connection = open_application_database(database)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION == 45
    assert connection.execute("SELECT * FROM trading_session_run WHERE id = ?", (run.id,)).fetchone() == before
    repo = TradingSessionRunRepository(connection)
    assert repo.get_by_id(run.id).qt_context == run.qt_context
    assert repo.get_by_id(run.id).review_observed_qt_context == run.review_observed_qt_context
    assert repo.amdx.get_history(run.id).claims == ()
    assert repo.amdx.get_evaluations(run.id) == ()
    repo.amdx.accept(**choice(run))
    initialize_schema(connection)
    assert len(repo.amdx.get_history(run.id).claims) == 1
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    connection.close()


def test_v38_migration_failure_rolls_back_all_new_ddl_and_version(tmp_path):
    connection = create_connection(tmp_path / "migration.db")
    legacy_schema(connection)
    def authorizer(action, name, *rest):
        return sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_CREATE_TRIGGER else sqlite3.SQLITE_OK
    connection.set_authorizer(authorizer)
    with pytest.raises(sqlite3.DatabaseError):
        initialize_schema(connection)
    connection.set_authorizer(None)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 37
    assert connection.execute("SELECT name FROM sqlite_master WHERE name LIKE 'amdx_%'").fetchall() == []
    initialize_schema(connection)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION
    connection.close()


def test_reused_cycle_identity_and_inconsistent_result_object_are_rejected(store):
    connection, repo, run = store
    repo.accept(**choice(run))
    other = saved_run(connection)
    day = intraday_cycles(REFERENCE)[0]
    changed = replace(day, quarters=tuple(replace(q, start=q.start + timedelta(days=1), end=q.end + timedelta(days=1)) for q in day.quarters))
    with pytest.raises(ValueError, match="different temporal"):
        repo.accept(**choice(other, revision="2", cycle=changed))
    evaluation = assessment(run)
    with pytest.raises(ValueError, match="disagrees"):
        repo.save_evaluation(replace(evaluation, governing_rule_ids=()), recorded_at=REFERENCE)
    assert counts(connection) == (1, 0, 1, 0)


def test_disposable_persistence_demo_exercises_real_repositories():
    result = subprocess.run([sys.executable, str(ROOT / "tools/amdx_persistence_demo.py")], cwd=ROOT,
                            capture_output=True, text=True, check=True)
    assert f"schema v{CURRENT_SCHEMA_VERSION}" in result.stdout
    assert "both revisions survive database reopen" in result.stdout
    assert "Foreign-key consistency: PASS" in result.stdout


def test_working_mixed_history_and_receipts_survive_restart(store, tmp_path):
    connection, repo, run = store
    first = repo.accept(**choice(run, role=Role.A, position=1))
    old_conflict = repo.accept(**choice(run, revision="2", role=Role.A, position=2, head=first.id))
    old_rows = connection.execute("SELECT * FROM amdx_claim ORDER BY sequence").fetchall()
    result = repo.revise_working(**choice(run, revision="3", head=old_conflict.id))
    assert result.changed and result.claim.inference.candidates == (Profile.XAMD,)
    assert connection.execute("SELECT * FROM amdx_claim ORDER BY sequence LIMIT 2").fetchall() == old_rows
    before = repo.get_history(run.id)
    reopened = open_application_database(tmp_path / "amdx database.db")
    try:
        other = AMDXRepository(reopened)
        assert other.get_history(run.id) == before
        assert before.claims[1].inference.state == "Conflict"
        assert other.revise_working(**choice(run, revision="3", head=old_conflict.id)) == result
    finally:
        reopened.close()
    code = """import json,sys
from pathlib import Path
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.amdx_repository import AMDXRepository
c=open_application_database(Path(sys.argv[1]));print(json.dumps(AMDXRepository(c).get_history(sys.argv[2]).to_payload()));c.close()
"""
    actual = subprocess.run([sys.executable,"-c",code,str(tmp_path / "amdx database.db"),run.id],
                            env={**os.environ,"PYTHONPATH":str(ROOT / "src")},capture_output=True,text=True,check=True)
    assert json.loads(actual.stdout) == before.to_payload()


def test_noop_receipts_reserve_identity_and_return_original_result_after_later_changes(store):
    connection, repo, run = store
    first = repo.revise_working(**choice(run))
    same = choice(run, revision="2", head=first.claim.id)
    noop = repo.revise_working(**same)
    assert not noop.changed and noop.claim == first.claim
    changed = repo.revise_working(**choice(run,revision="3",role=Role.D,head=first.claim.id))
    assert changed.changed
    assert repo.revise_working(**same) == noop
    assert repo.revise_working(**choice(run)) == first
    assert len(repo.get_history(run.id).claims) == 2
    assert connection.execute("SELECT COUNT(*) FROM amdx_working_command").fetchone()[0] == 3
    with pytest.raises(ValueError,match="overwritten"):
        repo.revise_working(**{**same,"anchor":replace(same["anchor"],role=Role.D)})
    with pytest.raises(ValueError,match="working command identity"):
        repo.accept(**same)
    with pytest.raises(StaleAMDXUpdate):
        repo.revise_working(**choice(run,revision="4",head=first.claim.id,role=Role.D))
    with pytest.raises(ValueError,match="structurally valid"):
        repo.revise_working(**choice(run,revision="5",head=changed.claim.id,role=Role.A))
    assert len(repo.get_history(run.id).claims) == 2


def test_empty_clear_noop_has_durable_idempotent_receipt_without_inventing_a_claim(store):
    connection, repo, run = store
    clear = choice(run,role=None)
    result = repo.revise_working(**clear)
    assert not result.changed and result.claim is None
    first = repo.revise_working(**choice(run,revision="2"))
    assert first.changed and repo.revise_working(**clear) == result
    assert len(repo.get_history(run.id).claims) == 1


def test_evaluation_keeps_its_explicit_v2_basis_after_later_working_revision(store):
    connection, repo, run = store
    first = repo.revise_working(**choice(run))
    evaluation = repo.save_evaluation(assessment(run),recorded_at=REFERENCE,basis_claim_id=first.claim.id)
    repo.revise_working(**choice(run,revision='2',role=Role.D,head=first.claim.id))
    assert repo.get_evaluation(evaluation.evaluation.id) == evaluation
    assert evaluation.basis_claim_id == first.claim.id


def test_receipt_insert_failure_rolls_back_claim_cycle_and_command_together(store):
    connection, repo, run = store
    connection.execute("CREATE TRIGGER fail_receipt BEFORE INSERT ON amdx_working_command BEGIN SELECT RAISE(ABORT,'fixture receipt failure'); END")
    with pytest.raises(sqlite3.IntegrityError,match="receipt failure"):
        repo.revise_working(**choice(run))
    assert counts(connection) == (0,0,0,0)
    assert connection.execute("SELECT COUNT(*) FROM amdx_working_command").fetchone()[0] == 0
    connection.execute("DROP TRIGGER fail_receipt")
    first = repo.revise_working(**choice(run))
    connection.execute("CREATE TRIGGER fail_receipt BEFORE INSERT ON amdx_working_command BEGIN SELECT RAISE(ABORT,'fixture receipt failure'); END")
    with pytest.raises(sqlite3.IntegrityError):
        repo.revise_working(**choice(run,revision="2",role=Role.D,head=first.claim.id))
    assert repo.get_history(run.id).claims == (first.claim,)


@pytest.mark.parametrize("operation", ["UPDATE", "DELETE", "REPLACE"])
def test_working_receipts_are_sql_immutable_including_noops(store, operation):
    connection, repo, run = store
    first = repo.revise_working(**choice(run))
    repo.revise_working(**choice(run,revision="2",head=first.claim.id))
    before = connection.execute("SELECT * FROM amdx_working_command ORDER BY id").fetchall()
    sql = {"UPDATE":"UPDATE amdx_working_command SET changed=0",
           "DELETE":"DELETE FROM amdx_working_command",
           "REPLACE":"INSERT OR REPLACE INTO amdx_working_command SELECT * FROM amdx_working_command"}[operation]
    with pytest.raises(sqlite3.IntegrityError,match="immutable"):
        with connection:
            connection.execute(sql)
    assert connection.execute("SELECT * FROM amdx_working_command ORDER BY id").fetchall() == before


def test_working_two_writer_contention_cannot_partially_retire_or_duplicate(store, tmp_path):
    connection, repo, run = store
    first = repo.revise_working(**choice(run,role=Role.A,position=1))
    barrier = Barrier(2)
    def worker(revision, role):
        c = open_application_database(tmp_path / "amdx database.db")
        try:
            other = AMDXRepository(c)
            barrier.wait(timeout=10)
            try:
                return other.revise_working(**choice(run,revision=revision,role=role,head=first.claim.id)).claim
            except StaleAMDXUpdate:
                return None
        finally:
            c.close()
    with ThreadPoolExecutor(max_workers=2) as workers:
        futures = [workers.submit(worker,"2",Role.M),workers.submit(worker,"3",Role.D)]
        outcomes = [f.result(timeout=15) for f in futures]
    assert sum(result is not None for result in outcomes) == 1
    assert len(repo.get_history(run.id).claims) == 2
    assert connection.execute("SELECT COUNT(*) FROM amdx_working_command").fetchone()[0] == 2


def test_tampered_noop_receipt_cannot_claim_a_phase_change_was_unchanged(store):
    connection, repo, run = store
    first = repo.revise_working(**choice(run))
    command = choice(run,revision="2",head=first.claim.id)
    repo.revise_working(**command)
    encoded = json.loads(connection.execute("SELECT payload_json FROM amdx_working_command WHERE id=?",(command["claim_id"],)).fetchone()[0])
    encoded["anchor"]["role"] = "D"
    connection.execute("DROP TRIGGER amdx_working_command_no_update")
    with connection:
        connection.execute("UPDATE amdx_working_command SET payload_json=? WHERE id=?",
                           (json.dumps(encoded,sort_keys=True,separators=(',',':')),command["claim_id"]))
    with pytest.raises(ValueError,match="action basis"):
        repo.revise_working(**{**command,"anchor":replace(command["anchor"],role=Role.D)})


def test_v38_migration_preserves_claim_bytes_guards_old_reader_and_rolls_back_failed_receipts(tmp_path):
    from ict_cockpit.analysis.amdx import InterpretationHistory, claim_payload, payload
    database = tmp_path / 'legacy-v38.db'
    connection = create_connection(database)
    old_code = subprocess.check_output(['git','show','4346c88b7d8a6b98e1dd776b12c41845ae35598a:src/ict_cockpit/database/schema.py'],cwd=ROOT,text=True)
    old = {}
    exec(compile(old_code,'v38-schema','exec'),old)
    old['initialize_schema'](connection)
    run = saved_run(connection)
    history = InterpretationHistory()
    for arguments in (choice(run,role=Role.A,position=1),choice(run,revision='2',role=Role.A,position=2)):
        history = history.accept(**{k:v for k,v in arguments.items() if k != 'expected_head_id'})
    connection.execute('INSERT INTO amdx_cycle_identity VALUES (?,?)',(history.claims[0].cycle.id,json.dumps(payload(history.claims[0].cycle),sort_keys=True,separators=(',',':'))))
    for i, claim in enumerate(history.claims):
        connection.execute('INSERT INTO amdx_claim(id,run_id,branch_id,channel,cycle_id,parent_claim_id,payload_json) VALUES (?,?,?,?,?,?,?)',
                           (claim.id,run.id,claim.branch_id,claim.channel,claim.cycle.id,history.claims[i-1].id if i else None,
                            json.dumps({'version':1,'claim':claim_payload(claim)},sort_keys=True,separators=(',',':'))))
    connection.commit()
    original = connection.execute('SELECT * FROM amdx_claim ORDER BY sequence').fetchall()
    connection.set_authorizer(lambda action,*_: sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_CREATE_TRIGGER else sqlite3.SQLITE_OK)
    with pytest.raises(sqlite3.DatabaseError):
        initialize_schema(connection)
    connection.set_authorizer(None)
    assert connection.execute('PRAGMA user_version').fetchone()[0] == 38
    assert not connection.execute("SELECT name FROM sqlite_master WHERE name LIKE 'amdx_working_command%'").fetchall()
    initialize_schema(connection)
    assert connection.execute('PRAGMA user_version').fetchone()[0] == CURRENT_SCHEMA_VERSION
    assert connection.execute('SELECT * FROM amdx_claim ORDER BY sequence').fetchall() == original
    repo = AMDXRepository(connection)
    assert repo.get_history(run.id) == history
    with pytest.raises(RuntimeError,match=f'Unsupported database schema version: {CURRENT_SCHEMA_VERSION}'):
        old['initialize_schema'](connection)
    revised = repo.revise_working(**choice(run,revision='3',head=history.claims[-1].id))
    assert revised.claim.inference.candidates == (Profile.XAMD,)
    assert connection.execute('SELECT * FROM amdx_claim ORDER BY sequence LIMIT 2').fetchall() == original
    assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
    connection.close()
