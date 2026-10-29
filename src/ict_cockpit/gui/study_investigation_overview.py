"""Read-only investigation composition over existing immutable associations/results."""
import sqlite3
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QTextBrowser, QPushButton,
    QSplitter, QStackedWidget, QScrollArea,
)
from ict_cockpit.database.study_investigation_repository import describe_association
from ict_cockpit.gui.study_criterion_dialog import describe_result
from ict_cockpit.gui.study_find_review_widget import StudyFindReviewWidget
from ict_cockpit.database.study_finding_repository import StudyFindingRepository, describe_finding


class StudyInvestigationOverview(QDialog):
    def __init__(self, links, criteria, finds, *, task_id, plan_id, question, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Study investigation · retained material')
        self.resize(1050, 740)
        layout = QVBoxLayout(self)
        heading = QLabel(f'Study question: {question or "Not yet entered"}')
        heading.setWordWrap(True)
        layout.addWidget(heading)
        note = QLabel('Saved items retain their original questions and references. Association with this investigation '
                      'does not link a capture to a particular result or establish competency evidence.')
        note.setWordWrap(True)
        layout.addWidget(note)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.items = QListWidget()
        self.detail = QTextBrowser()
        self.find_review = StudyFindReviewWidget(finds)
        self.find_review.study_list.parentWidget().hide()
        self.pages = QStackedWidget()
        self.pages.addWidget(self.detail)
        self.find_scroll = QScrollArea()
        self.find_scroll.setWidgetResizable(True)
        self.find_scroll.setWidget(self.find_review)
        self.pages.addWidget(self.find_scroll)
        split = QSplitter()
        split.addWidget(self.items)
        split.addWidget(self.pages)
        split.setStretchFactor(1, 3)
        layout.addWidget(split, 1)
        close = QPushButton('Return to investigation')
        close.clicked.connect(self.accept)
        layout.addWidget(close)
        self.entries = []
        self.items.currentRowChanged.connect(self.inspect)
        try:
            results = tuple(r for r in criteria.list_for_task(task_id) if r.plan_id == plan_id)
            associations = tuple(r for r in links.list_for_task(task_id) if r['plan_id'] == plan_id)
            for record in results:
                e = record.evaluation
                self.entries.append(('result', record))
                self.items.addItem(f'{e.market_reference.isoformat()} · {e.results[0].state}\n'
                                   f'Criterion {e.definitions[0].revision} · {record.instrument}')
            saved_count = 0
            for association in associations:
                find = finds.get_by_id(association['capture_id'])
                draft = finds.connection.execute('SELECT pattern_name,observation,notes FROM study_find_draft WHERE id=?',
                                                (association['capture_id'],)).fetchone() if find is None else None
                state = 'Saved Study Find' if find else 'Linked draft' if draft else 'Capture unavailable'
                saved_count += int(find is not None)
                self.entries.append(('capture', (association, find, draft)))
                self.items.addItem(f'{association["market_reference"]} · {state}\n{association["instrument"]}')
            findings = StudyFindingRepository(finds.connection).list_for_task(plan_id, task_id)
            for finding in findings:
                self.entries.append(('finding', finding))
                self.items.addItem(f"{finding['kind']} · {finding['finding']}".replace('\n', ' ')[:180])
            self.summary.setText(f'{len(results)} saved criterion results · {saved_count} saved linked finds · '
                                 f'{len(associations) - saved_count} other capture associations · {len(findings)} findings/partial answers. '
                                 'Only explicitly associated material appears here.')
            if self.entries:
                self.items.setCurrentRow(0)
            else:
                self.detail.setPlainText('No retained material for this investigation yet.\n\n'
                    'Return to evaluate a criterion, or open Study Find, enter content and explicitly link the capture. '
                    'Unlinked finds remain available in Review saved finds.')
        except (ValueError, sqlite3.Error) as error:
            self.entries.clear()
            self.items.clear()
            self.summary.setText('Investigation material could not be loaded; no changes were made.')
            self.detail.setPlainText(str(error))

    def inspect(self, row):
        if not 0 <= row < len(self.entries):
            return
        kind, record = self.entries[row]
        if kind == 'finding':
            self.pages.setCurrentWidget(self.detail)
            self.detail.setPlainText(describe_finding(record))
            return
        if kind == 'result':
            self.pages.setCurrentWidget(self.detail)
            self.detail.setPlainText(describe_result(record))
            return
        association, find, draft = record
        if find is not None:
            self.find_review.study_finds = [find]
            self.find_review.show_selected_study_find(0)
            self.pages.setCurrentWidget(self.find_scroll)
        else:
            self.pages.setCurrentWidget(self.detail)
            self.detail.setPlainText(describe_association(association) + '\n\n' + (
                f'Linked draft (not a saved Study Find)\n{draft[0]}\n{draft[1]}\n{draft[2]}' if draft
                else 'Capture content unavailable. The association receipt remains; no content is inferred.'))
