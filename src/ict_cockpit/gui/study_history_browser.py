"""Read-only retrieval across investigations; occurrence is not proficiency evidence."""
from datetime import datetime, timezone
import sqlite3
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                              QComboBox, QPushButton, QListWidget, QTextBrowser, QSplitter)
from ict_cockpit.database.study_question_repository import StudyQuestionRepository
from ict_cockpit.database.study_finding_repository import StudyFindingRepository, describe_finding
from ict_cockpit.database.study_review_repository import StudyReviewRepository, describe_review


def describe_question(item):
    source = item['source']
    association = source.get('association')
    context = (f"Source investigation: {association['question']}\nReference: {association['market_reference']}"
               if association else 'No saved investigation association in the source snapshot.')
    return (f"Question: {item['question']}\n\nOriginal wording: {item['original_text'] or '(none)'}\n"
            f"Plan {item['plan_revision']} · recorded {item['recorded_at']}\n{context}\n"
            f"Source: {source['date']} · {source['instrument']} · {source['session']} · {source['state']}\n"
            f"Pattern: {source['pattern']}\nObservation: {source['observation']}\nNotes: {source['notes']}\n"
            'Chart references:\n' + ('\n'.join(source['images']) or '(none)'))


class StudyHistoryBrowser(QDialog):
    def __init__(self, connection, *, plan_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Study history · questions, findings and reviews')
        self.resize(1100, 720)
        self.records = []
        self.visible_records = []
        self.load_error = False
        layout = QVBoxLayout(self)
        explanation = QLabel('Browse retained learning across investigations and revisions of this Trade Plan. '
            'Text matches help retrieve records; they do not measure frequency of mistakes or competency. '
            'Unlinked questions/findings remain visible. Standalone Study Finds are in Review saved finds.')
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search saved wording and retained context…')
        self.kind = QComboBox()
        self.kind.addItems(['All types', 'Question', 'Finding', 'Partial answer', 'Review'])
        row.addWidget(self.search, 1)
        row.addWidget(self.kind)
        clear = QPushButton('Clear filters')
        clear.clicked.connect(self.clear_filters)
        row.addWidget(clear)
        layout.addLayout(row)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.items = QListWidget()
        self.detail = QTextBrowser()
        split = QSplitter()
        split.addWidget(self.items)
        split.addWidget(self.detail)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 2)
        layout.addWidget(split, 1)
        close = QPushButton('Return to current work')
        close.clicked.connect(self.reject)
        layout.addWidget(close)
        self.items.currentRowChanged.connect(self.inspect)
        self.search.textChanged.connect(self.filter_records)
        self.kind.currentTextChanged.connect(self.filter_records)
        try:
            for item in StudyQuestionRepository(connection).list_for_plan(plan_id):
                self.add_record('Question', item['question'], item, describe_question(item))
            for item in StudyFindingRepository(connection).list_for_plan(plan_id):
                self.add_record(item['kind'], item['finding'], item, describe_finding(item))
            for item in StudyReviewRepository(connection).list_for_plan(plan_id):
                thought = next(item[k].strip() for k in ('understanding', 'uncertainty', 'next_step') if item[k].strip())
                self.add_record('Review', thought, item, describe_review(item))
            self.records.sort(key=lambda r: (datetime.fromisoformat(r['item']['recorded_at']).astimezone(timezone.utc),
                                              r['kind'], r['item']['id']), reverse=True)
        except (ValueError, KeyError, TypeError, sqlite3.Error) as error:
            self.records.clear()
            self.load_error = True
            self.status.setText(f'History could not be loaded completely: {error}. No records changed.')
            self.detail.setPlainText('Close and reopen after resolving the read error. An unavailable history is not an empty evidence set.')
            self.search.setEnabled(False)
            self.kind.setEnabled(False)
            clear.setEnabled(False)
        if not self.load_error:
            self.filter_records()

    def add_record(self, kind, title, item, detail):
        self.records.append(dict(kind=kind, title=title, item=item, detail=detail))

    def filter_records(self, *_):
        if self.load_error:
            return
        words = self.search.text().strip().casefold().split()
        kind = self.kind.currentText()
        self.visible_records = [r for r in self.records if (kind == 'All types' or r['kind'] == kind)
            and all(word in (r['title'] + '\n' + r['detail']).casefold() for word in words)]
        self.items.clear()
        self.detail.clear()
        for r in self.visible_records:
            self.items.addItem(f"{r['kind']} · {r['title'].replace(chr(10), ' ')[:110]}\n"
                               f"Recorded {r['item']['recorded_at']} · plan {r['item']['plan_revision']}")
        self.status.setText(f'{len(self.visible_records)} of {len(self.records)} retained records · newest recording first. '
                            'Recording time is distinct from historical market time; these are not counts of independent examples.')
        if self.visible_records:
            self.items.setCurrentRow(0)
        else:
            self.detail.setPlainText('No records match these filters.' if self.records else 'No saved questions, findings or reviews for this Trade Plan yet.')

    def inspect(self, row):
        if 0 <= row < len(self.visible_records):
            self.detail.setPlainText(self.visible_records[row]['detail'])

    def clear_filters(self):
        self.search.clear()
        self.kind.setCurrentIndex(0)
