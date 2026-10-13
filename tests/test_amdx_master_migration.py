from datetime import datetime
from pathlib import Path
import sqlite3
import subprocess

import pytest

from ict_cockpit.analysis.amdx import Role
from ict_cockpit.analysis.amdx_catalog import Catalog
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from test_amdx_repository import saved_run


PARENT='f4f2363a55183f95dede642e439069e332b7612b'


@pytest.mark.parametrize('inject_failure',[False,True])
def test_actual_v42_migration_preserves_every_source_row_and_assigns_nothing(tmp_path,inject_failure):
    namespace={}
    code=subprocess.check_output(['git','show',PARENT+':src/ict_cockpit/database/schema.py'],
                                 cwd=Path(__file__).resolve().parents[1],text=True)
    exec(compile(code,'actual-v42-schema','exec'),namespace)
    previous=namespace['initialize_schema']
    connection=create_connection(tmp_path/'actual-v42.db')
    previous(connection)
    saved_run(connection)
    repo=AMDXRepository(connection)
    cat=repo.catalog.create(Catalog('existing','Historical study'))
    reference=datetime(1985,8,12,9,15,tzinfo=MARKET_TIMEZONE)
    target=repo.catalog.prepare_target(cat.id,reference=reference,level='year',position=3)
    repo.catalog.revise(target,command_id='original',recorded_at=reference,role=Role.D,
                        anchor_id='anchor',source_ref='original chart')
    names=[r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    before={n:connection.execute(f'SELECT * FROM "{n}"').fetchall() for n in names}
    archive=repo.catalog.export_archive(cat.id)
    if inject_failure:
        connection.set_authorizer(lambda action,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_CREATE_TRIGGER else sqlite3.SQLITE_OK)
        with pytest.raises(sqlite3.DatabaseError):
            initialize_schema(connection)
        connection.set_authorizer(None)
        assert connection.execute('PRAGMA user_version').fetchone()[0]==42
        assert not connection.execute("SELECT name FROM sqlite_master WHERE name LIKE '%master_binding%' OR name='idx_amdx_catalog_owner_instrument'").fetchall()
        assert {n:connection.execute(f'SELECT * FROM "{n}"').fetchall() for n in names}==before
    initialize_schema(connection)
    assert connection.execute('PRAGMA user_version').fetchone()[0]==45
    assert {n:connection.execute(f'SELECT * FROM "{n}"').fetchall() for n in names}==before
    assert not connection.execute('SELECT * FROM amdx_master_binding').fetchall()
    assert repo.catalog.export_archive(cat.id)==archive
    with pytest.raises(ValueError,match='no canonical'):
        repo.master.resolve('MNQ')
    with pytest.raises(RuntimeError,match='Unsupported database schema version: 45'):
        previous(connection)
    assert not connection.execute('PRAGMA foreign_key_check').fetchall()
    connection.close()
