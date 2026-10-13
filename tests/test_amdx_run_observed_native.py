from datetime import timedelta
import sqlite3

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.amdx import Role, XSubtype
from ict_cockpit.analysis.market_time import build_market_time_context
from ict_cockpit.gui.amdx_captured_stack_dialog import AMDXCapturedStackDialog
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.database.study_find_repository import StudyFindRepository
from test_amdx_shared_native import cockpit, dispose, REFERENCE


def review(shell):
    assert shell.runtime.apply_transition('finish-tda', override_incomplete=True)
    assert shell.runtime.apply_transition('live-finish')
    return shell.runtime.amdx_context_widget


def count(connection):
    return tuple(connection.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for name in
        ('amdx_catalog_command','amdx_run_observed_command','amdx_claim','amdx_comparison','amdx_run_capture'))


def test_real_review_entry_is_same_calendar_and_immutable_run_receipt_without_extra_save(cockpit):
    window,shell,connection=cockpit
    pane=review(shell)
    assert 'Maintained Observed AMDX' in pane.target_label.text()
    assert shell.runtime.post_market_review_widget.qt_review_frame.isHidden()
    snapshots=shell.runtime.post_market_review_widget.tda_snapshot_list
    assert not any(snapshots.item(i).text().startswith('QT / AMDX Stack') for i in range(snapshots.count()))
    pane.select_quarter(1,2)
    before=count(connection)
    QTest.mouseClick(pane.phase_buttons[Role.M],Qt.MouseButton.LeftButton)
    assert 'Recorded in maintained Observed' in pane.status_label.text()
    assert pane.table.item(1,4).text()=='XAMD'
    assert count(connection)==(before[0]+1,before[1]+1,before[2],before[3],before[4])
    lab=window.amdx_catalog_widget
    window.tabs.setCurrentWidget(lab)
    lab.leave_run_scope()
    lab.set_reference(REFERENCE.isoformat())
    assert lab.channel_selector.currentText()=='Observed'
    assert lab.table.item(6,5).text()=='XAMD'
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    assert not pane.assessment_button.isHidden()


def test_one_click_subtype_and_four_session_navigation_use_observed_owner(cockpit):
    window,shell,connection=cockpit
    pane=review(shell)
    pane.select_quarter(1,0)
    QTest.mouseClick(pane.subtype_buttons[XSubtype.REVERSAL],Qt.MouseButton.LeftButton)
    assert pane.table.item(1,4).text()=='XAMD'
    for index in (0,1,2,3):
        before=count(connection)
        pane.session_selector.setCurrentIndex(index)
        assert count(connection)==before
        pane.select_quarter(1,2)
        QTest.mouseClick(pane.phase_buttons[Role.M],Qt.MouseButton.LeftButton)
        assert pane.table.item(1,4).text()=='XAMD'


def test_failure_keeps_calendar_and_assessment_unchanged_until_explicit_reload(cockpit):
    window,shell,connection=cockpit
    pane=review(shell)
    pane.select_quarter(1,2)
    before=count(connection)
    connection.execute("CREATE TRIGGER fail_assessment BEFORE INSERT ON amdx_run_observed_command BEGIN SELECT RAISE(ABORT,'injected'); END")
    QTest.mouseClick(pane.phase_buttons[Role.M],Qt.MouseButton.LeftButton)
    assert count(connection)==before
    assert 'Not recorded' in pane.status_label.text()
    shell._refresh_market_time_display()
    assert not pane.phase_buttons[Role.M].isEnabled()
    assert 'Reload AMDX' in pane.status_label.text()
    connection.execute('DROP TRIGGER fail_assessment')
    pane.reload_button.click()
    QTest.mouseClick(pane.phase_buttons[Role.M],Qt.MouseButton.LeftButton)
    assert pane.table.item(1,4).text()=='XAMD'


@pytest.mark.parametrize('change',['lab-head','tab','run-metadata'])
def test_gesture_cannot_use_changed_source_or_surface(cockpit,change):
    window,shell,connection=cockpit
    pane=review(shell)
    pane.select_quarter(1,2)
    button=pane.phase_buttons[Role.M]
    QTest.mousePress(button,Qt.MouseButton.LeftButton)
    if change=='tab':
        window.tabs.setCurrentWidget(window.amdx_catalog_widget)
        window.tabs.setCurrentWidget(window.trade_plan_widget)
    elif change=='lab-head':
        target=pane._observed_prepared.target.target
        shell.calendar_repository.catalog.revise(target,command_id='outside',role=Role.D,
            anchor_id='outside-a',source_ref='Lab correction',recorded_at=pane.launch_capture.recorded_at)
    else:
        shell.active_trading_run.review_takeaway='another writer'
        window.trading_session_run_repository.save(shell.active_trading_run)
    before=count(connection)
    QTest.mouseRelease(button,Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    assert count(connection)==before


def test_original_assessment_is_read_only_after_lab_correction_and_restart(cockpit):
    window,shell,connection=cockpit
    pane=review(shell)
    pane.select_quarter(1,2)
    pane.phase_buttons[Role.M].click()
    original=pane.observed_capture
    lab=window.amdx_catalog_widget
    window.tabs.setCurrentWidget(lab)
    lab.leave_run_scope()
    lab.set_reference(REFERENCE.isoformat())
    lab.select_cell(6,3)
    lab.phase_buttons[Role.D].click()
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    shell._refresh_market_time_display()
    assert pane.table.item(1,4).text()=='AMDX'
    assert pane.observed_capture==original
    before=count(connection)
    dialog=AMDXCapturedStackDialog(original,shell.calendar_repository,window)
    try:
        assert dialog.pane.channel_selector.currentText()=='Observed'
        assert dialog.pane.table.item(6,5).text()=='XAMD'
        dialog.pane.select_cell(6,3)
        assert not dialog.pane.phase_buttons[Role.M].isEnabled()
    finally:
        dialog.close();dialog.deleteLater()
    reopened=MainWindow(TDARepository(connection),StudyFindRepository(connection))
    try:
        restored=reopened.trade_plan_widget.trading_day_shell_widget.runtime.amdx_context_widget
        assert restored.observed_capture==original
        assert restored.table.item(1,4).text()=='AMDX'
        assert count(connection)==before
    finally:
        dispose(reopened)


def test_clock_rollover_does_not_change_review_day_or_record_phase(cockpit):
    window,shell,connection=cockpit
    pane=review(shell)
    pane.select_quarter(1,2)
    pane.phase_buttons[Role.M].click()
    before=count(connection)
    shell.active_trading_run.market_time_context=build_market_time_context(REFERENCE+timedelta(days=1),source='Historical Reference').to_dict()
    window.save_trading_session_run(shell.active_trading_run)
    shell._refresh_market_time_display()
    assert pane.review_day_label=='2026-10-09'
    assert pane.table.item(1,4).text()=='XAMD'
    assert count(connection)==before
    reopened=MainWindow(TDARepository(connection),StudyFindRepository(connection))
    try:
        restored=reopened.trade_plan_widget.trading_day_shell_widget.runtime.amdx_context_widget
        assert restored.review_day_label=='2026-10-09'
        assert restored.session_selector.currentText()=='NYAM'
        assert restored.table.item(1,4).text()=='XAMD'
    finally:
        dispose(reopened)
