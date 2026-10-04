from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.schema import (
    CURRENT_SCHEMA_VERSION)

def test_create_connection(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)

    assert database_path.exists()

    connection.close()

def test_connection_configures_sqlite(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)

    journal_mode = connection.execute(
        "PRAGMA journal_mode"
    ).fetchone()[0]

    foreign_keys = connection.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    assert journal_mode == "wal"
    assert foreign_keys == 1

    connection.close()

def test_initialize_schema_creates_tda_table(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)

    initialize_schema(connection)

    table = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'tda_analysis'
        """
    ).fetchone()

    assert table is not None
    assert table[0] == "tda_analysis"

    connection.close()

def test_initialize_schema_can_run_multiple_times(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)

    initialize_schema(connection)
    initialize_schema(connection)

    table = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'tda_analysis'
        """
    ).fetchone()

    assert table is not None

    connection.close()

def test_initialize_schema_sets_current_version(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)

    initialize_schema(connection)

    version = connection.execute(
        "PRAGMA user_version"
    ).fetchone()[0]

    assert version == CURRENT_SCHEMA_VERSION

    connection.close()
    
def test_schema_migrates_existing_v1_database(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)

    with connection:
        connection.execute(
            """
            CREATE TABLE tda_analysis (
                id TEXT PRIMARY KEY,
                analysis_date TEXT NOT NULL,
                instrument TEXT NOT NULL,
                weekly_bias TEXT NOT NULL,
                daily_bias TEXT NOT NULL,
                primary_draw TEXT NOT NULL,
                secondary_draw TEXT NOT NULL DEFAULT '',
                narrative TEXT NOT NULL DEFAULT ''
            )
            """
        )

        connection.execute("PRAGMA user_version = 1")

    initialize_schema(connection)

    columns = connection.execute(
        "PRAGMA table_info(tda_analysis)"
    ).fetchall()

    column_names = {column[1] for column in columns}

    version = connection.execute(
        "PRAGMA user_version"
    ).fetchone()[0]

    assert "status" in column_names
    assert version == CURRENT_SCHEMA_VERSION

    connection.close()

def test_schema_creates_study_find_table(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    table = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'study_find'
        """
    ).fetchone()

    assert table is not None
    assert table[0] == "study_find"

    connection.close()

def test_schema_creates_study_find_image_table(tmp_path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)
    initialize_schema(connection)

    table = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'study_find_image'
        """
    ).fetchone()

    assert table is not None
    assert table[0] == "study_find_image"

    connection.close()