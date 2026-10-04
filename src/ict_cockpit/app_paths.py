import os
from pathlib import Path


APP_DATA_DIRECTORY_NAME = "ict-trading-cockpit"
DATABASE_FILENAME = "ict_cockpit.db"
STUDY_FIND_MEDIA_DIRECTORY = "media/study_finds"


def get_app_data_directory() -> Path:
    xdg_data_home = os.environ.get("XDG_DATA_HOME")

    if xdg_data_home:
        return Path(xdg_data_home) / APP_DATA_DIRECTORY_NAME

    return Path.home() / ".local" / "share" / APP_DATA_DIRECTORY_NAME


def get_database_path() -> Path:
    return get_app_data_directory() / DATABASE_FILENAME

def get_study_find_media_directory() -> Path:
    return get_app_data_directory() / STUDY_FIND_MEDIA_DIRECTORY

def get_study_find_media_path(
    study_find_id: str,
) -> Path:
    return get_study_find_media_directory() / study_find_id