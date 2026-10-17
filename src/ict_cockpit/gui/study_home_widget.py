"""Read-only Study doorway; the existing launcher owns preparation and launch."""

from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QVBoxLayout, QWidget


class StudyHomeWidget(QWidget):
    study_requested = Signal(str)
    resume_requested = Signal()
    capture_requested = Signal()
    calendar_requested = Signal()

    def __init__(self, competencies):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
        heading = QLabel("Study · choose the next useful task")
        heading.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(heading)
        self.run_label = QLabel()
        self.run_label.setWordWrap(True)
        layout.addWidget(self.run_label)
        self.resume_button = QPushButton("Resume active run")
        self.resume_button.clicked.connect(self.resume_requested.emit)
        layout.addWidget(self.resume_button)
        self.basis_label = QLabel()
        self.basis_label.setWordWrap(True)
        layout.addWidget(self.basis_label)
        self.competency_combo = QComboBox()
        self.competency_combo.addItem("Choose a competency", "")
        for competency in competencies:
            self.competency_combo.addItem(competency.name, competency.id)
        layout.addWidget(self.competency_combo)
        self.study_button = QPushButton("Study this competency")
        self.study_button.clicked.connect(
            lambda: self.study_requested.emit(self.competency_combo.currentData() or "")
        )
        self.competency_combo.currentIndexChanged.connect(self._sync_button)
        layout.addWidget(self.study_button)
        self.explanation = QLabel(
            "Prepare a question and historical reference in the existing launcher. "
            "Nothing starts until you choose Begin Process Run. Study preparation "
            "does not change proficiency or environment eligibility."
        )
        self.explanation.setWordWrap(True)
        layout.addWidget(self.explanation)
        self.capture_button = QPushButton("Open Study Find")
        self.capture_button.clicked.connect(self.capture_requested.emit)
        layout.addWidget(self.capture_button)
        self.calendar_button = QPushButton("Explore AMDX calendar")
        self.calendar_button.clicked.connect(self.calendar_requested.emit)
        layout.addWidget(self.calendar_button)
        layout.addStretch()
        self._active_run = False
        self._sync_button()

    def _sync_button(self):
        self.study_button.setEnabled(
            not self._active_run and bool(self.competency_combo.currentData())
        )

    def refresh(self, *, run, mode_name, directions, revision, has_draft):
        self._active_run = run is not None
        self.resume_button.setVisible(self._active_run)
        self.run_label.setText(
            f"Active: {run.run_label} · {run.environment.value} · {mode_name} · "
            f"Trade Plan {run.trade_plan_revision}. Resume this run before starting another."
            if run else "No active trading run. Study can begin with a question or a calendar investigation."
        )
        eligible = [d for d in directions if d.direction.value == "Study"
                    and d.trade_plan_revision == revision
                    and self.competency_combo.findData(d.competency_id) >= 0]
        def recorded_time(direction):
            try:
                stamp = datetime.fromisoformat(direction.updated_at)
                return stamp.timestamp() if stamp.tzinfo is not None else None
            except ValueError:
                return None

        eligible = [d for d in eligible if recorded_time(d) is not None]
        eligible.sort(key=lambda d: (recorded_time(d), d.competency_id), reverse=True)
        if eligible:
            direction = eligible[0]
            index = self.competency_combo.findData(direction.competency_id)
            self.basis_label.setText(
                f"Recorded Study direction: {self.competency_combo.itemText(index)}\n"
                f"Basis: most recently updated Study direction in {revision} "
                f"({direction.updated_at}). This is not a skill ranking.\n"
                f"Recorded note: {direction.note or 'No note recorded.'}"
            )
            if not self.competency_combo.currentData():
                self.competency_combo.setCurrentIndex(index)
        else:
            self.basis_label.setText(
                "No recorded Study direction with a valid update time for this Trade Plan revision. "
                "Choose a competency yourself, resume capture, or explore the calendar."
            )
        self.capture_button.setText("Resume Study Find draft" if has_draft else "Open Study Find")
        self._sync_button()
