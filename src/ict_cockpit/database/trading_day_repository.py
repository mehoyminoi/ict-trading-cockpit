import sqlite3

from ict_cockpit.analysis.trading_day import TradingDay, TradingDayLifecycleStatus


class TradingDayRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, trading_day: TradingDay) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO trading_day (
                    id, futures_day_label, status, active_session_run_id,
                    started_at, completed_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    futures_day_label = excluded.futures_day_label,
                    status = excluded.status,
                    active_session_run_id = excluded.active_session_run_id,
                    started_at = excluded.started_at,
                    completed_at = excluded.completed_at,
                    updated_at = excluded.updated_at
                """,
                (
                    trading_day.id,
                    trading_day.futures_day_label,
                    trading_day.status.value,
                    trading_day.active_session_run_id,
                    trading_day.started_at,
                    trading_day.completed_at,
                    trading_day.updated_at,
                ),
            )

    def get_latest(self) -> TradingDay | None:
        row = self.connection.execute(
            """
            SELECT id, futures_day_label, status, active_session_run_id,
                   started_at, completed_at, updated_at
            FROM trading_day
            ORDER BY updated_at DESC, rowid DESC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None
        return TradingDay(
            id=row[0],
            futures_day_label=row[1],
            status=TradingDayLifecycleStatus(row[2]),
            active_session_run_id=row[3],
            started_at=row[4],
            completed_at=row[5],
            updated_at=row[6],
        )

    def get_latest_active(self) -> TradingDay | None:
        row = self.connection.execute(
            """
            SELECT id, futures_day_label, status, active_session_run_id,
                   started_at, completed_at, updated_at
            FROM trading_day
            WHERE status = ?
            ORDER BY updated_at DESC, rowid DESC
            LIMIT 1
            """,
            (TradingDayLifecycleStatus.ACTIVE.value,),
        ).fetchone()
        if row is None:
            return None
        return TradingDay(
            id=row[0],
            futures_day_label=row[1],
            status=TradingDayLifecycleStatus(row[2]),
            active_session_run_id=row[3],
            started_at=row[4],
            completed_at=row[5],
            updated_at=row[6],
        )
