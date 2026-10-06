import sqlite3


CURRENT_SCHEMA_VERSION = 13


def initialize_schema(connection: sqlite3.Connection) -> None:
    with connection:
        version = connection.execute("PRAGMA user_version").fetchone()[0]

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
        if version == 6:
            _migrate_version_6_to_7(connection)
            version = 7
        if version == 7:
            _migrate_version_7_to_8(connection)
            version = 8
        if version == 8:
            _migrate_version_8_to_9(connection)
            version = 9
        if version == 9:
            _migrate_version_9_to_10(connection)
            version = 10
        if version == 10:
            _migrate_version_10_to_11(connection)
            version = 11
        if version == 11:
            _migrate_version_11_to_12(connection)
            version = 12
        if version == 12:
            _migrate_version_12_to_13(connection)
            version = 13

        if version != CURRENT_SCHEMA_VERSION:
            raise RuntimeError(f"Unsupported database schema version: {version}")


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
    columns = connection.execute("PRAGMA table_info(tda_analysis)").fetchall()
    column_names = {column[1] for column in columns}
    if "status" not in column_names:
        connection.execute(
            "ALTER TABLE tda_analysis ADD COLUMN status TEXT NOT NULL DEFAULT 'Draft'"
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
        SELECT id, analysis_date, instrument, weekly_bias, daily_bias,
               primary_draw, secondary_draw, narrative, status
        FROM tda_analysis
        """
    )
    connection.execute("DROP TABLE tda_analysis")
    connection.execute("ALTER TABLE tda_analysis_v3 RENAME TO tda_analysis")
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
            FOREIGN KEY (study_find_id) REFERENCES study_find(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_study_find_image_study_find_id ON study_find_image(study_find_id)"
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


def _migrate_version_6_to_7(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE feedback_entry (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            category TEXT NOT NULL,
            note TEXT NOT NULL,
            context TEXT NOT NULL DEFAULT '',
            record_id TEXT NOT NULL DEFAULT '',
            app_version TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_feedback_entry_created_at ON feedback_entry(created_at)"
    )
    connection.execute("PRAGMA user_version = 7")


def _migrate_version_7_to_8(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE trade_record (
            id TEXT PRIMARY KEY,
            instrument TEXT NOT NULL,
            trade_source TEXT NOT NULL,
            account_context TEXT NOT NULL DEFAULT '',
            trade_number INTEGER NOT NULL,
            model TEXT NOT NULL DEFAULT '',
            direction TEXT NOT NULL,
            entry_tf TEXT NOT NULL DEFAULT '',
            entry_time TEXT NOT NULL,
            close_time TEXT NOT NULL,
            entry_price REAL NOT NULL,
            close_price REAL NOT NULL,
            stop_price REAL NOT NULL,
            tick_size REAL NOT NULL,
            cycle_16y TEXT NOT NULL DEFAULT '',
            quadrennial TEXT NOT NULL DEFAULT '',
            quarter TEXT NOT NULL DEFAULT '',
            month TEXT NOT NULL DEFAULT '',
            week TEXT NOT NULL DEFAULT '',
            day TEXT NOT NULL DEFAULT '',
            session TEXT NOT NULL DEFAULT '',
            macro_90m TEXT NOT NULL DEFAULT '',
            summary TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE trade_record_image (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_record_id TEXT NOT NULL,
            image_path TEXT NOT NULL,
            image_order INTEGER NOT NULL,
            FOREIGN KEY (trade_record_id) REFERENCES trade_record(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE trade_record_draft (
            id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute("PRAGMA user_version = 8")


def _migrate_version_8_to_9(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE tda_station_session (
            id TEXT PRIMARY KEY,
            blueprint_revision TEXT NOT NULL,
            current_station_id TEXT NOT NULL,
            observations_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_tda_station_session_updated_at ON tda_station_session(updated_at)"
    )
    connection.execute("PRAGMA user_version = 9")


def _migrate_version_9_to_10(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE trading_day_session (
            id TEXT PRIMARY KEY,
            blueprint_revision TEXT NOT NULL,
            mode_ids_json TEXT NOT NULL,
            current_mode_id TEXT NOT NULL,
            completed_mode_ids_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_trading_day_session_updated_at ON trading_day_session(updated_at)"
    )
    connection.execute("PRAGMA user_version = 10")


def _migrate_version_10_to_11(connection: sqlite3.Connection) -> None:
    connection.execute(
        "ALTER TABLE trading_day_session ADD COLUMN status TEXT NOT NULL DEFAULT 'Active'"
    )
    connection.execute(
        "ALTER TABLE trading_day_session ADD COLUMN day_outcome TEXT NOT NULL DEFAULT ''"
    )
    connection.execute(
        "ALTER TABLE trading_day_session ADD COLUMN transitions_json TEXT NOT NULL DEFAULT '[]'"
    )
    connection.execute("PRAGMA user_version = 11")


def _migrate_version_11_to_12(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE trading_day (
            id TEXT PRIMARY KEY,
            futures_day_label TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Active',
            active_session_run_id TEXT NOT NULL DEFAULT '',
            started_at TEXT NOT NULL,
            completed_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_trading_day_updated_at ON trading_day(updated_at)"
    )
    connection.execute(
        """
        CREATE TABLE trading_session_run (
            id TEXT PRIMARY KEY,
            trading_day_id TEXT NOT NULL,
            session_name TEXT NOT NULL,
            process_session_id TEXT NOT NULL,
            tda_station_session_id TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Active',
            outcome TEXT NOT NULL DEFAULT '',
            started_at TEXT NOT NULL,
            concluded_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            FOREIGN KEY (trading_day_id) REFERENCES trading_day(id) ON DELETE CASCADE,
            FOREIGN KEY (process_session_id) REFERENCES trading_day_session(id) ON DELETE RESTRICT
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_trading_session_run_day ON trading_session_run(trading_day_id, started_at)"
    )
    connection.execute("PRAGMA user_version = 12")


def _migrate_version_12_to_13(connection: sqlite3.Connection) -> None:
    connection.execute(
        "ALTER TABLE trading_session_run ADD COLUMN current_thesis_state TEXT NOT NULL DEFAULT 'Not Set'"
    )
    connection.execute(
        "ALTER TABLE trading_session_run ADD COLUMN evidence_json TEXT NOT NULL DEFAULT '[]'"
    )
    connection.execute("PRAGMA user_version = 13")
