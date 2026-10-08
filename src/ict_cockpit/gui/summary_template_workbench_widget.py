from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.database.summary_template_repository import (
    SummaryTemplateRepository,
)
from ict_cockpit.summary.renderer import SummaryRenderer
from ict_cockpit.summary.template_definition import SummaryTemplateKind
from ict_cockpit.summary.templates import TEMPLATE_FIELDS


class SummaryTemplateWorkbenchWidget(QWidget):
    """Small Workbench surface for publishing immutable template revisions."""

    template_published = Signal(str)

    def __init__(self, repository: SummaryTemplateRepository) -> None:
        super().__init__()
        self.repository = repository
        self.active_template = None

        heading = QLabel("Summary Templates")
        heading.setStyleSheet("font-size: 18px; font-weight: 600;")

        note = QLabel(
            "Edit a working copy, then publish it as a new immutable revision. "
            "Published revisions are retained; the new revision becomes active "
            "for generated summaries."
        )
        note.setWordWrap(True)

        self.kind_combo = QComboBox()
        for kind in SummaryTemplateKind:
            self.kind_combo.addItem(kind.value, kind.value)
        self.kind_combo.currentTextChanged.connect(self.load_active_template)

        self.name_input = QLineEdit()
        self.revision_label = QLabel()
        self.body_input = QPlainTextEdit()
        self.body_input.setMinimumHeight(340)

        self.fields_label = QLabel()
        self.fields_label.setWordWrap(True)

        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        self.validation_label.hide()

        self.publish_button = QPushButton("Publish New Revision")
        self.publish_button.clicked.connect(self.publish_revision)

        form = QFormLayout()
        form.addRow("Template kind", self.kind_combo)
        form.addRow("Name", self.name_input)
        form.addRow("Active revision", self.revision_label)

        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(note)
        layout.addLayout(form)
        layout.addWidget(self.fields_label)
        layout.addWidget(self.body_input, 1)
        layout.addWidget(self.validation_label)
        layout.addWidget(self.publish_button)

        self.load_active_template()

    @property
    def selected_kind(self) -> SummaryTemplateKind:
        return SummaryTemplateKind(self.kind_combo.currentData())

    def load_active_template(self, *_args) -> None:
        template = self.repository.get_active(self.selected_kind)
        self.active_template = template
        if template is None:
            self.name_input.clear()
            self.revision_label.setText("No active template")
            self.body_input.clear()
            self.publish_button.setEnabled(False)
        else:
            self.name_input.setText(template.name)
            self.revision_label.setText(f"r{template.revision}")
            self.body_input.setPlainText(template.body)
            self.publish_button.setEnabled(True)

        fields = ", ".join(sorted(TEMPLATE_FIELDS[self.selected_kind]))
        self.fields_label.setText("Available fields: " + fields)
        self.validation_label.hide()

    def publish_revision(self) -> None:
        if self.active_template is None:
            return

        name = self.name_input.text().strip()
        body = self.body_input.toPlainText()
        if not name:
            self.validation_label.setText("Template name is required.")
            self.validation_label.show()
            return
        if not body.strip():
            self.validation_label.setText("Template body is required.")
            self.validation_label.show()
            return

        try:
            SummaryRenderer().validate(
                body,
                TEMPLATE_FIELDS[self.selected_kind],
            )
            published = self.repository.publish_revision(
                self.active_template,
                name=name,
                body=body,
            )
        except ValueError as exc:
            self.validation_label.setText(str(exc))
            self.validation_label.show()
            return

        self.active_template = published
        self.revision_label.setText(f"r{published.revision}")
        self.body_input.setPlainText(published.body)
        self.validation_label.setText(
            f"Published {published.label}. Previous revisions remain immutable."
        )
        self.validation_label.show()
        self.template_published.emit(published.kind.value)
