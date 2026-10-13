from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from threading import Barrier

import pytest

from ict_cockpit.analysis.amdx import Profile, Role, XSubtype, payload
from ict_cockpit.analysis.amdx_catalog import CaptureBasis, Catalog
from ict_cockpit.analysis.amdx_context import HIGHER_LEVELS
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.database.amdx_catalog_repository import read_catalog_archive
from ict_cockpit.database.amdx_repository import AMDXRepository, StaleAMDXUpdate
from ict_cockpit.database.bootstrap import open_application_database


REFERENCE = datetime(1998, 5, 12, 9, 15, tzinfo=MARKET_TIMEZONE)
RECORDED = datetime(2026, 10, 13, 10, tzinfo=MARKET_TIMEZONE)
LEVELS = HIGHER_LEVELS + ("day", "session")


@pytest.fixture
def store(tmp_path):
    path = tmp_path / "catalog.db"
    connection = open_application_database(path)
    repo = AMDXRepository(connection).catalog
    catalog = repo.create(Catalog("historical", "Synthetic old data", definition_ref="candidate:rules-1"))
    yield connection, repo, catalog, path
    connection.close()


def target(repo, catalog, channel="Observed", level="year", reference=REFERENCE, position=3):
    return repo.prepare_target(catalog.id, reference=reference, channel=channel, level=level, position=position)


def write(repo, pinned, id="command-1", role=Role.M, **extra):
    args = dict(command_id=id, recorded_at=RECORDED, role=role)
    if role is not None:
        args.update(anchor_id="anchor-"+id, source_ref="synthetic chart")
    args.update(extra)
    return repo.revise(pinned, **args)


def rows(connection):
    return tuple(tuple(connection.execute(f"SELECT * FROM {t}").fetchall()) for t in
                 ("amdx_cycle_identity", "amdx_catalog", "amdx_catalog_command", "trading_session_run"))


@pytest.mark.parametrize("channel", ["Expected", "Observed"])
@pytest.mark.parametrize("level", LEVELS)
def test_all_identified_layers_backfill_before_2011_and_restore_without_run(store, channel, level):
    connection, repo, catalog, path = store
    pinned = target(repo, catalog, channel, level)
    result = write(repo, pinned)
    assert result.changed and result.claim.inference.candidates == (Profile.XAMD,)
    assert result.claim.run_id == catalog.owner_id
    assert not connection.execute("SELECT id FROM trading_session_run").fetchall()
    assert not connection.execute("SELECT id FROM amdx_claim").fetchall()
    assert not connection.execute("SELECT id FROM amdx_comparison").fetchall()
    before = rows(connection)
    other = open_application_database(path)
    try:
        restored = AMDXRepository(other).catalog
        view = restored.load_stack(catalog.id, reference=REFERENCE, channel=channel)
        assert next(r.claim for r in view.cycles if r.context.cycle.layer == level) == result.claim
        archived, history = read_catalog_archive(json.loads(json.dumps(restored.export_archive(catalog.id))))
        assert archived == catalog and history.claims == (result.claim,)
        assert rows(other) == before
    finally:
        other.close()


@pytest.mark.parametrize("year", [1900, 1950, 1985, 2005, 2026])
def test_no_rolling_retention_or_recent_date_gate(store, year):
    _, repo, catalog, _ = store
    reference = REFERENCE.replace(year=year)
    result = write(repo, target(repo, catalog, reference=reference))
    assert result.claim.cycle.id.endswith(str(year))
    assert result.claim.market_reference == reference
    assert result.claim.recorded_at == RECORDED


def test_instruments_collections_and_channels_do_not_borrow_heads(store):
    _, repo, catalog, _ = store
    other = repo.create(Catalog("other", "Another instrument", instrument="NNQ"))
    another = repo.create(Catalog("method-2", "Competing approach"))
    first = write(repo, target(repo, catalog))
    second = write(repo, target(repo, other), "command-2", role=Role.D)
    third = write(repo, target(repo, catalog, "Expected"), "command-3", role=Role.D)
    assert first.claim.inference.candidates != second.claim.inference.candidates
    assert target(repo, catalog).expected_head_id == first.claim.id
    assert target(repo, other).expected_head_id == second.claim.id
    assert target(repo, catalog, "Expected").expected_head_id == third.claim.id
    assert target(repo, another).expected_head_id is None
    assert repo.list_catalogs(instrument="MNQ") == (catalog, another)
    assert repo.list_catalogs(instrument="NNQ") == (other,)
    with pytest.raises(ValueError, match="ownership"):
        write(repo, replace(target(repo, catalog), instrument="NNQ"), "bad")


