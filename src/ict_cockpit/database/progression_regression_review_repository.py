import json
import sqlite3

from ict_cockpit.progression import (
    ProgressionBoundary,
    ProgressionRegressionReview,
)


class ProgressionRegressionReviewRepository:
    """Human review of lost support for an already-attained boundary."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(
        self,
        item: ProgressionRegressionReview,
    ) -> ProgressionRegressionReview:
        existing = self.get(
            item.trade_plan_id,
            item.trade_plan_revision,
            item.boundary,
            item.prior_attainment_id,
        )
        created_at = existing.created_at if existing is not None else item.created_at
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO progression_regression_review (
                    trade_plan_id,
                    trade_plan_revision,
                    progression_boundary,
                    prior_attainment_id,
                    eligibility_snapshot_json,
                    classification,
                    note,
                    supporting_evidence_ids_json,
                    source,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(
                    trade_plan_id,
                    trade_plan_revision,
                    progression_boundary,
                    prior_attainment_id
                ) DO UPDATE SET
                    eligibility_snapshot_json =
                        excluded.eligibility_snapshot_json,
                    classification = excluded.classification,
                    note = excluded.note,
                    supporting_evidence_ids_json =
                        excluded.supporting_evidence_ids_json,
                    source = excluded.source,
                    updated_at = excluded.updated_at
                """,
                (
                    item.trade_plan_id,
                    item.trade_plan_revision,
                    item.boundary.value,
                    item.prior_attainment_id,
                    json.dumps(item.eligibility_snapshot, sort_keys=True),
                    item.classification.value,
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
        trade_plan_revision: str,
        boundary: ProgressionBoundary | str,
        prior_attainment_id: str,
    ) -> ProgressionRegressionReview | None:
        boundary = ProgressionBoundary(boundary)
        row = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision,
                   progression_boundary, prior_attainment_id,
                   eligibility_snapshot_json, classification, note,
                   supporting_evidence_ids_json, source,
                   created_at, updated_at
            FROM progression_regression_review
            WHERE trade_plan_id = ?
              AND trade_plan_revision = ?
              AND progression_boundary = ?
              AND prior_attainment_id = ?
            """,
            (
                trade_plan_id,
                trade_plan_revision,
                boundary.value,
                prior_attainment_id,
            ),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def list_for_plan(
        self,
        trade_plan_id: str,
    ) -> list[ProgressionRegressionReview]:
        rows = self.connection.execute(
            """
            SELECT trade_plan_id, trade_plan_revision,
                   progression_boundary, prior_attainment_id,
                   eligibility_snapshot_json, classification, note,
                   supporting_evidence_ids_json, source,
                   created_at, updated_at
            FROM progression_regression_review
            WHERE trade_plan_id = ?
            ORDER BY updated_at DESC
            """,
            (trade_plan_id,),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row) -> ProgressionRegressionReview:
        return ProgressionRegressionReview(
            trade_plan_id=row[0],
            trade_plan_revision=row[1],
            boundary=row[2],
            prior_attainment_id=row[3],
            eligibility_snapshot=json.loads(row[4] or "{}"),
            classification=row[5],
            note=row[6],
            supporting_evidence_ids=json.loads(row[7] or "[]"),
            source=row[8],
            created_at=row[9],
            updated_at=row[10],
        )
