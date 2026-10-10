import json
import sqlite3

from ict_cockpit.progression import ProgressionAttainment, ProgressionBoundary


class ProgressionAttainmentRepository:
    """Immutable history for deliberately crossed progression boundaries."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def record_if_absent(
        self,
        item: ProgressionAttainment,
    ) -> ProgressionAttainment:
        existing = self.get_for_policy(
            item.trade_plan_id,
            item.trade_plan_revision,
            item.boundary,
            item.policy_id,
        )
        if existing is not None:
            return existing

        with self.connection:
            self.connection.execute(
                """
                INSERT INTO progression_attainment (
                    id,
                    trade_plan_id,
                    trade_plan_revision,
                    progression_boundary,
                    policy_id,
                    eligibility_snapshot_json,
                    attained_environment,
                    attained_at,
                    source,
                    note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.trade_plan_id,
                    item.trade_plan_revision,
                    item.boundary.value,
                    item.policy_id,
                    json.dumps(item.eligibility_snapshot, sort_keys=True),
                    item.attained_environment,
                    item.attained_at,
                    item.source,
                    item.note,
                ),
            )
        return item

    def get_for_policy(
        self,
        trade_plan_id: str,
        trade_plan_revision: str,
        boundary: ProgressionBoundary | str,
        policy_id: str,
    ) -> ProgressionAttainment | None:
        boundary = ProgressionBoundary(boundary)
        row = self.connection.execute(
            """
            SELECT id, trade_plan_id, trade_plan_revision,
                   progression_boundary, policy_id,
                   eligibility_snapshot_json, attained_environment,
                   attained_at, source, note
            FROM progression_attainment
            WHERE trade_plan_id = ?
              AND trade_plan_revision = ?
              AND progression_boundary = ?
              AND policy_id = ?
            ORDER BY attained_at DESC, id DESC
            LIMIT 1
            """,
            (
                trade_plan_id,
                trade_plan_revision,
                boundary.value,
                policy_id,
            ),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def latest_for_boundary(
        self,
        trade_plan_id: str,
        boundary: ProgressionBoundary | str,
    ) -> ProgressionAttainment | None:
        boundary = ProgressionBoundary(boundary)
        row = self.connection.execute(
            """
            SELECT id, trade_plan_id, trade_plan_revision,
                   progression_boundary, policy_id,
                   eligibility_snapshot_json, attained_environment,
                   attained_at, source, note
            FROM progression_attainment
            WHERE trade_plan_id = ?
              AND progression_boundary = ?
            ORDER BY attained_at DESC, id DESC
            LIMIT 1
            """,
            (trade_plan_id, boundary.value),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def list_for_plan(self, trade_plan_id: str) -> list[ProgressionAttainment]:
        rows = self.connection.execute(
            """
            SELECT id, trade_plan_id, trade_plan_revision,
                   progression_boundary, policy_id,
                   eligibility_snapshot_json, attained_environment,
                   attained_at, source, note
            FROM progression_attainment
            WHERE trade_plan_id = ?
            ORDER BY attained_at DESC, id DESC
            """,
            (trade_plan_id,),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row) -> ProgressionAttainment:
        return ProgressionAttainment(
            id=row[0],
            trade_plan_id=row[1],
            trade_plan_revision=row[2],
            boundary=row[3],
            policy_id=row[4],
            eligibility_snapshot=json.loads(row[5] or "{}"),
            attained_environment=row[6],
            attained_at=row[7],
            source=row[8],
            note=row[9],
        )
