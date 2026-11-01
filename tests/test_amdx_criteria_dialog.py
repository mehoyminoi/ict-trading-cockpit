from dataclasses import replace

from PySide6.QtWidgets import QApplication
import pytest

from ict_cockpit.analysis.amdx import intraday_cycles
from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.gui.amdx_criteria_dialog import AMDXCriteriaDialog
from test_amdx_repository import REFERENCE, assessment, saved_run


@pytest.fixture
def editor(tmp_path):
    app = QApplication.instance() or QApplication([])
    connection = open_application_database(tmp_path / 'criteria.db')
    repo = AMDXRepository(connection)
    dialog = AMDXCriteriaDialog(repo.definitions, plan_revision='synthetic-plan',
        cycle=intraday_cycles(REFERENCE)[0], instrument='MNQ', reference=REFERENCE)
    yield dialog, repo, connection
    dialog.discard()
    dialog.close()
    connection.close()


def fill(dialog):
    dialog.new_button.click()
    dialog.rationale.setText('Synthetic close-inside criterion')
    dialog.output.setCurrentText('Assigned Role')
    dialog.target.setCurrentIndex(0)
    dialog.conditions.cellWidget(0, 0).setCurrentIndex(1)
    dialog.conditions.cellWidget(0, 1).setText('synthetic-close-inside')
    dialog.conditions.cellWidget(0, 4).setText('True')


def test_save_revise_and_reopen_without_run_or_adoption(editor):
    d, repo, connection = editor
    before = connection.total_changes
    fill(d)
    assert connection.total_changes == before
    d.save_button.click()
    first = d.browser.currentData()
    assert first.conditions[0].scope_id == d.cycle.quarters[1].id
    assert first.target_position == 1
    assert first.publication == 'Candidate'
    d.edit_button.click()
    d.priority.setValue(2)
    d.save_button.click()
    second = d.browser.currentData()
    assert first.id == second.id and first.revision != second.revision
    assert second.priority == 2
    assert len(repo.definitions.list_revisions(plan_revision='synthetic-plan')) == 2
    reopened = AMDXCriteriaDialog(repo.definitions, plan_revision='synthetic-plan', cycle=d.cycle, instrument='MNQ', reference=REFERENCE)
    assert reopened.browser.count() == 3
    reopened.close()
    for table in ('trading_session_run', 'amdx_evaluation', 'amdx_claim'):
        assert connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] == 0


def test_invalid_input_and_save_failure_retain_draft(editor, monkeypatch):
    d, repo, connection = editor
    fill(d)
    d.conditions.cellWidget(0, 4).setText('perhaps')
    d.save_button.click()
    assert d.editing and 'Not saved' in d.status.text()
    assert repo.definitions.list_revisions(plan_revision='synthetic-plan') == ()
    d.conditions.cellWidget(0, 4).setText('True')
    def fail(*args):
        raise RuntimeError('Storage unavailable')
    monkeypatch.setattr(repo.definitions, 'save_candidate', fail)
    d.save_button.click()
    assert d.editing and 'Storage unavailable' in d.status.text()
    assert d.rationale.text() == 'Synthetic close-inside criterion'
    d.discard_button.click()
    assert not d.editing


def test_output_constraints_and_local_behavior_are_distinct(editor):
    d, _, _ = editor
    fill(d)
    d.target.setCurrentIndex(2)
    assert [d.role.itemText(i) for i in range(d.role.count())] == ['M', 'D']
    d.output.setCurrentText('Local Behavior')
    assert d.role.findText('X(R)') >= 0
    d.output.setCurrentText('Assigned Role')
    d.target.setCurrentIndex(3)
    assert d.role.findText('X(C)') >= 0
    assert d.role.findText('A') == -1


def test_published_record_forks_candidate_preserving_outside_inputs(editor):
    d, repo, connection = editor
    run = saved_run(connection)
    evaluation = assessment(run)
    # Fixture registry record; publication is not exposed by the editor.
    published = replace(evaluation.definitions[0], publication='Published',
        conditions=(replace(evaluation.definitions[0].conditions[0], scope_id='other-explicit-quarter'),))
    with repo._transaction():
        repo.definitions._store_locked(published)
    d.reload(published)
    changes = connection.total_changes
    d.inspect()
    assert connection.total_changes == changes
    assert 'Outside pinned quartet' in d.details.toPlainText()
    d.edit_button.click()
    d.save_button.click()
    candidate = d.browser.currentData()
    assert candidate.publication == 'Candidate'
    assert candidate.conditions == published.conditions
    assert repo.definitions.get(plan_revision=published.plan_revision, rule_id=published.id,
        revision=published.revision, publication='Published') == published


from test_study_home import cockpit

def test_study_route_pins_selected_cycle_and_does_not_write(cockpit, monkeypatch):
    window, connection = cockpit
    pane = window.amdx_catalog_widget
    window.tabs.setCurrentWidget(pane)
    pane.table.setCurrentCell(4, 1)
    target = pane.target
    assert target is not None
    before = connection.total_changes
    seen = []
    def inspect_dialog(dialog):
        seen.append(dialog.cycle)
        assert dialog.cycle == target.cycle
        assert dialog.plan_revision == window.trade_plan.revision
        assert not dialog.editing
        return 0
    monkeypatch.setattr(AMDXCriteriaDialog, 'exec', inspect_dialog)
    window.integrated_study_task.criteria_button.click()
    assert seen == [target.cycle]
    assert pane.target == target
    assert connection.total_changes == before


def test_cancel_return_keeps_unsaved_draft_and_explicit_discard_exits(editor, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    d, repo, _ = editor
    fill(d)
    d.show()
    QApplication.processEvents()
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Cancel)
    d.reject()
    assert d.isVisible() and d.editing
    assert d.rationale.text() == 'Synthetic close-inside criterion'
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Discard)
    d.reject()
    assert not d.isVisible()
    assert repo.definitions.list_revisions(plan_revision='synthetic-plan') == ()


def test_reusable_scope_survives_edit_and_previews_new_date(editor):
    from datetime import timedelta
    from ict_cockpit.analysis.amdx_rules import QuartetScope
    d, repo, _ = editor
    fill(d)
    scope = d.conditions.cellWidget(0, 0)
    index = next(i for i in range(scope.count()) if scope.itemData(i) == QuartetScope(2))
    scope.setCurrentIndex(index)
    d.save_button.click()
    saved = d.browser.currentData()
    assert saved.conditions[0].scope_id == QuartetScope(2)
    d.edit_button.click()
    assert d.conditions.cellWidget(0, 0).currentData() == QuartetScope(2)
    d.discard()
    later = AMDXCriteriaDialog(repo.definitions, plan_revision='synthetic-plan',
        cycle=intraday_cycles(REFERENCE + timedelta(days=1))[0], instrument='MNQ',
        reference=REFERENCE + timedelta(days=1))
    later.reload(saved)
    assert 'Reusable: selected quartet Q2' in later.details.toPlainText()
    assert '2026-10-09' in later.details.toPlainText()
    assert later.browser.currentData() == saved
    later.close()
