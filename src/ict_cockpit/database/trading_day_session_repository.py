import json
import sqlite3

from ict_cockpit.analysis.trading_day_session import (
    TradingDaySession,
    TradingDayStatus,
    TradingDayTransition,
    TransitionOutcome,
)


class TradingDaySessionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, session: TradingDaySession) -> None:
        transitions_json = json.dumps(
            [
                {
                    "from_mode_id": transition.from_mode_id,
                    "to_mode_id": transition.to_mode_id,
                    "outcome": transition.outcome.value,
                    "reason": transition.reason,
                    "override_incomplete": transition.override_incomplete,
                    "created_at": transition.created_at,
                }
                for transition in session.transitions
            ]
        )

        with self.connection:
            self.connection.execute(
                """
                INSERT INTO trading_day_session (
                    id, blueprint_revision, mode_ids_json, current_mode_id,
                    completed_mode_ids_json, updated_at, status, day_outcome,
                    transitions_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    blueprint_revision = excluded.blueprint_revision,
                    mode_ids_json = excluded.mode_ids_json,
                    current_mode_id = excluded.current_mode_id,
                    completed_mode_ids_json = excluded.completed_mode_ids_json,
                    updated_at = excluded.updated_at,
                    status = excluded.status,
                    day_outcome = excluded.day_outcome,
                    transitions_json = excluded.transitions_json
                """,
                (
                    session.id,
                    session.blueprint_revision,
                    json.dumps(session.mode_ids),
                    session.current_mode_id,
                    json.dumps(session.completed_mode_ids),
                    session.updated_at,
                    session.status.value,
                    session.day_outcome,
                    transitions_json,
                ),
            )

    def get_latest(self) -> TradingDaySession | None:
        row = self.connection.execute(
            """
            SELECT id, blueprint_revision, mode_ids_json, current_mode_id,
                   completed_mode_ids_json, updated_at, status, day_outcome,
                   transitions_json
            FROM trading_day_session
            ORDER BY updated_at DESC, rowid DESC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None

        transitions = [
            TradingDayTransition(
                from_mode_id=item["from_mode_id"],
                to_mode_id=item.get("to_mode_id"),
                outcome=TransitionOutcome(item["outcome"]),
                reason=item.get("reason", ""),
                override_incomplete=bool(item.get("override_incomplete", False)),
                created_at=item["created_at"],
            )
            for item in json.loads(row[8])
        ]

        return TradingDaySession(
            id=row[0],
            blueprint_revision=row[1],
            mode_ids=list(json.loads(row[2])),
            current_mode_id=row[3],
            completed_mode_ids=list(json.loads(row[4])),
            updated_at=row[5],
            status=TradingDayStatus(row[6]),
            day_outcome=row[7],
            transitions=transitions,
        )

    def delete(self, session_id: str) -> None:
        with self.connection:
            self.connection.execute(
                "DELETE FROM trading_day_session WHERE id = ?",
                (session_id,),
            )
