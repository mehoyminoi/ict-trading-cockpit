from PySide6.QtTest import QTest
from test_study_home import cockpit


def test_summary_disclosure_and_divider_preserve_capture_and_undo(cockpit):
    window, c = cockpit
    source = window.study_find_widget
    window.integrated_study_task.question.setText('Capture layout')
    window._open_investigation_capture()
    QTest.keyClicks(source.observation_input, 'Keep this observation')
    source.notes_input.setPlainText('Higher timeframe context')
    window.save_pending_study_find_draft()
    draft = source.build_draft()
    target = window._study_save_target()
    changes = c.total_changes
    assert source.summary_area.isHidden()
    assert window.capture_association_label.isHidden()
    window.capture_association_details_action.setChecked(True)
    assert not window.capture_association_label.isHidden()
    window.capture_association_details_action.setChecked(False)
    source.summary_toggle.click()
    source.capture_splitter.setSizes([650, 350])
    source.summary_toggle.click()
    assert source.summary_area.isHidden()
    assert source.build_draft() == draft
    assert window._study_save_target() == target
    assert c.total_changes == changes
    assert source.observation_input.document().isUndoAvailable()
    source.observation_input.undo()
    source.observation_input.redo()
    assert source.observation_input.toPlainText() == draft.observation
    source.generate_summary_button.click()
    assert not source.summary_area.isHidden()
    assert source.build_draft() == draft


def test_context_warning_remains_visible_and_commands_stay_with_their_work(cockpit):
    window, c = cockpit
    source = window.study_find_widget
    window.integrated_study_task.question.setText('Context warning')
    window._open_investigation_capture()
    assert window.capture_context_notice.isHidden()
    source.date_input.setDate(source.date_input.date().addDays(1))
    assert not window.capture_context_notice.isHidden()
    assert 'differs' in window.capture_context_notice.text()
    assert source.entry_actions.indexOf(window.keep_study_question_button) >= 0
    assert source.entry_actions.indexOf(window.keep_study_finding_button) >= 0
    assert source.save_area.indexOf(source.save_feedback) >= 0
    assert source.save_area.indexOf(window.discard_study_draft_button) >= 0
