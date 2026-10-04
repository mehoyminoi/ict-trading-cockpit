from dataclasses import dataclass

from ict_cockpit.analysis.study_find import StudyFind


@dataclass
class StudyFindSummaryContext:
    study_find: StudyFind

    def to_template_values(self) -> dict[str, object]:
        available_move = ""

        if self.study_find.available_move_handles is not None:
            available_move = (
                f"{self.study_find.available_move_handles:.2f} handles"
            )

        return {
            "date": self.study_find.observation_date.strftime("%y-%m-%d"),
            "asset": self.study_find.instrument,
            "session": self.study_find.session,
            "pattern": self.study_find.pattern_name,
            "available_move": available_move,
            "observation": self.study_find.observation,
            "notes": self.study_find.notes,
        }