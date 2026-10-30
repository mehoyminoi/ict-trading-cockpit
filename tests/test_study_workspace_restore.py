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
