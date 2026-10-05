import shutil
from pathlib import Path

from ict_cockpit.app_paths import get_trade_media_path


def get_trade_image_destination(
    trade_id: str,
    image_number: int,
    suffix: str,
) -> Path:
    destination_directory = get_trade_media_path(trade_id)
    destination_directory.mkdir(parents=True, exist_ok=True)

    normalized_suffix = suffix.lower()
    if not normalized_suffix.startswith("."):
        normalized_suffix = f".{normalized_suffix}"

    return destination_directory / f"chart-{image_number}{normalized_suffix}"


def store_trade_image(
    trade_id: str,
    source_path: Path,
    image_number: int,
) -> Path:
    destination_path = get_trade_image_destination(
        trade_id,
        image_number,
        source_path.suffix,
    )
    shutil.copy2(source_path, destination_path)
    return destination_path
