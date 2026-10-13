from datetime import datetime
import json
import sqlite3

import pytest
from PySide6.QtCore import QSettings, QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.amdx import Role, XSubtype
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.amdx_review_stack_dialog import AMDXReviewStackWidget, AMDXReviewStackDialog
from ict_cockpit.gui.amdx_captured_stack_dialog import AMDXCapturedStackDialog
from ict_cockpit.gui.main_window import MainWindow
from test_amdx_shared_native import dispose
from test_amdx_run_observed_repository import count
from test_amdx_higher_review import BOUNDARY


@pytest.fixture
def cockpit(tmp_path):
    connection=open_application_database(tmp_path/'higher.db')
    window=MainWindow(TDARepository(connection),StudyFindRepository(connection))
    for timer in window.findChildren(QTimer):timer.stop()
    shell=window.trade_plan_widget.trading_day_shell_widget
    shell.run_environment=RunEnvironment.REPLAY
    shell.run_market_timestamp=BOUNDARY
    assert shell.start_trading_run(),shell.summary_label.text()
    assert shell.runtime.apply_transition('finish-tda',override_incomplete=True)
    assert shell.runtime.apply_transition('live-finish')
    window.tabs.setCurrentWidget(window.trade_plan_widget)
    window.show()
    yield window,shell,connection
    dispose(window)
    connection.close()


def widget(shell):
    pane=AMDXReviewStackWidget(shell.calendar_repository,shell.active_trading_run.id)
    pane.resize(1344,756)
    pane.show()
    QApplication.processEvents()
    return pane


def click_x(pane,subtype):
    assert pane.subtype_buttons[subtype].isEnabled(),pane.status_label.text()
    QTest.mouseClick(pane.subtype_buttons[subtype],Qt.MouseButton.LeftButton)
    assert 'Recorded' in pane.status_label.text(),pane.status_label.text()


def test_mouse_entry_two_contexts_and_intraday_selection_stays_put(cockpit):
    window,shell,c=cockpit
    quiet=shell.runtime.amdx_context_widget
    quiet.session_selector.setCurrentText('London')
    previous=quiet.target
    assert not quiet.review_stack_button.isHidden()
    pane=widget(shell)
    try:
        assert pane.orientation_selector.count()==2
        assert not pane.orientation_selector.isHidden()
        assert pane.reference().second==37
        assert pane.target.cycle.layer=='year'
        assert pane._position==1
        click_x(pane,XSubtype.CONTINUATION)
        assert pane.table.item(2,5).text()=='XAMD'
        before=count(c)
        pane.orientation_selector.setCurrentIndex(1)
        assert count(c)==before
        assert pane._position==4
        assert pane.table.item(2,5).text()=='Unresolved'
        assert pane.table.item(0,5).text()=='Unresolved'
        click_x(pane,XSubtype.REVERSAL)
        assert pane.table.item(2,5).text()=='AMDX'
        pane.orientation_selector.setCurrentIndex(0)
        assert pane.table.item(2,5).text()=='XAMD'
        assert quiet.target==previous
        assert shell.calendar_repository.run_observed.latest(shell.active_trading_run.id).packet['request']['scope_proof']['selected_reference'].startswith('2026-12-31')
    finally:pane.close()


def test_inactive_month_and_week_inspection_do_not_create_an_active_quarter(cockpit):
    _,shell,c=cockpit
    pane=widget(shell)
    try:
        before=count(c)
        pane.select_cell(3,0)
        assert pane.target is None
        assert not pane.phase_buttons[Role.A].isEnabled()
        assert pane.projection.cycles[3].context.state.value=='Unassigned'
        pane.select_cell(4,0)
        assert pane.target is None
        assert pane.projection.cycles[4].context.state.value=='Distortion'
        pane.select_cell(4,1)
        assert pane.phase_buttons[Role.A].isEnabled()
        pane.select_cell(6,1)
        assert pane.target.cycle.layer=='week'
        assert count(c)==before
    finally:pane.close()


