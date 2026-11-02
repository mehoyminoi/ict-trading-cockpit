"""One atomic, operator-attested reference command over existing run storage."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from uuid import uuid4

from ict_cockpit.analysis.market_time import build_market_time_context
from ict_cockpit.analysis.quarter_theory import apply_time_derived_qt_context
from ict_cockpit.analysis.replay_reference import (
    REPLAY_ADVANCE_KEY, REPLAY_RECEIPT_KEY, aware_instant, validate_progression,
)
from ict_cockpit.analysis.trading_session_run import RunEnvironment, TradingRunStatus
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository, RUN_COLUMNS


def advance_replay_reference(calendar, expected_run, requested, *, operation_id=None, recorded_at=None):
    """Return the committed run. Caller refreshes only after successful commit.

    expected_run is the displayed run snapshot. consume checks that persisted run,
    capture head and master basis still match inside its owned transaction.
    """
    operation_id = operation_id or str(uuid4())
    repository = TradingSessionRunRepository(calendar.connection)
    saved = repository.get_by_id(expected_run.id)
    if saved is None:
        raise ValueError("Replay run is unavailable")
    if saved.environment is not RunEnvironment.REPLAY or saved.status is not TradingRunStatus.ACTIVE:
        raise ValueError("Only an active Replay run can advance its reference")
    requested = aware_instant(requested)
    # Stable request identity makes retry safe, even after subsequent advances.
    for entry in saved.evidence:
        receipt = entry.market_time_context.get(REPLAY_RECEIPT_KEY, {})
        if receipt.get("operation_id") == operation_id:
            if aware_instant(receipt["to"]).astimezone(timezone.utc) != requested.astimezone(timezone.utc):
                raise ValueError("Replay command identity was reused with different input")
            return saved
    expected_values = repository._values_for_run(expected_run)
    if repository._values_for_run(saved) != expected_values:
        raise ValueError("Replay run changed; close and reopen Set Replay reference")
    binding = calendar.run_calendar.get_binding(saved.id)
    original_snapshot = json.loads(binding["run_basis"]["market_context_snapshot_json"])
    if saved.market_context_snapshot != original_snapshot:
        raise ValueError("Original Replay launch context has changed")
    original = original_snapshot.get("reference_market_time")
    if not original:
        raise ValueError("Original Replay launch reference is unavailable")
    current = saved.market_time_context.get("captured_at")
    requested = validate_progression(original, current, requested)
    if requested.astimezone(timezone.utc) == aware_instant(current).astimezone(timezone.utc):
        return saved
    now = recorded_at or datetime.now().astimezone()
    aware_instant(now)
    prepared = calendar.run_calendar.prepare_capture(saved.id, reference=requested)
    if json.loads(prepared.run_context_json) != dict(zip(RUN_COLUMNS, expected_values)):
        raise ValueError("Replay run changed; close and reopen Set Replay reference")
    updated = deepcopy(saved)
    updated.market_time_context = build_market_time_context(requested, source="Manual Replay reference").to_dict()
    updated.market_time_context[REPLAY_ADVANCE_KEY] = {
        "version": 1, "operation_id": operation_id, "previous": current,
        "selected": requested.isoformat(), "recorded_at": now.isoformat(),
        "qualification": "Withheld; interactive requalification not supported",
    }
    updated.qt_context = apply_time_derived_qt_context(updated.qt_context, updated.market_time_context)
    receipt_context = deepcopy(updated.market_time_context)
    receipt_context[REPLAY_RECEIPT_KEY] = {
        "version": 1, "operation_id": operation_id, "from": current,
        "to": requested.isoformat(), "origin": "Operator administrative action",
        "intervening_observation": "Unspecified",
    }
    entry = updated.add_observation(
        f"Replay reference advanced · {current} → {requested.isoformat()}. "
        "Manual administrative action; intervening price action is not assumed observed.",
        market_time_context=receipt_context,
    )
    entry.created_at = now.isoformat(timespec="seconds")
    calendar.run_calendar.consume(prepared, updated, operation_id=operation_id,
        capture_id=str(uuid4()), recorded_at=now)
    return repository.get_by_id(saved.id)
