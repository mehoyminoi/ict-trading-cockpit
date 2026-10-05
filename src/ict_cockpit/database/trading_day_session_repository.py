import json
import sqlite3

from ict_cockpit.analysis.trading_day_session import TradingDaySession


class TradingDaySessionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, session: TradingDaySession) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO trading_day_session (
                    id, blueprint_revision, mode_ids_json, current_mode_id,
                    completed_mode_ids_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    blueprint_revision = excluded.blueprint_revision,
                    mode_ids_json = excluded.mode_ids_json,
                    current_mode_id = excluded.current_mode_id,
                    completed_mode_ids_json = excluded.completed_mode_ids_json,
                    updated_at = excluded.updated_at
                """,
                (
                    session.id,
                    session.blueprint_revision,
                    json.dumps(session.mode_ids),
                    session.current_mode_id,
                    json.dumps(session.completed_mode_ids),
                    session.updated_at,
                ),
            )

    def get_latest(self) -> TradingDaySession | None:
        row = self.connection.execute(
            """
            SELECT id, blueprint_revision, mode_ids_json, current_mode_id,
                   completed_mode_ids_json, updated_at
            FROM trading_day_session
            ORDER BY updated_at DESC, rowid DESC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None

        return TradingDaySession(
            id=row[0],
            blueprint_revision=row[1],
            mode_ids=list(json.loads(row[2])),
            current_mode_id=row[3],
            completed_mode_ids=list(json.loads(row[4])),
            updated_at=row[5],
        )

    def delete(self, session_id: str) -> None:
        with self.connection:
            self.connection.execute(
                "DELETE FROM trading_day_session WHERE id = ?",
                (session_id,),
            )
