"""Shared working/observed AMDX entry; navigation never records a phase."""
from dataclasses import dataclass
from datetime import date, datetime, time
import sqlite3
from uuid import uuid4

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFrame, QHeaderView, QHBoxLayout, QLabel, QMenu,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from ict_cockpit.analysis.amdx import (
    Anchor, Cycle, InterpretationHistory, Role, XSubtype, available_roles, infer_profile, intraday_cycles, timestamp,
)
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, futures_trading_day_for
from ict_cockpit.analysis.amdx_review import StaleComparison
from ict_cockpit.analysis.amdx_review_date import resolve_review_date
from ict_cockpit.analysis.quarter_theory import QT_LEVELS, normalize_qt_context
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate


@dataclass(frozen=True)
class EditTarget:
    run_id: str
    cycle: Cycle
    quarter_id: str
    expected_head_id: str | None
    channel: str = "Expected"
    comparison_head_id: str | None = None


@dataclass(frozen=True)
class AMDXDecisionProjection:
    """Read-only active-target projection for contextual command surfaces."""

    token: tuple
    available: bool
    unavailable_reason: str
    target_label: str
    quarter_position: int | None
    legal_roles: tuple[Role, ...]
    legal_x_subtypes: tuple[XSubtype, ...]
    current_role: Role | None
    current_subtype: XSubtype | None
    current_origin: str
    profile: str


def role_text(role, subtype=None):
    return f"X({subtype.value if subtype else '?'})" if role is Role.X else role.value


