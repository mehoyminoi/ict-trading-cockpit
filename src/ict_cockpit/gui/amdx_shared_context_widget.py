"""Quiet shared working orientation; legacy run input remains independently scoped."""
from datetime import datetime
import sqlite3
from uuid import uuid4

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton

from ict_cockpit.analysis.amdx import InterpretationHistory, payload
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate
from ict_cockpit.gui.amdx_context_widget import AMDXContextWidget, role_text
from ict_cockpit.gui.amdx_catalog_widget import LEVEL_NAMES


class AMDXSharedContextWidget(AMDXContextWidget):
    open_stack = Signal(object)

    def __init__(self):
        self.binding = None
        self.shared_projection = None
        self.launch_capture = None
        self.observed_capture = None
        self._observed_prepared = None
        self._review_initial_reference = None
        self._surface_active = True
        self._shared_needs_reload = False
        self._shared_target_reference = None
        self._gesture_scope = None
        self._gesture_mode = None
        self._gesture_cancelled = False
        self._loading = False
        super().__init__()
        self.captured_label = QLabel()
        self.captured_label.setWordWrap(True)
        self.layout().insertWidget(self.layout().count()-1, self.captured_label)
        controls = QHBoxLayout()
        self.full_stack_button = QPushButton("Full AMDX stack")
        self.full_stack_button.clicked.connect(self._open_stack)
        self.reload_button = QPushButton("Reload AMDX")
        self.reload_button.clicked.connect(self._deliberate_reload)
        self.assessment_button = QPushButton("Captured run assessment")
        self.assessment_button.clicked.connect(self._open_assessment)
        self.review_stack_button = QPushButton("Review full AMDX stack")
        self.review_stack_button.clicked.connect(self._open_review_stack)
        controls.addWidget(self.review_stack_button)
        controls.addWidget(self.full_stack_button)
        controls.addWidget(self.reload_button)
        controls.addWidget(self.assessment_button)
        controls.addStretch()
        self.layout().addLayout(controls)

    def set_active(self, active):
        if active != self._surface_active:
            self._gesture_cancelled = True
        self._surface_active = active
        self._render()

    def _deliberate_reload(self):
        self._shared_needs_reload = False
        self.status_label.clear()
        self._gesture_target = self._gesture_reference = self._gesture_scope = None
        self._reload_context()

    def load_context(self, run, market_context, mode_id, **kwargs):
        previous = self.run.id if self.run else None
        if previous != (run.id if run else None):
            self._shared_needs_reload = False
        retained_failure = self.status_label.text()
        if self._gesture_target and (mode_id != self._gesture_mode or previous != (run.id if run else None)):
            self._gesture_cancelled = True
        self._loading = True
        self.binding = self.shared_projection = self.launch_capture = self.observed_capture = self._observed_prepared = None
        self._review_initial_reference = None
        try:
            if mode_id == "post-market" and run and self.repository and self.repository.connection.execute(
                "SELECT 1 FROM amdx_run_binding WHERE run_id=?", (run.id,)).fetchone():
                original_binding = self.repository.run_calendar.get_binding(run.id)
                self._review_initial_reference = self.repository.run_calendar.get_result(
                    original_binding["launch_operation_id"]).capture.projection.reference
            super().load_context(run, market_context, mode_id, **kwargs)
            if run and self.repository:
                saved = self.repository.connection.execute("SELECT 1 FROM amdx_run_binding WHERE run_id=?", (run.id,)).fetchone()
                if saved:
                    self.binding = self.repository.run_calendar.get_binding(run.id)
                    if self.channel == "Expected":
                        if self.reference is None:
                            raise ValueError("Shared working context requires a valid market reference")
                        inspected_reference = self._shared_target_reference if self._pinned and self.target else self.reference
                        snapshot = self.repository.master.load_stack(self.binding["instrument"], reference=inspected_reference)
                        if snapshot.binding.id != self.binding["master_binding_id"]:
                            raise ValueError("Run's canonical master binding is unavailable")
                        self.shared_projection = snapshot.projection
                        self.history = self.repository.catalog.history(snapshot.binding.catalog_id)
                        if not self._pinned and self._gesture_target is None:
                            self._set_current_target()
                        elif self.target and self._gesture_target is None:
                            reference = self._shared_target_reference
                            self.target = self._edit_target(self.target.cycle, self.target.quarter_id)
                            self._shared_target_reference = reference
                    else:
                        self.launch_capture = self.repository.run_calendar.get_result(self.binding["launch_operation_id"]).capture
                        self.observed_capture = self.repository.run_observed.latest(run.id)
                        if self.target:
                            quarter = next(q for q in self.target.cycle.quarters if q.id == self.target.quarter_id)
                            prepared = self.repository.run_observed.prepare(run.id, reference=quarter.start,
                                level=self.target.cycle.layer, position=quarter.position)
                            if prepared.target.target.cycle != self.target.cycle:
                                raise ValueError("Selected Review occurrence differs from maintained calendar")
                            self._observed_prepared = prepared
                            self.history = self.repository.catalog.history(self.binding["catalog_id"])
                            self.comparisons = ()
                            self.target = self._edit_target(self.target.cycle, self.target.quarter_id)
            if self._shared_needs_reload:
                self._read_error = True
                self.status_label.setText(retained_failure or "Shared context unavailable · use Reload AMDX")
        except (ValueError, TypeError, KeyError, sqlite3.Error, RuntimeError) as error:
            self._shared_needs_reload = self._read_error = True
            self.history = InterpretationHistory()
            self.target = None
            self.status_label.setText(f"Shared context unavailable · {error} · use Reload AMDX")
        finally:
            self._loading = False
            self._render()

    def _edit_target(self, cycle, quarter_id):
        target = super()._edit_target(cycle, quarter_id)
        if not self._loading or not self._pinned:
            self._shared_target_reference = self.reference
        return target

    def _scope(self, target, reference):
        prepared = self.repository.run_calendar.prepare_capture(self.run.id, reference=reference)
        if self.shared_projection is None or payload(prepared.snapshot.projection) != payload(self.shared_projection):
            raise StaleAMDXUpdate("Displayed working stack changed; reload before choosing")
        position = next(q.position for q in target.cycle.quarters if q.id == target.quarter_id)
        master_target = self.repository.master.prepare_target(self.binding["instrument"], reference=reference,
            level=target.cycle.layer, position=position)
        if master_target.target.cycle != target.cycle or master_target.target.expected_head_id != target.expected_head_id:
            raise StaleAMDXUpdate("Displayed working quartet changed; reload before choosing")
        return prepared, master_target

    def select_quarter(self, row, column):
        previous = self.target
        retained_reference = self._shared_target_reference
        retained = self._pinned and previous and 0 <= row < len(self.cycles) and self.cycles[row] == previous.cycle
        super().select_quarter(row, column)
        if self.binding:
            if retained and self.channel == "Expected":
                self._shared_target_reference = retained_reference
            self._reload_context()

    def _select_review_session(self, index):
        super()._select_review_session(index)
        if self.binding and self.channel == "Observed" and not self._gesture_target:
            self._reload_context()

    def _load_review_cycles(self, initialize):
        reference = self.reference
        if initialize and self._review_initial_reference is not None:
            self.reference = self._review_initial_reference
        try:
            super()._load_review_cycles(initialize)
        finally:
            self.reference = reference

    def _begin_gesture(self):
        super()._begin_gesture()
        self._gesture_mode = self.mode_id
        self._gesture_cancelled = False
        self._gesture_scope = None
        if self.binding and self.channel == "Expected" and self.target:
            try:
                self._gesture_scope = self._scope(self.target, self._shared_target_reference or self.reference)
            except (ValueError, TypeError, KeyError, sqlite3.Error, RuntimeError) as error:
                self._gesture_cancelled = self._shared_needs_reload = self._read_error = True
                self.status_label.setText(f"Entry unavailable · {error} · use Reload AMDX")
                self._render()
        elif self.binding and self.channel == "Observed":
            self._gesture_scope = self._observed_prepared

    def _end_gesture(self, generation):
        if generation == self._gesture_generation:
            self._gesture_scope = None
        super()._end_gesture(generation)

    def choose(self, role, subtype=None, *, clear_applicability=False):
        if self.binding and (not self._surface_active or self._gesture_cancelled):
            return
        if self.binding and self.channel == "Observed":
            return self._choose_observed(role, subtype, clear_applicability=clear_applicability)
        if not self.binding:
            return super().choose(role, subtype, clear_applicability=clear_applicability)
        target = self._gesture_target or self.target
        scope = self._gesture_scope
        self._gesture_target = self._gesture_reference = self._gesture_scope = None
        self._gesture_clear_applicability = None
        if (self._gesture_cancelled or not self._surface_active or self._read_error or not target
                or target.run_id != self.run.id or self.mode_id not in ("tda", "live-watch")):
            return
        committed = False
        try:
            prepared, master_target = scope or self._scope(target, self._shared_target_reference or self.reference)
            if prepared.run_id != self.run.id:
                raise StaleAMDXUpdate("Run changed during the gesture")
            result = self.repository.run_calendar.revise(prepared, master_target,
                operation_id=str(uuid4()), capture_id=str(uuid4()), recorded_at=datetime.now().astimezone(),
                role=role, anchor_id=str(uuid4()) if role is not None else None,
                source_ref="Technician / maintained working AMDX" if role is not None else "",
                subtype=subtype, clear_applicability=clear_applicability)
            committed = True
            self._reload_context()
            if self._read_error:
                self.status_label.setText("Entry recorded; refreshed context unavailable. Use Reload AMDX.")
                return
            self.status_label.setText("Recorded in maintained calendar" if result.calendar_result.changed else "Already current · run context captured")
            self.recorded.emit(result.calendar_result.claim)
        except (ValueError, TypeError, KeyError, sqlite3.Error, RuntimeError) as error:
            self._shared_needs_reload = self._read_error = True
            self.status_label.setText(("Entry recorded; refresh unavailable" if committed else "Not recorded") + f" · {error} · use Reload AMDX")
            self._render()

    def _choose_observed(self, role, subtype, *, clear_applicability):
        target = self._gesture_target or self.target
        prepared = self._gesture_scope or self._observed_prepared
        self._gesture_target = self._gesture_reference = self._gesture_scope = None
        self._gesture_clear_applicability = None
        if (self._read_error or not target or not prepared or self.mode_id != "post-market"
                or target.run_id != self.run.id or target.channel != "Observed"
                or target.cycle != prepared.target.target.cycle or target.quarter_id != prepared.target.target.quarter_id):
            return
        committed = False
        try:
            result = self.repository.run_observed.revise(prepared, operation_id=str(uuid4()),
                recorded_at=datetime.now().astimezone(), role=role, anchor_id=str(uuid4()) if role is not None else None,
                source_ref="Technician / maintained Observed Review" if role is not None else "", subtype=subtype,
                clear_applicability=clear_applicability)
            committed = True
            self._reload_context()
            if self._read_error:
                self.status_label.setText("Assessment recorded; refresh unavailable · use Reload AMDX")
                return
            self.status_label.setText("Recorded in maintained Observed calendar · run assessment captured"
                if result.changed else "Already current · run assessment captured")
            row = next(r for r in result.projection.cycles if r.context.cycle.id == target.cycle.id)
            self.recorded.emit(row.claim)
        except (ValueError, TypeError, KeyError, sqlite3.Error, RuntimeError) as error:
            self._shared_needs_reload = self._read_error = True
            self.status_label.setText(("Assessment recorded; refresh unavailable" if committed else "Not recorded")
                + f" · {error} · use Reload AMDX")
            self._render()

    def _open_review_stack(self):
        if self.binding and self.channel == "Observed" and self._surface_active and not self._read_error:
            self.open_stack.emit(dict(review_run_id=self.run.id))

    def _open_assessment(self):
        if self.observed_capture and not self._read_error:
            self.open_stack.emit(dict(capture=self.observed_capture, instrument=self.binding["instrument"], run_id=self.run.id))

    def _open_stack(self):
        if not self.binding or self._read_error:
            return
        self.open_stack.emit(dict(instrument=self.binding["instrument"],
            reference=self._shared_target_reference or self.reference, capture=self.launch_capture, run_id=self.run.id))

    def _render(self):
        super()._render()
        if self._loading or not hasattr(self, "captured_label"):
            return
        self.review_stack_button.setVisible(self.binding is not None and self.channel == "Observed")
        self.review_stack_button.setEnabled(not self._read_error and self._surface_active)
        self.captured_label.hide()
        self.assessment_button.setVisible(self.channel == "Observed" and self.observed_capture is not None)
        self.assessment_button.setEnabled(not self._read_error)
        self.full_stack_button.setText("Captured launch stack" if self.channel == "Observed" else "Full AMDX stack")
        self.full_stack_button.setVisible(self.binding is not None)
        self.reload_button.setVisible(self.binding is not None or self._shared_needs_reload)
        self.full_stack_button.setEnabled(not self._read_error)
        if self.binding and self.channel == "Observed":
            self.target_label.setText(self.target_label.text().replace("Observed AMDX", "Maintained Observed AMDX"))
            self.target_label.setToolTip("Current maintained Observed judgment for this run's reviewed day. Entering a phase captures its exact revision for this run; earlier assessments stay immutable.")
        projection = self.launch_capture.projection if self.launch_capture else self.shared_projection
        if projection:
            parts = []
            for row in projection.cycles[:5]:
                quarter = row.context.active_quarter
                phase = row.inference.roles[quarter.position-1] if quarter else None
                position = row.context.position or row.context.state.value
                profile = row.inference.candidates[0].value if len(row.inference.candidates)==1 else row.inference.state
                parts.append(f"{LEVEL_NAMES[row.context.cycle.layer]} {position} "
                             + (role_text(phase.role, phase.subtype) if phase and phase.role else "?") + f" · {profile}")
            self.higher_label.setText(self.binding["instrument"] + " · " + " | ".join(parts))
            self.higher_label.setToolTip("Captured working context at run launch" if self.launch_capture else
                "Maintained working calendar · position and phase are distinct · reference " + projection.reference.isoformat())
            if self.launch_capture:
                self.captured_label.setText("Working context captured at run launch · " + self.launch_capture.projection.reference.isoformat()
                    + " · " + " | ".join(f"{LEVEL_NAMES[r.context.cycle.layer]} "
                        + (r.inference.candidates[0].value if len(r.inference.candidates)==1 else r.inference.state)
                        for r in projection.cycles[-2:]))
                self.captured_label.show()
        elif self.run and not self.binding and not self._shared_needs_reload:
            self.higher_label.setToolTip("Legacy run-owned context; instrument unassigned. It is not merged into the maintained calendar.")
        if self.binding and not self._surface_active:
            for button in (*self.phase_buttons.values(), *self.subtype_buttons.values(), self.more_button):
                button.setEnabled(False)
        if self._shared_needs_reload:
            for button in (*self.phase_buttons.values(), *self.subtype_buttons.values(), self.more_button):
                button.setEnabled(False)
