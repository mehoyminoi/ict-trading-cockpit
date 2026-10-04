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
                    tda.weekly_bias.value,
                    tda.daily_bias.value,
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
            weekly_bias=Bias(row[3]),
            daily_bias=Bias(row[4]),
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