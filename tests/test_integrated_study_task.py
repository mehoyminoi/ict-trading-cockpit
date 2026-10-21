from PySide6.QtCore import QDate, QSettings
from ict_cockpit.gui.integrated_study_task_widget import IntegratedStudyTaskWidget
from test_study_home import cockpit, close
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.database.study_find_repository import StudyFindRepository


def test_question_restores_only_for_same_plan_revision(tmp_path):
    settings = QSettings(str(tmp_path / 'workspace.ini'), QSettings.Format.IniFormat)
    first = IntegratedStudyTaskWidget(plan_id='p', revision='r1', settings=settings)
    first.question.setText('Which quarter contains manipulation?')
    second = IntegratedStudyTaskWidget(plan_id='p', revision='r1', settings=settings)
    other = IntegratedStudyTaskWidget(plan_id='p', revision='r2', settings=settings)
    assert second.question.text() == first.question.text()
    assert other.question.text() == ''
    for widget in (first, second, other):
        widget.close()


def test_capture_return_preserves_draft_reference_and_no_domain_writes(cockpit):
    window, connection = cockpit
    pane = window.amdx_catalog_widget
    window.tabs.setCurrentWidget(pane)
    pane.date_input.setDate(QDate(2026, 10, 9))
    window.integrated_study_task.question.setText('Inspect session manipulation')
    window.study_find_widget.pattern_input.setText('Existing unfinished capture')
    window.save_pending_study_find_draft()
    reference = pane.reference()
    before = connection.total_changes
    window.integrated_study_task.capture_button.click()
    assert window.tabs.currentWidget() is window.study_find_widget
    assert window.study_find_widget.pattern_input.text() == 'Existing unfinished capture'
    assert 'Inspect session manipulation' in window.investigation_context_labels[0].text()
    assert 'not a saved link' in window.investigation_context_labels[0].text()
    window.investigation_return_buttons[0].click()
    assert window.tabs.currentWidget() is pane
    assert pane.reference() == reference
    assert connection.total_changes == before
    assert window.trade_plan_widget.trading_day_shell_widget.active_trading_run is None


def test_review_route_preserves_active_run_and_restores_question(cockpit):
    window, connection = cockpit
    shell = window.trade_plan_widget.trading_day_shell_widget
    assert shell.start_trading_run()
    run_id = shell.active_trading_run.id
    window.integrated_study_task.question.setText('Retain investigation')
    window.integrated_study_task.review_button.click()
    assert window.tabs.currentWidget() is window.study_find_review_widget
    window.investigation_return_buttons[1].click()
    assert shell.active_trading_run.id == run_id
    restored = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    try:
        assert restored.integrated_study_task.question.text() == 'Retain investigation'
        assert restored.tabs.currentWidget() is restored.trade_plan_widget
        assert restored.trade_plan_widget.trading_day_shell_widget.active_trading_run.id == run_id
    finally:
        close(restored)


def test_separate_demo_keeps_question_and_rejects_unrelated_directory(tmp_path):
    import pytest
    from tools.integrated_study_task_demo import open_demo
    trial = tmp_path / 'trial'
    connection, window = open_demo(trial)
    window.integrated_study_task.question.setText('Restart this investigation')
    close(window)
    connection.close()
    connection, window = open_demo(trial)
    try:
        assert window.tabs.currentWidget() is window.amdx_catalog_widget
        assert window.integrated_study_task.question.text() == 'Restart this investigation'
    finally:
        close(window)
        connection.close()
    unrelated = tmp_path / 'unrelated'
    unrelated.mkdir()
    (unrelated / 'keep.txt').write_text('keep')
    with pytest.raises(ValueError):
        open_demo(unrelated)


def test_explicit_link_preserves_displayed_context_through_save_and_restart(cockpit):
    window, connection = cockpit
    task = window.integrated_study_task
    pane = window.amdx_catalog_widget
    task.question.setText('Original question')
    pane.date_input.setDate(QDate(2026, 10, 9))
    source = window.study_find_widget
    source.instrument_input.setText('MNQ')
    source.session_input.setText('NYAM')
    source.pattern_input.setText('Manipulation')
    source.observation_input.setPlainText('Observed sweep')
    task.capture_button.click()
    reference = pane.reference().isoformat()
    task.question.setText('Changed later')
    window.link_investigation_button.click()
    link = window.investigation_repository.get(source.current_study_find_id)
    assert link['question'] == 'Original question'
    assert link['market_reference'] == reference
    assert source.submit()
    window._open_investigation_review()
    assert 'Original question' in window.study_find_review_widget.details_label.text()
    assert 'Linked investigation' in window.study_find_review_widget.details_label.text()
    restored = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    try:
        assert restored.investigation_repository.get(source.current_study_find_id) == link
        assert restored.integrated_study_task.task_id == task.task_id
    finally:
        close(restored)
    task.capture_button.click()
    window.link_investigation_button.click()
    assert 'cannot be reassigned' in window.capture_association_label.text()
    assert window.investigation_repository.get(source.current_study_find_id) == link
    old_id = task.task_id
    task.new_task_button.click()
    assert task.task_id != old_id
    assert task.question.text() == ''
    assert window.investigation_repository.get(source.current_study_find_id) == link


def test_small_window_uses_scroll_without_changing_calendar_owner(cockpit):
    from PySide6.QtWidgets import QApplication
    window, _connection = cockpit
    window.tabs.setCurrentWidget(window.amdx_catalog_widget)
    window.resize(1280, 720)
    window.show()
    QApplication.processEvents()
    assert window.height() == 720
    assert window.workspace_scroll.widget() is window.tabs
    assert window.amdx_catalog_widget.parent() is not None
    assert window.workspace_scroll.verticalScrollBar().maximum() > 0
