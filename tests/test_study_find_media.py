from pathlib import Path

from ict_cockpit.media.study_find_media import (
    store_study_find_image,
)


def test_store_study_find_image_copies_file(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    source = tmp_path / "source.png"
    source.write_bytes(b"fake image data")

    stored = store_study_find_image(
        "study-123",
        source,
    )

    assert stored.exists()
    assert stored.read_bytes() == b"fake image data"
    assert stored.name == "chart-1.png"