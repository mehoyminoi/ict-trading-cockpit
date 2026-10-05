from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class TDAStationObservation:
    station_id: str
    observation: str = ""
    completed: bool = False
    completed_actions: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.station_id = self.station_id.strip()
        self.observation = self.observation.strip()
        self.completed_actions = sorted(set(self.completed_actions))
        if not self.station_id:
            raise ValueError("station id cannot be empty")
        if any(index < 0 for index in self.completed_actions):
            raise ValueError("completed action indexes cannot be negative")


@dataclass
class TDAStationSession:
    blueprint_revision: str
    observations: list[TDAStationObservation]
    current_station_id: str
    id: str = field(default_factory=lambda: str(uuid4()))
    updated_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        self.blueprint_revision = self.blueprint_revision.strip()
        self.current_station_id = self.current_station_id.strip()
        if not self.blueprint_revision:
            raise ValueError("blueprint revision cannot be empty")
        if not self.observations:
            raise ValueError("TDA station session must contain observations")
        if self.current_station_id not in self.station_ids:
            raise ValueError("current station must exist in observations")

    @property
    def station_ids(self) -> list[str]:
        return [item.station_id for item in self.observations]

    def observation_for(self, station_id: str) -> TDAStationObservation:
        for observation in self.observations:
            if observation.station_id == station_id:
                return observation
        raise KeyError(station_id)

    def completed_count(self) -> int:
        return sum(1 for item in self.observations if item.completed)
