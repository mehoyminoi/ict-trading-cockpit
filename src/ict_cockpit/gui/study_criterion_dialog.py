"""Question → retained criterion → explicit observations → explained result."""
from datetime import datetime, timezone
import sqlite3
from uuid import uuid4

from PySide6.QtCore import QDateTime, QTimeZone, Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTextBrowser, QGroupBox, QFormLayout, QDateTimeEdit,
    QScrollArea, QWidget, QMessageBox,
)
from ict_cockpit.analysis.amdx_rules import Fact, QuartetScope, evaluate
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.database.study_criterion_repository import StudyCriterionRecord


def describe_result(record):
    e = record.evaluation
    d = e.definitions[0]
    result = e.results[0]
    lines = [f'Question: {record.question}',
             f'{record.instrument} · {e.cycle.layer} · information reference {e.market_reference.isoformat()}',
             f'Criterion: {d.rationale}', f'{d.publication} · {d.id} @ {d.revision} · plan {d.plan_revision}',
             f'Result: {result.state}']
    if result.state == 'Matched':
        lines.append(f'The supplied observations satisfy this criterion. Its proposed {d.output_kind.value.lower()} is Q{d.target_position} = {d.role.value}' + (f'({d.subtype.value})' if d.subtype else '') + '.')
    elif result.state == 'Not Matched':
        lines.append('At least one available observation fails the declared condition; this does not prove an alternative AMDX profile.')
    elif result.state == 'Unknown':
        lines.append('The supplied information is insufficient at this reference. Missing or later information is not a negative observation.')
    else:
        lines.append('This criterion does not apply to the selected layer.')
    lines.extend(['', 'Criterion requires all of:'])
    for condition in d.conditions:
        scope = condition.scope_id.bind(e.cycle) if isinstance(condition.scope_id, QuartetScope) else condition.scope_id
        quarter = next((q for q in e.cycle.quarters if q.id == scope), None)
        label = f'Q{quarter.position} {quarter.label}' if quarter else f'fixed scope {scope}'
        comparison = {'eq': 'equals', 'gt': 'is greater than', 'ge': 'is at least', 'lt': 'is less than', 'le': 'is at most'}[condition.operator.value]
        lines.append(f'{label}: {condition.key} {comparison} {condition.value!r} {condition.unit}')
    lines.extend(['', 'Why:', *result.reasons, '', 'Retained observations:'])
    for fact in e.facts:
        lines.append(f'{fact.key}: {fact.value!r} {fact.unit} · source: {fact.source_ref}\n  Scope: {fact.scope_id}\n  Available: {fact.available_at.astimezone(MARKET_TIMEZONE).isoformat() if fact.available_at else "Unknown"}')
    if not e.facts:
        lines.append('No observations supplied.')
    lines.extend(['', 'This checks a criterion against supplied observations. It does not establish trading validity, adopt the criterion, change AMDX, or create competency evidence.'])
    return '\n'.join(lines)


