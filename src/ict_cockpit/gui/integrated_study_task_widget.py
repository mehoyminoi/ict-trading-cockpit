"""Retained investigation intent; no run, evidence or AMDX command ownership."""
from uuid import uuid4
import sqlite3

from PySide6.QtCore import Signal, QSettings
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QInputDialog


class IntegratedStudyTaskWidget(QWidget):
    unfinished_capture_requested = Signal()
    overview_requested = Signal()
    checkpoint_requested = Signal()
    capture_requested = Signal()
    review_requested = Signal()
    criteria_requested = Signal()
    evaluation_requested = Signal()

    def __init__(self, *, plan_id, revision, settings=None, registry=None, can_switch=None):
        super().__init__()
        self.registry = registry
        self.plan_id, self.revision = plan_id, revision
        self.can_switch = can_switch or (lambda: True)
        self.settings = settings
        self.key = f"integrated-study/{plan_id}/{revision}/question"
        self.task_id = str(settings.value(self.key + "/task-id", "")) if settings else ""
        if not self.task_id:
            self.task_id = str(uuid4())
            if settings is not None:
                settings.setValue(self.key + "/task-id", self.task_id)
                settings.sync()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel("Study · current investigation")
        font = heading.font()
        font.setBold(True)
        heading.setFont(font)
        layout.addWidget(heading)
        row = QHBoxLayout()
        self.question = QLineEdit()
        self.question.setAccessibleName("Current study question")
        self.question.setPlaceholderText("What are you investigating?")
        if settings is not None:
            self.question.setText(str(settings.value(self.key, "")))
        row.addWidget(self.question, 1)
        self.resume_button = QPushButton("Resume investigation…")
        self.resume_button.setEnabled(registry is not None)
        self.resume_button.clicked.connect(self._resume)
        row.addWidget(self.resume_button)
        self.new_task_button = QPushButton("New investigation")
        self.new_task_button.clicked.connect(self._new_task)
        row.addWidget(self.new_task_button)
        layout.addLayout(row)
        self.question_state = QLabel()
        layout.addWidget(self.question_state)

        # Keep the explanation and recovery action beside the controls that were blocked.
        self.switch_notice = QWidget()
        notice_layout = QHBoxLayout(self.switch_notice)
        notice_layout.setContentsMargins(0, 0, 0, 0)
        message = QLabel("Switch paused: an unfinished Study Find contains work. Save it or deliberately discard it before switching.")
        message.setWordWrap(True)
        notice_layout.addWidget(message, 1)
        self.return_to_draft_button = QPushButton("Return to unfinished capture")
        self.return_to_draft_button.clicked.connect(self.unfinished_capture_requested.emit)
        notice_layout.addWidget(self.return_to_draft_button)
        layout.addWidget(self.switch_notice)
        self.switch_notice.hide()

        actions = QHBoxLayout()
        self.capture_button = QPushButton("Open Study Find")
        self.capture_button.setToolTip("Capture an example for this question; check the calendar reference first.")
        self.overview_button = QPushButton("Investigation overview…")
        self.overview_button.clicked.connect(self.overview_requested.emit)
        self.checkpoint_button = QPushButton("Review this investigation…")
        self.checkpoint_button.setToolTip("Take stock now; opens the review editor directly.")
        self.checkpoint_button.clicked.connect(self.checkpoint_requested.emit)
        for button in (self.capture_button, self.overview_button, self.checkpoint_button):
            actions.addWidget(button)
        layout.addLayout(actions)

        self.tools_toggle = QPushButton("Show supporting tools")
        self.tools_toggle.setCheckable(True)
        layout.addWidget(self.tools_toggle)
        self.supporting_tools = QWidget()
        self.support_layout = QVBoxLayout(self.supporting_tools)
        self.support_layout.setContentsMargins(0, 0, 0, 0)
        criteria_row = QHBoxLayout()
        criteria_row.addWidget(QLabel("Plan criteria"))
        self.criteria_button = QPushButton("Study criteria…")
        self.criteria_button.clicked.connect(self.criteria_requested.emit)
        criteria_row.addWidget(self.criteria_button)
        self.evaluate_button = QPushButton("Evaluate a criterion…")
        self.evaluate_button.clicked.connect(self.evaluation_requested.emit)
        criteria_row.addWidget(self.evaluate_button)
        self.support_layout.addLayout(criteria_row)
        self.library_actions = QHBoxLayout()
        self.library_actions.addWidget(QLabel("Retained work"))
        self.review_button = QPushButton("Review saved finds")
        self.library_actions.addWidget(self.review_button)
        self.support_layout.addLayout(self.library_actions)
        layout.addWidget(self.supporting_tools)
        self.supporting_tools.hide()
        self.tools_toggle.toggled.connect(self._show_tools)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.question.textChanged.connect(self._save)
        self.capture_button.clicked.connect(self.capture_requested.emit)
        self.review_button.clicked.connect(self.review_requested.emit)
        if registry:
            known = registry.connection.execute('SELECT question FROM study_task_registry WHERE task_id=? AND plan_id=? AND plan_revision=?', (self.task_id, plan_id, revision)).fetchone()
            if known:
                self.question.setText(known[0])
                self.question.setReadOnly(True)
        self._refresh_question_state()
        self.status.setText("Choose the chart date/session in the calendar, then Open Study Find. Resume leaves the calendar unchanged.")

    def _show_tools(self, visible):
        self.supporting_tools.setVisible(visible)
        self.tools_toggle.setText("Hide supporting tools" if visible else "Show supporting tools")

    def _refresh_question_state(self):
        self.question_state.setText(
            "Retained question · wording is read-only. Resume another question or use New investigation."
            if self.question.isReadOnly() else "New question · enter the question you want to investigate.")

    def show_switch_blocked(self):
        self.switch_notice.show()
        self.return_to_draft_button.setFocus()

    def _save(self):
        self._refresh_question_state()
        if self.settings is None:
            self.status.setText("Question retained in this window only; persistent workspace settings unavailable.")
            return
        self.settings.setValue(self.key, self.question.text())
        self.settings.setValue(self.key + "/task-id", self.task_id)
        self.settings.sync()
        self.status.setText(
            "Investigation question saved locally. Use Save to investigation in Study Find to save an associated example."
            if self.settings.status() == QSettings.Status.NoError
            else "Question could not be saved. Keep this window open and correct workspace storage."
        )

    def _retain_current(self):
        if self.registry and self.question.text().strip():
            self.registry.register(self.task_id, self.plan_id, self.revision, self.question.text())
            self.question.setReadOnly(True)
            self._refresh_question_state()

    def _resume(self):
        try:
            if not self.can_switch():
                return
            self._retain_current()
            choices = self.registry.choices(self.plan_id, self.revision)
            if not choices:
                self.status.setText("No named investigations in this plan revision yet. Older revisions remain in Study history.")
                return
            labels = [f"{q or '(unnamed)'} · {task}" + (" · historical wording: confirm to resume" if legacy else "")
                      for task, q, legacy in choices]
            label, ok = QInputDialog.getItem(self, "Resume investigation", "Choose wording and identity (current plan revision only):", labels, 0, False)
            if not ok:
                return
            task, question, legacy = choices[labels.index(label)]
            self.registry.register(task, self.plan_id, self.revision, question)
            self.task_id = task
            self.question.setText(question)
            self.question.setReadOnly(True)
            self._save()
            self.status.setText("Investigation resumed. Calendar reference unchanged. Saved wording is read-only; use New investigation for a different question.")
        except (ValueError, sqlite3.Error) as error:
            self.status.setText(f"Investigation not switched: {error}")

    def _new_task(self):
        if not self.can_switch():
            return
        try:
            self._retain_current()
        except (ValueError, sqlite3.Error) as error:
            self.status.setText(f"Investigation not switched: {error}")
            return
        self.question.setReadOnly(False)
        self.task_id = str(uuid4())
        self.question.clear()
        self._save()
        self.status.setText("New investigation draft. Previously linked captures retain their recorded context.")
