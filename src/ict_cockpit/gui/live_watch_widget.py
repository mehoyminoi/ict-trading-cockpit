from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.trading_session_run import (
    RunEvidenceEntry,
    RunEvidenceKind,
    ThesisState,
)


class LiveWatchWidget(QWidget):
    """Low-friction evidence capture for an active Trading Run."""

    observation_submitted = Signal(str)
    thesis_state_submitted = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()

        heading = QLabel("Live Watch")
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")

        guidance = QLabel(
            "Capture only what materially changes the picture. The goal is to preserve evidence, not narrate every candle."
        )
        guidance.setWordWrap(True)

        self.thesis_state_label = QLabel("Current thesis state: Not Set")
        self.thesis_state_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.thesis_state_label.setContentsMargins(10, 8, 10, 8)

        thesis_heading = QLabel("Thesis Crossroads")
        thesis_heading.setStyleSheet("font-weight: 600;")

        self.thesis_note_input = QLineEdit()
        self.thesis_note_input.setPlaceholderText(
            "Why did the thesis state change? (optional)"
        )

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

        observation_heading = QLabel("Quick Observation")
        observation_heading.setStyleSheet("font-weight: 600;")
        observation_row = QHBoxLayout()
        self.observation_input = QLineEdit()
        self.observation_input.setPlaceholderText(
            "What changed or became important?"
        )
        self.capture_observation_button = QPushButton("Capture Observation")
        self.capture_observation_button.clicked.connect(self._submit_observation)
        self.observation_input.returnPressed.connect(self._submit_observation)
        observation_row.addWidget(self.observation_input, 1)
        observation_row.addWidget(self.capture_observation_button)

        evidence_heading = QLabel("Recent Evidence")
        evidence_heading.setStyleSheet("font-weight: 600;")
        self.evidence_list = QListWidget()
        self.evidence_list.setMaximumHeight(150)

        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(guidance)
        layout.addWidget(self.thesis_state_label)
        layout.addWidget(thesis_heading)
        layout.addWidget(self.thesis_note_input)
        layout.addLayout(thesis_buttons)
        layout.addSpacing(8)
        layout.addWidget(observation_heading)
        layout.addLayout(observation_row)
        layout.addSpacing(8)
        layout.addWidget(evidence_heading)
        layout.addWidget(self.evidence_list)
        layout.addStretch()

    def clear_state(self) -> None:
        self.thesis_note_input.clear()
        self.observation_input.clear()
        self.load_state(ThesisState.NOT_SET, [])

    def load_state(
        self,
        thesis_state: ThesisState | str,
        evidence: list[RunEvidenceEntry],
    ) -> None:
        thesis_state = ThesisState(thesis_state)
        self.thesis_state_label.setText(
            f"Current thesis state: {thesis_state.value}"
        )
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
