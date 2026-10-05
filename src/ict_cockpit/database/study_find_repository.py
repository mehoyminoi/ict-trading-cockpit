import json
import sqlite3
from datetime import date

from ict_cockpit.analysis.study_find import StudyFind, StudyFindDraft


class StudyFindRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, study_find: StudyFind) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO study_find (
                    id,
                    observation_date,
                    instrument,
                    session,
                    pattern_name,
                    observation,
                    available_move_handles,
                    notes,
                    image_path
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    study_find.id,
                    study_find.observation_date.isoformat(),
                    study_find.instrument,
                    study_find.session,
                    study_find.pattern_name,
                    study_find.observation,
                    study_find.available_move_handles,
                    study_find.notes,
                    study_find.image_path,
                ),
            )

    def get_by_id(self, study_find_id: str) -> StudyFind | None:
        row = self.connection.execute(
            """
            SELECT
                id,
                observation_date,
                instrument,
                session,
                pattern_name,
                observation,
                available_move_handles,
                notes,
                image_path
            FROM study_find
            WHERE id = ?
            """,
            (study_find_id,),
        ).fetchone()

        if row is None:
            return None

        return StudyFind(
            id=row[0],
            observation_date=date.fromisoformat(row[1]),
            instrument=row[2],
            session=row[3],
            pattern_name=row[4],
            observation=row[5],
            available_move_handles=row[6],
            notes=row[7],
            image_path=row[8],
        )

    def save_draft(self, draft: StudyFindDraft) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO study_find_draft (
                    id,
                    observation_date,
                    instrument,
                    session,
                    pattern_name,
                    observation,
                    available_move_handles,
                    notes,
                    image_paths,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    observation_date = excluded.observation_date,
                    instrument = excluded.instrument,
                    session = excluded.session,
                    pattern_name = excluded.pattern_name,
                    observation = excluded.observation,
                    available_move_handles = excluded.available_move_handles,
                    notes = excluded.notes,
                    image_paths = excluded.image_paths,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    draft.id,
                    draft.observation_date.isoformat(),
                    draft.instrument,
                    draft.session,
                    draft.pattern_name,
                    draft.observation,
                    draft.available_move_handles,
                    draft.notes,
                    json.dumps(draft.image_paths),
                ),
            )

    def get_latest_draft(self) -> StudyFindDraft | None:
        row = self.connection.execute(
            """
            SELECT
                id,
                observation_date,
                instrument,
                session,
                pattern_name,
                observation,
                available_move_handles,
                notes,
                image_paths
            FROM study_find_draft
            ORDER BY updated_at DESC, rowid DESC
            LIMIT 1
            """
        ).fetchone()

        if row is None:
            return None

        return StudyFindDraft(
            id=row[0],
            observation_date=date.fromisoformat(row[1]),
            instrument=row[2],
            session=row[3],
            pattern_name=row[4],
            observation=row[5],
            available_move_handles=row[6],
            notes=row[7],
            image_paths=json.loads(row[8]),
        )

    def delete_draft(self, study_find_id: str) -> None:
        with self.connection:
            self.connection.execute(
                "DELETE FROM study_find_draft WHERE id = ?",
                (study_find_id,),
            )

    def add_image(
        self,
        study_find_id: str,
        image_path: str,
    ) -> None:
        with self.connection:
            next_order = self.connection.execute(
                """
                SELECT COALESCE(MAX(image_order), 0) + 1
                FROM study_find_image
                WHERE study_find_id = ?
                """,
                (study_find_id,),
            ).fetchone()[0]

            self.connection.execute(
                """
                INSERT INTO study_find_image (
                    study_find_id,
                    image_path,
                    image_order
                )
                VALUES (?, ?, ?)
                """,
                (
                    study_find_id,
                    image_path,
                    next_order,
                ),
            )

    def get_images(
        self,
        study_find_id: str,
    ) -> list[str]:
        rows = self.connection.execute(
            """
            SELECT image_path
            FROM study_find_image
            WHERE study_find_id = ?
            ORDER BY image_order
            """,
            (study_find_id,),
        ).fetchall()

        return [row[0] for row in rows]

    def get_recent(
        self,
        limit: int = 50,
    ) -> list[StudyFind]:
        rows = self.connection.execute(
            """
            SELECT
                id,
                observation_date,
                instrument,
                session,
                pattern_name,
                observation,
                available_move_handles,
                notes,
                image_path
            FROM study_find
            ORDER BY observation_date DESC, rowid DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [
            StudyFind(
                id=row[0],
                observation_date=date.fromisoformat(row[1]),
                instrument=row[2],
                session=row[3],
                pattern_name=row[4],
                observation=row[5],
                available_move_handles=row[6],
                notes=row[7],
                image_path=row[8],
            )
            for row in rows
        ]
