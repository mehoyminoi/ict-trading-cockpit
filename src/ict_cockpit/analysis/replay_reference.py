"""Manual Replay reference validation; no market observation or rule inference."""
from datetime import datetime, timezone

from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, futures_trading_day_for

REPLAY_ADVANCE_KEY = "manual_replay_reference_v1"
REPLAY_RECEIPT_KEY = "manual_replay_reference_receipt_v1"
FRESHNESS_MESSAGE = "Retained assessment · not revalidated at this Replay reference; authorization withheld"


def aware_instant(value):
    moment = datetime.fromisoformat(value) if isinstance(value, str) else value
    if not isinstance(moment, datetime) or moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("Replay reference requires an explicit timezone/offset")
    # Reject imaginary ZoneInfo wall times; fixed-offset inputs denote real instants.
    local = moment.astimezone(timezone.utc).astimezone(moment.tzinfo)
    if local.replace(tzinfo=None) != moment.replace(tzinfo=None):
        raise ValueError("This local time does not exist")
    return moment.astimezone(MARKET_TIMEZONE)


def resolve_new_york(value: str, occurrence: int | None = None):
    """Resolve a local editor value; repeated hours require explicit occurrence."""
    try:
        wall = datetime.fromisoformat(value.strip())
    except ValueError as error:
        raise ValueError("Use YYYY-MM-DD HH:MM[:SS] in New York") from error
    if wall.tzinfo is not None:
        raise ValueError("Enter New York local time without an offset; select occurrence if needed")
    options = []
    for fold in (0, 1):
        candidate = wall.replace(tzinfo=MARKET_TIMEZONE, fold=fold)
        restored = candidate.astimezone(timezone.utc).astimezone(MARKET_TIMEZONE)
        if restored.replace(tzinfo=None) == wall and restored.fold == fold:
            options.append(candidate)
    if not options:
        raise ValueError("This New York time does not exist (daylight-saving transition)")
    if len(options) == 2:
        if occurrence not in (0, 1):
            raise ValueError("Repeated New York time: choose first or second occurrence")
        return options[occurrence]
    return options[0]


def validate_progression(original, current, requested):
    original, current, requested = map(aware_instant, (original, current, requested))
    day = futures_trading_day_for(original)
    if futures_trading_day_for(current) != day:
        raise ValueError("Saved current reference disagrees with original Trading Day")
    if current.astimezone(timezone.utc) < original.astimezone(timezone.utc):
        raise ValueError("Saved current reference precedes the original launch")
    if futures_trading_day_for(requested) != day:
        raise ValueError("Another Trading Day requires the existing new-day/run workflow (18:00 NY boundary)")
    if requested.astimezone(timezone.utc) < current.astimezone(timezone.utc):
        raise ValueError("Replay reference cannot move backward in this run")
    return requested
