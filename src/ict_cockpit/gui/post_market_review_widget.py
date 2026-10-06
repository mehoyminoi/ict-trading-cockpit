from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.trading_day_session import TradingDayTransition
from ict_cockpit.analysis.trading_session_run import (
    ProcessAdherence,
    RunEvidenceKind,
    TradingRun,
)


class PostMarketReviewWidget(QWidget):
    """Show the run back to the user, then capture only non-inferable judgments."""

    review_changed = Signal(str, str, bool)

    def __init__(self) -> None:
        super().__init__()
        self._loading = False

        heading = QLabel("Post-Market Review")
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        purpose = QLabel(
            "The cockpit reconstructs the run first. Add only the judgments it cannot infer."
        )
        purpose.setWordWrap(True)

        self.run_summary_label = QLabel("No Trading Run loaded")
        self.run_summary_label.setWordWrap(True)
        self.run_summary_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.run_summary_label.setContentsMargins(10, 8, 10, 8)

        timeline_heading = QLabel("What the cockpit recorded")
        timeline_heading.setStyleSheet("font-weight: 600;")
        self.timeline_list = QListWidget()
        self.timeline_list.setMaximumHeight(180)

        adherence_heading = QLabel("Process adherence")
        adherence_heading.setStyleSheet("font-weight: 600;")
        adherence_note = QLabel(
            "Separate whether the process was followed from whether the market thesis was right."
        )
        adherence_note.setWordWrap(True)

        self.adherence_group = QButtonGroup(self)
        self.adherence_group.setExclusive(True)
        self.adherence_buttons: dict[ProcessAdherence, QPushButton] = {}
        adherence_layout = QHBoxLayout()
        for state in (
            ProcessAdherence.FOLLOWED,
            ProcessAdherence.MIXED,
            ProcessAdherence.DEVIATION,
        ):
            button = QPushButton(state.value)
            button.setCheckable(True)
            self.adherence_group.addButton(button)
            self.adherence_buttons[state] = button
            adherence_layout.addWidget(button)
        adherence_layout.addStretch()
        self.adherence_group.buttonClicked.connect(self._emit_review)

        self.takeaway_input = QLineEdit()
        self.takeaway_input.setPlaceholderText(
            "Optional takeaway — what is worth carrying forward?"
        )
        self.takeaway_input.editingFinished.connect(self._emit_review)

        self.film_night_checkbox = QCheckBox("Take this Trading Run to Film Night / Lab")
        self.film_night_checkbox.toggled.connect(self._emit_review)

        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(purpose)
        layout.addWidget(self.run_summary_label)
        layout.addWidget(timeline_heading)
        layout.addWidget(self.timeline_list)
        layout.addWidget(adherence_heading)
        layout.addWidget(adherence_note)
        layout.addLayout(adherence_layout)
        layout.addWidget(self.takeaway_input)
        layout.addWidget(self.film_night_checkbox)
        layout.addStretch()

    def load_state(
        self,
        trading_run: TradingRun,
        transitions: list[TradingDayTransition],
    ) -> None:
        self._loading = True
        try:
            outcome = trading_run.outcome or "In review"
            self.run_summary_label.setText(
                f"{trading_run.run_label} · Outcome: {outcome} · "
                f"Current thesis: {trading_run.current_thesis_state.value}"
            )

            self.timeline_list.clear()
            for transition in transitions:
                target = transition.to_mode_id or "end"
                reason = f" · {transition.reason}" if transition.reason else ""
                self.timeline_list.addItem(
                    f"Process · {transition.from_mode_id} → {target} · "
                    f"{transition.outcome.value}{reason}"
                )

            for item in trading_run.evidence:
                timestamp = item.created_at[11:19] if len(item.created_at) >= 19 else item.created_at
                if item.kind is RunEvidenceKind.THESIS_STATE:
                    text = f"{timestamp} · Thesis → {item.thesis_state.value}"
                    if item.note:
                        text += f" · {item.note}"
                else:
                    text = f"{timestamp} · Observation · {item.note}"
                self.timeline_list.addItem(text)

            for state, button in self.adherence_buttons.items():
                button.setChecked(trading_run.review_process_adherence is state)
            self.takeaway_input.setText(trading_run.review_takeaway)
            self.film_night_checkbox.setChecked(trading_run.review_film_night)
        finally:
            self._loading = False

    def clear_state(self) -> None:
        self._loading = True
        try:
            self.run_summary_label.setText("No Trading Run loaded")
            self.timeline_list.clear()
            self.adherence_group.setExclusive(False)
            for button in self.adherence_buttons.values():
                button.setChecked(False)
            self.adherence_group.setExclusive(True)
            self.takeaway_input.clear()
            self.film_night_checkbox.setChecked(False)
        finally:
            self._loading = False

    def _selected_adherence(self) -> ProcessAdherence:
        for state, button in self.adherence_buttons.items():
            if button.isChecked():
                return state
        return ProcessAdherence.NOT_REVIEWED

    def _emit_review(self, *_args) -> None:
        if self._loading:
            return
        self.review_changed.emit(
            self._selected_adherence().value,
            self.takeaway_input.text().strip(),
            self.film_night_checkbox.isChecked(),
        )
