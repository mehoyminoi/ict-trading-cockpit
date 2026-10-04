from datetime import date

import pytest

from ict_cockpit.analysis.tda import Bias, TDARecord


def test_create_tda_record() -> None:
    tda = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.BULLISH,
        primary_draw="Previous Week High",
    )

    assert tda.analysis_date == date(2026, 10, 3)
    assert tda.instrument == "MNQ"
    assert tda.weekly_bias == Bias.BULLISH
    assert tda.daily_bias == Bias.BULLISH
    assert tda.primary_draw == "Previous Week High"
    assert tda.secondary_draw == ""
    assert tda.narrative == ""
    assert tda.id


def test_tda_records_receive_unique_ids() -> None:
    first = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.BULLISH,
        primary_draw="Previous Week High",
    )

    second = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="MNQ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.BULLISH,
        primary_draw="Previous Week High",
    )

    assert first.id
    assert second.id
    assert first.id != second.id


def test_tda_rejects_empty_instrument() -> None:
    with pytest.raises(ValueError):
        TDARecord(
            analysis_date=date(2026, 10, 3),
            instrument="",
            weekly_bias=Bias.BULLISH,
            daily_bias=Bias.BULLISH,
            primary_draw="Previous Week High",
        )


def test_tda_rejects_invalid_bias() -> None:
    with pytest.raises(ValueError):
        TDARecord(
            analysis_date=date(2026, 10, 3),
            instrument="MNQ",
            weekly_bias="potato",
            daily_bias=Bias.BULLISH,
            primary_draw="Previous Week High",
        )

def test_tda_rejects_empty_primary_draw() -> None:
    with pytest.raises(ValueError):
        TDARecord(
            analysis_date=date(2026, 10, 3),
            instrument="MNQ",
            weekly_bias=Bias.BULLISH,
            daily_bias=Bias.BULLISH,
            primary_draw="",
        )

def test_tda_normalizes_text_fields() -> None:
    tda = TDARecord(
        analysis_date=date(2026, 10, 3),
        instrument="  mnq  ",
        weekly_bias=Bias.BULLISH,
        daily_bias=Bias.NEUTRAL,
        primary_draw="  Previous Week High  ",
        secondary_draw="  Previous Day High  ",
        narrative="  Expecting continuation after London liquidity sweep.  ",
    )

    assert tda.instrument == "MNQ"
    assert tda.primary_draw == "Previous Week High"
    assert tda.secondary_draw == "Previous Day High"
    assert tda.narrative == "Expecting continuation after London liquidity sweep."

def test_tda_rejects_whitespace_only_instrument() -> None:
    with pytest.raises(ValueError):
        TDARecord(
            analysis_date=date(2026, 10, 3),
            instrument="   ",
            weekly_bias=Bias.BULLISH,
            daily_bias=Bias.BULLISH,
            primary_draw="Previous Week High",
        )