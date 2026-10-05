from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.trading_day_session import (
    TradingDaySession,
    TradingDayStatus,
    TransitionOutcome,
)
from ict_cockpit.gui.tda_station_runner_widget import TDAStationRunnerWidget
from ict_cockpit.process_blueprint import (
    ModeDefinition,
    ProcessBlueprint,
    TransitionDefinition,
)


class TradingDayRuntimeWidget(QWidget):
    """Runtime shell for deliberate movement through trading-day process modes."""

    session_changed = Signal(TradingDaySession)

    def __init__(self, blueprint: ProcessBlueprint) -> None:
        super().__init__()
        self.blueprint = blueprint
        self.modes = list(blueprint.modes)
        if not self.modes:
            raise ValueError("blueprint must contain trading-day modes")

        self.session = self._new_session()

        self.title_label = QLabel("Trading Day Session")
        self.title_label.setStyleSheet("font-size: 17px; font-weight: 600;")
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)

        self.mode_rail = QHBoxLayout()
        self.mode_labels: dict[str, QLabel] = {}
        for mode in self.modes:
            label = QLabel()
            label.setFrameShape(QFrame.Shape.StyledPanel)
            label.setContentsMargins(10, 8, 10, 8)
            self.mode_labels[mode.id] = label
            self.mode_rail.addWidget(label, 1)

        self.mode_stack = QStackedWidget()
        self.mode_pages: dict[str, QWidget] = {}

        self.tda_station_runner_widget = TDAStationRunnerWidget(blueprint)
        for mode in self.modes:
            if mode.id == "tda":
                page = self.tda_station_runner_widget
            else:
                page = self._build_placeholder_mode_page(mode)
            self.mode_pages[mode.id] = page
            self.mode_stack.addWidget(page)

        self.transition_frame = QFrame()
        self.transition_frame.setFrameShape(QFrame.Shape.StyledPanel)
        transition_layout = QVBoxLayout(self.transition_frame)
        transition_heading = QLabel("Available process transitions")
        transition_heading.setStyleSheet("font-weight: 600;")
        transition_layout.addWidget(transition_heading)

        self.transition_note_input = QLineEdit()
        self.transition_note_input.setPlaceholderText(
            "Decision note / reason (optional, but useful for later review)"
        )
        transition_layout.addWidget(self.transition_note_input)

        self.transition_buttons_layout = QHBoxLayout()
        transition_layout.addLayout(self.transition_buttons_layout)
        self.transition_buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.summary_label)
        layout.addLayout(self.mode_rail)
        layout.addWidget(self.mode_stack, 1)
        layout.addWidget(self.transition_frame)

        self._update_view()

    def _new_session(self) -> TradingDaySession:
        mode_ids = [mode.id for mode in self.modes]
        return TradingDaySession(
            blueprint_revision=self.blueprint.revision,
            mode_ids=mode_ids,
            current_mode_id=mode_ids[0],
        )

    @property
    def current_mode(self) -> ModeDefinition:
        return self.modes[self.session.current_mode_index]

    @property
    def feedback_record_id(self) -> str:
        if self.session.current_mode_id == "tda":
            return self.tda_station_runner_widget.current_station_id
        return self.session.current_mode_id

    @property
    def incomplete_tda_station_ids(self) -> list[str]:
        return [
            observation.station_id
            for observation in self.tda_station_runner_widget.session.observations
            if not observation.completed
        ]

    def _touch(self) -> None:
        self.session.updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
        self.session_changed.emit(self.session)

    def apply_transition(
        self,
        transition_id: str,
        *,
        reason: str = "",
        override_incomplete: bool = False,
    ) -> bool:
        """Apply one transition declared by the current process mode."""
        if self.session.status is TradingDayStatus.COMPLETE:
            return False

        transition = self.current_mode.transition_by_id(transition_id)
        if transition is None:
            return False

        if (
            self.session.current_mode_id == "tda"
            and transition.outcome == "advance"
            and self.incomplete_tda_station_ids
            and not override_incomplete
        ):
            return False

        if transition.outcome == "advance":
            self.session.transition_to(
                transition.target_mode_id,
                TransitionOutcome.ADVANCE,
                reason=reason,
                override_incomplete=override_incomplete,
            )
        elif transition.outcome == "return_to_analysis":
            self.session.return_to_analysis(
                transition.target_mode_id,
                reason=reason,
            )
        elif transition.outcome == "stand_down":
            self.session.stand_down(
                transition.target_mode_id,
                reason=reason,
            )
        elif transition.outcome == "complete_day":
            self.session.complete_day(reason=reason)
        else:
            return False

        self.transition_note_input.clear()
        self._touch()
        self._update_view()
        return True

    def request_transition(self, transition_id: str) -> None:
        transition = self.current_mode.transition_by_id(transition_id)
        if transition is None:
            return

        reason = self.transition_note_input.text().strip()
        if (
            self.session.current_mode_id == "tda"
            and transition.outcome == "advance"
            and self.incomplete_tda_station_ids
        ):
            missing_count = len(self.incomplete_tda_station_ids)
            message = QMessageBox(self)
            message.setIcon(QMessageBox.Icon.Warning)
            message.setWindowTitle("TDA is incomplete")
            message.setText(
                f"{missing_count} TDA station(s) are still incomplete."
            )
            message.setInformativeText(
                "Return to the missing work, or intentionally file the TDA incomplete and continue to Live Watch."
            )
            return_button = message.addButton(
                "Return to TDA",
                QMessageBox.ButtonRole.RejectRole,
            )
            override_button = message.addButton(
                "File Incomplete Anyway",
                QMessageBox.ButtonRole.AcceptRole,
            )
            message.exec()
            if message.clickedButton() is not override_button:
                if message.clickedButton() is return_button:
                    self._focus_first_incomplete_tda_station()
                return
            self.apply_transition(
                transition_id,
                reason=reason,
                override_incomplete=True,
            )
            return

        self.apply_transition(transition_id, reason=reason)

    def _focus_first_incomplete_tda_station(self) -> None:
        if not self.incomplete_tda_station_ids:
            return
        self.tda_station_runner_widget.select_station(self.incomplete_tda_station_ids[0])
        self.tda_station_runner_widget.view_tabs.setCurrentWidget(
            self.tda_station_runner_widget.focus_page
        )

    # Backward-compatible helper while older tests/callers migrate to named transitions.
    def go_next_mode(self) -> None:
        for transition in self.current_mode.transitions:
            if transition.outcome == "advance":
                self.apply_transition(
                    transition.id,
                    override_incomplete=(self.session.current_mode_id == "tda"),
                )
                return

    def go_previous_mode(self) -> None:
        # Generic backward navigation is intentionally no longer part of the UI.
        # Legitimate returns are represented as explicit process transitions.
        if self.session.current_mode_id == "live-watch":
            transition = self.current_mode.transition_by_id("live-return-analysis")
            if transition is not None:
                self.apply_transition(transition.id)

    def load_session(self, session: TradingDaySession) -> None:
        expected_ids = [mode.id for mode in self.modes]
        if session.blueprint_revision != self.blueprint.revision:
            return
        if session.mode_ids != expected_ids:
            return
        self.session = session
        self._update_view()

    def start_new(self) -> None:
        self.session = self._new_session()
        self.transition_note_input.clear()
        self._touch()
        self._update_view()

    def _build_placeholder_mode_page(self, mode: ModeDefinition) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        heading = QLabel(mode.name)
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(heading)

        purpose = QLabel(mode.purpose)
        purpose.setWordWrap(True)
        layout.addWidget(purpose)

        note = QLabel(
            "Runtime shell only — this mode is visible so the full trading-day loop can be tested before its stations become executable."
        )
        note.setWordWrap(True)
        note.setFrameShape(QFrame.Shape.StyledPanel)
        note.setContentsMargins(10, 8, 10, 8)
        layout.addWidget(note)

        for deck in mode.decks:
            deck_label = QLabel(f"{deck.name} · TradingView: {deck.tradingview_layout}")
            deck_label.setStyleSheet("font-weight: 600;")
            deck_label.setWordWrap(True)
            layout.addWidget(deck_label)

            for station in deck.stations:
                station_label = QLabel(f"• {station.name} — {station.question}")
                station_label.setWordWrap(True)
                station_label.setContentsMargins(12, 2, 4, 2)
                layout.addWidget(station_label)

        layout.addStretch()
        return page

    def _clear_transition_buttons(self) -> None:
        while self.transition_buttons_layout.count():
            item = self.transition_buttons_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.transition_buttons = {}

    def _rebuild_transition_buttons(self) -> None:
        self._clear_transition_buttons()
        if self.session.status is TradingDayStatus.COMPLETE:
            label = QLabel("✓ Trading day complete")
            self.transition_buttons_layout.addWidget(label)
            self.transition_buttons_layout.addStretch()
            self.transition_note_input.setEnabled(False)
            return

        self.transition_note_input.setEnabled(True)
        for transition in self.current_mode.transitions:
            button = QPushButton(transition.name)
            button.setToolTip(transition.description)
            button.clicked.connect(
                lambda _checked=False, transition_id=transition.id: self.request_transition(
                    transition_id
                )
            )
            self.transition_buttons[transition.id] = button
            self.transition_buttons_layout.addWidget(button)
        self.transition_buttons_layout.addStretch()

    def _update_view(self) -> None:
        current_index = self.session.current_mode_index
        current_mode = self.current_mode
        self.mode_stack.setCurrentWidget(self.mode_pages[current_mode.id])

        if self.session.status is TradingDayStatus.COMPLETE:
            summary = (
                f"Trading day complete · Outcome: {self.session.day_outcome or 'Complete'} · "
                f"{len(self.session.transitions)} recorded transition(s)"
            )
        else:
            summary = (
                f"Current mode: {current_mode.name} · "
                f"{len(self.session.completed_mode_ids)}/{len(self.modes)} modes concluded · "
                f"{len(self.session.transitions)} recorded transition(s)"
            )
        self.summary_label.setText(summary)

        for index, mode in enumerate(self.modes):
            if mode.id == self.session.current_mode_id and self.session.status is TradingDayStatus.ACTIVE:
                state = "▶ ACTIVE"
            elif mode.id in self.session.completed_mode_ids:
                state = "✓ CONCLUDED"
            elif index < current_index:
                state = "↶ AVAILABLE BY PROCESS"
            else:
                state = "○ UPCOMING"
            self.mode_labels[mode.id].setText(f"{state}\n{mode.name}")

        self._rebuild_transition_buttons()
