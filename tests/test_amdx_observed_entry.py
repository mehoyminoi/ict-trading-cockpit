"""Normal-window Review binding, independent observations and pinned gestures."""
from copy import deepcopy
from datetime import datetime
from uuid import uuid4
import sqlite3

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.amdx import Anchor, Profile, Role, XSubtype, available_roles
from test_amdx_context_widget import cockpit, close, history, reference, refresh, widget


def review(shell):
    assert shell.runtime.apply_transition("finish-tda", override_incomplete=True)
    assert shell.runtime.apply_transition("live-finish")
    assert widget(shell).channel == "Observed"
    return widget(shell)


def saved_review(window, shell):
    return window.trading_session_run_repository.amdx.review.get_history(shell.active_trading_run.id)


def external_observation(pane, role):
    target = pane.target
    return pane.repository.review.revise_observed(
        claim_id=str(uuid4()), comparison_id=str(uuid4()), run_id=target.run_id,
        branch_id="working", cycle=target.cycle, quarter_id=target.quarter_id,
        anchor=Anchor(str(uuid4()), target.quarter_id, role, "Other editor"),
        recorded_at=datetime.now().astimezone(), market_reference=pane.reference,
        expected_observed_head_id=target.expected_head_id,
        expected_comparison_head_id=target.comparison_head_id,
    )


def test_review_records_independent_observation_without_save_or_automatic_baseline(cockpit):
    window, shell, connection = cockpit
    pane = widget(shell)
    pane.phase_buttons[Role.M].click()
    expected = history(window, shell).claims[-1]
    run = shell.active_trading_run
    legacy = deepcopy((run.qt_context, run.review_observed_qt_context))
    pane = review(shell)
    before = connection.execute("SELECT * FROM trading_session_run WHERE id=?", (run.id,)).fetchone()
    assert pane.table.item(1, 4).text() == "Unresolved"
    QTest.mouseClick(pane.phase_buttons[Role.D], Qt.MouseButton.LeftButton)
    saved = saved_review(window, shell)
    assert saved.interpretations.claims[0] == expected
    observed = saved.interpretations.claims[-1]
    assert observed.channel == "Observed" and observed.inference.candidates == (Profile.AMDX,)
    assert saved.comparisons[-1].expected_claim_id is None
    assert pane.table.item(1, 4).text() == "AMDX"
    assert pane.target.comparison_head_id == saved.comparisons[-1].id
    assert (run.qt_context, run.review_observed_qt_context) == legacy
    assert connection.execute("SELECT * FROM trading_session_run WHERE id=?", (run.id,)).fetchone() == before
    assert shell.runtime.current_mode.id == "post-market"
    assert shell.runtime.post_market_review_widget.qt_comparison_list.isHidden()
    assert shell.runtime.post_market_review_widget.observed_qt_combos["session"].isHidden()
    assert not shell.runtime.post_market_review_widget.observed_qt_combos["week"].isHidden()


@pytest.mark.parametrize("position", [1, 2, 3, 4])
def test_review_only_enables_structural_roles_and_direct_subtypes(cockpit, position):
    _, shell, _ = cockpit
    pane = review(shell)
    pane.select_quarter(0, position - 1)
    for role, button in pane.phase_buttons.items():
        assert button.isEnabled() == (role in available_roles(position))
    for button in pane.subtype_buttons.values():
        assert button.isEnabled() == (position in (1, 4))


@pytest.mark.parametrize("subtype", list(XSubtype))
def test_one_click_x_subtype_correction_retains_previous_judgment(cockpit, subtype):
    window, shell, _ = cockpit
    pane = review(shell)
    pane.select_quarter(0, 3)
    QTest.mouseClick(pane.subtype_buttons[subtype], Qt.MouseButton.LeftButton)
    first = history(window, shell).claims[-1]
    assert first.anchors[0].subtype is subtype
    assert pane.table.item(0, 3).text().startswith(f"NYPM · X({subtype.value})")
    pane.select_quarter(0, 2)
    pane.phase_buttons[Role.M].click()
    second = history(window, shell).claims[-1]
    assert second.inference.candidates == (Profile.XAMD,)
    assert first.id != second.id and first.anchors[0].id in second.retired_anchor_ids
    assert pane.table.item(0, 0).text().startswith("Asia · X(?)")
    assert history(window, shell).claims[0] == first


