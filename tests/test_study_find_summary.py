from datetime import date

from ict_cockpit.analysis.study_find import StudyFind
from ict_cockpit.summary.renderer import SummaryRenderer
from ict_cockpit.summary.study_find_context import StudyFindSummaryContext
from ict_cockpit.summary.templates import STUDY_FIND_SUMMARY_V1


def test_study_find_summary_renders() -> None:
    study_find = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="MNQ",
        session="NYAM",
        pattern_name="London low raid",
        observation="Bullish displacement followed the sweep.",
        available_move_handles=74.5,
        notes="Clean example.",
    )

    context = StudyFindSummaryContext(study_find, 
                                      image_paths=[],
                                      
                )

    rendered = SummaryRenderer().render(
        STUDY_FIND_SUMMARY_V1,
        context.to_template_values(),
    )

    assert "Date: 26-10-04" in rendered
    assert "Asset: MNQ" in rendered
    assert "Session: NYAM" in rendered
    assert "Pattern: London low raid" in rendered
    assert "Available Move: 74.50 handles" in rendered
    assert "Bullish displacement followed the sweep." in rendered
    assert "Clean example." in rendered

def test_study_find_summary_context_formats_images() -> None:
    study_find = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="MNQ",
        session="NYAM",
        pattern_name="London low raid",
        observation="Bullish displacement.",
    )

    context = StudyFindSummaryContext(
        study_find=study_find,
        image_paths=[
            "/tmp/chart-1.png",
            "/tmp/chart-2.jpg",
        ],
    )

    values = context.to_template_values()

    assert values["chart_images"] == (
        "- chart-1.png\n"
        "- chart-2.jpg"
    )

def test_study_find_summary_context_formats_no_images() -> None:
    study_find = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="MNQ",
        session="NYAM",
        pattern_name="London low raid",
        observation="Bullish displacement.",
    )

    context = StudyFindSummaryContext(
        study_find=study_find,
        image_paths=[],
    )

    values = context.to_template_values()

    assert values["chart_images"] == "None"