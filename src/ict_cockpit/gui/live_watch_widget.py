from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.tda_station_session import TDAStationSession
from ict_cockpit.analysis.trading_session_run import (
    RunEvidenceEntry,
    RunEvidenceKind,
    ThesisState,
    WatchPointState,
)
from ict_cockpit.process_blueprint import ProcessBlueprint
from ict_cockpit.trade_plan import LiveWatchPolicyDefinition


class LiveWatchWidget(QWidget):
    """Primary waiting-and-watching surface for an active Trading Run."""

    observation_submitted = Signal(str)
    thesis_state_submitted = Signal(str, str)
    entry_condition_changed = Signal(str, bool)
    watch_point_state_changed = Signal(str, str)

    def __init__(
        self,
        policy: LiveWatchPolicyDefinition | None = None,
    ) -> None:
        super().__init__()
        self.policy = policy or LiveWatchPolicyDefinition()
        self._loading_readiness = False
        self._loading_watch_points = False
        self.entry_checkboxes: dict[str, QCheckBox] = {}
        self.watch_point_combos: dict[str, QComboBox] = {}

        self.heading = QLabel("Live Watch · Waiting & Watching")
        self.heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.guidance = QLabel(
            "Stay oriented to the TDA, wait for planned conditions, and act only when the Trade Plan authorizes it."
        )
        self.guidance.setWordWrap(True)

        self.tda_frame = QFrame()
        self.tda_frame.setFrameShape(QFrame.Shape.StyledPanel)
        tda_layout = QVBoxLayout(self.tda_frame)
        tda_layout.setContentsMargins(9, 7, 9, 7)
        tda_layout.setSpacing(4)
        tda_heading = QLabel("TDA Carry-Forward")
        tda_heading.setStyleSheet("font-weight: 600;")
        self.tda_summary_label = QLabel("No TDA context loaded")
        self.tda_summary_label.setWordWrap(True)
        self.watch_points_list = QListWidget()
        self.watch_points_list.setMaximumHeight(100)
        tda_layout.addWidget(tda_heading)
        tda_layout.addWidget(self.tda_summary_label)
        tda_layout.addWidget(self.watch_points_list)

        structured_heading = QLabel("If / Then Watch Points")
        structured_heading.setStyleSheet("font-weight: 600;")
        tda_layout.addWidget(structured_heading)
        self.structured_watch_points_host = QWidget()
        self.structured_watch_points_layout = QVBoxLayout(
            self.structured_watch_points_host
        )
        self.structured_watch_points_layout.setContentsMargins(0, 0, 0, 0)
        self.structured_watch_points_layout.setSpacing(3)
        tda_layout.addWidget(self.structured_watch_points_host)

        self.readiness_frame = QFrame()
        self.readiness_frame.setFrameShape(QFrame.Shape.StyledPanel)
        readiness_layout = QVBoxLayout(self.readiness_frame)
        readiness_layout.setContentsMargins(9, 7, 9, 7)
        readiness_layout.setSpacing(4)
        readiness_heading = QLabel("Entry Readiness")
        readiness_heading.setStyleSheet("font-weight: 600;")
        self.readiness_count_label = QLabel()
        self.readiness_count_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.readiness_required_label = QLabel()
        self.readiness_status_label = QLabel()
        self.readiness_status_label.setWordWrap(True)
        self.criteria_host = QWidget()
        self.criteria_layout = QVBoxLayout(self.criteria_host)
        self.criteria_layout.setContentsMargins(0, 0, 0, 0)
        self.criteria_layout.setSpacing(2)
        readiness_layout.addWidget(readiness_heading)
        readiness_layout.addWidget(self.readiness_count_label)
        readiness_layout.addWidget(self.readiness_required_label)
        readiness_layout.addWidget(self.readiness_status_label)
        readiness_layout.addWidget(self.criteria_host)
        readiness_layout.addStretch()
        self._build_entry_criteria()

        self.risk_frame = QFrame()
        self.risk_frame.setFrameShape(QFrame.Shape.StyledPanel)
        risk_layout = QVBoxLayout(self.risk_frame)
        risk_layout.setContentsMargins(9, 7, 9, 7)
        risk_layout.setSpacing(4)
        risk_heading = QLabel("Risk Envelope")
        risk_heading.setStyleSheet("font-weight: 600;")
        self.risk_instrument_label = QLabel(
            "Instrument / account context: inherited when configured"
        )
        self.risk_stop_label = QLabel("Maximum permitted stop: Not configured")
        self.risk_status_label = QLabel()
        self.risk_status_label.setWordWrap(True)
        risk_layout.addWidget(risk_heading)
        risk_layout.addWidget(self.risk_instrument_label)
        risk_layout.addWidget(self.risk_stop_label)
        risk_layout.addWidget(self.risk_status_label)
        risk_layout.addStretch()
        self._render_risk_policy()

        self.thesis_frame = QFrame()
        self.thesis_frame.setFrameShape(QFrame.Shape.StyledPanel)
        thesis_layout = QVBoxLayout(self.thesis_frame)
        thesis_layout.setContentsMargins(9, 7, 9, 7)
        thesis_layout.setSpacing(4)
        thesis_top = QHBoxLayout()
        thesis_heading = QLabel("Thesis Crossroads")
        thesis_heading.setStyleSheet("font-weight: 600;")
        self.thesis_state_label = QLabel("Current thesis: Not Set")
        thesis_top.addWidget(thesis_heading)
        thesis_top.addStretch()
        thesis_top.addWidget(self.thesis_state_label)
        thesis_layout.addLayout(thesis_top)

        self.thesis_note_input = QLineEdit()
        self.thesis_note_input.setPlaceholderText(
            "Reason for a meaningful thesis change (optional)"
        )
        thesis_layout.addWidget(self.thesis_note_input)

        thesis_buttons = QHBoxLayout()
        self.thesis_buttons: dict[ThesisState, QPushButton] = {}
        for state in (
            ThesisState.SUPPORTED,
            ThesisState.WEAKENED,
            ThesisState.INVALIDATED,
            ThesisState.UNCERTAIN,
        ):
            button = QPushButton(state.value)
            button.clicked.connect(
                lambda _checked=False, selected=state: self._submit_thesis_state(
                    selected
                )
            )
            self.thesis_buttons[state] = button
            thesis_buttons.addWidget(button)
        thesis_buttons.addStretch()
        thesis_layout.addLayout(thesis_buttons)

        self.observation_input = QLineEdit()
        self.observation_input.setPlaceholderText(
            "Capture a material change or observation"
        )
        self.capture_observation_button = QPushButton("Capture")
        self.capture_observation_button.clicked.connect(self._submit_observation)
        self.observation_input.returnPressed.connect(self._submit_observation)
        observation_row = QHBoxLayout()
        observation_row.addWidget(self.observation_input, 1)
        observation_row.addWidget(self.capture_observation_button)

        self.evidence_list = QListWidget()
        self.evidence_list.hide()

        dashboard = QGridLayout()
        dashboard.setContentsMargins(0, 0, 0, 0)
        dashboard.setHorizontalSpacing(8)
        dashboard.setVerticalSpacing(8)
        dashboard.addWidget(self.tda_frame, 0, 0, 2, 1)
        dashboard.addWidget(self.readiness_frame, 0, 1)
        dashboard.addWidget(self.risk_frame, 1, 1)
        dashboard.setColumnStretch(0, 3)
        dashboard.setColumnStretch(1, 2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        layout.addWidget(self.heading)
        layout.addWidget(self.guidance)
        layout.addLayout(dashboard, 1)
        layout.addWidget(self.thesis_frame)
        layout.addLayout(observation_row)
        layout.addWidget(self.evidence_list)

    def _build_entry_criteria(self) -> None:
        if not self.policy.entry_criteria:
            self.readiness_count_label.setText("Entry criteria: Not configured")
            self.readiness_required_label.setText(
                "Required for entry: Not configured"
            )
            self.readiness_status_label.setText(
                "This Trade Plan revision does not yet define entry-readiness criteria. Live Watch will not invent them."
            )
            return

        for criterion in self.policy.entry_criteria:
            checkbox = QCheckBox(criterion.name)
            if criterion.description:
                checkbox.setToolTip(criterion.description)
            checkbox.toggled.connect(
                lambda checked, criterion_id=criterion.id: self._entry_condition_toggled(
                    criterion_id, checked
                )
            )
            self.entry_checkboxes[criterion.id] = checkbox
            self.criteria_layout.addWidget(checkbox)
        self._render_readiness({})

    def _render_risk_policy(self) -> None:
        if self.policy.risk_summary.strip():
            self.risk_status_label.setText(self.policy.risk_summary.strip())
        else:
            self.risk_status_label.setText(
                "Risk rules are not yet encoded in this Trade Plan revision. Lower layers remain read-only with respect to trading policy."
            )

    def clear_state(self) -> None:
        self.thesis_note_input.clear()
        self.observation_input.clear()
        self.watch_points_list.clear()
        self.tda_summary_label.setText("No TDA context loaded")
        self._render_structured_watch_points(None, {})
        self.load_state(ThesisState.NOT_SET, [], {}, {})

    def load_operating_context(
        self,
        thesis_state: ThesisState | str,
        evidence: list[RunEvidenceEntry],
        entry_condition_states: dict[str, bool],
        watch_point_states: dict[str, WatchPointState],
        tda_session: TDAStationSession | None,
        blueprint: ProcessBlueprint,
    ) -> None:
        self.load_state(
            thesis_state,
            evidence,
            entry_condition_states,
            watch_point_states,
        )
        self._load_tda_context(tda_session, blueprint, watch_point_states)

    def load_state(
        self,
        thesis_state: ThesisState | str,
        evidence: list[RunEvidenceEntry],
        entry_condition_states: dict[str, bool] | None = None,
        watch_point_states: dict[str, WatchPointState] | None = None,
    ) -> None:
        thesis_state = ThesisState(thesis_state)
        self.thesis_state_label.setText(f"Current thesis: {thesis_state.value}")
        self.evidence_list.clear()
        for item in reversed(evidence[-12:]):
            time_text = (
                item.created_at[11:19]
                if len(item.created_at) >= 19
                else item.created_at
            )
            if item.kind is RunEvidenceKind.THESIS_STATE:
                detail = item.thesis_state.value
                if item.note:
                    detail += f" — {item.note}"
                text = f"{time_text} · Thesis: {detail}"
            else:
                text = f"{time_text} · {item.note}"
            self.evidence_list.addItem(text)
        self._render_readiness(entry_condition_states or {})
        self._apply_watch_point_states(watch_point_states or {})

    def _render_readiness(self, states: dict[str, bool]) -> None:
        if not self.policy.entry_criteria:
            return

        valid_ids = {criterion.id for criterion in self.policy.entry_criteria}
        satisfied = sum(
            1 for criterion_id in valid_ids if states.get(criterion_id, False)
        )
        total = len(self.policy.entry_criteria)
        required = self.policy.required_entry_count

        self._loading_readiness = True
        for criterion_id, checkbox in self.entry_checkboxes.items():
            checkbox.setChecked(states.get(criterion_id, False))
        self._loading_readiness = False

        self.readiness_count_label.setText(
            f"{satisfied} / {total} criteria currently met"
        )
        self.readiness_required_label.setText(
            f"Required for entry: {required} / {total}"
        )
        if required is not None and satisfied >= required:
            self.readiness_status_label.setText(
                "Readiness threshold satisfied by the active Trade Plan."
            )
        else:
            remaining = (required or 0) - satisfied
            self.readiness_status_label.setText(
                f"Waiting · {max(remaining, 0)} additional criterion/criteria required."
            )

    def _entry_condition_toggled(self, criterion_id: str, checked: bool) -> None:
        if self._loading_readiness:
            return
        self.entry_condition_changed.emit(criterion_id, checked)

    def _clear_layout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout(child_layout)
                child_layout.deleteLater()
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _render_structured_watch_points(
        self,
        tda_session: TDAStationSession | None,
        states: dict[str, WatchPointState],
    ) -> None:
        self._clear_layout(self.structured_watch_points_layout)
        self.watch_point_combos = {}

        if tda_session is None or not tda_session.watch_points:
            empty = QLabel("No structured If / Then watch points were filed in TDA.")
            empty.setWordWrap(True)
            self.structured_watch_points_layout.addWidget(empty)
            return

        self._loading_watch_points = True
        for watch_point in tda_session.watch_points:
            row = QHBoxLayout()
            label = QLabel(
                f"IF {watch_point.if_condition}  →  THEN {watch_point.then_action}"
            )
            label.setWordWrap(True)
            combo = QComboBox()
            combo.addItems([state.value for state in WatchPointState])
            current_state = states.get(
                watch_point.id,
                WatchPointState.WAITING,
            )
            if not isinstance(current_state, WatchPointState):
                current_state = WatchPointState(current_state)
            combo.setCurrentText(current_state.value)
            combo.currentTextChanged.connect(
                lambda state_text, watch_point_id=watch_point.id: self._watch_point_state_changed(
                    watch_point_id, state_text
                )
            )
            self.watch_point_combos[watch_point.id] = combo
            row.addWidget(label, 1)
            row.addWidget(combo)
            self.structured_watch_points_layout.addLayout(row)
        self._loading_watch_points = False

    def _apply_watch_point_states(
        self,
        states: dict[str, WatchPointState],
    ) -> None:
        if not self.watch_point_combos:
            return
        self._loading_watch_points = True
        for watch_point_id, combo in self.watch_point_combos.items():
            state = states.get(watch_point_id, WatchPointState.WAITING)
            if not isinstance(state, WatchPointState):
                state = WatchPointState(state)
            combo.setCurrentText(state.value)
        self._loading_watch_points = False

    def _watch_point_state_changed(
        self,
        watch_point_id: str,
        state_text: str,
    ) -> None:
        if self._loading_watch_points:
            return
        self.watch_point_state_changed.emit(
            watch_point_id,
            WatchPointState(state_text).value,
        )

    def _load_tda_context(
        self,
        tda_session: TDAStationSession | None,
        blueprint: ProcessBlueprint,
        watch_point_states: dict[str, WatchPointState],
    ) -> None:
        self.watch_points_list.clear()
        self._render_structured_watch_points(tda_session, watch_point_states)
        if tda_session is None:
            self.tda_summary_label.setText("No saved TDA context available")
            return

        station_names: dict[str, str] = {}
        for mode in blueprint.modes:
            if mode.id != "tda":
                continue
            for deck in mode.decks:
                for station in deck.stations:
                    station_names[station.id] = station.name

        priority_ids = (
            "tda-primary-draw",
            "tda-secondary-draw",
            "tda-thesis",
        )
        populated = []
        for station_id in priority_ids:
            if station_id not in tda_session.station_ids:
                continue
            observation = tda_session.observation_for(
                station_id
            ).observation.strip()
            if observation:
                populated.append((station_id, observation))

        if not populated:
            populated = [
                (item.station_id, item.observation.strip())
                for item in tda_session.observations
                if item.observation.strip()
            ][-4:]

        self.tda_summary_label.setText(
            f"{tda_session.completed_count()}/{len(tda_session.station_ids)} TDA stations complete · key context carried forward"
        )
        if not populated:
            self.watch_points_list.addItem("○ No TDA synthesis observations recorded")
            return

        for station_id, observation in populated:
            name = station_names.get(station_id, station_id)
            compact = observation.replace("\n", " ")
            if len(compact) > 180:
                compact = compact[:177] + "..."
            self.watch_points_list.addItem(f"○ {name} · {compact}")

    def _submit_observation(self) -> None:
        note = self.observation_input.text().strip()
        if not note:
            return
        self.observation_submitted.emit(note)
        self.observation_input.clear()

    def _submit_thesis_state(self, state: ThesisState) -> None:
        note = self.thesis_note_input.text().strip()
        self.thesis_state_submitted.emit(state.value, note)
        self.thesis_note_input.clear()
