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


def test_observation_cue_is_repeatable_without_changing_draft_or_geometry(cockpit):
    window, c = cockpit
    source = window.study_find_widget
    window.tabs.setCurrentWidget(source)
    source.instrument_input.setText('MNQ')
    source.session_input.setText('London')
    source.pattern_input.setText('Return')
    source.observation_input.clear()
    before = source.build_draft()
    geometry = source.observation_input.geometry()
    source.generate_summary()
    cue = source.observation_input._validation_attention
    assert not cue.isHidden() and cue.timer.isActive()
    assert 'enter Observation' in window.status_bar.currentMessage()
    source.generate_summary()
    assert source.observation_input._validation_attention is cue
    assert source.observation_input.geometry() == geometry
    assert source.build_draft() == before
    cue.timer.timeout.emit()
    assert cue.isHidden()


def test_review_prompts_support_ctrl_y_but_saved_review_stays_readonly(cockpit):
    from ict_cockpit.gui.study_review_panel import StudyReviewPanel
    from ict_cockpit.database.study_review_repository import StudyReviewRepository
    window, c = cockpit
    panel = StudyReviewPanel(StudyReviewRepository(c), plan_id='plan', plan_revision='r1', task_id='task', question='Q')
    for editor in panel.fields.values():
        QTest.keyClicks(editor, 'Retained reflection')
        QTest.keyClick(editor, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        assert not editor.toPlainText()
        QTest.keyClick(editor, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
        assert editor.toPlainText() == 'Retained reflection'
    panel.save()
    assert panel.saved
    for editor in panel.fields.values():
        QTest.keyClick(editor, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        QTest.keyClick(editor, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
        assert editor.toPlainText() == 'Retained reflection'
    panel.close()
