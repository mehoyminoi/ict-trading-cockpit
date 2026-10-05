from dataclasses import dataclass, field


DEFAULT_STATION_ACTIONS = (
    "Prepare the paired TradingView pane and make any required manual chart markings.",
    "Observe the chart in the context of this station's question.",
    "Record the observation that should carry forward in the analysis.",
)


@dataclass(frozen=True)
class StationDefinition:
    id: str
    name: str
    question: str
    tradingview_role: str = ""
    reference: str = ""
    action_items: tuple[str, ...] = DEFAULT_STATION_ACTIONS
    layout_row: int = -1
    layout_column: int = -1

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("station id cannot be empty")
        if not self.name.strip():
            raise ValueError("station name cannot be empty")
        if not self.question.strip():
            raise ValueError("station question cannot be empty")
        if any(not item.strip() for item in self.action_items):
            raise ValueError("station action items cannot be empty")
        if self.layout_row < -1 or self.layout_column < -1:
            raise ValueError("station layout coordinates cannot be less than -1")


@dataclass(frozen=True)
class DeckDefinition:
    id: str
    name: str
    tradingview_layout: str = ""
    stations: tuple[StationDefinition, ...] = field(default_factory=tuple)
    grid_columns: int = 2

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("deck id cannot be empty")
        if not self.name.strip():
            raise ValueError("deck name cannot be empty")
        if not self.stations:
            raise ValueError("deck must contain at least one station")
        if self.grid_columns < 1:
            raise ValueError("deck grid columns must be at least one")


@dataclass(frozen=True)
class ModeDefinition:
    id: str
    name: str
    purpose: str
    decks: tuple[DeckDefinition, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("mode id cannot be empty")
        if not self.name.strip():
            raise ValueError("mode name cannot be empty")
        if not self.decks:
            raise ValueError("mode must contain at least one deck")


@dataclass(frozen=True)
class ProcessBlueprint:
    id: str
    name: str
    revision: str
    modes: tuple[ModeDefinition, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("process id cannot be empty")
        if not self.name.strip():
            raise ValueError("process name cannot be empty")
        if not self.revision.strip():
            raise ValueError("process revision cannot be empty")
        if not self.modes:
            raise ValueError("process must contain at least one mode")

    def iter_stations(self):
        for mode in self.modes:
            for deck in mode.decks:
                for station in deck.stations:
                    yield mode, deck, station

    def station_by_id(
        self,
        station_id: str,
    ) -> tuple[ModeDefinition, DeckDefinition, StationDefinition] | None:
        for mode, deck, station in self.iter_stations():
            if station.id == station_id:
                return mode, deck, station
        return None
