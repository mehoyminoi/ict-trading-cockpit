from io import BytesIO
from pathlib import Path
import sqlite3
import subprocess
import tarfile

import pytest

from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema


PARENT='fcc613833a1b068cd0be8e143c676fbbf257fedf'
ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('injected',[False,True])
def test_actual_v44_bound_run_migration_preserves_every_source_without_assessment_import(tmp_path,injected):
    archived=tmp_path/'old'
    archived.mkdir()
    archive=subprocess.check_output(['git','archive',PARENT],cwd=ROOT)
    with tarfile.open(fileobj=BytesIO(archive)) as tar:
        tar.extractall(archived,filter='data')
    database=tmp_path/'old.db'
    script="""
from pathlib import Path
import sys
sys.path[:0]=[sys.argv[1]+'/src',sys.argv[1]+'/tests']
from datetime import datetime
from test_amdx_repository import saved_run
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.amdx import Anchor,Role,intraday_cycles
from ict_cockpit.analysis.trading_session_run import TradingRun
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.amdx_repository import AMDXRepository
c=open_application_database(Path(sys.argv[2]))
legacy=saved_run(c)
r=AMDXRepository(c)
ref=datetime(2026,10,9,9,15,tzinfo=MARKET_TIMEZONE)
now=datetime(2026,10,13,12,tzinfo=MARKET_TIMEZONE)
r.master.ensure('MNQ',recorded_at=now)
run=TradingRun(legacy.trading_day_id,'actual v44 run',legacy.process_session_id)
run.market_context_snapshot={'reference_market_time':ref.isoformat()}
r.run_calendar.launch(r.run_calendar.prepare_launch(run,instrument='MNQ',reference=ref),
    operation_id='old-launch',capture_id='old-capture',recorded_at=now)
cycle=intraday_cycles(ref)[1]
q=cycle.quarters[2]
r.review.revise_observed(claim_id='old-observed',comparison_id='old-pair',run_id=run.id,
    branch_id='working',cycle=cycle,quarter_id=q.id,anchor=Anchor('old-anchor',q.id,Role.M,'old assessment'),
    recorded_at=now,market_reference=ref,expected_observed_head_id=None,expected_comparison_head_id=None)
assert c.execute('PRAGMA user_version').fetchone()[0]==44
c.close()
"""
    subprocess.run([__import__('sys').executable,'-c',script,str(archived),str(database)],cwd=archived,check=True)
    c=create_connection(database)
    names=[row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    before={name:c.execute('SELECT * FROM '+name).fetchall() for name in names}
    if injected:
        c.set_authorizer(lambda action,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_CREATE_TRIGGER else sqlite3.SQLITE_OK)
        with pytest.raises(sqlite3.DatabaseError): initialize_schema(c)
        c.set_authorizer(None)
        assert c.execute('PRAGMA user_version').fetchone()[0]==44
        assert not c.execute("SELECT name FROM sqlite_master WHERE name LIKE '%run_observed%'").fetchall()
        assert {name:c.execute('SELECT * FROM '+name).fetchall() for name in names}==before
    initialize_schema(c)
    assert c.execute('PRAGMA user_version').fetchone()[0]==52
    assert {name:c.execute('SELECT * FROM '+name).fetchall() for name in names}==before
    assert not c.execute('SELECT * FROM amdx_run_observed_command').fetchall()
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    namespace={}
    exec(compile((archived/'src/ict_cockpit/database/schema.py').read_text(),'actual-v44-schema','exec'),namespace)
    with pytest.raises(RuntimeError,match='Unsupported database schema version: 52'):
        namespace['initialize_schema'](c)
    c.close()