def test_orientation_press_race_cancels_without_recording(cockpit):
    _,shell,c=cockpit
    pane=widget(shell)
    try:
        before=count(c)
        button=pane.subtype_buttons[XSubtype.CONTINUATION]
        QTest.mousePress(button,Qt.MouseButton.LeftButton)
        pane.orientation_selector.setCurrentIndex(1)
        QTest.mouseRelease(button,Qt.MouseButton.LeftButton)
        assert count(c)==before
        assert 'cancelled' in pane.status_label.text()
    finally:pane.close()


def test_stale_source_stays_disabled_until_deliberate_reload(cockpit):
    _,shell,c=cockpit
    pane=widget(shell)
    try:
        target=pane.target
        shell.calendar_repository.catalog.revise(target,command_id='outside',recorded_at=datetime.now().astimezone(),
            role=Role.A,anchor_id='outside-anchor',source_ref='synthetic correction')
        before=count(c)
        QTest.mouseClick(pane.subtype_buttons[XSubtype.CONTINUATION],Qt.MouseButton.LeftButton)
        assert count(c)==before
        assert 'not recorded' in pane.status_label.text()
        pane.orientation_selector.setCurrentIndex(1)
        assert not pane.subtype_buttons[XSubtype.REVERSAL].isEnabled()
        pane.reload_button.click()
        click_x(pane,XSubtype.REVERSAL)
    finally:pane.close()


def test_failed_atomic_receipt_preserves_profile_and_requires_reload(cockpit):
    _,shell,c=cockpit
    pane=widget(shell)
    try:
        click_x(pane,XSubtype.CONTINUATION)
        before=count(c)
        c.execute("CREATE TRIGGER fail_higher BEFORE INSERT ON amdx_run_observed_command BEGIN SELECT RAISE(ABORT,'scope injection'); END")
        QTest.mouseClick(pane.subtype_buttons[XSubtype.REVERSAL],Qt.MouseButton.LeftButton)
        assert count(c)==before
        assert pane.table.item(2,1).text().endswith('X(C) · entered')
        assert not pane.subtype_buttons[XSubtype.REVERSAL].isEnabled()
        c.execute('DROP TRIGGER fail_higher')
        pane.reload_button.click()
        click_x(pane,XSubtype.REVERSAL)
    finally:pane.close()


def test_reopen_restores_per_run_scope_without_overwriting_lab_preferences(cockpit):
    window,shell,c=cockpit
    lab=window.amdx_catalog_widget
    prior=lab.settings.value('catalog-view-v1')
    pane=widget(shell)
    pane.orientation_selector.setCurrentIndex(1)
    pane.select_cell(0,4)
    pane.close()
    restored=widget(shell)
    try:
        assert restored.orientation_selector.currentIndex()==1
        assert restored._level=='cycle_16y' and restored._position==4
        assert lab.settings.value('catalog-view-v1')==prior
    finally:restored.close()


def test_captured_assessment_retains_proof_with_disabled_input(cockpit):
    _,shell,c=cockpit
    pane=widget(shell)
    try:
        pane.orientation_selector.setCurrentIndex(1)
        click_x(pane,XSubtype.REVERSAL)
        receipt=shell.calendar_repository.run_observed.latest(shell.active_trading_run.id)
        captured=AMDXCapturedStackDialog(receipt,shell.calendar_repository)
        assert not captured.pane.subtype_buttons[XSubtype.REVERSAL].isEnabled()
        assert captured.pane.projection.reference.year==2026
        assert any('Reviewed Trading Day 2027-01-01' in label.text() for label in captured.findChildren(__import__('PySide6.QtWidgets',fromlist=['QLabel']).QLabel))
        captured.close()
    finally:pane.close()


def test_operation_change_cancels_pressed_choice(cockpit):
    _,shell,c=cockpit
    allowed=[True]
    pane=AMDXReviewStackWidget(shell.calendar_repository,shell.active_trading_run.id,allowed=lambda:allowed[0])
    pane.show()
    try:
        before=count(c)
        button=pane.subtype_buttons[XSubtype.CONTINUATION]
        QTest.mousePress(button,Qt.MouseButton.LeftButton)
        allowed[0]=False
        QTest.mouseRelease(button,Qt.MouseButton.LeftButton)
        assert count(c)==before
        assert 'cancelled' in pane.status_label.text()
    finally:pane.close()


