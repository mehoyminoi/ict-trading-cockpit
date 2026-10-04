from pathlib import Path

from ict_cockpit.app_paths import (
    APP_DATA_DIRECTORY_NAME,
    DATABASE_FILENAME,
    get_app_data_directory,
    get_database_path,
    get_study_find_media_path,
)


def test_app_data_directory_uses_xdg_data_home(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    result = get_app_data_directory()

    assert result == tmp_path / APP_DATA_DIRECTORY_NAME


def test_database_path_is_inside_app_data_directory(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    result = get_database_path()

    assert result == tmp_path / APP_DATA_DIRECTORY_NAME / DATABASE_FILENAME

def test_study_find_media_path_uses_study_find_id(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    result = get_study_find_media_path("abc123")

    assert result == (
        tmp_path
        / APP_DATA_DIRECTORY_NAME
        / "media"
        / "study_finds"
        / "abc123"
    )