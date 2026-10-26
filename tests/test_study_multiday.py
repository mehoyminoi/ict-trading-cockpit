from dataclasses import replace

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import QApplication, QMessageBox

from ict_cockpit.gui.study_criterion_dialog import StudyCriterionDialog
from test_study_criterion import study
from test_amdx_repository import REFERENCE


def open_dialog(repo, original, d):
    return StudyCriterionDialog(repo, task_id='task', plan_id='plan', plan_revision=d.plan_revision,
        question='Study across days', instrument='MNQ', cycle=original.cycle, reference=REFERENCE)


def test_two_dates_keep_criterion_clear_inputs_and_preserve_original_evidence(study):
    app = QApplication.instance() or QApplication([])
    c, amdx, repo, original, d = study
    dialog = open_dialog(repo, original, d)
    try:
        dialog.criterion.setCurrentIndex(1)
        dialog.inputs[0][4].setText('True'); dialog.inputs[0][5].setText('Day one synthetic source')
        dialog.preview(); dialog.save()
        first = repo.list_for_task('task')[0]
        writes = c.total_changes
        dialog.next_day_button.click()
        assert dialog.reference.date().isoformat() == '2026-10-09'
        assert dialog.criterion.currentData() == d
        assert dialog.question.text() == 'Study across days'
        assert dialog.inputs[0][4].text() == dialog.inputs[0][5].text() == ''
        assert c.total_changes == writes
        assert dialog.inputs[0][0] != first.evaluation.facts[0].scope_id
        dialog.preview()
        assert 'Result: Unknown' in dialog.result.toPlainText()
        dialog.inputs[0][4].setText('False'); dialog.inputs[0][5].setText('Day two synthetic source')
        dialog.preview(); dialog.save()
        second = repo.list_for_task('task')[1]
        assert second.evaluation.results[0].state == 'Not Matched'
        assert repo.get(first.evaluation.id) == first
        assert '2 saved results · 2 New York reference dates · 1 criterion revisions' in dialog.coverage.text()
        dialog.saved.setCurrentIndex(1)
        assert 'Day one synthetic source' in dialog.result.toPlainText()
        assert dialog.reference == second.evaluation.market_reference
        assert dialog.inputs[0][4].text() == 'False'
        again = open_dialog(repo, original, d)
        assert again.saved.count() == 3
        again.saved.setCurrentIndex(2)
        assert 'Day two synthetic source' in again.result.toPlainText()
        again.close()
    finally:
        dialog.dirty = False; dialog.close()


def test_pending_date_and_canceled_transition_preserve_preview(study, monkeypatch):
    app = QApplication.instance() or QApplication([])
    c, _, repo, original, d = study
    dialog = open_dialog(repo, original, d)
    try:
        dialog.criterion.setCurrentIndex(1)
        dialog.inputs[0][4].setText('True'); dialog.inputs[0][5].setText('Synthetic')
        dialog.preview()
        preview = dialog.preview_record
        dialog.date_input.setDate(QDate(2026, 10, 9))
        assert dialog.reference == REFERENCE
        assert not dialog.preview_button.isEnabled() and not dialog.save_button.isEnabled()
        monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Cancel)
        dialog.apply_date_button.click()
        assert dialog.reference == REFERENCE and dialog.preview_record == preview
        assert dialog.date_input.date() == QDate(2026, 10, 8)
        assert dialog.save_button.isEnabled()
        assert dialog.inputs[0][4].text() == 'True'
        monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Discard)
        dialog.next_day_button.click()
        assert dialog.preview_record is None and not dialog.save_button.isEnabled()
        assert dialog.inputs[0][4].text() == ''
        assert repo.list_for_task('task') == ()
        dialog.question.setText('Unsaved revised question')
        dialog.next_day_button.click()
        assert dialog.question.text() == 'Unsaved revised question'
        assert dialog.dirty  # Navigation must not suppress the unsaved-question return prompt.
    finally:
        dialog.dirty = False; dialog.close()


def test_fixed_scopes_stay_fixed_and_invalid_clock_does_not_retarget(study):
    app = QApplication.instance() or QApplication([])
    c, amdx, repo, original, d = study
    fixed = replace(d, revision='fixed', conditions=original.definitions[0].conditions)
    amdx.definitions.save_candidate(fixed)
    dialog = open_dialog(repo, original, d)
    try:
        index = next(i for i in range(dialog.criterion.count()) if dialog.criterion.itemData(i) == fixed)
        dialog.criterion.setCurrentIndex(index)
        dialog.next_day_button.click()
        assert dialog.inputs[0][0] == fixed.conditions[0].scope_id
        active_reference = dialog.reference
        dialog.date_input.setDate(QDate(2026, 3, 8)); dialog.time_input.setTime(QTime(2, 30))
        dialog.apply_date_button.click()
        assert 'did not occur' in dialog.status.text()
        assert dialog.reference == active_reference
        assert not dialog.preview_button.isEnabled()
        assert repo.list_for_task('task') == ()
    finally:
        dialog.dirty = False; dialog.close()


def test_repeated_new_york_hour_uses_explicit_occurrence(study):
    from ict_cockpit.analysis.amdx_context import resolve_stack_cycles
    app = QApplication.instance() or QApplication([])
    _, _, repo, _, d = study
    cycle = next(c.cycle for c in resolve_stack_cycles(REFERENCE) if c.cycle.layer == 'week')
    dialog = StudyCriterionDialog(repo, task_id='task', plan_id='plan', plan_revision=d.plan_revision,
        question='Repeated-hour orientation', instrument='MNQ', cycle=cycle, reference=REFERENCE)
    try:
        dialog.date_input.setDate(QDate(2026, 11, 1)); dialog.time_input.setTime(QTime(1, 30))
        dialog.fold_input.setCurrentIndex(0); dialog.apply_reference()
        first = dialog.reference
        dialog.fold_input.setCurrentIndex(1); dialog.apply_reference()
        second = dialog.reference
        assert second.timestamp() - first.timestamp() == 3600
        assert first.utcoffset() != second.utcoffset()
        assert repo.list_for_task('task') == ()
    finally:
        dialog.dirty = False; dialog.close()
