from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QDate, QEvent, Qt, Signal
from PySide6.QtGui import QAction, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.study_find import StudyFind, StudyFindDraft
from ict_cockpit.media.study_find_media import (
    get_study_find_image_destination,
    store_study_find_image,
)
from ict_cockpit.database.summary_template_repository import (
    SummaryTemplateRepository,
)
from ict_cockpit.summary.renderer import SummaryRenderer
from ict_cockpit.summary.study_find_context import StudyFindSummaryContext
from ict_cockpit.summary.template_definition import SummaryTemplateKind
from ict_cockpit.summary.templates import STUDY_FIND_SUMMARY_V1


class StudyFindWidget(QWidget):
    """Capture a single Study Find and its chart attachments."""

    study_find_ready = Signal(StudyFind)
    draft_changed = Signal(StudyFindDraft)

    def __init__(
        self,
        summary_template_repository: SummaryTemplateRepository | None = None,
    ) -> None:
        super().__init__()

        self.summary_template_repository = summary_template_repository
        self.current_study_find_id = str(uuid4())
        self.image_paths: list[str] = []
        self.next_image_number = 1
        self._loading_draft = False

        self.paste_chart_action = QAction("Paste Chart", self)
        self.paste_chart_action.triggered.connect(
            self.paste_chart_from_clipboard
        )
        self.addAction(self.paste_chart_action)

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
        self.observation_input.setPlaceholderText("What happened in price?")

        self.available_move_input = QDoubleSpinBox()
        self.available_move_input.setRange(0.0, 100000.0)
        self.available_move_input.setDecimals(2)
        self.available_move_input.setSuffix(" handles")

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText(
            "Optional notes, lessons, context, or soft-skill observations..."
        )

        self.image_list = QListWidget()
        self.image_list.setMinimumHeight(80)
        self.image_list.currentRowChanged.connect(self.update_image_preview)

        self.image_preview = QLabel("No chart image selected")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumHeight(140)
        self.image_preview.setMaximumHeight(220)
        self.image_preview.setScaledContents(False)

        self.copy_image_button = QPushButton("Copy Selected Image")
        self.copy_image_button.setEnabled(False)
        self.copy_image_button.clicked.connect(self.copy_selected_image)

        self.attach_image_button = QPushButton("Add Chart Image")
        self.attach_image_button.clicked.connect(self.choose_chart_image)

        self.remove_image_button = QPushButton("Remove Selected")
        self.remove_image_button.clicked.connect(self.remove_selected_image)

        self.summary_template_label = QLabel()
        self.summary_template_label.setWordWrap(True)

        self.summary_preview = QPlainTextEdit()
        self.summary_preview.setReadOnly(True)
        self.summary_preview.setPlaceholderText(
            "Generated Study Find summary will appear here."
        )

        self.generate_summary_button = QPushButton("Generate Summary")
        self.generate_summary_button.clicked.connect(self.generate_summary)

        self.copy_summary_button = QPushButton("Copy Summary")
        self.copy_summary_button.clicked.connect(self.copy_summary)

        self.save_button = QPushButton("Save Study Find")
        self.save_button.clicked.connect(self.submit)

        self.new_study_find_button = QPushButton("Start New Study Find")
        self.new_study_find_button.hide()
        self.new_study_find_button.clicked.connect(self.reset_form)

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
        layout.addWidget(self.image_list)
        layout.addWidget(self.image_preview)
        layout.addWidget(self.copy_image_button)
        layout.addWidget(self.attach_image_button)
        layout.addWidget(self.remove_image_button)
        layout.addWidget(self.summary_template_label)
        layout.addWidget(self.generate_summary_button)
        layout.addWidget(self.summary_preview)
        layout.addWidget(self.copy_summary_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.new_study_find_button)
        self.setLayout(layout)

        self._connect_draft_signals()
        self.refresh_summary_template_label()

        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def _connect_draft_signals(self) -> None:
        self.date_input.dateChanged.connect(self.emit_draft_changed)
        self.instrument_input.textChanged.connect(self.emit_draft_changed)
        self.session_input.textChanged.connect(self.emit_draft_changed)
        self.pattern_input.textChanged.connect(self.emit_draft_changed)
        self.observation_input.textChanged.connect(self.emit_draft_changed)
        self.available_move_input.valueChanged.connect(self.emit_draft_changed)
        self.notes_input.textChanged.connect(self.emit_draft_changed)

    def eventFilter(self, watched, event) -> bool:
        if (
            isinstance(watched, QWidget)
            and (watched is self or self.isAncestorOf(watched))
            and event.type() == QEvent.Type.KeyPress
            and event.matches(QKeySequence.StandardKey.Paste)
            and QApplication.clipboard().mimeData().hasImage()
            and self.paste_chart_action.isEnabled()
        ):
            self.paste_chart_action.trigger()
            return True

        return super().eventFilter(watched, event)

    def build_draft(self) -> StudyFindDraft:
        return StudyFindDraft(
            id=self.current_study_find_id,
            observation_date=self.date_input.date().toPython(),
            instrument=self.instrument_input.text(),
            session=self.session_input.text(),
            pattern_name=self.pattern_input.text(),
            observation=self.observation_input.toPlainText(),
            available_move_handles=self.available_move_input.value(),
            notes=self.notes_input.toPlainText(),
            image_paths=list(self.image_paths),
        )

    def emit_draft_changed(self) -> None:
        if self._loading_draft or not self.save_button.isEnabled():
            return
        self.draft_changed.emit(self.build_draft())

    def load_draft(self, draft: StudyFindDraft) -> None:
        self._loading_draft = True
        try:
            self.current_study_find_id = draft.id
            self.date_input.setDate(
                QDate(
                    draft.observation_date.year,
                    draft.observation_date.month,
                    draft.observation_date.day,
                )
            )
            self.instrument_input.setText(draft.instrument)
            self.session_input.setText(draft.session)
            self.pattern_input.setText(draft.pattern_name)
            self.observation_input.setPlainText(draft.observation)
            self.available_move_input.setValue(
                draft.available_move_handles or 0.0
            )
            self.notes_input.setPlainText(draft.notes)

            self.image_paths = list(draft.image_paths)
            self.image_list.clear()
            for image_path in self.image_paths:
                self.image_list.addItem(Path(image_path).name)

            self.next_image_number = self._calculate_next_image_number()
            if self.image_paths:
                self.image_list.setCurrentRow(0)
            else:
                self.update_image_preview(-1)
        finally:
            self._loading_draft = False

    def _calculate_next_image_number(self) -> int:
        used_numbers: list[int] = []
        for image_path in self.image_paths:
            stem = Path(image_path).stem
            if stem.startswith("chart-"):
                try:
                    used_numbers.append(int(stem.removeprefix("chart-")))
                except ValueError:
                    pass
        return max(used_numbers, default=0) + 1

    def build_study_find(self) -> StudyFind:
        primary_image_path = self.image_paths[0] if self.image_paths else ""

        return StudyFind(
            id=self.current_study_find_id,
            observation_date=self.date_input.date().toPython(),
            instrument=self.instrument_input.text(),
            session=self.session_input.text(),
            pattern_name=self.pattern_input.text(),
            observation=self.observation_input.toPlainText(),
            available_move_handles=self.available_move_input.value(),
            notes=self.notes_input.toPlainText(),
            image_path=primary_image_path,
        )

    def submit(self) -> None:
        self.study_find_ready.emit(self.build_study_find())

    def _active_summary_template(self):
        if self.summary_template_repository is None:
            return None
        return self.summary_template_repository.get_active(
            SummaryTemplateKind.STUDY_FIND
        )

    def _active_summary_template_body(self) -> str:
        template = self._active_summary_template()
        return template.body if template is not None else STUDY_FIND_SUMMARY_V1

    def refresh_summary_template_label(self) -> None:
        if self.summary_template_repository is None:
            self.summary_template_label.setText(
                "Template · Study Find Default · r1"
            )
            return
        template = self.summary_template_repository.get_active(
            SummaryTemplateKind.STUDY_FIND
        )
        if template is None:
            self.summary_template_label.setText(
                "Template · Study Find Default · r1"
            )
        else:
            self.summary_template_label.setText(
                f"Template · {template.label}"
            )

    def generate_summary(self) -> str:
        context = StudyFindSummaryContext(
            study_find=self.build_study_find(),
            image_paths=self.image_paths,
        )
        renderer = SummaryRenderer()
        template = self._active_summary_template()
        if template is None:
            rendered = renderer.render(
                STUDY_FIND_SUMMARY_V1,
                context.to_template_values(),
            )
            rendered = (
                rendered.rstrip()
                + "\n\nTemplate: Study Find Default · r1\n"
            )
        else:
            rendered = renderer.render_versioned(
                template,
                context.to_template_values(),
            )
        self.summary_preview.setPlainText(rendered)
        return rendered

    def copy_summary(self) -> None:
        QApplication.clipboard().setText(self.generate_summary())

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
        self._add_managed_image(stored_path)

    def paste_chart_from_clipboard(self) -> bool:
        image = QApplication.clipboard().image()
        if image.isNull():
            return False

        destination_path = get_study_find_image_destination(
            self.current_study_find_id,
            self.next_image_number,
            ".png",
        )
        if not image.save(str(destination_path), "PNG"):
            return False

        self._add_managed_image(destination_path)
        return True

    def _add_managed_image(self, image_path: Path) -> None:
        path_string = str(image_path)
        self.image_paths.append(path_string)
        self.image_list.addItem(image_path.name)
        self.next_image_number += 1
        self.image_list.setCurrentRow(self.image_list.count() - 1)
        self.emit_draft_changed()

    def remove_selected_image(self) -> None:
        selected_row = self.image_list.currentRow()
        if selected_row < 0:
            return

        self.image_list.takeItem(selected_row)
        self.image_paths.pop(selected_row)

        if self.image_paths:
            new_row = min(selected_row, len(self.image_paths) - 1)
            self.image_list.setCurrentRow(new_row)
        else:
            self.update_image_preview(-1)

        self.emit_draft_changed()

    def mark_saved(self) -> None:
        self.save_button.setText("Saved")
        self.save_button.setEnabled(False)
        self.attach_image_button.setEnabled(False)
        self.remove_image_button.setEnabled(False)
        self.paste_chart_action.setEnabled(False)
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
        self.paste_chart_action.setEnabled(True)
        self.new_study_find_button.hide()

        self.emit_draft_changed()
        self.instrument_input.setFocus()

    def update_image_preview(self, row: int) -> None:
        if row < 0 or row >= len(self.image_paths):
            self.image_preview.clear()
            self.image_preview.setText("No chart image selected")
            self.copy_image_button.setEnabled(False)
            return

        pixmap = QPixmap(self.image_paths[row])
        if pixmap.isNull():
            self.image_preview.clear()
            self.image_preview.setText("Unable to load chart image")
            self.copy_image_button.setEnabled(False)
            return

        preview = pixmap.scaled(
            420,
            200,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_preview.setPixmap(preview)
        self.copy_image_button.setEnabled(True)

    def copy_selected_image(self) -> None:
        selected_row = self.image_list.currentRow()
        if selected_row < 0 or selected_row >= len(self.image_paths):
            return

        pixmap = QPixmap(self.image_paths[selected_row])
        if pixmap.isNull():
            return

        QApplication.clipboard().setPixmap(pixmap)
