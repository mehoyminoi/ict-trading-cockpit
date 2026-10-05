import sqlite3

from ict_cockpit.feedback import FeedbackEntry


class FeedbackRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, entry: FeedbackEntry) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO feedback_entry (
                    id,
                    created_at,
                    category,
                    note,
                    context,
                    record_id,
                    app_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.id,
                    entry.created_at,
                    entry.category,
                    entry.note,
                    entry.context,
                    entry.record_id,
                    entry.app_version,
                ),
            )

    def get_recent(self, limit: int = 200) -> list[FeedbackEntry]:
        rows = self.connection.execute(
            """
            SELECT
                id,
                created_at,
                category,
                note,
                context,
                record_id,
                app_version
            FROM feedback_entry
            ORDER BY created_at DESC, rowid DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [
            FeedbackEntry(
                id=row[0],
                created_at=row[1],
                category=row[2],
                note=row[3],
                context=row[4],
                record_id=row[5],
                app_version=row[6],
            )
            for row in rows
        ]

    def render_markdown_digest(self, limit: int = 200) -> str:
        entries = list(reversed(self.get_recent(limit=limit)))

        lines = [
            "# ICT Trading Cockpit — Alpha Feedback Digest",
            "",
            "Use this digest to review friction, bugs, wishes, and queued follow-up items from alpha testing.",
            "",
        ]

        if not entries:
            lines.append("No feedback entries recorded.")
            return "\n".join(lines)

        for entry in entries:
            lines.extend(
                [
                    f"## {entry.created_at} — {entry.category}",
                    f"- Context: {entry.context or 'Unknown'}",
                    f"- Record ID: {entry.record_id or 'None'}",
                    f"- App version: {entry.app_version or 'Unknown'}",
                    f"- Note: {entry.note}",
                    "",
                ]
            )

        return "\n".join(lines).rstrip() + "\n"