def test_invalid_saved_navigation_disables_input_until_explicit_reload(cockpit):
    _,shell,c=cockpit
    pane=widget(shell)
    settings=pane.settings
    key=pane._key()
    pane.close()
    settings.setValue(key,'{"original_reference":"different"}')
    settings.sync()
    reopened=widget(shell)
    try:
        assert reopened.reference()==BOUNDARY
        assert 'Saved Review navigation unavailable' in reopened.status_label.text()
        assert not reopened.subtype_buttons[XSubtype.CONTINUATION].isEnabled()
        reopened.reload_button.click()
        click_x(reopened,XSubtype.CONTINUATION)
    finally:reopened.close()


def test_ordinary_day_has_one_orientation_without_redundant_control(cockpit):
    _,shell,c=cockpit
    from ict_cockpit.analysis.trading_session_run import TradingRun
    repo=shell.calendar_repository
    run=TradingRun(shell.active_trading_run.trading_day_id,'ordinary synthetic day',shell.active_trading_run.process_session_id)
    reference=datetime(2026,10,9,9,15,tzinfo=MARKET_TIMEZONE)
    run.market_context_snapshot={'reference_market_time':reference.isoformat()}
    repo.run_calendar.launch(repo.run_calendar.prepare_launch(run,instrument='MNQ',reference=reference),
        operation_id='ordinary-launch',capture_id='ordinary-capture',recorded_at=datetime.now().astimezone())
    pane=AMDXReviewStackWidget(repo,run.id)
    try:
        assert pane.orientation_selector.count()==1
        assert pane.orientation_selector.isHidden()
        assert pane.reference()==reference
    finally:pane.close()


def test_actual_review_doorway_opens_modal_entry_and_refreshes_quiet_assessment(cockpit):
    window,shell,c=cockpit
    failures=[]
    def inspect():
        dialog=window.findChild(AMDXReviewStackDialog)
        try:
            assert dialog is not None
            assert dialog.isVisible()
            click_x(dialog.pane,XSubtype.CONTINUATION)
        except Exception as error:failures.append(error)
        finally:
            if dialog:dialog.reject()
    QTimer.singleShot(0,inspect)
    QTest.mouseClick(shell.runtime.amdx_context_widget.review_stack_button,Qt.MouseButton.LeftButton)
    assert not failures,failures
    quiet=shell.runtime.amdx_context_widget
    assert quiet.observed_capture is not None
    assert not quiet.assessment_button.isHidden()
    assert quiet.observed_capture.packet['request']['scope_proof']['selected_reference']==BOUNDARY.isoformat()


def test_retained_demo_reopens_original_run_and_keeps_injected_recovery_state(tmp_path):
    import importlib.util
    from pathlib import Path
    spec=importlib.util.spec_from_file_location('higher_trial',Path(__file__).resolve().parents[1]/'tools/amdx_higher_review_demo.py')
    tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
    c,window=tool.open_demo(tmp_path/'trial')
    shell=window.trade_plan_widget.trading_day_shell_widget
    run_id=shell.active_trading_run.id
    pane=widget(shell)
    pane.orientation_selector.setCurrentIndex(1)
    click_x(pane,XSubtype.REVERSAL)
    pane.close()
    window.higher_failure_action.setChecked(True)
    dispose(window);c.close()
    c,window=tool.open_demo(tmp_path/'trial')
    try:
        shell=window.trade_plan_widget.trading_day_shell_widget
        assert shell.active_trading_run.id==run_id
        assert window.higher_failure_action.isChecked()
        pane=widget(shell)
        assert pane.orientation_selector.currentIndex()==1
        assert pane.table.item(2,5).text()=='AMDX'
        window.higher_failure_action.setChecked(False)
        pane.close()
    finally:dispose(window);c.close()
