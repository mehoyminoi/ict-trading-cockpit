from datetime import datetime

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.tda_station_session import (
    TDAStationObservation,
    TDAStationSession,
)
from ict_cockpit.process_blueprint import ProcessBlueprint


class TDAStationRunnerWidget(QWidget):
    """Execute TDA stations in Focus view or spatial Deck view."""

    session_changed = Signal(TDAStationSession)

    def __init__(self, blueprint: ProcessBlueprint) -> None:
        super().__init__()
        self.blueprint = blueprint
        self._stations = [
            (deck, station)
            for mode in blueprint.modes
            if mode.id == "tda"
            for deck in mode.decks
            for station in deck.stations
        ]
        if not self._stations:
            raise ValueError("blueprint must contain TDA stations")

        self.session = self._new_session()
        self._loading = False
        self._action_checkboxes: list[QCheckBox] = []
        self._wheel_accumulator = 0
        self._wheel_threshold = 480

        self.view_tabs = QTabWidget()
        self.focus_page = QWidget()
        self.deck_page = QWidget()
        self.view_tabs.addTab(self.focus_page, "Focus")
        self.view_tabs.addTab(self.deck_page, "Deck")

        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("font-weight: 600;")
        self.deck_label = QLabel()
        self.deck_label.setWordWrap(True)
        self.station_label = QLabel()
        self.station_label.setStyleSheet("font-size: 17px; font-weight: 600;")
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.tradingview_label = QLabel()
        self.tradingview_label.setWordWrap(True)

        self.actions_frame = QFrame()
        self.actions_layout = QVBoxLayout(self.actions_frame)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)

        self.observation_input = QTextEdit()
        self.observation_input.setPlaceholderText(
            "Record what you see. Keep this factual; structured controls can be added later where useful."
        )
        self.observation_input.textChanged.connect(self._observation_changed)

        self.back_button = QPushButton("← Previous Station")
        self.next_button = QPushButton("Complete & Continue →")
        self.back_button.clicked.connect(self.go_back)
        self.next_button.clicked.connect(self.complete_and_continue)

        nav = QHBoxLayout()
        nav.addWidget(self.back_button)
        nav.addStretch()
        nav.addWidget(self.next_button)

        focus_layout = QVBoxLayout(self.focus_page)
        focus_layout.addWidget(self.progress_label)
        focus_layout.addWidget(self.deck_label)
        focus_layout.addWidget(self.station_label)
        focus_layout.addWidget(self.question_label)
        focus_layout.addWidget(self.tradingview_label)
        focus_layout.addWidget(QLabel("Actions"))
        focus_layout.addWidget(self.actions_frame)
        focus_layout.addWidget(QLabel("Observation"))
        focus_layout.addWidget(self.observation_input, 1)
        focus_layout.addLayout(nav)

        self.deck_layout = QVBoxLayout(self.deck_page)
        self.deck_heading = QLabel()
        self.deck_heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.deck_layout.addWidget(self.deck_heading)
        self.deck_grid_host = QWidget()
        self.deck_grid = QGridLayout(self.deck_grid_host)
        self.deck_layout.addWidget(self.deck_grid_host, 1)

        outer = QVBoxLayout(self)
        outer.addWidget(self.view_tabs)

        self._update_view()

        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def _new_session(self) -> TDAStationSession:
        observations = [
            TDAStationObservation(station_id=station.id)
            for _deck, station in self._stations
        ]
        return TDAStationSession(
            blueprint_revision=self.blueprint.revision,
            observations=observations,
            current_station_id=observations[0].station_id,
        )

    @property
    def current_station_index(self) -> int:
        station_ids = [station.id for _deck, station in self._stations]
        return station_ids.index(self.session.current_station_id)

    @property
    def current_station_id(self) -> str:
        return self.session.current_station_id

    def _touch(self) -> None:
        self.session.updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
        self.session_changed.emit(self.session)

    def _observation_changed(self) -> None:
        if self._loading:
            return
        observation = self.session.observation_for(self.current_station_id)
        observation.observation = self.observation_input.toPlainText().strip()
        self._touch()
        self._refresh_deck_view()

    def _action_changed(self, action_index: int, checked: bool) -> None:
        if self._loading:
            return
        observation = self.session.observation_for(self.current_station_id)
        indexes = set(observation.completed_actions)
        if checked:
            indexes.add(action_index)
        else:
            indexes.discard(action_index)
        observation.completed_actions = sorted(indexes)
        self._touch()
        self._refresh_deck_view()

    def complete_and_continue(self) -> None:
        observation = self.session.observation_for(self.current_station_id)
        observation.observation = self.observation_input.toPlainText().strip()
        observation.completed = True

        index = self.current_station_index
        if index < len(self._stations) - 1:
            self.session.current_station_id = self._stations[index + 1][1].id
        self._touch()
        self._update_view()

    def go_back(self) -> None:
        self.go_previous_station()

    def go_previous_station(self) -> None:
        index = self.current_station_index
        if index == 0:
            return
        self.select_station(self._stations[index - 1][1].id)

    def go_next_station(self) -> None:
        index = self.current_station_index
        if index >= len(self._stations) - 1:
            return
        self.select_station(self._stations[index + 1][1].id)

    def select_station(self, station_id: str) -> None:
        if station_id not in self.session.station_ids:
            return
        current = self.session.observation_for(self.current_station_id)
        current.observation = self.observation_input.toPlainText().strip()
        self.session.current_station_id = station_id
        self._touch()
        self._update_view()

    def open_station_from_deck(self, station_id: str) -> None:
        """Use Deck as a spatial index, then return directly to station work."""
        self.select_station(station_id)
        if self.current_station_id == station_id:
            self.view_tabs.setCurrentWidget(self.focus_page)

    def _navigate_wheel_direction(self, delta: int) -> None:
        """Navigate stations, using Deck as the zoomed-out boundary of Focus."""
        index = self.current_station_index
        if delta < 0:
            if index >= len(self._stations) - 1:
                self.view_tabs.setCurrentWidget(self.deck_page)
            else:
                self.go_next_station()
        else:
            if index == 0:
                self.view_tabs.setCurrentWidget(self.deck_page)
            else:
                self.go_previous_station()

    def _accumulate_wheel_navigation(self, delta: int) -> bool:
        """Accumulate wheel movement and navigate only after a deliberate threshold."""
        if delta == 0:
            return False

        if self._wheel_accumulator and (
            (delta > 0) != (self._wheel_accumulator > 0)
        ):
            self._wheel_accumulator = 0

        self._wheel_accumulator += delta
        if abs(self._wheel_accumulator) < self._wheel_threshold:
            return False

        self._navigate_wheel_direction(self._wheel_accumulator)
        self._wheel_accumulator = 0
        return True

    def eventFilter(self, watched, event) -> bool:
        if isinstance(watched, QWidget):
            belongs_to_runner = watched is self or self.isAncestorOf(watched)
            if belongs_to_runner:
                if event.type() == QEvent.Type.MouseButtonRelease:
                    if event.button() == Qt.MouseButton.BackButton:
                        self.go_previous_station()
                        return True
                    if event.button() == Qt.MouseButton.ForwardButton:
                        self.go_next_station()
                        return True

                if (
                    event.type() == QEvent.Type.Wheel
                    and self.view_tabs.currentWidget() is self.focus_page
                    and not isinstance(watched, QTextEdit)
                ):
                    delta = event.angleDelta()
                    dominant = delta.x() if abs(delta.x()) > abs(delta.y()) else delta.y()
                    if self._accumulate_wheel_navigation(dominant):
                        return True

        return super().eventFilter(watched, event)

    def load_session(self, session: TDAStationSession) -> None:
        expected_ids = [station.id for _deck, station in self._stations]
        if session.blueprint_revision != self.blueprint.revision:
            return
        if session.station_ids != expected_ids:
            return
        self.session = session
        self._update_view()

    def start_new(self) -> None:
        self.session = self._new_session()
        self._touch()
        self._update_view()

    def _rebuild_actions(self, action_items: tuple[str, ...], completed: list[int]) -> None:
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._action_checkboxes = []

        self._loading = True
        for index, text in enumerate(action_items):
            checkbox = QCheckBox(text)
            checkbox.setChecked(index in completed)
            checkbox.toggled.connect(
                lambda checked, action_index=index: self._action_changed(action_index, checked)
            )
            self.actions_layout.addWidget(checkbox)
            self._action_checkboxes.append(checkbox)
        self._loading = False

    def _current_deck(self):
        return self._stations[self.current_station_index][0]

    def _refresh_deck_view(self) -> None:
        while self.deck_grid.count():
            item = self.deck_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        current_deck = self._current_deck()
        self.deck_heading.setText(
            f"{current_deck.name} · TradingView: {current_deck.tradingview_layout}"
        )

        deck_stations = [
            station
            for deck, station in self._stations
            if deck.id == current_deck.id
        ]
        for index, station in enumerate(deck_stations):
            observation = self.session.observation_for(station.id)
            if observation.completed:
                state = "✓ Complete"
            elif station.id == self.current_station_id:
                state = "▶ Current"
            else:
                state = "○ Pending"

            summary = observation.observation.strip().replace("\n", " ")
            if len(summary) > 90:
                summary = summary[:87] + "..."
            if not summary:
                summary = "No observation yet"

            action_count = len(station.action_items)
            action_progress = f"{len(observation.completed_actions)}/{action_count} actions"
            button = QPushButton(
                f"{state}\n{station.name}\n{action_progress}\n\n{summary}"
            )
            button.setMinimumHeight(130)
            button.setCheckable(True)
            button.setChecked(station.id == self.current_station_id)
            button.clicked.connect(
                lambda _checked=False, station_id=station.id: self.open_station_from_deck(station_id)
            )

            if station.layout_row >= 0 and station.layout_column >= 0:
                row = station.layout_row
                column = station.layout_column
            else:
                row = index // current_deck.grid_columns
                column = index % current_deck.grid_columns
            self.deck_grid.addWidget(button, row, column)

    def _update_view(self) -> None:
        index = self.current_station_index
        deck, station = self._stations[index]
        observation = self.session.observation_for(station.id)

        self.progress_label.setText(
            f"TDA station {index + 1} of {len(self._stations)} · "
            f"{self.session.completed_count()} complete"
        )
        self.deck_label.setText(
            f"Deck: {deck.name}\nTradingView layout: {deck.tradingview_layout}"
        )
        self.station_label.setText(station.name)
        self.question_label.setText(f"Question\n{station.question}")
        self.tradingview_label.setText(
            f"TradingView role\n{station.tradingview_role or 'Not defined yet'}"
        )

        self._loading = True
        self.observation_input.setPlainText(observation.observation)
        self._loading = False
        self._rebuild_actions(station.action_items, observation.completed_actions)

        self.back_button.setEnabled(index > 0)
        if index == len(self._stations) - 1 and observation.completed:
            self.next_button.setText("TDA Stations Complete")
            self.next_button.setEnabled(False)
        elif index == len(self._stations) - 1:
            self.next_button.setText("Complete TDA Stations")
            self.next_button.setEnabled(True)
        else:
            self.next_button.setText("Complete & Continue →")
            self.next_button.setEnabled(True)

        self._refresh_deck_view()
