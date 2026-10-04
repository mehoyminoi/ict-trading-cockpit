from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema


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