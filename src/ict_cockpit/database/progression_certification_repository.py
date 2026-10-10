import sqlite3

from ict_cockpit.progression import (
    ProgressionBoundary,
    ProgressionCertification,
)


class ProgressionCertificationRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, item: ProgressionCertification) -> ProgressionCertification:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO progression_certification (
                    trade_plan_id,
                    trade_plan_revision,
                    progression_boundary,
                    requirement_id,
                    confirmed,
                    note,
                    confirmed_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(
                    trade_plan_id,
                    trade_plan_revision,
                    progression_boundary,
                    requirement_id
                ) DO UPDATE SET
                    confirmed = excluded.confirmed,
                    note = excluded.note,
                    confirmed_at = excluded.confirmed_at,
                    updated_at = excluded.updated_at
                """,
                (
                    item.trade_plan_id,
                    item.trade_plan_revision,
                    item.boundary.value,
                    item.requirement_id,
                    1 if item.confirmed else 0,
                    item.note,
                    item.confirmed_at,
                    item.updated_at,
                ),
            )
        return item

    def get(
        self,
        trade_plan_id: str,
        trade_plan_revision: str,
        boundary: ProgressionBoundary | str,
        requirement_id: str,
    ) -> ProgressionCertification | None:
        boundary = ProgressionBoundary(boundary)
        row = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision,
                   progression_boundary, requirement_id,
                   confirmed, note, confirmed_at, updated_at
            FROM progression_certification
            WHERE trade_plan_id = ?
              AND trade_plan_revision = ?
              AND progression_boundary = ?
              AND requirement_id = ?
            """,
            (
                trade_plan_id,
                trade_plan_revision,
                boundary.value,
                requirement_id,
            ),
        ).fetchone()
        if row is None:
            return None
        return ProgressionCertification(
            trade_plan_id=row[0],
            trade_plan_revision=row[1],
            boundary=row[2],
            requirement_id=row[3],
            confirmed=bool(row[4]),
            note=row[5],
            confirmed_at=row[6],
            updated_at=row[7],
        )