class AMDXContextWidget(QFrame):
    recorded = Signal(object)
    decision_projection_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.repository = None
        self.run = None
        self.mode_id = ""
        self.reference = None
        self.cycles = ()
        self.history = InterpretationHistory()
        self.comparisons = ()
        self.review_day_label = ""
        self._container_day_label = ""
        self._review_date_error = ""
        self._review_date_detail = ""
        self.review_sessions = ()
        self.target = None
        self._pinned = False
        self._read_error = False
        self._gesture_target = None
        self._gesture_reference = None
        self._gesture_clear_applicability = None
        self._gesture_generation = 0
        self._table_rendering = False
        self._last_decision_projection = None

        self.target_label = QLabel("AMDX · No active quarter")
        self.target_label.setWordWrap(True)
        self.target_label.setStyleSheet("font-weight: 600;")
        bar = QHBoxLayout()
        bar.setContentsMargins(0, 0, 0, 0)
        bar.setSpacing(3)
        bar.addWidget(self.target_label, 1)
        self.session_selector = QComboBox()
        self.session_selector.addItems(["Asia", "London", "NYAM", "NYPM"])
        self.session_selector.setToolTip("Inspect this session in the reviewed trading day; selecting it records nothing.")
        self.session_selector.currentIndexChanged.connect(self._select_review_session)
        bar.addWidget(self.session_selector)
        self.phase_buttons = {}
        for role in (Role.A, Role.M, Role.D, Role.X):
            button = QPushButton("X(?)" if role is Role.X else role.value)
            button.setMaximumWidth(48)
            button.setToolTip("Revise this working quartet immediately; sibling roles are implied. Earlier claims remain in history.")
            button.pressed.connect(self._begin_gesture)
            button.released.connect(self._schedule_end_gesture)
            button.clicked.connect(lambda _checked=False, r=role: self.choose(r))
            self.phase_buttons[role] = button
            bar.addWidget(button)
        self.subtype_buttons = {}
        for subtype in XSubtype:
            button = QPushButton(f"X({subtype.value})")
            button.setMaximumWidth(48)
            button.pressed.connect(self._begin_gesture)
            button.released.connect(self._schedule_end_gesture)
            button.clicked.connect(lambda _checked=False, s=subtype: self.choose(Role.X, s))
            self.subtype_buttons[subtype] = button
            bar.addWidget(button)
        self.more_button = QPushButton("…")
        self.more_button.setMaximumWidth(32)
        self.more_button.setToolTip("X subtype, uncertainty or clear this anchor")
        self.menu = QMenu(self)
        self.menu.aboutToShow.connect(self._begin_gesture)
        self.menu.aboutToHide.connect(self._schedule_end_gesture)
        self.menu_actions = {}
        for label, role, subtype in (
            ("X(C) · Continuation", Role.X, XSubtype.CONTINUATION),
            ("X(R) · Reversal", Role.X, XSubtype.REVERSAL),
            ("Unknown", Role.UNKNOWN, None),
            ("Not Applicable", Role.NOT_APPLICABLE, None),
            ("Clear this anchor", None, None),
        ):
            action = self.menu.addAction(label)
            if role is None:
                action.triggered.connect(self._clear_selected)
            else:
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

    @property
    def channel(self):
        return "Observed" if self.mode_id == "post-market" else "Expected"

    def load_context(self, run, market_context, mode_id, *, review_day_label=None):
        changed_run = (self.run.id if self.run else None) != (run.id if run else None)
        changed_channel = (mode_id == "post-market") != (self.mode_id == "post-market")
        self.run, self.mode_id = run, mode_id
        if review_day_label is not None:
            self._container_day_label = review_day_label
        prior_date_error = self._review_date_error
        prior_date = self.review_day_label
        resolved = resolve_review_date(run, self._container_day_label)
        self.review_day_label = resolved.day_label
        self._review_date_error, self._review_date_detail = resolved.error, resolved.detail
        changed_date = prior_date != self.review_day_label
        if prior_date_error and not self._review_date_error:
            self.status_label.setText("")
        if changed_run:
            self.target, self._pinned = None, False
            # An in-flight gesture retains its old run so release cannot write
            # into a newly loaded run. choose() rejects that ownership change.
            self.status_label.setText("")
            self.history = InterpretationHistory()
            self.comparisons = ()
        if changed_channel or (self.channel == "Observed" and changed_date):
            self.target, self._pinned = None, False
            self.status_label.setText("")
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
                if self.channel == "Observed":
                    review = self.repository.review.get_history(run.id)
                    self.history, self.comparisons = review.interpretations, review.comparisons
                else:
                    self.history = self.repository.get_history(run.id)
                if prior_read_error:
                    self.status_label.setText("")
            except (ValueError, TypeError, KeyError, sqlite3.Error, RuntimeError) as error:
                self._read_error = True
                self.status_label.setText(f"History unavailable · {error}")
        else:
            self.history = InterpretationHistory()
        if self.channel == "Observed":
            self._load_review_cycles(changed_run or changed_channel or changed_date)
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
                     c.cycle.id == cycle.id and c.branch_id == "working" and c.channel == self.channel), None)

    def _edit_target(self, cycle, quarter_id):
        head = self._head(cycle)
        pair = next((p for p in reversed(self.comparisons) if p.run_id == self.run.id
                     and p.branch_id == "working" and p.cycle_id == cycle.id), None)
        return EditTarget(self.run.id, cycle, quarter_id, head.id if head else None,
                          self.channel, pair.id if pair and self.channel == "Observed" else None)

    def _load_review_cycles(self, initialize):
        # The run's saved starting reference wins over a mislabeled container.
        self.review_sessions = ()
        self.cycles = ()
        if self.run is None:
            self.target = None
            return
        if self._review_date_error:
            self.target = None
            self.status_label.setText(f"Review date unavailable · {self._review_date_error} · recording disabled")
            return
        try:
            reviewed_date = date.fromisoformat(self.review_day_label)
            day, _ = intraday_cycles(datetime.combine(reviewed_date, time(9), MARKET_TIMEZONE))
            self.review_sessions = tuple(intraday_cycles(q.start)[1] for q in day.quarters)
        except (ValueError, TypeError, IndexError):
            self.target = None
            self.status_label.setText("Reviewed trading day unavailable · recording disabled")
            return
        index = self.session_selector.currentIndex()
        if initialize:
            parent = day.quarter_at(self.reference) if self.reference else None
            index = parent.position - 1 if parent else 0
            self.session_selector.blockSignals(True)
            self.session_selector.setCurrentIndex(index)
            self.session_selector.blockSignals(False)
        self.cycles = (day, self.review_sessions[index])
        if initialize or self.target is None:
            cycle = self.cycles[-1]
            quarter = cycle.quarter_at(self.reference) if self.reference else None
            self.target = self._edit_target(cycle, (quarter or cycle.quarters[0]).id)
            self._pinned = True

    def _select_review_session(self, index):
        if self.channel != "Observed" or not self.review_sessions or self._gesture_target:
            return
        cycle = self.review_sessions[index]
        self.cycles = (self.cycles[0], cycle)
        self.target, self._pinned = self._edit_target(cycle, cycle.quarters[0].id), True
        self._render()

    def _set_current_target(self):
        if not self.cycles or self.reference is None or self.run is None:
            self.target = None
            return
        cycle = self.cycles[-1]
        quarter = cycle.quarter_at(self.reference)
        if quarter is None:
            self.target = None
            return
        self.target = self._edit_target(cycle, quarter.id)

    def select_quarter(self, row, column):
        if not 0 <= row < len(self.cycles) or not 0 <= column < 4 or not self.run:
            return
        cycle = self.cycles[row]
        self.target = self._edit_target(cycle, cycle.quarters[column].id)
        if self.channel == "Observed" and row == 0 and self.review_sessions:
            self.session_selector.blockSignals(True)
            self.session_selector.setCurrentIndex(column)
            self.session_selector.blockSignals(False)
            self.cycles = (cycle, self.review_sessions[column])
        self._pinned = True
        self._render()

    def _selection_changed(self, row, column, _old_row, _old_column):
        if not self._table_rendering:
            self.select_quarter(row, column)

    def follow_current(self):
        if self.channel == "Observed":
            return
        self._pinned = False
        self.target = None
        self._gesture_target = self._gesture_reference = None
        self._gesture_clear_applicability = None
        self._reload_context()

    def _reload_context(self):
        self.load_context(self.run, {"captured_at": self.reference.isoformat()} if self.reference else {}, self.mode_id)

    def _begin_gesture(self):
        self._gesture_generation += 1
        self._gesture_target, self._gesture_reference = self.target, self.reference
        self._gesture_clear_applicability = self._has_applicability()
        self.session_selector.setEnabled(False)

    def _has_applicability(self):
        head = self._head(self.target.cycle) if self.target else None
        return bool(head and (head.applicability or any(a.role is Role.NOT_APPLICABLE for a in head.anchors)))

    def _clear_selected(self, _checked=False):
        clear = self._gesture_clear_applicability if self._gesture_clear_applicability is not None else self._has_applicability()
        self.choose(None, clear_applicability=clear)

    def _schedule_end_gesture(self):
        generation = self._gesture_generation
        QTimer.singleShot(0, lambda: self._end_gesture(generation))

    def _end_gesture(self, generation):
        if generation != self._gesture_generation:
            return
        if self._gesture_target is None:
            return
        self._gesture_target = self._gesture_reference = None
        self._gesture_clear_applicability = None
        if not self._pinned:
            self._reload_context()
        else:
            self._render()

    def choose(self, role, subtype=None, *, clear_applicability=False):
        target = self._gesture_target or self.target
        reference = self._gesture_reference or self.reference
        self._gesture_target = self._gesture_reference = None
        self._gesture_clear_applicability = None
        if (not target or not reference or not self.repository or self._read_error or not self.run
                or target.run_id != self.run.id or target.channel != self.channel
                or (self.channel == "Observed" and (self._review_date_error
                    or futures_trading_day_for(target.cycle.quarters[0].start).isoformat() != self.review_day_label))
                or self.mode_id not in ("tda", "live-watch", "post-market")):
            self._reload_context()
            return False
        anchor = Anchor(str(uuid4()), target.quarter_id, role,
                        "Technician / observed AMDX" if self.channel == "Observed" else "Technician / working AMDX", subtype) if role else None
        try:
            arguments = dict(
                claim_id=str(uuid4()), run_id=target.run_id, branch_id="working",
                cycle=target.cycle, quarter_id=target.quarter_id, anchor=anchor,
                recorded_at=datetime.now().astimezone(), market_reference=reference,
                clear_applicability=clear_applicability,
            )
            if self.channel == "Observed":
                result = self.repository.review.revise_observed(
                    **arguments, comparison_id=str(uuid4()),
                    expected_observed_head_id=target.expected_head_id,
                    expected_comparison_head_id=target.comparison_head_id,
                )
            else:
                result = self.repository.revise_working(
                    **arguments, channel="Expected", expected_head_id=target.expected_head_id,
                )
        except (ValueError, TypeError, KeyError, sqlite3.Error, RuntimeError) as error:
            self.status_label.setText(f"Not recorded · {error}")
            # Keep a failed choice's scope visible for a deliberate retry or release.
            self.target, self._pinned = target, True
            if isinstance(error, (StaleAMDXUpdate, StaleComparison)):
                # Refresh the inspected head, but require another deliberate choice.
                # The gesture's earlier reference belongs to the attempted claim,
                # not to the clock that continues advancing behind the pin.
                self._reload_context()
                self.target = self._edit_target(target.cycle, target.quarter_id)
            self._render()
            return False
        claim = result.claim
        if result.changed and all(c.id != claim.id for c in self.history.claims):
            self.history = InterpretationHistory(self.history.claims + (claim,))
        if self.channel == "Observed" and result.changed:
            self.comparisons += (result.comparison,)
        self.target = self._edit_target(target.cycle, target.quarter_id)
        self.status_label.setText(("Recorded · " if result.changed else "Already current · ")
                                  + (claim.inference.state if claim else "Unassigned") + " · entered anchors / implied siblings")
        self._reload_context()
        if result.changed:
            self.recorded.emit(claim)
        return True

    def decision_projection(self) -> AMDXDecisionProjection:
        target = self.target
        quarter = next(
            (item for item in target.cycle.quarters if item.id == target.quarter_id),
            None,
        ) if target else None
        head = self._head(target.cycle) if target else None
        inference = head.inference if head else (
            infer_profile(target.cycle, ()) if target else None
        )
        explicit = next(
            (item for item in (head.anchors if head else ()) if item.quarter_id == target.quarter_id),
            None,
        ) if target else None
        derived = next(
            (item for item in inference.roles if item.quarter_id == target.quarter_id),
            None,
        ) if target and inference else None
        current = explicit or derived
        legal_roles = available_roles(quarter.position) if quarter else ()
        profile = "Unavailable"
        if inference is not None:
            profile = (
                "/".join(item.value for item in inference.candidates)
                if inference.state == "Resolved"
                else inference.state
            )
        available = bool(
            self.repository
            and self.run
            and target
            and quarter
            and self.reference
            and not self._read_error
            and getattr(self, "_surface_active", True)
            and (self.channel != "Observed" or not self._review_date_error)
            and self.mode_id in ("tda", "live-watch", "post-market")
        )
        if available:
            reason = ""
        elif self._read_error:
            reason = self.status_label.text() or "AMDX context is unavailable"
        elif self.mode_id not in ("tda", "live-watch", "post-market"):
            reason = "No active operating mode"
        elif not target or not quarter:
            reason = "No active AMDX quarter"
        else:
            reason = "AMDX recording is unavailable"
        decision_reference = getattr(self, "_shared_target_reference", None) or self.reference
        reference = decision_reference.isoformat() if decision_reference else ""
        token = (
            target.run_id if target else "",
            target.channel if target else "",
            target.cycle.id if target else "",
            target.quarter_id if target else "",
            target.expected_head_id if target else None,
            reference,
            self.mode_id,
            available,
        )
        return AMDXDecisionProjection(
            token=token,
            available=available,
            unavailable_reason=reason,
            target_label=self.target_label.text(),
            quarter_position=quarter.position if quarter else None,
            legal_roles=tuple(legal_roles),
            legal_x_subtypes=tuple(XSubtype) if Role.X in legal_roles else (),
            current_role=current.role if current else None,
            current_subtype=current.subtype if current else None,
            current_origin=("entered" if explicit else derived.origin.lower() if derived else "unresolved"),
            profile=profile,
        )

    def choose_decision(self, token, role, subtype=None) -> bool:
        """Invoke the existing command only for the exact displayed projection."""

        projection = self.decision_projection()
        if token != projection.token:
            self.status_label.setText("Not recorded · AMDX target changed; review the current target and choose again")
            self._render()
            return False
        if not projection.available or role not in projection.legal_roles:
            self.status_label.setText("Not recorded · that role is unavailable for the current AMDX target")
            self._render()
            return False
        if subtype is not None and (role is not Role.X or subtype not in projection.legal_x_subtypes):
            self.status_label.setText("Not recorded · that X subtype is unavailable for the current AMDX target")
            self._render()
            return False
        # A token-validated decision is a new gesture. In particular, returning
        # from another workspace must not inherit an earlier gesture's cancel
        # flag. Start only after validation so stale/inactive decisions stay inert.
        self._begin_gesture()
        generation = self._gesture_generation
        try:
            return bool(self.choose(role, subtype))
        finally:
            self._end_gesture(generation)

    def _publish_decision_projection(self):
        projection = self.decision_projection()
        if projection != self._last_decision_projection:
            self._last_decision_projection = projection
            self.decision_projection_changed.emit(projection)

    def _render_table(self):
        self.table.setRowCount(len(self.cycles))
        self.table.setVerticalHeaderLabels(["Day" if c.layer == "day" else "90m" for c in self.cycles])
        for row, cycle in enumerate(self.cycles):
            head = self._head(cycle)
            inference = head.inference if head else infer_profile(cycle, ())
            for col, quarter in enumerate(cycle.quarters):
                derived = next((r for r in inference.roles if r.quarter_id == quarter.id), None)
                explicit = next((a for a in (head.anchors if head else ()) if a.quarter_id == quarter.id), None)
                if explicit is None and head:
                    explicit = next((a for a in head.applicability if a.quarter_id == quarter.id), None)
                phase = role_text(explicit.role, explicit.subtype) if explicit else role_text(derived.role, derived.subtype) if derived else "?"
                origin = "entered" if explicit else "implied" if derived and derived.origin == "Implied" else "unresolved"
                if explicit and explicit.role is Role.UNKNOWN and derived and derived.role is not Role.UNKNOWN:
                    phase, origin = "Unknown / " + role_text(derived.role, derived.subtype), "entered / implied"
                label = quarter.label if cycle.layer == "day" else quarter.start.astimezone(MARKET_TIMEZONE).strftime("%H:%M")
                item = QTableWidgetItem(f"{label} · {phase}\n{origin}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setToolTip(f"{quarter.id}\n{quarter.start.isoformat()} → {quarter.end.isoformat()}\n"
                                f"{inference.structural_revision}; {origin}\n"
                                + ("Technician judgment: Unknown. Conditional structural role: " + role_text(derived.role, derived.subtype) + ".\n"
                                   if explicit and explicit.role is Role.UNKNOWN and derived and derived.role is not Role.UNKNOWN else "")
                                + "\n".join(inference.reasons))
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
        self.target_label.setText((f"Observed AMDX · {self.review_day_label} · " if self.channel == "Observed" else "Working AMDX · ")
                                  + scope + (" · pinned" if self._pinned and self.channel != "Observed" else ""))
        self.target_label.setToolTip(self._review_date_detail if self.channel == "Observed" else "")
        enabled = bool(self.repository and self.run and self.target and self.reference and not self._read_error
                       and (self.channel != "Observed" or not self._review_date_error)
                       and self.mode_id in ("tda", "live-watch", "post-market"))
        self.session_selector.setVisible(self.channel == "Observed")
        self.session_selector.setEnabled(bool(self.review_sessions) and not self._gesture_target)
        roles = available_roles(quarter.position) if quarter else ()
        for role, button in self.phase_buttons.items():
            button.setEnabled(enabled and role in roles)
            button.setToolTip((f"Q{quarter.position} permits " + "/".join(r.value for r in roles) + " under AMDX/XAMD. "
                               if quarter else "") + f"Revise the {self.channel.lower()} quartet immediately; earlier claims remain in history.")
        for subtype, button in self.subtype_buttons.items():
            button.setEnabled(enabled and Role.X in roles)
            button.setToolTip(f"Record X({subtype.value}) for the selected quarter immediately.")
        self.more_button.setEnabled(enabled)
        for key, action in self.menu_actions.items():
            action.setEnabled(enabled and (not key.startswith("X(") or Role.X in roles))
        self.menu_actions["Not Applicable"].setText("Not Applicable · whole quartet")
        applicability = self._gesture_clear_applicability if self._gesture_clear_applicability is not None else self._has_applicability()
        self.menu_actions["Clear this anchor"].setText("Clear Not Applicable" if applicability else "Clear this anchor")
        self.follow_button.setVisible(self._pinned and self.mode_id != "post-market")
        if not self.status_label.text():
            self.status_label.setText("Select a quarter to inspect; choose a phase to record. X subtype may remain unresolved."
                                      if self.repository else "AMDX recording requires the application database.")
        self._publish_decision_projection()
