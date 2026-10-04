import sqlite3
from datetime import date

from ict_cockpit.analysis.study_find import StudyFind


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