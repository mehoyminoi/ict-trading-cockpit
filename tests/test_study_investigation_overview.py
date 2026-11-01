from dataclasses import replace
from datetime import date
from PySide6.QtWidgets import QApplication
from ict_cockpit.analysis.study_find import StudyFind, StudyFindDraft
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.study_investigation_repository import StudyInvestigationRepository
from ict_cockpit.gui.study_investigation_overview import StudyInvestigationOverview
from test_study_criterion import study, record
from test_study_investigation_repository import context


def test_overview_scopes_material_inspects_without_writes_and_reopens(study):
    app = QApplication.instance() or QApplication([])
    c, amdx, criteria, original, d = study
    criteria.save(record(original, d))
    criteria.save(replace(record(original, d, 'other-result'), task_id='other'))
    finds = StudyFindRepository(c)
    links = StudyInvestigationRepository(c)
    saved = StudyFind(observation_date=date(2026,10,9), instrument='MNQ',
                      session='London', pattern_name='Counterexample', observation='chart observation')
    finds.save(saved)
    links.link(saved.id, **context())
    draft = StudyFindDraft(observation_date=date(2026,10,9), pattern_name='Unfinished', observation='draft words')
    finds.save_draft(draft)
    links.link(draft.id, **context())
    unlinked = StudyFind(observation_date=date(2026,10,9), instrument='MNQ',
                         session='London', pattern_name='Not linked', observation='same date')
    finds.save(unlinked)
    before = c.total_changes
    for _ in range(2):
        dialog = StudyInvestigationOverview(links, criteria, finds, task_id='task', plan_id='plan', question='Current question')
        assert len(dialog.entries) == 3
        assert '1 saved criterion results' in dialog.summary.text()
        assert 'Question:' in dialog.detail.toPlainText()
        dialog.items.setCurrentRow(1)
        assert dialog.find_review.observation_view.toPlainText() == 'chart observation'
        dialog.items.setCurrentRow(2)
        assert 'draft words' in dialog.detail.toPlainText()
        assert 'not a saved Study Find' in dialog.detail.toPlainText()
        dialog.reject()
    assert c.total_changes == before
    empty = StudyInvestigationOverview(links, criteria, finds, task_id='unknown', plan_id='plan', question='')
    assert not empty.entries
    assert 'No retained material' in empty.detail.toPlainText()
    empty.close()


def test_overview_return_preserves_calendar_question_and_capture(cockpit, monkeypatch):
    from ict_cockpit.gui.study_investigation_overview import StudyInvestigationOverview
    window, connection = cockpit
    pane = window.amdx_catalog_widget
    window.tabs.setCurrentWidget(pane)
    window.integrated_study_task.question.setText('Keep this working question')
    window.study_find_widget.pattern_input.setText('Unfinished capture')
    window.save_pending_study_find_draft()
    before = connection.total_changes
    reference = pane.reference()
    task_id = window.integrated_study_task.task_id
    opened = []
    def inspect_and_return(dialog):
        opened.append(dialog.windowTitle())
        dialog.reject()
    monkeypatch.setattr(StudyInvestigationOverview, 'exec', inspect_and_return)
    window.integrated_study_task.overview_button.click()
    assert opened
    assert window.tabs.currentWidget() is pane
    assert pane.reference() == reference
    assert window.integrated_study_task.task_id == task_id
    assert window.integrated_study_task.question.text() == 'Keep this working question'
    assert window.study_find_widget.pattern_input.text() == 'Unfinished capture'
    assert connection.total_changes == before


from test_study_home import cockpit
