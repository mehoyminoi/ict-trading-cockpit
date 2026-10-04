import sqlite3


CURRENT_SCHEMA_VERSION = 2


def initialize_schema(connection: sqlite3.Connection) -> None:
    with connection:
        version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        if version == 0:
            _initialize_version_1(connection)
            version = 1

        if version == 1:
            _migrate_version_1_to_2(connection)
            version = 2

        if version != CURRENT_SCHEMA_VERSION:
            raise RuntimeError(
                f"Unsupported database schema version: {version}"
            )


def _initialize_version_1(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tda_analysis (
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


def _migrate_version_1_to_2(
    connection: sqlite3.Connection,
) -> None:
    columns = connection.execute(
        "PRAGMA table_info(tda_analysis)"
    ).fetchall()

    column_names = {column[1] for column in columns}

    if "status" not in column_names:
        connection.execute(
            """
            ALTER TABLE tda_analysis
            ADD COLUMN status TEXT NOT NULL DEFAULT 'Draft'
            """
        )

    connection.execute("PRAGMA user_version = 2")