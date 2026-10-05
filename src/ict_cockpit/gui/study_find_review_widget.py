from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.study_find import StudyFind
from ict_cockpit.database.study_find_repository import (
    StudyFindRepository,
)


class StudyFindReviewWidget(QWidget):
    def __init__(
        self,
        repository: StudyFindRepository,
    ) -> None:
        super().__init__()

        self.repository = repository
        self.study_finds: list[StudyFind] = []
        self.image_paths: list[str] = []

        self.study_list = QListWidget()
        self.study_list.currentRowChanged.connect(
            self.show_selected_study_find
        )

        self.details_label = QLabel(
            "Select a saved Study Find."
        )
        self.details_label.setWordWrap(True)

        self.observation_view = QTextEdit()
        self.observation_view.setReadOnly(True)
        self.observation_view.setPlaceholderText(
            "Observation"
        )

        self.notes_view = QTextEdit()
        self.notes_view.setReadOnly(True)
        self.notes_view.setPlaceholderText(
            "Notes"
        )

        self.image_list = QListWidget()
        self.image_list.currentRowChanged.connect(
            self.update_image_preview
        )

        self.image_preview = QLabel(
            "No chart image selected"
        )
        self.image_preview.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.image_preview.setMinimumHeight(140)
        self.image_preview.setMaximumHeight(260)

        self.copy_image_button = QPushButton(
            "Copy Selected Image"
        )
        self.copy_image_button.setEnabled(False)
        self.copy_image_button.clicked.connect(
            self.copy_selected_image
        )

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Saved Study Finds"))
        layout.addWidget(self.study_list)
        layout.addWidget(self.details_label)
        layout.addWidget(QLabel("Observation"))
        layout.addWidget(self.observation_view)
        layout.addWidget(QLabel("Notes"))
        layout.addWidget(self.notes_view)
        layout.addWidget(QLabel("Chart Attachments"))
        layout.addWidget(self.image_list)
        layout.addWidget(self.image_preview)
        layout.addWidget(self.copy_image_button)

        self.setLayout(layout)

        self.refresh()

    def refresh(self) -> None:
        self.study_finds = self.repository.get_recent()

        self.study_list.clear()

        for study_find in self.study_finds:
            label = (
                f"{study_find.observation_date:%y-%m-%d}"
                f" | {study_find.instrument}"
                f" | {study_find.session}"
                f" | {study_find.pattern_name}"
            )

            self.study_list.addItem(label)
    def show_selected_study_find(
        self,
        row: int,
    ) -> None:
        if row < 0 or row >= len(self.study_finds):
            return

        study_find = self.study_finds[row]

        available_move = ""

        if study_find.available_move_handles is not None:
            available_move = (
                f"{study_find.available_move_handles:.2f} handles"
            )

        self.details_label.setText(
            f"Date: {study_find.observation_date:%y-%m-%d}\n"
            f"Instrument: {study_find.instrument}\n"
            f"Session: {study_find.session}\n"
            f"Pattern: {study_find.pattern_name}\n"
            f"Available Move: {available_move}"
        )

        self.observation_view.setPlainText(
            study_find.observation
        )

        self.notes_view.setPlainText(
            study_find.notes
        )

        self.image_paths = self.repository.get_images(
            study_find.id
        )

        self.image_list.clear()

        for image_path in self.image_paths:
            self.image_list.addItem(
                Path(image_path).name
            )

        self.update_image_preview(-1)        

    def update_image_preview(
        self,
        row: int,
    ) -> None:
        if row < 0 or row >= len(self.image_paths):
            self.image_preview.clear()
            self.image_preview.setText(
                "No chart image selected"
            )
            self.copy_image_button.setEnabled(False)
            return

        pixmap = QPixmap(
            self.image_paths[row]
        )

        if pixmap.isNull():
            self.image_preview.clear()
            self.image_preview.setText(
                "Unable to load chart image"
            )
            self.copy_image_button.setEnabled(False)
            return

        preview = pixmap.scaled(
            520,
            240,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.image_preview.setPixmap(preview)
        self.copy_image_button.setEnabled(True)


    def copy_selected_image(self) -> None:
        row = self.image_list.currentRow()

        if row < 0 or row >= len(self.image_paths):
            return

        pixmap = QPixmap(
            self.image_paths[row]
        )

        if pixmap.isNull():
            return

        QApplication.clipboard().setPixmap(
            pixmap
        )