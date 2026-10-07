from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4

from ict_cockpit.analysis.market_time import temporal_relevance_for


MARKET_SESSION_NAMES = ("Asia", "London", "NYAM", "NYPM")
SESSION_NAMES = MARKET_SESSION_NAMES


class TradingSessionRunStatus(str, Enum):
    ACTIVE = "Active"
    CONCLUDED = "Concluded"


class RunEnvironment(str, Enum):
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
    NOT_REVIEWED = "Not Reviewed"
    MATERIALLY_ACCURATE = "Materially Accurate / Remained Intact"
    MISSED_CRITICAL_INFORMATION = "Changed — Critical Information Missed"
    UNEXPLAINED_STUDY_NEEDED = "Changed — Unexplained / Study Needed"
    EXOGENOUS_EVENT = "Changed — External / Exogenous Event"


class WatchPointState(str, Enum):
    WAITING = "Waiting"
    OCCURRED = "Occurred"
    INVALIDATED = "Invalidated"


class AuthorizationGateState(str, Enum):
    PENDING = "Pending"
    CLEAR = "Clear"
    BLOCKED = "Blocked"


class AuthorizationStatus(str, Enum):
    NOT_CONFIGURED = "Not Configured"
    BLOCKED = "Blocked"
    AUTHORIZED = "Authorized"


class RunEvidenceKind(str, Enum):
    OBSERVATION = "Observation"
    THESIS_STATE = "Thesis State"


class ProcessAdherence(str, Enum):
    NOT_REVIEWED = "Not Reviewed"
    FOLLOWED = "Followed"
    MIXED = "Mixed"
    DEVIATION = "Deviation"


@dataclass
class AuthorizationResult:
    status: AuthorizationStatus
    blockers: list[str] = field(default_factory=list)
    detail: str = ""


@dataclass
class RunEvidenceEntry:
    kind: RunEvidenceKind
    note: str = ""
    thesis_state: ThesisState = ThesisState.NOT_SET
    market_time_context: dict = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        self.note = self.note.strip()
        self.market_time_context = dict(self.market_time_context or {})
        if isinstance(self.kind, str):
            self.kind = RunEvidenceKind(self.kind)
        if isinstance(self.thesis_state, str):
            self.thesis_state = ThesisState(self.thesis_state)


@dataclass
class SetupCandidate:
    """One possible setup being watched during a Trading Run."""

    name: str
    source_type: str = "Custom"
    source_id: str = ""
    source_revision: str = ""
    definition_snapshot: dict = field(default_factory=dict)
    entry_condition_states: dict[str, bool] = field(default_factory=dict)
    watch_point_states: dict[str, WatchPointState] = field(default_factory=dict)
    authorization_gate_states: dict[str, AuthorizationGateState] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.source_type = self.source_type.strip() or "Custom"
        self.source_id = self.source_id.strip()
        self.source_revision = self.source_revision.strip()
        self.definition_snapshot = dict(self.definition_snapshot or {})
        self.entry_condition_states = {
            str(key).strip(): bool(value)
            for key, value in self.entry_condition_states.items()
            if str(key).strip()
        }
        self.watch_point_states = {
            str(key).strip(): (
                value if isinstance(value, WatchPointState) else WatchPointState(value)
            )
            for key, value in self.watch_point_states.items()
            if str(key).strip()
        }
        self.authorization_gate_states = {
            str(key).strip(): (
                value if isinstance(value, AuthorizationGateState) else AuthorizationGateState(value)
            )
            for key, value in self.authorization_gate_states.items()
            if str(key).strip()
        }
        if not self.name:
            raise ValueError("setup candidate name cannot be empty")
        if self.source_type == "Playbook":
            if not self.source_id or not self.source_revision or not self.definition_snapshot:
                raise ValueError("playbook setup candidate requires source id, revision, and snapshot")

    def set_entry_condition(self, criterion_id: str, satisfied: bool) -> None:
        criterion_id = criterion_id.strip()
        if not criterion_id:
            raise ValueError("entry criterion id cannot be empty")
        self.entry_condition_states[criterion_id] = bool(satisfied)

    def set_watch_point_state(self, watch_point_id: str, state: WatchPointState | str) -> None:
        watch_point_id = watch_point_id.strip()
        if not watch_point_id:
            raise ValueError("watch point id cannot be empty")
        state = WatchPointState(state)
        self.watch_point_states[watch_point_id] = state

        templates = self.definition_snapshot.get("watch_point_templates", [])
        template = next((item for item in templates if str(item.get("id", "")) == watch_point_id), None)
        if template is not None:
            satisfied = state is WatchPointState.OCCURRED
            for criterion_id in template.get("satisfies_criterion_ids", []):
                criterion_id = str(criterion_id).strip()
                if criterion_id:
                    self.entry_condition_states[criterion_id] = satisfied

    def set_authorization_gate(self, gate_id: str, state: AuthorizationGateState | str) -> None:
        gate_id = gate_id.strip()
        if not gate_id:
            raise ValueError("authorization gate id cannot be empty")
        self.authorization_gate_states[gate_id] = AuthorizationGateState(state)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "source_revision": self.source_revision,
            "definition_snapshot": self.definition_snapshot,
            "entry_condition_states": self.entry_condition_states,
            "watch_point_states": {key: value.value for key, value in self.watch_point_states.items()},
            "authorization_gate_states": {key: value.value for key, value in self.authorization_gate_states.items()},
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "SetupCandidate":
        return cls(
            id=str(payload.get("id", str(uuid4()))),
            name=str(payload.get("name", "")),
            source_type=str(payload.get("source_type", "Custom")),
            source_id=str(payload.get("source_id", "")),
            source_revision=str(payload.get("source_revision", "")),
            definition_snapshot=dict(payload.get("definition_snapshot", {}) or {}),
            entry_condition_states=dict(payload.get("entry_condition_states", {}) or {}),
            watch_point_states=dict(payload.get("watch_point_states", {}) or {}),
            authorization_gate_states=dict(payload.get("authorization_gate_states", {}) or {}),
        )


