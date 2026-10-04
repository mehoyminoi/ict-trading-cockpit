import shutil
from pathlib import Path

from ict_cockpit.app_paths import get_study_find_media_path


def store_study_find_image(
    study_find_id: str,
    source_path: Path,
) -> Path:
    destination_directory = get_study_find_media_path(
        study_find_id
    )

    destination_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination_path = (
        destination_directory
        / f"chart-1{source_path.suffix.lower()}"
    )

    shutil.copy2(
        source_path,
        destination_path,
    )

    return destination_path