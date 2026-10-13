"""Resolve a run's reviewed date from preserved provenance, never a live clock."""
from dataclasses import dataclass
from datetime import date

from ict_cockpit.analysis.amdx import timestamp
from ict_cockpit.analysis.market_time import futures_trading_day_for


@dataclass(frozen=True)
class ReviewDate:
    day_label: str
    source: str
    detail: str
    error: str = ""


def resolve_review_date(run, container_label: str) -> ReviewDate:
    if run is None:
        return ReviewDate("", "", "", "No trading run is loaded")
    snapshot = run.market_context_snapshot
    reference = snapshot.get("reference_market_time")
    if reference is not None and reference != "":
        try:
            if not isinstance(reference, str) or not reference.strip():
                raise ValueError("reference must be a timezone-aware timestamp")
            label = futures_trading_day_for(timestamp(reference)).isoformat()
        except (ValueError, TypeError, AttributeError):
            return ReviewDate("", "Run-start reference", "",
                              "Saved run-start reference is invalid; the containing day is not substituted")
        detail = "Reviewed date comes from this run's saved starting reference; later clock changes do not replace it."
        if container_label and container_label != label:
            detail += f" Containing Trading Day is labeled {container_label}; this run's reference identifies {label}."
        return ReviewDate(label, "Run-start reference", detail)
    try:
        label = date.fromisoformat(container_label).isoformat()
    except (ValueError, TypeError):
        return ReviewDate("", "Legacy Trading Day", "",
                          "No saved run-start reference or valid containing Trading Day date is available")
    return ReviewDate(label, "Legacy Trading Day",
                      "No run-start reference was retained. Reviewed date uses the saved containing Trading Day; "
                      "the current clock and interpretation claims are not used as substitutes.")
