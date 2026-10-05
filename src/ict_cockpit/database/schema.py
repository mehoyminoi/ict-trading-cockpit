import sqlite3


CURRENT_SCHEMA_VERSION = 6


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

        if version == 2:
            _migrate_version_2_to_3(connection)
            version = 3

        if version == 3:
            _migrate_version_3_to_4(connection)
            version = 4

        if version == 4:
            _migrate_version_4_to_5(connection)
            version = 5

        if version == 5:
            _migrate_version_5_to_6(connection)
            version = 6

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


def _migrate_version_1_to_2(connection: sqlite3.Connection) -> None:
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


def _migrate_version_2_to_3(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE tda_analysis_v3 (
            id TEXT PRIMARY KEY,
            analysis_date TEXT NOT NULL,
            instrument TEXT NOT NULL,
            weekly_bias TEXT,
            daily_bias TEXT,
            primary_draw TEXT,
            secondary_draw TEXT NOT NULL DEFAULT '',
            narrative TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Draft'
        )
        """
    )
    connection.execute(
        """
        INSERT INTO tda_analysis_v3 (
            id, analysis_date, instrument, weekly_bias, daily_bias,
            primary_draw, secondary_draw, narrative, status
        )
        SELECT
            id, analysis_date, instrument, weekly_bias, daily_bias,
            primary_draw, secondary_draw, narrative, status
        FROM tda_analysis
        """
    )
    connection.execute("DROP TABLE tda_analysis")
    connection.execute(
        "ALTER TABLE tda_analysis_v3 RENAME TO tda_analysis"
    )
    connection.execute("PRAGMA user_version = 3")


def _migrate_version_3_to_4(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE study_find (
            id TEXT PRIMARY KEY,
            observation_date TEXT NOT NULL,
            instrument TEXT NOT NULL,
            session TEXT NOT NULL,
            pattern_name TEXT NOT NULL,
            observation TEXT NOT NULL,
            available_move_handles REAL,
            notes TEXT NOT NULL DEFAULT '',
            image_path TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.execute("PRAGMA user_version = 4")


def _migrate_version_4_to_5(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE study_find_image (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_find_id TEXT NOT NULL,
            image_path TEXT NOT NULL,
            image_order INTEGER NOT NULL,
            FOREIGN KEY (study_find_id)
                REFERENCES study_find(id)
                ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX idx_study_find_image_study_find_id
        ON study_find_image(study_find_id)
        """
    )
    connection.execute("PRAGMA user_version = 5")


def _migrate_version_5_to_6(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE study_find_draft (
            id TEXT PRIMARY KEY,
            observation_date TEXT NOT NULL,
            instrument TEXT NOT NULL DEFAULT '',
            session TEXT NOT NULL DEFAULT '',
            pattern_name TEXT NOT NULL DEFAULT '',
            observation TEXT NOT NULL DEFAULT '',
            available_move_handles REAL,
            notes TEXT NOT NULL DEFAULT '',
            image_paths TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute("PRAGMA user_version = 6")
