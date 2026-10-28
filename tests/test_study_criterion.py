from dataclasses import replace
from datetime import timedelta
import sqlite3

import pytest
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.amdx_rules import evaluate
from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_criterion_repository import StudyCriterionRecord, StudyCriterionRepository
from ict_cockpit.gui.study_criterion_dialog import StudyCriterionDialog
from test_amdx_reusable_scopes import basis
from test_amdx_repository import REFERENCE


@pytest.fixture
def study(tmp_path):
    c = open_application_database(tmp_path / 'study.db')
    amdx = AMDXRepository(c)
    original, d = basis()
    amdx.definitions.save_candidate(d)
    yield c, amdx, StudyCriterionRepository(amdx), original, d
    c.close()


def record(original, d, identity='study-1', facts=None):
    e = evaluate(evaluation_id=identity, run_id=None, cycle=original.cycle, market_reference=REFERENCE,
        definitions=(d,), facts=original.facts if facts is None else facts)
    return StudyCriterionRecord('task', 'plan', 'Does this observation satisfy the candidate?', 'MNQ', REFERENCE, e)


def test_independent_result_reopens_exact_basis_and_is_immutable(study):
    c, amdx, repo, original, d = study
    saved = repo.save(record(original, d))
    changes = c.total_changes
    assert repo.save(saved) == saved
    assert c.total_changes == changes
    assert repo.get(saved.evaluation.id) == saved
    assert repo.list_for_task('task') == (saved,)
    from pathlib import Path
    reopened = open_application_database(Path(c.execute('PRAGMA database_list').fetchone()[2]))
    assert StudyCriterionRepository(AMDXRepository(reopened)).get(saved.evaluation.id) == saved
    reopened.close()
    assert repo.list_for_task('other') == ()
    for table in ('trading_session_run', 'amdx_evaluation', 'amdx_claim'):
        assert c.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] == 0
    with pytest.raises(ValueError, match='overwritten'):
        repo.save(replace(saved, question='different'))
    for sql in ("DELETE FROM study_criterion_evaluation", "UPDATE study_criterion_evaluation SET task_id='other'",
                "INSERT OR REPLACE INTO study_criterion_evaluation SELECT * FROM study_criterion_evaluation"):
        with pytest.raises(sqlite3.IntegrityError):
            c.execute(sql)
        c.rollback()
    with pytest.raises(ValueError):
        amdx.save_evaluation(saved.evaluation, recorded_at=REFERENCE)


def test_save_requires_retained_definition_and_does_not_commit_caller(study):
    c, _, repo, original, d = study
    with pytest.raises(ValueError, match='Save the criterion'):
        repo.save(record(original, replace(d, revision='not-saved')))
    c.execute('BEGIN')
    with pytest.raises(RuntimeError, match='pending transaction'):
        repo.save(record(original, d))
    assert c.in_transaction
    c.rollback()
    assert repo.list_for_task('task') == ()


def test_result_retains_unknown_future_and_original_revision(study):
    _, amdx, repo, original, d = study
    future = replace(original.facts[0], available_at=REFERENCE + timedelta(hours=1))
    saved = repo.save(record(original, d, facts=(future,)))
    assert saved.evaluation.results[0].state == 'Unknown'
    amdx.definitions.save_candidate(replace(d, revision='v2', priority=2))
    assert repo.get(saved.evaluation.id) == saved


def test_dialog_preview_edit_save_and_reopen(study):
    app = QApplication.instance() or QApplication([])
    c, _, repo, original, d = study
    dialog = StudyCriterionDialog(repo, task_id='task', plan_id='plan', plan_revision=d.plan_revision,
        question='Synthetic criterion question', instrument='MNQ', cycle=original.cycle, reference=REFERENCE)
    try:
        dialog.criterion.setCurrentIndex(1)
        before = c.total_changes
        dialog.preview_button.click()
        assert 'Result: Unknown' in dialog.result.toPlainText()
        assert c.total_changes == before
        _, _, _, _, value, source, available = dialog.inputs[0]
        value.setText('True'); source.setText('Synthetic chart observation')
        assert not dialog.save_button.isEnabled()
        dialog.preview_button.click()
        assert 'Result: Matched' in dialog.result.toPlainText()
        assert c.total_changes == before
        dialog.save_button.click()
        assert len(repo.list_for_task('task')) == 1
        assert 'SAVED STUDY RESULT' in dialog.result.toPlainText()
        value.setText('False')
        dialog.preview_button.click()
        assert 'Result: Not Matched' in dialog.result.toPlainText()
        available.setDateTime(QDateTime.fromString((REFERENCE + timedelta(hours=1)).isoformat(), Qt.DateFormat.ISODate))
        dialog.preview_button.click()
        assert 'Result: Unknown' in dialog.result.toPlainText()
        assert len(repo.list_for_task('task')) == 1
        second = StudyCriterionDialog(repo, task_id='task', plan_id='plan', plan_revision=d.plan_revision,
            question='New question draft', instrument='MNQ', cycle=original.cycle, reference=REFERENCE)
        second.saved.setCurrentIndex(1)
        assert 'Synthetic criterion question' in second.result.toPlainText()
        assert 'Synthetic chart observation' in second.result.toPlainText()
        second.close()
    finally:
        dialog.dirty = False
        dialog.close()


