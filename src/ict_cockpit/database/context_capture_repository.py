import json
import sqlite3

from ict_cockpit.analysis.forex_factory_import import ImportedContextCapture


class ContextCaptureRepository:
    """Insert-only local source history. Selection does not rewrite a capture."""
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, capture: ImportedContextCapture):
        payload = json.dumps(capture.to_dict(), ensure_ascii=False, sort_keys=True)
        with self.connection:
            existing = self.connection.execute(
                "SELECT payload_json FROM context_source_capture WHERE id = ?", (capture.id,)
            ).fetchone()
            if existing:
                if existing[0] != payload:
                    raise ValueError("A stored source capture is immutable")
                return
            self.connection.execute(
                "INSERT INTO context_source_capture (id, imported_at, payload_json) VALUES (?, ?, ?)",
                (capture.id, capture.provenance.imported_at, payload),
            )

    def get_by_id(self, capture_id):
        row = self.connection.execute(
            "SELECT payload_json FROM context_source_capture WHERE id = ?", (capture_id,)
        ).fetchone()
        return ImportedContextCapture.from_dict(json.loads(row[0])) if row else None

    def list_all(self):
        rows = self.connection.execute(
            "SELECT payload_json FROM context_source_capture ORDER BY imported_at DESC, id"
        ).fetchall()
        return [ImportedContextCapture.from_dict(json.loads(row[0])) for row in rows]
