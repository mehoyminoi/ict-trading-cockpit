"""Date provenance must survive rollover without selecting claim/clock defaults."""
from types import SimpleNamespace

import pytest

from ict_cockpit.analysis.amdx_review_date import resolve_review_date


def run(reference=None):
    return SimpleNamespace(market_context_snapshot={"reference_market_time": reference},
                           market_time_context={"captured_at": "2030-01-01T10:00:00-05:00"})


@pytest.mark.parametrize("reference,expected", [
    ("2026-10-09T09:15:00-04:00", "2026-10-09"),
    ("2026-10-08T18:00:00-04:00", "2026-10-09"),
    ("2026-10-09T01:00:00Z", "2026-10-09"),
])
def test_run_start_reference_wins_over_old_container_and_current_clock(reference, expected):
    result = resolve_review_date(run(reference), "2026-10-08")
    assert result.day_label == expected and not result.error
    assert result.source == "Run-start reference"
    assert "Containing Trading Day" in result.detail


@pytest.mark.parametrize("reference", ["not-a-date", "2026-10-09T09:15:00", 0, False, [], " "])
def test_malformed_present_reference_disables_capture_without_container_substitution(reference):
    result = resolve_review_date(run(reference), "2026-10-08")
    assert not result.day_label and result.error


@pytest.mark.parametrize("reference", [None, ""])
def test_legacy_missing_reference_uses_saved_day_with_explicit_provenance(reference):
    result = resolve_review_date(run(reference), "2026-10-08")
    assert result.day_label == "2026-10-08" and not result.error
    assert result.source == "Legacy Trading Day"
    assert "current clock" in result.detail


@pytest.mark.parametrize("label", ["", "invalid", None])
def test_no_original_reference_and_no_valid_day_disables_capture(label):
    result = resolve_review_date(run(), label)
    assert not result.day_label and result.error


def test_valid_original_reference_needs_no_container_date():
    assert resolve_review_date(run("2026-10-09T09:15:00-04:00"), "").day_label == "2026-10-09"
