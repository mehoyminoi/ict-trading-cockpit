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

from ict_cockpit.analysis.market_time import temporal_relevance_for
from ict_cockpit.analysis.quarter_theory import (
    qt_context_summary,
    raw_quarter_alignment,
    raw_quarter_stack_detail,
    raw_quarter_stack_summary,
)
from ict_cockpit.analysis.tda_station_session import TDAStationSession
from ict_cockpit.analysis.trading_session_run import (
    AuthorizationGateState,
    AuthorizationStatus,
    RunEvidenceEntry,
    RunEvidenceKind,
    SetupCandidate,
    ThesisState,
    TradingRun,
    WatchPointState,
)
from ict_cockpit.process_blueprint import ProcessBlueprint
from ict_cockpit.trade_plan import LiveWatchPolicyDefinition, PlaybookDefinition


class LiveWatchWidget(QWidget):
    """Primary waiting-and-watching surface for an active Trading Run."""

    observation_submitted = Signal(str)
    thesis_state_submitted = Signal(str, str)
    entry_condition_changed = Signal(str, bool)
    watch_point_state_changed = Signal(str, str)
    candidate_entry_condition_changed = Signal(str, str, bool)
    candidate_watch_point_state_changed = Signal(str, str, str)
    authorization_gate_state_changed = Signal(str, str)
    candidate_authorization_gate_state_changed = Signal(str, str, str)

    def __init__(self, policy: LiveWatchPolicyDefinition | None = None) -> None:
        super().__init__()
        self.base_policy = policy or LiveWatchPolicyDefinition()
        self._loading = False
        self.entry_checkboxes: dict[str, QCheckBox] = {}
        self.watch_point_combos: dict[str, QComboBox] = {}
        self.candidate_entry_checkboxes: dict[tuple[str, str], QCheckBox] = {}
        self.candidate_watch_point_combos: dict[tuple[str, str], QComboBox] = {}
        self.run_gate_combos: dict[str, QComboBox] = {}
        self.candidate_gate_combos: dict[tuple[str, str], QComboBox] = {}
        self.candidate_temporal_relevance: dict[str, dict] = {}

        self.heading = QLabel("Live Watch · Waiting & Watching")
        self.heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.guidance = QLabel(
            "Watch the market thesis and setups becoming valid. Authorization requires both setup-specific conditions and Trade Plan safety/risk gates."
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
        self.qt_summary_label = QLabel("QT / AMDX · No interpretation recorded")
        self.qt_summary_label.setWordWrap(True)
        self.qt_summary_label.setStyleSheet("font-weight: 600;")
        self.raw_qt_stack_label = QLabel("Raw QT stack · Not available")
        self.raw_qt_stack_label.setWordWrap(True)
        self.watch_points_list = QListWidget()
        self.watch_points_list.setMaximumHeight(145)
        tda_layout.addWidget(tda_heading)
        tda_layout.addWidget(self.tda_summary_label)
        tda_layout.addWidget(self.qt_summary_label)
        tda_layout.addWidget(self.raw_qt_stack_label)
        tda_layout.addWidget(self.watch_points_list)

        self.authorization_frame = QFrame()
        self.authorization_frame.setFrameShape(QFrame.Shape.StyledPanel)
        authorization_layout = QVBoxLayout(self.authorization_frame)
        authorization_layout.setContentsMargins(9, 7, 9, 7)
        authorization_layout.setSpacing(4)
        authorization_heading = QLabel("Trade Plan Authorization Gates")
        authorization_heading.setStyleSheet("font-weight: 600;")
        self.authorization_summary_label = QLabel("Authorization policy: Not configured")
        self.authorization_summary_label.setWordWrap(True)
        self.authorization_host = QWidget()
        self.authorization_layout = QVBoxLayout(self.authorization_host)
        self.authorization_layout.setContentsMargins(0, 0, 0, 0)
        self.authorization_layout.setSpacing(3)
        authorization_layout.addWidget(authorization_heading)
        authorization_layout.addWidget(self.authorization_summary_label)
        authorization_layout.addWidget(self.authorization_host)

        self.readiness_frame = QFrame()
        self.readiness_frame.setFrameShape(QFrame.Shape.StyledPanel)
        readiness_layout = QVBoxLayout(self.readiness_frame)
        readiness_layout.setContentsMargins(9, 7, 9, 7)
        readiness_layout.setSpacing(5)
        self.readiness_heading = QLabel("Setups in Play")
        self.readiness_heading.setStyleSheet("font-weight: 600;")
        self.readiness_count_label = QLabel("Entry criteria: Not configured")
        self.readiness_count_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.readiness_required_label = QLabel("Required for entry: Not configured")
        self.readiness_status_label = QLabel("No setup candidate currently defines an authorization threshold.")
        self.readiness_status_label.setWordWrap(True)
        self.criteria_host = QWidget()
        self.criteria_layout = QVBoxLayout(self.criteria_host)
        self.criteria_layout.setContentsMargins(0, 0, 0, 0)
        self.criteria_layout.setSpacing(6)
        readiness_layout.addWidget(self.readiness_heading)
        readiness_layout.addWidget(self.readiness_count_label)
        readiness_layout.addWidget(self.readiness_required_label)
        readiness_layout.addWidget(self.readiness_status_label)
        readiness_layout.addWidget(self.criteria_host)
        readiness_layout.addStretch()

        self.risk_frame = QFrame()
        self.risk_frame.setFrameShape(QFrame.Shape.StyledPanel)
        risk_layout = QVBoxLayout(self.risk_frame)
        risk_layout.setContentsMargins(9, 7, 9, 7)
        risk_heading = QLabel("Risk Envelope")
        risk_heading.setStyleSheet("font-weight: 600;")
        self.risk_instrument_label = QLabel("Instrument / account context: inherited when configured")
        self.risk_stop_label = QLabel("Model stop rule: see setup candidate")
        self.risk_status_label = QLabel()
        self.risk_status_label.setWordWrap(True)
        risk_layout.addWidget(risk_heading)
        risk_layout.addWidget(self.risk_instrument_label)
        risk_layout.addWidget(self.risk_stop_label)
        risk_layout.addWidget(self.risk_status_label)
        risk_layout.addStretch()

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
        self.thesis_note_input.setPlaceholderText("Reason for a meaningful thesis change (optional)")
        thesis_layout.addWidget(self.thesis_note_input)
        thesis_buttons = QHBoxLayout()
        self.thesis_buttons: dict[ThesisState, QPushButton] = {}
        for state in (ThesisState.SUPPORTED, ThesisState.WEAKENED, ThesisState.INVALIDATED, ThesisState.UNCERTAIN):
            button = QPushButton(state.value)
            button.clicked.connect(lambda _checked=False, selected=state: self._submit_thesis_state(selected))
            self.thesis_buttons[state] = button
            thesis_buttons.addWidget(button)
        thesis_buttons.addStretch()
        thesis_layout.addLayout(thesis_buttons)

        self.observation_input = QLineEdit()
        self.observation_input.setPlaceholderText("Capture a material change or observation")
        self.capture_observation_button = QPushButton("Capture")
        self.capture_observation_button.clicked.connect(self._submit_observation)
        self.observation_input.returnPressed.connect(self._submit_observation)
        observation_row = QHBoxLayout()
        observation_row.addWidget(self.observation_input, 1)
        observation_row.addWidget(self.capture_observation_button)

        self.evidence_list = QListWidget()
        self.evidence_list.hide()
        self.structured_watch_points_host = QWidget()
        self.structured_watch_points_layout = QVBoxLayout(self.structured_watch_points_host)
        self.structured_watch_points_host.hide()

        dashboard = QGridLayout()
        dashboard.setContentsMargins(0, 0, 0, 0)
        dashboard.setHorizontalSpacing(8)
        dashboard.setVerticalSpacing(8)
        dashboard.addWidget(self.tda_frame, 0, 0, 2, 1)
        dashboard.addWidget(self.authorization_frame, 0, 1)
        dashboard.addWidget(self.risk_frame, 1, 1)
        dashboard.setColumnStretch(0, 3)
        dashboard.setColumnStretch(1, 2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        layout.addWidget(self.heading)
        layout.addWidget(self.guidance)
        layout.addLayout(dashboard)
        layout.addWidget(self.readiness_frame, 1)
        layout.addWidget(self.thesis_frame)
        layout.addLayout(observation_row)
        layout.addWidget(self.evidence_list)

        self._render_base_policy({}, {})

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

    def clear_state(self) -> None:
        self.thesis_note_input.clear()
        self.observation_input.clear()
        self.watch_points_list.clear()
        self.tda_summary_label.setText("No TDA context loaded")
        self.qt_summary_label.setText("QT / AMDX · No interpretation recorded")
        self.raw_qt_stack_label.setText("Raw QT stack · Not available")
        self._clear_layout(self.authorization_layout)
        self.authorization_summary_label.setText("Authorization policy: Not configured")
        self.load_state(ThesisState.NOT_SET, [], {}, {})
        self._render_base_policy({}, {})

    def load_state(self, thesis_state, evidence, entry_condition_states=None, watch_point_states=None) -> None:
        thesis_state = ThesisState(thesis_state)
        self.thesis_state_label.setText(f"Current thesis: {thesis_state.value}")
        self.evidence_list.clear()
        for item in reversed(evidence[-12:]):
            time_text = item.created_at[11:19] if len(item.created_at) >= 19 else item.created_at
            if item.kind is RunEvidenceKind.THESIS_STATE:
                detail = item.thesis_state.value + (f" — {item.note}" if item.note else "")
                text = f"{time_text} · Thesis: {detail}"
            else:
                text = f"{time_text} · {item.note}"
            self.evidence_list.addItem(text)
        if not self.candidate_entry_checkboxes:
            self._render_base_policy(entry_condition_states or {}, watch_point_states or {})

    def load_operating_context(self, thesis_state, evidence, entry_condition_states, watch_point_states, tda_session, blueprint, playbook=None) -> None:
        self.load_state(thesis_state, evidence, entry_condition_states, watch_point_states)
        self._load_tda_context(tda_session, blueprint)
        if playbook is not None:
            candidate = SetupCandidate(
                name=playbook.name,
                source_type="Playbook",
                source_id=playbook.id,
                source_revision=playbook.revision,
                definition_snapshot=playbook.to_snapshot(),
                entry_condition_states=entry_condition_states,
            )
            self._render_candidates([candidate], tda_session, None)
        else:
            self._render_base_policy(entry_condition_states, watch_point_states, tda_session)

    def load_run_context(self, trading_run: TradingRun, tda_session: TDAStationSession | None, blueprint: ProcessBlueprint) -> None:
        self.candidate_entry_checkboxes = {}
        self.candidate_watch_point_combos = {}
        self.entry_checkboxes = {}
        self.watch_point_combos = {}
        self.load_state(trading_run.current_thesis_state, trading_run.evidence)
        self.qt_summary_label.setText(
            "QT / AMDX · " + qt_context_summary(trading_run.qt_context)
        )
        raw_summary = raw_quarter_stack_summary(trading_run.market_time_context)
        raw_detail = raw_quarter_stack_detail(trading_run.market_time_context)
        alignment = raw_quarter_alignment(trading_run.market_time_context)
        strongest = max(alignment.items(), key=lambda item: item[1]) if alignment else None
        alignment_text = (
            f" · strongest {strongest[0]}×{strongest[1]}"
            if strongest is not None and strongest[1] > 1
            else ""
        )
        self.raw_qt_stack_label.setText(
            "Raw QT stack · "
            + raw_summary
            + alignment_text
            + ("\n" + raw_detail if raw_detail != "Not available" else "")
        )
        self._load_tda_context(tda_session, blueprint)
        self._render_authorization_gates(trading_run)
        if trading_run.setup_candidates:
            self._render_candidates(trading_run.setup_candidates, tda_session, trading_run)
        else:
            self._render_base_policy(trading_run.entry_condition_states, trading_run.watch_point_states, tda_session)

    def _render_authorization_gates(self, trading_run: TradingRun) -> None:
        self._clear_layout(self.authorization_layout)
        self.run_gate_combos = {}
        gates = [item for item in trading_run.authorization_policy_snapshot if str(item.get("scope", "Run")) == "Run"]
        if not trading_run.authorization_policy_snapshot:
            self.authorization_summary_label.setText("Authorization policy: Not configured for this run")
            return
        pending = 0
        blocked = 0
        for gate in gates:
            gate_id = str(gate.get("id", ""))
            state = trading_run.authorization_gate_states.get(gate_id, AuthorizationGateState.PENDING)
            if state is AuthorizationGateState.PENDING:
                pending += 1
            elif state is AuthorizationGateState.BLOCKED:
                blocked += 1
            row = QHBoxLayout()
            label = QLabel(str(gate.get("name", gate_id)))
            label.setWordWrap(True)
            label.setToolTip(str(gate.get("description", "")))
            combo = QComboBox()
            combo.addItems([item.value for item in AuthorizationGateState])
            combo.setCurrentText(state.value)
            combo.currentTextChanged.connect(
                lambda text, gid=gate_id: self.authorization_gate_state_changed.emit(gid, text)
            )
            self.run_gate_combos[gate_id] = combo
            row.addWidget(label, 1)
            row.addWidget(combo)
            self.authorization_layout.addLayout(row)
        if blocked:
            self.authorization_summary_label.setText(f"GLOBAL BLOCK · {blocked} Trade Plan gate(s) blocked")
        elif pending:
            self.authorization_summary_label.setText(f"Waiting · {pending} Trade Plan gate(s) still pending")
        else:
            self.authorization_summary_label.setText("Global Trade Plan gates clear")

    def _load_tda_context(self, tda_session: TDAStationSession | None, blueprint: ProcessBlueprint) -> None:
        self.watch_points_list.clear()
        if tda_session is None:
            self.tda_summary_label.setText("No saved TDA context available")
            return
        station_names = {
            station.id: station.name
            for mode in blueprint.modes if mode.id == "tda"
            for deck in mode.decks for station in deck.stations
        }
        priority_ids = ("tda-primary-draw", "tda-secondary-draw", "tda-thesis")
        populated = []
        for station_id in priority_ids:
            if station_id in tda_session.station_ids:
                observation = tda_session.observation_for(station_id).observation.strip()
                if observation:
                    populated.append((station_id, observation))
        if not populated:
            populated = [(item.station_id, item.observation.strip()) for item in tda_session.observations if item.observation.strip()][-4:]
        self.tda_summary_label.setText(
            f"{tda_session.completed_count()}/{len(tda_session.station_ids)} TDA stations complete · key context carried forward"
        )
        if not populated:
            self.watch_points_list.addItem("○ No TDA synthesis observations recorded")
        for station_id, observation in populated:
            compact = observation.replace("\n", " ")
            if len(compact) > 180:
                compact = compact[:177] + "..."
            self.watch_points_list.addItem(f"○ {station_names.get(station_id, station_id)} · {compact}")

    def _render_candidates(self, candidates: list[SetupCandidate], tda_session: TDAStationSession | None, trading_run: TradingRun | None) -> None:
        self._clear_layout(self.criteria_layout)
        self.candidate_entry_checkboxes = {}
        self.candidate_watch_point_combos = {}
        self.candidate_gate_combos = {}
        self.entry_checkboxes = {}
        self.watch_point_combos = {}

        playbook_candidates = [item for item in candidates if item.source_type == "Playbook"]
        configured = [item for item in playbook_candidates if item.definition_snapshot.get("entry_criteria")]
        self.readiness_count_label.setText(f"{len(playbook_candidates)} reference model(s) in play")
        self.readiness_required_label.setText("Authorization evaluated independently per setup candidate")
        self.readiness_status_label.setText("AUTHORIZED means the setup threshold and every applicable Trade Plan gate are clear.")
        self.risk_stop_label.setText("Model stop / risk guidance: shown per candidate")
        self.risk_status_label.setText(
            self.base_policy.risk_summary.strip()
            or "Candidate risk must still clear the plan-owned risk gate; model guidance never overrides account-level limits."
        )

        self.candidate_temporal_relevance = {}
        market_context = (
            dict(trading_run.market_time_context or {})
            if trading_run is not None
            else {}
        )
        priority = {
            "Active": 0,
            "Upcoming": 1,
            "Not Time-Bound": 2,
            "Not Configured": 3,
            "Closed": 4,
        }

        renderable = []
        for candidate in candidates:
            if candidate.source_type == "Custom" and not (
                tda_session and tda_session.watch_points
            ):
                continue
            timed_window_ids = list(
                candidate.definition_snapshot.get("timed_window_ids", []) or []
            )
            relevance = temporal_relevance_for(
                market_context,
                timed_window_ids,
            )
            self.candidate_temporal_relevance[candidate.id] = relevance
            renderable.append((candidate, relevance))

        renderable.sort(
            key=lambda item: (
                priority.get(str(item[1].get("state", "")), 9),
                item[0].name,
            )
        )
        for candidate, _relevance in renderable:
            self.criteria_layout.addWidget(
                self._build_candidate_card(
                    candidate,
                    tda_session,
                    trading_run,
                )
            )

        if len(configured) == 1:
            candidate = configured[0]
            for (candidate_id, criterion_id), checkbox in self.candidate_entry_checkboxes.items():
                if candidate_id == candidate.id:
                    self.entry_checkboxes[criterion_id] = checkbox
            criteria = candidate.definition_snapshot.get("entry_criteria", [])
            total = len(criteria)
            required = candidate.definition_snapshot.get("required_entry_count")
            satisfied = sum(candidate.entry_condition_states.get(str(item.get("id", "")), False) for item in criteria)
            self.readiness_count_label.setText(f"{satisfied} / {total} criteria currently met")
            self.readiness_required_label.setText(f"Required for setup: {required} / {total}")

    def _build_candidate_card(self, candidate: SetupCandidate, tda_session: TDAStationSession | None, trading_run: TradingRun | None) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(7, 6, 7, 6)
        layout.setSpacing(3)
        title = candidate.name + (f" · {candidate.source_revision}" if candidate.source_type == "Playbook" else "")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(title_label)

        relevance = self.candidate_temporal_relevance.get(candidate.id, {})
        relevance_state = str(relevance.get("state", "Not Time-Bound"))
        if relevance_state != "Not Time-Bound":
            window_name = str(relevance.get("window_name", ""))
            minutes = relevance.get("minutes_until_start")
            if relevance_state == "Active":
                temporal_text = f"TIME · ACTIVE · {window_name}"
            elif relevance_state == "Upcoming":
                temporal_text = (
                    f"TIME · UPCOMING · {window_name}"
                    + (f" in {minutes}m" if minutes is not None else "")
                )
            elif relevance_state == "Closed":
                temporal_text = "TIME · CLOSED · no configured model window remains today"
            else:
                temporal_text = "TIME · NOT CONFIGURED"
            temporal_label = QLabel(temporal_text)
            temporal_label.setWordWrap(True)
            if relevance_state == "Active":
                temporal_label.setStyleSheet("font-weight: 700;")
            layout.addWidget(temporal_label)

        if trading_run is not None:
            result = trading_run.candidate_authorization(candidate.id)
            status = QLabel(result.status.value.upper())
            status.setStyleSheet("font-size: 15px; font-weight: 700;")
            layout.addWidget(status)
            if result.blockers:
                blockers = QLabel("Blocked because:\n• " + "\n• ".join(result.blockers))
                blockers.setWordWrap(True)
                layout.addWidget(blockers)
            elif result.detail:
                detail = QLabel(result.detail)
                detail.setWordWrap(True)
                layout.addWidget(detail)

            candidate_gates = [item for item in trading_run.authorization_policy_snapshot if str(item.get("scope", "Run")) == "Candidate"]
            for gate in candidate_gates:
                gate_id = str(gate.get("id", ""))
                row = QHBoxLayout()
                gate_label = QLabel(str(gate.get("name", gate_id)))
                gate_label.setWordWrap(True)
                gate_label.setToolTip(str(gate.get("description", "")))
                combo = QComboBox()
                combo.addItems([item.value for item in AuthorizationGateState])
                combo.setCurrentText(candidate.authorization_gate_states.get(gate_id, AuthorizationGateState.PENDING).value)
                combo.currentTextChanged.connect(
                    lambda text, cid=candidate.id, gid=gate_id: self.candidate_authorization_gate_state_changed.emit(cid, gid, text)
                )
                self.candidate_gate_combos[(candidate.id, gate_id)] = combo
                row.addWidget(gate_label, 1)
                row.addWidget(combo)
                layout.addLayout(row)

        if (
            candidate.source_type == "Playbook"
            and relevance_state == "Closed"
        ):
            quiet = QLabel(
                "This model is outside its configured entry windows for the current "
                "market time. Detailed setup controls are quiet until a relevant window."
            )
            quiet.setWordWrap(True)
            layout.addWidget(quiet)
            return frame

        if candidate.source_type == "Custom":
            note = QLabel("Technician/day-specific setup · explicit authorization criteria can be added later without requiring a named model.")
            note.setWordWrap(True)
            layout.addWidget(note)
            for point in (tda_session.watch_points if tda_session else []):
                self._add_candidate_watch_row(layout, candidate, point.id, point.if_condition, point.then_action)
            return frame

        snapshot = candidate.definition_snapshot
        criteria = snapshot.get("entry_criteria", [])
        required = snapshot.get("required_entry_count")
        if criteria:
            satisfied = sum(candidate.entry_condition_states.get(str(item.get("id", "")), False) for item in criteria)
            layout.addWidget(QLabel(f"Setup readiness: {satisfied}/{len(criteria)} · required {required}/{len(criteria)}"))
            for item in criteria:
                criterion_id = str(item.get("id", ""))
                checkbox = QCheckBox(str(item.get("name", criterion_id)))
                checkbox.setToolTip(str(item.get("description", "")))
                checkbox.setChecked(candidate.entry_condition_states.get(criterion_id, False))
                checkbox.toggled.connect(
                    lambda checked, candidate_id=candidate.id, cid=criterion_id: self._candidate_entry_toggled(candidate_id, cid, checked)
                )
                self.candidate_entry_checkboxes[(candidate.id, criterion_id)] = checkbox
                layout.addWidget(checkbox)
        else:
            layout.addWidget(QLabel("Setup authorization threshold: not explicitly encoded for this model."))

        watch_points = snapshot.get("watch_point_templates", [])
        if watch_points:
            wp_heading = QLabel("Watch sequence")
            wp_heading.setStyleSheet("font-weight: 600;")
            layout.addWidget(wp_heading)
            for item in watch_points:
                self._add_candidate_watch_row(
                    layout,
                    candidate,
                    str(item.get("id", "")),
                    str(item.get("if_condition", "")),
                    str(item.get("then_action", "")),
                )
        risk = str(snapshot.get("risk_summary", "")).strip()
        if risk:
            risk_label = QLabel(f"Risk / stop guidance: {risk}")
            risk_label.setWordWrap(True)
            layout.addWidget(risk_label)
        return frame

    def _add_candidate_watch_row(self, layout, candidate, watch_id, if_condition, then_action) -> None:
        row = QHBoxLayout()
        label = QLabel(f"IF {if_condition} → THEN {then_action}")
        label.setWordWrap(True)
        combo = QComboBox()
        combo.addItems([state.value for state in WatchPointState])
        combo.setCurrentText(candidate.watch_point_states.get(watch_id, WatchPointState.WAITING).value)
        combo.currentTextChanged.connect(
            lambda state_text, candidate_id=candidate.id, wid=watch_id: self._candidate_watch_changed(candidate_id, wid, state_text)
        )
        self.candidate_watch_point_combos[(candidate.id, watch_id)] = combo
        if candidate.source_type == "Custom":
            self.watch_point_combos[watch_id] = combo
        row.addWidget(label, 1)
        row.addWidget(combo)
        layout.addLayout(row)

    def _render_base_policy(self, states, watch_states, tda_session=None) -> None:
        self._clear_layout(self.criteria_layout)
        self.entry_checkboxes = {}
        self.watch_point_combos = {}
        policy = self.base_policy
        if not policy.entry_criteria:
            self.readiness_count_label.setText("Entry criteria: Not configured")
            self.readiness_required_label.setText("Required for entry: Not configured")
            self.readiness_status_label.setText("This Trade Plan revision does not define a legacy/global entry-readiness threshold.")
        else:
            valid_ids = {criterion.id for criterion in policy.entry_criteria}
            satisfied = sum(states.get(item, False) for item in valid_ids)
            total = len(valid_ids)
            required = policy.required_entry_count
            self.readiness_count_label.setText(f"{satisfied} / {total} criteria currently met")
            self.readiness_required_label.setText(f"Required for entry: {required} / {total}")
            self.readiness_status_label.setText(
                "Readiness threshold satisfied by the active Trade Plan."
                if required is not None and satisfied >= required
                else f"Waiting · {max((required or 0) - satisfied, 0)} additional criterion/criteria required."
            )
            for criterion in policy.entry_criteria:
                checkbox = QCheckBox(criterion.name)
                checkbox.setToolTip(criterion.description)
                checkbox.setChecked(states.get(criterion.id, False))
                checkbox.toggled.connect(lambda checked, cid=criterion.id: self.entry_condition_changed.emit(cid, checked))
                self.entry_checkboxes[criterion.id] = checkbox
                self.criteria_layout.addWidget(checkbox)
        self.risk_status_label.setText(policy.risk_summary.strip() or "Risk rules are not yet encoded in this legacy policy path.")
        if tda_session is not None:
            for point in tda_session.watch_points:
                row = QHBoxLayout()
                label = QLabel(f"Day · IF {point.if_condition} → THEN {point.then_action}")
                combo = QComboBox()
                combo.addItems([state.value for state in WatchPointState])
                combo.setCurrentText(watch_states.get(point.id, WatchPointState.WAITING).value)
                combo.currentTextChanged.connect(lambda text, wid=point.id: self.watch_point_state_changed.emit(wid, text))
                self.watch_point_combos[point.id] = combo
                row.addWidget(label, 1)
                row.addWidget(combo)
                self.criteria_layout.addLayout(row)

    def _candidate_entry_toggled(self, candidate_id, criterion_id, checked) -> None:
        if not self._loading:
            self.candidate_entry_condition_changed.emit(candidate_id, criterion_id, checked)

    def _candidate_watch_changed(self, candidate_id, watch_id, state_text) -> None:
        if not self._loading:
            self.candidate_watch_point_state_changed.emit(candidate_id, watch_id, WatchPointState(state_text).value)

    def _submit_observation(self) -> None:
        note = self.observation_input.text().strip()
        if note:
            self.observation_submitted.emit(note)
            self.observation_input.clear()

    def _submit_thesis_state(self, state: ThesisState) -> None:
        note = self.thesis_note_input.text().strip()
        self.thesis_state_submitted.emit(state.value, note)
        self.thesis_note_input.clear()
