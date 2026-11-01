"""Retained investigation intent; no run, evidence or AMDX command ownership."""
from uuid import uuid4

from PySide6.QtCore import Signal, QSettings
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


class IntegratedStudyTaskWidget(QWidget):
    overview_requested = Signal()
    capture_requested = Signal()
    review_requested = Signal()
    criteria_requested = Signal()
    evaluation_requested = Signal()

    def __init__(self, *, plan_id, revision, settings=None):
        super().__init__()
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
        row = QHBoxLayout()
        row.addWidget(QLabel("Study question"))
        self.question = QLineEdit()
        self.question.setPlaceholderText("What are you investigating? Calendar exploration needs no run.")
        if settings is not None:
            self.question.setText(str(settings.value(self.key, "")))
        row.addWidget(self.question, 1)
        self.new_task_button = QPushButton("New investigation")
        self.new_task_button.clicked.connect(self._new_task)
        row.addWidget(self.new_task_button)
        self.capture_button = QPushButton("Open Study Find")
        self.review_button = QPushButton("Review saved finds")
        row.addWidget(self.capture_button)
        row.addWidget(self.review_button)
        self.criteria_button = QPushButton("Study criteria…")
        row.addWidget(self.criteria_button)
        self.criteria_button.clicked.connect(self.criteria_requested.emit)
        layout.addLayout(row)
        self.overview_button = QPushButton("Investigation overview…")
        self.overview_button.clicked.connect(self.overview_requested.emit)
        layout.addWidget(self.overview_button)
        self.evaluate_button = QPushButton("Evaluate a criterion…")
        self.evaluate_button.clicked.connect(self.evaluation_requested.emit)
        layout.addWidget(self.evaluate_button)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.question.textChanged.connect(self._save)
        self.capture_button.clicked.connect(self.capture_requested.emit)
        self.review_button.clicked.connect(self.review_requested.emit)
        self.status.setText(f"Investigation draft · {revision} · separate from run intent and evidence. Historical reference and interpretation below belong to the calendar.")

    def _save(self):
        if self.settings is None:
            self.status.setText("Question retained in this window only; persistent workspace settings unavailable.")
            return
        self.settings.setValue(self.key, self.question.text())
        self.settings.setValue(self.key + "/task-id", self.task_id)
        self.settings.sync()
        self.status.setText(
            "Investigation question saved locally. Use Link this capture in Study Find to preserve an explicit association."
            if self.settings.status() == QSettings.Status.NoError
            else "Question could not be saved. Keep this window open and correct workspace storage."
        )

    def _new_task(self):
        self.task_id = str(uuid4())
        self.question.clear()
        self._save()
        self.status.setText("New investigation draft. Previously linked captures retain their recorded context.")
