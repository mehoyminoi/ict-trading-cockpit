"""Spacious maintained higher Observed Review with a bounded temporal selector."""
from datetime import datetime
import json
import sqlite3

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from ict_cockpit.analysis.amdx import payload, timestamp
from ict_cockpit.analysis.amdx_context import HIGHER_LEVELS
from ict_cockpit.analysis.amdx_review_scope import day_bounds
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate
from ict_cockpit.gui.amdx_catalog_widget import AMDXCatalogWidget


class _ReviewEntries:
    def __init__(self, pane, amdx):
        self.pane, self.amdx, self.connection = pane, amdx, amdx.connection

    def revise(self, target, **arguments):
        pane = self.pane
        if not pane.allowed() or pane.prepared is None or pane.prepared.target.target != target:
            raise ValueError("Review run or inspected scope changed; reopen Review")
        arguments["operation_id"] = arguments.pop("command_id")
        try:
            return self.amdx.run_observed.revise(pane.prepared, **arguments)
        except RuntimeError as error:
            raise ValueError(str(error)) from error


class AMDXReviewStackWidget(AMDXCatalogWidget):
    def __init__(self, amdx, run_id, *, allowed=None, **kwargs):
        self.amdx, self.run_id = amdx, run_id
        self.allowed = allowed or (lambda: True)
        self.binding = amdx.run_calendar.get_binding(run_id)
        self.launch = amdx.run_calendar.get_result(self.binding["launch_operation_id"]).capture
        self.original_reference = self.launch.projection.reference
        self.selected_reference = self.original_reference
        self.orientations = amdx.run_observed.higher_orientations(run_id)
        self.prepared = None
        self.orientation_selector = QComboBox()
        for item in self.orientations:
            self.orientation_selector.addItem(f'{item["source"]} · {item["reference"]}', item["reference"])
        self._sticky_error = False
        self._restore_failed = False
        super().__init__(_ReviewEntries(self, amdx), reference=self.original_reference,
            clock=lambda: datetime.now().astimezone(), **kwargs)
        if self._restore_failed:
            self._sticky_error = self._read_error = True
            self.status_label.setText("Saved Review navigation unavailable; original launch shown. Use Reload before entry.")
            self._render_editor()
        self.heading.setText(f'AMDX Review · {self.binding["instrument"]} maintained Observed')
        self.layout().itemAt(0).layout().insertWidget(2, self.orientation_selector)
        self.orientation_selector.setVisible(len(self.orientations) > 1)
        self.orientation_selector.currentIndexChanged.connect(self._orientation_changed)
        for control in (self.catalog_selector, self.new_button, self.capture_selector, self.channel_selector,
                        self.previous_button, self.next_button, self.fold_selector, *self.session_buttons.values()):
            control.hide()
        for control in (self.date_input, self.time_input):
            control.setEnabled(False)
            control.hide()
        for label in self.findChildren(QLabel):
            if label.text() in ("Inspect 90-minute quartet", "Interpretation", "Historical reference · New York"):
                label.hide()
        self.table.setRowHidden(5, True)
        self.table.setRowHidden(6, True)
        self.rule_label.setText("One choice records maintained Observed and its run assessment together. Context selection records nothing. Sessions and 90-minute input stay in Review.")

    def reference(self):
        # Keep exact original seconds/offset; the disabled HH:mm controls are display only.
        return self.selected_reference

    def _key(self):
        return "higher-review-v1/" + self.run_id

    def _restore(self):
        self._restore_catalog_id = None
        self._level, self._position = "year", None
        if self.settings is None:
            return
        try:
            value = json.loads(self.settings.value(self._key(), "{}"))
            if not value:
                return
            if set(value) != {"original_reference", "selected_reference", "level", "position"} or (
                value["original_reference"] != self.original_reference.isoformat() or value["level"] not in HIGHER_LEVELS or
                value["position"] is not None and (type(value["position"]) is not int or value["position"] not in (1,2,3,4))
            ):
                raise ValueError("Saved Review navigation differs from this run")
            index = next(i for i, c in enumerate(self.orientations) if c["reference"] == value["selected_reference"])
            self.orientation_selector.setCurrentIndex(index)
            self.selected_reference = timestamp(value["selected_reference"])
            self._level, self._position = value["level"], value["position"]
        except (ValueError, TypeError, KeyError, StopIteration):
            self._warning = "Saved Review navigation unavailable; original launch shown. Use Reload before entry."
            self._restore_failed = True
            self._sticky_error = True

    def _save_navigation(self):
        if self.settings is None or self._rendering or self._read_error:
            return
        self.settings.setValue(self._key(), json.dumps(dict(original_reference=self.original_reference.isoformat(),
            selected_reference=self.selected_reference.isoformat(), level=self._level, position=self._position)))
        self.settings.sync()

    def _load_draft(self):
        # Review provenance is local to this assessment; never consume Lab drafts.
        pass

    def _orientation_changed(self, *args):
        self._invalidate_gesture()
        self.prepared = None
        self.selected_reference = timestamp(self.orientation_selector.currentData())
        self._position = None
        if self._sticky_error:
            self._read_error = True
            self._render_editor()
            return
        self.refresh()

    def select_cell(self, row, column):
        if row >= 5:
            return
        super().select_cell(row, column)

    def inspect_session(self, position):
        return

    def refresh(self):
        self._invalidate_gesture()
        self.prepared = None
        try:
            if not self.allowed():
                raise ValueError("Review run or operation changed; reopen this run's Review")
            with self.amdx.review._snapshot():
                # Obtain all source rows consistently before preparing any editable target.
                snapshot = self.amdx.master.load_stack(self.binding["instrument"], reference=self.reference(), channel="Observed")
                if snapshot.binding.id != self.binding["master_binding_id"]:
                    raise ValueError("Original run master binding differs")
                current = self.amdx.run_observed.higher_orientations(self.run_id)
                if current != self.orientations:
                    raise ValueError("Higher temporal contexts changed; reopen Review")
                self.catalog = self.amdx.catalog.get(self.binding["catalog_id"])
                self.projection = snapshot.projection
                self._read_error = False
                self.set_reference(self.reference(), refresh=False)
                self._render_stack()
                if self._read_error:
                    raise ValueError("Inspected Review basis unavailable; use Reload")
            day, start, end = day_bounds(self.original_reference)
            self.reference_label.setText(f"Reviewed Trading Day {day} · {start.isoformat()} → {end.isoformat()} (end excluded)\n"
                f"Original launch {self.original_reference.isoformat()} · selected higher context {self.reference().isoformat()} · • marks temporal position")
            self._sticky_error = False
            self._warning = ""
            self._save_navigation()
            self.status_label.setText("Maintained Observed · retrospective assessment · original launch remains unchanged")
        except (ValueError, TypeError, KeyError, sqlite3.Error, RuntimeError) as error:
            self._sticky_error = self._read_error = True
            self.target = self.prepared = None
            self._render_editor()
            self.status_label.setText(f"Context unavailable · {error} · use Reload")

    def _render_editor(self):
        self.prepared = None
        if self.target is not None and not self._read_error:
            try:
                if self.target.cycle.layer not in HIGHER_LEVELS:
                    self.target = None
                else:
                    position = next(q.position for q in self.target.cycle.quarters if q.id == self.target.quarter_id)
                    prepared = self.amdx.run_observed.prepare(self.run_id, reference=self.reference(),
                        level=self.target.cycle.layer, position=position, higher_scope=True)
                    if json.loads(prepared.basis_json)["projection"] != payload(self.projection):
                        raise StaleAMDXUpdate("Inspected stack changed; use Reload")
                    self.prepared = prepared
            except (ValueError, TypeError, KeyError, sqlite3.Error, RuntimeError) as error:
                self._sticky_error = self._read_error = True
                self.status_label.setText(f"Context unavailable · {error} · use Reload")
        super()._render_editor()
        for button in self.session_buttons.values():
            button.setEnabled(False)

    def choose(self, *args, **kwargs):
        if not self.allowed():
            self._invalidate_gesture()
            self.set_active(False)
            self.status_label.setText("Entry cancelled because Review run or operation changed")
            return
        super().choose(*args, **kwargs)
        if self._read_error:
            self._sticky_error = True


class AMDXReviewStackDialog(QDialog):
    def __init__(self, amdx, run_id, parent=None, *, allowed=None):
        super().__init__(parent)
        self.setWindowTitle("AMDX · higher Observed Review")
        self.resize(1344, 756)
        layout = QVBoxLayout(self)
        self.pane = AMDXReviewStackWidget(amdx, run_id, allowed=allowed)
        layout.addWidget(self.pane)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.reject)
        layout.addWidget(close)

    def done(self, result):
        self.pane.set_active(False)
        super().done(result)
