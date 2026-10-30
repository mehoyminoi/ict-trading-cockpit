from datetime import date
from PySide6.QtCore import QDate, QTime
from test_study_home import cockpit


def select(window, layer='day', position=2):
    pane = window.amdx_catalog_widget
    window.tabs.setCurrentWidget(pane)
    pane.date_input.setDate(QDate(2026,10,8))
    pane.time_input.setTime(QTime(9,15))
    row = next(i for i,r in enumerate(pane.projection.cycles) if r.context.cycle.layer == layer)
    pane.table.setCurrentCell(row, position)
    return pane


def test_fresh_capture_uses_selected_london_not_clock_and_saved_next_day_is_new(cockpit):
    window,c = cockpit
    pane = select(window)
    source = window.study_find_widget
    window.integrated_study_task.question.setText('Study London')
    window.integrated_study_task.capture_button.click()
    assert source.date_input.date().toPython() == date(2026,10,8)
    assert source.instrument_input.text() == 'MNQ'
    assert source.session_input.text() == 'London'
    source.pattern_input.setText('First')
    source.observation_input.setPlainText('First day observation')
    window.link_investigation_action.trigger()
    identity = source.current_study_find_id
    assert source.submit()
    assert window.study_find_repository.get_by_id(identity).observation == 'First day observation'
    window.tabs.setCurrentWidget(pane)
    pane.date_input.setDate(QDate(2026,10,9))
    window.integrated_study_task.capture_button.click()
    assert source.current_study_find_id != identity
    assert source.date_input.date().toPython() == date(2026,10,9)
    assert source.pattern_input.text() == ''
    assert source.observation_input.toPlainText() == ''
    assert window.investigation_repository.get(identity)['market_reference'].startswith('2026-10-08')
    assert window.study_find_repository.get_by_id(identity)


def test_unfinished_capture_retains_inputs_and_exposes_mismatch(cockpit, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Cancel)
    window,c = cockpit
    pane = select(window)
    source = window.study_find_widget
    source.date_input.setDate(QDate(2026,10,7))
    source.instrument_input.setText('OTHER')
    source.session_input.setText('NYPM')
    source.observation_input.setPlainText('Do not replace')
    identity = source.current_study_find_id
    window.integrated_study_task.capture_button.click()
    assert source.current_study_find_id == identity
    assert source.observation_input.toPlainText() == 'Do not replace'
    assert source.date_input.date().day() == 7
    assert 'date: capture 2026-10-07 / selected context 2026-10-08' in window.capture_context_notice.text()
    assert 'instrument:' in window.capture_context_notice.text()
    source.date_input.setDate(QDate(2026,10,8))
    source.instrument_input.setText('MNQ')
    source.session_input.setText('London')
    assert 'matches' in window.capture_context_notice.text()


def test_higher_layer_does_not_invent_session(cockpit):
    window,c = cockpit
    select(window, 'week', 1)
    window.integrated_study_task.capture_button.click()
    assert window.study_find_widget.session_input.text() == ''


def test_90m_selection_inherits_parent_session(cockpit):
    window,c = cockpit
    select(window, 'session', 2)
    window.integrated_study_task.capture_button.click()
    assert window.study_find_widget.session_input.text() == 'NYAM'
