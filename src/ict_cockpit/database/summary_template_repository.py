from __future__ import annotations

from datetime import datetime
import sqlite3

from ict_cockpit.summary.template_definition import (
    SummaryTemplateDefinition,
    SummaryTemplateKind,
)
from ict_cockpit.summary.templates import DEFAULT_SUMMARY_TEMPLATES


class SummaryTemplateRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def ensure_defaults(self) -> None:
        with self.connection:
            for template in DEFAULT_SUMMARY_TEMPLATES:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO summary_template (
                        template_id, revision, kind, name, body, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        template.template_id,
                        template.revision,
                        template.kind.value,
                        template.name,
                        template.body,
                        template.created_at
                        or datetime.now().astimezone().isoformat(timespec="seconds"),
                    ),
                )
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO summary_template_active (
                        kind, template_id, revision
                    ) VALUES (?, ?, ?)
                    """,
                    (
                        template.kind.value,
                        template.template_id,
                        template.revision,
                    ),
                )

    def get(
        self,
        template_id: str,
        revision: int,
    ) -> SummaryTemplateDefinition | None:
        row = self.connection.execute(
            """
            SELECT template_id, revision, kind, name, body, created_at
            FROM summary_template
            WHERE template_id = ? AND revision = ?
            """,
            (template_id, revision),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def get_active(
        self,
        kind: SummaryTemplateKind | str,
    ) -> SummaryTemplateDefinition | None:
        kind = SummaryTemplateKind(kind)
        row = self.connection.execute(
            """
            SELECT t.template_id, t.revision, t.kind, t.name, t.body, t.created_at
            FROM summary_template_active a
            JOIN summary_template t
              ON t.template_id = a.template_id
             AND t.revision = a.revision
            WHERE a.kind = ?
            """,
            (kind.value,),
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def list_revisions(
        self,
        template_id: str,
    ) -> list[SummaryTemplateDefinition]:
        rows = self.connection.execute(
            """
            SELECT template_id, revision, kind, name, body, created_at
            FROM summary_template
            WHERE template_id = ?
            ORDER BY revision DESC
            """,
            (template_id,),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    def publish_revision(
        self,
        base: SummaryTemplateDefinition,
        *,
        name: str,
        body: str,
    ) -> SummaryTemplateDefinition:
        latest_revision = self.connection.execute(
            """
            SELECT COALESCE(MAX(revision), 0)
            FROM summary_template
            WHERE template_id = ?
            """,
            (base.template_id,),
        ).fetchone()[0]
        published = SummaryTemplateDefinition(
            template_id=base.template_id,
            revision=int(latest_revision) + 1,
            kind=base.kind,
            name=name,
            body=body,
            created_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        )
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO summary_template (
                    template_id, revision, kind, name, body, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    published.template_id,
                    published.revision,
                    published.kind.value,
                    published.name,
                    published.body,
                    published.created_at,
                ),
            )
            self.connection.execute(
                """
                INSERT INTO summary_template_active (
                    kind, template_id, revision
                ) VALUES (?, ?, ?)
                ON CONFLICT(kind) DO UPDATE SET
                    template_id = excluded.template_id,
                    revision = excluded.revision
                """,
                (
                    published.kind.value,
                    published.template_id,
                    published.revision,
                ),
            )
        return published

    @staticmethod
    def _from_row(row) -> SummaryTemplateDefinition:
        return SummaryTemplateDefinition(
            template_id=row[0],
            revision=int(row[1]),
            kind=SummaryTemplateKind(row[2]),
            name=row[3],
            body=row[4],
            created_at=row[5],
        )
