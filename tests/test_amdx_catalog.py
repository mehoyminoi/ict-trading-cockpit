from dataclasses import replace
from datetime import datetime

import pytest

from ict_cockpit.analysis.amdx_catalog import CaptureBasis, Catalog
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE


def test_catalog_defaults_and_tagged_owner_are_not_a_trading_run():
    catalog = Catalog("study-1", "Historical quarters")
    assert catalog.instrument == "MNQ" and catalog.purpose == "Backtest"
    assert catalog.owner_id == "catalog:study-1"


@pytest.mark.parametrize("change", [dict(id=""), dict(title=""), dict(instrument=""),
    dict(instrument="mnq"), dict(instrument=" MNQ"), dict(purpose="Live"), dict(definition_ref=None)])
def test_catalog_rejects_ambiguous_identity(change):
    with pytest.raises(ValueError):
        replace(Catalog("study-1", "Historical quarters"), **change)


def test_unknown_basis_stays_unspecified_and_fold_instants_are_retained():
    assert CaptureBasis().information_available_at is None
    time = datetime(2026, 11, 1, 1, 30, tzinfo=MARKET_TIMEZONE, fold=1)
    basis = CaptureBasis("ForwardEntry", time)
    assert basis.information_available_at.isoformat() == "2026-11-01T01:30:00-05:00"
    with pytest.raises(ValueError, match="availability"):
        basis.validate_recording(time.replace(fold=0))


@pytest.mark.parametrize("kind", ["", "Expected", "Live", None])
def test_capture_kind_is_explicit(kind):
    with pytest.raises(ValueError):
        CaptureBasis(kind)
