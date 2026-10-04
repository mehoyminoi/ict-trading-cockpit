import sqlite3
from pathlib import Path

from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.app_paths import get_database_path


def open_application_database(database_path: Path) -> sqlite3.Connection:
    connection = create_connection(database_path)
    initialize_schema(connection)

    return connection

def open_default_application_database() -> sqlite3.Connection:
    return open_application_database(get_database_path())