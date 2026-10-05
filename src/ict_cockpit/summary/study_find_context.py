from dataclasses import dataclass
from pathlib import Path

from ict_cockpit.analysis.study_find import StudyFind


@dataclass
class StudyFindSummaryContext:
    study_find: StudyFind
    image_paths: list[str]

    def to_template_values(self) -> dict[str, object]:
        if self.study_find.available_move_handles is None:
            available_move = ""
        else:
            available_move = (
                f"{self.study_find.available_move_handles:.2f} handles"
            )

        if self.image_paths:
            chart_images = "\n".join(
                f"- {Path(image_path).name}"
                for image_path in self.image_paths
            )
        else:
            chart_images = "None"

        return {
            "date": self.study_find.observation_date.strftime("%y-%m-%d"),
            "asset": self.study_find.instrument,
            "session": self.study_find.session,
            "pattern": self.study_find.pattern_name,
            "available_move": available_move,
            "observation": self.study_find.observation,
            "notes": self.study_find.notes,
            "chart_images": chart_images,
        }