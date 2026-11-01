from io import BytesIO
from pathlib import Path
import sqlite3
import subprocess
import sys
import tarfile

import pytest
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema

PARENT='9d6ab3e5b6011529ccd9c01210318bcc1d3f536d'
ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('injected',[False,True])
def test_actual_v45_receipts_remain_byte_identical_with_no_retroactive_proof(tmp_path,injected):
    archived=tmp_path/'v45';archived.mkdir()
    with tarfile.open(fileobj=BytesIO(subprocess.check_output(['git','archive',PARENT],cwd=ROOT))) as tar:
        tar.extractall(archived,filter='data')
    database=tmp_path/'old.db'
    script='''
import sys
sys.path[:0]=[sys.argv[1]+'/src',sys.argv[1]+'/tests']
from pathlib import Path
from test_amdx_repository import saved_run
from test_amdx_run_calendar_repository import REFERENCE,RECORDED,launch
from test_amdx_run_observed_repository import prepare,revise
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.analysis.trading_session_run import TradingRun
c=open_application_database(Path(sys.argv[2]))
legacy=saved_run(c)
r=AMDXRepository(c)
r.master.ensure('MNQ',recorded_at=RECORDED)
run=TradingRun(legacy.trading_day_id,'v45 synthetic run',legacy.process_session_id)
run.market_context_snapshot={'reference_market_time':REFERENCE.isoformat()}
launch(r,run)
revise(r,prepare(r,run))
assert c.execute('PRAGMA user_version').fetchone()[0]==45
c.close()
'''
    subprocess.run([sys.executable,'-c',script,str(archived),str(database)],cwd=archived,check=True)
    c=create_connection(database)
    names=[row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    before={name:c.execute('SELECT * FROM '+name).fetchall() for name in names}
    if injected:
        c.set_authorizer(lambda action,a,b,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_PRAGMA and a=='user_version' and b=='52' else sqlite3.SQLITE_OK)
        with pytest.raises(sqlite3.DatabaseError):initialize_schema(c)
        c.set_authorizer(None)
        assert c.execute('PRAGMA user_version').fetchone()[0]==45
        assert {name:c.execute('SELECT * FROM '+name).fetchall() for name in names}==before
    initialize_schema(c)
    assert c.execute('PRAGMA user_version').fetchone()[0]==52
    assert {name:c.execute('SELECT * FROM '+name).fetchall() for name in names}==before
    from ict_cockpit.database.amdx_repository import AMDXRepository
    receipt=AMDXRepository(c).run_observed.get_result('review')
    assert receipt.packet['version']==1 and 'scope_proof' not in receipt.packet['request']
    namespace={}
    exec(compile((archived/'src/ict_cockpit/database/schema.py').read_text(),'actual-v45-schema','exec'),namespace)
    with pytest.raises(RuntimeError,match='Unsupported database schema version: 52'):namespace['initialize_schema'](c)
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    c.close()
