"""Open the supported retained Study workspace without creation or migration."""
import json
import os
from pathlib import Path
import sqlite3

from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION
from ict_cockpit.media.workspace_paths import manifest_roots


def open_existing_workspace(directory):
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f'Workspace directory does not exist: {root}')
    for name in ('demo.db', 'demo.db.workspace.ini', 'study-criterion-v0.txt'):
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Workspace requires its own existing {name}')
    if (root / 'study-criterion-v0.txt').read_text() != 'Synthetic criterion Study v0':
        raise ValueError('Unrecognized retained Study workspace marker')
    if (root / 'xdg').is_symlink() or not (root / 'xdg').is_dir():
        raise ValueError('Workspace requires its existing xdg media directory')
    manifest = root / 'study-workspace-origin.json'
    if manifest.is_symlink():
        raise ValueError('Workspace origin manifest must belong to this directory')
    if manifest.exists():
        roots = list(dict.fromkeys(manifest_roots(json.loads(manifest.read_text())) + [root]))
        for index, origin in enumerate(roots):
            if any(origin in other.parents or other in origin.parents for other in roots[index + 1:]):
                raise ValueError('Ambiguous overlapping workspace origin roots')
    # mode=rw never creates a missing database. Validation makes no schema writes.
    connection = sqlite3.connect((root / 'demo.db').as_uri() + '?mode=rw', uri=True)
    try:
        version = connection.execute('PRAGMA user_version').fetchone()[0]
        if version != CURRENT_SCHEMA_VERSION:
            raise ValueError(f'Workspace schema {version}; this launcher requires {CURRENT_SCHEMA_VERSION}. '
                             'No migration was performed; keep your backup and use the reviewed upgrade procedure.')
        required = {'study_find', 'study_find_draft', 'study_task_registry', 'study_capture_context',
                    'study_investigation_capture', 'study_review', 'trading_session_run', 'amdx_master_binding'}
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not required.issubset(tables):
            raise ValueError('Workspace database is missing required cockpit tables')
        if connection.execute('PRAGMA quick_check').fetchall() != [('ok',)]:
            raise ValueError('Workspace database failed its integrity check')
        if connection.execute('PRAGMA foreign_key_check').fetchone():
            raise ValueError('Workspace database has foreign-key violations')
        connection.execute('PRAGMA foreign_keys=ON')
    except BaseException:
        connection.close()
        raise
    os.environ['XDG_DATA_HOME'] = str(root / 'xdg')
    return connection, root
