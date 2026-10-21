from pathlib import Path
import sqlite3
import subprocess

import pytest

from ict_cockpit.analysis.amdx import Anchor, Role, intraday_cycles
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from test_amdx_repository import saved_run
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]
PARENT = "e80a17be3d9ff28896aeb344e5f76a69722228cd"


def old_schema():
    namespace = {}
    code = subprocess.check_output(["git", "show", PARENT+":src/ict_cockpit/database/schema.py"], cwd=ROOT, text=True)
    exec(compile(code, "actual-v41-schema", "exec"), namespace)
    return namespace["initialize_schema"]


@pytest.mark.parametrize("inject_failure", [False, True])
def test_actual_v41_migration_preserves_every_original_table_without_guessing_assets(tmp_path, inject_failure):
    connection = create_connection(tmp_path / "old-v41.db")
    previous = old_schema()
    previous(connection)
    run = saved_run(connection)
    repo = AMDXRepository(connection)
    reference = datetime(2026, 10, 9, 9, 15, tzinfo=MARKET_TIMEZONE)
    cycle = intraday_cycles(reference)[0]
    first = repo.revise_working(claim_id="old-noop", run_id=run.id, branch_id="working", channel="Expected",
        cycle=cycle, quarter_id=cycle.quarters[2].id, anchor=None, recorded_at=reference,
        market_reference=reference, expected_head_id=None)
    observed = repo.review.revise_observed(claim_id="old-observed-noop", comparison_id="old-pair-noop",
        run_id=run.id, branch_id="working", cycle=cycle, quarter_id=cycle.quarters[2].id,
        anchor=None, recorded_at=reference, market_reference=reference,
        expected_observed_head_id=None, expected_comparison_head_id=None)
    repo.revise_working(claim_id="old-working", run_id=run.id, branch_id="working", channel="Expected",
        cycle=cycle, quarter_id=cycle.quarters[2].id,
        anchor=Anchor("old-working-anchor", cycle.quarters[2].id, Role.D, "old chart"),
        recorded_at=reference, market_reference=reference, expected_head_id=None)
    repo.review.revise_observed(claim_id="old-observed", comparison_id="old-pair",
        run_id=run.id, branch_id="working", cycle=cycle, quarter_id=cycle.quarters[2].id,
        anchor=Anchor("old-observed-anchor", cycle.quarters[2].id, Role.M, "old chart"),
        recorded_at=reference, market_reference=reference,
        expected_observed_head_id=None, expected_comparison_head_id=None)
    names = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    before = {name:connection.execute(f'SELECT * FROM "{name}"').fetchall() for name in names}
    if inject_failure:
        connection.set_authorizer(lambda action,*_: sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_CREATE_TRIGGER else sqlite3.SQLITE_OK)
        with pytest.raises(sqlite3.DatabaseError):initialize_schema(connection)
        connection.set_authorizer(None)
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 41
        assert not connection.execute("SELECT name FROM sqlite_master WHERE name LIKE '%amdx_catalog%'").fetchall()
        for name in names:assert connection.execute(f'SELECT * FROM "{name}"').fetchall() == before[name]
    initialize_schema(connection)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 47
    for name in names:assert connection.execute(f'SELECT * FROM "{name}"').fetchall() == before[name]
    assert not repo.catalog.list_catalogs()
    assert not connection.execute("SELECT * FROM amdx_catalog_command").fetchall()
    assert repo.revise_working(claim_id="old-noop", run_id=run.id, branch_id="working", channel="Expected",
        cycle=cycle, quarter_id=cycle.quarters[2].id, anchor=None, recorded_at=reference,
        market_reference=reference, expected_head_id=None) == first
    assert repo.review.revise_observed(claim_id="old-observed-noop", comparison_id="old-pair-noop",
        run_id=run.id, branch_id="working", cycle=cycle, quarter_id=cycle.quarters[2].id,
        anchor=None, recorded_at=reference, market_reference=reference,
        expected_observed_head_id=None, expected_comparison_head_id=None) == observed
    with pytest.raises(RuntimeError, match="Unsupported database schema version: 47"):
        previous(connection)
    assert not connection.execute("PRAGMA foreign_key_check").fetchall()
    connection.close()