def test_observed_noop_unknown_na_and_clear_remain_immediate_and_independent(cockpit):
    window, shell, connection = cockpit
    pane = review(shell)
    pane.select_quarter(0, 2)
    pane.menu_actions["Clear this anchor"].trigger()
    assert history(window, shell).claims == ()
    assert "Already current" in pane.status_label.text()
    pane.phase_buttons[Role.D].click()
    first = history(window, shell).claims[-1]
    pane.phase_buttons[Role.D].click()
    assert history(window, shell).claims == (first,)
    assert "Already current" in pane.status_label.text()
    assert len(saved_review(window, shell).comparisons) == 1
    pane.menu_actions["Unknown"].trigger()
    assert "Unknown" in pane.table.item(0, 2).text()
    pane.menu_actions["Not Applicable"].trigger()
    assert pane.table.item(0, 4).text() == "Not Applicable"
    pane.menu_actions["Clear this anchor"].trigger()
    assert pane.table.item(0, 4).text() == "Unresolved"
    assert all(c.channel == "Observed" for c in history(window, shell).claims)
    assert connection.execute("SELECT COUNT(*) FROM amdx_observed_command").fetchone()[0] == 6


def test_review_day_all_sessions_and_selection_are_stable_across_rollover(cockpit):
    window, shell, _ = cockpit
    pane = review(shell)
    original = pane.target
    refresh(shell, reference(19, 30, day=9))
    assert pane.target == original
    assert pane.cycles[0].id == "day:2026-10-08"
    for index, name in enumerate(("Asia", "London", "NYAM", "NYPM")):
        pane.session_selector.setCurrentIndex(index)
        assert pane.cycles[-1].parent_quarter_id == f"day:2026-10-08:Q{index + 1}"
        assert name in pane.target_label.text()
        assert pane.target.quarter_id.endswith("Q1")
    pane.select_quarter(0, 1)
    assert pane.session_selector.currentText() == "London"
    pane.select_quarter(1, 1)
    pane.phase_buttons[Role.M].click()
    assert history(window, shell).claims[-1].cycle.parent_quarter_id == "day:2026-10-08:Q2"
    assert history(window, shell).claims[-1].market_reference == reference(19, 30, day=9)
    assert pane.follow_button.isHidden()


