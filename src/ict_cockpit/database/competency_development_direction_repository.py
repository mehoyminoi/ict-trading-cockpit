import json
import sqlite3

from ict_cockpit.analysis.competency import (
    CompetencyDevelopmentDirection,
)


class CompetencyDevelopmentDirectionRepository:
    """Persistence for current human-reviewed Development Direction."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(
        self,
        item: CompetencyDevelopmentDirection,
    ) -> CompetencyDevelopmentDirection:
        existing = self.get(item.trade_plan_id, item.competency_id)
        created_at = existing.created_at if existing is not None else item.created_at
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO competency_development_direction (
                    trade_plan_id,
                    trade_plan_revision,
                    competency_id,
                    direction,
                    note,
                    supporting_evidence_ids_json,
                    source,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(trade_plan_id, competency_id) DO UPDATE SET
                    trade_plan_revision = excluded.trade_plan_revision,
                    direction = excluded.direction,
                    note = excluded.note,
                    supporting_evidence_ids_json = excluded.supporting_evidence_ids_json,
                    source = excluded.source,
                    updated_at = excluded.updated_at
                """,
                (
                    item.trade_plan_id,
                    item.trade_plan_revision,
                    item.competency_id,
                    item.direction.value,
                    item.note,
                    json.dumps(item.supporting_evidence_ids),
                    item.source,
                    created_at,
                    item.updated_at,
                ),
            )
        item.created_at = created_at
        return item

    def get(
        self,
        trade_plan_id: str,
        competency_id: str,
    ) -> CompetencyDevelopmentDirection | None:
        row = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision, competency_id,
                   direction, note, supporting_evidence_ids_json,
                   source, created_at, updated_at
            FROM competency_development_direction
            WHERE trade_plan_id = ? AND competency_id = ?
            """,
            (trade_plan_id, competency_id),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def list_for_plan(
        self,
        trade_plan_id: str,
    ) -> list[CompetencyDevelopmentDirection]:
        rows = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision, competency_id,
                   direction, note, supporting_evidence_ids_json,
                   source, created_at, updated_at
            FROM competency_development_direction
            WHERE trade_plan_id = ?
            ORDER BY competency_id
            """,
            (trade_plan_id,),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row) -> CompetencyDevelopmentDirection:
        return CompetencyDevelopmentDirection(
            trade_plan_id=row[0],
            trade_plan_revision=row[1],
            competency_id=row[2],
            direction=row[3],
            note=row[4],
            supporting_evidence_ids=json.loads(row[5] or "[]"),
            source=row[6],
            created_at=row[7],
            updated_at=row[8],
        )
