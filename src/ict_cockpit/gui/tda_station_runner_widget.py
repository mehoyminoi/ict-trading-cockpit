from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
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
    """Execute the TDA portion of the process blueprint one station at a time."""

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

        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.deck_label)
        layout.addWidget(self.station_label)
        layout.addWidget(self.question_label)
        layout.addWidget(self.tradingview_label)
        layout.addWidget(QLabel("Observation"))
        layout.addWidget(self.observation_input, 1)
        layout.addLayout(nav)

        self._update_view()

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
        index = self.current_station_index
        if index == 0:
            return
        current = self.session.observation_for(self.current_station_id)
        current.observation = self.observation_input.toPlainText().strip()
        self.session.current_station_id = self._stations[index - 1][1].id
        self._touch()
        self._update_view()

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
