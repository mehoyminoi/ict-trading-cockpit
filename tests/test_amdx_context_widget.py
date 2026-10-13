from copy import deepcopy
from datetime import datetime
import sqlite3

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.amdx import Anchor, Profile, Role, XSubtype, intraday_cycles
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, build_market_time_context
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


def reference(hour=9, minute=15, day=8):
    return datetime(2026, 10, day, hour, minute, tzinfo=MARKET_TIMEZONE)


def close(window, connection):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    connection.close()


@pytest.fixture
def cockpit(tmp_path):
    connection = open_application_database(tmp_path / "ui.db")
    window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    shell = window.trade_plan_widget.trading_day_shell_widget
    shell.run_environment = RunEnvironment.REPLAY
    shell.run_market_timestamp = reference()
    assert shell.start_trading_run()
    yield window, shell, connection
    close(window, connection)


def widget(shell):
    return shell.runtime.amdx_context_widget


def history(window, shell):
    return window.trading_session_run_repository.amdx.get_history(shell.active_trading_run.id)


def refresh(shell, moment):
    # Replay owns its explicit reference, never the workstation clock.
    shell.active_trading_run.market_time_context = build_market_time_context(moment, source="Historical Reference").to_dict()
    shell._refresh_market_time_display()


def test_real_tda_choice_is_committed_immediately_without_station_completion_or_legacy_rewrite(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    run = shell.active_trading_run
    legacy = deepcopy(run.qt_context)
    station = deepcopy(shell.runtime.tda_station_runner_widget.session)
    before = connection.execute("SELECT * FROM trading_session_run WHERE id = ?", (run.id,)).fetchone()
    assert pane.target.cycle.layer == "session"
    assert pane.target.quarter_id.endswith("Q3")
    QTest.mouseClick(pane.phase_buttons[Role.M], Qt.MouseButton.LeftButton)
    saved = history(window, shell).claims[-1]
    assert saved.inference.candidates == (Profile.XAMD,)
    assert saved.market_reference == reference()
    assert "Recorded" in pane.status_label.text()
    assert "implied" in pane.table.item(1, 0).text()
    assert "entered" in pane.table.item(1, 2).text()
    assert pane.table.item(1, 4).text() == "XAMD"
    assert run.qt_context == legacy
    assert shell.runtime.tda_station_runner_widget.session == station
    assert connection.execute("SELECT * FROM trading_session_run WHERE id = ?", (run.id,)).fetchone() == before


def test_watch_and_tda_share_one_panel_without_reanalysis_or_new_authorization(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    run = shell.active_trading_run
    before_gates = deepcopy(run.authorization_gate_states)
    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    assert pane.mode_id == "live-watch"
    pane.select_quarter(0, 2)  # Daily NYAM=Q3, rather than NYAM's separate 90m Q3.
    pane.phase_buttons[Role.D].click()
    assert shell.runtime.current_mode.id == "live-watch"
    assert history(window, shell).claims[-1].inference.candidates == (Profile.AMDX,)
    assert pane.table.item(0, 3).text().startswith("NYPM · X(?)")
    assert pane.table.item(1, 4).text() == "Unresolved"
    assert run.authorization_gate_states == before_gates
    assert shell.runtime.apply_transition("live-return-analysis")
    assert widget(shell) is pane
    assert pane.table.item(0, 4).text() == "AMDX"


def test_inspection_render_clock_and_review_never_append_history(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    for i in range(4):
        pane.select_quarter(0, i)
        pane._render()
    refresh(shell, reference(10, 30))
    shell.runtime.tda_station_runner_widget.go_next_station()
    assert history(window, shell).claims == ()
    shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    shell.runtime.apply_transition("live-finish")
    assert pane.mode_id == "post-market"
    pane.choose(Role.D)
    assert history(window, shell).claims == ()
    assert not pane.phase_buttons[Role.D].isVisible()


def test_successful_current_input_follows_new_90m_quarter_without_follow_button_obligation(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.phase_buttons[Role.M].click()
    assert not pane._pinned
    refresh(shell, reference(10, 30))
    assert pane.target.quarter_id.endswith("Q4")
    pane.phase_buttons[Role.D].click()
    claims = history(window, shell).claims
    assert [c.action_quarter_id.rsplit(":", 1)[-1] for c in claims] == ["Q3", "Q4"]


def test_selected_target_stays_pinned_across_session_boundary_and_follow_is_navigation_only(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.select_quarter(1, 2)
    original = pane.target
    refresh(shell, reference(12, 1))
    assert pane.target == original
    assert pane.cycles[-1] == original.cycle
    pane.phase_buttons[Role.M].click()
    assert history(window, shell).claims[-1].cycle == original.cycle
    assert history(window, shell).claims[-1].market_reference == reference(12, 1)
    pane.follow_button.click()
    assert pane.target.cycle != original.cycle
    assert pane.target.quarter_id.endswith("Q1")
    assert len(history(window, shell).claims) == 1


def test_mouse_press_pins_identity_and_reference_until_release_across_boundary(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    button = pane.phase_buttons[Role.M]
    original = pane.target
    QTest.mousePress(button, Qt.MouseButton.LeftButton)
    refresh(shell, reference(12, 1))
    QTest.mouseRelease(button, Qt.MouseButton.LeftButton)
    saved = history(window, shell).claims[-1]
    assert saved.cycle == original.cycle
    assert saved.action_quarter_id == original.quarter_id
    assert saved.market_reference == reference()
    assert pane.reference == reference(12, 1)
    assert pane.target.cycle != original.cycle
    assert pane.target.quarter_id.endswith("Q1")
    assert not pane._pinned
    QApplication.processEvents()
    assert len(history(window, shell).claims) == 1


@pytest.mark.parametrize("pinned", [False, True])
def test_cancelled_menu_preserves_inspection_or_resumes_current_without_recording(cockpit, pinned):
    window, shell, connection = cockpit
    pane = widget(shell)
    if pinned:
        pane.select_quarter(1, 2)
    original = pane.target
    pane.menu.popup(pane.more_button.mapToGlobal(pane.more_button.rect().bottomLeft()))
    refresh(shell, reference(12, 1))
    assert pane.target == original
    pane.menu.close()
    QApplication.processEvents()
    assert pane.reference == reference(12, 1)
    if pinned:
        assert pane.target == original
        assert pane.cycles[-1] == original.cycle
    else:
        assert pane.target.cycle != original.cycle
        assert pane.target.quarter_id.endswith("Q1")
    assert pane._pinned is pinned
    assert history(window, shell).claims == ()


def test_menu_choice_across_boundary_records_original_basis_then_resumes_current(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    refresh(shell, reference(10, 30))  # Q4 permits X; Q3 deliberately does not.
    original = pane.target
    pane.menu.popup(pane.more_button.mapToGlobal(pane.more_button.rect().bottomLeft()))
    refresh(shell, reference(12, 1))
    action = pane.menu_actions["X(R) · Reversal"]
    QTest.mouseClick(pane.menu, Qt.MouseButton.LeftButton, pos=pane.menu.actionGeometry(action).center())
    QApplication.processEvents()
    saved = history(window, shell).claims[-1]
    assert saved.cycle == original.cycle
    assert saved.action_quarter_id == original.quarter_id
    assert saved.market_reference == reference(10, 30)
    assert saved.anchors[0].subtype is XSubtype.REVERSAL
    assert pane.reference == reference(12, 1)
    assert pane.target.cycle != original.cycle
    assert not pane._pinned
    assert len(history(window, shell).claims) == 1


def test_failed_boundary_input_pins_original_target_for_explicit_retry(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    original = pane.target
    button = pane.phase_buttons[Role.M]
    connection.execute("CREATE TRIGGER fail_boundary_append BEFORE INSERT ON amdx_claim BEGIN SELECT RAISE(ABORT, 'fixture disk failure'); END")
    QTest.mousePress(button, Qt.MouseButton.LeftButton)
    refresh(shell, reference(12, 1))
    QTest.mouseRelease(button, Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    assert "Not recorded" in pane.status_label.text()
    assert pane.target == original
    assert pane._pinned
    assert "pinned" in pane.target_label.text()
    refresh(shell, reference(13, 30))
    assert pane.target == original
    assert history(window, shell).claims == ()
    connection.execute("DROP TRIGGER fail_boundary_append")
    button.click()
    saved = history(window, shell).claims[-1]
    assert saved.cycle == original.cycle
    assert saved.action_quarter_id == original.quarter_id
    assert saved.market_reference == reference(13, 30)
    pane.follow_button.click()
    assert pane.target.cycle != original.cycle
    assert len(history(window, shell).claims) == 1


def test_stale_boundary_gesture_keeps_latest_clock_and_pins_original_scope(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    original = pane.target
    button = pane.phase_buttons[Role.D]
    QTest.mousePress(button, Qt.MouseButton.LeftButton)
    pane.repository.accept(claim_id="boundary-outside-edit", run_id=original.run_id, branch_id="working", channel="Expected",
                           cycle=original.cycle, quarter_id=original.quarter_id,
                           anchor=Anchor("boundary-outside-anchor", original.quarter_id, Role.M, "synthetic-other-editor"),
                           recorded_at=reference(), market_reference=reference(), expected_head_id=None)
    refresh(shell, reference(12, 1))
    QTest.mouseRelease(button, Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    assert "Not recorded" in pane.status_label.text()
    assert pane.reference == reference(12, 1)
    assert pane.target.quarter_id == original.quarter_id
    assert pane.target.cycle == original.cycle
    assert pane.target.expected_head_id == "boundary-outside-edit"
    assert pane._pinned
    assert pane.table.item(1, 4).text() == "XAMD"
    assert len(history(window, shell).claims) == 1
    button.click()
    assert history(window, shell).claims[-1].market_reference == reference(12, 1)
    assert history(window, shell).claims[-1].inference.candidates == (Profile.AMDX,)
    pane.follow_button.click()
    assert pane.target.cycle != original.cycle


def test_x_subtype_clear_and_unknown_are_explicit_distinct_actions(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.select_quarter(0, 3)
    pane.phase_buttons[Role.X].click()
    assert history(window, shell).claims[-1].anchors[0].subtype is None
    pane.menu_actions["X(R) · Reversal"].trigger()
    assert history(window, shell).claims[-1].anchors[0].subtype is XSubtype.REVERSAL
    pane.menu_actions["Unknown"].trigger()
    assert history(window, shell).claims[-1].anchors[0].role is Role.UNKNOWN
    pane.menu_actions["Clear this anchor"].trigger()
    assert history(window, shell).claims[-1].anchors == ()
    assert len(history(window, shell).claims) == 4


def test_new_entry_changes_order_without_old_anchor_cleanup_or_erasing_history(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.select_quarter(0, 0)
    pane.phase_buttons[Role.A].click()
    pane.select_quarter(0, 1)
    pane.phase_buttons[Role.A].click()
    assert pane.table.item(0, 4).text() == "XAMD"
    claims = history(window, shell).claims
    assert len(claims[-1].anchors) == 1
    assert claims[-1].retired_anchor_ids == (claims[0].anchors[0].id,)
    assert claims[0].inference.candidates == (Profile.AMDX,)
    assert "implied" in pane.table.item(0, 0).text()
    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True)


def test_failed_write_displays_not_recorded_and_retains_last_committed_profile(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.phase_buttons[Role.M].click()
    connection.execute("CREATE TRIGGER fail_ui_append BEFORE INSERT ON amdx_claim BEGIN SELECT RAISE(ABORT, 'fixture disk failure'); END")
    pane.phase_buttons[Role.D].click()
    assert len(history(window, shell).claims) == 1
    assert pane.table.item(1, 4).text() == "XAMD"
    assert "Not recorded" in pane.status_label.text()
    shell._refresh_market_time_display()
    assert "Not recorded" in pane.status_label.text()
    connection.execute("DROP TRIGGER fail_ui_append")
    pane.phase_buttons[Role.D].click()
    assert len(history(window, shell).claims) == 2


def test_stale_input_reloads_same_quarter_and_requires_another_deliberate_choice(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.select_quarter(0, 2)
    target = pane.target
    pane.repository.accept(claim_id="outside-edit", run_id=target.run_id, branch_id="working", channel="Expected",
                           cycle=target.cycle, quarter_id=target.quarter_id,
                           anchor=Anchor("outside-anchor", target.quarter_id, Role.M, "synthetic-other-editor"),
                           recorded_at=reference(), market_reference=reference(), expected_head_id=None)
    refresh(shell, reference(12, 1))
    pane.phase_buttons[Role.D].click()
    assert len(history(window, shell).claims) == 1
    assert "Not recorded" in pane.status_label.text()
    assert pane.target.quarter_id == target.quarter_id
    assert pane.target.expected_head_id == "outside-edit"
    pane.phase_buttons[Role.D].click()
    assert history(window, shell).claims[-1].inference.candidates == (Profile.AMDX,)


def test_normal_window_restore_retains_claim_ids_profile_and_legacy_values(cockpit, tmp_path):
    window, shell, connection = cockpit
    pane = widget(shell)
    shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    pane.phase_buttons[Role.M].click()
    saved = history(window, shell).claims[-1]
    run_id = shell.active_trading_run.id
    legacy = deepcopy(shell.active_trading_run.qt_context)
    reopened = open_application_database(tmp_path / "ui.db")
    restored = MainWindow(TDARepository(reopened), StudyFindRepository(reopened))
    try:
        other = restored.trade_plan_widget.trading_day_shell_widget
        assert other.active_trading_run.id == run_id
        assert other.runtime.current_mode.id == "live-watch"
        assert widget(other).table.item(1, 4).text() == "XAMD"
        assert restored.trading_session_run_repository.amdx.get_history(run_id).claims == (saved,)
        assert other.active_trading_run.qt_context == legacy
        assert not other.runtime.qt_context_widget.phase_combos["session"].isEnabled()
        assert "Higher QT" in widget(other).higher_label.text()
    finally:
        close(restored, reopened)


def test_read_failure_disables_recording_without_clearing_last_validated_view(cockpit, monkeypatch):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.phase_buttons[Role.M].click()
    original = pane.repository.get_history
    def fail(*_):
        raise sqlite3.OperationalError("fixture read failure")
    monkeypatch.setattr(pane.repository, "get_history", fail)
    shell._refresh_market_time_display()
    assert "History unavailable" in pane.status_label.text()
    assert pane.table.item(1, 4).text() == "XAMD"
    assert not pane.phase_buttons[Role.M].isEnabled()
    monkeypatch.setattr(pane.repository, "get_history", original)
    shell._refresh_market_time_display()
    assert pane.phase_buttons[Role.M].isEnabled()
    assert "History unavailable" not in pane.status_label.text()


def test_orientation_stays_outside_scroll_and_small_window_keeps_controls_reachable(cockpit):
    window, shell, connection = cockpit
    window.trade_plan_widget.focus_runtime()
    window.resize(1024, 768)
    window.show()
    QApplication.processEvents()
    pane = widget(shell)
    assert pane.parent() is shell
    assert pane.width() <= shell.width()
    assert all(pane.rect().contains(b.mapTo(pane, b.rect().bottomRight()))
               for b in (*pane.phase_buttons.values(), pane.more_button))
    position = pane.pos()
    shell.runtime_scroll.verticalScrollBar().setValue(shell.runtime_scroll.verticalScrollBar().maximum())
    QApplication.processEvents()
    assert pane.pos() == position
    assert shell.runtime_scroll.verticalScrollBarPolicy() is Qt.ScrollBarPolicy.ScrollBarAsNeeded
    assert not shell.runtime.tda_station_runner_widget._accumulate_wheel_navigation(-480)
    shell.runtime_scroll.ensureWidgetVisible(shell.runtime.tda_station_runner_widget.observation_input)
    QApplication.processEvents()
    observation = shell.runtime.tda_station_runner_widget.observation_input
    viewport = shell.runtime_scroll.viewport()
    assert viewport.rect().intersects(observation.rect().translated(observation.mapTo(viewport, observation.rect().topLeft())))


def test_keyboard_quarter_selection_pins_target_without_recording(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.table.setFocus()
    QTest.keyClick(pane.table, Qt.Key.Key_Left)
    assert pane.target.quarter_id.endswith("Q2")
    assert pane._pinned
    assert history(window, shell).claims == ()
    pane.phase_buttons[Role.M].click()
    assert history(window, shell).claims[-1].action_quarter_id.endswith("Q2")


def test_entry_demo_retains_one_run_claims_and_explicit_reference_without_reseeding(tmp_path):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("amdx_entry_demo", Path(__file__).resolve().parents[1] / "tools/amdx_entry_demo.py")
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)
    directory = tmp_path / "sandbox with spaces"
    connection, window = demo.open_demo(directory)
    shell = window.trade_plan_widget.trading_day_shell_widget
    pane = widget(shell)
    pane.phase_buttons[Role.M].click()
    run_id = shell.active_trading_run.id
    claim = history(window, shell).claims[-1]
    window.amdx_demo_advance.trigger()
    assert pane.target.quarter_id.endswith("Q4")
    manifest = (directory / "amdx-entry-fixture.json").read_bytes()
    close(window, connection)
    connection, window = demo.open_demo(directory)
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        assert shell.active_trading_run.id == run_id
        assert history(window, shell).claims == (claim,)
        assert widget(shell).target.quarter_id.endswith("Q4")
        assert (directory / "amdx-entry-fixture.json").read_bytes() == manifest
    finally:
        close(window, connection)


def test_entry_demo_refuses_to_replace_unrelated_files(tmp_path):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("amdx_entry_demo_refusal", Path(__file__).resolve().parents[1] / "tools/amdx_entry_demo.py")
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)
    (tmp_path / "demo.db").write_bytes(b"operator data")
    with pytest.raises(ValueError, match="empty"):
        demo.open_demo(tmp_path)
    assert (tmp_path / "demo.db").read_bytes() == b"operator data"


@pytest.mark.parametrize("position,valid", [(1,{Role.A,Role.X}),(2,{Role.A,Role.M}),(3,{Role.M,Role.D}),(4,{Role.D,Role.X})])
def test_phase_buttons_and_x_menu_follow_selected_quarter_structure(cockpit, position, valid):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.select_quarter(0, position - 1)
    assert {role for role, button in pane.phase_buttons.items() if button.isEnabled()} == valid
    assert pane.menu_actions['X(R) · Reversal'].isEnabled() == (Role.X in valid)
    assert pane.menu_actions['X(C) · Continuation'].isEnabled() == (Role.X in valid)
    invalid = next(role for role in (Role.A,Role.M,Role.D,Role.X) if role not in valid)
    pane.phase_buttons[invalid].click()
    assert history(window, shell).claims == ()
    pane.choose(invalid)  # all adapters are checked at the shared action, too
    assert history(window, shell).claims == ()
    assert 'Not recorded' in pane.status_label.text()


def test_legacy_conflict_remains_inspectable_and_new_entry_revises_in_one_action(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    day = intraday_cycles(reference())[0]
    common = dict(run_id=shell.active_trading_run.id,branch_id='working',channel='Expected',cycle=day,
                  recorded_at=reference(),market_reference=reference())
    first = pane.repository.accept(**common,claim_id='legacy-1',quarter_id=day.quarters[0].id,
                                   anchor=Anchor('legacy-a1',day.quarters[0].id,Role.A,'fixture-legacy'),expected_head_id=None)
    conflict = pane.repository.accept(**common,claim_id='legacy-2',quarter_id=day.quarters[1].id,
                                      anchor=Anchor('legacy-a2',day.quarters[1].id,Role.A,'fixture-legacy'),expected_head_id=first.id)
    refresh(shell, reference())
    assert pane.table.item(0,4).text() == 'Conflict'
    pane.select_quarter(0,2)
    pane.phase_buttons[Role.M].click()
    claims = history(window, shell).claims
    assert claims[-1].basis_claim_id == conflict.id
    assert claims[-1].retired_anchor_ids == ('legacy-a1',)
    assert pane.table.item(0,4).text() == 'XAMD'
    assert claims[1].inference.state == 'Conflict'
    assert len(claims) == 3


def test_identical_explicit_choice_is_noop_but_implied_choice_becomes_explicit(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.select_quarter(0,2)
    pane.phase_buttons[Role.D].click()
    first = history(window, shell).claims[-1]
    pane.phase_buttons[Role.D].click()
    assert history(window, shell).claims == (first,)
    assert 'Already current' in pane.status_label.text()
    pane.select_quarter(0,0)
    pane.phase_buttons[Role.A].click()
    assert len(history(window, shell).claims) == 2
    assert len(history(window, shell).claims[-1].anchors) == 2


def test_unknown_shows_conditional_role_and_applicability_can_be_restored_without_hunting(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.select_quarter(0,0)
    pane.phase_buttons[Role.A].click()
    pane.select_quarter(0,2)
    pane.phase_buttons[Role.D].click()
    pane.menu_actions['Unknown'].trigger()
    assert 'Unknown / D' in pane.table.item(0,2).text()
    assert 'entered / implied' in pane.table.item(0,2).text()
    assert 'Conditional structural role: D' in pane.table.item(0,2).toolTip()
    pane.menu_actions['Not Applicable'].trigger()
    assert pane.table.item(0,4).text() == 'Not Applicable'
    pane.menu_actions['Unknown'].trigger()
    assert pane.table.item(0,4).text() == 'Not Applicable'
    assert pane.menu_actions['Clear this anchor'].text() == 'Clear Not Applicable'
    pane.menu_actions['Clear this anchor'].trigger()
    assert pane.table.item(0,4).text() == 'Unresolved'
    pane.menu_actions['Not Applicable'].trigger()
    pane.select_quarter(0,1)
    pane.phase_buttons[Role.A].click()
    assert pane.table.item(0,4).text() == 'XAMD'
    assert not history(window, shell).claims[-1].applicability


def test_read_failure_after_success_retains_just_committed_meaning(cockpit, monkeypatch):
    window, shell, connection = cockpit
    pane = widget(shell)
    original = pane.repository.get_history
    calls = 0
    def fail_after_write(*args):
        nonlocal calls
        calls += 1
        if calls > 1:
            raise sqlite3.OperationalError('fixture post-commit read failure')
        return original(*args)
    monkeypatch.setattr(pane.repository,'get_history',fail_after_write)
    pane.phase_buttons[Role.M].click()
    assert 'History unavailable' in pane.status_label.text()
    assert pane.table.item(1,4).text() == 'XAMD'
    assert not pane.phase_buttons[Role.M].isEnabled()
    monkeypatch.setattr(pane.repository,'get_history',original)
    assert len(history(window, shell).claims) == 1


def test_queued_old_menu_close_cannot_cancel_new_gesture_across_boundary(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    original = pane.target
    point = pane.more_button.mapToGlobal(pane.more_button.rect().bottomLeft())
    pane.menu.popup(point)
    pane.menu.close()
    pane.menu.popup(point)  # new gesture before the old deferred close callback
    refresh(shell, reference(12,1))
    QApplication.processEvents()
    assert pane.target == original
    action = pane.menu_actions['Unknown']
    QTest.mouseClick(pane.menu,Qt.MouseButton.LeftButton,pos=pane.menu.actionGeometry(action).center())
    QApplication.processEvents()
    saved = history(window, shell).claims[-1]
    assert saved.action_quarter_id == original.quarter_id
    assert saved.market_reference == reference()
    assert pane.target.cycle != original.cycle
