import sqlite3

from ict_cockpit.analysis.competency import (
    CompetencyAssessment,
    CompetencyState,
)


class CompetencyAssessmentRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, assessment: CompetencyAssessment) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO competency_assessment (
                    trade_plan_id,
                    trade_plan_revision,
                    competency_id,
                    state,
                    note,
                    source,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(
                    trade_plan_id,
                    competency_id
                ) DO UPDATE SET
                    trade_plan_revision = excluded.trade_plan_revision,
                    state = excluded.state,
                    note = excluded.note,
                    source = excluded.source,
                    updated_at = excluded.updated_at
                """,
                (
                    assessment.trade_plan_id,
                    assessment.trade_plan_revision,
                    assessment.competency_id,
                    assessment.state.value,
                    assessment.note,
                    assessment.source,
                    assessment.updated_at,
                ),
            )

    def get(
        self,
        trade_plan_id: str,
        competency_id: str,
    ) -> CompetencyAssessment | None:
        row = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision, competency_id,
                   state, note, source, updated_at
            FROM competency_assessment
            WHERE trade_plan_id = ?
              AND competency_id = ?
            """,
            (
                trade_plan_id,
                competency_id,
            ),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def list_for_plan(
        self,
        trade_plan_id: str,
    ) -> list[CompetencyAssessment]:
        rows = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision, competency_id,
                   state, note, source, updated_at
            FROM competency_assessment
            WHERE trade_plan_id = ?
            ORDER BY competency_id
            """,
            (trade_plan_id,),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row) -> CompetencyAssessment:
        return CompetencyAssessment(
            trade_plan_id=row[0],
            trade_plan_revision=row[1],
            competency_id=row[2],
            state=CompetencyState(row[3]),
            note=row[4],
            source=row[5],
            updated_at=row[6],
        )
