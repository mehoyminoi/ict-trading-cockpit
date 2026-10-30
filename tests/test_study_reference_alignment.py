import sqlite3
from PySide6.QtCore import QDate
from test_study_home import cockpit, close
from test_study_capture_context import select
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.database.study_find_repository import StudyFindRepository


def prepare(window):
    select(window)
    window.integrated_study_task.question.setText('Reference study')
    window._open_investigation_capture()
    source = window.study_find_widget
    source.pattern_input.setText('Example')
    source.observation_input.setPlainText('Keep observation')
    source.notes_input.setPlainText('Keep notes')
    source.image_paths = ['/example/image.png']
    source.emit_draft_changed()
    window.amdx_catalog_widget.date_input.setDate(QDate(2026,10,9))
    window._open_investigation_capture()
    return source


def test_explicit_alignment_preserves_content_and_survives_restart(cockpit):
    window,c = cockpit
    source = prepare(window)
    identity = source.current_study_find_id
    assert '2026-10-08' in window.study_reference_summary.text()
    assert '2026-10-09' in window.study_reference_summary.text()
    assert source.date_input.date().day() == 8
    window.align_study_reference_button.click()
    assert source.date_input.date().day() == 9
    assert source.observation_input.toPlainText() == 'Keep observation'
    assert source.notes_input.toPlainText() == 'Keep notes'
    assert source.image_paths == ['/example/image.png']
    assert source.current_study_find_id == identity
    assert window._study_save_target()['market_reference'].startswith('2026-10-09')
    assert window.investigation_repository.get(identity) is None
    assert window.study_find_repository.get_by_id(identity) is None
    restored = MainWindow(TDARepository(c), StudyFindRepository(c))
    try:
        assert restored.study_find_widget.current_study_find_id == identity
        assert restored.study_find_widget.date_input.date().day() == 9
        assert restored._study_save_target()['market_reference'].startswith('2026-10-09')
    finally:close(restored)


def test_failure_rolls_back_draft_and_context(cockpit):
    window,c = cockpit
    source = prepare(window)
    window.save_pending_study_find_draft()
    draft = source.build_draft()
    target = window._study_save_target()
    c.execute("CREATE TRIGGER fail_alignment BEFORE UPDATE ON study_capture_context BEGIN SELECT RAISE(ABORT,'test failure'); END")
    c.commit()
    window.align_study_reference_button.click()
    assert source.build_draft() == draft
    assert window.study_find_repository.get_latest_draft() == draft
    assert window._study_save_target() == target
    assert 'not changed' in source.save_feedback.text()


def test_linked_capture_cannot_be_reassigned(cockpit):
    window,c = cockpit
    source = prepare(window)
    window._link_investigation_capture()
    target = window.investigation_repository.get(source.current_study_find_id)
    window._refresh_study_reference()
    assert not window.align_study_reference_button.isEnabled()
    window._align_capture_reference()
    assert window.investigation_repository.get(source.current_study_find_id) == target
    assert source.date_input.date().day() == 8
    assert 'not changed' in source.save_feedback.text()
