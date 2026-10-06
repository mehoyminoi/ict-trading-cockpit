from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


MARKET_SESSION_NAMES = ("Asia", "London", "NYAM", "NYPM")
SESSION_NAMES = MARKET_SESSION_NAMES


class TradingSessionRunStatus(str, Enum):
    ACTIVE = "Active"
    CONCLUDED = "Concluded"


class RunEnvironment(str, Enum):
    """Where the same operating process is being practiced or executed."""

    LIVE = "Live"
    REPLAY = "Replay"
    HISTORICAL_BACKTEST = "Historical Backtest"
    FORWARD_TEST = "Forward Test"


class ThesisState(str, Enum):
    NOT_SET = "Not Set"
    SUPPORTED = "Supported"
    WEAKENED = "Weakened"
    INVALIDATED = "Invalidated"
    UNCERTAIN = "Uncertain"


class InterpretationOutcome(str, Enum):
    """Post-run judgment of the initial market interpretation."""

    NOT_REVIEWED = "Not Reviewed"
    MATERIALLY_ACCURATE = "Materially Accurate / Remained Intact"
    MISSED_CRITICAL_INFORMATION = "Changed — Critical Information Missed"
    UNEXPLAINED_STUDY_NEEDED = "Changed — Unexplained / Study Needed"
    EXOGENOUS_EVENT = "Changed — External / Exogenous Event"


class WatchPointState(str, Enum):
    WAITING = "Waiting"
    OCCURRED = "Occurred"
    INVALIDATED = "Invalidated"


class RunEvidenceKind(str, Enum):
    OBSERVATION = "Observation"
    THESIS_STATE = "Thesis State"


class ProcessAdherence(str, Enum):
    NOT_REVIEWED = "Not Reviewed"
    FOLLOWED = "Followed"
    MIXED = "Mixed"
    DEVIATION = "Deviation"


@dataclass
class RunEvidenceEntry:
    kind: RunEvidenceKind
    note: str = ""
    thesis_state: ThesisState = ThesisState.NOT_SET
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        self.note = self.note.strip()
        if isinstance(self.kind, str):
            self.kind = RunEvidenceKind(self.kind)
        if isinstance(self.thesis_state, str):
            self.thesis_state = ThesisState(self.thesis_state)


