from datetime import datetime

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.market_time import build_market_time_context, current_new_york_time
from ict_cockpit.analysis.trading_day import TradingDay, TradingDayLifecycleStatus
from ict_cockpit.analysis.trading_day_session import TradingDaySession, TradingDayStatus
from ict_cockpit.analysis.trading_session_run import RunEnvironment, TradingRun, TradingRunStatus
from ict_cockpit.gui.trading_day_runtime_widget import TradingDayRuntimeWidget
from ict_cockpit.process_blueprint import ProcessBlueprint
from ict_cockpit.trade_plan import AuthorizationGateDefinition, LiveWatchPolicyDefinition, PlaybookDefinition


class TradingDayShellWidget(QWidget):
    """Own one or more Trading Runs under a Trading Day."""

    trading_day_changed = Signal(object)
    session_run_changed = Signal(object)

    def __init__(
        self,
        blueprint: ProcessBlueprint,
        live_watch_policy: LiveWatchPolicyDefinition | None = None,
        playbooks: tuple[PlaybookDefinition, ...] = (),
        authorization_gates: tuple[AuthorizationGateDefinition, ...] = (),
        *,
        run_environment: RunEnvironment = RunEnvironment.LIVE,
        trade_plan_revision: str = "",
    ) -> None:
        super().__init__()
        self.blueprint = blueprint
        self.live_watch_policy = live_watch_policy or LiveWatchPolicyDefinition()
        self.playbooks = tuple(playbooks)
        self.authorization_gates = tuple(authorization_gates)
        self.run_environment = RunEnvironment(run_environment)
        self.trade_plan_revision = trade_plan_revision.strip()
        self.run_market_timestamp: datetime | None = None
        self.trading_day = TradingDay()
        self.trading_runs: list[TradingRun] = []
        self.active_trading_run: TradingRun | None = None
        self.session_runs = self.trading_runs
        self.active_session_run = self.active_trading_run

        self.title_label = QLabel("Trading Day")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.resume_context_label = QLabel()
        self.resume_context_label.setWordWrap(True)
        self.resume_context_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.resume_context_label.setContentsMargins(8, 4, 8, 4)
        self.market_time_label = QLabel()
        self.market_time_label.setWordWrap(True)
        self.market_time_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.market_time_label.setContentsMargins(8, 4, 8, 4)

        self.run_history_label = QLabel("Trading Runs")
        self.run_history = QListWidget()
        self.run_history.setMaximumHeight(72)
        self.run_history.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.session_history = self.run_history

        self.start_run_button = QPushButton("Start Trading Run")
        self.start_run_button.clicked.connect(self.start_trading_run)
        self.start_session_button = self.start_run_button
        self.complete_day_button = QPushButton("Complete Trading Day")
        self.complete_day_button.clicked.connect(self.complete_trading_day)
        self.start_new_day_button = QPushButton("Start New Trading Day")
        self.start_new_day_button.clicked.connect(self.start_new_trading_day)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.addWidget(self.start_run_button)
        controls.addStretch()
        controls.addWidget(self.complete_day_button)
        controls.addWidget(self.start_new_day_button)

        self.runtime_frame = QFrame()
        self.runtime_frame.setFrameShape(QFrame.Shape.StyledPanel)
        runtime_layout = QVBoxLayout(self.runtime_frame)
        runtime_layout.setContentsMargins(4, 4, 4, 4)
        runtime_layout.setSpacing(4)
        self.runtime = TradingDayRuntimeWidget(
            blueprint,
            embedded_session_run=True,
            live_watch_policy=self.live_watch_policy,
            playbooks=self.playbooks,
        )
        self.runtime.layout().removeWidget(self.runtime.transition_frame)
        self.runtime.transition_frame.setParent(self)
        runtime_layout.addWidget(self.runtime)

        self.runtime.session_changed.connect(self._process_session_changed)
        self.runtime.models_in_play_changed.connect(self._sync_models_in_play)
        self.runtime.playbook_selected.connect(self._legacy_select_playbook)
        runner = self.runtime.tda_station_runner_widget
        runner.session_changed.connect(lambda _session: self._update_view())
        runner.view_tabs.currentChanged.connect(lambda _index: self._update_view())
        self.runtime.live_observation_submitted.connect(self._capture_live_observation)
        self.runtime.live_thesis_state_submitted.connect(self._record_live_thesis_state)
        self.runtime.live_entry_condition_changed.connect(self._set_live_entry_condition)
        self.runtime.live_watch_point_state_changed.connect(self._set_live_watch_point_state)
        self.runtime.live_candidate_entry_condition_changed.connect(self._set_candidate_entry_condition)
        self.runtime.live_candidate_watch_point_state_changed.connect(self._set_candidate_watch_point_state)
        self.runtime.live_watch_widget.authorization_gate_state_changed.connect(self._set_authorization_gate)
        self.runtime.live_watch_widget.candidate_authorization_gate_state_changed.connect(self._set_candidate_authorization_gate)
        self.runtime.post_market_interpretation_submitted.connect(self._update_interpretation_outcome)
        self.runtime.post_market_review_submitted.connect(self._update_post_market_review)

        self.tda_nav_frame = QFrame()
        self.tda_nav_frame.setFrameShape(QFrame.Shape.StyledPanel)
        tda_nav_layout = QHBoxLayout(self.tda_nav_frame)
        tda_nav_layout.setContentsMargins(8, 5, 8, 5)
        self.tda_back_button = QPushButton("← Previous Station")
        self.tda_next_button = QPushButton("Mark Station Complete & Continue →")
        self.tda_back_button.clicked.connect(runner.go_previous_station)
        self.tda_next_button.clicked.connect(runner.complete_and_continue)
        tda_nav_layout.addWidget(self.tda_back_button)
        tda_nav_layout.addStretch()
        tda_nav_layout.addWidget(self.tda_next_button)
        runner.back_button.hide()
        runner.next_button.hide()

        self.runtime_scroll = QScrollArea()
        self.runtime_scroll.setWidgetResizable(True)
        self.runtime_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.runtime_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.runtime_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.runtime_scroll.setWidget(self.runtime_frame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        layout.addWidget(self.title_label)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.resume_context_label)
        layout.addWidget(self.market_time_label)
        layout.addWidget(self.run_history_label)
        layout.addWidget(self.run_history)
        layout.addLayout(controls)
        layout.addWidget(self.runtime_scroll, 1)
        layout.addWidget(self.tda_nav_frame)
        layout.addWidget(self.runtime.transition_frame)
        self.market_time_timer = QTimer(self)
        self.market_time_timer.setInterval(30000)
        self.market_time_timer.timeout.connect(self._refresh_market_time_display)
        self.market_time_timer.start()
        self._update_view()

    @property
    def feedback_record_id(self) -> str:
        if self.active_trading_run is not None:
            return self.runtime.feedback_record_id
        return self.trading_day.id

    def _sync_legacy_aliases(self) -> None:
        self.session_runs = self.trading_runs
        self.active_session_run = self.active_trading_run

    def _playbook_by_id(self, playbook_id: str) -> PlaybookDefinition | None:
        return next((item for item in self.playbooks if item.id == playbook_id), None)

    def _current_tda_station_name(self) -> str:
        station_id = self.runtime.tda_station_runner_widget.current_station_id
        for mode in self.blueprint.modes:
            if mode.id == "tda":
                for deck in mode.decks:
                    for station in deck.stations:
                        if station.id == station_id:
                            return station.name
        return station_id

    def _resume_context_text(self) -> str:
        run = self.active_trading_run
        if run is None:
            if self.trading_day.status is TradingDayLifecycleStatus.COMPLETE:
                return "You are here · Trading Day complete"
            if self.trading_runs:
                return "You are here · Between Trading Runs"
            return "You are here · Fresh Trading Day"

        mode = self.runtime.current_mode
        environment = f" · {run.environment.value}" if run.environment is not RunEnvironment.LIVE else ""
        model_count = len([item for item in run.setup_candidates if item.source_type == "Playbook"])
        models = f" · {model_count} model(s) in play" if model_count else ""
        text = f"{run.run_label}{environment} · {mode.name}{models}"
        if mode.id == "tda":
            runner = self.runtime.tda_station_runner_widget
            text += f" · {self._current_tda_station_name()} · {runner.session.completed_count()}/{len(runner.session.station_ids)} complete"
        elif mode.id == "live-watch":
            text += f" · Thesis: {run.current_thesis_state.value}"
        elif mode.id == "post-market":
            text += " · Review in progress"
        return text

    def _market_time_context_for_new_run(self) -> dict:
        historical = self.run_environment in {
            RunEnvironment.REPLAY,
            RunEnvironment.HISTORICAL_BACKTEST,
        }
        if historical:
            moment = self.run_market_timestamp or current_new_york_time()
            source = "Historical Reference"
        else:
            moment = current_new_york_time()
            source = "Live Clock"
        return build_market_time_context(moment, source=source).to_dict()

    def _current_market_time_context(self) -> dict:
        run = self.active_trading_run
        if run is None:
            return build_market_time_context(
                current_new_york_time(),
                source="Live Clock",
            ).to_dict()
        if run.environment in {RunEnvironment.REPLAY, RunEnvironment.HISTORICAL_BACKTEST}:
            return dict(run.market_time_context or {})
        return build_market_time_context(
            current_new_york_time(),
            source="Live Clock",
        ).to_dict()

    def _refresh_market_time_display(self) -> None:
        context = self._current_market_time_context()
        if not context:
            self.market_time_label.setText("Market time · Not configured")
            return
        captured = str(context.get("captured_at", ""))
        clock = captured[11:16] if len(captured) >= 16 else captured
        session = str(context.get("session", "Closed"))
        daily_q = str(context.get("daily_quarter", ""))
        session_q = str(context.get("session_quarter", ""))
        quarter_text = " / ".join(item for item in (daily_q, session_q) if item)
        active_ids = list(context.get("active_window_ids", []) or [])
        windows = {
            str(item.get("id", "")): item
            for item in list(context.get("timed_windows", []) or [])
        }
        if active_ids:
            window_text = " · ACTIVE: " + ", ".join(
                str(windows.get(window_id, {}).get("name", window_id))
                for window_id in active_ids
            )
        else:
            next_id = str(context.get("next_window_id", ""))
            next_item = windows.get(next_id, {})
            if next_item:
                minutes = next_item.get("minutes_until_start")
                window_text = (
                    f" · Next: {next_item.get('name', next_id)}"
                    + (f" in {minutes}m" if minutes is not None else "")
                )
            else:
                window_text = ""
        quarter_suffix = f" · QT {quarter_text}" if quarter_text else ""
        self.market_time_label.setText(
            f"NY market time · {clock} ET · Trading Day {context.get('futures_trading_day', '')} "
            f"· {session}{quarter_suffix}{window_text}"
        )

    def ensure_primary_trading_run_started(self) -> bool:
        if self.trading_day.status is TradingDayLifecycleStatus.COMPLETE or self.active_trading_run is not None or self.trading_runs:
            return False
        return self.start_trading_run()

    def start_trading_run(self) -> bool:
        if self.trading_day.status is TradingDayLifecycleStatus.COMPLETE or self.active_trading_run is not None:
            return False
        self.runtime.start_new()
        market_time_context = self._market_time_context_for_new_run()
        if not self.trading_day.futures_day_label:
            self.trading_day.futures_day_label = str(
                market_time_context.get("futures_trading_day", "")
            )
        run = TradingRun(
            trading_day_id=self.trading_day.id,
            session_name=f"Trading Run {len(self.trading_runs) + 1}",
            process_session_id=self.runtime.session.id,
            tda_station_session_id=self.runtime.tda_station_runner_widget.session.id,
            environment=self.run_environment,
            trade_plan_revision=self.trade_plan_revision,
            authorization_policy_snapshot=[gate.to_dict() for gate in self.authorization_gates],
            market_time_context=market_time_context,
        )
        if self.playbooks:
            run.ensure_day_specific_candidate()
        self.trading_day.activate_session_run(run)
        self.trading_runs.append(run)
        self.active_trading_run = run
        self._sync_legacy_aliases()
        self.runtime.load_trading_run(run)
        self.trading_day_changed.emit(self.trading_day)
        self.session_run_changed.emit(run)
        self._update_view()
        return True

    def start_session_run(self, _session_name: str = "") -> bool:
        return self.start_trading_run()

    def _sync_models_in_play(self, playbook_ids) -> None:
        run = self.active_trading_run
        if run is None:
            return
        if run.trade_plan_revision and self.trade_plan_revision and run.trade_plan_revision != self.trade_plan_revision:
            self.runtime.load_trading_run(run)
            return
        snapshots = []
        for playbook_id in list(playbook_ids or []):
            playbook = self._playbook_by_id(str(playbook_id))
            if playbook is not None and playbook.available:
                snapshots.append(playbook.to_snapshot())
        run.sync_playbook_candidates(snapshots)
        if self.playbooks:
            run.ensure_day_specific_candidate()
        run.selected_playbook_id = ""
        run.selected_playbook_revision = ""
        run.playbook_snapshot = {}
        self._save_and_reload(run)

    def _legacy_select_playbook(self, playbook_id: str) -> None:
        selected = self.runtime.tda_watch_point_widget.selected_playbook_ids()
        if len(selected) == 1 and selected[0] == playbook_id:
            self._sync_models_in_play(selected)

    def _capture_live_observation(self, note: str) -> None:
        run = self.active_trading_run
        if run is not None:
            context = self._current_market_time_context()
            run.market_time_context = dict(context)
            run.add_observation(note, market_time_context=context)
            self._save_and_reload(run)

    def _record_live_thesis_state(self, state: str, note: str) -> None:
        run = self.active_trading_run
        if run is not None:
            context = self._current_market_time_context()
            run.market_time_context = dict(context)
            run.record_thesis_state(
                state,
                note,
                market_time_context=context,
            )
            self._save_and_reload(run)

    def _set_authorization_gate(self, gate_id: str, state: str) -> None:
        run = self.active_trading_run
        if run is not None:
            run.set_authorization_gate(gate_id, state)
            self._save_and_reload(run)

    def _set_candidate_authorization_gate(self, candidate_id: str, gate_id: str, state: str) -> None:
        run = self.active_trading_run
        if run is not None:
            run.set_candidate_authorization_gate(candidate_id, gate_id, state)
            self._save_and_reload(run)

    def _set_live_entry_condition(self, criterion_id: str, satisfied: bool) -> None:
        run = self.active_trading_run
        if run is None:
            return
        valid_ids = {criterion.id for criterion in self.live_watch_policy.entry_criteria}
        if criterion_id in valid_ids:
            run.set_entry_condition(criterion_id, satisfied)
            self._save_and_reload(run)

    def _set_live_watch_point_state(self, watch_point_id: str, state: str) -> None:
        run = self.active_trading_run
        if run is None:
            return
        valid_ids = {item.id for item in self.runtime.tda_station_runner_widget.session.watch_points}
        if watch_point_id in valid_ids:
            run.set_watch_point_state(watch_point_id, state)
            self._save_and_reload(run)

    def _set_candidate_entry_condition(self, candidate_id: str, criterion_id: str, satisfied: bool) -> None:
        run = self.active_trading_run
        if run is not None:
            run.set_candidate_entry_condition(candidate_id, criterion_id, satisfied)
            self._save_and_reload(run)

    def _set_candidate_watch_point_state(self, candidate_id: str, watch_point_id: str, state: str) -> None:
        run = self.active_trading_run
        if run is None:
            return
        candidate = run.setup_candidate_by_id(candidate_id)
        if candidate is None:
            return
        run.set_candidate_watch_point_state(candidate_id, watch_point_id, state)
        if candidate.source_type == "Custom":
            run.set_watch_point_state(watch_point_id, state)
        self._save_and_reload(run)

    def _save_and_reload(self, run: TradingRun) -> None:
        self.session_run_changed.emit(run)
        self.runtime.load_trading_run(run)
        self._update_view()

    def _update_interpretation_outcome(self, interpretation_outcome: str) -> None:
        run = self.active_trading_run
        if run is not None:
            run.update_post_market_review(interpretation_outcome=interpretation_outcome)
            self._save_and_reload(run)

    def _update_post_market_review(self, process_adherence: str, takeaway: str, film_night: bool) -> None:
        run = self.active_trading_run
        if run is not None:
            run.update_post_market_review(process_adherence=process_adherence, takeaway=takeaway, film_night=film_night)
            self._save_and_reload(run)

    def _process_session_changed(self, process_session: TradingDaySession) -> None:
        if self.active_trading_run is None or process_session.id != self.active_trading_run.process_session_id:
            return
        if process_session.status is TradingDayStatus.COMPLETE:
            self._conclude_active_trading_run(process_session.day_outcome)
        else:
            self._update_view()

    def _conclude_active_trading_run(self, outcome: str = "") -> None:
        run = self.active_trading_run
        if run is None:
            return
        self.trading_day.conclude_session_run(run, outcome)
        self.active_trading_run = None
        self._sync_legacy_aliases()
        self.session_run_changed.emit(run)
        self.trading_day_changed.emit(self.trading_day)
        self._update_view()

    def complete_trading_day(self) -> bool:
        if self.active_trading_run is not None or self.trading_day.status is TradingDayLifecycleStatus.COMPLETE:
            return False
        self.trading_day.complete()
        self.trading_day_changed.emit(self.trading_day)
        self._update_view()
        return True

    def start_new_trading_day(self) -> None:
        if self.active_trading_run is not None:
            return
        self.trading_day = TradingDay()
        self.trading_runs = []
        self.active_trading_run = None
        self._sync_legacy_aliases()
        self.trading_day_changed.emit(self.trading_day)
        self._update_view()
        self.ensure_primary_trading_run_started()

    def load_state(self, trading_day: TradingDay, session_runs: list[TradingRun], *, process_session: TradingDaySession | None = None, tda_session=None) -> None:
        self.trading_day = trading_day
        self.trading_runs = list(session_runs)
        self.active_trading_run = next(
            (run for run in self.trading_runs if run.id == trading_day.active_session_run_id and run.status is TradingRunStatus.ACTIVE),
            None,
        )
        self._sync_legacy_aliases()
        if self.active_trading_run is not None:
            if process_session is not None:
                self.runtime.load_session(process_session)
            if tda_session is not None:
                self.runtime.tda_station_runner_widget.load_session(tda_session)
            self.runtime.load_trading_run(self.active_trading_run)
        self._update_view()

    def _refresh_history(self) -> None:
        self.run_history.clear()
        for run in self.trading_runs:
            state = "▶ ACTIVE" if run.status is TradingRunStatus.ACTIVE else "✓ CONCLUDED"
            environment = f" · {run.environment.value}" if run.environment is not RunEnvironment.LIVE else ""
            model_count = len([item for item in run.setup_candidates if item.source_type == "Playbook"])
            models = f" · {model_count} model(s)" if model_count else ""
            outcome = f" · {run.outcome}" if run.outcome else ""
            self.run_history.addItem(f"{state} · {run.run_label}{environment}{models}{outcome}")

    def _sync_tda_nav(self) -> None:
        runner = self.runtime.tda_station_runner_widget
        index = runner.current_station_index
        observation = runner.session.observation_for(runner.current_station_id)
        last_index = len(runner.session.station_ids) - 1
        self.tda_back_button.setEnabled(index > 0)
        if observation.completed:
            self.tda_next_button.setText("Station Complete")
            self.tda_next_button.setEnabled(False)
        elif index == last_index:
            self.tda_next_button.setText("Mark Final Station Complete")
            self.tda_next_button.setEnabled(True)
        else:
            self.tda_next_button.setText("Mark Station Complete & Continue →")
            self.tda_next_button.setEnabled(True)

    def _update_view(self) -> None:
        self._refresh_history()
        day_complete = self.trading_day.status is TradingDayLifecycleStatus.COMPLETE
        if day_complete:
            self.summary_label.setText(f"Trading day complete · {len(self.trading_runs)} Trading Run(s) recorded")
        elif self.active_trading_run is not None:
            self.summary_label.setText(f"Trading day active · {self.active_trading_run.run_label} active · {len(self.trading_runs)} total run(s)")
        else:
            self.summary_label.setText(f"Trading day active · No Trading Run active · {len(self.trading_runs)} concluded run(s)")
        self.resume_context_label.setText(self._resume_context_text())
        self._refresh_market_time_display()

        active = self.active_trading_run is not None
        self.runtime_scroll.setVisible(active)
        self.runtime.transition_frame.setVisible(active)
        self.title_label.setVisible(not active)
        self.summary_label.setVisible(not active)
        runner = self.runtime.tda_station_runner_widget
        tda_focus_active = active and self.runtime.current_mode.id == "tda" and runner.view_tabs.currentWidget() is runner.focus_page
        self.tda_nav_frame.setVisible(tda_focus_active)
        self._sync_tda_nav()
        self.runtime_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff if tda_focus_active else Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.run_history_label.setVisible(not active)
        self.run_history.setVisible(not active)
        can_start_another = not day_complete and self.active_trading_run is None and bool(self.trading_runs)
        self.start_run_button.setVisible(can_start_another)
        self.start_run_button.setEnabled(can_start_another)
        self.start_run_button.setText("Start Another Trading Run")
        self.complete_day_button.setVisible(not active)
        self.complete_day_button.setEnabled(not day_complete and self.active_trading_run is None)
        self.start_new_day_button.setVisible(day_complete)
        self.start_new_day_button.setEnabled(day_complete)
        self.complete_day_button.setText("Trading Day Complete" if day_complete else "Complete Trading Day")