class StudyCriterionDialog(QDialog):
    def __init__(self, repository, *, task_id, plan_id, plan_revision, question, instrument, cycle, reference, parent=None):
        super().__init__(parent)
        self.repository = repository
        self.task_id, self.plan_id, self.plan_revision = task_id, plan_id, plan_revision
        self.instrument, self.cycle, self.reference = instrument, cycle, reference
        self.preview_record = None
        self.dirty = False
        self.inputs = []
        self.criterion_index = 0
        self.setWindowTitle('Study a criterion · observations and result')
        self.resize(1000, 800)
        outer = QVBoxLayout(self)
        heading = QLabel(f'{instrument} · {cycle.layer} · pinned information reference {reference.isoformat()}\n'
                         'Choose one saved criterion. Supply observations and their source; blank values mean unknown. No Trading Run is needed.')
        heading.setWordWrap(True)
        outer.addWidget(heading)
        self.question = QLineEdit(question)
        self.question.setPlaceholderText('What question are you investigating?')
        outer.addWidget(QLabel('Study question'))
        outer.addWidget(self.question)
        self.criterion = QComboBox()
        self.criterion.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.criterion.setMinimumContentsLength(40)
        self.criterion.addItem('Choose a retained criterion…', None)
        for d in repository.amdx.definitions.list_revisions(plan_revision=plan_revision):
            if d.layer == cycle.layer:
                self.criterion.addItem(f'{d.publication} · {d.rationale} · {d.revision}', d)
        outer.addWidget(self.criterion)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.fields = QWidget()
        self.fields_layout = QVBoxLayout(self.fields)
        self.scroll.setWidget(self.fields)
        outer.addWidget(self.scroll, 1)
        actions = QHBoxLayout()
        self.preview_button = QPushButton('Explain result')
        self.save_button = QPushButton('Save this Study result')
        self.save_button.setEnabled(False)
        self.close_button = QPushButton('Return to investigation')
        for button in (self.preview_button, self.save_button, self.close_button):
            actions.addWidget(button)
        outer.addLayout(actions)
        self.saved = QComboBox()
        self.saved.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.saved.setMinimumContentsLength(40)
        outer.addWidget(QLabel('Saved results for this investigation (inspection leaves your current inputs unchanged)'))
        outer.addWidget(self.saved)
        self.result = QTextBrowser()
        self.result.setMinimumHeight(200)
        outer.addWidget(self.result, 1)
        self.status = QLabel('A matched criterion is not proof of a successful trade plan.')
        self.status.setWordWrap(True)
        outer.addWidget(self.status)
        self.question.textChanged.connect(self.invalidate)
        self.criterion.currentIndexChanged.connect(self.build_inputs)
        self.preview_button.clicked.connect(self.preview)
        self.save_button.clicked.connect(self.save)
        self.close_button.clicked.connect(self.reject)
        self.saved.currentIndexChanged.connect(self.inspect_saved)
        self.reload_saved()

    def invalidate(self, *_):
        self.preview_record = None
        self.save_button.setEnabled(False)
        self.dirty = True
        self.result.clear()
        self.status.setText('Inputs changed. Choose Explain result before saving.')

    def build_inputs(self, *_):
        if self.inputs and self.dirty and any(row[4].text() or row[5].text() for row in self.inputs):
            answer = QMessageBox.question(self, 'Change criterion', 'Discard current unsaved observations and choose another criterion?',
                QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
            if answer != QMessageBox.StandardButton.Discard:
                self.criterion.blockSignals(True)
                self.criterion.setCurrentIndex(self.criterion_index)
                self.criterion.blockSignals(False)
                return
        self.criterion_index = self.criterion.currentIndex()
        # Keep one observation per scope/key even when the criterion uses multiple thresholds.
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.inputs = []
        self.invalidate()
        d = self.criterion.currentData()
        if d is None:
            return
        seen = {}
        for condition in d.conditions:
            scope = condition.scope_id.bind(self.cycle) if isinstance(condition.scope_id, QuartetScope) else condition.scope_id
            key = (scope, condition.key)
            value_type = bool if type(condition.value) is bool else float if type(condition.value) in (int, float) else str
            signature = (condition.unit, value_type)
            if key in seen:
                if seen[key] != signature:
                    self.status.setText('This criterion expects incompatible types/units for one observation. Revise the criterion before evaluation.')
                    self.inputs = None
                    return
                continue
            seen[key] = signature
            quarter = next((q for q in self.cycle.quarters if q.id == scope), None)
            title = f'{condition.key} · ' + (f'Q{quarter.position} {quarter.label}' if quarter else f'fixed external scope {scope}')
            group = QGroupBox(title)
            form = QFormLayout(group)
            value = QLineEdit()
            value.setPlaceholderText('True or False; blank = unknown' if value_type is bool else 'Number; blank = unknown' if value_type is float else 'Text; blank = unknown')
            source = QLineEdit()
            source.setPlaceholderText('Chart observation, saved note reference, or synthetic fixture source')
            available = QDateTimeEdit()
            available.setTimeZone(QTimeZone(b'America/New_York'))
            available.setDateTime(QDateTime.fromString(self.reference.isoformat(), Qt.DateFormat.ISODate).toTimeZone(QTimeZone(b'America/New_York')))
            available.setDisplayFormat('yyyy-MM-dd HH:mm t')
            available.setCalendarPopup(True)
            form.addRow('Observed value' + (f' ({condition.unit})' if condition.unit else ''), value)
            form.addRow('Source / reference', source)
            form.addRow('Became available (New York)', available)
            self.fields_layout.addWidget(group)
            for widget in (value, source):
                widget.textChanged.connect(self.invalidate)
            available.dateTimeChanged.connect(self.invalidate)
            self.inputs.append((scope, condition.key, condition.unit, value_type, value, source, available))
        self.fields_layout.addStretch()

    def preview(self):
        try:
            d = self.criterion.currentData()
            if d is None or not self.question.text().strip():
                raise ValueError('Enter a Study question and choose a saved criterion')
            if self.inputs is None:
                raise ValueError('Resolve incompatible input types/units in the criterion first')
            facts = []
            for scope, key, unit, value_type, value, source, available in self.inputs:
                raw = value.text().strip()
                if not raw:
                    continue
                if not source.text().strip():
                    raise ValueError(f'Provide a source for {key}')
                if value_type is bool:
                    if raw.lower() not in ('true', 'false'):
                        raise ValueError(f'{key}: enter True or False, or leave blank for unknown')
                    parsed = raw.lower() == 'true'
                elif value_type is float:
                    parsed = float(raw)
                else:
                    parsed = raw
                facts.append(Fact(str(uuid4()), scope, key, parsed, unit,
                    datetime.fromtimestamp(available.dateTime().toSecsSinceEpoch(), timezone.utc), source.text().strip()))
            evaluation = evaluate(evaluation_id=str(uuid4()), run_id=None, cycle=self.cycle,
                market_reference=self.reference, definitions=(d,), facts=tuple(facts))
            self.preview_record = StudyCriterionRecord(self.task_id, self.plan_id, self.question.text().strip(),
                self.instrument, datetime.now(timezone.utc), evaluation)
            self.saved.blockSignals(True)
            self.saved.setCurrentIndex(0)
            self.saved.blockSignals(False)
            self.result.setPlainText('UNSAVED PREVIEW\n\n' + describe_result(self.preview_record))
            self.save_button.setEnabled(True)
            self.status.setText('Preview only. Save retains this exact question, criterion, observations and result.')
        except (ValueError, RuntimeError) as exc:
            self.preview_record = None
            self.save_button.setEnabled(False)
            self.status.setText(f'Cannot explain result: {exc}. Inputs remain available.')

    def save(self):
        if self.preview_record is None:
            return
        try:
            saved = self.repository.save(self.preview_record)
        except (ValueError, RuntimeError, sqlite3.Error) as exc:
            self.status.setText(f'Not saved: {exc}. The preview and inputs remain available; retry deliberately.')
            return
        self.dirty = False
        self.save_button.setEnabled(False)
        self.reload_saved(saved.evaluation.id)
        self.status.setText('Study result saved independently. No criterion was adopted and no AMDX entry changed.')

    def reload_saved(self, selected=None):
        self.saved.blockSignals(True)
        self.saved.clear()
        self.saved.addItem('Inspect a saved result…', None)
        for record in self.repository.list_for_task(self.task_id):
            e = record.evaluation
            self.saved.addItem(f'{e.market_reference.isoformat()} · {e.results[0].state} · {record.question}', e.id)
            if e.id == selected:
                self.saved.setCurrentIndex(self.saved.count()-1)
        self.saved.blockSignals(False)
        if selected:
            self.inspect_saved()

    def inspect_saved(self, *_):
        identity = self.saved.currentData()
        if identity is None:
            return
        try:
            record = self.repository.get(identity)
            self.result.setPlainText('SAVED STUDY RESULT\n\n' + describe_result(record))
            self.save_button.setEnabled(False)
            self.status.setText('Inspecting retained evidence. Current input fields are unchanged; Explain result returns to them.')
        except (ValueError, sqlite3.Error) as exc:
            self.status.setText(f'Cannot read saved result: {exc}')

    def reject(self):
        if self.dirty and QMessageBox.question(self, 'Unsaved Study inputs', 'Discard unsaved inputs/preview and return?',
                QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel) != QMessageBox.StandardButton.Discard:
            return
        super().reject()
