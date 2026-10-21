"""Pinned, candidate-only criteria editing over explicit quarter scopes."""
import sqlite3
from uuid import uuid4

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QSpinBox, QTableWidget, QTextBrowser, QWidget,
    QMessageBox, QScrollArea,
)
from ict_cockpit.analysis.amdx import XSubtype, available_roles
from ict_cockpit.analysis.amdx_rules import Condition, Definition, Operator, OutputKind, QuartetScope


class AMDXCriteriaDialog(QDialog):
    def __init__(self, repository, *, plan_revision, cycle, instrument, reference, parent=None):
        super().__init__(parent)
        self.repository, self.plan_revision, self.cycle = repository, plan_revision, cycle
        self.editing = False
        self.rule_id = None
        self.setWindowTitle("Study criteria · candidate definitions")
        self.resize(1000, 720)
        outer = QVBoxLayout(self)
        context = QLabel(f"{instrument} · {cycle.layer} · {reference}\n"
                         f"Pinned quartet: {cycle.quarters[0].label} → {cycle.quarters[-1].label}\n"
                         f"Plan revision {plan_revision}. Saving creates a candidate only; it does not classify price, change AMDX or adopt a rule.")
        context.setWordWrap(True)
        outer.addWidget(context)
        content = QWidget()
        layout = QVBoxLayout(content)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)
        self.browser = QComboBox()
        self.browser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.browser.setMinimumContentsLength(40)
        layout.addWidget(self.browser)
        self.details = QTextBrowser()
        self.details.setMinimumHeight(130)
        layout.addWidget(self.details)
        row = QHBoxLayout()
        self.new_button = QPushButton("New candidate")
        self.edit_button = QPushButton("Create candidate revision")
        row.addWidget(self.new_button)
        row.addWidget(self.edit_button)
        layout.addLayout(row)
        self.form = QWidget()
        form = QFormLayout(self.form)
        self.rationale = QLineEdit()
        self.rationale.setPlaceholderText("Explain the criterion and why it is worth studying")
        form.addRow("Criterion / rationale", self.rationale)
        self.output = QComboBox()
        for kind in OutputKind:
            self.output.addItem(kind.value, kind.value)
        form.addRow("Output meaning", self.output)
        self.target = QComboBox()
        for q in cycle.quarters:
            self.target.addItem(f"Q{q.position} · {q.label}", q.position)
        form.addRow("Output quarter", self.target)
        self.role = QComboBox()
        form.addRow("Proposed role / behavior", self.role)
        self.priority = QSpinBox()
        self.priority.setRange(0, 2147483647)
        form.addRow("Priority (smaller wins)", self.priority)
        self.conditions = QTableWidget(0, 6)
        self.conditions.setHorizontalHeaderLabels(["Input quarter", "Feature name", "Comparison", "Value type", "Value", "Unit"])
        self.conditions.setMinimumHeight(170)
        form.addRow(QLabel("All conditions must match. Fixed inputs keep their original date; reusable inputs follow Q1–Q4 of each selected quartet."))
        form.addRow(self.conditions)
        condition_actions = QHBoxLayout()
        self.add_button = QPushButton("Add condition")
        self.remove_button = QPushButton("Remove selected condition")
        condition_actions.addWidget(self.add_button)
        condition_actions.addWidget(self.remove_button)
        form.addRow(condition_actions)
        layout.addWidget(self.form)
        actions = QHBoxLayout()
        self.save_button = QPushButton("Save candidate revision")
        self.discard_button = QPushButton("Discard draft")
        close = QPushButton("Return to investigation")
        for button in (self.save_button, self.discard_button, close):
            actions.addWidget(button)
        outer.addLayout(actions)
        self.status = QLabel()
        self.status.setWordWrap(True)
        outer.addWidget(self.status)
        self.browser.currentIndexChanged.connect(self.inspect)
        self.new_button.clicked.connect(self.new_candidate)
        self.edit_button.clicked.connect(self.edit_selected)
        self.target.currentIndexChanged.connect(self._roles)
        self.output.currentIndexChanged.connect(self._roles)
        self.add_button.clicked.connect(lambda: self.add_condition())
        self.remove_button.clicked.connect(lambda: self.conditions.removeRow(self.conditions.currentRow()))
        self.save_button.clicked.connect(self.save)
        self.discard_button.clicked.connect(self.discard)
        close.clicked.connect(self.reject)
        self._roles()
        self._set_editing(False)
        self.reload()

    def _set_editing(self, editing):
        self.editing = editing
        self.form.setEnabled(editing)
        self.save_button.setEnabled(editing)
        self.discard_button.setEnabled(editing)
        self.browser.setEnabled(not editing)
        self.new_button.setEnabled(not editing)
        self.edit_button.setEnabled(not editing and self.browser.currentData() is not None)

    def reload(self, selected=None):
        self.browser.blockSignals(True)
        self.browser.clear()
        self.browser.addItem("Choose a retained definition…", None)
        try:
            definitions = self.repository.list_revisions(plan_revision=self.plan_revision)
            for d in definitions:
                if d.layer != self.cycle.layer:
                    continue
                self.browser.addItem(f"{d.publication} · {d.rationale} · {d.revision}", d)
                if selected is not None and d == selected:
                    self.browser.setCurrentIndex(self.browser.count()-1)
        except (ValueError, sqlite3.Error) as exc:
            self.status.setText(f"Definitions could not be loaded: {exc}")
        finally:
            self.browser.blockSignals(False)
        self.inspect()

    def inspect(self, *_):
        d = self.browser.currentData()
        self.edit_button.setEnabled(d is not None and not self.editing)
        if d is None:
            self.details.setPlainText("No definition selected. This browser lists retained candidates and published records for this plan revision and layer. A published record is not proof of active plan adoption.")
            return
        quarter_names = {q.id: f"Q{q.position} · {q.label}" for q in self.cycle.quarters}
        lines = [f"{d.publication} · {d.id} @ {d.revision}", f"Plan {d.plan_revision} · {d.layer}",
                 d.rationale, f"Output: {d.output_kind.value} · Q{d.target_position} · {d.role.value}" + (f"({d.subtype.value})" if d.subtype else ""),
                 f"Priority: {d.priority} (smaller wins)", "Inputs (all required):"]
        for c in d.conditions:
            if isinstance(c.scope_id, QuartetScope):
                q = self.cycle.quarters[c.scope_id.position - 1]
                scope = f"Reusable: selected quartet Q{q.position} → {q.label} ({q.start.isoformat()})"
            else:
                scope = quarter_names.get(c.scope_id, f"Outside pinned quartet: {c.scope_id}")
                scope = f"Fixed: {scope}"
            lines.append(f"{scope}: {c.key} {c.operator.value} {c.value!r} {c.unit}")
        self.details.setPlainText("\n".join(lines))

    def _roles(self, *_):
        previous = self.role.currentData()
        self.role.clear()
        allowed = "".join(role.value for role in available_roles(self.target.currentData() or 1))
        if self.output.currentData() == OutputKind.LOCAL_BEHAVIOR.value:
            allowed = "AMDX"
        for role in allowed:
            self.role.addItem(role, role + "|")
            if role == "X":
                for subtype in XSubtype:
                    self.role.addItem(f"X({subtype.value})", role + "|" + subtype.value)
        index = self.role.findData(previous)
        if index >= 0:
            self.role.setCurrentIndex(index)

    def add_condition(self, condition=None):
        row = self.conditions.rowCount()
        self.conditions.insertRow(row)
        scope = QComboBox()
        for q in self.cycle.quarters:
            scope.addItem(f"Fixed Q{q.position} · {q.label}", q.id)
        for q in self.cycle.quarters:
            scope.addItem(f"Reusable Q{q.position} · selected quartet", QuartetScope(q.position))
        if condition is not None:
            index = next((i for i in range(scope.count()) if scope.itemData(i) == condition.scope_id), -1)
            if index < 0:
                scope.addItem(f"Outside quartet: {condition.scope_id}", condition.scope_id)
                index = scope.count()-1
            scope.setCurrentIndex(index)
        scope.setToolTip("Fixed keeps an exact quarter identity. Reusable selects that position in the explicitly evaluated quartet; it does not fetch facts or adopt a rule.")
        key = QLineEdit(condition.key if condition else "")
        operator = QComboBox()
        for op in Operator:
            operator.addItem({"eq":"equals", "gt":">", "ge":">=", "lt":"<", "le":"<="}[op.value], op.value)
        kind = QComboBox()
        kind.addItems(["Boolean", "Number", "Text"])
        value = QLineEdit()
        unit = QLineEdit(condition.unit if condition else "")
        if condition:
            operator.setCurrentIndex(operator.findData(condition.operator.value))
            kind.setCurrentText("Boolean" if type(condition.value) is bool else "Number" if type(condition.value) in (int, float) else "Text")
            value.setText(str(condition.value))
        value.setPlaceholderText("True / False, number, or text")
        for column, widget in enumerate((scope, key, operator, kind, value, unit)):
            self.conditions.setCellWidget(row, column, widget)
        self.conditions.resizeColumnsToContents()

    def new_candidate(self):
        self.rule_id = str(uuid4())
        self.rationale.clear()
        self.priority.setValue(0)
        self.output.setCurrentIndex(0)
        self.target.setCurrentIndex(0)
        self.conditions.setRowCount(0)
        self.add_condition()
        self._set_editing(True)
        self.status.setText("Unsaved candidate. Choose input and output quarters separately; use explicit features, not a prose classifier.")

    def edit_selected(self):
        d = self.browser.currentData()
        if d is None:
            return
        self.rule_id = d.id
        self.rationale.setText(d.rationale)
        self.priority.setValue(d.priority)
        self.output.setCurrentIndex(self.output.findData(d.output_kind.value))
        self.target.setCurrentIndex(self.target.findData(d.target_position))
        self._roles()
        index = self.role.findData(d.role.value + "|" + (d.subtype.value if d.subtype else ""))
        if index < 0:
            self.status.setText("This retained output conflicts with structural choices. Inspect it without rewriting; create a new candidate deliberately.")
            return
        self.role.setCurrentIndex(index)
        self.conditions.setRowCount(0)
        for condition in d.conditions:
            self.add_condition(condition)
        self._set_editing(True)
        self.status.setText(f"New candidate revision of {d.id} @ {d.revision}. Existing input scopes are preserved, including any outside this quartet.")

    def save(self):
        try:
            conditions = []
            for row in range(self.conditions.rowCount()):
                scope, key, operator, kind, value, unit = [self.conditions.cellWidget(row, col) for col in range(6)]
                raw = value.text()
                if kind.currentText() == "Boolean":
                    if raw.lower() not in ("true", "false"):
                        raise ValueError(f"Condition {row+1}: Boolean value must be True or False")
                    parsed = raw.lower() == "true"
                elif kind.currentText() == "Number":
                    try:
                        parsed = int(raw)
                    except ValueError:
                        parsed = float(raw)
                else:
                    parsed = raw
                conditions.append(Condition(scope.currentData(), key.text().strip(), operator.currentData(), parsed, unit.text()))
            role, subtype = self.role.currentData().split("|")
            subtype = subtype or None
            definition = Definition(self.rule_id, str(uuid4()), self.plan_revision, "Candidate", self.cycle.layer,
                                    self.target.currentData(), self.output.currentData(), role, self.priority.value(),
                                    tuple(conditions), self.rationale.text().strip(), subtype)
            saved = self.repository.save_candidate(definition)
        except (ValueError, RuntimeError, sqlite3.Error) as exc:
            self.status.setText(f"Not saved: {exc}. Your draft remains open.")
            return
        self._set_editing(False)
        self.reload(saved)
        self.status.setText("Candidate revision saved. Existing revisions and AMDX entries are unchanged. No rule was adopted or evaluated.")

    def discard(self):
        self._set_editing(False)
        self.inspect()
        self.status.setText("Draft discarded; retained definitions are unchanged.")

    def reject(self):
        if self.editing and QMessageBox.question(self, "Unsaved candidate", "Discard this unsaved candidate and return?",
                QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel) != QMessageBox.StandardButton.Discard:
            return
        super().reject()
