from datetime import datetime
import sqlite3

import pytest
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.amdx import Profile, Role, XSubtype
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, build_market_time_context
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.amdx_captured_stack_dialog import AMDXCapturedStackDialog
from ict_cockpit.gui.main_window import MainWindow


REFERENCE = datetime(2026, 10, 9, 9, 15, tzinfo=MARKET_TIMEZONE)


def dispose(window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()


@pytest.fixture
def cockpit(tmp_path):
    connection = open_application_database(tmp_path / 'shared.db')
    window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    shell = window.trade_plan_widget.trading_day_shell_widget
    shell.run_environment = RunEnvironment.REPLAY
    shell.run_market_timestamp = REFERENCE
    assert shell.start_trading_run(), shell.summary_label.text()
    window.resize(1344, 756)
    window.show()
    QApplication.processEvents()
    yield window, shell, connection
    dispose(window)
    connection.close()


def records(connection):
    return tuple(connection.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0] for name in
        ('amdx_catalog_command', 'amdx_run_capture', 'amdx_run_calendar_command'))


def lab_edit(window, role, *, reference=REFERENCE, channel='Expected', row=2, column=3):
    lab = window.amdx_catalog_widget
    window.tabs.setCurrentWidget(lab)
    lab.channel_selector.setCurrentText(channel)
    lab.set_reference(reference.isoformat())
    lab.select_cell(row, column)
    QTest.mouseClick(lab.phase_buttons[role], Qt.MouseButton.LeftButton)
    assert 'Recorded' in lab.status_label.text(), lab.status_label.text()
    return lab


def test_normal_launch_binds_one_visible_instrument_calendar_and_captures_absence(cockpit):
    window, shell, connection = cockpit
    lab = window.amdx_catalog_widget
    pane = shell.runtime.amdx_context_widget
    assert not lab.adoption_required
    assert lab.catalog_selector.isHidden() and lab.new_button.isHidden()
    assert pane.binding['instrument'] == 'MNQ'
    assert pane.shared_projection.run_id == lab.catalog.owner_id
    assert records(connection) == (0, 1, 1)
    assert 'MNQ' in pane.higher_label.text()
    assert shell.runtime.qt_context_widget.isHidden()
    captured = shell.calendar_repository.run_calendar.get_result(pane.binding['launch_operation_id']).capture
    assert len(captured.projection.cycles) == 7
    assert all(row.claim is None for row in captured.projection.cycles)


def test_historical_lab_backfill_and_current_working_stack_share_owner_without_borrowing(cockpit):
    window, shell, connection = cockpit
    run_id = shell.active_trading_run.id
    lab = lab_edit(window, Role.D, reference=REFERENCE.replace(year=1985), channel='Observed')
    owner = lab.catalog.owner_id
    assert records(connection) == (1, 1, 1)
    lab_edit(window, Role.D)
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    pane = shell.runtime.amdx_context_widget
    assert 'Yearly Q4 X(?) · AMDX' in pane.higher_label.text()
    assert records(connection) == (2, 1, 1)
    assert len(shell.calendar_repository.catalog.history(lab.catalog.id).claims) == 2
    assert pane.shared_projection.run_id == owner
    assert connection.execute('SELECT COUNT(*) FROM trading_session_run').fetchone()[0] == 1
    assert shell.active_trading_run.id == run_id
    assert all(row.claim is None for row in shell.calendar_repository.master.load_stack('MNQ',
        reference=REFERENCE, channel='Observed').projection.cycles)


def test_watch_real_mouse_entry_and_direct_x_subtype_capture_same_calendar(cockpit):
    window, shell, connection = cockpit
    pane = shell.runtime.amdx_context_widget
    assert shell.runtime.apply_transition('finish-tda', override_incomplete=True)
    assert shell.runtime.live_watch_widget.qt_summary_label.isHidden()
    QTest.mouseClick(pane.phase_buttons[Role.M], Qt.MouseButton.LeftButton)
    assert pane.table.item(1, 4).text() == 'XAMD'
    assert records(connection)[0] == 1
    pane.select_quarter(1, 0)
    QTest.mouseClick(pane.subtype_buttons[XSubtype.REVERSAL], Qt.MouseButton.LeftButton)
    claim = shell.calendar_repository.catalog.history(window.amdx_catalog_widget.catalog.id).claims[-1]
    assert claim.inference.roles[0].subtype is XSubtype.REVERSAL
    assert pane.table.item(1, 4).text() == 'XAMD'
    assert records(connection)[0] == 2
    assert shell.calendar_repository.get_history(shell.active_trading_run.id).claims == ()


