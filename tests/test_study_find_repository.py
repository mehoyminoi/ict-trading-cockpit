from datetime import date

from ict_cockpit.analysis.study_find import StudyFind
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository


def test_save_and_load_study_find(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = StudyFindRepository(connection)

    original = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="MNQ",
        session="NYAM",
        pattern_name="London low raid",
        observation="Bullish displacement followed the sweep.",
        available_move_handles=74.5,
        notes="Clean example.",
        image_path="/tmp/example.png",
    )

    repository.save(original)

    loaded = repository.get_by_id(original.id)

    assert loaded is not None
    assert loaded.id == original.id
    assert loaded.observation_date == original.observation_date
    assert loaded.instrument == original.instrument
    assert loaded.session == original.session
    assert loaded.pattern_name == original.pattern_name
    assert loaded.observation == original.observation
    assert loaded.available_move_handles == original.available_move_handles
    assert loaded.notes == original.notes
    assert loaded.image_path == original.image_path

    connection.close()

def test_study_find_survives_database_reopen(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    first_connection = create_connection(database_path)
    initialize_schema(first_connection)

    first_repository = StudyFindRepository(first_connection)

    original = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="MNQ",
        session="NYAM",
        pattern_name="FVG continuation",
        observation="Price returned to the imbalance and expanded higher.",
        available_move_handles=42.0,
    )

    first_repository.save(original)

    first_connection.close()

    second_connection = create_connection(database_path)
    second_repository = StudyFindRepository(second_connection)

    loaded = second_repository.get_by_id(original.id)

    assert loaded is not None
    assert loaded.id == original.id
    assert loaded.pattern_name == "FVG continuation"
    assert loaded.available_move_handles == 42.0

    second_connection.close()

def test_get_by_id_returns_none_when_study_find_missing(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = StudyFindRepository(connection)

    loaded = repository.get_by_id("does-not-exist")

    assert loaded is None

    connection.close()

def test_study_find_repository_stores_multiple_images(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = StudyFindRepository(connection)

    study_find = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="MNQ",
        session="NYAM",
        pattern_name="London low raid",
        observation="Test observation.",
    )

    repository.save(study_find)

    repository.add_image(
        study_find.id,
        "/tmp/chart-1.png",
    )

    repository.add_image(
        study_find.id,
        "/tmp/chart-2.png",
    )

    images = repository.get_images(
        study_find.id
    )

    assert images == [
        "/tmp/chart-1.png",
        "/tmp/chart-2.png",
    ]

    connection.close()