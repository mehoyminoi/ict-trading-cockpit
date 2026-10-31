"""Investigation inspection with optional review entry over shared retained material."""
import sqlite3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QTextBrowser, QPushButton,
    QSplitter, QStackedWidget, QScrollArea, QComboBox, QHBoxLayout,
)
from ict_cockpit.database.study_review_repository import StudyReviewRepository, describe_review
from ict_cockpit.database.study_investigation_repository import describe_association
from ict_cockpit.gui.study_criterion_dialog import describe_result
from ict_cockpit.gui.study_find_review_widget import StudyFindReviewWidget
from ict_cockpit.database.study_finding_repository import StudyFindingRepository, describe_finding


def preview(text, limit=105):
    """Display-only excerpt; the original record remains available in the inspector."""
    line = ' '.join(text.split())
    return line if len(line) <= limit else line[:limit - 1] + '…'


class StudyInvestigationOverview(QDialog):
    def __init__(self, links, criteria, finds, *, task_id, plan_id, question, plan_revision=None, review_open=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Study investigation · retained material')
        self.resize(1280, 800)
        layout = QVBoxLayout(self)
        heading = QLabel(f'Study question: {question or "Not yet entered"}')
        heading.setWordWrap(True)
        heading.setTextFormat(Qt.TextFormat.PlainText)
        font = heading.font()
        font.setBold(True)
        heading.setFont(font)
        layout.addWidget(heading)
        note = QLabel('Saved items retain their original questions and references. Association with this investigation '
                      'does not link a capture to a particular result or establish competency evidence.')
        note.setWordWrap(True)
        layout.addWidget(note)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel('Show material'))
        self.material_filter = QComboBox()
        for label, kind in [('All material', ''), ('Captures', 'capture'),
                            ('Findings / partial answers', 'finding'), ('Criterion results', 'result'),
                            ('Review checkpoints', 'review')]:
            self.material_filter.addItem(label, kind)
        self.material_filter.setAccessibleName('Investigation material type')
        filter_row.addWidget(self.material_filter)
        self.filter_status = QLabel()
        filter_row.addWidget(self.filter_status, 1)
        layout.addLayout(filter_row)
        self.items = QListWidget()
        self.items.setSpacing(5)
        self.items.setWordWrap(True)
        self.items.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.items.setMinimumWidth(240)
        self.items.setAccessibleName("Retained investigation material")
        self.detail = QTextBrowser()
        self.find_review = StudyFindReviewWidget(finds, compact=True)
        self.find_review.study_list.parentWidget().hide()
        self.pages = QStackedWidget()
        self.pages.addWidget(self.detail)
        self.find_scroll = QScrollArea()
        self.find_scroll.setWidgetResizable(True)
        self.find_scroll.setWidget(self.find_review)
        self.pages.addWidget(self.find_scroll)
        split = self.splitter = QSplitter()
        split.addWidget(self.items)
        split.addWidget(self.pages)
        split.setStretchFactor(1, 3)
        layout.addWidget(split, 1)
        from ict_cockpit.gui.study_review_panel import StudyReviewPanel
        self.review_panel = StudyReviewPanel(StudyReviewRepository(finds.connection),
            plan_id=plan_id, plan_revision=plan_revision or 'Unspecified', task_id=task_id,
            question=question, parent=self)
        split.addWidget(self.review_panel)
        split.setStretchFactor(2, 2)
        self.review_panel.setMinimumWidth(320)
        self.review_panel.hide()
        split.setSizes([300, 620, 340])
        self.review_toggle = QPushButton('Review this investigation…')
        self.review_toggle.setCheckable(True)
        self.review_toggle.toggled.connect(self._set_review_visible)
        layout.addWidget(self.review_toggle)
        self.review_panel.add_source_button.clicked.connect(self.use_selected_support)
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
                title = (find.pattern_name or find.observation) if find else (draft[0] or draft[1]) if draft else 'Content unavailable'
                excerpt = find.observation if find else draft[1] if draft else ''
                session = f' · {find.session}' if find and find.session else ''
                self.items.addItem(f'{state} · {preview(title, 70)}\n'
                                   f'{association["market_reference"]} · {association["instrument"]}{session}\n'
                                   f'{preview(excerpt)}')
            findings = StudyFindingRepository(finds.connection).list_for_task(plan_id, task_id)
            for finding in findings:
                self.entries.append(('finding', finding))
                self.items.addItem(f"{finding['kind']} · {finding['finding']}".replace('\n', ' ')[:180])
            reviews = self.review_panel.records
            for review in reviews:
                text = next(review[k] for k in ('understanding', 'uncertainty', 'next_step') if review[k].strip())
                self.entries.append(('review', review))
                self.items.addItem(f'Review checkpoint · {review["recorded_at"]}\n{preview(text)}')
            self.summary.setText(f'{len(results)} saved criterion results · {saved_count} saved linked finds · '
                                 f'{len(associations) - saved_count} other capture associations · {len(findings)} findings/partial answers. '
                                 f'{len(reviews)} review checkpoints. Only explicitly associated material appears here.')
            if self.entries:
                self.items.setCurrentRow(0)
            else:
                self.detail.setPlainText('No retained material for this investigation yet.\n\n'
                    'Return to Open Study Find, enter an example and use Save to investigation. '
                    'Unlinked finds remain available in Review saved finds.')
        except (ValueError, sqlite3.Error) as error:
            self.entries.clear()
            self.items.clear()
            self.summary.setText('Investigation material could not be loaded; no changes were made.')
            self.detail.setPlainText(str(error))

        self.material_filter.currentIndexChanged.connect(self._filter_material)
        self.review_toggle.setChecked(review_open)

    def _filter_material(self):
        kind = self.material_filter.currentData()
        visible = []
        for row, (entry_kind, _) in enumerate(self.entries):
            show = not kind or entry_kind == kind
            self.items.item(row).setHidden(not show)
            if show:
                visible.append(row)
        self.filter_status.setText(f"{len(visible)} matching items" if visible else "No material of this type")
        if self.items.currentRow() not in visible:
            self.items.setCurrentRow(visible[0] if visible else -1)
        if not visible:
            self.pages.setCurrentWidget(self.detail)
            self.detail.setPlainText('No material of this type. Choose All material to return. Your review entry is unchanged.')

    def _set_review_visible(self, visible):
        self.review_panel.setVisible(visible)
        self.review_toggle.setText('Hide review entry' if visible else 'Review this investigation…')
        if visible:
            self.review_panel.fields['understanding'].setFocus()

    def inspect(self, row):
        if not 0 <= row < len(self.entries):
            return
        kind, record = self.entries[row]
        if kind == 'review':
            self.pages.setCurrentWidget(self.detail)
            self.detail.setPlainText(describe_review(record))
            return
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

    def use_selected_support(self):
        row = self.items.currentRow()
        if not 0 <= row < len(self.entries):
            self.review_panel.status.setText('Select material in the investigation list first; support is optional.')
            return
        kind, record = self.entries[row]
        if kind == 'review':
            self.review_panel.status.setText('A checkpoint records reflection. Select a capture, finding or criterion result as support instead.')
            return
        identity = record['id'] if kind == 'finding' else record.evaluation.id if kind == 'result' else record[0]['capture_id']
        self.review_panel.add_source(kind, identity, self.items.item(row).text())

    def done(self, result):
        if self.review_panel.can_leave():
            super().done(result)
