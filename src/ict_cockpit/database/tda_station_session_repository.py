import json
import sqlite3

from ict_cockpit.analysis.tda_station_session import (
    TDAStationObservation,
    TDAStationSession,
)


class TDAStationSessionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, session: TDAStationSession) -> None:
        payload = [
            {
                "station_id": item.station_id,
                "observation": item.observation,
                "completed": item.completed,
                "completed_actions": item.completed_actions,
            }
            for item in session.observations
        ]
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO tda_station_session (
                    id, blueprint_revision, current_station_id,
                    observations_json, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    blueprint_revision = excluded.blueprint_revision,
                    current_station_id = excluded.current_station_id,
                    observations_json = excluded.observations_json,
                    updated_at = excluded.updated_at
                """,
                (
                    session.id,
                    session.blueprint_revision,
                    session.current_station_id,
                    json.dumps(payload),
                    session.updated_at,
                ),
            )

    def get_latest(self) -> TDAStationSession | None:
        row = self.connection.execute(
            """
            SELECT id, blueprint_revision, current_station_id,
                   observations_json, updated_at
            FROM tda_station_session
            ORDER BY updated_at DESC, rowid DESC
            LIMIT 1
            """
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def get_by_id(self, session_id: str) -> TDAStationSession | None:
        row = self.connection.execute(
            """
            SELECT id, blueprint_revision, current_station_id,
                   observations_json, updated_at
            FROM tda_station_session
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    @staticmethod
    def _from_row(row) -> TDAStationSession:
        payload = json.loads(row[3])
        return TDAStationSession(
            id=row[0],
            blueprint_revision=row[1],
            current_station_id=row[2],
            observations=[
                TDAStationObservation(
                    station_id=item["station_id"],
                    observation=item.get("observation", ""),
                    completed=bool(item.get("completed", False)),
                    completed_actions=list(item.get("completed_actions", [])),
                )
                for item in payload
            ],
            updated_at=row[4],
        )

    def delete(self, session_id: str) -> None:
        with self.connection:
            self.connection.execute(
                "DELETE FROM tda_station_session WHERE id = ?",
                (session_id,),
            )
