import json
import sqlite3
from datetime import datetime

from ict_cockpit.analysis.trade_record import TradeRecord, TradeRecordDraft


class TradeRecordRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, trade: TradeRecord) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO trade_record (
                    id, instrument, trade_source, account_context, trade_number,
                    model, direction, entry_tf, entry_time, close_time,
                    entry_price, close_price, stop_price, tick_size,
                    cycle_16y, quadrennial, quarter, month, week, day,
                    session, macro_90m, summary
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    trade.id, trade.instrument, trade.trade_source,
                    trade.account_context, trade.trade_number, trade.model,
                    trade.direction, trade.entry_tf,
                    trade.entry_time.isoformat(), trade.close_time.isoformat(),
                    trade.entry_price, trade.close_price, trade.stop_price,
                    trade.tick_size, trade.cycle_16y, trade.quadrennial,
                    trade.quarter, trade.month, trade.week, trade.day,
                    trade.session, trade.macro_90m, trade.summary,
                ),
            )

    def get_by_id(self, trade_id: str) -> TradeRecord | None:
        row = self.connection.execute(
            "SELECT * FROM trade_record WHERE id = ?",
            (trade_id,),
        ).fetchone()
        if row is None:
            return None
        return TradeRecord(
            id=row[0], instrument=row[1], trade_source=row[2],
            account_context=row[3], trade_number=row[4], model=row[5],
            direction=row[6], entry_tf=row[7],
            entry_time=datetime.fromisoformat(row[8]),
            close_time=datetime.fromisoformat(row[9]),
            entry_price=row[10], close_price=row[11], stop_price=row[12],
            tick_size=row[13], cycle_16y=row[14], quadrennial=row[15],
            quarter=row[16], month=row[17], week=row[18], day=row[19],
            session=row[20], macro_90m=row[21], summary=row[22],
        )

    def add_image(self, trade_id: str, image_path: str) -> None:
        with self.connection:
            next_order = self.connection.execute(
                """
                SELECT COALESCE(MAX(image_order), 0) + 1
                FROM trade_record_image
                WHERE trade_record_id = ?
                """,
                (trade_id,),
            ).fetchone()[0]
            self.connection.execute(
                """
                INSERT INTO trade_record_image (
                    trade_record_id, image_path, image_order
                ) VALUES (?, ?, ?)
                """,
                (trade_id, image_path, next_order),
            )

    def get_images(self, trade_id: str) -> list[str]:
        rows = self.connection.execute(
            """
            SELECT image_path FROM trade_record_image
            WHERE trade_record_id = ? ORDER BY image_order
            """,
            (trade_id,),
        ).fetchall()
        return [row[0] for row in rows]

    def save_draft(self, draft: TradeRecordDraft) -> None:
        payload = {
            "instrument": draft.instrument,
            "trade_source": draft.trade_source,
            "account_context": draft.account_context,
            "trade_number": draft.trade_number,
            "model": draft.model,
            "direction": draft.direction,
            "entry_tf": draft.entry_tf,
            "entry_time": draft.entry_time.isoformat() if draft.entry_time else None,
            "close_time": draft.close_time.isoformat() if draft.close_time else None,
            "entry_price": draft.entry_price,
            "close_price": draft.close_price,
            "stop_price": draft.stop_price,
            "tick_size": draft.tick_size,
            "cycle_16y": draft.cycle_16y,
            "quadrennial": draft.quadrennial,
            "quarter": draft.quarter,
            "month": draft.month,
            "week": draft.week,
            "day": draft.day,
            "session": draft.session,
            "macro_90m": draft.macro_90m,
            "summary": draft.summary,
            "image_paths": draft.image_paths,
        }
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO trade_record_draft (id, payload, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (draft.id, json.dumps(payload)),
            )

    def get_latest_draft(self) -> TradeRecordDraft | None:
        row = self.connection.execute(
            """
            SELECT id, payload FROM trade_record_draft
            ORDER BY updated_at DESC, rowid DESC LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None
        payload = json.loads(row[1])
        return TradeRecordDraft(
            id=row[0],
            instrument=payload["instrument"],
            trade_source=payload["trade_source"],
            account_context=payload["account_context"],
            trade_number=payload["trade_number"],
            model=payload["model"],
            direction=payload["direction"],
            entry_tf=payload["entry_tf"],
            entry_time=datetime.fromisoformat(payload["entry_time"]) if payload["entry_time"] else None,
            close_time=datetime.fromisoformat(payload["close_time"]) if payload["close_time"] else None,
            entry_price=payload["entry_price"], close_price=payload["close_price"],
            stop_price=payload["stop_price"], tick_size=payload["tick_size"],
            cycle_16y=payload["cycle_16y"], quadrennial=payload["quadrennial"],
            quarter=payload["quarter"], month=payload["month"], week=payload["week"],
            day=payload["day"], session=payload["session"], macro_90m=payload["macro_90m"],
            summary=payload["summary"], image_paths=payload["image_paths"],
        )

    def delete_draft(self, draft_id: str) -> None:
        with self.connection:
            self.connection.execute(
                "DELETE FROM trade_record_draft WHERE id = ?",
                (draft_id,),
            )
