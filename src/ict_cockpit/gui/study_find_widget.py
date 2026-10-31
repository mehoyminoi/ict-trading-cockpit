from ict_cockpit.media.workspace_paths import resolve_study_image
from ict_cockpit.gui.editor_feedback import handle_ctrl_y, focus_invalid_field
import sqlite3
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QDate, QEvent, Qt, Signal
from PySide6.QtGui import QAction, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QSplitter,
    QScrollArea,
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
    submission_failed = Signal(str)
    action_status = Signal(str)

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

        self.save_feedback = QLabel()
        self.save_feedback.setWordWrap(True)
        self.save_button = QPushButton("Save Study Find")
        self.save_button.clicked.connect(self.submit)

        self.new_study_find_button = QPushButton("Start New Study Find")
        self.new_study_find_button.hide()
        self.new_study_find_button.clicked.connect(self.reset_form)

        layout = QVBoxLayout(self)
        self.context_layout = QVBoxLayout()
        layout.addLayout(self.context_layout)
        self.action_feedback = QLabel()
        self.action_feedback.setWordWrap(True)
        self.action_feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.action_feedback.setAccessibleName("Capture action feedback")
        self.action_feedback.setFixedHeight(self.action_feedback.fontMetrics().lineSpacing() * 2 + 8)
        layout.addWidget(self.action_feedback)
        metadata = QHBoxLayout()
        for label, widget in (("Date", self.date_input), ("Instrument", self.instrument_input), ("Session", self.session_input)):
            metadata.addWidget(QLabel(label))
            metadata.addWidget(widget, 1)
        layout.addLayout(metadata)
        pattern = QHBoxLayout()
        pattern.addWidget(QLabel("Pattern"))
        pattern.addWidget(self.pattern_input, 2)
        pattern.addWidget(QLabel("Available move"))
        pattern.addWidget(self.available_move_input, 1)
        layout.addLayout(pattern)

        writing = QWidget()
        writing_layout = QVBoxLayout(writing)
        writing_layout.setContentsMargins(0, 0, 0, 0)
        writing_layout.addWidget(QLabel("Observation · what happened in price"))
        writing_layout.addWidget(self.observation_input, 1)
        writing_layout.addWidget(QLabel("Notes · interpretation, uncertainty, larger context"))
        writing_layout.addWidget(self.notes_input, 1)
        self.entry_actions = QHBoxLayout()
        writing_layout.addLayout(self.entry_actions)
        self.entry_feedback = QVBoxLayout()
        writing_layout.addLayout(self.entry_feedback)
        charts = QWidget()
        chart_layout = QVBoxLayout(charts)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.addWidget(QLabel("Chart context · paste an image or add a file"))
        chart_layout.addWidget(self.image_preview, 1)
        self.image_list.setMaximumHeight(90)
        chart_layout.addWidget(self.image_list)
        chart_actions = QHBoxLayout()
        for button in (self.attach_image_button, self.copy_image_button, self.remove_image_button):
            chart_actions.addWidget(button)
        chart_layout.addLayout(chart_actions)
        chart_layout.addStretch()
        self.capture_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.capture_splitter.addWidget(writing)
        self.capture_splitter.addWidget(charts)
        self.capture_splitter.setStretchFactor(0, 3)
        self.capture_splitter.setStretchFactor(1, 2)
        layout.addWidget(self.capture_splitter, 1)

        summary_actions = QHBoxLayout()
        summary_actions.addWidget(self.generate_summary_button)
        self.summary_toggle = QPushButton("Show summary")
        self.summary_toggle.setCheckable(True)
        summary_actions.addWidget(self.summary_toggle)
        summary_actions.addStretch()
        layout.addLayout(summary_actions)
        self.summary_area = QWidget()
        summary_layout = QVBoxLayout(self.summary_area)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.addWidget(self.summary_template_label)
        summary_layout.addWidget(self.summary_preview)
        summary_layout.addWidget(self.copy_summary_button)
        layout.addWidget(self.summary_area)
        self.summary_area.hide()
        self.summary_toggle.toggled.connect(self._show_summary)

        self.save_area = QVBoxLayout()
        self.save_area.addWidget(self.save_feedback)
        self.save_area.addWidget(self.save_button)
        self.save_area.addWidget(self.new_study_find_button)
        layout.addLayout(self.save_area)
        # Keep the familiar typing order despite the visual two-column composition.
        order = (self.date_input, self.instrument_input, self.session_input,
                 self.pattern_input, self.observation_input, self.available_move_input, self.notes_input)
        for before, after in zip(order, order[1:]):
            QWidget.setTabOrder(before, after)

        self._connect_draft_signals()
        self.refresh_summary_template_label()

        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def _show_summary(self, visible):
        self.summary_area.setVisible(visible)
        self.summary_toggle.setText("Hide summary" if visible else "Show summary")

    def _connect_draft_signals(self) -> None:
        self.date_input.dateChanged.connect(self.emit_draft_changed)
        self.instrument_input.textChanged.connect(self.emit_draft_changed)
        self.session_input.textChanged.connect(self.emit_draft_changed)
        self.pattern_input.textChanged.connect(self.emit_draft_changed)
        self.observation_input.textChanged.connect(self.emit_draft_changed)
        self.available_move_input.valueChanged.connect(self.emit_draft_changed)
        self.notes_input.textChanged.connect(self.emit_draft_changed)

    def eventFilter(self, watched, event) -> bool:
        if watched in (self.observation_input, self.notes_input) and handle_ctrl_y(watched, event):
            return True
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

    def submit(self) -> bool:
        try:
            study_find = self.build_study_find()
        except ValueError as error:
            self.save_feedback.setText(f"Not saved: {error}. Complete the required field and try again.")
            self.submission_failed.emit(str(error))
            return False
        self.save_feedback.clear()
        self.study_find_ready.emit(study_find)
        return True

    def apply_context_defaults(
        self,
        *,
        observation_date=None,
        instrument: str = "",
        session: str = "",
    ) -> bool:
        """Seed supported context only when the current draft is empty."""
        if self.build_draft().has_content() or not self.save_button.isEnabled():
            return False
        self._loading_draft = True
        try:
            if observation_date is not None:
                self.date_input.setDate(
                    QDate(
                        observation_date.year,
                        observation_date.month,
                        observation_date.day,
                    )
                )
            if instrument:
                self.instrument_input.setText(instrument)
            if session:
                self.session_input.setText(session)
        finally:
            self._loading_draft = False
        self.emit_draft_changed()
        return True

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

    def _show_action_error(self, error):
        fields = {
            "instrument cannot be empty": ("Instrument", self.instrument_input),
            "session cannot be empty": ("Session", self.session_input),
            "pattern_name cannot be empty": ("Pattern", self.pattern_input),
            "observation cannot be empty": ("Observation", self.observation_input),
        }
        field = fields.get(str(error))
        message = (f"Summary not generated: enter {field[0]}, then try Generate Summary again."
                   if field else f"Summary not generated: {error}")
        self.action_feedback.setText(message + " Existing summary and draft retained.")
        self.action_status.emit(self.action_feedback.text())
        self.action_feedback.setToolTip(self.action_feedback.text())
        target = field[1] if field else self.action_feedback
        if field:
            focus_invalid_field(target)
        ancestor = target.parentWidget()
        while ancestor is not None:
            if isinstance(ancestor, QScrollArea):
                ancestor.ensureWidgetVisible(target)
                break
            ancestor = ancestor.parentWidget()

    def generate_summary(self) -> str:
        try:
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
        except (ValueError, sqlite3.Error) as error:
            self._show_action_error(error)
            return ""
        self.action_feedback.clear()
        self.summary_preview.setPlainText(rendered)
        self.summary_toggle.setChecked(True)
        self.action_status.emit("Study summary generated. Capture has not been saved by this action.")
        return rendered

    def copy_summary(self) -> None:
        rendered = self.generate_summary()
        if rendered:
            QApplication.clipboard().setText(rendered)

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
        self.save_feedback.setText("Study Find saved.")
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
        self.action_feedback.clear()

        self.save_feedback.clear()
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

        pixmap = QPixmap(resolve_study_image(self.image_paths[row]))
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

        pixmap = QPixmap(resolve_study_image(self.image_paths[selected_row]))
        if pixmap.isNull():
            return

        QApplication.clipboard().setPixmap(pixmap)
