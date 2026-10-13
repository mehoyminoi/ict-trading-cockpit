# Sync the merged AMDX main checkpoint

PRs **#67–75 are merged into main**, in the reviewed order with merge commits. Main now contains the shared maintained AMDX calendar and bounded higher Review, schema **v46**, Trade Plan **Alpha 0.7**. All 20 operator checks 261–280 are PASS. The merged implementation tree exactly matches reviewed checkpoint `15e64af8d51f946696e9927b5ce731857bdc8602`; the final code merge is `8b7f8ae0e8e6da76bed266f771fce75d4bfaaefb`. A subsequent main checkpoint adds only these sync/handoff notes.

## 1 — Close the application and sync main

Close the regular cockpit and any demo windows. From your terminal:

```bash
cd /home/jesse/projects/ict-trading-cockpit
git status --short
git stash push -m 'local smoke notes before AMDX main sync' -- docs/SMOKE_TEST.md

git fetch origin
git switch main
git pull --ff-only origin main
git log -1 --oneline
source .venv/bin/activate
```

The stash command preserves uncommitted smoke notes; “No local changes to save” is fine. Leave earlier saved stashes intact. If any command fails, stop there and retain the exact message; do not discard changes or force the pull. The final expected main ID is provided with the published checkpoint.

## 2 — Back up the regular database before opening the application

The normal application upgrades its database when it opens. The following standard-library script only reads your existing regular database and writes a separate, uniquely named backup. It uses the application's actual configured path, honors `XDG_DATA_HOME`, and includes committed WAL data via SQLite's backup API. It does not initialize or migrate the source database.

Run this complete terminal command after activating the same environment you use for the regular application, including the first and last lines:

```bash
PYTHONPATH=src python - <<'PY'
import os
from pathlib import Path
import sqlite3
import tempfile
from ict_cockpit.app_paths import get_database_path

database = get_database_path().resolve()
print(f"Regular database: {database}")
if not database.exists():
    print("No existing regular database; no backup is needed before first launch.")
else:
    source = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
    try:
        version = source.execute("PRAGMA user_version").fetchone()[0]
        backup_dir = database.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=f"ict_cockpit-v{version}-", suffix=".db", dir=backup_dir)
        os.close(descriptor)
        backup = Path(name)
        target = sqlite3.connect(backup)
        try:
            source.backup(target)
            assert target.execute("PRAGMA integrity_check").fetchone() == ("ok",)
            assert target.execute("PRAGMA user_version").fetchone()[0] == version
        finally:
            target.close()
        print(f"Saved database backup (schema v{version}): {backup}")
    finally:
        source.close()
PY
```

Expected: **Saved database backup (schema v…): …** with a new backup path, or **No existing regular database**. Keep that path. If the command reports an error, resolve it before opening the regular application. If your regular database is already v46, it is still backed up with its actual version labeled.

An older v41 application cannot read the upgraded v46 database. An unmigrated database copy is required to return to that older application; switching Git branches alone does not downgrade SQLite. The database backup covers the database; existing media and navigation files remain in their current locations.

## 3 — Open the regular cockpit when you want to use main

```bash
PYTHONPATH=src python -m ict_cockpit.main
```

No repeat of checks 275–280 is required for this merge. The merged code tree is the exact reviewed/tested tree: **1,136 tests PASS across 89 isolated modules**. Existing unbound runs retain their old data and legacy path; migration does not guess instruments or copy them into the maintained MNQ calendar. The next product milestone is the comprehensive whole-cockpit UX/Study plan, not another smoke trial or speculative storage layer.
