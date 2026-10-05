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
    QSplitter,
    QHBoxLayout,
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

        # New full-size button
        self.open_image_button = QPushButton(
            "Open Full Size"
        )
        self.open_image_button.setEnabled(False)
        self.open_image_button.clicked.connect(
            self.open_selected_image
        )

        image_button_layout = QHBoxLayout()

        image_button_layout.addWidget(
            self.copy_image_button
        )

        image_button_layout.addWidget(
            self.open_image_button
        )

        left_widget = QWidget()
        left_layout = QVBoxLayout()

        left_layout.addWidget(QLabel("Saved Study Finds"))
        left_layout.addWidget(self.study_list)

        left_widget.setLayout(left_layout)


        right_widget = QWidget()
        right_layout = QVBoxLayout()

        right_layout.addWidget(self.details_label)

        right_layout.addWidget(QLabel("Observation"))
        right_layout.addWidget(self.observation_view)

        right_layout.addWidget(QLabel("Notes"))
        right_layout.addWidget(self.notes_view)

        right_layout.addWidget(QLabel("Chart Attachments"))
        right_layout.addWidget(self.image_list)

        right_layout.addWidget(self.image_preview)
        right_layout.addLayout(
            image_button_layout
        )

        right_widget.setLayout(right_layout)


        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout = QVBoxLayout()
        layout.addWidget(splitter)

        self.setLayout(layout)

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
        if self.study_finds:
            self.study_list.setCurrentRow(0)
        else:
            self.clear_selection()

    def show_selected_study_find(
        self,
        row: int,
    ) -> None:
        if row < 0 or row >= len(self.study_finds):
            self.clear_selection()
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
            self.open_image_button.setEnabled(False)
            return

        preview = pixmap.scaled(
            520,
            240,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.image_preview.setPixmap(preview)
        self.copy_image_button.setEnabled(True)
        self.copy_image_button.setEnabled(True)
        self.open_image_button.setEnabled(True)


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

    def clear_selection(self) -> None:
        self.details_label.setText(
            "No saved Study Finds."
        )

        self.observation_view.clear()
        self.notes_view.clear()

        self.image_paths.clear()
        self.image_list.clear()

        self.update_image_preview(-1)

    def open_selected_image(self) -> None:
        row = self.image_list.currentRow()

        if row < 0 or row >= len(self.image_paths):
            return

        pixmap = QPixmap(
            self.image_paths[row]
        )

        if pixmap.isNull():
            return

        viewer = QLabel()
        viewer.setPixmap(pixmap)
        viewer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        viewer.setWindowTitle(
            Path(self.image_paths[row]).name
        )

        viewer.resize(
            min(pixmap.width(), 1400),
            min(pixmap.height(), 900),
        )

        viewer.show()

        self.full_size_viewer = viewer