def test_dialog_missing_source_and_storage_failure_keep_inputs(study, monkeypatch):
    app = QApplication.instance() or QApplication([])
    _, _, repo, original, d = study
    dialog = StudyCriterionDialog(repo, task_id='task', plan_id='plan', plan_revision=d.plan_revision,
        question='Question', instrument='MNQ', cycle=original.cycle, reference=REFERENCE)
    try:
        dialog.criterion.setCurrentIndex(1)
        value, source = dialog.inputs[0][4:6]
        value.setText('True')
        dialog.preview_button.click()
        assert 'Provide a source' in dialog.status.text()
        source.setText('Synthetic')
        dialog.preview_button.click()
        def fail(_record):
            raise sqlite3.OperationalError('disk unavailable')
        monkeypatch.setattr(repo, 'save', fail)
        dialog.save_button.click()
        assert 'Not saved' in dialog.status.text()
        assert dialog.preview_record is not None
        assert value.text() == 'True'
    finally:
        dialog.dirty = False
        dialog.close()


def test_v47_upgrade_preserves_existing_definitions_and_rolls_back_on_failure(tmp_path, monkeypatch):
    from ict_cockpit.database import schema
    path = tmp_path / 'upgrade.db'
    c = open_application_database(path)
    _, d = basis()
    AMDXRepository(c).definitions.save_candidate(d)
    c.execute('DROP TABLE study_question')
    c.execute('DROP TABLE study_criterion_evaluation')
    c.execute('PRAGMA user_version=47')
    c.commit()
    migrate = schema._migrate_version_47_to_48
    def fail(connection):
        migrate(connection)
        raise RuntimeError('synthetic migration failure')
    monkeypatch.setattr(schema, '_migrate_version_47_to_48', fail)
    with pytest.raises(RuntimeError):
        schema.initialize_schema(c)
    assert c.execute('PRAGMA user_version').fetchone()[0] == 47
    assert c.execute("SELECT name FROM sqlite_master WHERE name='study_criterion_evaluation'").fetchone() is None
    monkeypatch.setattr(schema, '_migrate_version_47_to_48', migrate)
    schema.initialize_schema(c)
    assert c.execute('PRAGMA user_version').fetchone()[0] == 49
    assert AMDXRepository(c).definitions.list_revisions(plan_revision=d.plan_revision) == (d,)
    c.close()
    reopened = open_application_database(path)
    assert StudyCriterionRepository(AMDXRepository(reopened)).list_for_task('task') == ()
    reopened.close()


def test_demo_seed_and_route_do_not_manufacture_a_run(tmp_path, monkeypatch):
    from tools.study_criterion_demo import open_demo
    from test_study_home import close
    app = QApplication.instance() or QApplication([])
    c, window = open_demo(tmp_path / 'demo')
    try:
        assert window.amdx_catalog_widget.target.cycle.layer == 'day'
        assert window.amdx_catalog_widget.reference().hour == 9
        assert 'Synthetic study' in window.integrated_study_task.question.text()
        before = c.total_changes
        seen = []
        def inspect(dialog):
            seen.append(dialog)
            assert dialog.criterion.count() == 2
            assert dialog.question.text() == window.integrated_study_task.question.text()
            return 0
        monkeypatch.setattr(StudyCriterionDialog, 'exec', inspect)
        window.integrated_study_task.evaluate_button.click()
        assert len(seen) == 1
        assert c.total_changes == before
        assert window.trade_plan_widget.trading_day_shell_widget.active_trading_run is None
    finally:
        close(window); c.close()
    c, window = open_demo(tmp_path / 'demo')
    try:
        assert len(window.trading_session_run_repository.amdx.definitions.list_revisions(plan_revision=window.trade_plan.revision)) == 1
    finally:
        close(window); c.close()


def test_switching_criterion_and_return_can_preserve_unsaved_inputs(study, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    app = QApplication.instance() or QApplication([])
    _, amdx, repo, original, d = study
    amdx.definitions.save_candidate(replace(d, revision='v2'))
    dialog = StudyCriterionDialog(repo, task_id='task', plan_id='plan', plan_revision=d.plan_revision,
        question='Question', instrument='MNQ', cycle=original.cycle, reference=REFERENCE)
    try:
        dialog.criterion.setCurrentIndex(1)
        value, source = dialog.inputs[0][4:6]
        value.setText('True'); source.setText('Synthetic')
        monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Cancel)
        dialog.criterion.setCurrentIndex(2)
        assert dialog.criterion.currentIndex() == 1
        assert value.text() == 'True'
        dialog.show(); QApplication.processEvents(); dialog.reject()
        assert dialog.isVisible()
        assert value.text() == 'True'
    finally:
        dialog.dirty = False
        dialog.close()
