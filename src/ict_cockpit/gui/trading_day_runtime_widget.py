from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.gui.tda_station_runner_widget import TDAStationRunnerWidget
from ict_cockpit.process_blueprint import ModeDefinition, ProcessBlueprint


class TradingDayRuntimeWidget(QWidget):
    """Runtime shell for moving through the trading-day process modes."""

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
            label.setAlignment(label.alignment())
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

        self.previous_button = QPushButton("← Previous Mode")
        self.next_button = QPushButton()
        self.previous_button.clicked.connect(self.go_previous_mode)
        self.next_button.clicked.connect(self.go_next_mode)

        nav = QHBoxLayout()
        nav.addWidget(self.previous_button)
        nav.addStretch()
        nav.addWidget(self.next_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.summary_label)
        layout.addLayout(self.mode_rail)
        layout.addWidget(self.mode_stack, 1)
        layout.addLayout(nav)

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

    def _touch(self) -> None:
        self.session.updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
        self.session_changed.emit(self.session)

    def go_next_mode(self) -> None:
        if self.session.move_next():
            self._touch()
            self._update_view()
            return

        # The final mode remains active; completing the whole Trading Day will
        # become its own explicit session-level lifecycle action later.
        self.session.mark_current_complete()
        self._touch()
        self._update_view()

    def go_previous_mode(self) -> None:
        if self.session.move_previous():
            self._touch()
            self._update_view()

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

    def _update_view(self) -> None:
        current_index = self.session.current_mode_index
        current_mode = self.current_mode
        self.mode_stack.setCurrentWidget(self.mode_pages[current_mode.id])

        self.summary_label.setText(
            f"Current mode: {current_mode.name} · "
            f"{len(self.session.completed_mode_ids)}/{len(self.modes)} modes marked complete"
        )

        for index, mode in enumerate(self.modes):
            if mode.id == self.session.current_mode_id:
                state = "▶ ACTIVE"
            elif mode.id in self.session.completed_mode_ids:
                state = "✓ COMPLETE"
            elif index < current_index:
                state = "↶ AVAILABLE"
            else:
                state = "○ UPCOMING"
            self.mode_labels[mode.id].setText(f"{state}\n{mode.name}")

        self.previous_button.setEnabled(current_index > 0)
        if current_index < len(self.modes) - 1:
            next_mode = self.modes[current_index + 1]
            self.next_button.setText(f"Continue to {next_mode.name} →")
            self.next_button.setEnabled(True)
        elif current_mode.id not in self.session.completed_mode_ids:
            self.next_button.setText("Mark Post-Market Review Complete")
            self.next_button.setEnabled(True)
        else:
            self.next_button.setText("Trading-Day Modes Complete")
            self.next_button.setEnabled(False)
