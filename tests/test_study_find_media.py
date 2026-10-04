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
    1,
    )

    assert stored.exists()
    assert stored.read_bytes() == b"fake image data"
    assert stored.name == "chart-1.png"

def test_store_multiple_study_find_images(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    first_source = tmp_path / "first.png"
    second_source = tmp_path / "second.jpg"

    first_source.write_bytes(b"first")
    second_source.write_bytes(b"second")

    first = store_study_find_image(
        "study-123",
        first_source,
        1,
    )

    second = store_study_find_image(
        "study-123",
        second_source,
        2,
    )

    assert first.name == "chart-1.png"
    assert second.name == "chart-2.jpg"
    assert first.read_bytes() == b"first"
    assert second.read_bytes() == b"second"