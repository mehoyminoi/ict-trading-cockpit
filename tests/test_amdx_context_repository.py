"""Higher entry ownership, atomic provenance, receipts and actual reload."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess
import sys
from threading import Barrier

import pytest

from ict_cockpit.analysis.amdx import Profile, Role, XSubtype, payload
from ict_cockpit.analysis.amdx_context import HIGHER_LEVELS
from ict_cockpit.analysis.amdx_review import StaleComparison
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, build_market_time_context
from ict_cockpit.database.amdx_context_repository import AMDXContextRepository
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from test_amdx_repository import saved_run
from test_amdx_context_widget import cockpit, close


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = datetime(2026, 10, 8, 9, 15, tzinfo=MARKET_TIMEZONE)
TABLES = ("amdx_cycle_identity", "amdx_claim", "amdx_working_command",
          "amdx_comparison", "amdx_observed_command", "amdx_review_command")


@pytest.fixture
def store(tmp_path):
    path = tmp_path / "higher.db"
    connection = open_application_database(path)
    run = saved_run(connection)
    run.market_context_snapshot = {"reference_market_time": REFERENCE.isoformat()}
    run.market_time_context = build_market_time_context(REFERENCE).to_dict()
    run.qt_context = {"quarter": "D", "month": "A"}
    run.review_observed_qt_context = {"quarter": "M"}
    owner = TradingSessionRunRepository(connection)
    owner.save(run)
    yield connection, owner.amdx, run, path
    connection.close()


def snapshot(repo, run, channel="Expected", reference=REFERENCE):
    return repo.context.load_stack(run.id, channel=channel,
        **({"reference": reference} if channel == "Expected" else {}))


def target(repo, run, channel="Expected", level="year", position=3, reference=REFERENCE):
    return repo.context.prepare_target(snapshot(repo, run, channel, reference), level, position)


def write(repo, pinned, revision="1", role=Role.M, **extra):
    args = dict(claim_id="claim-" + revision, recorded_at=REFERENCE + timedelta(minutes=1), role=role)
    if role is not None:
        args.update(anchor_id="anchor-" + revision, source_ref="synthetic-operator")
    if pinned.channel == "Observed":
        args["comparison_id"] = "pair-" + revision
    args.update(extra)
    return repo.context.revise(pinned, **args)


def counts(connection):
    return tuple(connection.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES)


def run_bytes(connection, id):
    return connection.execute("SELECT * FROM trading_session_run WHERE id=?", (id,)).fetchone()


@pytest.mark.parametrize("channel", ["Expected", "Observed"])
@pytest.mark.parametrize("level", HIGHER_LEVELS)
def test_each_higher_cycle_records_one_entry_and_restores_without_legacy_rewrite(store, channel, level):
    connection, repo, run, path = store
    original = run_bytes(connection, run.id)
    first = write(repo, target(repo, run, channel, level))
    assert first.changed and first.claim.inference.candidates == (Profile.XAMD,)
    assert first.claim.action_quarter_id.endswith(":Q3")
    reopened = open_application_database(path)
    try:
        restored = TradingSessionRunRepository(reopened).amdx
        view = snapshot(restored, run, channel)
        row = next(r for r in view.projection.cycles if r.context.cycle.layer == level)
        assert row.claim == first.claim
        assert row.inference.roles[2].origin == "Technician"
        assert all(r.origin == "Implied" for i, r in enumerate(row.inference.roles) if i != 2)
        assert run_bytes(reopened, run.id) == original
        assert reopened.execute("PRAGMA user_version").fetchone()[0] == 45
    finally:
        reopened.close()
    assert run_bytes(connection, run.id) == original
    assert len(repo.get_history(run.id).claims) == 1
    if channel == "Observed":
        assert first.comparison.expected_claim_id is None


def test_working_and_observed_higher_channels_and_other_runs_remain_independent(store):
    connection, repo, run, _ = store
    working = write(repo, target(repo, run), role=Role.D)
    observed = write(repo, target(repo, run, "Observed"), revision="2", role=Role.M)
    other = saved_run(connection)
    for channel, expected in (("Expected", working.claim), ("Observed", observed.claim)):
        row = snapshot(repo, run, channel).projection.cycles[2]
        assert row.claim == expected
    other_view = snapshot(repo, other).projection
    assert all(r.claim is None for r in other_view.cycles)
    assert observed.comparison.expected_claim_id is None


def test_current_clock_changes_do_not_retarget_saved_observed_higher_reference(store):
    connection, repo, run, _ = store
    original = snapshot(repo, run, "Observed")
    run.market_time_context = build_market_time_context(
        datetime(2027, 1, 5, 9, 15, tzinfo=MARKET_TIMEZONE)).to_dict()
    TradingSessionRunRepository(connection).save(run)
    restored = snapshot(repo, run, "Observed")
    assert restored.projection.reference == original.projection.reference == REFERENCE
    assert restored.projection.cycles == original.projection.cycles
    with pytest.raises(ValueError, match="not a caller clock"):
        repo.context.load_stack(run.id, channel="Observed", reference=REFERENCE)


@pytest.mark.parametrize("value", [None, "", "2026-10-08T09:15:00", "bad", 42])
def test_missing_malformed_original_reference_disables_higher_observed_without_day_fallback(store, value):
    connection, repo, run, _ = store
    run.market_context_snapshot = {"reference_market_time": value}
    TradingSessionRunRepository(connection).save(run)
    before = run_bytes(connection, run.id), counts(connection)
    with pytest.raises(ValueError, match="run-start"):
        snapshot(repo, run, "Observed")
    assert (run_bytes(connection, run.id), counts(connection)) == before
    assert not connection.in_transaction
    assert snapshot(repo, run).projection.reference == REFERENCE


@pytest.mark.parametrize("channel", ["Expected", "Observed"])
def test_exact_no_op_retry_returns_original_nullable_result_after_later_entry(store, channel):
    connection, repo, run, _ = store
    inspected = target(repo, run, channel)
    first = write(repo, inspected, role=None)
    assert first.claim is None and not first.changed
    later = write(repo, inspected, revision="2")
    assert later.changed
    after = counts(connection)
    assert write(repo, inspected, role=None) == first
    assert counts(connection) == after
    repeat_target = target(repo, run, channel)
    same = write(repo, repeat_target, revision="3")
    assert not same.changed and same.claim == later.claim
    with pytest.raises(ValueError, match="cannot be overwritten or reused"):
        write(repo, inspected, role=Role.D)


@pytest.mark.parametrize("channel", ["Expected", "Observed"])
def test_exact_committed_retry_survives_later_reference_or_resolver_changes(store, channel, monkeypatch):
    connection, repo, run, _ = store
    inspected = target(repo, run, channel)
    first = write(repo, inspected)
    run.market_context_snapshot = {"reference_market_time": "2027-01-05T09:15:00-05:00"}
    TradingSessionRunRepository(connection).save(run)
    import ict_cockpit.database.amdx_context_repository as module
    monkeypatch.setattr(module, "resolve_higher_cycles", lambda _: ())
    after = counts(connection)
    assert write(repo, inspected) == first
    assert counts(connection) == after
    with pytest.raises(ValueError, match="temporal identity"):
        write(repo, inspected, revision="2")
    assert counts(connection) == after


def test_changed_original_reference_rejects_new_observed_entry_atomically(store):
    connection, repo, run, _ = store
    inspected = target(repo, run, "Observed")
    run.market_context_snapshot = {"reference_market_time": "2027-01-05T09:15:00-05:00"}
    TradingSessionRunRepository(connection).save(run)
    before = counts(connection), run_bytes(connection, run.id)
    with pytest.raises(StaleAMDXUpdate, match="reference changed"):
        write(repo, inspected)
    assert (counts(connection), run_bytes(connection, run.id)) == before
    assert not connection.in_transaction
    fresh = target(repo, run, "Observed")
    assert fresh.cycle.id.endswith(":year:2027")
    assert write(repo, fresh).changed


def test_original_reference_is_checked_after_acquiring_write_transaction(store):
    connection, repo, run, path = store
    inspected = target(repo, run, "Observed")
    other = open_application_database(path)
    fired = False
    def change_at_lock(sql):
        nonlocal fired
        if not fired and sql.strip() == "BEGIN IMMEDIATE":
            fired = True
            run.market_context_snapshot = {"reference_market_time": "2027-01-05T09:15:00-05:00"}
            TradingSessionRunRepository(other).save(run)
    connection.set_trace_callback(change_at_lock)
    try:
        with pytest.raises(StaleAMDXUpdate, match="reference changed"):
            write(repo, inspected)
    finally:
        connection.set_trace_callback(None)
        other.close()
    assert fired and counts(connection) == (0,) * len(TABLES)


def test_equivalent_utc_z_original_reference_does_not_invalidate_inspected_meaning(store):
    connection, repo, run, _ = store
    inspected = target(repo, run, "Observed")
    run.market_context_snapshot = {"reference_market_time": "2026-10-08T13:15:00Z"}
    TradingSessionRunRepository(connection).save(run)
    assert write(repo, inspected).claim.market_reference == REFERENCE
    assert snapshot(repo, run, "Observed").projection.reference == REFERENCE


def test_repeated_dst_hour_change_rejects_original_observed_target(store):
    connection, repo, run, _ = store
    run.market_context_snapshot = {"reference_market_time": "2025-11-02T01:30:00-04:00"}
    TradingSessionRunRepository(connection).save(run)
    inspected = target(repo, run, "Observed")
    run.market_context_snapshot = {"reference_market_time": "2025-11-02T01:30:00-05:00"}
    TradingSessionRunRepository(connection).save(run)
    with pytest.raises(StaleAMDXUpdate, match="reference changed"):
        write(repo, inspected)
    assert counts(connection) == (0,) * len(TABLES)


def test_repeated_dst_hour_exact_retry_retains_original_instant(store):
    connection, repo, run, _ = store
    run.market_context_snapshot = {"reference_market_time": "2025-11-02T01:30:00-04:00"}
    TradingSessionRunRepository(connection).save(run)
    inspected = target(repo, run, "Observed")
    first = write(repo, inspected)
    run.market_context_snapshot = {"reference_market_time": "2025-11-02T01:30:00-05:00"}
    TradingSessionRunRepository(connection).save(run)
    before = counts(connection)
    retry = write(repo, inspected)
    assert payload(retry) == payload(first)
    assert retry.claim.market_reference.isoformat() == "2025-11-02T01:30:00-04:00"
    assert counts(connection) == before


@pytest.mark.parametrize("channel", ["Expected", "Observed"])
def test_stale_inspected_head_rejects_new_action_without_partial_records(store, channel):
    connection, repo, run, _ = store
    inspected = target(repo, run, channel)
    write(repo, inspected)
    before = counts(connection)
    with pytest.raises(StaleAMDXUpdate):
        write(repo, inspected, revision="2", role=Role.D)
    assert counts(connection) == before
    assert write(repo, target(repo, run, channel), revision="2", role=Role.D).changed


def test_saved_same_cycle_pair_basis_is_retained_and_changed_pair_head_is_rejected(store):
    connection, repo, run, _ = store
    expected = write(repo, target(repo, run), role=Role.D).claim
    observed = write(repo, target(repo, run, "Observed"), revision="2")
    stale = target(repo, run, "Observed")
    selected = repo.review.record_comparison(run_id=run.id, comparison_id="selected-basis",
        expected_claim_id=expected.id, observed_claim_id=observed.claim.id,
        expected_head_id=observed.comparison.id, recorded_at=REFERENCE + timedelta(minutes=1),
        market_reference=REFERENCE)
    before = counts(connection)
    with pytest.raises(StaleComparison):
        write(repo, stale, revision="3", role=Role.D)
    assert counts(connection) == before
    write(repo, target(repo, run), revision="new-expectation")
    fresh = target(repo, run, "Observed")
    assert fresh.expected_comparison_head_id == selected.id
    corrected = write(repo, fresh, revision="3", role=Role.D)
    assert corrected.comparison.expected_claim_id == expected.id


@pytest.mark.parametrize("channel", ["Expected", "Observed"])
def test_write_fault_rolls_back_cycle_claim_pair_and_receipt_then_allows_deliberate_retry(store, channel):
    connection, repo, run, _ = store
    inspected = target(repo, run, channel)
    table = "amdx_observed_command" if channel == "Observed" else "amdx_working_command"
    connection.execute(f"CREATE TRIGGER synthetic_failure BEFORE INSERT ON {table} "
                       "BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END")
    before = counts(connection)
    with pytest.raises(Exception, match="synthetic failure"):
        write(repo, inspected)
    assert counts(connection) == before
    assert not connection.in_transaction
    connection.execute("DROP TRIGGER synthetic_failure")
    assert write(repo, inspected).changed


@pytest.mark.parametrize("channel", ["Expected", "Observed"])
def test_competing_connections_commit_once_and_reject_the_other_inspected_target(store, channel):
    connection, repo, run, path = store
    inspected = target(repo, run, channel)
    barrier = Barrier(2)
    def contender(index):
        c = open_application_database(path)
        try:
            writer = TradingSessionRunRepository(c).amdx
            barrier.wait(timeout=10)
            try:
                return write(writer, inspected, revision=str(index), role=Role.M if index == 1 else Role.D)
            except StaleAMDXUpdate:
                return "stale"
        finally:
            c.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(contender, (1, 2)))
    assert sum(r == "stale" for r in results) == 1
    assert len(repo.get_history(run.id).claims) == 1
    assert connection.execute("SELECT COUNT(*) FROM amdx_cycle_identity").fetchone()[0] == 1


def test_consistent_read_keeps_original_run_reference_and_history_in_one_wal_snapshot(store):
    connection, repo, run, path = store
    other = open_application_database(path)
    writer = TradingSessionRunRepository(other).amdx
    fired = False
    def concurrent(sql):
        nonlocal fired
        if not fired and "SELECT id, branch_id, channel, cycle_id" in sql:
            fired = True
            run.market_context_snapshot = {"reference_market_time": "2027-01-05T09:15:00-05:00"}
            TradingSessionRunRepository(other).save(run)
            write(writer, target(writer, run, "Observed"))
    connection.set_trace_callback(concurrent)
    try:
        old = snapshot(repo, run, "Observed")
    finally:
        connection.set_trace_callback(None)
        other.close()
    assert fired and old.projection.cycles[2].claim is None
    assert old.projection.reference == REFERENCE
    fresh = snapshot(repo, run, "Observed")
    assert fresh.projection.cycles[2].claim is not None
    assert fresh.projection.cycles[2].context.cycle.id.endswith(":year:2027")


def test_snapshot_does_not_commit_or_rollback_callers_unrelated_transaction(store):
    connection, repo, run, _ = store
    inspected = target(repo, run)
    connection.execute("BEGIN")
    connection.execute("UPDATE trading_session_run SET session_name='Uncommitted caller note' WHERE id=?", (run.id,))
    snapshot(repo, run)
    assert connection.in_transaction
    with pytest.raises(RuntimeError, match="pending transaction"):
        write(repo, inspected)
    assert connection.in_transaction
    connection.rollback()
    assert run_bytes(connection, run.id)[0] == run.id
    assert not repo.get_history(run.id).claims


@pytest.mark.parametrize("position", [0, 5, True])
def test_invalid_positions_are_not_prepared(store, position):
    _, repo, run, _ = store
    with pytest.raises(ValueError, match="1 through 4"):
        repo.context.prepare_target(snapshot(repo, run), "year", position)


@pytest.mark.parametrize("reference,level", [
    (datetime(2026, 10, 1, 9, 15, tzinfo=MARKET_TIMEZONE), "month"),
    (datetime(2026, 6, 29, 9, 15, tzinfo=MARKET_TIMEZONE), "month"),
    (datetime(2026, 10, 9, 9, 15, tzinfo=MARKET_TIMEZONE), "week"),
])
def test_unassigned_or_distortion_requires_explicit_existing_quarter_selection(store, reference, level):
    _, repo, run, _ = store
    view = snapshot(repo, run, reference=reference)
    with pytest.raises(ValueError, match="No active"):
        repo.context.prepare_target(view, level)
    assert write(repo, repo.context.prepare_target(view, level, 3)).changed


@pytest.mark.parametrize("change", [
    {"channel": "Working"}, {"branch_id": "alternative"},
    {"quarter_id": "outside"}, {"reference_source": "Live Clock"},
    {"expected_comparison_head_id": "unrelated"},
])
def test_forged_scope_or_target_is_rejected_without_writes(store, change):
    connection, repo, run, _ = store
    inspected = replace(target(repo, run), **change)
    before = counts(connection)
    with pytest.raises(ValueError):
        write(repo, inspected)
    assert counts(connection) == before


def test_forged_temporal_identity_and_illegal_role_do_not_register_partial_cycles(store):
    connection, repo, run, _ = store
    inspected = target(repo, run)
    forged = replace(inspected, cycle=replace(inspected.cycle, parent_quarter_id="invented"))
    with pytest.raises(ValueError, match="temporal identity"):
        write(repo, forged)
    with pytest.raises(ValueError, match="structurally valid"):
        write(repo, inspected, role=Role.A)
    assert counts(connection) == (0,) * len(TABLES)


def test_original_anchor_uncertainty_subtype_clear_and_applicability_semantics_are_retained(store):
    _, repo, run, _ = store
    x = target(repo, run, position=4)
    write(repo, x, subtype=XSubtype.REVERSAL, role=Role.X)
    write(repo, target(repo, run, position=4), revision="2", subtype=XSubtype.CONTINUATION, role=Role.X)
    write(repo, target(repo, run), revision="3", role=Role.UNKNOWN)
    write(repo, target(repo, run), revision="4", role=Role.NOT_APPLICABLE)
    view = snapshot(repo, run)
    assert view.projection.cycles[2].inference.state == "Not Applicable"
    cleared = write(repo, target(repo, run), revision="5", role=None, clear_applicability=True)
    assert cleared.claim.anchors == () and cleared.claim.applicability == ()
    assert cleared.claim.inference.state == "Unresolved"


def test_new_python_process_restores_same_higher_profiles_and_original_reference(store):
    _, repo, run, path = store
    expected = write(repo, target(repo, run))
    observed = write(repo, target(repo, run, "Observed"), revision="2", role=Role.D)
    script = '''import json,sys
from datetime import datetime
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
c=open_application_database(__import__('pathlib').Path(sys.argv[1]))
r=TradingSessionRunRepository(c).amdx.context
e=r.load_stack(sys.argv[2],reference=datetime(2026,10,8,9,15,tzinfo=MARKET_TIMEZONE))
o=r.load_stack(sys.argv[2],channel='Observed')
print(json.dumps([e.projection.cycles[2].claim.id,o.projection.cycles[2].claim.id,o.projection.reference.isoformat()]))
c.close()
'''
    result = subprocess.run([sys.executable, "-c", script, str(path), run.id], cwd=ROOT,
        env={**__import__('os').environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True, text=True, timeout=30, check=True)
    assert json.loads(result.stdout) == [expected.claim.id, observed.claim.id, REFERENCE.isoformat()]


def test_read_keeps_exact_legacy_maps_and_never_infers_higher_anchors(store):
    _, repo, run, _ = store
    expected = snapshot(repo, run)
    observed = snapshot(repo, run, "Observed")
    assert {v.key: v.value for v in expected.projection.legacy_values} == {"quarter": "D", "month": "A"}
    assert {v.key: v.value for v in observed.projection.legacy_values} == {"quarter": "M"}
    assert all(r.claim is None for r in expected.projection.cycles + observed.projection.cycles)


def test_normal_mainwindow_reopen_retains_higher_history_and_existing_intraday_surface(cockpit, tmp_path):
    from ict_cockpit.database.study_find_repository import StudyFindRepository
    from ict_cockpit.database.tda_repository import TDARepository
    from ict_cockpit.gui.main_window import MainWindow
    window, shell, _ = cockpit
    run = shell.active_trading_run
    repo = window.trading_session_run_repository.amdx
    expected = write(repo, target(repo, run))
    observed = write(repo, target(repo, run, "Observed"), revision="2", role=Role.D)
    original = repo.get_history(run.id)
    connection = open_application_database(tmp_path / "ui.db")
    restored = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    try:
        other_shell = restored.trade_plan_widget.trading_day_shell_widget
        other_repo = restored.trading_session_run_repository.amdx
        assert other_shell.active_trading_run.id == run.id
        assert other_repo.get_history(run.id) == original
        assert snapshot(other_repo, run).projection.cycles[2].claim == expected.claim
        assert snapshot(other_repo, run, "Observed").projection.cycles[2].claim == observed.claim
        assert other_shell.runtime.amdx_context_widget.table.rowCount() == 2
    finally:
        close(restored, connection)


def test_owned_revision_helpers_refuse_to_run_outside_a_transaction(store):
    _, repo, run, _ = store
    with pytest.raises(RuntimeError, match="owned transaction"):
        repo._revise_working_locked(expected_head_id=None)
    with pytest.raises(RuntimeError, match="owned transaction"):
        repo.review._revise_observed_locked(claim_id="c", comparison_id="p", run_id=run.id,
            branch_id="working", cycle=target(repo, run).cycle, quarter_id="outside", anchor=None,
            recorded_at=REFERENCE, market_reference=REFERENCE,
            expected_observed_head_id=None, expected_comparison_head_id=None)
