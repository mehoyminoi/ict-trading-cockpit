import sqlite3
from datetime import date

from ict_cockpit.analysis.tda import Bias, TDARecord, TDAStatus


class TDARepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, tda: TDARecord) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO tda_analysis (
                    id,
                    analysis_date,
                    instrument,
                    weekly_bias,
                    daily_bias,
                    primary_draw,
                    secondary_draw,
                    narrative,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tda.id,
                    tda.analysis_date.isoformat(),
                    tda.instrument,
                    tda.weekly_bias.value if tda.weekly_bias is not None else None,
                    tda.daily_bias.value if tda.daily_bias is not None else None,
                    tda.primary_draw,
                    tda.secondary_draw,
                    tda.narrative,
                    tda.status.value,
                ),
            )

    def get_by_id(self, tda_id: str) -> TDARecord | None:
        row = self.connection.execute(
            """
            SELECT
                id,
                analysis_date,
                instrument,
                weekly_bias,
                daily_bias,
                primary_draw,
                secondary_draw,
                narrative,
                status
            FROM tda_analysis
            WHERE id = ?
            """,
            (tda_id,),
        ).fetchone()

        if row is None:
            return None

        return TDARecord(
            id=row[0],
            analysis_date=date.fromisoformat(row[1]),
            instrument=row[2],
            weekly_bias=Bias(row[3]) if row[3] is not None else None,
            daily_bias=Bias(row[4]) if row[4] is not None else None,
            primary_draw=row[5],
            secondary_draw=row[6],
            narrative=row[7],
            status=TDAStatus(row[8]),
        )

    def update(self, tda: TDARecord) -> None:
        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE tda_analysis
                SET
                    analysis_date = ?,
                    instrument = ?,
                    weekly_bias = ?,
                    daily_bias = ?,
                    primary_draw = ?,
                    secondary_draw = ?,
                    narrative = ?,
                    status = ?
                WHERE id = ?
                """,
                (
                    tda.analysis_date.isoformat(),
                    tda.instrument,
                    tda.weekly_bias.value,
                    tda.daily_bias.value,
                    tda.primary_draw,
                    tda.secondary_draw,
                    tda.narrative,
                    tda.status.value,
                    tda.id
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(f"TDA record not found: {tda.id}")

    def save_draft(self, tda: TDARecord) -> None:
        if tda.status != TDAStatus.DRAFT:
            raise ValueError("save_draft only accepts draft TDA records")

        with self.connection:
            existing = self.connection.execute(
                """
                SELECT status
                FROM tda_analysis
                WHERE id = ?
                """,
                (tda.id,),
            ).fetchone()

            if existing is not None and existing[0] != TDAStatus.DRAFT.value:
                raise ValueError(
                    f"Cannot overwrite finalized TDA record: {tda.id}"
                )

            self.connection.execute(
                """
                INSERT INTO tda_analysis (
                    id,
                    analysis_date,
                    instrument,
                    weekly_bias,
                    daily_bias,
                    primary_draw,
                    secondary_draw,
                    narrative,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    analysis_date = excluded.analysis_date,
                    instrument = excluded.instrument,
                    weekly_bias = excluded.weekly_bias,
                    daily_bias = excluded.daily_bias,
                    primary_draw = excluded.primary_draw,
                    secondary_draw = excluded.secondary_draw,
                    narrative = excluded.narrative,
                    status = excluded.status
                """,
                (
                    tda.id,
                    tda.analysis_date.isoformat(),
                    tda.instrument,
                    tda.weekly_bias.value if tda.weekly_bias is not None else None,
                    tda.daily_bias.value if tda.daily_bias is not None else None,
                    tda.primary_draw,
                    tda.secondary_draw,
                    tda.narrative,
                    tda.status.value,
                ),
            )