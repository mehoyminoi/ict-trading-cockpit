from PySide6.QtCore import QDate, Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QListWidget,
)

from ict_cockpit.analysis.study_find import StudyFind
from ict_cockpit.summary.renderer import SummaryRenderer
from ict_cockpit.summary.study_find_context import StudyFindSummaryContext
from ict_cockpit.summary.templates import STUDY_FIND_SUMMARY_V1
from uuid import uuid4
from pathlib import Path

from ict_cockpit.media.study_find_media import (
    store_study_find_image,
)


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

        self.new_study_find_button = QPushButton(
            "Start New Study Find"
        )
        self.new_study_find_button.hide()

        self.new_study_find_button.clicked.connect(
            self.reset_form
        )

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


        self.image_paths: list[str] = []
        self.next_image_number = 1

        self.image_list = QListWidget()
        self.image_list.setMinimumHeight(80)

        self.attach_image_button = QPushButton("Add Chart Image")
        self.remove_image_button = QPushButton("Remove Selected")

        self.attach_image_button.clicked.connect(
                    self.choose_chart_image
        )
        
        self.remove_image_button.clicked.connect(
            self.remove_selected_image
        )

        self.image_preview = QLabel("No chart image selected")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.image_preview.setMinimumHeight(200)
        self.image_preview.setScaledContents(False)

        self.copy_image_button = QPushButton("Copy Selected Image")
        self.copy_image_button.setEnabled(False)

        self.image_list.currentRowChanged.connect(
            self.update_image_preview
        )

        self.copy_image_button.clicked.connect(
            self.copy_selected_image
        )


        layout.addWidget(self.image_list)
        layout.addWidget(self.image_preview)
        layout.addWidget(self.copy_image_button)
        layout.addWidget(self.attach_image_button)

        layout.addWidget(self.remove_image_button)

        self.summary_preview = QPlainTextEdit()
        self.summary_preview.setReadOnly(True)
        self.summary_preview.setPlaceholderText(
            "Generated Study Find summary will appear here."
        )

        self.current_study_find_id = str(uuid4())

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
        layout.addWidget(self.save_button)
        layout.addWidget(self.new_study_find_button)

        self.setLayout(layout)

    def build_study_find(self) -> StudyFind:
        selected_date = self.date_input.date()

        observation_date = selected_date.toPython()

        available_move = self.available_move_input.value()

        primary_image_path = ""

        if self.image_paths:
            primary_image_path = self.image_paths[0]

        return StudyFind(
            id=self.current_study_find_id,
            observation_date=observation_date,
            instrument=self.instrument_input.text(),
            session=self.session_input.text(),
            pattern_name=self.pattern_input.text(),
            observation=self.observation_input.toPlainText(),
            available_move_handles=available_move,
            notes=self.notes_input.toPlainText(),
            image_path=primary_image_path,
        )

    def submit(self) -> None:
        study_find = self.build_study_find()
        self.study_find_ready.emit(study_find)

    def generate_summary(self) -> str:
        study_find = self.build_study_find()

        context = StudyFindSummaryContext(
            study_find=study_find,
            image_paths=self.image_paths,
        )

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

    def choose_chart_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Attach Chart Image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)",
        )

        if not file_path:
            return

        stored_path = store_study_find_image(
            self.current_study_find_id,
            Path(file_path),
            self.next_image_number,
        )

        self.next_image_number += 1

        path_string = str(stored_path)

        self.image_paths.append(path_string)
        self.image_list.addItem(path_string)

    def remove_selected_image(self) -> None:
        selected_row = self.image_list.currentRow()

        if selected_row < 0:
            return

        self.image_list.takeItem(selected_row)
        self.image_paths.pop(selected_row)
        if self.image_paths:
            new_row = min(
                selected_row,
                len(self.image_paths) - 1,
            )

            self.image_list.setCurrentRow(new_row)
        else:
            self.update_image_preview(-1)

    def mark_saved(self) -> None:
        self.save_button.setText("Saved")
        self.save_button.setEnabled(False)

        self.attach_image_button.setEnabled(False)
        self.remove_image_button.setEnabled(False)

        self.new_study_find_button.show()

    def reset_form(self) -> None:
        self.current_study_find_id = str(uuid4())

        self.instrument_input.clear()
        self.session_input.clear()
        self.pattern_input.clear()
        self.observation_input.clear()
        self.notes_input.clear()

        self.available_move_input.setValue(0)

        self.image_paths.clear()
        self.image_list.clear()
        self.update_image_preview(-1)

        self.next_image_number = 1

        self.summary_preview.clear()

        self.save_button.setText("Save Study Find")
        self.save_button.setEnabled(True)

        self.attach_image_button.setEnabled(True)
        self.remove_image_button.setEnabled(True)

        self.new_study_find_button.hide()

        self.instrument_input.setFocus()

    def update_image_preview(self, row: int) -> None:
        if row < 0 or row >= len(self.image_paths):
            self.image_preview.clear()
            self.image_preview.setText(
                "No chart image selected"
            )
            self.copy_image_button.setEnabled(False)
            return

        image_path = self.image_paths[row]

        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            self.image_preview.clear()
            self.image_preview.setText(
                "Unable to load chart image"
            )
            self.copy_image_button.setEnabled(False)
            return

        preview = pixmap.scaled(
            700,
            400,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.image_preview.setPixmap(preview)
        self.copy_image_button.setEnabled(True)

    def copy_selected_image(self) -> None:
        selected_row = self.image_list.currentRow()

        if selected_row < 0:
            return

        if selected_row >= len(self.image_paths):
            return

        pixmap = QPixmap(
            self.image_paths[selected_row]
        )

        if pixmap.isNull():
            return

        QApplication.clipboard().setPixmap(pixmap)