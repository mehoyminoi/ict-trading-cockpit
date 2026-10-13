"""Shared compact working AMDX entry; rendering/navigation never records a phase."""
from dataclasses import dataclass
from datetime import datetime
import sqlite3
from uuid import uuid4

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHeaderView, QHBoxLayout, QLabel, QMenu,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from ict_cockpit.analysis.amdx import (
    Anchor, Cycle, InterpretationHistory, Role, XSubtype, infer_profile, intraday_cycles, timestamp,
)
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.quarter_theory import QT_LEVELS, normalize_qt_context
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate


@dataclass(frozen=True)
class EditTarget:
    run_id: str
    cycle: Cycle
    quarter_id: str
    expected_head_id: str | None


def role_text(role, subtype=None):
    return f"X({subtype.value if subtype else '?'})" if role is Role.X else role.value


class AMDXContextWidget(QFrame):
    recorded = Signal(object)

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.repository = None
        self.run = None
        self.mode_id = ""
        self.reference = None
        self.cycles = ()
        self.history = InterpretationHistory()
        self.target = None
        self._pinned = False
        self._read_error = False
        self._gesture_target = None
        self._gesture_reference = None
        self._table_rendering = False

        self.target_label = QLabel("AMDX · No active quarter")
        self.target_label.setWordWrap(True)
        self.target_label.setStyleSheet("font-weight: 600;")
        bar = QHBoxLayout()
        bar.setContentsMargins(0, 0, 0, 0)
        bar.setSpacing(3)
        bar.addWidget(self.target_label, 1)
        self.phase_buttons = {}
        for role in (Role.A, Role.M, Role.D, Role.X):
            button = QPushButton("X(?)" if role is Role.X else role.value)
            button.setMaximumWidth(48)
            button.setToolTip("Record this explicit anchor immediately; sibling roles are implied.")
            button.pressed.connect(self._begin_gesture)
            button.released.connect(lambda: QTimer.singleShot(0, self._end_gesture))
            button.clicked.connect(lambda _checked=False, r=role: self.choose(r))
            self.phase_buttons[role] = button
            bar.addWidget(button)
        self.more_button = QPushButton("…")
        self.more_button.setMaximumWidth(32)
        self.more_button.setToolTip("X subtype, uncertainty or clear this anchor")
        self.menu = QMenu(self)
        self.menu.aboutToShow.connect(self._begin_gesture)
        self.menu.aboutToHide.connect(lambda: QTimer.singleShot(0, self._end_gesture))
        self.menu_actions = {}
        for label, role, subtype in (
            ("X(C) · Continuation", Role.X, XSubtype.CONTINUATION),
            ("X(R) · Reversal", Role.X, XSubtype.REVERSAL),
            ("Unknown", Role.UNKNOWN, None),
            ("Not Applicable", Role.NOT_APPLICABLE, None),
            ("Clear this anchor", None, None),
        ):
            action = self.menu.addAction(label)
            action.triggered.connect(lambda _checked=False, r=role, s=subtype: self.choose(r, s))
            self.menu_actions[label] = action
        self.more_button.setMenu(self.menu)
        bar.addWidget(self.more_button)
        self.follow_button = QPushButton("Follow current")
        self.follow_button.clicked.connect(self.follow_current)
        bar.addWidget(self.follow_button)

        self.table = QTableWidget(2, 5)
        self.table.setHorizontalHeaderLabels(["Q1", "Q2", "Q3", "Q4", "Profile"])
        self.table.setVerticalHeaderLabels(["Day", "Session"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setFixedHeight(98)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.cellClicked.connect(self.select_quarter)
        self.table.currentCellChanged.connect(self._selection_changed)
        self.higher_label = QLabel()
        self.higher_label.setWordWrap(True)
        self.status_label = QLabel("AMDX history not loaded")
        self.status_label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)
        layout.addLayout(bar)
        layout.addWidget(self.table)
        layout.addWidget(self.higher_label)
        layout.addWidget(self.status_label)
        self._render()

    def set_repository(self, repository):
        self.repository = repository

    def load_context(self, run, market_context, mode_id):
        changed_run = (self.run.id if self.run else None) != (run.id if run else None)
        self.run, self.mode_id = run, mode_id
        if changed_run:
            self.target, self._pinned = None, False
            self._gesture_target = self._gesture_reference = None
            self.status_label.setText("")
            self.history = InterpretationHistory()
        self.reference = None
        self.cycles = ()
        try:
            if run and market_context.get("captured_at"):
                self.reference = timestamp(market_context["captured_at"])
                self.cycles = intraday_cycles(self.reference)
        except (ValueError, TypeError):
            pass
        prior_read_error = self._read_error
        self._read_error = False
        if self.repository is not None and run:
            try:
                self.history = self.repository.get_history(run.id)
                if prior_read_error:
                    self.status_label.setText("")
            except (ValueError, TypeError, KeyError, sqlite3.Error, RuntimeError) as error:
                self._read_error = True
                self.status_label.setText(f"History unavailable · {error}")
        else:
            self.history = InterpretationHistory()
        if not self._pinned and self._gesture_target is None:
            self._set_current_target()
        # Preserve the selected scope even when its session/day leaves the clock's view.
        if self.target and (self._pinned or self._gesture_target) and self.target.cycle not in self.cycles:
            if self.target.cycle.layer == "day":
                self.cycles = (self.target.cycle,)
            else:
                parent = next((c.cycle for c in reversed(self.history.claims)
                               if any(q.id == self.target.cycle.parent_quarter_id for q in c.cycle.quarters)), None)
                if parent is None:
                    historical = intraday_cycles(self.target.cycle.quarters[0].start)
                    parent = historical[0] if historical else None
                self.cycles = (parent, self.target.cycle) if parent else (self.target.cycle,)
        self._render()

    def _head(self, cycle):
        return next((c for c in reversed(self.history.claims) if
                     c.cycle.id == cycle.id and c.branch_id == "working" and c.channel == "Expected"), None)

    def _set_current_target(self):
        if not self.cycles or self.reference is None or self.run is None:
            self.target = None
            return
        cycle = self.cycles[-1]
        quarter = cycle.quarter_at(self.reference)
        if quarter is None:
            self.target = None
            return
        head = self._head(cycle)
        self.target = EditTarget(self.run.id, cycle, quarter.id, head.id if head else None)

    def select_quarter(self, row, column):
        if not 0 <= row < len(self.cycles) or not 0 <= column < 4 or not self.run:
            return
        cycle = self.cycles[row]
        head = self._head(cycle)
        self.target = EditTarget(self.run.id, cycle, cycle.quarters[column].id, head.id if head else None)
        self._pinned = True
        self._render()

    def _selection_changed(self, row, column, _old_row, _old_column):
        if not self._table_rendering:
            self.select_quarter(row, column)

    def follow_current(self):
        self._pinned = False
        self.target = None
        self._gesture_target = self._gesture_reference = None
        self._reload_context()

    def _reload_context(self):
        self.load_context(self.run, {"captured_at": self.reference.isoformat()} if self.reference else {}, self.mode_id)

    def _begin_gesture(self):
        self._gesture_target, self._gesture_reference = self.target, self.reference

    def _end_gesture(self):
        if self._gesture_target is None:
            return
        self._gesture_target = self._gesture_reference = None
        if not self._pinned:
            self._reload_context()

    def choose(self, role, subtype=None):
        target = self._gesture_target or self.target
        reference = self._gesture_reference or self.reference
        self._gesture_target = self._gesture_reference = None
        if (not target or not reference or not self.repository or self._read_error or not self.run
                or target.run_id != self.run.id or self.mode_id not in ("tda", "live-watch")):
            return
        anchor = Anchor(str(uuid4()), target.quarter_id, role, "Technician / working AMDX", subtype) if role else None
        try:
            claim = self.repository.accept(
                claim_id=str(uuid4()), run_id=target.run_id, branch_id="working", channel="Expected",
                cycle=target.cycle, quarter_id=target.quarter_id, anchor=anchor,
                recorded_at=datetime.now().astimezone(), market_reference=reference,
                expected_head_id=target.expected_head_id,
            )
        except (ValueError, TypeError, KeyError, sqlite3.Error, RuntimeError) as error:
            self.status_label.setText(f"Not recorded · {error}")
            # Keep a failed choice's scope visible for a deliberate retry or release.
            self.target, self._pinned = target, True
            if isinstance(error, StaleAMDXUpdate):
                # Refresh the inspected head, but require another deliberate choice.
                # The gesture's earlier reference belongs to the attempted claim,
                # not to the clock that continues advancing behind the pin.
                self._reload_context()
                head = self._head(target.cycle)
                self.target = EditTarget(target.run_id, target.cycle, target.quarter_id, head.id if head else None)
            self._render()
            return
        self.history = InterpretationHistory(self.history.claims + (claim,))
        self.target = EditTarget(target.run_id, target.cycle, target.quarter_id, claim.id)
        self.status_label.setText("Recorded · " + claim.inference.state + " · entered anchors / implied siblings")
        if self._pinned:
            self._render()
        else:
            self._reload_context()
        self.recorded.emit(claim)

    def _render_table(self):
        self.table.setRowCount(len(self.cycles))
        self.table.setVerticalHeaderLabels(["Day" if c.layer == "day" else "90m" for c in self.cycles])
        for row, cycle in enumerate(self.cycles):
            head = self._head(cycle)
            inference = head.inference if head else infer_profile(cycle, ())
            for col, quarter in enumerate(cycle.quarters):
                derived = next((r for r in inference.roles if r.quarter_id == quarter.id), None)
                explicit = next((a for a in (head.anchors if head else ()) if a.quarter_id == quarter.id), None)
                phase = role_text(explicit.role, explicit.subtype) if explicit else role_text(derived.role, derived.subtype) if derived else "?"
                origin = "entered" if explicit else "implied" if derived and derived.origin == "Implied" else "unresolved"
                label = quarter.label if cycle.layer == "day" else quarter.start.astimezone(MARKET_TIMEZONE).strftime("%H:%M")
                item = QTableWidgetItem(f"{label} · {phase}\n{origin}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setToolTip(f"{quarter.id}\n{quarter.start.isoformat()} → {quarter.end.isoformat()}\n"
                                f"{inference.structural_revision}; {origin}\n" + "\n".join(inference.reasons))
                self.table.setItem(row, col, item)
                if self.target and self.target.quarter_id == quarter.id:
                    self.table.setCurrentCell(row, col)
            profile = "/".join(p.value for p in inference.candidates) if inference.state == "Resolved" else inference.state
            profile_item = QTableWidgetItem(profile)
            profile_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            profile_item.setToolTip("AMDX = A → M → D → X; XAMD = X → A → M → D.\n"
                                    "Manual anchors constrain one quartet; X subtype is separate.\n"
                                    "Candidate orders: " + ", ".join(p.value for p in inference.candidates)
                                    + "\n" + "\n".join(inference.reasons))
            self.table.setItem(row, 4, profile_item)

    def _render(self):
        self._table_rendering = True
        try:
            self._render_table()
        finally:
            self._table_rendering = False
        legacy = normalize_qt_context(self.run.qt_context if self.run else {})
        self.higher_label.setText("Higher QT · " + " · ".join(
            f"{label} {legacy[level]}" for level, label in QT_LEVELS[:5]
        ) + " · legacy/derived context")
        self.higher_label.setToolTip("Earlier flat entries retain their provenance. They are not migrated cycle anchors or rule-derived siblings.")
        quarter = next((q for q in self.target.cycle.quarters if q.id == self.target.quarter_id), None) if self.target else None
        parent = next((q for c in self.cycles for q in c.quarters if self.target and q.id == self.target.cycle.parent_quarter_id), None)
        scope = (f"{parent.label + ' 90m' if parent else self.target.cycle.layer} Q{quarter.position}"
                 if quarter else "No active quarter")
        self.target_label.setText("Working AMDX · " + scope + (" · pinned" if self._pinned else ""))
        enabled = bool(self.repository and self.run and self.target and self.reference and not self._read_error
                       and self.mode_id in ("tda", "live-watch"))
        for button in (*self.phase_buttons.values(), self.more_button):
            button.setEnabled(enabled)
            button.setVisible(self.mode_id != "post-market")
        self.follow_button.setVisible(self._pinned and self.mode_id != "post-market")
        if not self.status_label.text():
            self.status_label.setText("Select a quarter to inspect; choose a phase to record. X subtype may remain unresolved."
                                      if self.repository else "AMDX recording requires the application database.")
