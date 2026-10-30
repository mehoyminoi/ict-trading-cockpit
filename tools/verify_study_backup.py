"""Verify a closed Study demo workspace archive without using original files."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sqlite3
import tarfile
import tempfile


def image_references(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == 'image_path' and isinstance(item, str) and item:
                yield item
            elif key in ('image_paths', 'images') and isinstance(item, list):
                for path in item:
                    if not isinstance(path, str):
                        raise ValueError('Invalid image reference')
                    if path:
                        yield path
            else:
                yield from image_references(item)
    elif isinstance(value, list):
        for item in value:
            yield from image_references(item)


def verify(archive, original_root):
    archive = Path(archive).resolve()
    original_root = Path(original_root)
    if not original_root.is_absolute() or '..' in original_root.parts:
        raise ValueError('Original workspace path must be absolute without ..')
    with tempfile.TemporaryDirectory(prefix='ict-backup-check-') as temporary:
        root = Path(temporary)
        with tarfile.open(archive, 'r:*') as bundle:
            members = bundle.getmembers()
            seen = set()
            for member in members:
                path = PurePosixPath(member.name)
                if (path.is_absolute() or '..' in path.parts or not path.parts
                        or path.parts[0] != original_root.name
                        or not (member.isfile() or member.isdir())
                        or str(path) in seen):
                    raise ValueError('Unsafe, duplicate or unexpected archive member: ' + member.name)
                seen.add(str(path))
            # Only regular files/directories beneath one verified root; never links.
            for member in members:
                target = root / member.name
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with bundle.extractfile(member) as source, target.open('xb') as destination:
                        import shutil
                        shutil.copyfileobj(source, destination)
        workspace = root / original_root.name
        database = workspace / 'demo.db'
        if not database.is_file():
            raise ValueError('Archive is missing demo.db')
        if (workspace / 'study-criterion-v0.txt').read_text() != 'Synthetic criterion Study v0':
            raise ValueError('Unexpected fixture marker')
        if not (workspace / 'demo.db.workspace.ini').is_file():
            raise ValueError('Archive is missing workspace settings')
        connection = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
        try:
            if connection.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                raise ValueError('Restored database integrity check failed')
            if connection.execute('PRAGMA foreign_key_check').fetchone():
                raise ValueError('Restored database has foreign-key violations')
            version = connection.execute('PRAGMA user_version').fetchone()[0]
            if version != 51:
                raise ValueError(f'This verifier supports schema 51, found {version}')
            counts, references = {}, set()
            tables = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
            for (table,) in tables:
                quoted = '"' + table.replace('"', '""') + '"'
                cursor = connection.execute('SELECT * FROM ' + quoted)
                columns = [item[0] for item in cursor.description]
                count = 0
                for row in cursor:
                    count += 1
                    for key, value in zip(columns, row):
                        if key == 'image_path' and value:
                            references.add(value)
                        elif key == 'image_paths' and value:
                            references.update(image_references({'image_paths': json.loads(value)}))
                        elif key == 'payload_json' and value:
                            references.update(image_references(json.loads(value)))
                counts[table] = count
            missing, external = [], []
            for reference in sorted(references):
                path = Path(reference)
                if '..' in path.parts:
                    external.append(reference)
                    continue
                try:
                    relative = path.relative_to(original_root)
                except ValueError:
                    external.append(reference)
                    continue
                restored = workspace / relative
                if not restored.is_file() or restored.stat().st_size == 0:
                    missing.append(reference)
                else:
                    # Read the entire restored file; never fall back to the original.
                    with restored.open('rb') as image:
                        while image.read(1024 * 1024):
                            pass
            if missing or external:
                raise ValueError(f'Incomplete backup: {len(missing)} missing/empty images, '
                                 f'{len(external)} references outside workspace.\n' + '\n'.join(missing + external))
        finally:
            connection.close()
    digest = hashlib.sha256()
    with archive.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return dict(status='PASS', archive=str(archive), sha256=digest.hexdigest(), schema=version,
                unique_image_references=len(references), rows=counts,
                scope='Isolated archive restore, database integrity, settings presence and referenced-file availability. '
                      'Not image decoding, GUI restoration, migration or portable relocation validation.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--original-root', default='/tmp/ict-study-review-v0')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.archive, args.original_root), indent=2))
    except (ValueError, OSError, sqlite3.Error, tarfile.TarError) as error:
        parser.exit(1, f'Backup verification FAILED: {error}\n')


if __name__ == '__main__':
    main()