def test_full_stack_from_watch_captures_large_thesis_edit_then_navigation_returns_to_study(cockpit):
    window, shell, connection = cockpit
    pane = shell.runtime.amdx_context_widget
    before = records(connection)
    QTest.mouseClick(pane.full_stack_button, Qt.MouseButton.LeftButton)
    lab = window.amdx_catalog_widget
    assert window.tabs.currentWidget() is lab
    assert lab.run_scope[0] == shell.active_trading_run.id
    assert lab.channel_selector.currentText() == 'Expected'
    lab.select_cell(2, 3)
    QTest.mouseClick(lab.phase_buttons[Role.D], Qt.MouseButton.LeftButton)
    assert records(connection) == tuple(n+1 for n in before)
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    assert 'AMDX' in pane.higher_label.text()
    window.tabs.setCurrentWidget(lab)
    lab.set_reference(REFERENCE.replace(year=1985).isoformat())
    assert lab.run_scope is None


def test_live_action_captures_displayed_basis_and_failure_preserves_typed_note(cockpit):
    window, shell, connection = cockpit
    lab_edit(window, Role.D)
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    assert shell.runtime.apply_transition('finish-tda', override_incomplete=True)
    watch = shell.runtime.live_watch_widget
    watch.observation_input.setText('decision at displayed stack')
    watch.capture_observation_button.click()
    assert shell.active_trading_run.evidence[-1].note == 'decision at displayed stack'
    before = records(connection)
    connection.execute("CREATE TRIGGER fail_capture BEFORE INSERT ON amdx_run_capture BEGIN SELECT RAISE(ABORT,'injected'); END")
    watch.observation_input.setText('keep this failed note')
    watch.capture_observation_button.click()
    assert watch.observation_input.text() == 'keep this failed note'
    assert records(connection) == before
    assert len(shell.active_trading_run.evidence) == 1
    pane = shell.runtime.amdx_context_widget
    assert 'Action not recorded' in pane.status_label.text()
    assert not pane.phase_buttons[Role.M].isEnabled()
    connection.execute('DROP TRIGGER fail_capture')
    pane.reload_button.click()
    watch.capture_observation_button.click()
    assert len(shell.active_trading_run.evidence) == 2
    assert watch.observation_input.text() == ''


