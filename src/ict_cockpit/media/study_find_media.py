import shutil
from pathlib import Path

from ict_cockpit.app_paths import get_study_find_media_path


def get_study_find_image_destination(
    study_find_id: str,
    image_number: int,
    suffix: str,
) -> Path:
    """Return a managed path for one Study Find chart image."""
    destination_directory = get_study_find_media_path(study_find_id)
    destination_directory.mkdir(parents=True, exist_ok=True)

    normalized_suffix = suffix.lower()
    if not normalized_suffix.startswith("."):
        normalized_suffix = f".{normalized_suffix}"

    return destination_directory / f"chart-{image_number}{normalized_suffix}"


def store_study_find_image(
    study_find_id: str,
    source_path: Path,
    image_number: int,
) -> Path:
    destination_path = get_study_find_image_destination(
        study_find_id,
        image_number,
        source_path.suffix,
    )

    shutil.copy2(source_path, destination_path)
    return destination_path
