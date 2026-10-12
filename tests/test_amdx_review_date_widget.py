"""Native launch, restored provenance and clock/gesture boundary regressions."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from ict_cockpit.analysis.amdx import Role
from ict_cockpit.analysis.market_context_event import capture_market_context_snapshot
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, build_market_time_context
from ict_cockpit.analysis.trading_session_run import TradingRunStatus
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow
from test_amdx_context_widget import cockpit, close, history, reference, refresh, widget
from test_amdx_observed_entry import review


def conclude(shell):
    assert shell.runtime.apply_transition("tda-stand-down")
    assert shell.runtime.apply_transition("complete-day")
    assert shell.active_trading_run is None


def restore_old_mismatched_run(window, shell):
    """Recreate a persisted combination allowed by the earlier launch code."""
    first = shell.active_trading_run
    conclude(shell)
    shell.runtime.start_new()
    window.save_trading_day_session(shell.runtime.session)
    window.save_tda_station_session(shell.runtime.tda_station_runner_widget.session)
    context = build_market_time_context(reference(day=9), source="Historical Reference").to_dict()
    snapshot = capture_market_context_snapshot(
        provider=None, market_time_context=context, market_timezone=MARKET_TIMEZONE,
        captured_at=reference(day=9).isoformat(),
    ).to_dict()
    run = replace(first, id=str(uuid4()), status=TradingRunStatus.ACTIVE, concluded_at="",
                  process_session_id=shell.runtime.session.id,
                  tda_station_session_id=shell.runtime.tda_station_runner_widget.session.id,
                  market_time_context=context, market_context_snapshot=snapshot)
    shell.trading_day.activate_trading_run(run)
    window.save_trading_session_run(run)
    window.save_trading_day(shell.trading_day)
    shell.load_state(shell.trading_day, [first, run], process_session=shell.runtime.session,
                     tda_session=shell.runtime.tda_station_runner_widget.session)
    return run


def test_different_date_launch_is_rejected_before_reset_and_existing_new_day_path_works(cockpit):
    window, shell, connection = cockpit
    first = shell.active_trading_run
    widget(shell).phase_buttons[Role.M].click()
    saved = history(window, shell)
    conclude(shell)
    process, tda = deepcopy(shell.runtime.session), deepcopy(shell.runtime.tda_station_runner_widget.session)
    day_id = shell.trading_day.id
    shell.run_market_timestamp = reference(day=9)
    assert not shell.start_trading_run()
    assert "Run not started" in shell.summary_label.text()
    assert "2026-10-09" in shell.summary_label.text()
    assert "Start New Trading Day" in shell.summary_label.text()
    assert shell.runtime.session == process
    assert shell.runtime.tda_station_runner_widget.session == tda
    assert shell.trading_day.id == day_id and shell.trading_day.futures_day_label == "2026-10-08"
    assert connection.execute("SELECT COUNT(*) FROM trading_session_run").fetchone()[0] == 1
    assert window.trading_session_run_repository.amdx.get_history(first.id) == saved
    assert shell.complete_trading_day()
    shell.start_new_trading_day()
    assert shell.trading_day.id != day_id
    assert shell.trading_day.futures_day_label == "2026-10-09"
    pane = review(shell)
    assert pane.review_day_label == "2026-10-09"
    pane.phase_buttons[Role.M].click()
    assert history(window, shell).claims[-1].cycle.parent_quarter_id == "day:2026-10-09:Q3"
    assert window.trading_session_run_repository.amdx.get_history(first.id) == saved


def test_same_date_additional_run_remains_allowed(cockpit):
    _, shell, _ = cockpit
    original_day = shell.trading_day.id
    conclude(shell)
    assert shell.start_trading_run()
    assert shell.trading_day.id == original_day and len(shell.trading_runs) == 2


def test_missing_old_container_date_does_not_get_rewritten_by_a_later_run(cockpit):
    _, shell, _ = cockpit
    conclude(shell)
    shell.trading_day.futures_day_label = ""
    process_id = shell.runtime.session.id
    assert not shell.start_trading_run()
    assert shell.trading_day.futures_day_label == ""
    assert shell.runtime.session.id == process_id


def test_existing_misgrouped_run_uses_own_snapshot_through_gesture_rollover_and_restart(cockpit):
    window, shell, connection = cockpit
    run = restore_old_mismatched_run(window, shell)
    original_snapshot = deepcopy(run.market_context_snapshot)
    pane = review(shell)
    assert shell.trading_day.futures_day_label == "2026-10-08"
    assert pane.review_day_label == "2026-10-09"
    assert pane.cycles[0].id == "day:2026-10-09"
    assert "Containing Trading Day" in pane.target_label.toolTip()
    target = pane.target
    button = pane.phase_buttons[Role.M]
    QTest.mousePress(button, Qt.MouseButton.LeftButton)
    refresh(shell, reference(19, day=9))
    QTest.mouseRelease(button, Qt.MouseButton.LeftButton)
    saved = history(window, shell).claims[-1]
    assert saved.run_id == run.id and saved.cycle == target.cycle
    assert saved.market_reference == reference(day=9)
    assert pane.reference == reference(19, day=9) and pane.review_day_label == "2026-10-09"
    assert run.market_context_snapshot == original_snapshot
    window.save_trading_session_run(run)
    path = Path(connection.execute("PRAGMA database_list").fetchone()[2])
    reopened = open_application_database(path)
    restored = MainWindow(TDARepository(reopened), StudyFindRepository(reopened))
    try:
        other = restored.trade_plan_widget.trading_day_shell_widget
        assert other.active_trading_run.id == run.id and other.runtime.current_mode.id == "post-market"
        assert widget(other).review_day_label == "2026-10-09"
        widget(other).session_selector.setCurrentIndex(2)
        assert widget(other).table.item(1, 4).text() == "XAMD"
        assert other.trading_day.futures_day_label == "2026-10-08"
        assert restored.trading_session_run_repository.amdx.get_history(run.id).claims == (saved,)
    finally:
        close(restored, reopened)


@pytest.mark.parametrize("reference_value", ["not-a-date", "2026-10-08T09:15:00"])
def test_malformed_original_reference_blocks_even_an_open_gesture_and_recovers(cockpit, reference_value):
    window, shell, _ = cockpit
    pane = review(shell)
    snapshot = deepcopy(shell.active_trading_run.market_context_snapshot)
    pane._begin_gesture()
    shell.active_trading_run.market_context_snapshot["reference_market_time"] = reference_value
    shell.runtime.refresh_market_context()
    assert not pane.phase_buttons[Role.M].isEnabled()
    pane.choose(Role.M)
    assert history(window, shell).claims == ()
    assert "Review date unavailable" in pane.status_label.text()
    shell.active_trading_run.market_context_snapshot = snapshot
    shell.runtime.refresh_market_context()
    assert pane.phase_buttons[Role.M].isEnabled()
    pane.phase_buttons[Role.M].click()
    assert history(window, shell).claims[-1].cycle.parent_quarter_id == "day:2026-10-08:Q3"


def test_legacy_without_snapshot_uses_saved_day_while_clock_moves(cockpit):
    window, shell, _ = cockpit
    shell.active_trading_run.market_context_snapshot = {}
    pane = review(shell)
    assert "No run-start reference" in pane.target_label.toolTip()
    target = pane.target
    refresh(shell, reference(19))
    assert pane.target == target and pane.review_day_label == "2026-10-08"
    pane.phase_buttons[Role.M].click()
    assert history(window, shell).claims[-1].cycle == target.cycle


def test_provenance_date_change_cannot_record_an_older_inflight_target(cockpit):
    window, shell, _ = cockpit
    pane = review(shell)
    pane._begin_gesture()
    shell.active_trading_run.market_context_snapshot["reference_market_time"] = reference(day=9).isoformat()
    shell.runtime.refresh_market_context()
    pane.choose(Role.M)
    assert history(window, shell).claims == ()
    assert pane.review_day_label == "2026-10-09" and pane.target.cycle.id.startswith("session:day:2026-10-09")


def test_date_demo_keeps_run_reference_and_observed_profile_through_restart(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("date_demo", Path(__file__).resolve().parents[1]/"tools/amdx_entry_demo.py")
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)
    directory = tmp_path/"date-trial"
    connection, window = demo.open_demo(directory, review=True, date_case=True)
    shell = window.trade_plan_widget.trading_day_shell_widget
    pane = widget(shell)
    assert shell.trading_day.futures_day_label == "2026-10-08"
    assert pane.review_day_label == "2026-10-09"
    pane.phase_buttons[Role.M].click()
    run_id = shell.active_trading_run.id
    saved = history(window, shell)
    for _ in range(7):
        window.amdx_demo_advance.trigger()
    assert shell.active_trading_run.market_time_context["futures_trading_day"] == "2026-10-10"
    assert pane.review_day_label == "2026-10-09"
    close(window, connection)
    connection, window = demo.open_demo(directory, review=True, date_case=True)
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        pane = widget(shell)
        assert shell.active_trading_run.id == run_id
        assert pane.review_day_label == "2026-10-09"
        pane.session_selector.setCurrentIndex(2)
        assert pane.table.item(1, 4).text() == "XAMD"
        assert history(window, shell) == saved
    finally:
        close(window, connection)
