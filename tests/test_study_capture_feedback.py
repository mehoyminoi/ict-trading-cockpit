from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from test_study_home import cockpit


def test_ctrl_y_redoes_in_observation_and_notes(cockpit):
    window, c = cockpit
    source = window.study_find_widget
    window.tabs.setCurrentWidget(source)
    for editor in (source.observation_input, source.notes_input):
        QTest.keyClicks(editor, 'Useful words')
        QTest.keyClick(editor, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        assert editor.toPlainText() == ''
        QTest.keyClick(editor, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
        assert editor.toPlainText() == 'Useful words'


def test_incomplete_summary_is_visible_and_preserves_preview_clipboard_draft(cockpit):
    window, c = cockpit
    source = window.study_find_widget
    window.tabs.setCurrentWidget(source)
    source.instrument_input.setText('MNQ')
    source.session_input.setText('London')
    source.observation_input.setPlainText('Keep the chart narrative')
    source.pattern_input.clear()
    source.summary_preview.setPlainText('Previously generated summary')
    QApplication.clipboard().setText('Clipboard must remain')
    before = source.build_draft()
    height = source.action_feedback.height()
    source.generate_summary_button.click()
    assert 'enter Pattern' in source.action_feedback.text()
    assert 'enter Pattern' in window.status_bar.currentMessage()
    assert source.action_feedback.height() == height
    assert source.summary_area.isHidden()
    assert source.summary_preview.toPlainText() == 'Previously generated summary'
    source.copy_summary()
    assert QApplication.clipboard().text() == 'Clipboard must remain'
    assert source.build_draft() == before
    source.pattern_input.setText('London return')
    source.generate_summary_button.click()
    assert source.action_feedback.text() == ''
    assert not source.summary_area.isHidden()
    assert 'London return' in source.summary_preview.toPlainText()
    assert 'summary generated' in window.status_bar.currentMessage()
