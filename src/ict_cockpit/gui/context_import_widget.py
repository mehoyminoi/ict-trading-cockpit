from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QFileDialog, QHBoxLayout, QLabel,
    QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

from ict_cockpit.analysis.forex_factory_import import import_forex_factory_json, ImportedCaptureProvider


class ContextImportWidget(QWidget):
    """Explicit import/selection outside the active operating surface."""
    def __init__(self, repository, shell):
        super().__init__()
        self.repository = repository
        self.shell = shell
        self.pending_capture = None
        self.setObjectName("process.calendar_import")
        layout = QVBoxLayout(self)
        intro = QLabel(
            "Calendar captures — Forex Factory JSON\n"
            "On Forex Factory Calendar, choose Weekly Export > JSON and save the file. "
            "Choose that export's starting Sunday in UTC, preview it, then save. "
            "Select a saved capture explicitly for new runs. Existing runs keep their own snapshot."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
        row = QHBoxLayout()
        row.addWidget(QLabel("Export week starts (Sunday, UTC)"))
        self.week_start = QDateEdit()
        self.week_start.setDisplayFormat("yyyy-MM-dd")
        self.week_start.setCalendarPopup(True)
        today = datetime.now(timezone.utc).date()
        sunday = today - timedelta(days=(today.weekday() + 1) % 7)
        self.week_start.setDate(QDate(sunday.year, sunday.month, sunday.day))
        row.addWidget(self.week_start)
        self.preview_button = QPushButton("Preview JSON export…")
        self.preview_button.clicked.connect(self._choose_file)
        row.addWidget(self.preview_button)
        self.save_button = QPushButton("Save capture")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_pending_capture)
        row.addWidget(self.save_button)
        layout.addLayout(row)
        self.status_label = QLabel("No export previewed.")
        self.status_label.setTextFormat(Qt.TextFormat.PlainText)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(240)
        layout.addWidget(self.preview)
        row = QHBoxLayout()
        self.captures = QComboBox()
        self.captures.setMinimumContentsLength(22)
        self.captures.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.captures.setObjectName("process.calendar_import.capture")
        self.captures.currentIndexChanged.connect(self._show_selected)
        row.addWidget(self.captures, 1)
        self.use_button = QPushButton("Use selected capture for new runs")
        self.use_button.clicked.connect(self.use_selected_capture)
        row.addWidget(self.use_button)
        layout.addLayout(row)
        self.selection_label = QLabel("New runs: Not Configured. Select a capture deliberately after each restart.")
        self.selection_label.setTextFormat(Qt.TextFormat.PlainText)
        self.selection_label.setWordWrap(True)
        layout.addWidget(self.selection_label)
        layout.addStretch()
        self.refresh()

    def refresh(self):
        self.captures.blockSignals(True)
        self.captures.clear()
        self.captures.addItem("Not Configured", "")
        for capture in self.repository.list_all():
            p = capture.provenance
            self.captures.addItem(f"Week {p.declared_start[:10]} · imported {p.imported_at} · {capture.id[:8]}", capture.id)
        self.captures.blockSignals(False)

    @staticmethod
    def capture_detail(capture):
        p = capture.provenance
        return "\n".join([
            f"Declared UTC week: {p.declared_start} → {p.declared_end}",
            f"Imported: {p.imported_at}", f"Source: {p.source_reference}",
            f"Capture: {capture.id}", f"SHA-256: {p.content_sha256}",
            f"Adapter / mapping: {p.adapter_revision} / {p.mapping_revision}",
            f"Timezone: {p.timezone_basis}", f"Knowledge: {p.knowledge_basis}",
            f"{len(capture.events)} records; completeness unverified. Manual gates remain in force.",
            *p.limitations, "", *[event.native_record for event in capture.events],
        ])

    def preview_path(self, path, *, week_start, imported_at=None):
        self.pending_capture = None
        self.save_button.setEnabled(False)
        self.preview.clear()
        capture = import_forex_factory_json(
            Path(path).read_bytes(), week_start=week_start,
            imported_at=imported_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            source_reference=str(Path(path).resolve()),
        )
        self.pending_capture = capture
        self.preview.setPlainText(self.capture_detail(capture))
        self.status_label.setText("Preview only. Check the source week and records before Save capture.")
        self.save_button.setEnabled(True)
        return capture

    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Forex Factory JSON export", "", "JSON files (*.json)")
        if path:
            try:
                self.preview_path(path, week_start=self.week_start.date().toString("yyyy-MM-dd"))
            except (OSError, ValueError) as exc:
                self.status_label.setText(f"Import unavailable: {exc}. No capture saved.")

    def save_pending_capture(self):
        if self.pending_capture is None:
            return
        try:
            self.repository.save(self.pending_capture)
        except (ValueError, sqlite3.Error) as exc:
            self.status_label.setText(f"Capture could not be saved: {exc}")
            return
        capture_id = self.pending_capture.id
        self.pending_capture = None
        self.save_button.setEnabled(False)
        self.refresh()
        self.captures.setCurrentIndex(self.captures.findData(capture_id))
        self.status_label.setText("Capture saved. Use selected capture for new runs to configure it explicitly.")

    def _show_selected(self):
        # Changing what is inspected invalidates an unsaved file preview.
        # Save must never commit different content from the visible preview.
        self.pending_capture = None
        self.save_button.setEnabled(False)
        capture_id = self.captures.currentData()
        if capture_id:
            capture = self.repository.get_by_id(capture_id)
            self.preview.setPlainText(self.capture_detail(capture))
            self.status_label.setText("Inspecting a saved capture. Use selected capture for new runs to configure it.")
        else:
            self.preview.clear()
            self.status_label.setText("No saved capture selected. Preview an export to import it.")

    def use_selected_capture(self):
        capture_id = self.captures.currentData()
        capture = self.repository.get_by_id(capture_id) if capture_id else None
        self.shell.market_context_event_provider = ImportedCaptureProvider(capture) if capture else None
        self.selection_label.setText(
            f"New runs: capture {capture.id[:8]} · week {capture.provenance.declared_start[:10]}. Existing runs unchanged."
            if capture else "New runs: Not Configured. Existing runs unchanged."
        )
