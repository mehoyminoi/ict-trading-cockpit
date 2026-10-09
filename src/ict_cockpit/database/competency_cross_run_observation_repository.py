import json
import sqlite3

from ict_cockpit.analysis.competency import CompetencyCrossRunObservation


class CompetencyCrossRunObservationRepository:
    """Persistence for current human-authored Cross-Run Observation."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(
        self,
        item: CompetencyCrossRunObservation,
    ) -> CompetencyCrossRunObservation:
        existing = self.get(item.trade_plan_id, item.competency_id)
        created_at = existing.created_at if existing is not None else item.created_at
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO competency_cross_run_observation (
                    trade_plan_id,
                    trade_plan_revision,
                    competency_id,
                    observation,
                    supporting_evidence_ids_json,
                    source,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(trade_plan_id, competency_id) DO UPDATE SET
                    trade_plan_revision = excluded.trade_plan_revision,
                    observation = excluded.observation,
                    supporting_evidence_ids_json = excluded.supporting_evidence_ids_json,
                    source = excluded.source,
                    updated_at = excluded.updated_at
                """,
                (
                    item.trade_plan_id,
                    item.trade_plan_revision,
                    item.competency_id,
                    item.observation,
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
    ) -> CompetencyCrossRunObservation | None:
        row = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision, competency_id,
                   observation, supporting_evidence_ids_json,
                   source, created_at, updated_at
            FROM competency_cross_run_observation
            WHERE trade_plan_id = ? AND competency_id = ?
            """,
            (trade_plan_id, competency_id),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def list_for_plan(
        self,
        trade_plan_id: str,
    ) -> list[CompetencyCrossRunObservation]:
        rows = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision, competency_id,
                   observation, supporting_evidence_ids_json,
                   source, created_at, updated_at
            FROM competency_cross_run_observation
            WHERE trade_plan_id = ?
            ORDER BY competency_id
            """,
            (trade_plan_id,),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row) -> CompetencyCrossRunObservation:
        return CompetencyCrossRunObservation(
            trade_plan_id=row[0],
            trade_plan_revision=row[1],
            competency_id=row[2],
            observation=row[3],
            supporting_evidence_ids=json.loads(row[4] or "[]"),
            source=row[5],
            created_at=row[6],
            updated_at=row[7],
        )