@dataclass
class TradingSessionRun:
    trading_day_id: str
    session_name: str
    process_session_id: str
    tda_station_session_id: str = ""
    environment: RunEnvironment = RunEnvironment.LIVE
    trade_plan_revision: str = ""
    setup_candidates: list[SetupCandidate] = field(default_factory=list)
    authorization_policy_snapshot: list[dict] = field(default_factory=list)
    authorization_gate_states: dict[str, AuthorizationGateState] = field(default_factory=dict)
    market_time_context: dict = field(default_factory=dict)

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
    started_at: str = field(default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds"))
    concluded_at: str = ""
    updated_at: str = field(default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds"))

    def __post_init__(self) -> None:
        self.trading_day_id = self.trading_day_id.strip()
        self.session_name = self.session_name.strip()
        self.process_session_id = self.process_session_id.strip()
        self.tda_station_session_id = self.tda_station_session_id.strip()
        self.trade_plan_revision = self.trade_plan_revision.strip()
        self.selected_playbook_id = self.selected_playbook_id.strip()
        self.selected_playbook_revision = self.selected_playbook_revision.strip()
        self.playbook_snapshot = dict(self.playbook_snapshot or {})
        self.authorization_policy_snapshot = [dict(item) for item in (self.authorization_policy_snapshot or [])]
        self.market_time_context = dict(self.market_time_context or {})
        self.authorization_gate_states = {
            str(key).strip(): (
                value if isinstance(value, AuthorizationGateState) else AuthorizationGateState(value)
            )
            for key, value in self.authorization_gate_states.items()
            if str(key).strip()
        }
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
            self.review_interpretation_outcome = InterpretationOutcome(self.review_interpretation_outcome)
        if isinstance(self.review_process_adherence, str):
            self.review_process_adherence = ProcessAdherence(self.review_process_adherence)
        self.evidence = [item if isinstance(item, RunEvidenceEntry) else RunEvidenceEntry(**item) for item in self.evidence]
        self.setup_candidates = [item if isinstance(item, SetupCandidate) else SetupCandidate.from_dict(item) for item in self.setup_candidates]

        if not self.setup_candidates and self.selected_playbook_id and self.playbook_snapshot:
            name = str(self.playbook_snapshot.get("name", self.selected_playbook_id))
            self.setup_candidates.append(
                SetupCandidate(
                    name=name,
                    source_type="Playbook",
                    source_id=self.selected_playbook_id,
                    source_revision=self.selected_playbook_revision,
                    definition_snapshot=self.playbook_snapshot,
                    entry_condition_states=self.entry_condition_states,
                    watch_point_states={
                        key.removeprefix(f"playbook:{self.selected_playbook_id}:"): value
                        for key, value in self.watch_point_states.items()
                        if key.startswith(f"playbook:{self.selected_playbook_id}:")
                    },
                )
            )

        if not self.trading_day_id:
            raise ValueError("trading day id cannot be empty")
        if not self.session_name:
            raise ValueError("trading run label cannot be empty")
        if not self.process_session_id:
            raise ValueError("process session id cannot be empty")

    @property
    def run_label(self) -> str:
        return self.session_name

    @run_label.setter
    def run_label(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("trading run label cannot be empty")
        self.session_name = value

    def setup_candidate_by_id(self, candidate_id: str) -> SetupCandidate | None:
        return next((item for item in self.setup_candidates if item.id == candidate_id), None)

    def playbook_candidate(self, playbook_id: str) -> SetupCandidate | None:
        return next((item for item in self.setup_candidates if item.source_type == "Playbook" and item.source_id == playbook_id), None)

    def sync_playbook_candidates(self, snapshots: list[dict]) -> None:
        selected_ids = {str(item.get("id", "")) for item in snapshots}
        kept = [item for item in self.setup_candidates if item.source_type != "Playbook" or item.source_id in selected_ids]
        by_source = {item.source_id: item for item in kept if item.source_type == "Playbook"}
        for snapshot in snapshots:
            source_id = str(snapshot.get("id", "")).strip()
            revision = str(snapshot.get("revision", "")).strip()
            if source_id and revision and source_id not in by_source:
                kept.append(
                    SetupCandidate(
                        name=str(snapshot.get("name", source_id)),
                        source_type="Playbook",
                        source_id=source_id,
                        source_revision=revision,
                        definition_snapshot=snapshot,
                    )
                )
        self.setup_candidates = kept
        self._touch()

    def ensure_day_specific_candidate(self) -> SetupCandidate:
        candidate = next(
            (item for item in self.setup_candidates if item.source_type == "Custom" and item.source_id == "day-specific"),
            None,
        )
        if candidate is None:
            candidate = SetupCandidate(name="Technician / Day-Specific", source_type="Custom", source_id="day-specific")
            self.setup_candidates.append(candidate)
            self._touch()
        return candidate

    def set_authorization_gate(self, gate_id: str, state: AuthorizationGateState | str) -> None:
        gate_id = gate_id.strip()
        if not gate_id:
            raise ValueError("authorization gate id cannot be empty")
        self.authorization_gate_states[gate_id] = AuthorizationGateState(state)
        self._touch()

    def set_candidate_authorization_gate(self, candidate_id: str, gate_id: str, state: AuthorizationGateState | str) -> None:
        candidate = self.setup_candidate_by_id(candidate_id)
        if candidate is None:
            return
        candidate.set_authorization_gate(gate_id, state)
        self._touch()

    def set_candidate_entry_condition(self, candidate_id: str, criterion_id: str, satisfied: bool) -> None:
        candidate = self.setup_candidate_by_id(candidate_id)
        if candidate is None:
            return
        candidate.set_entry_condition(criterion_id, satisfied)
        self._touch()

    def set_candidate_watch_point_state(self, candidate_id: str, watch_point_id: str, state: WatchPointState | str) -> None:
        candidate = self.setup_candidate_by_id(candidate_id)
        if candidate is None:
            return
        candidate.set_watch_point_state(watch_point_id, state)
        self._touch()

    def candidate_authorization(self, candidate_id: str) -> AuthorizationResult:
        candidate = self.setup_candidate_by_id(candidate_id)
        if candidate is None:
            return AuthorizationResult(AuthorizationStatus.NOT_CONFIGURED, detail="Setup candidate is unavailable.")
        if not self.authorization_policy_snapshot:
            return AuthorizationResult(
                AuthorizationStatus.NOT_CONFIGURED,
                detail="Trade Plan authorization gates are not snapshotted for this run.",
            )

        blockers: list[str] = []
        timed_window_ids = list(
            candidate.definition_snapshot.get("timed_window_ids", []) or []
        )
        if timed_window_ids:
            temporal = temporal_relevance_for(
                self.market_time_context,
                timed_window_ids,
            )
            temporal_state = str(temporal.get("state", "Not Configured"))
            if temporal_state == "Upcoming":
                minutes = temporal.get("minutes_until_start")
                window_name = str(temporal.get("window_name", "model window"))
                blockers.append(
                    f"Model time window: {window_name} upcoming"
                    + (f" in {minutes}m" if minutes is not None else "")
                )
            elif temporal_state == "Closed":
                blockers.append("Model time window: closed for the current market time")
            elif temporal_state != "Active":
                blockers.append("Model time window: temporal eligibility is not configured")

        for gate in self.authorization_policy_snapshot:
            gate_id = str(gate.get("id", "")).strip()
            name = str(gate.get("name", gate_id))
            scope = str(gate.get("scope", "Run"))
            if not gate_id:
                continue
            if scope == "Candidate":
                state = candidate.authorization_gate_states.get(gate_id, AuthorizationGateState.PENDING)
            else:
                state = self.authorization_gate_states.get(gate_id, AuthorizationGateState.PENDING)
            if state is AuthorizationGateState.PENDING:
                blockers.append(f"{name}: not cleared")
            elif state is AuthorizationGateState.BLOCKED:
                blockers.append(f"{name}: blocked")

        criteria = list(candidate.definition_snapshot.get("entry_criteria", []))
        required = candidate.definition_snapshot.get("required_entry_count")
        if not criteria or required is None:
            detail = (
                "This setup has no explicit authorization threshold yet."
                if candidate.source_type == "Playbook"
                else "Technician/day-specific setup authorization is not configured yet."
            )
            return AuthorizationResult(AuthorizationStatus.NOT_CONFIGURED, blockers=blockers, detail=detail)

        satisfied = sum(
            1
            for item in criteria
            if candidate.entry_condition_states.get(str(item.get("id", "")), False)
        )
        remaining = max(int(required) - satisfied, 0)
        if remaining:
            unmet_names = [
                str(item.get("name", item.get("id", "criterion")))
                for item in criteria
                if not candidate.entry_condition_states.get(str(item.get("id", "")), False)
            ]
            blockers.append(
                f"Setup criteria: need {remaining} more"
                + (f" ({', '.join(unmet_names)})" if unmet_names else "")
            )

        if blockers:
            return AuthorizationResult(
                AuthorizationStatus.BLOCKED,
                blockers=blockers,
                detail=f"{satisfied}/{len(criteria)} setup criteria satisfied.",
            )
        return AuthorizationResult(
            AuthorizationStatus.AUTHORIZED,
            detail=f"{satisfied}/{len(criteria)} setup criteria satisfied and all Trade Plan gates are clear.",
        )

    def select_playbook(self, playbook_id: str, playbook_revision: str, snapshot: dict) -> None:
        self.sync_playbook_candidates([dict(snapshot)])
        self.selected_playbook_id = playbook_id.strip()
        self.selected_playbook_revision = playbook_revision.strip()
        self.playbook_snapshot = dict(snapshot)

    def clear_playbook(self) -> None:
        self.sync_playbook_candidates([])
        self.selected_playbook_id = ""
        self.selected_playbook_revision = ""
        self.playbook_snapshot = {}

    def set_entry_condition(self, criterion_id: str, satisfied: bool) -> None:
        playbooks = [item for item in self.setup_candidates if item.source_type == "Playbook"]
        if len(playbooks) == 1:
            self.set_candidate_entry_condition(playbooks[0].id, criterion_id, satisfied)
        self.entry_condition_states[criterion_id.strip()] = bool(satisfied)
        self._touch()

    def set_watch_point_state(self, watch_point_id: str, state: WatchPointState | str) -> None:
        self.watch_point_states[watch_point_id.strip()] = WatchPointState(state)
        self._touch()

    def add_observation(
        self,
        note: str,
        *,
        market_time_context: dict | None = None,
    ) -> RunEvidenceEntry:
        note = note.strip()
        if not note:
            raise ValueError("observation cannot be empty")
        entry = RunEvidenceEntry(
            kind=RunEvidenceKind.OBSERVATION,
            note=note,
            market_time_context=dict(market_time_context or self.market_time_context),
        )
        self.evidence.append(entry)
        self._touch()
        return entry

    def record_thesis_state(
        self,
        state: ThesisState | str,
        note: str = "",
        *,
        market_time_context: dict | None = None,
    ) -> RunEvidenceEntry:
        state = ThesisState(state)
        if state is ThesisState.NOT_SET:
            raise ValueError("an explicit thesis update must choose a thesis state")
        entry = RunEvidenceEntry(
            kind=RunEvidenceKind.THESIS_STATE,
            note=note,
            thesis_state=state,
            market_time_context=dict(market_time_context or self.market_time_context),
        )
        self.current_thesis_state = state
        self.evidence.append(entry)
        self._touch()
        return entry

    def update_post_market_review(self, *, interpretation_outcome=None, process_adherence=None, takeaway=None, film_night=None) -> None:
        if interpretation_outcome is not None:
            self.review_interpretation_outcome = InterpretationOutcome(interpretation_outcome)
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
