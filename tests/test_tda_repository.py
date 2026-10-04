from datetime import date
import sqlite3
import pytest

from ict_cockpit.analysis.tda import Bias, TDARecord, TDAStatus
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.tda_repository import TDARepository

def test_save_tda_record(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    tda = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.NEUTRAL,
        primary_draw="Previous Week High",
        secondary_draw="Previous Day High",
        narrative="Expecting continuation after liquidity sweep.",
    )

    repository.save(tda)

    row = connection.execute(
        """
        SELECT id, instrument
        FROM tda_analysis
        WHERE id = ?
        """,
        (tda.id,),
    ).fetchone()

    assert row is not None
    assert row[0] == tda.id
    assert row[1] == "MNQ"

    connection.close()

def test_get_tda_record_by_id(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    original = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.BEARISH,
        primary_draw="Previous Week High",
        secondary_draw="Previous Day Low",
        narrative="Weekly and daily draws are conflicting.",
    )

    repository.save(original)

    loaded = repository.get_by_id(original.id)

    assert loaded is not None
    assert loaded.id == original.id
    assert loaded.analysis_date == original.analysis_date
    assert loaded.instrument == original.instrument
    assert loaded.weekly_bias == original.weekly_bias
    assert loaded.daily_bias == original.daily_bias
    assert loaded.primary_draw == original.primary_draw
    assert loaded.secondary_draw == original.secondary_draw
    assert loaded.narrative == original.narrative

    connection.close()

def test_tda_survives_database_reopen(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    first_connection = create_connection(database_path)
    initialize_schema(first_connection)

    first_repository = TDARepository(first_connection)

    original = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.BULLISH,
        primary_draw="Previous Week High",
        secondary_draw="Previous Month High",
        narrative="Testing persistence across database connections.",
    )

    first_repository.save(original)

    first_connection.close()

    second_connection = create_connection(database_path)
    second_repository = TDARepository(second_connection)

    loaded = second_repository.get_by_id(original.id)

    assert loaded is not None
    assert loaded.id == original.id
    assert loaded.analysis_date == original.analysis_date
    assert loaded.instrument == original.instrument
    assert loaded.weekly_bias == original.weekly_bias
    assert loaded.daily_bias == original.daily_bias
    assert loaded.primary_draw == original.primary_draw
    assert loaded.secondary_draw == original.secondary_draw
    assert loaded.narrative == original.narrative

    second_connection.close()

def test_get_by_id_returns_none_when_record_does_not_exist(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    loaded = repository.get_by_id("does-not-exist")

    assert loaded is None

    connection.close()

def test_save_rejects_duplicate_tda_id(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    tda = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.BULLISH,
        primary_draw="Previous Week High",
    )

    repository.save(tda)

    with pytest.raises(sqlite3.IntegrityError):
        repository.save(tda)

    connection.close()

def test_update_existing_tda_record(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    original = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.BULLISH,
        primary_draw="Previous Week High",
        narrative="Original narrative.",
    )

    repository.save(original)

    updated = TDARecord(
        id=original.id,
        analysis_date=original.analysis_date,
        instrument=original.instrument,
        weekly_bias=Bias.BEARISH,
        daily_bias=Bias.NEUTRAL,
        primary_draw="Previous Day Low",
        secondary_draw="Weekly Open",
        narrative="Updated narrative.",
    )

    repository.update(updated)

    loaded = repository.get_by_id(original.id)

    assert loaded is not None
    assert loaded.id == original.id
    assert loaded.weekly_bias == Bias.BEARISH
    assert loaded.daily_bias == Bias.NEUTRAL
    assert loaded.primary_draw == "Previous Day Low"
    assert loaded.secondary_draw == "Weekly Open"
    assert loaded.narrative == "Updated narrative."

    connection.close()

def test_update_raises_when_tda_does_not_exist(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    missing = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.NEUTRAL,
        daily_bias=Bias.NEUTRAL,
        primary_draw="No clear draw",
    )

    with pytest.raises(KeyError):
        repository.update(missing)

    connection.close()

def test_tda_status_survives_persistence(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    original = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.BULLISH,
        primary_draw="Previous Week High",
        status=TDAStatus.INCOMPLETE_OVERRIDE,
    )

    repository.save(original)

    loaded = repository.get_by_id(original.id)

    assert loaded is not None
    assert loaded.status == TDAStatus.INCOMPLETE_OVERRIDE

    connection.close()

def test_incomplete_tda_preserves_missing_values(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    repository = TDARepository(connection)

    original = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=None,
        primary_draw=None,
        status=TDAStatus.INCOMPLETE_OVERRIDE,
    )

    repository.save(original)

    loaded = repository.get_by_id(original.id)

    assert loaded is not None
    assert loaded.weekly_bias == Bias.BULLISH
    assert loaded.daily_bias is None
    assert loaded.primary_draw is None
    assert loaded.status == TDAStatus.INCOMPLETE_OVERRIDE

    connection.close()

def test_schema_version_3_allows_incomplete_tda_fields(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    columns = connection.execute(
        "PRAGMA table_info(tda_analysis)"
    ).fetchall()

    columns_by_name = {
        column[1]: column
        for column in columns
    }

    assert columns_by_name["weekly_bias"][3] == 0
    assert columns_by_name["daily_bias"][3] == 0
    assert columns_by_name["primary_draw"][3] == 0

    connection.close()