import sqlite3
import subprocess
import pytest
from PySide6.QtWidgets import QInputDialog, QMessageBox
from ict_cockpit.database.study_task_registry import StudyTaskRegistry
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.database.study_find_repository import StudyFindRepository
from test_study_home import cockpit, close


def test_switch_guard_and_resume(cockpit, monkeypatch):
    window, c = cockpit
    task = window.integrated_study_task
    task.question.setText('Question A')
    a = task.task_id
    reference = window.amdx_catalog_widget.reference()
    window.study_find_widget.notes_input.setPlainText('Unfinished')
    task.new_task_button.click()
    assert task.task_id == a and 'before switching' in task.status.text()
    window.study_find_widget.notes_input.clear()
    task.new_task_button.click()
    b = task.task_id
    assert b != a
    task.question.setText('Question B')
    monkeypatch.setattr(QInputDialog, 'getItem', lambda *args: (next(x for x in args[3] if x.startswith('Question A')), True))
    task.resume_button.click()
    assert task.task_id == a and task.question.isReadOnly()
    assert window.amdx_catalog_widget.reference() == reference
    assert len(window.study_task_registry.choices(window.trade_plan.id, window.trade_plan.revision)) == 2
    restored = MainWindow(TDARepository(c), StudyFindRepository(c))
    try:
        assert restored.integrated_study_task.task_id == a
        assert restored.integrated_study_task.question.text() == 'Question A'
        assert restored.integrated_study_task.question.isReadOnly()
    finally:
        close(restored)


def test_retained_destination_survives_restart_and_reentry(cockpit, monkeypatch):
    window, c = cockpit
    task = window.integrated_study_task
    task.question.setText('Question A')
    window._open_investigation_capture()
    context = window._study_save_target()
    window.study_find_widget.notes_input.setPlainText('Original context')
    window.save_pending_study_find_draft()
    restored = MainWindow(TDARepository(c), StudyFindRepository(c))
    try:
        assert restored._study_save_target() == context
        restored.amdx_catalog_widget.date_input.setDate(restored.amdx_catalog_widget.date_input.date().addDays(1))
        restored._open_investigation_capture()
        assert restored._study_save_target() == context
        assert restored.study_find_widget.notes_input.toPlainText() == 'Original context'
    finally:
        close(restored)


def test_legacy_unbound_capture_requires_explicit_destination(cockpit, monkeypatch):
    window, c = cockpit
    window.study_find_widget.notes_input.setPlainText('Legacy unbound')
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Cancel)
    window._open_investigation_capture()
    assert window._study_save_target() is None
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Yes)
    window._open_investigation_capture()
    assert window._study_save_target() is not None


def test_migration_preserves_old_data_and_rolls_back(tmp_path):
    source = subprocess.check_output(['git', 'show', 'e9dd0db:src/ict_cockpit/database/schema.py'], text=True)
    old = {};exec(source, old)
    for fail in (True, False):
        c = sqlite3.connect(tmp_path / f'{fail}.db')
        old['initialize_schema'](c)
        c.execute("INSERT INTO study_review VALUES ('r','p','t','{}')");c.commit()
        if fail:
            c.set_authorizer(lambda action,a,b,*_: sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_PRAGMA and a == 'user_version' and b == '52' else sqlite3.SQLITE_OK)
            with pytest.raises(sqlite3.DatabaseError): initialize_schema(c)
            c.set_authorizer(None)
            assert c.execute('PRAGMA user_version').fetchone()[0] == 51
            assert not c.execute("SELECT name FROM sqlite_master WHERE name='study_task_registry'").fetchall()
        initialize_schema(c)
        assert c.execute('SELECT * FROM study_review').fetchall() == [('r','p','t','{}')]
        with pytest.raises(RuntimeError):old['initialize_schema'](c)
        c.close()


def test_historical_variants_are_explicit_and_registration_cannot_rewrite(cockpit):
    import json
    window, c = cockpit
    r = window.study_task_registry
    plan, revision = window.trade_plan.id, window.trade_plan.revision
    for identity, question in [('one', 'Original wording'), ('two', 'Different wording')]:
        c.execute('INSERT INTO study_review VALUES (?,?,?,?)',
                  (identity, plan, 'legacy', json.dumps(dict(task_id='legacy',plan_id=plan,plan_revision=revision,question=question))))
    c.commit()
    choices = r.choices(plan, revision)
    assert len(choices) == 2 and all(x[2] for x in choices)
    assert not r.choices('other-plan', revision)
    assert not r.choices(plan, 'other-revision')
    r.register('legacy', plan, revision, 'Original wording')
    assert r.choices(plan, revision) == [('legacy', 'Original wording', False)]
    with pytest.raises(ValueError):r.register('legacy', plan, revision, 'Rewritten')
    assert c.execute('SELECT count(*) FROM study_review').fetchone()[0] == 2


def test_switch_failure_and_cancel_preserve_active_identity(cockpit, monkeypatch):
    window, c = cockpit
    task = window.integrated_study_task
    task.question.setText('Keep this task')
    before = task.task_id
    monkeypatch.setattr(QInputDialog, 'getItem', lambda *a: ('', False))
    task.resume_button.click()
    assert task.task_id == before
    original_register = window.study_task_registry.register
    def fail(*a):raise sqlite3.OperationalError('unavailable')
    monkeypatch.setattr(window.study_task_registry, 'register', fail)
    task.new_task_button.click()
    assert task.task_id == before and task.question.text() == 'Keep this task'
    assert 'not switched' in task.status.text()
    monkeypatch.setattr(window.study_task_registry, 'register', original_register)
    original_register('another-id', window.trade_plan.id, window.trade_plan.revision, 'Keep this task')
    assert len(window.study_task_registry.choices(window.trade_plan.id, window.trade_plan.revision)) == 2
