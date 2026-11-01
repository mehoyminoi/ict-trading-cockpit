"""Durable explicit Review references, transaction boundaries and migration."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from threading import Barrier

import pytest

from ict_cockpit.analysis.amdx import Anchor, Role, intraday_cycles
from ict_cockpit.analysis.amdx_review import ReviewHistory, StaleComparison
from ict_cockpit.database.amdx_repository import AMDXRepository, StaleAMDXUpdate
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from test_amdx_repository import REFERENCE, choice, saved_run


ROOT = Path(__file__).resolve().parents[1]
DAY, SESSION = intraday_cycles(REFERENCE)


@pytest.fixture
def store(tmp_path):
    connection = open_application_database(tmp_path / "review.db")
    run = saved_run(connection)
    repo = TradingSessionRunRepository(connection).amdx
    repo.revise_working(**choice(run, role=Role.D))
    yield connection, repo, run
    connection.close()


def observed(run, *, number=2, comparison="P1", basis="claim-1", pair_head=None, observed_head=None,
             cycle=DAY, role=Role.M, branch="working"):
    args = choice(run, revision=str(number), role=role, cycle=cycle, branch=branch)
    args.pop("channel")
    args.pop("expected_head_id")
    return dict(**args, comparison_id=comparison, expected_claim_id=basis,
                expected_comparison_head_id=pair_head, expected_observed_head_id=observed_head)


def pairing(run, *, id="P2", basis="claim-1", observed="claim-2", head="P1", minutes=10):
    return dict(run_id=run.id, comparison_id=id, expected_claim_id=basis,
                observed_claim_id=observed, expected_head_id=head,
                recorded_at=REFERENCE + timedelta(minutes=minutes), market_reference=REFERENCE)


def counts(connection):
    return tuple(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                 for table in ("amdx_cycle_identity", "amdx_claim", "amdx_comparison", "amdx_review_command"))


def test_atomic_observation_pair_and_alternate_survive_run_save_reopen_and_separate_process(store, tmp_path):
    connection, repo, run = store
    original_claims = connection.execute("SELECT * FROM amdx_claim").fetchall()
    original_run = connection.execute("SELECT * FROM trading_session_run").fetchall()
    p1 = repo.review.record_observation(**observed(run))
    repo.revise_working(**choice(run, revision="3", head="claim-1", role=Role.M))
    p2 = repo.review.record_comparison(**pairing(run, basis="claim-3"))
    assert p2.previous_comparison_id == p1.id
    review = repo.review.get_history(run.id)
    assert review.summarize("P1").order_relation == "Different order"
    assert review.summarize("P2").order_relation == "Same order"
    assert connection.execute("SELECT * FROM amdx_claim LIMIT 1").fetchall() == original_claims
    assert connection.execute("SELECT * FROM trading_session_run").fetchall() == original_run
    TradingSessionRunRepository(connection).save(run)
    assert repo.review.get_history(run.id) == review
    assert repo.review.record_observation(**observed(run)) == p1
    assert repo.review.record_comparison(**pairing(run, basis="claim-3")) == p2
    assert counts(connection) == (1, 3, 2, 2)
    assert ReviewHistory.from_payload(review.to_payload()) == review
    reopened = open_application_database(tmp_path / "review.db")
    assert AMDXRepository(reopened).review.get_history(run.id) == review
    assert AMDXRepository(reopened).review.get_comparison("P1") == p1
    assert AMDXRepository(reopened).review.get_comparison("missing") is None
    reopened.close()
    code = ('from pathlib import Path; from ict_cockpit.database.bootstrap import open_application_database; '
            'from ict_cockpit.database.amdx_repository import AMDXRepository; '
            f'c=open_application_database(Path({str(tmp_path / "review.db")!r})); '
            f'h=AMDXRepository(c).review.get_history({run.id!r}); '
            'print(h.summarize("P1").order_relation,h.summarize("P2").order_relation); c.close()')
    result = subprocess.run([sys.executable, "-c", code], check=True, text=True, capture_output=True,
                            env={**os.environ, "PYTHONPATH": str(ROOT / "src")})
    assert result.stdout.strip() == "Different order Same order"


def test_missing_baseline_and_later_expectation_are_not_retargeted(store):
    connection, repo, run = store
    p1 = repo.review.record_observation(**observed(run, basis=None))
    repo.revise_working(**choice(run, revision="3", head="claim-1", role=Role.M))
    assert repo.review.get_comparison(p1.id).expected_claim_id is None
    assert repo.review.get_history(run.id).summarize(p1.id).order_relation == "No expected baseline"
    before = counts(connection)
    with pytest.raises(ValueError, match="identity"):
        repo.review.record_observation(**observed(run, basis="claim-3"))
    assert counts(connection) == before


@pytest.mark.parametrize("change", [
    {"expected_claim_id": None}, {"expected_comparison_head_id": "P1"},
    {"expected_observed_head_id": "claim-2"}, {"comparison_id": "P2"},
])
def test_bundle_identity_or_original_basis_cannot_drift(store, change):
    connection, repo, run = store
    repo.review.record_observation(**observed(run))
    before = counts(connection)
    with pytest.raises(ValueError):
        repo.review.record_observation(**{**observed(run), **change})
    assert counts(connection) == before


def test_stale_observed_or_comparison_head_rolls_back_without_partial_claim(store):
    connection, repo, run = store
    repo.review.record_observation(**observed(run))
    before = counts(connection)
    with pytest.raises(StaleAMDXUpdate):
        repo.review.record_observation(**observed(run, number=3, comparison="P2", pair_head="P1"))
    with pytest.raises(StaleComparison):
        repo.review.record_observation(**observed(run, number=3, comparison="P2", observed_head="claim-2"))
    with pytest.raises(StaleComparison):
        repo.review.record_comparison(**pairing(run, head=None))
    assert counts(connection) == before
    assert repo.review.record_observation(**observed(run, number=3, comparison="P2", pair_head="P1",
                                                   observed_head="claim-2")).id == "P2"


@pytest.mark.parametrize("target", ["amdx_claim", "amdx_comparison", "amdx_review_command"])
def test_failed_atomic_insert_rolls_back_new_cycle_observation_pair_and_receipt(store, target):
    connection, repo, run = store
    before = counts(connection)
    connection.execute(f"CREATE TRIGGER fail_insert BEFORE INSERT ON {target} BEGIN SELECT RAISE(ABORT, 'injected'); END")
    with pytest.raises(sqlite3.IntegrityError, match="injected"):
        repo.review.record_observation(**observed(run, cycle=SESSION, basis=None))
    assert counts(connection) == before
    assert not connection.in_transaction
    connection.execute("DROP TRIGGER fail_insert")
    pair = repo.review.record_observation(**observed(run, cycle=SESSION, basis=None))
    assert pair.cycle_id == SESSION.id


@pytest.mark.parametrize("table", ["amdx_comparison", "amdx_review_command"])
@pytest.mark.parametrize("operation", ["UPDATE", "DELETE", "REPLACE"])
def test_review_records_cannot_be_mutated_by_sql(store, table, operation):
    connection, repo, run = store
    repo.review.record_observation(**observed(run))
    original = repo.review.get_history(run.id)
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        with connection:
            if operation == "UPDATE":
                connection.execute(f"UPDATE {table} SET payload_json='{{}}' WHERE id='P1'")
            elif operation == "DELETE":
                connection.execute(f"DELETE FROM {table} WHERE id='P1'")
            else:
                connection.execute(f"INSERT OR REPLACE INTO {table} SELECT * FROM {table} WHERE id='P1'")
    assert repo.review.get_history(run.id) == original


def test_sequence_collision_and_source_deletion_are_protected(store):
    connection, repo, run = store
    repo.review.record_observation(**observed(run))
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        with connection:
            connection.execute("""INSERT OR REPLACE INTO amdx_comparison
                SELECT sequence, 'other', run_id, branch_id, cycle_id, expected_claim_id,
                       observed_claim_id, parent_comparison_id, payload_json FROM amdx_comparison""")
    with pytest.raises(sqlite3.IntegrityError):
        with connection:
            connection.execute("DELETE FROM trading_session_run WHERE id=?", (run.id,))
    assert repo.review.get_history(run.id).comparisons[0].id == "P1"


def test_changed_pair_retry_wrong_operation_and_cross_action_ids_are_rejected(store):
    connection, repo, run = store
    p1 = repo.review.record_observation(**observed(run))
    repo.review.record_comparison(**pairing(run))
    before = counts(connection)
    with pytest.raises(ValueError, match="identity"):
        repo.review.record_comparison(**pairing(run, basis=None))
    with pytest.raises(ValueError, match="identity"):
        repo.review.record_comparison(**pairing(run, id=p1.id, head=None))
    for id in ("P1", "P2"):
        with pytest.raises(ValueError, match="Review identity"):
            repo.accept(**{**choice(run, revision="3"), "claim_id": id})
        with pytest.raises(ValueError, match="Review identity"):
            repo.revise_working(**{**choice(run, revision="3", head="claim-1"), "claim_id": id})
    with pytest.raises(ValueError, match="identity"):
        repo.review.record_comparison(**pairing(run, id="claim-1"))
    # A no-op identity has no profile claim but is still unavailable to Review.
    repo.revise_working(**choice(run, revision="3", head="claim-1", role=Role.D))
    with pytest.raises(ValueError, match="identity"):
        repo.review.record_comparison(**pairing(run, id="claim-3"))
    assert counts(connection) == before


@pytest.mark.parametrize("scope", ["run", "branch", "cycle", "channel"])
def test_wrong_expected_scope_rolls_back_observation_and_pair(store, scope):
    connection, repo, run = store
    other = saved_run(connection) if scope == "run" else run
    args = choice(other, revision="4", branch="alternative" if scope == "branch" else "working",
                  cycle=SESSION if scope == "cycle" else DAY,
                  channel="Observed" if scope == "channel" else "Expected")
    repo.accept(**args)
    before = counts(connection)
    with pytest.raises(ValueError, match="Expected claim" if scope == "channel" else "basis|same run"):
        repo.review.record_observation(**observed(run, basis="claim-4", number=5,
                                                   observed_head="claim-4" if scope == "channel" else None))
    assert counts(connection) == before


def test_caller_transaction_is_neither_committed_nor_rolled_back(store):
    connection, repo, run = store
    connection.execute("INSERT INTO amdx_cycle_identity VALUES ('caller', '{}')")
    with pytest.raises(RuntimeError, match="pending transaction"):
        repo.review.record_observation(**observed(run))
    assert connection.in_transaction
    assert repo.review.get_history(run.id).comparisons == ()
    assert connection.in_transaction
    assert connection.execute("SELECT id FROM amdx_cycle_identity WHERE id='caller'").fetchone() == ("caller",)
    connection.rollback()
    assert repo.review.get_history(run.id).comparisons == ()


def test_two_writers_cannot_accept_the_same_inspected_heads_twice(store, tmp_path):
    connection, repo, run = store
    barrier = Barrier(2)
    def writer(number):
        local = open_application_database(tmp_path / "review.db")
        try:
            barrier.wait(timeout=5)
            return AMDXRepository(local).review.record_observation(
                **observed(run, number=number, comparison=f"P{number}"))
        except (StaleAMDXUpdate, StaleComparison) as error:
            return error
        finally:
            local.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(writer, (2, 3)))
    assert sum(isinstance(r, (StaleAMDXUpdate, StaleComparison)) for r in results) == 1
    assert counts(connection) == (1, 2, 1, 1)
    assert len(repo.review.get_history(run.id).comparisons) == 1


def test_two_writers_retrying_the_same_bundle_receive_one_original_result(store, tmp_path):
    connection, repo, run = store
    barrier = Barrier(2)
    def writer(_):
        local = open_application_database(tmp_path / "review.db")
        try:
            barrier.wait(timeout=5)
            return AMDXRepository(local).review.record_observation(**observed(run))
        finally:
            local.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(writer, (1, 2)))
    assert results[0] == results[1] == repo.review.get_comparison("P1")
    assert counts(connection) == (1, 2, 1, 1)


@pytest.mark.parametrize("table,field,value", [
    ("amdx_comparison", "run_id", "other"),
    ("amdx_review_command", "payload_json", "{}"),
    ("amdx_review_command", "operation", "Pair"),
])
def test_inconsistent_stored_metadata_or_receipts_fail_on_reload(store, table, field, value):
    connection, repo, run = store
    repo.review.record_observation(**observed(run))
    # Controlled corruption after disabling write protection, not a supported action.
    connection.execute(f"DROP TRIGGER {table}_no_update")
    with connection:
        if field == "run_id":
            # Change ownership inside the payload; SQL run stays intact.
            raw = json.loads(connection.execute("SELECT payload_json FROM amdx_comparison").fetchone()[0])
            raw["comparison"][field] = value
            connection.execute("UPDATE amdx_comparison SET payload_json=?", (json.dumps(raw),))
        else:
            connection.execute(f"UPDATE {table} SET {field}=?", (value,))
    with pytest.raises(ValueError):
        repo.review.get_history(run.id)


def test_missing_receipt_and_inconsistent_predecessor_are_not_silently_repaired(store):
    connection, repo, run = store
    repo.review.record_observation(**observed(run))
    connection.execute("DROP TRIGGER amdx_review_command_no_delete")
    with connection:
        connection.execute("DELETE FROM amdx_review_command")
    with pytest.raises(ValueError, match="receipts"):
        repo.review.get_history(run.id)


def test_v39_migration_preserves_claim_receipt_and_run_bytes_and_guards_old_reader(tmp_path):
    old_schema = {}
    code = subprocess.check_output(['git','show','d940138:src/ict_cockpit/database/schema.py'],cwd=ROOT,text=True)
    exec(compile(code,'archived-v39-schema','exec'),old_schema)
    connection = create_connection(tmp_path / "legacy-v39.db")
    old_schema['initialize_schema'](connection)
    run = saved_run(connection)
    old_repo = {}
    code = subprocess.check_output(['git','show','d940138:src/ict_cockpit/database/amdx_repository.py'],cwd=ROOT,text=True)
    exec(compile(code,'archived-v39-repository','exec'),old_repo)
    legacy = old_repo['AMDXRepository'](connection)
    legacy.revise_working(**choice(run, role=Role.D))
    legacy.revise_working(**choice(run, revision="2", role=Role.D, head="claim-1"))
    tables=("trading_session_run", "amdx_claim", "amdx_working_command", "amdx_cycle_identity")
    before={table: connection.execute(f"SELECT * FROM {table}").fetchall() for table in tables}
    connection.set_authorizer(lambda action,*args: sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_CREATE_TRIGGER else sqlite3.SQLITE_OK)
    with pytest.raises(sqlite3.DatabaseError):
        initialize_schema(connection)
    connection.set_authorizer(None)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 39
    assert not connection.execute("SELECT name FROM sqlite_master WHERE name LIKE 'amdx_review_%' OR name LIKE 'amdx_comparison%'").fetchall()
    initialize_schema(connection)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION == 47
    for table in tables:
        assert connection.execute(f"SELECT * FROM {table}").fetchall() == before[table]
    with pytest.raises(RuntimeError, match=f"Unsupported database schema version: {CURRENT_SCHEMA_VERSION}"):
        old_schema['initialize_schema'](connection)
    repo=AMDXRepository(connection)
    assert repo.review.get_history(run.id).comparisons == ()
    assert repo.revise_working(**choice(run, revision="2", role=Role.D, head="claim-1")).changed is False
    repo.review.record_observation(**observed(run, number=3))
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    initialize_schema(connection)
    assert len(repo.review.get_history(run.id).comparisons) == 1
    connection.close()


def test_disposable_persistence_demo_checks_reopen_and_exact_retry():
    result = subprocess.run([sys.executable, str(ROOT / "tools" / "amdx_review_persistence_demo.py")],
                            text=True, capture_output=True, check=True)
    assert f"schema v{CURRENT_SCHEMA_VERSION}" in result.stdout
    assert "database reopen: PASS" in result.stdout


def test_read_snapshot_remains_consistent_if_another_writer_commits_between_queries(store, tmp_path, monkeypatch):
    connection, repo, run = store
    other = open_application_database(tmp_path / "review.db")
    original = repo.get_history
    committed = False
    def overlapping_read(run_id):
        nonlocal committed
        source = original(run_id)
        if not committed:
            committed = True
            AMDXRepository(other).review.record_observation(**observed(run))
        return source
    monkeypatch.setattr(repo, "get_history", overlapping_read)
    try:
        # The first read must be wholly before the external commit, not a mix
        # of old source claims and a newer comparison pointing to an absent O1.
        assert repo.review.get_history(run.id).comparisons == ()
        assert not connection.in_transaction
        assert repo.review.get_history(run.id).comparisons[0].observed_claim_id == "claim-2"
    finally:
        other.close()


def test_observed_clear_preserves_original_pair_and_nullable_meaning(store):
    connection, repo, run = store
    original = repo.review.record_observation(**observed(run))
    cleared = repo.review.record_observation(**observed(run, number=3, comparison="P2", role=None,
                                                       pair_head="P1", observed_head="claim-2"))
    history = repo.review.get_history(run.id)
    assert history.summarize(original.id).order_relation == "Different order"
    assert history.summarize(cleared.id).order_relation == "Not comparable"
    assert history.claim(cleared.observed_claim_id).action == "Clear"
    assert history.claim(original.observed_claim_id).anchors[0].role is Role.M
