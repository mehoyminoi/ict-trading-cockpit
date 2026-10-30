import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import tarfile
import pytest

spec = importlib.util.spec_from_file_location('backup', Path(__file__).parents[1] / 'tools/verify_study_backup.py')
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


def fixture_archive(tmp_path, *, missing=False, external=False):
    root = tmp_path / 'workspace'
    root.mkdir()
    image = root / 'xdg/chart.png'
    image.parent.mkdir()
    image.write_bytes(b'fixture image bytes')
    (root / 'study-criterion-v0.txt').write_text('Synthetic criterion Study v0')
    (root / 'demo.db.workspace.ini').write_text('[General]\n')
    c = sqlite3.connect(root / 'demo.db')
    from ict_cockpit.database.schema import initialize_schema
    initialize_schema(c)
    c.execute('CREATE TABLE records(image_path TEXT, image_paths TEXT, payload_json TEXT)')
    path = '/outside/chart.png' if external else str(image)
    c.execute('INSERT INTO records VALUES (?,?,?)', ('', '[]', json.dumps({'source': {'images': [path]}})))
    c.commit();c.close()
    archive = tmp_path / 'backup.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        tar.add(root, arcname=root.name, filter=lambda m: None if missing and m.name.endswith('chart.png') else m)
    return archive, root


def test_restores_without_original_and_preserves_archive(tmp_path):
    archive, root = fixture_archive(tmp_path)
    before = archive.read_bytes()
    import shutil
    shutil.rmtree(root)
    report = backup.verify(archive, root)
    assert report['status'] == 'PASS'
    assert report['unique_image_references'] == 1
    assert report['rows']['records'] == 1
    assert archive.read_bytes() == before
    assert not root.exists()


@pytest.mark.parametrize('options', [{'missing': True}, {'external': True}])
def test_missing_or_external_fails_even_with_original_available(tmp_path, options):
    archive, root = fixture_archive(tmp_path, **options)
    assert (root / 'xdg/chart.png').exists()
    with pytest.raises(ValueError, match='Incomplete backup'):
        backup.verify(archive, root)


@pytest.mark.parametrize('name,link', [('../escape', False), ('workspace/link', True)])
def test_rejects_unsafe_archive_members(tmp_path, name, link):
    archive = tmp_path / 'unsafe.tar'
    with tarfile.open(archive, 'w') as tar:
        member = tarfile.TarInfo(name)
        if link:
            member.type = tarfile.SYMTYPE
            member.linkname = '/tmp'
            tar.addfile(member)
        else:
            member.size = 1
            tar.addfile(member, io.BytesIO(b'x'))
    with pytest.raises(ValueError, match='Unsafe'):
        backup.verify(archive, tmp_path / 'workspace')
