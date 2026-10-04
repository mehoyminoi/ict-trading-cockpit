import sqlite3


def initialize_schema(connection: sqlite3.Connection) -> None:
    with connection:
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