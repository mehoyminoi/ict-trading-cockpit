from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QApplication,
    QPlainTextEdit,
)

from ict_cockpit.analysis.study_find import StudyFind
from ict_cockpit.summary.renderer import SummaryRenderer
from ict_cockpit.summary.study_find_context import StudyFindSummaryContext
from ict_cockpit.summary.templates import STUDY_FIND_SUMMARY_V1


class StudyFindWidget(QWidget):
    study_find_ready = Signal(StudyFind)

    def __init__(self) -> None:
        super().__init__()

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.instrument_input = QLineEdit()
        self.instrument_input.setPlaceholderText("MNQ")

        self.session_input = QLineEdit()
        self.session_input.setPlaceholderText("NYAM")

        self.pattern_input = QLineEdit()
        self.pattern_input.setPlaceholderText("London low raid")

        self.observation_input = QTextEdit()
        self.observation_input.setPlaceholderText(
            "What happened in price?"
        )

        self.available_move_input = QDoubleSpinBox()
        self.available_move_input.setRange(0.0, 100000.0)
        self.available_move_input.setDecimals(2)
        self.available_move_input.setSuffix(" handles")

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText(
            "Optional notes, lessons, context, or soft-skill observations..."
        )

        self.save_button = QPushButton("Save Study Find")
        self.save_button.clicked.connect(self.submit)

        form_layout = QFormLayout()
        form_layout.addRow("Date", self.date_input)
        form_layout.addRow("Instrument", self.instrument_input)
        form_layout.addRow("Session", self.session_input)
        form_layout.addRow("Pattern", self.pattern_input)
        form_layout.addRow("Observation", self.observation_input)
        form_layout.addRow("Available Move", self.available_move_input)
        form_layout.addRow("Notes", self.notes_input)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.save_button)

    

        self.summary_preview = QPlainTextEdit()
        self.summary_preview.setReadOnly(True)
        self.summary_preview.setPlaceholderText(
            "Generated Study Find summary will appear here."
        )

        self.generate_summary_button = QPushButton("Generate Summary")
        self.copy_summary_button = QPushButton("Copy Summary")

        self.generate_summary_button.clicked.connect(
            self.generate_summary
        )
        self.copy_summary_button.clicked.connect(
            self.copy_summary
        )

        layout.addWidget(self.generate_summary_button)
        layout.addWidget(self.summary_preview)
        layout.addWidget(self.copy_summary_button)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def build_study_find(self) -> StudyFind:
        selected_date = self.date_input.date()

        observation_date = selected_date.toPython()

        available_move = self.available_move_input.value()

        return StudyFind(
            observation_date=observation_date,
            instrument=self.instrument_input.text(),
            session=self.session_input.text(),
            pattern_name=self.pattern_input.text(),
            observation=self.observation_input.toPlainText(),
            available_move_handles=available_move,
            notes=self.notes_input.toPlainText(),
        )

    def submit(self) -> None:
        study_find = self.build_study_find()
        self.study_find_ready.emit(study_find)

    def generate_summary(self) -> str:
        study_find = self.build_study_find()

        context = StudyFindSummaryContext(study_find)

        rendered = SummaryRenderer().render(
            STUDY_FIND_SUMMARY_V1,
            context.to_template_values(),
        )

        self.summary_preview.setPlainText(rendered)

        return rendered


    def copy_summary(self) -> None:
        rendered = self.generate_summary()

        clipboard = QApplication.clipboard()
        clipboard.setText(rendered)