from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
)

from ict_cockpit.feedback import FEEDBACK_CATEGORIES, FeedbackEntry


class FeedbackDialog(QDialog):
    def __init__(
        self,
        context: str,
        record_id: str,
        app_version: str,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.context = context
        self.record_id = record_id
        self.app_version = app_version

        self.setWindowTitle("Capture Feedback")
        self.setModal(True)
        self.resize(460, 260)

        self.category_input = QComboBox()
        self.category_input.addItems(FEEDBACK_CATEGORIES)

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText(
            "What felt wrong, slow, confusing, or worth improving?"
        )

        context_label = QLabel(context or "Unknown")
        context_label.setWordWrap(True)
        context_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        form_layout = QFormLayout()
        form_layout.addRow("Type", self.category_input)
        form_layout.addRow("Context", context_label)
        form_layout.addRow("Note", self.note_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        self.note_input.setFocus()

    def build_entry(self) -> FeedbackEntry:
        return FeedbackEntry(
            category=self.category_input.currentText(),
            note=self.note_input.toPlainText(),
            context=self.context,
            record_id=self.record_id,
            app_version=self.app_version,
        )

    def accept(self) -> None:
        if not self.note_input.toPlainText().strip():
            self.note_input.setFocus()
            return

        super().accept()
