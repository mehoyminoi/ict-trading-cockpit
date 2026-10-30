"""Restore a verified closed-workspace archive into a new durable directory."""
import argparse
import json
from pathlib import Path
import shutil
import sqlite3
import tarfile
import tempfile
from verify_study_backup import verify


def restore(archive, destination, original_root='/tmp/ict-study-review-v0'):
    destination = Path(destination).absolute()
    if destination.exists():
        raise ValueError('Destination already exists; choose a new directory')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.study-restore-', dir=destination.parent) as temporary:
        staging = Path(temporary)
        snapshot = staging / 'source.tar.gz'
        shutil.copyfile(archive, snapshot)
        report = verify(snapshot, original_root)
        report['archive'] = str(Path(archive).resolve())
        with tarfile.open(snapshot) as bundle:
            # verify() has validated this private snapshot: no links or traversal.
            for member in bundle.getmembers():
                target = staging / member.name
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with bundle.extractfile(member) as source, target.open('xb') as output:
                        shutil.copyfileobj(source, output)
        restored = staging / Path(original_root).name
        if (restored / 'study-workspace-origin.json').exists():
            raise ValueError('Already relocated workspace: chained relocation is not supported yet')
        (restored / 'study-workspace-origin.json').write_text(json.dumps({
            'version': 1, 'original_root': str(original_root),
            'archive_sha256': report['sha256'], 'verification': report,
        }, indent=2))
        # Reserve the name exclusively; never overwrite an existing workspace.
        destination.mkdir()
        try:
            for child in restored.iterdir():
                shutil.move(str(child), destination / child.name)
        except BaseException:
            shutil.rmtree(destination)
            raise
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--original-root', default='/tmp/ict-study-review-v0')
    args = parser.parse_args()
    try:
        result = restore(args.archive, args.destination, args.original_root)
    except (ValueError, OSError, sqlite3.Error, tarfile.TarError) as error:
        parser.exit(1, f'Restore failed: {error}\n')
    print(f'Restored workspace: {result}\nOriginals unchanged. Open with study_criterion_demo.py --data-dir at this path.')


if __name__ == '__main__':
    main()
