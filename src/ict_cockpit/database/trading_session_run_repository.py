import sqlite3

from ict_cockpit.analysis.trading_session_run import (
    TradingSessionRun,
    TradingSessionRunStatus,
)


class TradingSessionRunRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, session_run: TradingSessionRun) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO trading_session_run (
                    id, trading_day_id, session_name, process_session_id,
                    tda_station_session_id, status, outcome, started_at,
                    concluded_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    trading_day_id = excluded.trading_day_id,
                    session_name = excluded.session_name,
                    process_session_id = excluded.process_session_id,
                    tda_station_session_id = excluded.tda_station_session_id,
                    status = excluded.status,
                    outcome = excluded.outcome,
                    started_at = excluded.started_at,
                    concluded_at = excluded.concluded_at,
                    updated_at = excluded.updated_at
                """,
                (
                    session_run.id,
                    session_run.trading_day_id,
                    session_run.session_name,
                    session_run.process_session_id,
                    session_run.tda_station_session_id,
                    session_run.status.value,
                    session_run.outcome,
                    session_run.started_at,
                    session_run.concluded_at,
                    session_run.updated_at,
                ),
            )

    def get_by_id(self, session_run_id: str) -> TradingSessionRun | None:
        row = self.connection.execute(
            """
            SELECT id, trading_day_id, session_name, process_session_id,
                   tda_station_session_id, status, outcome, started_at,
                   concluded_at, updated_at
            FROM trading_session_run
            WHERE id = ?
            """,
            (session_run_id,),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def get_for_day(self, trading_day_id: str) -> list[TradingSessionRun]:
        rows = self.connection.execute(
            """
            SELECT id, trading_day_id, session_name, process_session_id,
                   tda_station_session_id, status, outcome, started_at,
                   concluded_at, updated_at
            FROM trading_session_run
            WHERE trading_day_id = ?
            ORDER BY started_at, rowid
            """,
            (trading_day_id,),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row) -> TradingSessionRun:
        return TradingSessionRun(
            id=row[0],
            trading_day_id=row[1],
            session_name=row[2],
            process_session_id=row[3],
            tda_station_session_id=row[4],
            status=TradingSessionRunStatus(row[5]),
            outcome=row[6],
            started_at=row[7],
            concluded_at=row[8],
            updated_at=row[9],
        )