def test_same_asset_separate_definition_collections_and_identity_reuse(store):
    connection, repo, catalog, _ = store
    before = rows(connection)
    assert repo.create(catalog) == catalog
    assert rows(connection) == before
    for changed in (replace(catalog, instrument="NNQ"), replace(catalog, definition_ref="candidate:rules-2")):
        with pytest.raises(ValueError, match="identity"):
            repo.create(changed)
    assert rows(connection) == before


@pytest.mark.parametrize("channel", ["Expected", "Observed"])
def test_one_entry_corrections_direct_subtype_uncertainty_applicability_and_clear(store, channel):
    _, repo, catalog, _ = store
    write(repo, target(repo, catalog, channel, position=3), role=Role.D)
    revised = write(repo, target(repo, catalog, channel), "command-2")
    assert revised.claim.inference.candidates == (Profile.XAMD,)
    assert revised.claim.retired_anchor_ids == ("anchor-command-1",)
    x = write(repo, target(repo, catalog, channel, position=1), "command-3", role=Role.X, subtype=XSubtype.REVERSAL)
    assert x.claim.inference.roles[0].subtype is XSubtype.REVERSAL
    unknown = write(repo, target(repo, catalog, channel, position=1), "command-4", role=Role.UNKNOWN)
    assert unknown.claim.inference.roles[0].subtype is None
    na = write(repo, target(repo, catalog, channel), "command-5", role=Role.NOT_APPLICABLE)
    assert na.claim.applicability
    clear = write(repo, target(repo, catalog, channel), "command-6", role=None, clear_applicability=True)
    assert not clear.claim.applicability
    assert len(repo.history(catalog.id).claims) == 6


@pytest.mark.parametrize("channel", ["Expected", "Observed"])
def test_no_op_metadata_and_original_nullable_retry_survive_later_entry(store, channel, monkeypatch):
    connection, repo, catalog, _ = store
    pinned = target(repo, catalog, channel)
    basis = CaptureBasis("HistoricalEntry", evidence_ref="chart:old", definition_ref="rules-1")
    first = write(repo, pinned, role=None, capture=basis)
    assert not first.changed and first.claim is None
    later = write(repo, pinned, "command-2")
    before = rows(connection)
    import ict_cockpit.database.amdx_catalog_repository as module
    monkeypatch.setattr(module, "resolve_stack_cycles", lambda _: ())
    assert write(repo, pinned, role=None, capture=basis) == first
    assert rows(connection) == before
    with pytest.raises(ValueError, match="cannot be overwritten"):
        write(repo, pinned, role=None, capture=replace(basis, evidence_ref="other"))
    with pytest.raises(ValueError, match="canonical"):
        write(repo, pinned, "new", role=None)
    archive = repo.export_archive(catalog.id)
    assert archive["commands"][0]["request"]["capture"] == payload(basis)
    assert read_catalog_archive(archive)[1].claims == (later.claim,)


def test_unchanged_meaning_still_preserves_each_capture_basis(store):
    _, repo, catalog, _ = store
    first = write(repo, target(repo, catalog))
    metadata = CaptureBasis("ForwardEntry", RECORDED-timedelta(minutes=1), "event:1", "rules-2")
    same = write(repo, target(repo, catalog), "command-2", capture=metadata)
    assert not same.changed and same.claim == first.claim
    archive = repo.export_archive(catalog.id)
    assert len(archive["commands"]) == 2
    assert archive["commands"][1]["request"]["capture"] == payload(metadata)
    assert archive["commands"][0]["request"]["capture"]["kind"] == "HistoricalEntry"


