"""Isolated Replay command, native integration and historical-integrity checks."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import sqlite3

import pytest
from PySide6.QtCore import QTimer, QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QLabel

from ict_cockpit.analysis.replay_reference import resolve_new_york, validate_progression, REPLAY_RECEIPT_KEY
from ict_cockpit.analysis.trading_session_run import RunEnvironment, AuthorizationStatus
from ict_cockpit.database.replay_reference import advance_replay_reference
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.gui.replay_reference_dialog import ReplayReferenceDialog
from tools.tda_watch_journey_demo import open_demo
from test_time_aware_watch import clear_all_non_time_gates
from ict_cockpit.default_trade_plan import build_default_trade_plan


@pytest.fixture
def cockpit(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path / 'outside'))
    connection, window = open_demo(tmp_path / 'replay')
    yield window, window.trade_plan_widget.trading_day_shell_widget, connection
    close(connection, window)


def close(connection, window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    QApplication.processEvents()
    connection.close()


def at(time):
    return resolve_new_york('2026-10-09 ' + time)


def rows(connection):
    return {name: connection.execute(f'SELECT * FROM {name}').fetchall() for name in (
        'trading_session_run', 'amdx_run_binding', 'amdx_run_capture',
        'amdx_run_calendar_command', 'amdx_claim')}


def test_advance_preserves_history_and_resumes(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path / 'outside'))
    path = tmp_path / 'replay'
    connection, window = open_demo(path)
    shell = window.trade_plan_widget.trading_day_shell_widget
    try:
        shell._capture_live_observation('Initial prospective expectation; simulated')
        original = deepcopy(shell.active_trading_run)
        before = rows(connection)
        shell.runtime.apply_transition('finish-tda', override_incomplete=True)
        watch = shell.runtime.live_watch_widget
        watch.observation_input.setText('unfinished observation')
        watch.thesis_note_input.setText('unfinished thesis')
        updated = shell.set_replay_reference(at('10:45'))
        assert updated.id == original.id
        assert updated.market_context_snapshot == original.market_context_snapshot
        assert updated.evidence[:-1] == original.evidence
        assert updated.market_time_context['captured_at'].startswith('2026-10-09T10:45')
        assert updated.evidence[-1].market_time_context[REPLAY_RECEIPT_KEY]['intervening_observation'] == 'Unspecified'
        assert watch.observation_input.text() == 'unfinished observation'
        assert watch.thesis_note_input.text() == 'unfinished thesis'
        assert '10:45' in shell.runtime.watch_quiet_composition.orientation.market_time_label.text()
        assert shell.runtime.amdx_context_widget.reference == at('10:45')
        after = rows(connection)
        assert after['amdx_claim'] == before['amdx_claim']
        assert after['amdx_run_binding'] == before['amdx_run_binding']
        assert after['amdx_run_capture'][:-1] == before['amdx_run_capture']
        packet = json.loads(connection.execute('SELECT payload_json FROM amdx_run_capture ORDER BY sequence DESC LIMIT 1').fetchone()[0])
        assert packet['projection']['reference'].startswith('2026-10-09T10:45')
        shell._capture_live_observation('Away 10:00–10:45; not observed. Stand down.')
        last = shell.active_trading_run.evidence[-1]
        assert last.market_time_context['captured_at'].startswith('2026-10-09T10:45')
        assert abs((datetime.now(timezone.utc) - datetime.fromisoformat(last.created_at)).total_seconds()) < 20
        saved = deepcopy(shell.active_trading_run)
        review = shell.runtime.post_market_review_widget
        review.load_state(saved, shell.runtime.tda_station_runner_widget.session)
        texts = [review.live_changes_list.item(i).text() for i in range(review.live_changes_list.count())]
        assert any('administrative' in text and 'Recorded:' in text for text in texts)
    finally:
        close(connection, window)
    connection, window = open_demo(path)
    try:
        restored = window.trade_plan_widget.trading_day_shell_widget.active_trading_run
        assert restored == saved
        assert restored.evidence[0] == original.evidence[0]
        assert restored.replay_qualification_withheld
    finally:
        close(connection, window)


@pytest.mark.parametrize('value', ['08:59', '18:00'])
def test_invalid_progression_changes_nothing(cockpit, value):
    _, shell, connection = cockpit
    before = rows(connection)
    with pytest.raises(ValueError):
        shell.set_replay_reference(at(value))
    assert rows(connection) == before


def test_noop_retry_and_drift(cockpit):
    _, shell, connection = cockpit
    original = deepcopy(shell.active_trading_run)
    before = rows(connection)
    shell.set_replay_reference(at('09:15'))
    assert rows(connection) == before
    result = advance_replay_reference(shell.calendar_repository, original, at('10:05'), operation_id='manual-clock-1')
    once = rows(connection)
    assert advance_replay_reference(shell.calendar_repository, original, at('10:05'), operation_id='manual-clock-1') == result
    assert rows(connection) == once
    with pytest.raises(ValueError, match='different input'):
        advance_replay_reference(shell.calendar_repository, original, at('10:15'), operation_id='manual-clock-1')
    with pytest.raises(ValueError, match='changed'):
        advance_replay_reference(shell.calendar_repository, original, at('10:15'))


def test_atomic_rollback(cockpit):
    _, shell, connection = cockpit
    before = rows(connection)
    connection.execute("CREATE TEMP TRIGGER fail_replay BEFORE INSERT ON amdx_run_capture BEGIN SELECT RAISE(ABORT, 'test failure'); END")
    with pytest.raises(ValueError, match='test failure'):
        shell.set_replay_reference(at('10:15'))
    assert rows(connection) == before
    assert shell.active_trading_run.market_time_context['captured_at'].startswith('2026-10-09T09:15')


def test_stale_write_rejected_under_transaction(cockpit, monkeypatch):
    _, shell, connection = cockpit
    calendar = shell.calendar_repository.run_calendar
    actual = calendar.consume
    def racing(prepared, updated, **kwargs):
        other = TradingSessionRunRepository(connection).get_by_id(updated.id)
        other.add_observation('Another writer')
        TradingSessionRunRepository(connection).save(other)
        return actual(prepared, updated, **kwargs)
    monkeypatch.setattr(calendar, 'consume', racing)
    with pytest.raises(ValueError):
        shell.set_replay_reference(at('10:15'))
    saved = TradingSessionRunRepository(connection).get_by_id(shell.active_trading_run.id)
    assert saved.evidence[-1].note == 'Another writer'
    assert not saved.replay_qualification_withheld


def test_qualification_withheld_without_erasing_assessments(cockpit):
    _, shell, _ = cockpit
    run = shell.active_trading_run
    silver = build_default_trade_plan().playbook_by_id('silver-bullet')
    run.sync_playbook_candidates([silver.to_snapshot()])
    candidate = run.playbook_candidate('silver-bullet')
    clear_all_non_time_gates(run, candidate.id)
    assert shell._save_and_reload(run)
    retained = deepcopy(candidate.entry_condition_states)
    shell.set_replay_reference(at('10:15'))
    run = shell.active_trading_run
    assert run.candidate_authorization(candidate.id).status is AuthorizationStatus.BLOCKED
    assert run.setup_candidate_by_id(candidate.id).entry_condition_states == retained
    assert 'not revalidated' in shell.runtime.live_watch_widget.authorization_summary_label.text()
    assert 'authorization withheld' in shell.runtime.live_watch_widget.readiness_status_label.text()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    cards = '\n'.join(label.text() for label in shell.runtime.live_watch_widget.findChildren(QLabel))
    assert 'Retained assessment' in cards
    assert 'criteria currently met' not in cards
    assert 'Setup readiness: 3/3' not in cards
    assert 'not revalidated' in shell.runtime.live_watch_widget.situation_candidates_label.text().lower()
    # Other environments do not inherit Replay's administrative hold.
    run.environment = RunEnvironment.FORWARD_TEST
    assert run.candidate_authorization(candidate.id).status is AuthorizationStatus.AUTHORIZED


def test_dialog_rejects_then_applies_without_touching_drafts(cockpit):
    _, shell, _ = cockpit
    dialog = ReplayReferenceDialog(shell)
    dialog.time_input.setText('2026-10-09 09:00')
    dialog.apply()
    assert 'backward' in dialog.status.text()
    dialog.time_input.setText('2026-10-09 10:15')
    dialog.apply()
    assert dialog.result() == dialog.DialogCode.Accepted
    dialog.deleteLater()


def test_pinned_context_and_pressed_gesture(cockpit):
    _, shell, _ = cockpit
    pane = shell.runtime.amdx_context_widget
    pane.select_quarter(1, 0)
    target, reference = pane.target, pane._shared_target_reference
    pane._begin_gesture()
    shell.set_replay_reference(at('10:45'))
    assert pane.target.cycle == target.cycle
    assert pane._shared_target_reference == reference
    assert pane._gesture_cancelled
    from ict_cockpit.analysis.amdx import Role
    assert not pane.choose(Role.A)
    assert shell.active_trading_run.market_time_context['captured_at'].startswith('2026-10-09T10:45')


@pytest.mark.parametrize('text', ['garbage', '2026-03-08 02:30', '2026-11-01 01:30', '2026-10-09T10:00-04:00'])
def test_local_editor_invalid_or_ambiguous(text):
    with pytest.raises(ValueError):
        resolve_new_york(text)


def test_dst_occurrences_and_midnight_boundaries():
    first = resolve_new_york('2026-11-01 01:30', 0)
    second = resolve_new_york('2026-11-01 01:30', 1)
    assert (second.astimezone(timezone.utc) - first.astimezone(timezone.utc)).total_seconds() == 3600
    assert validate_progression(first, first, second) == second
    with pytest.raises(ValueError, match='backward'):
        validate_progression(first, second, first)
    original = resolve_new_york('2026-10-08 19:00')
    assert validate_progression(original, original, at('00:01')) == at('00:01')
    assert validate_progression(original, original, at('17:59')) == at('17:59')
    with pytest.raises(ValueError, match='Another Trading Day'):
        validate_progression(original, original, at('18:00'))
    with pytest.raises(ValueError, match='timezone'):
        validate_progression(original, original, datetime(2026, 10, 9, 10))


@pytest.mark.parametrize('environment', [RunEnvironment.LIVE, RunEnvironment.FORWARD_TEST, RunEnvironment.HISTORICAL_BACKTEST])
def test_other_environments_rejected(cockpit, environment):
    _, shell, connection = cockpit
    run = shell.active_trading_run
    run.environment = environment
    TradingSessionRunRepository(connection).save(run)
    before = rows(connection)
    with pytest.raises(ValueError, match='active Replay'):
        shell.set_replay_reference(at('10:15'))
    assert rows(connection) == before


def test_open_study_draft_keeps_its_basis(cockpit):
    window, shell, _ = cockpit
    shell.runtime.apply_transition('finish-tda', override_incomplete=True)
    shell._toggle_contextual_study_find()
    dock = window.contextual_study_find_dock
    dock.observation_input.setPlainText('Unfinished earlier observation')
    basis = deepcopy(dock.basis)
    identity = window.study_find_widget.current_study_find_id
    shell.set_replay_reference(at('10:45'))
    assert dock.basis == basis
    assert window.study_find_widget.current_study_find_id == identity
    assert dock.observation_input.toPlainText() == 'Unfinished earlier observation'
    assert '90m Q4' in shell.runtime.amdx_context_widget.target_label.text()
    dock.dismiss()


def test_completed_and_changed_original_are_rejected(cockpit):
    _, shell, connection = cockpit
    repository = TradingSessionRunRepository(connection)
    original = deepcopy(shell.active_trading_run)
    shell.active_trading_run.market_context_snapshot['reference_market_time'] = at('08:00').isoformat()
    repository.save(shell.active_trading_run)
    before = rows(connection)
    with pytest.raises(ValueError, match='Original Replay launch context'):
        shell.set_replay_reference(at('10:15'))
    assert rows(connection) == before
    original.conclude('Synthetic complete')
    repository.save(original)
    shell.active_trading_run = original
    before = rows(connection)
    with pytest.raises(ValueError, match='active Replay'):
        shell.set_replay_reference(at('10:15'))
    assert rows(connection) == before


def test_later_advancement_keeps_receipts_and_hold(cockpit):
    _, shell, connection = cockpit
    first = deepcopy(shell.set_replay_reference(at('10:15')))
    second = shell.set_replay_reference(at('11:15'))
    assert second.evidence[:-1] == first.evidence
    assert len(second.evidence) == 2
    assert second.replay_qualification_withheld
    assert second.current_thesis_state == first.current_thesis_state
    assert not connection.execute('SELECT * FROM amdx_claim').fetchall()
    assert 'withheld' in shell.runtime.watch_quiet_composition.safety.cells['authorization'][1].text().lower()
