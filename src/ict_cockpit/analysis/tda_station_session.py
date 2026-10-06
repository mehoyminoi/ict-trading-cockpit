from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class TDAWatchPoint:
    """One explicit IF/THEN condition authored during TDA."""

    if_condition: str
    then_action: str
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self.if_condition = self.if_condition.strip()
        self.then_action = self.then_action.strip()
        if not self.if_condition:
            raise ValueError("watch point IF condition cannot be empty")
        if not self.then_action:
            raise ValueError("watch point THEN action cannot be empty")


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
    watch_points: list[TDAWatchPoint] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    updated_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        self.blueprint_revision = self.blueprint_revision.strip()
        self.current_station_id = self.current_station_id.strip()
        self.watch_points = [
            item if isinstance(item, TDAWatchPoint) else TDAWatchPoint(**item)
            for item in self.watch_points
        ]
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

    def add_watch_point(self, if_condition: str, then_action: str) -> TDAWatchPoint:
        watch_point = TDAWatchPoint(if_condition=if_condition, then_action=then_action)
        self.watch_points.append(watch_point)
        return watch_point

    def remove_watch_point(self, watch_point_id: str) -> bool:
        for index, watch_point in enumerate(self.watch_points):
            if watch_point.id == watch_point_id:
                del self.watch_points[index]
                return True
        return False

    def completed_count(self) -> int:
        return sum(1 for item in self.observations if item.completed)
