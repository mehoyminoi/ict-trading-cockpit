"""Optional investigation synthesis beside existing source inspection."""
from datetime import datetime, timezone
from uuid import uuid4
import sqlite3
import json
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit, QPushButton, QListWidget, QTextBrowser, QMessageBox
from ict_cockpit.database.study_review_repository import describe_review


class StudyReviewPanel(QWidget):
    def __init__(self, repository, *, plan_id, plan_revision, task_id, question, parent=None):
        super().__init__(parent)
        self.repository = repository
        self.scope = dict(plan_id=plan_id, plan_revision=plan_revision, task_id=task_id, question=question)
        self.sources = []
        self.pending = None
        self.saved = False
        self.identity = str(uuid4())
        layout = QVBoxLayout(self)
        label = QLabel('Keep what matters from this study pause. Any prompt may be left empty; no conclusion is required.')
        label.setWordWrap(True)
        layout.addWidget(label)
        self.fields = {}
        self._question_field = None
        self._pending_question = None
        for key, prompt in [('understanding', 'What did I learn?'), ('uncertainty', 'What remains uncertain or conflicts?'), ('next_step', 'What would be useful to study next?')]:
            editor = QPlainTextEdit()
            editor.setPlaceholderText(prompt)
            editor.setMaximumHeight(75)
            layout.addWidget(editor)
            self.fields[key] = editor
            editor.installEventFilter(self)
            editor.selectionChanged.connect(lambda k=key: self._remember_question_selection(k))
        self.keep_question_button = QPushButton('Keep question for later')
        self.keep_question_button.setToolTip('Select wording in a review prompt to save directly; no selection opens the question composer.')
        self.keep_question_button.clicked.connect(self.keep_question)
        layout.addWidget(self.keep_question_button)
        self.question_feedback = QLabel()
        self.question_feedback.setWordWrap(True)
        layout.addWidget(self.question_feedback)
        self.add_source_button = QPushButton('Use selected material as support')
        layout.addWidget(self.add_source_button)
        self.support = QListWidget()
        self.support.setMaximumHeight(65)
        layout.addWidget(self.support)
        self.remove_source_button = QPushButton('Remove selected support')
        self.remove_source_button.clicked.connect(self.remove_source)
        layout.addWidget(self.remove_source_button)
        self.save_button = QPushButton('Keep review checkpoint')
        self.save_button.clicked.connect(self.save)
        layout.addWidget(self.save_button)
        self.new_button = QPushButton('Start a later checkpoint')
        self.new_button.setEnabled(False)
        self.new_button.clicked.connect(self.start_new)
        layout.addWidget(self.new_button)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addWidget(QLabel('Saved checkpoints · newest first'))
        self.history = QListWidget()
        self.history.setMaximumHeight(65)
        self.history.currentRowChanged.connect(self.inspect)
        layout.addWidget(self.history)
        self.detail = QTextBrowser()
        layout.addWidget(self.detail, 1)
        self.records = []
        self.refresh()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.FocusIn:
            self._question_field = next((k for k, editor in self.fields.items() if editor is watched), self._question_field)
        return super().eventFilter(watched, event)

    def _remember_question_selection(self, key):
        if self.fields[key].textCursor().hasSelection():
            self._question_field = key

    def keep_question(self):
        from ict_cockpit.database.study_question_repository import StudyQuestionRepository
        from ict_cockpit.gui.study_question_dialog import StudyQuestionDialog
        editor = self.fields.get(self._question_field)
        selected = editor.textCursor().selectedText().replace('\u2029', '\n') if editor else ''
        source = json.loads(json.dumps(dict(kind='review', review_id=self.identity, **self.scope,
            state='Saved review snapshot' if self.saved else 'Draft review snapshot',
            selected_field=self._question_field if selected else '',
            fields={k: e.toPlainText() for k, e in self.fields.items()}, sources=self.sources)))
        repository = StudyQuestionRepository(self.repository.connection)
        if not selected.strip():
            dialog = StudyQuestionDialog(repository, plan_id=self.scope['plan_id'],
                plan_revision=self.scope['plan_revision'], source=source, parent=self)
            dialog.exec()
            if dialog.saved:
                self.question_feedback.setText('Question kept in the existing Study inbox. Review remains unchanged.')
            return
        item = dict(version=2, id=str(uuid4()), plan_id=self.scope['plan_id'], plan_revision=self.scope['plan_revision'],
                    question=selected.strip(), original_text=selected, source=source,
                    recorded_at=datetime.now(timezone.utc).isoformat())
        if self._pending_question and all(self._pending_question[k] == item[k] for k in item if k not in ('id', 'recorded_at')):
            item = self._pending_question
        self._pending_question = item
        try:
            repository.save(item)
        except (ValueError, RuntimeError, sqlite3.Error) as error:
            self.question_feedback.setText(f'Question not saved: {error}. Review wording remains here; retry when ready.')
            return
        self.question_feedback.setText('Question kept in the existing Study inbox. Review remains unchanged.')

    def add_source(self, kind, identity, label):
        if self.saved:
            return
        try:
            source = self.repository.source(kind, identity, self.scope['plan_id'], self.scope['task_id'])
            if any(s['kind'] == kind and s['id'] == identity for s in self.sources):
                return
            self.sources.append(source)
            self.support.addItem(label)
            self.status.setText('Selected material retained as support. Other items are not automatically included.')
        except (ValueError, sqlite3.Error) as error:
            self.status.setText(f'Support not added: {error}')

    def remove_source(self):
        row = self.support.currentRow()
        if not self.saved and 0 <= row < len(self.sources):
            self.sources.pop(row)
            self.support.takeItem(row)

    def save(self):
        if self.saved:
            return
        item = dict(version=1, id=self.identity, **self.scope,
                    **{k: e.toPlainText() for k,e in self.fields.items()},
                    sources=list(self.sources), recorded_at=datetime.now(timezone.utc).isoformat())
        if self.pending and all(self.pending[k] == item[k] for k in item if k != 'recorded_at'):
            item = self.pending
        self.pending = item
        try:
            self.repository.save(item)
        except (ValueError, RuntimeError, sqlite3.Error) as error:
            self.status.setText(f'Review not saved: {error}. Your input remains here.')
            return
        self.saved = True
        for editor in self.fields.values():
            editor.setReadOnly(True)
        for button in (self.save_button, self.add_source_button, self.remove_source_button):
            button.setEnabled(False)
        self.new_button.setEnabled(True)
        self.refresh()
        self.status.setText('Review kept. Return to study whenever ready; the investigation remains open.')

    def start_new(self):
        if not self.saved:
            return
        self.saved = False
        self.identity = str(uuid4())
        self.pending = None
        self.sources = []
        self.support.clear()
        for editor in self.fields.values():
            editor.setReadOnly(False)
            editor.clear()
        for button in (self.save_button, self.add_source_button, self.remove_source_button):
            button.setEnabled(True)
        self.new_button.setEnabled(False)
        self._pending_question = None
        self._question_field = None
        self.question_feedback.clear()
        self.status.setText('Fresh checkpoint; earlier reviews remain below.')

    def refresh(self):
        try:
            self.records = self.repository.list_for_task(self.scope['plan_id'], self.scope['task_id'])
            self.history.clear()
            for item in self.records:
                summary = next(item[k].strip() for k in ('understanding','uncertainty','next_step') if item[k].strip())
                self.history.addItem(f"{item['recorded_at']} · {summary[:80]}")
            if self.records:
                self.history.setCurrentRow(0)
        except (ValueError, sqlite3.Error) as error:
            self.status.setText(f'Could not load review history: {error}')

    def inspect(self, row):
        if 0 <= row < len(self.records):
            self.detail.setPlainText(describe_review(self.records[row]))

    def can_leave(self):
        if self.saved or not (self.sources or any(e.toPlainText().strip() for e in self.fields.values())):
            return True
        return QMessageBox.question(self, 'Unsaved review',
            'Discard this unsaved review and return? Saved material and your capture remain unchanged.',
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.Discard
