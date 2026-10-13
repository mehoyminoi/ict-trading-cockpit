"""Spacious catalog orientation with adjacent immediate quarter entry."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from uuid import uuid4

from PySide6.QtCore import QDate, QSettings, QSignalBlocker, QTime, QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFormLayout,
    QGroupBox, QHeaderView, QHBoxLayout, QLabel, QLineEdit, QMenu, QPushButton,
    QTableWidget, QTableWidgetItem, QTimeEdit, QVBoxLayout, QWidget,
)

from ict_cockpit.analysis.amdx import Role, XSubtype, available_roles, aware, canonical_timestamp, timestamp
from ict_cockpit.analysis.amdx_catalog import CaptureBasis, Catalog
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, current_new_york_time
from ict_cockpit.database.amdx_catalog_repository import CatalogTarget


LEVEL_NAMES = {
    "cycle_16y": "16-year", "quadrennial": "Quadrennial", "year": "Yearly",
    "month": "Monthly", "week": "Weekly", "day": "Sessions", "session": "90-minute",
}


def historical_reference(day, clock, fold=0):
    """Reject skipped wall times and retain repeated-hour choice explicitly."""
    value = datetime(day.year(), day.month(), day.day(), clock.hour(), clock.minute(),
                     tzinfo=MARKET_TIMEZONE, fold=fold)
    restored = value.astimezone(timezone.utc).astimezone(MARKET_TIMEZONE)
    if restored.replace(tzinfo=None) != value.replace(tzinfo=None):
        raise ValueError("This New York time did not occur; choose a valid historical time")
    return canonical_timestamp(value)


def _role_text(role, subtype=None):
    return f"X({subtype.value if subtype else '?'})" if role is Role.X else role.value


class AMDXCatalogWidget(QWidget):
    recorded = Signal(object)
    def __init__(self, repository, *, reference=None, settings=None, clock=None):
        super().__init__()
        self.repository = repository
        self.clock = clock or current_new_york_time
        self.active = True
        self.catalog = None
        self.projection = None
        self.target = None
        self._level = "session"
        self._position = None
        self._generation = 0
        self._gesture = None
        self._rendering = False
        self._read_error = False
        self._warning = ""
        self._drafts = {}
        if settings is None:
            db = next((row[2] for row in repository.connection.execute("PRAGMA database_list") if row[1] == "main"), "")
            settings = QSettings(str(Path(db).with_name(Path(db).name + ".amdx-lab.ini")), QSettings.Format.IniFormat) if db else None
        self.settings = settings

        heading = self.heading = QLabel("AMDX Lab · Historical catalog")
        heading.setStyleSheet("font-size: 20px; font-weight: 600;")
        self.catalog_selector = QComboBox()
        self.catalog_selector.setMinimumContentsLength(20)
        self.catalog_selector.currentIndexChanged.connect(self._catalog_changed)
        self.new_button = QPushButton("New MNQ catalog…")
        self.new_button.clicked.connect(self._new_catalog_dialog)
        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.refresh)
        top = QHBoxLayout()
        top.addWidget(heading)
        top.addStretch()
        top.addWidget(self.catalog_selector, 1)
        top.addWidget(self.new_button)
        top.addWidget(self.reload_button)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDateRange(QDate(1, 1, 1), QDate(9998, 12, 31))
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        self.fold_selector = QComboBox()
        self.fold_selector.addItems(["First occurrence", "Second occurrence"])
        self.fold_selector.setToolTip("The New York autumn clock repeats this hour; choose its exact occurrence.")
        self.channel_selector = QComboBox()
        self.channel_selector.addItems(["Observed", "Expected"])
        self.reference_label = QLabel()
        self.reference_label.setWordWrap(True)
        self.session_buttons = {}
        sessions = QHBoxLayout()
        sessions.addWidget(QLabel("Inspect 90-minute quartet"))
        for position, name in enumerate(("Asia", "London", "NYAM", "NYPM"), 1):
            button = QPushButton(name)
            button.clicked.connect(lambda _checked=False, p=position: self.inspect_session(p))
            self.session_buttons[name] = button
            sessions.addWidget(button)
        sessions.addStretch()
        self.previous_button = QPushButton("← Day")
        self.next_button = QPushButton("Day →")
        self.previous_button.clicked.connect(lambda: self.date_input.setDate(self.date_input.date().addDays(-1)))
        self.next_button.clicked.connect(lambda: self.date_input.setDate(self.date_input.date().addDays(1)))
        nav = QHBoxLayout()
        nav.addWidget(QLabel("Historical reference · New York"))
        nav.addWidget(self.previous_button)
        nav.addWidget(self.date_input)
        nav.addWidget(self.time_input)
        nav.addWidget(self.fold_selector)
        nav.addWidget(self.next_button)
        nav.addStretch()
        nav.addWidget(QLabel("Interpretation"))
        nav.addWidget(self.channel_selector)

        self.table = QTableWidget(7, 6)
        self.table.setHorizontalHeaderLabels(["Level / occurrence", "Q1", "Q2", "Q3", "Q4", "Profile"])
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(65)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setMinimumHeight(485)
        self.table.cellClicked.connect(self.select_cell)
        self.table.currentCellChanged.connect(lambda row, column, _old_row, _old_column: self.select_cell(row, column))

        inspector = QGroupBox("Selected quarter")
        right = QVBoxLayout(inspector)
        self.target_label = QLabel("Choose a catalog to begin")
        self.target_label.setWordWrap(True)
        self.target_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.bounds_label = QLabel()
        self.bounds_label.setWordWrap(True)
        self.basis_label = QLabel()
        self.basis_label.setWordWrap(True)
        self.basis_label.setMinimumHeight(52)
        right.addWidget(self.target_label)
        right.addWidget(self.bounds_label)
        right.addWidget(self.basis_label)
        buttons = QHBoxLayout()
        self.phase_buttons = {}
        for role in (Role.A, Role.M, Role.D, Role.X):
            button = QPushButton("X(?)" if role is Role.X else role.value)
            self._connect_choice(button, role)
            self.phase_buttons[role] = button
            buttons.addWidget(button)
        right.addLayout(buttons)
        more = QHBoxLayout()
        self.subtype_buttons = {}
        for subtype in XSubtype:
            button = QPushButton(f"X({subtype.value})")
            self._connect_choice(button, Role.X, subtype)
            self.subtype_buttons[subtype] = button
            more.addWidget(button)
        self.more_button = QPushButton("Other…")
        self.menu = QMenu(self)
        self.menu.aboutToShow.connect(self._begin_gesture)
        self.menu.aboutToHide.connect(self._end_gesture_later)
        self.unknown_action = self.menu.addAction("Unknown")
        self.na_action = self.menu.addAction("Not Applicable · whole quartet")
        self.clear_action = self.menu.addAction("Clear this anchor")
        self.clear_na_action = self.menu.addAction("Clear whole-quartet Not Applicable")
        self.unknown_action.triggered.connect(lambda: self.choose(Role.UNKNOWN))
        self.na_action.triggered.connect(lambda: self.choose(Role.NOT_APPLICABLE))
        self.clear_action.triggered.connect(lambda: self.choose(None))
        self.clear_na_action.triggered.connect(lambda: self.choose(None, clear_applicability=True))
        self.more_button.setMenu(self.menu)
        more.addWidget(self.more_button)
        right.addLayout(more)
        rule = QLabel("One accepted choice records immediately. The other quarters show implied context; navigation records nothing.")
        self.rule_label = rule
        rule.setWordWrap(True)
        right.addWidget(rule)
        self.definition_label = QLabel()
        self.definition_label.setWordWrap(True)
        right.addWidget(self.definition_label)

        self.details_button = QPushButton("Entry provenance ▸")
        self.details_button.setCheckable(True)
        right.addWidget(self.details_button)
        self.details = QWidget()
        form = QFormLayout(self.details)
        self.capture_selector = QComboBox()
        self.capture_selector.addItems(["Historical entry", "Forward entry (declared)"])
        self.evidence_input = QLineEdit()
        self.definition_input = QLineEdit()
        self.availability_input = QLineEdit()
        self.availability_input.setPlaceholderText("Optional ISO time with offset; empty = unspecified")
        form.addRow("Capture", self.capture_selector)
        form.addRow("Evidence", self.evidence_input)
        form.addRow("Definition", self.definition_input)
        form.addRow("Information available", self.availability_input)
        form.addRow(QLabel("Backfilled Expected is retrospective; declared forward entry does not prove no look-ahead."))
        self.details.hide()
        self.details_button.toggled.connect(self.details.setVisible)
        right.addWidget(self.details)
        right.addStretch()
        body = QHBoxLayout()
        body.addWidget(self.table, 3)
        body.addWidget(inspector, 2)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.addLayout(top)
        layout.addLayout(nav)
        layout.addWidget(self.reference_label)
        layout.addLayout(sessions)
        layout.addLayout(body, 1)
        layout.addWidget(self.status_label)

        self.date_input.dateChanged.connect(self._navigation_changed)
        self.time_input.timeChanged.connect(self._navigation_changed)
        self.fold_selector.currentIndexChanged.connect(self._navigation_changed)
        self.channel_selector.currentIndexChanged.connect(self._navigation_changed)
        self.capture_selector.currentIndexChanged.connect(self._metadata_changed)
        for field in (self.evidence_input, self.definition_input, self.availability_input):
            field.textChanged.connect(self._metadata_changed)
        self.set_reference(reference or self.clock(), refresh=False)
        self._restore()
        self.refresh()

    def _connect_choice(self, button, role, subtype=None):
        button.setToolTip("Record one catalog revision; earlier interpretations remain saved.")
        button.pressed.connect(self._begin_gesture)
        button.released.connect(self._end_gesture_later)
        button.clicked.connect(lambda _checked=False: self.choose(role, subtype))

    def set_active(self, active):
        if self.active != active:
            self.active = active
            self._invalidate_gesture()
        self._render_editor()

    def _invalidate_gesture(self):
        self._generation += 1

    def _begin_gesture(self):
        try:
            capture = self._capture()
        except (ValueError, TypeError):
            capture = None
        self._gesture = (self._generation, self.target, capture)

    def _end_gesture_later(self):
        gesture = self._gesture
        QTimer.singleShot(0, lambda: self._finish_gesture(gesture))

    def _finish_gesture(self, gesture):
        if self._gesture is gesture:
            self._gesture = None

    def set_reference(self, value, *, refresh=True):
        value = timestamp(value) if isinstance(value, str) else value
        value = aware(value).astimezone(MARKET_TIMEZONE)
        blockers = [QSignalBlocker(w) for w in (self.date_input, self.time_input, self.fold_selector)]
        self.date_input.setDate(QDate(value.year, value.month, value.day))
        self.time_input.setTime(QTime(value.hour, value.minute))
        self.fold_selector.setCurrentIndex(value.fold)
        del blockers
        if refresh:
            self._navigation_changed()

    def reference(self):
        return historical_reference(self.date_input.date(), self.time_input.time(), self.fold_selector.currentIndex())

    def _navigation_changed(self, *args):
        self._invalidate_gesture()
        if self._rendering:
            return
        self.refresh()

    def _catalog_changed(self, *args):
        if self._rendering:
            return
        self._invalidate_gesture()
        if self.catalog_selector.currentData() and self._warning.startswith("The previous catalog"):
            self._warning = ""
        self._load_draft()
        self.refresh()

    def _capture(self):
        value = self.availability_input.text().strip()
        return CaptureBasis("ForwardEntry" if self.capture_selector.currentIndex() else "HistoricalEntry",
            timestamp(value) if value else None, self.evidence_input.text().strip(), self.definition_input.text().strip())

    def _metadata_changed(self, *args):
        if not self._rendering:
            self._invalidate_gesture()
            self._save_navigation()
            self._render_editor()
            if self._warning:
                self.status_label.setText(self._warning)

    def _load_draft(self):
        id = self.catalog_selector.currentData()
        value = self._drafts.get(id, {})
        catalog = next((c for c in getattr(self, "catalogs", ()) if c.id == id), None)
        self._rendering = True
        self.capture_selector.setCurrentIndex(value.get("capture", int(bool(catalog and getattr(catalog, "purpose", "") == "ForwardTest"))))
        self.evidence_input.setText(value.get("evidence", ""))
        self.definition_input.setText(value.get("definition", catalog.definition_ref if catalog else ""))
        self.availability_input.setText(value.get("availability", ""))
        self._rendering = False

    def _restore(self):
        self._restore_catalog_id = None
        if self.settings is None:
            return
        try:
            value = json.loads(self.settings.value("catalog-view-v1", "{}"))
            self._drafts = value.get("drafts", {})
            if not isinstance(self._drafts, dict):
                raise ValueError("Invalid navigation drafts")
            for id, draft in self._drafts.items():
                if not isinstance(id, str) or not isinstance(draft, dict) or (
                    type(draft.get("capture")) is not int or draft["capture"] not in (0, 1)
                ) or any(not isinstance(draft.get(key), str) for key in ("evidence", "definition", "availability")):
                    raise ValueError("Invalid navigation draft fields")
            if value.get("channel", "Observed") not in ("Observed", "Expected"):
                raise ValueError("Invalid restored channel")
            self._restore_catalog_id = value.get("catalog_id")
            if value.get("reference"):
                self.set_reference(timestamp(value["reference"]), refresh=False)
            self._level = value.get("level", "session")
            self._position = value.get("position")
            if self._level not in LEVEL_NAMES or (self._position is not None and (type(self._position) is not int or self._position not in (1, 2, 3, 4))):
                raise ValueError("Invalid restored quarter")
            with QSignalBlocker(self.channel_selector):
                self.channel_selector.setCurrentText(value.get("channel", "Observed"))
        except (ValueError, TypeError, AttributeError, KeyError):
            self._drafts = {}
            self._level, self._position = "session", None
            self._restore_catalog_id = None
            self._warning = "Saved navigation could not be restored; inspect the displayed reference before entry."

    def _save_navigation(self):
        if self.settings is None or self._rendering:
            return
        id = self.catalog_selector.currentData()
        if id:
            self._drafts[id] = dict(capture=self.capture_selector.currentIndex(), evidence=self.evidence_input.text(),
                definition=self.definition_input.text(), availability=self.availability_input.text())
        try:
            reference = self.reference().isoformat()
        except ValueError:
            return
        value = dict(catalog_id=id, reference=reference, channel=self.channel_selector.currentText(),
                     level=self._level, position=self._position, drafts=self._drafts)
        self.settings.setValue("catalog-view-v1", json.dumps(value))
        self.settings.sync()
        if self.settings.status() != QSettings.Status.NoError:
            self._warning = "Navigation preferences could not be saved; recorded AMDX remains in the database."

    def create_catalog(self, title, purpose="Backtest", definition_ref=""):
        catalog = self.repository.create(Catalog(str(uuid4()), title.strip(), purpose=purpose, definition_ref=definition_ref.strip()))
        self._restore_catalog_id = catalog.id
        self.refresh()
        self._load_draft()
        self._save_navigation()
        return catalog

    def _new_catalog_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("New MNQ catalog")
        layout = QFormLayout(dialog)
        title = QLineEdit("MNQ historical study")
        purpose = QComboBox()
        purpose.addItems(["Backtest", "ForwardTest"])
        definition = QLineEdit()
        definition.setPlaceholderText("Optional method / definition revision")
        layout.addRow("Name", title)
        layout.addRow("Purpose", purpose)
        layout.addRow("Definition", definition)
        error = QLabel()
        error.setWordWrap(True)
        layout.addRow(error)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addRow(buttons)
        buttons.rejected.connect(dialog.reject)
        def accept():
            try:
                self.create_catalog(title.text(), purpose.currentText(), definition.text())
            except (ValueError, sqlite3.Error) as exc:
                error.setText(str(exc))
                return
            dialog.accept()
        buttons.accepted.connect(accept)
        dialog.exec()

    def refresh(self):
        self._invalidate_gesture()
        try:
            with self.repository.amdx.review._snapshot():
                self.catalogs = self.repository.list_catalogs()
                wanted = self._restore_catalog_id or self.catalog_selector.currentData()
                self._restore_catalog_id = None
                self._rendering = True
                with QSignalBlocker(self.catalog_selector):
                    self.catalog_selector.clear()
                    for c in self.catalogs:
                        self.catalog_selector.addItem(f"{c.instrument} · {c.title}", c.id)
                    index = self.catalog_selector.findData(wanted)
                    self.catalog_selector.setCurrentIndex(index if index >= 0 else (0 if self.catalogs and not wanted else -1))
                    if wanted and index < 0:
                        self._warning = "The previous catalog is unavailable; explicitly choose a catalog before entry."
                self._rendering = False
                self.catalog = next((c for c in self.catalogs if c.id == self.catalog_selector.currentData()), None)
                reference = self.reference()
                local = reference.astimezone(MARKET_TIMEZONE)
                ambiguous = local.replace(fold=0).utcoffset() != local.replace(fold=1).utcoffset()
                self.fold_selector.setVisible(ambiguous)
                self.reference_label.setText(f"Reference {reference.isoformat()} · • marks position at reference; the selected cell is the inspected quarter")
                self.projection = self.repository.load_stack(self.catalog.id, reference=reference,
                    channel=self.channel_selector.currentText()) if self.catalog else None
            self._read_error = False
            self._load_draft()
            self._render_stack()
            self._save_navigation()
            self.status_label.setText(self._warning or ("Select a quarter; one phase choice records it immediately." if self.catalog else "Create an MNQ catalog to begin historical entry. No trading run is needed."))
        except (ValueError, TypeError, sqlite3.Error) as exc:
            self._rendering = False
            self._read_error = True
            self.target = None
            self.status_label.setText(f"Context unavailable — entry disabled. {exc}. Use Reload after correcting the source/reference.")
            self._render_editor()

    def _render_stack(self):
        self._rendering = True
        self.target = None
        self.table.clearContents()
        if self.projection is not None:
            for row, item in enumerate(self.projection.cycles):
                context = item.context
                occurrence = context.cycle.id.rsplit(':', 1)[-1]
                if context.cycle.layer == "session":
                    day = next(r.context.cycle for r in self.projection.cycles if r.context.cycle.layer == "day")
                    parent = next(q for q in day.quarters if q.id == context.cycle.parent_quarter_id)
                    occurrence = f"{parent.label} · {day.id.rsplit(':', 1)[-1]}"
                self.table.setItem(row, 0, QTableWidgetItem(f"{LEVEL_NAMES[context.cycle.layer]}\n{occurrence} · {context.state.value}"))
                for column, (quarter, role) in enumerate(zip(context.cycle.quarters, item.inference.roles), 1):
                    text = "—" if role.role is None or role.origin == "Unresolved" else _role_text(role.role, role.subtype)
                    origin = "entered" if role.origin == "Technician" else "implied" if role.origin == "Implied" else "unresolved"
                    marker = "• " if quarter == context.active_quarter else ""
                    label = f"Week {quarter.position} · {quarter.label.rsplit(' ', 1)[-1][5:]}" if context.cycle.layer == "month" else quarter.label
                    if context.cycle.layer == "week":
                        label = quarter.label.split()[0]
                    cell = QTableWidgetItem(f"{marker}{label}\n{text} · {origin}")
                    cell.setToolTip(f"{quarter.label}\n{quarter.start.isoformat()} → {quarter.end.isoformat()}\n{context.cycle.id}\n{origin}; • marks temporal position, not an inferred AMDX phase.")
                    self.table.setItem(row, column, cell)
                profile = item.inference.candidates[0].value if len(item.inference.candidates) == 1 else item.inference.state
                self.table.setItem(row, 5, QTableWidgetItem(profile))
            if len(self.projection.cycles) == 5:
                for index, name in ((5, "Sessions"), (6, "90-minute")):
                    self.table.setItem(index, 0, QTableWidgetItem(f"{name}\nClosed reference"))
                    self.table.setItem(index, 5, QTableWidgetItem("Unavailable"))
            selected = next((i for i, row in enumerate(self.projection.cycles) if row.context.cycle.layer == self._level), None)
            if selected is not None:
                row = self.projection.cycles[selected]
                if self._position is None:
                    active = row.context.active_quarter
                    self._position = active.position if active else None
                if self._position is not None:
                    self.table.setCurrentCell(selected, self._position)
                    quarter = row.context.cycle.quarters[self._position-1]
                    self.target = CatalogTarget(self.catalog.id, self.catalog.instrument, self.projection.channel,
                        row.context.cycle, quarter.id, canonical_timestamp(self.projection.reference), row.claim.id if row.claim else None)
        self._rendering = False
        self._render_editor()

    def inspect_session(self, position):
        if self._read_error or self.projection is None:
            return
        day = next((r.context.cycle for r in self.projection.cycles if r.context.cycle.layer == "day"), None)
        if day is None:
            return
        self._level = "session"
        self.set_reference(day.quarters[position-1].start)

    def select_cell(self, row, column):
        if self._rendering or self._read_error or self.projection is None or not 0 <= row < len(self.projection.cycles):
            return
        self._invalidate_gesture()
        if column in (0, 5):
            active = self.projection.cycles[row].context.active_quarter
            column = active.position if active else None
        if column is not None and column not in (1, 2, 3, 4):
            return
        self._level = self.projection.cycles[row].context.cycle.layer
        self._position = column
        self._render_stack()
        self._save_navigation()

    def _render_editor(self):
        target = self.target
        enabled = self.active and target is not None and not self._read_error
        for button in self.session_buttons.values():
            button.setEnabled(self.projection is not None and len(self.projection.cycles) == 7 and not self._read_error)
        position = next((q.position for q in target.cycle.quarters if q.id == target.quarter_id), 0) if target else 0
        allowed = available_roles(position) if position else ()
        for role, button in self.phase_buttons.items():
            button.setEnabled(enabled and role in allowed)
        for button in self.subtype_buttons.values():
            button.setEnabled(enabled and Role.X in allowed)
        self.more_button.setEnabled(enabled)
        if not target:
            self.target_label.setText("Select Q1–Q4 to inspect and edit" if self.catalog else "Choose a catalog to begin")
            self.bounds_label.clear()
            self.basis_label.clear()
        else:
            quarter = next(q for q in target.cycle.quarters if q.id == target.quarter_id)
            row = next(r for r in self.projection.cycles if r.context.cycle.id == target.cycle.id)
            self.target_label.setText(f"{target.instrument} · {LEVEL_NAMES[target.cycle.layer]} · Q{position}\n{quarter.label} · {target.channel}")
            self.bounds_label.setText(f"{quarter.start.isoformat()}\n→ {quarter.end.isoformat()}")
            role = row.inference.roles[position-1]
            value = _role_text(role.role, role.subtype) if role.role is not None else "Unresolved"
            origin = "Entered" if role.origin == "Technician" else "Implied" if role.origin == "Implied" else "Unresolved"
            meaning = "Unresolved · no active anchor" if origin == "Unresolved" else f"{value} · {origin}"
            self.basis_label.setText(meaning + (f"\nRecorded {row.claim.recorded_at.isoformat()}" if row.claim else ""))
        self.definition_label.setText(
            f"{getattr(self.catalog, 'purpose', 'Maintained calendar')} · {self.capture_selector.currentText()}\n"
            f"Definition: {self.definition_input.text().strip() or 'unspecified'}"
            if self.catalog else "")

    def choose(self, role, subtype=None, *, clear_applicability=False):
        if not self.active or self._read_error or self.target is None:
            return
        try:
            capture = self._capture()
            if self._gesture is not None:
                generation, target, original_capture = self._gesture
                if generation != self._generation or target != self.target or capture != original_capture:
                    self.status_label.setText("Entry cancelled because selection or provenance changed. Inspect the current quarter, then choose again.")
                    return
            target = self.target
            id = str(uuid4())
            result = self.repository.revise(target, command_id=id, recorded_at=self.clock(), role=role,
                anchor_id=str(uuid4()) if role is not None else None,
                source_ref=capture.evidence_ref or "Technician catalog entry" if role is not None else "",
                subtype=subtype, capture=capture, clear_applicability=clear_applicability)
            self.recorded.emit(result)
            self.refresh()
            if self._read_error:
                self.status_label.setText("Entry recorded, but refreshed context is unavailable. Entry is disabled; use Reload to inspect the committed result.")
                return
            self.status_label.setText(("Recorded" if result.changed else "Unchanged meaning; capture basis recorded") + f" · {target.instrument} · {target.channel} · {target.cycle.layer}" + (f". {self._warning}" if self._warning else ""))
        except (ValueError, TypeError, sqlite3.Error) as exc:
            self._read_error = True
            self._invalidate_gesture()
            self.status_label.setText(f"Entry not recorded — {exc}. Use Reload, inspect the committed context, then choose again.")
            self._render_editor()
