from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
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
)
from ict_cockpit.process_blueprint import ProcessBlueprint


class LiveWatchWidget(QWidget):
    """Primary waiting-and-watching surface for an active Trading Run.

    Live Watch should answer, at a glance: what did TDA establish, what am I
    waiting for, how close is the setup to authorization, and what risk envelope
    applies?  Evidence capture remains available but subordinate to operating
    state.
    """

    observation_submitted = Signal(str)
    thesis_state_submitted = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()

        self.heading = QLabel("Live Watch · Waiting & Watching")
        self.heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.guidance = QLabel(
            "Stay oriented to the TDA, wait for planned conditions, and act only when the Trade Plan authorizes it."
        )
        self.guidance.setWordWrap(True)

        # ------------------------------------------------------------------
        # TDA carry-forward / watch points
        # ------------------------------------------------------------------
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
        self.watch_points_list.setMaximumHeight(145)
        tda_layout.addWidget(tda_heading)
        tda_layout.addWidget(self.tda_summary_label)
        tda_layout.addWidget(self.watch_points_list)

        # ------------------------------------------------------------------
        # Entry readiness.  The alpha knows that the current Trade Plan expects
        # eight confluence slots, but it does not yet encode their authoritative
        # names or the required threshold.  Show that gap explicitly rather
        # than converting an example into a trading rule.
        # ------------------------------------------------------------------
        self.readiness_frame = QFrame()
        self.readiness_frame.setFrameShape(QFrame.Shape.StyledPanel)
        readiness_layout = QVBoxLayout(self.readiness_frame)
        readiness_layout.setContentsMargins(9, 7, 9, 7)
        readiness_layout.setSpacing(4)
        readiness_heading = QLabel("Entry Readiness")
        readiness_heading.setStyleSheet("font-weight: 600;")
        self.readiness_count_label = QLabel("0 / 8 confluences configured")
        self.readiness_count_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.readiness_required_label = QLabel("Required for entry: Not configured")
        self.readiness_note_label = QLabel(
            "The operating surface is ready for the eight Trade Plan conditions; their authoritative definitions still need to be encoded."
        )
        self.readiness_note_label.setWordWrap(True)
        readiness_layout.addWidget(readiness_heading)
        readiness_layout.addWidget(self.readiness_count_label)
        readiness_layout.addWidget(self.readiness_required_label)
        readiness_layout.addWidget(self.readiness_note_label)
        readiness_layout.addStretch()

        # ------------------------------------------------------------------
        # Risk envelope.  Same principle: expose the decision slot now, but do
        # not invent an instrument/account-specific stop allowance.
        # ------------------------------------------------------------------
        self.risk_frame = QFrame()
        self.risk_frame.setFrameShape(QFrame.Shape.StyledPanel)
        risk_layout = QVBoxLayout(self.risk_frame)
        risk_layout.setContentsMargins(9, 7, 9, 7)
        risk_layout.setSpacing(4)
        risk_heading = QLabel("Risk Envelope")
        risk_heading.setStyleSheet("font-weight: 600;")
        self.risk_instrument_label = QLabel("Instrument / account: Not configured")
        self.risk_stop_label = QLabel("Maximum permitted stop: Not configured")
        self.risk_status_label = QLabel(
            "Risk sizing will be derived from the active Trade Plan + account context, not re-entered here."
        )
        self.risk_status_label.setWordWrap(True)
        risk_layout.addWidget(risk_heading)
        risk_layout.addWidget(self.risk_instrument_label)
        risk_layout.addWidget(self.risk_stop_label)
        risk_layout.addWidget(self.risk_status_label)
        risk_layout.addStretch()

        # ------------------------------------------------------------------
        # Thesis state is useful, but it is no longer the center of the room.
        # ------------------------------------------------------------------
        self.thesis_frame = QFrame()
        self.thesis_frame.setFrameShape(QFrame.Shape.StyledPanel)
        thesis_layout = QVBoxLayout(self.thesis_frame)
        thesis_layout.setContentsMargins(9, 7, 9, 7)
        thesis_layout.setSpacing(4)
        thesis_top = QHBoxLayout()
        thesis_heading = QLabel("Thesis Crossroads")
        thesis_heading.setStyleSheet("font-weight: 600;")
        self.thesis_state_label = QLabel("Current thesis state: Not Set")
        thesis_top.addWidget(thesis_heading)
        thesis_top.addStretch()
        thesis_top.addWidget(self.thesis_state_label)
        thesis_layout.addLayout(thesis_top)

        self.thesis_note_input = QLineEdit()
        self.thesis_note_input.setPlaceholderText("Reason for a meaningful thesis change (optional)")
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
                lambda _checked=False, selected=state: self._submit_thesis_state(selected)
            )
            self.thesis_buttons[state] = button
            thesis_buttons.addWidget(button)
        thesis_buttons.addStretch()
        thesis_layout.addLayout(thesis_buttons)

        # Quiet evidence capture.  The full evidence list is intentionally kept
        # populated for compatibility/telemetry but not rendered as a log in the
        # normal operating room.
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

    def clear_state(self) -> None:
        self.thesis_note_input.clear()
        self.observation_input.clear()
        self.watch_points_list.clear()
        self.tda_summary_label.setText("No TDA context loaded")
        self.load_state(ThesisState.NOT_SET, [])

    def load_operating_context(
        self,
        thesis_state: ThesisState | str,
        evidence: list[RunEvidenceEntry],
        tda_session: TDAStationSession | None,
        blueprint: ProcessBlueprint,
    ) -> None:
        self.load_state(thesis_state, evidence)
        self._load_tda_context(tda_session, blueprint)

    def load_state(
        self,
        thesis_state: ThesisState | str,
        evidence: list[RunEvidenceEntry],
    ) -> None:
        thesis_state = ThesisState(thesis_state)
        self.thesis_state_label.setText(f"Current thesis: {thesis_state.value}")
        self.evidence_list.clear()
        for item in reversed(evidence[-12:]):
            time_text = item.created_at[11:19] if len(item.created_at) >= 19 else item.created_at
            if item.kind is RunEvidenceKind.THESIS_STATE:
                detail = item.thesis_state.value
                if item.note:
                    detail += f" — {item.note}"
                text = f"{time_text} · Thesis: {detail}"
            else:
                text = f"{time_text} · {item.note}"
            self.evidence_list.addItem(text)

    def _load_tda_context(
        self,
        tda_session: TDAStationSession | None,
        blueprint: ProcessBlueprint,
    ) -> None:
        self.watch_points_list.clear()
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
            observation = tda_session.observation_for(station_id).observation.strip()
            if observation:
                populated.append((station_id, observation))

        # If the synthesis stations are blank, surface other recorded TDA facts
        # rather than making Live Watch feel disconnected from completed work.
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
            self.watch_points_list.addItem("○ No explicit TDA watch points recorded yet")
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
