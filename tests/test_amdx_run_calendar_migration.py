from datetime import datetime
from pathlib import Path
import sqlite3
import subprocess

import pytest

from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from test_amdx_repository import saved_run


PARENT='6c7362b9d267f920164cbf13dff0415bfc27d3c2'


@pytest.mark.parametrize('inject_failure',[False,True])
def test_actual_v43_migration_preserves_every_old_table_and_does_not_bind_legacy_runs(tmp_path,inject_failure):
    namespace={}
    code=subprocess.check_output(['git','show',PARENT+':src/ict_cockpit/database/schema.py'],
        cwd=Path(__file__).resolve().parents[1],text=True)
    exec(compile(code,'actual-v43-schema','exec'),namespace)
    previous=namespace['initialize_schema']
    connection=create_connection(tmp_path/'actual-v43.db')
    previous(connection)
    run=saved_run(connection)
    repo=AMDXRepository(connection)
    repo.master.ensure('MNQ',recorded_at=datetime(2026,10,13,12,tzinfo=MARKET_TIMEZONE))
    names=[r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    before={name:connection.execute(f'SELECT * FROM "{name}"').fetchall() for name in names}
    if inject_failure:
        connection.set_authorizer(lambda action,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_CREATE_TRIGGER else sqlite3.SQLITE_OK)
        with pytest.raises(sqlite3.DatabaseError):
            initialize_schema(connection)
        connection.set_authorizer(None)
        assert connection.execute('PRAGMA user_version').fetchone()[0]==43
        assert not connection.execute("SELECT name FROM sqlite_master WHERE name LIKE 'amdx_run_%' OR name='idx_amdx_master_bound_scope'").fetchall()
        assert {name:connection.execute(f'SELECT * FROM "{name}"').fetchall() for name in names}==before
    initialize_schema(connection)
    assert connection.execute('PRAGMA user_version').fetchone()[0]==45
    assert {name:connection.execute(f'SELECT * FROM "{name}"').fetchall() for name in names}==before
    for table in ('amdx_run_binding','amdx_run_capture','amdx_run_calendar_command'):
        assert not connection.execute(f'SELECT * FROM {table}').fetchall()
    with pytest.raises(ValueError,match='legacy ownership is unknown'):
        repo.run_calendar.get_binding(run.id)
    with pytest.raises(RuntimeError,match='Unsupported database schema version: 45'):
        previous(connection)
    assert not connection.execute('PRAGMA foreign_key_check').fetchall()
    connection.close()
