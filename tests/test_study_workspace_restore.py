import importlib.util
from pathlib import Path
import sys
import tarfile
import pytest
from test_study_backup_verification import fixture_archive, backup
from ict_cockpit.media.workspace_paths import resolve_study_image

sys.modules['verify_study_backup'] = backup
spec = importlib.util.spec_from_file_location('restore', Path(__file__).parents[1] / 'tools/restore_study_workspace.py')
restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(restore)


def test_copy_preserves_database_and_resolves_without_original(tmp_path, monkeypatch):
    archive, original = fixture_archive(tmp_path)
    old_image = original / 'xdg/chart.png'
    db = (original / 'demo.db').read_bytes()
    destination = tmp_path / 'durable'
    restore.restore(archive, destination, str(original))
    assert (destination / 'demo.db').read_bytes() == db
    assert (original / 'demo.db').read_bytes() == db
    monkeypatch.setenv('XDG_DATA_HOME', str(destination / 'xdg'))
    assert resolve_study_image(str(old_image)) == str(destination / 'xdg/chart.png')
    import shutil
    shutil.rmtree(original)
    assert Path(resolve_study_image(str(old_image))).read_bytes() == b'fixture image bytes'
    # A missing relocated image must never resolve to a still-existing original.
    (destination / 'xdg/chart.png').unlink()
    old_image.parent.mkdir(parents=True);old_image.write_bytes(b'wrong original')
    assert not Path(resolve_study_image(str(old_image))).exists()
    with pytest.raises(ValueError, match='already exists'):
        restore.restore(archive, destination, str(original))


def test_durable_backup_accepts_preserved_historical_paths(tmp_path, monkeypatch):
    archive, original = fixture_archive(tmp_path)
    destination = tmp_path / 'durable'
    restore.restore(archive, destination, str(original))
    next_archive = tmp_path / 'next.tar.gz'
    with tarfile.open(next_archive, 'w:gz') as tar:
        tar.add(destination, arcname=destination.name)
    assert backup.verify(next_archive, destination)['unique_image_references'] == 1
    monkeypatch.setenv('XDG_DATA_HOME', str(destination / 'xdg'))
    assert resolve_study_image('/outside/image.png') == ''
    (destination / 'study-workspace-origin.json').write_text('invalid')
    assert resolve_study_image(str(original / 'xdg/chart.png')) == ''


def test_repeated_recovery_preserves_all_generations(tmp_path, monkeypatch):
    import json
    import shutil
    import sqlite3
    archive, original = fixture_archive(tmp_path)
    current = tmp_path / 'durable'
    restore.restore(archive, current, str(original))
    references = [original / 'xdg/chart.png']
    shutil.rmtree(original)
    for generation in range(3):
        image = current / f'xdg/new-{generation}.png'
        image.write_bytes(f'generation {generation}'.encode())
        references.append(image)
        with sqlite3.connect(current / 'demo.db') as connection:
            connection.execute('INSERT INTO records VALUES (?,?,?)', (str(image), '[]', '{}'))
        database = (current / 'demo.db').read_bytes()
        settings = (current / 'demo.db.workspace.ini').read_bytes()
        previous = json.loads((current / 'study-workspace-origin.json').read_text())
        archive = tmp_path / f'generation-{generation}.tar.gz'
        with tarfile.open(archive, 'w:gz') as tar:
            tar.add(current, arcname=current.name)
        archive_bytes = archive.read_bytes()
        destination = tmp_path / f'recovery-{generation}'
        restore.restore(archive, destination, str(current))
        assert archive.read_bytes() == archive_bytes
        assert (current / 'demo.db').read_bytes() == database
        assert (destination / 'demo.db').read_bytes() == database
        assert (destination / 'demo.db.workspace.ini').read_bytes() == settings
        manifest = json.loads((destination / 'study-workspace-origin.json').read_text())
        assert manifest['previous_manifest'] == previous
        shutil.rmtree(current)
        monkeypatch.setenv('XDG_DATA_HOME', str(destination / 'xdg'))
        for reference in references:
            resolved = Path(resolve_study_image(str(reference)))
            assert resolved.parent == destination / 'xdg'
            assert resolved.is_file()
        assert backup.verify(archive, current)['unique_image_references'] == len(references)
        current = destination
    # Missing copied media never falls back to any surviving older location.
    missing = references[-1]
    missing.parent.mkdir(parents=True)
    missing.write_bytes(b'old location must not be used')
    (current / 'xdg' / missing.name).unlink()
    assert not Path(resolve_study_image(str(missing))).exists()


@pytest.mark.parametrize('manifest', [
    {'version': 3, 'original_root': '/old'},
    {'version': 2, 'original_root': '/old', 'reference_roots': []},
    {'version': 2, 'original_root': '/old', 'reference_roots': ['/old', '/old']},
    {'version': 2, 'original_root': '/old', 'reference_roots': ['/old', '/']},
    {'version': 2, 'original_root': '/old', 'reference_roots': ['/old', '/bad/../path']},
    {'version': 2, 'original_root': '/different', 'reference_roots': ['/old']},
])
def test_bad_manifest_fails_without_destination(tmp_path, monkeypatch, manifest):
    import json
    archive, original = fixture_archive(tmp_path)
    (original / 'study-workspace-origin.json').write_text(json.dumps(manifest))
    with tarfile.open(archive, 'w:gz') as tar:
        tar.add(original, arcname=original.name)
    destination = tmp_path / 'recovery'
    with pytest.raises(ValueError):
        restore.restore(archive, destination, str(original))
    assert not destination.exists()
    monkeypatch.setenv('XDG_DATA_HOME', str(original / 'xdg'))
    assert resolve_study_image(str(original / 'xdg/chart.png')) == ''


def test_nested_destination_refused(tmp_path):
    archive, original = fixture_archive(tmp_path)
    destination = original / 'nested'
    with pytest.raises(ValueError, match='Overlapping'):
        restore.restore(archive, destination, str(original))
    assert not destination.exists()


def test_ambiguous_roots_and_symlink_escape_fail_closed(tmp_path, monkeypatch):
    import json
    from ict_cockpit.media.workspace_paths import reference_relative
    with pytest.raises(ValueError, match='ambiguous'):
        reference_relative('/old/nested/xdg/chart.png', [Path('/old'), Path('/old/nested')])
    workspace = tmp_path / 'copy'
    workspace.mkdir()
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'chart.png').write_bytes(b'not managed media')
    (workspace / 'xdg').symlink_to(outside, target_is_directory=True)
    (workspace / 'study-workspace-origin.json').write_text(json.dumps({
        'version': 2, 'original_root': '/old', 'reference_roots': ['/old', '/durable'],
    }))
    monkeypatch.setenv('XDG_DATA_HOME', str(workspace / 'xdg'))
    assert resolve_study_image('/durable/xdg/chart.png') == ''
