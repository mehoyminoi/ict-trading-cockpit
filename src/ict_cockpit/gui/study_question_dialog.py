"""Park a follow-up without replacing the current Study question or capture."""
from datetime import datetime, timezone
from uuid import uuid4
import json
import sqlite3
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPlainTextEdit,
                              QPushButton, QListWidget, QTextBrowser, QMessageBox)


class StudyQuestionDialog(QDialog):
    def __init__(self, repository, *, plan_id, plan_revision, source=None, original_text='', parent=None):
        super().__init__(parent)
        self.repository = repository
        self.plan_id = plan_id
        self.source = json.loads(json.dumps(source)) if source else None
        self.original_text = original_text
        self.identity = str(uuid4())
        self.saved = False
        self.pending_item = None
        self.setWindowTitle('Study questions · keep for later')
        self.resize(850, 700)
        layout = QVBoxLayout(self)
        self.question = QPlainTextEdit(original_text)
        self.question.setPlaceholderText('What would you like to investigate later?')
        self.question.setMaximumHeight(110)
        self.save_button = QPushButton('Keep question for later')
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.records = []
        if source:
            label = QLabel('Keep the question and a snapshot of this source. Your current investigation stays in place. '
                           'Selected wording is retained separately if you refine it below.')
            label.setWordWrap(True)
            layout.addWidget(label)
            layout.addWidget(self.question)
            layout.addWidget(self.save_button)
        else:
            self.question.hide()
            self.save_button.hide()
        layout.addWidget(self.status)
        layout.addWidget(QLabel('Saved questions for this Trade Plan · newest first'))
        self.items = QListWidget()
        self.items.setMaximumHeight(150)
        layout.addWidget(self.items)
        self.detail = QTextBrowser()
        layout.addWidget(self.detail, 1)
        close = QPushButton('Return to current work')
        close.clicked.connect(self.reject)
        layout.addWidget(close)
        self.save_button.clicked.connect(lambda: self.save(plan_revision))
        self.items.currentRowChanged.connect(self.inspect)
        self.refresh()

    def refresh(self):
        try:
            self.records = self.repository.list_for_plan(self.plan_id)
            self.items.clear()
            for item in self.records:
                self.items.addItem(item['question'].replace('\n', ' ')[:180])
            if self.records:
                self.items.setCurrentRow(0)
            else:
                self.detail.setPlainText('No saved questions yet. Select wording in Study Find or a review prompt, then choose Keep question for later; no selection opens the composer.')
        except (ValueError, sqlite3.Error) as error:
            self.status.setText(f'Could not load questions: {error}')

    def inspect(self, row):
        if not 0 <= row < len(self.records):
            return
        item = self.records[row]
        source = item['source']
        if item['version'] == 2:
            from ict_cockpit.database.study_question_repository import describe_review_question
            self.detail.setPlainText(describe_review_question(item))
            return
        association = source.get('association')
        context = (f"Linked investigation: {association['question']}\nReference: {association['market_reference']}"
                   if association else 'No explicit saved investigation association at capture time.')
        self.detail.setPlainText(
            f"Question: {item['question']}\n\nOriginal selected text: {item['original_text'] or '(none)'}\n\n"
            f"Plan revision: {item['plan_revision']} · recorded {item['recorded_at']}\n"
            f"Source capture {source['capture_id']} · {source['state']}\n"
            f"{source['date']} · {source['instrument'] or 'Instrument unknown'} · {source['session'] or 'Session unknown'}\n"
            f"{context}\n\nPattern: {source['pattern']}\nObservation: {source['observation']}\n\nNotes: {source['notes']}\n\n"
            'Chart references:\n' + ('\n'.join(source['images']) or '(none)') +
            '\n\nRetained source snapshot; later capture edits do not rewrite this question. Chart references do not duplicate image files. This is not a competency assessment.')

    def save(self, revision):
        if not self.question.toPlainText().strip():
            self.status.setText('Enter a question before keeping it.')
            return
        item = dict(version=2 if self.source.get("kind") == "review" else 1, id=self.identity, plan_id=self.plan_id, plan_revision=revision,
                    question=self.question.toPlainText().strip(), original_text=self.original_text,
                    source=self.source, recorded_at=datetime.now(timezone.utc).isoformat())
        if self.pending_item is not None and all(
                self.pending_item[k] == item[k] for k in item if k != 'recorded_at'):
            item = self.pending_item
        self.pending_item = item
        try:
            self.repository.save(item)
        except (ValueError, RuntimeError, sqlite3.Error) as error:
            self.status.setText(f'Question not saved: {error}. Your text remains here.')
            return
        self.saved = True
        self.question.setReadOnly(True)
        self.save_button.setEnabled(False)
        self.refresh()
        self.status.setText('Question kept. Return to your current work whenever ready.')

    def reject(self):
        if self.source and not self.saved and self.question.toPlainText().strip():
            answer = QMessageBox.question(self, 'Unsaved question',
                'Discard this unsaved question and return? Your source work will remain unchanged.',
                QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel)
            if answer != QMessageBox.StandardButton.Discard:
                return
        super().reject()