@dataclass
class TradingSessionRun:
    """One deliberate operating run inside a Trading Day.

    Environment, Trade Plan revision, and the selected Playbook snapshot are
    provenance. The snapshot preserves the exact strategy rules that governed
    this run even after a later Trade Plan revision changes them.
    """

    trading_day_id: str
    session_name: str
    process_session_id: str
    tda_station_session_id: str = ""
    environment: RunEnvironment = RunEnvironment.LIVE
    trade_plan_revision: str = ""
    selected_playbook_id: str = ""
    selected_playbook_revision: str = ""
    playbook_snapshot: dict = field(default_factory=dict)
    status: TradingSessionRunStatus = TradingSessionRunStatus.ACTIVE
    outcome: str = ""
    current_thesis_state: ThesisState = ThesisState.NOT_SET
    evidence: list[RunEvidenceEntry] = field(default_factory=list)
    entry_condition_states: dict[str, bool] = field(default_factory=dict)
    watch_point_states: dict[str, WatchPointState] = field(default_factory=dict)
    review_interpretation_outcome: InterpretationOutcome = InterpretationOutcome.NOT_REVIEWED
    review_process_adherence: ProcessAdherence = ProcessAdherence.NOT_REVIEWED
    review_takeaway: str = ""
    review_film_night: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))
    started_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )
    concluded_at: str = ""
    updated_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        self.trading_day_id = self.trading_day_id.strip()
        self.session_name = self.session_name.strip()
        self.process_session_id = self.process_session_id.strip()
        self.tda_station_session_id = self.tda_station_session_id.strip()
        self.trade_plan_revision = self.trade_plan_revision.strip()
        self.selected_playbook_id = self.selected_playbook_id.strip()
        self.selected_playbook_revision = self.selected_playbook_revision.strip()
        self.playbook_snapshot = dict(self.playbook_snapshot or {})
        self.outcome = self.outcome.strip()
        self.review_takeaway = self.review_takeaway.strip()
        self.concluded_at = self.concluded_at.strip()
        if isinstance(self.environment, str):
            self.environment = RunEnvironment(self.environment)
        if isinstance(self.status, str):
            self.status = TradingSessionRunStatus(self.status)
        if isinstance(self.current_thesis_state, str):
            self.current_thesis_state = ThesisState(self.current_thesis_state)
        if isinstance(self.review_interpretation_outcome, str):
            self.review_interpretation_outcome = InterpretationOutcome(
                self.review_interpretation_outcome
            )
        if isinstance(self.review_process_adherence, str):
            self.review_process_adherence = ProcessAdherence(self.review_process_adherence)
        self.evidence = [
            item if isinstance(item, RunEvidenceEntry) else RunEvidenceEntry(**item)
            for item in self.evidence
        ]
        self.entry_condition_states = {
            str(criterion_id).strip(): bool(state)
            for criterion_id, state in self.entry_condition_states.items()
            if str(criterion_id).strip()
        }
        self.watch_point_states = {
            str(watch_point_id).strip(): (
                state if isinstance(state, WatchPointState) else WatchPointState(state)
            )
            for watch_point_id, state in self.watch_point_states.items()
            if str(watch_point_id).strip()
        }

        if not self.trading_day_id:
            raise ValueError("trading day id cannot be empty")
        if not self.session_name:
            raise ValueError("trading run label cannot be empty")
        if not self.process_session_id:
            raise ValueError("process session id cannot be empty")
        if self.selected_playbook_id and not self.selected_playbook_revision:
            raise ValueError("selected playbook revision cannot be empty")
        if self.selected_playbook_id and not self.playbook_snapshot:
            raise ValueError("selected playbook requires a snapshot")

    @property
    def run_label(self) -> str:
        return self.session_name

    @run_label.setter
    def run_label(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("trading run label cannot be empty")
        self.session_name = value

    def select_playbook(
        self,
        playbook_id: str,
        playbook_revision: str,
        snapshot: dict,
    ) -> None:
        playbook_id = playbook_id.strip()
        playbook_revision = playbook_revision.strip()
        snapshot = dict(snapshot or {})
        if not playbook_id or not playbook_revision or not snapshot:
            raise ValueError("playbook selection requires id, revision, and snapshot")

        self.selected_playbook_id = playbook_id
        self.selected_playbook_revision = playbook_revision
        self.playbook_snapshot = snapshot
        self.entry_condition_states = {}
        self.watch_point_states = {
            key: value
            for key, value in self.watch_point_states.items()
            if not key.startswith("playbook:")
        }
        self._touch()

    def clear_playbook(self) -> None:
        self.selected_playbook_id = ""
        self.selected_playbook_revision = ""
        self.playbook_snapshot = {}
        self.entry_condition_states = {}
        self.watch_point_states = {
            key: value
            for key, value in self.watch_point_states.items()
            if not key.startswith("playbook:")
        }
        self._touch()

    def set_entry_condition(self, criterion_id: str, satisfied: bool) -> None:
        criterion_id = criterion_id.strip()
        if not criterion_id:
            raise ValueError("entry criterion id cannot be empty")
        self.entry_condition_states[criterion_id] = bool(satisfied)
        self._touch()

    def set_watch_point_state(
        self,
        watch_point_id: str,
        state: WatchPointState | str,
    ) -> None:
        watch_point_id = watch_point_id.strip()
        if not watch_point_id:
            raise ValueError("watch point id cannot be empty")
        self.watch_point_states[watch_point_id] = WatchPointState(state)
        self._touch()

    def add_observation(self, note: str) -> RunEvidenceEntry:
        note = note.strip()
        if not note:
            raise ValueError("observation cannot be empty")
        entry = RunEvidenceEntry(kind=RunEvidenceKind.OBSERVATION, note=note)
        self.evidence.append(entry)
        self._touch()
        return entry

    def record_thesis_state(
        self,
        state: ThesisState | str,
        note: str = "",
    ) -> RunEvidenceEntry:
        state = ThesisState(state)
        if state is ThesisState.NOT_SET:
            raise ValueError("an explicit thesis update must choose a thesis state")
        entry = RunEvidenceEntry(
            kind=RunEvidenceKind.THESIS_STATE,
            note=note,
            thesis_state=state,
        )
        self.current_thesis_state = state
        self.evidence.append(entry)
        self._touch()
        return entry

    def update_post_market_review(
        self,
        *,
        interpretation_outcome: InterpretationOutcome | str | None = None,
        process_adherence: ProcessAdherence | str | None = None,
        takeaway: str | None = None,
        film_night: bool | None = None,
    ) -> None:
        if interpretation_outcome is not None:
            self.review_interpretation_outcome = InterpretationOutcome(
                interpretation_outcome
            )
        if process_adherence is not None:
            self.review_process_adherence = ProcessAdherence(process_adherence)
        if takeaway is not None:
            self.review_takeaway = takeaway.strip()
        if film_night is not None:
            self.review_film_night = bool(film_night)
        self._touch()

    def conclude(self, outcome: str = "") -> None:
        if self.status is TradingSessionRunStatus.CONCLUDED:
            return
        self.outcome = outcome.strip()
        self.status = TradingSessionRunStatus.CONCLUDED
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        self.concluded_at = now
        self.updated_at = now

    def _touch(self) -> None:
        self.updated_at = datetime.now().astimezone().isoformat(timespec="seconds")


TradingRun = TradingSessionRun
TradingRunStatus = TradingSessionRunStatus
