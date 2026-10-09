import sqlite3

from ict_cockpit.analysis.competency import (
    CompetencyEvidenceMaturityProfile,
)


class CompetencyEvidenceMaturityRepository:
    """Persistence for current boundary-aware Evidence Maturity profiles."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(
        self,
        item: CompetencyEvidenceMaturityProfile,
    ) -> CompetencyEvidenceMaturityProfile:
        existing = self.get(
            item.trade_plan_id,
            item.competency_id,
            item.progression_boundary.value,
        )
        created_at = existing.created_at if existing is not None else item.created_at
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO competency_evidence_maturity (
                    trade_plan_id,
                    trade_plan_revision,
                    competency_id,
                    progression_boundary,
                    maturity_state,
                    maturity_note,
                    consistency_note,
                    known_gap_note,
                    source,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(
                    trade_plan_id,
                    competency_id,
                    progression_boundary
                ) DO UPDATE SET
                    trade_plan_revision = excluded.trade_plan_revision,
                    maturity_state = excluded.maturity_state,
                    maturity_note = excluded.maturity_note,
                    consistency_note = excluded.consistency_note,
                    known_gap_note = excluded.known_gap_note,
                    source = excluded.source,
                    updated_at = excluded.updated_at
                """,
                (
                    item.trade_plan_id,
                    item.trade_plan_revision,
                    item.competency_id,
                    item.progression_boundary.value,
                    item.maturity_state.value,
                    item.maturity_note,
                    item.consistency_note,
                    item.known_gap_note,
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
        progression_boundary: str,
    ) -> CompetencyEvidenceMaturityProfile | None:
        row = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision, competency_id,
                   progression_boundary, maturity_state, maturity_note,
                   consistency_note, known_gap_note, source,
                   created_at, updated_at
            FROM competency_evidence_maturity
            WHERE trade_plan_id = ?
              AND competency_id = ?
              AND progression_boundary = ?
            """,
            (trade_plan_id, competency_id, progression_boundary),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def list_for_competency(
        self,
        trade_plan_id: str,
        competency_id: str,
    ) -> list[CompetencyEvidenceMaturityProfile]:
        rows = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision, competency_id,
                   progression_boundary, maturity_state, maturity_note,
                   consistency_note, known_gap_note, source,
                   created_at, updated_at
            FROM competency_evidence_maturity
            WHERE trade_plan_id = ? AND competency_id = ?
            ORDER BY progression_boundary
            """,
            (trade_plan_id, competency_id),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row) -> CompetencyEvidenceMaturityProfile:
        return CompetencyEvidenceMaturityProfile(
            trade_plan_id=row[0],
            trade_plan_revision=row[1],
            competency_id=row[2],
            progression_boundary=row[3],
            maturity_state=row[4],
            maturity_note=row[5],
            consistency_note=row[6],
            known_gap_note=row[7],
            source=row[8],
            created_at=row[9],
            updated_at=row[10],
        )
