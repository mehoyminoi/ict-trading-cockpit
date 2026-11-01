"""Retain an insight without turning it into a question or completing an investigation."""
from datetime import datetime, timezone
from uuid import uuid4
import json
import sqlite3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPlainTextEdit, QPushButton,
                              QComboBox, QCheckBox, QListWidget, QTextBrowser, QMessageBox)
from ict_cockpit.database.study_finding_repository import describe_finding


class StudyFindingDialog(QDialog):
    def __init__(self, repository, *, plan_id, plan_revision, source=None,
                 original_text='', destination=None, parent=None):
        super().__init__(parent)
        self.repository = repository
        self.plan_id = plan_id
        self.plan_revision = plan_revision
        self.source = json.loads(json.dumps(source)) if source else None
        self.destination = json.loads(json.dumps(destination)) if destination else None
        self.original_text = original_text
        self.identity = str(uuid4())
        self.pending_item = None
        self.saved = False
        self.records = []
        self.setWindowTitle('Study findings · insights and partial answers')
        self.resize(820, 680)
        layout = QVBoxLayout(self)
        self.text = QPlainTextEdit(original_text)
        self.text.setPlaceholderText('What did you learn? Include uncertainty or alternative explanations where useful.')
        self.text.setMaximumHeight(120)
        self.kind = QComboBox()
        self.kind.addItems(['Finding', 'Partial answer'])
        self.associate = QCheckBox('Associate this finding with the investigation shown below')
        self.associate.setEnabled(bool(destination))
        target = destination
        self.destination_label = QLabel(
            f"{target['question']}\n{target['instrument']} · {target['market_reference']} · {target['interpretation']}\n"
            f"Capture: {source['date']} · {source['instrument']} · {source['session']}. Check both contexts before associating."
            if target else 'No investigation destination available. Open capture from an investigation with a question to associate a finding.')
        self.destination_label.setTextFormat(Qt.TextFormat.PlainText)
        self.destination_label.setWordWrap(True)
        self.save_button = QPushButton('Keep finding')
        self.status = QLabel()
        self.status.setWordWrap(True)
        if source:
            layout.addWidget(QLabel('Retain an interpretation; this does not complete or validate an investigation.'))
            for widget in (self.text, self.kind, self.associate, self.destination_label, self.save_button):
                layout.addWidget(widget)
        else:
            for widget in (self.text, self.kind, self.associate, self.destination_label, self.save_button):
                widget.hide()
        layout.addWidget(self.status)
        layout.addWidget(QLabel('Saved findings for this Trade Plan · newest first'))
        self.items = QListWidget()
        self.items.setMaximumHeight(120)
        layout.addWidget(self.items)
        self.detail = QTextBrowser()
        layout.addWidget(self.detail, 1)
        close = QPushButton('Return to current work')
        close.clicked.connect(self.reject)
        layout.addWidget(close)
        self.save_button.clicked.connect(self.save)
        self.items.currentRowChanged.connect(self.inspect)
        self.refresh()

    def refresh(self):
        try:
            self.records = self.repository.list_for_plan(self.plan_id)
            self.items.clear()
            for item in self.records:
                self.items.addItem(f"{item['kind']} · {item['finding']}".replace('\n', ' ')[:180])
            if self.records:
                self.items.setCurrentRow(0)
            else:
                self.detail.setPlainText('No retained findings yet. Select wording in Study Find and choose Keep finding…')
        except (ValueError, sqlite3.Error) as error:
            self.status.setText(f'Could not load findings: {error}')

    def inspect(self, row):
        if 0 <= row < len(self.records):
            self.detail.setPlainText(describe_finding(self.records[row]))

    def save(self):
        if self.saved or self.source is None:
            return
        item = dict(version=1, id=self.identity, plan_id=self.plan_id, plan_revision=self.plan_revision,
                    finding=self.text.toPlainText().strip(), kind=self.kind.currentText(),
                    original_text=self.original_text, source=self.source,
                    investigation=self.destination if self.associate.isChecked() else None,
                    recorded_at=datetime.now(timezone.utc).isoformat())
        if self.pending_item is not None and all(self.pending_item[k] == item[k]
                for k in item if k != 'recorded_at'):
            item = self.pending_item
        self.pending_item = item
        try:
            self.repository.save(item)
        except (ValueError, RuntimeError, sqlite3.Error) as error:
            self.status.setText(f'Finding not saved: {error}. Your text remains here.')
            return
        self.saved = True
        self.text.setReadOnly(True)
        for widget in (self.kind, self.associate, self.save_button):
            widget.setEnabled(False)
        self.refresh()
        self.status.setText('Finding kept. Continue your current study whenever ready.')

    def reject(self):
        if self.source and not self.saved and self.text.toPlainText().strip():
            answer = QMessageBox.question(self, 'Unsaved finding',
                'Discard this unsaved finding and return? Your source capture remains unchanged.',
                QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel)
            if answer != QMessageBox.StandardButton.Discard:
                return
        super().reject()