def test_review_mouse_gesture_pins_reference_and_quarter_through_clock_refresh(cockpit):
    window, shell, _ = cockpit
    pane = review(shell)
    original = pane.target
    button = pane.phase_buttons[Role.M]
    QTest.mousePress(button, Qt.MouseButton.LeftButton)
    refresh(shell, reference(18, 1))
    QTest.mouseRelease(button, Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    claim = history(window, shell).claims[-1]
    assert claim.cycle == original.cycle and claim.action_quarter_id == original.quarter_id
    assert claim.market_reference == reference()
    assert pane.reference == reference(18, 1)
    assert pane.target.cycle == original.cycle


def test_working_gesture_cannot_become_observed_entry_after_mode_transition(cockpit):
    window, shell, _ = cockpit
    pane = widget(shell)
    button = pane.phase_buttons[Role.M]
    QTest.mousePress(button, Qt.MouseButton.LeftButton)
    review(shell)
    QTest.mouseRelease(button, Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    assert history(window, shell).claims == ()
    assert pane.session_selector.isEnabled()


def test_review_menu_cancel_is_navigation_only_and_reenables_session_selection(cockpit):
    window, shell, _ = cockpit
    pane = review(shell)
    target = pane.target
    pane.menu.popup(pane.more_button.mapToGlobal(pane.more_button.rect().bottomLeft()))
    assert not pane.session_selector.isEnabled()
    refresh(shell, reference(18, 1))
    pane.menu.close()
    QApplication.processEvents()
    assert pane.target == target and pane.session_selector.isEnabled()
    assert history(window, shell).claims == ()


def test_pressed_review_choice_cannot_write_into_a_different_loaded_run(cockpit):
    from dataclasses import replace
    window, shell, _ = cockpit
    pane = review(shell)
    original_run = shell.active_trading_run
    new_run = replace(original_run, id=str(uuid4()))
    window.trading_session_run_repository.save(new_run)
    button = pane.phase_buttons[Role.M]
    QTest.mousePress(button, Qt.MouseButton.LeftButton)
    pane.load_context(new_run, new_run.market_time_context, "post-market", review_day_label="2026-10-08")
    QTest.mouseRelease(button, Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    assert pane.repository.get_history(new_run.id).claims == ()
    assert pane.repository.get_history(original_run.id).claims == ()


@pytest.mark.parametrize("table", ["amdx_claim", "amdx_comparison", "amdx_observed_command"])
def test_failure_keeps_original_target_and_committed_meaning_without_partial_rows(cockpit, table):
    window, shell, connection = cockpit
    pane = review(shell)
    pane.phase_buttons[Role.M].click()
    original, target = saved_review(window, shell), pane.target
    connection.execute(f"CREATE TRIGGER fail_observed_ui BEFORE INSERT ON {table} BEGIN SELECT RAISE(ABORT, 'fixture write failure'); END")
    pane.phase_buttons[Role.D].click()
    assert "Not recorded" in pane.status_label.text()
    assert saved_review(window, shell) == original
    assert pane.target == target and pane.table.item(1, 4).text() == "XAMD"
    refresh(shell, reference(18, 1))
    assert pane.target == target
    connection.execute("DROP TRIGGER fail_observed_ui")
    pane.phase_buttons[Role.D].click()
    assert pane.table.item(1, 4).text() == "AMDX"
    assert len(saved_review(window, shell).comparisons) == 2


def test_stale_observed_head_reloads_without_replaying_then_allows_deliberate_retry(cockpit):
    window, shell, _ = cockpit
    pane = review(shell)
    external = external_observation(pane, Role.D)
    pane.phase_buttons[Role.M].click()
    assert "Not recorded" in pane.status_label.text()
    assert pane.target.expected_head_id == external.claim.id
    assert pane.target.comparison_head_id == external.comparison.id
    assert history(window, shell).claims == (external.claim,)
    pane.phase_buttons[Role.M].click()
    assert len(history(window, shell).claims) == 2
    assert pane.table.item(1, 4).text() == "XAMD"


def test_stale_pair_head_reloads_without_replay_and_preserves_deliberately_selected_basis(cockpit):
    window, shell, _ = cockpit
    pane = widget(shell)
    pane.phase_buttons[Role.M].click()
    expected = history(window, shell).claims[-1]
    pane = review(shell)
    pane.phase_buttons[Role.D].click()
    observed = history(window, shell).claims[-1]
    pair = pane.repository.review.record_comparison(
        comparison_id=str(uuid4()), run_id=pane.run.id, expected_claim_id=expected.id,
        observed_claim_id=observed.id, recorded_at=datetime.now().astimezone(),
        market_reference=pane.reference, expected_head_id=pane.target.comparison_head_id,
    )
    pane.phase_buttons[Role.M].click()
    assert "Not recorded" in pane.status_label.text()
    assert history(window, shell).claims[-1] == observed
    assert pane.target.comparison_head_id == pair.id
    pane.phase_buttons[Role.M].click()
    assert saved_review(window, shell).comparisons[-1].expected_claim_id == expected.id


def test_review_read_failure_after_commit_preserves_committed_view_and_disables_writes(cockpit, monkeypatch):
    window, shell, _ = cockpit
    pane = review(shell)
    original = pane.repository.review.get_history
    calls = 0
    def fail_after_commit(*args):
        nonlocal calls
        calls += 1
        if calls > 1:
            raise sqlite3.OperationalError("fixture read failure")
        return original(*args)
    monkeypatch.setattr(pane.repository.review, "get_history", fail_after_commit)
    pane.phase_buttons[Role.M].click()
    assert "History unavailable" in pane.status_label.text()
    assert pane.table.item(1, 4).text() == "XAMD"
    assert not pane.phase_buttons[Role.M].isEnabled()
    assert not pane.subtype_buttons[XSubtype.REVERSAL].isEnabled()
    assert original(pane.run.id).interpretations.claims[-1].id == pane.target.expected_head_id
    monkeypatch.setattr(pane.repository.review, "get_history", original)
    shell._refresh_market_time_display()
    assert pane.phase_buttons[Role.M].isEnabled()
    assert "History unavailable" not in pane.status_label.text()


def test_missing_saved_review_day_disables_entry_without_guessing_today(cockpit):
    window, shell, _ = cockpit
    pane = review(shell)
    shell.runtime.review_day_label = ""
    shell.active_trading_run.market_context_snapshot = {}
    shell.runtime.refresh_market_context()
    assert pane.target is None and not pane.phase_buttons[Role.M].isEnabled()
    pane.choose(Role.M)
    assert history(window, shell).claims == ()


def test_review_fixture_reopens_exact_observed_history_and_saved_day_after_rollover(tmp_path):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("amdx_entry_demo", Path(__file__).resolve().parents[1] / "tools/amdx_entry_demo.py")
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)
    directory = tmp_path / "review trial"
    connection, window = demo.open_demo(directory, review=True)
    shell = window.trade_plan_widget.trading_day_shell_widget
    pane = widget(shell)
    pane.select_quarter(0, 3)
    pane.subtype_buttons[XSubtype.REVERSAL].click()
    saved = saved_review(window, shell)
    manifest = (directory / "amdx-entry-fixture.json").read_bytes()
    for _ in range(12):
        window.amdx_demo_advance.trigger()
    assert pane.cycles[0].id == "day:2026-10-08"
    window.amdx_demo_failure.setChecked(True)
    pane.select_quarter(0, 2)
    pane.phase_buttons[Role.M].click()
    assert "Not recorded" in pane.status_label.text()
    assert saved_review(window, shell) == saved
    window.amdx_demo_failure.setChecked(False)
    close(window, connection)
    connection, window = demo.open_demo(directory, review=True)
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        pane = widget(shell)
        assert shell.runtime.current_mode.id == "post-market"
        assert pane.cycles[0].id == "day:2026-10-08"
        assert pane.table.item(0, 3).text().startswith("NYPM · X(R)")
        assert saved_review(window, shell) == saved
        assert (directory / "amdx-entry-fixture.json").read_bytes() == manifest
    finally:
        close(window, connection)