@pytest.mark.parametrize('change', ['head', 'higher-head', 'tab', 'mode'])
def test_pressed_entry_cannot_follow_changed_scope_or_overwrite_newer_head(cockpit, change):
    window, shell, connection = cockpit
    pane = shell.runtime.amdx_context_widget
    button = pane.phase_buttons[Role.M]
    if change != 'higher-head':
        QTest.mousePress(button, Qt.MouseButton.LeftButton)
    if change in ('head', 'higher-head'):
        target = shell.calendar_repository.master.prepare_target('MNQ', reference=REFERENCE,
            level='session' if change == 'head' else 'year', position=3)
        shell.calendar_repository.catalog.revise(target.target, command_id='outside', role=Role.D,
            recorded_at=datetime.now().astimezone(), anchor_id='outside-anchor', source_ref='another writer')
    elif change == 'tab':
        window.tabs.setCurrentWidget(window.amdx_catalog_widget)
        window.tabs.setCurrentWidget(window.trade_plan_widget)
    else:
        shell.runtime.apply_transition('finish-tda', override_incomplete=True)
    if change == 'higher-head':
        QTest.mousePress(button, Qt.MouseButton.LeftButton)
    before = records(connection)
    QTest.mouseRelease(button, Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    assert records(connection) == before
    if change in ('head', 'higher-head'):
        assert 'Reload AMDX' in pane.status_label.text()
        shell._refresh_market_time_display()
        assert not pane.phase_buttons[Role.M].isEnabled()
        pane.reload_button.click()
        assert 'AMDX' in (pane.table.item(1, 4).text() if change == 'head' else pane.higher_label.text())


def test_pinned_input_retains_displayed_reference_across_clock_change(cockpit):
    window, shell, connection = cockpit
    pane = shell.runtime.amdx_context_widget
    pane.select_quarter(1, 2)
    original_cycle = pane.target.cycle
    shell.active_trading_run.market_time_context = build_market_time_context(
        REFERENCE.replace(hour=11), source='Historical Reference').to_dict()
    shell._refresh_market_time_display()
    assert pane.shared_projection.reference == REFERENCE
    QTest.mouseClick(pane.phase_buttons[Role.M], Qt.MouseButton.LeftButton)
    assert pane.target.cycle == original_cycle
    assert 'Recorded' in pane.status_label.text()
    claims = shell.calendar_repository.catalog.history(window.amdx_catalog_widget.catalog.id).claims
    assert claims[-1].market_reference == REFERENCE


def test_unavailable_binding_blocks_run_action_without_legacy_fallback(cockpit, monkeypatch):
    window, shell, connection = cockpit
    assert shell.runtime.apply_transition('finish-tda', override_incomplete=True)
    pane = shell.runtime.amdx_context_widget
    before = records(connection)
    def unavailable(*args):
        raise ValueError('damaged source')
    monkeypatch.setattr(shell.calendar_repository.run_calendar, 'get_binding', unavailable)
    shell._refresh_market_time_display()
    watch = shell.runtime.live_watch_widget
    watch.observation_input.setText('must stay unsaved')
    watch.capture_observation_button.click()
    assert records(connection) == before
    assert shell.active_trading_run.evidence == []
    assert watch.observation_input.text() == 'must stay unsaved'


def test_review_and_full_stack_keep_original_launch_absence_after_calendar_correction(cockpit):
    window, shell, connection = cockpit
    pane = shell.runtime.amdx_context_widget
    launch = shell.calendar_repository.run_calendar.get_result(pane.binding['launch_operation_id']).capture
    lab_edit(window, Role.D)
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    assert shell.runtime.apply_transition('finish-tda', override_incomplete=True)
    assert shell.runtime.apply_transition('live-finish')
    assert pane.launch_capture == launch
    assert 'Unresolved' in pane.higher_label.text()
    assert 'Working context captured at run launch' in pane.captured_label.text()
    before = records(connection)
    dialog = AMDXCapturedStackDialog(launch, shell.calendar_repository, window)
    try:
        assert dialog.pane.table.rowCount() == 7
        assert dialog.pane.table.item(2, 5).text() == 'Unresolved'
        dialog.pane.select_cell(2, 3)
        assert not dialog.pane.phase_buttons[Role.D].isEnabled()
        dialog.pane.choose(Role.D)
        assert records(connection) == before
    finally:
        dialog.close()
        dialog.deleteLater()


def test_native_reopen_preserves_binding_and_current_calendar_without_relaunch(cockpit):
    window, shell, connection = cockpit
    lab_edit(window, Role.D)
    original_id = shell.active_trading_run.id
    binding = shell.calendar_repository.run_calendar.get_binding(original_id)
    before = records(connection)
    reopened = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    try:
        resumed = reopened.trade_plan_widget.trading_day_shell_widget
        assert resumed.active_trading_run.id == original_id
        assert resumed.runtime.amdx_context_widget.binding == binding
        assert 'AMDX' in resumed.runtime.amdx_context_widget.higher_label.text()
        assert records(connection) == before
    finally:
        dispose(reopened)


def test_launch_failure_saves_no_run_and_keeps_retry_available(tmp_path):
    connection = open_application_database(tmp_path/'failed.db')
    window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        shell.run_environment = RunEnvironment.REPLAY
        shell.run_market_timestamp = REFERENCE
        connection.execute("CREATE TRIGGER fail_launch BEFORE INSERT ON amdx_run_capture BEGIN SELECT RAISE(ABORT,'injected'); END")
        assert not shell.start_trading_run()
        assert shell.active_trading_run is None
        assert connection.execute('SELECT COUNT(*) FROM trading_session_run').fetchone()[0] == 0
        assert not shell.start_run_button.isHidden()
        connection.execute('DROP TRIGGER fail_launch')
        assert shell.start_trading_run()
        assert records(connection) == (0, 1, 1)
    finally:
        dispose(window)
        connection.close()
