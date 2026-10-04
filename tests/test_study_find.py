from datetime import date

import pytest

from ict_cockpit.analysis.study_find import StudyFind


def test_create_study_find() -> None:
    find = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="mnq",
        session="NYAM",
        pattern_name="London low raid",
        observation="Bullish displacement followed the liquidity sweep.",
        available_move_handles=74.5,
        notes="Clean example.",
    )

    assert find.instrument == "MNQ"
    assert find.session == "NYAM"
    assert find.pattern_name == "London low raid"
    assert find.available_move_handles == 74.5


def test_study_find_has_unique_ids() -> None:
    first = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="MNQ",
        session="NYAM",
        pattern_name="Pattern A",
        observation="First observation.",
    )

    second = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="MNQ",
        session="NYAM",
        pattern_name="Pattern A",
        observation="Second observation.",
    )

    assert first.id != second.id


def test_study_find_normalizes_text() -> None:
    find = StudyFind(
        observation_date=date(2026, 10, 4),
        instrument="  mnq  ",
        session="  NYAM  ",
        pattern_name="  London low raid  ",
        observation="  Bullish displacement.  ",
        notes="  Clean example.  ",
    )

    assert find.instrument == "MNQ"
    assert find.session == "NYAM"
    assert find.pattern_name == "London low raid"
    assert find.observation == "Bullish displacement."
    assert find.notes == "Clean example."


def test_study_find_rejects_empty_required_fields() -> None:
    with pytest.raises(ValueError):
        StudyFind(
            observation_date=date(2026, 10, 4),
            instrument="MNQ",
            session="",
            pattern_name="Pattern A",
            observation="Observation.",
        )