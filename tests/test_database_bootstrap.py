from ict_cockpit.database.bootstrap import open_application_database


def test_open_application_database_creates_ready_database(tmp_path) -> None:
    database_path = tmp_path / "app-data" / "ict_cockpit.db"

    connection = open_application_database(database_path)

    assert database_path.exists()

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

    journal_mode = connection.execute(
        "PRAGMA journal_mode"
    ).fetchone()[0]

    foreign_keys = connection.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    assert journal_mode == "wal"
    assert foreign_keys == 1

    connection.close()