def test_catalog_occurrences_are_enumerable_and_survive_a_separate_process(store):
    _, repo, catalog, path = store
    first = write(repo, target(repo, catalog))
    second = write(repo, target(repo, catalog, reference=REFERENCE.replace(year=1985)), "command-2")
    third = write(repo, target(repo, catalog, channel="Expected", level="day"), "command-3")
    assert repo.current_heads(catalog.id, channel="Observed", level="year") == (first.claim, second.claim)
    assert repo.current_heads(catalog.id, channel="Expected") == (third.claim,)
    root = Path(__file__).resolve().parents[1]
    script = '''
import json,sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.database.amdx_catalog_repository import read_catalog_archive
c=open_application_database(Path(sys.argv[1]))
r=AMDXRepository(c).catalog
a,h=read_catalog_archive(r.export_archive('historical'))
assert a.instrument=='MNQ' and len(h.claims)==3
assert len(r.current_heads(a.id))==3
assert c.execute('SELECT COUNT(*) FROM trading_session_run').fetchone()[0]==0
c.close()
print('catalog process restore passed')
'''
    result = subprocess.run([sys.executable, "-c", script, str(path)], cwd=root, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout+result.stderr
    assert result.stdout.strip() == "catalog process restore passed"


def test_stale_heads_and_sql_failure_roll_back_every_catalog_record(store):
    connection, repo, catalog, _ = store
    stale = target(repo, catalog)
    write(repo, stale)
    before = rows(connection)
    with pytest.raises(StaleAMDXUpdate):
        write(repo, stale, "stale", role=Role.D)
    assert rows(connection) == before
    connection.execute("CREATE TRIGGER injected_failure BEFORE INSERT ON amdx_catalog_command BEGIN SELECT RAISE(ABORT,'fault'); END")
    with pytest.raises(sqlite3.IntegrityError, match="fault"):
        write(repo, target(repo, catalog, level="day"), "fault")
    assert rows(connection) == before
    assert not connection.in_transaction


@pytest.mark.parametrize("change", [dict(channel="bad"), dict(quarter_id="outside"), dict(instrument="NNQ"),
    dict(market_reference=datetime(1998, 5, 12))])
def test_bad_target_has_no_partial_write(store, change):
    connection, repo, catalog, _ = store
    before = rows(connection)
    with pytest.raises(ValueError):
        write(repo, replace(target(repo, catalog), **change))
    assert rows(connection) == before


def test_friday_pre_monday_and_fifth_week_context_have_no_fabricated_active_input(store):
    _, repo, catalog, _ = store
    for reference, level in [(REFERENCE.replace(year=2026, month=10, day=9), "week"),
                             (REFERENCE.replace(year=2026, month=10, day=1), "month"),
                             (REFERENCE.replace(year=2026, month=8, day=31), "month")]:
        with pytest.raises(ValueError, match="No active quarter"):
            repo.prepare_target(catalog.id, reference=reference, level=level)
        assert target(repo, catalog, level=level, reference=reference).quarter_id.endswith(":Q3")


@pytest.mark.parametrize("tamper", ["result", "instrument", "head", "future_basis", "duplicate", "missing_capture", "missing_basis_field", "numeric_change"])
def test_archive_validates_original_requests_results_and_ownership(store, tamper):
    _, repo, catalog, _ = store
    write(repo, target(repo, catalog))
    value = deepcopy(repo.export_archive(catalog.id))
    request = value["commands"][0]["request"]
    if tamper == "result":value["commands"][0]["result"]["claim"]["inference"]["state"] = "invented"
    elif tamper == "instrument":value["catalog"]["instrument"] = "NNQ"
    elif tamper == "head":request["target"]["expected_head_id"] = "missing"
    elif tamper == "future_basis":request["capture"]["information_available_at"] = (RECORDED+timedelta(days=1)).isoformat()
    elif tamper == "duplicate":value["commands"].append(value["commands"][0])
    elif tamper == "missing_capture":del request["capture"]
    elif tamper == "missing_basis_field":del request["capture"]["evidence_ref"]
    else:value["commands"][0]["result"]["changed"] = 1
    with pytest.raises(ValueError):
        read_catalog_archive(value)


def test_reads_preserve_caller_transaction_and_writes_refuse_it(store):
    connection, repo, catalog, _ = store
    connection.execute("BEGIN")
    assert not repo.history(catalog.id).claims
    repo.export_archive(catalog.id)
    assert connection.in_transaction
    with pytest.raises(RuntimeError, match="pending"):
        write(repo, target(repo, catalog))
    connection.rollback()


def test_two_connections_compete_for_the_same_inspected_catalog_head(store):
    _, repo, catalog, path = store
    pinned = target(repo, catalog)
    barrier = Barrier(2)
    def attempt(id):
        connection = open_application_database(path)
        try:
            other = AMDXRepository(connection).catalog
            barrier.wait()
            try:return write(other, pinned, id).changed
            except StaleAMDXUpdate:return "stale"
        finally:connection.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(attempt, ("one", "two")))
    assert result.count(True) == 1 and result.count("stale") == 1
    assert len(repo.history(catalog.id).claims) == 1


@pytest.mark.parametrize("table", ["amdx_catalog", "amdx_catalog_command"])
def test_catalog_history_rejects_update_delete_and_replace(store, table):
    connection, repo, catalog, _ = store
    write(repo, target(repo, catalog))
    for sql in (f"UPDATE {table} SET payload_json='{{}}'", f"DELETE FROM {table}",
                f"INSERT OR REPLACE INTO {table} SELECT * FROM {table}"):
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            with connection:connection.execute(sql)
    assert len(repo.history(catalog.id).claims) == 1
