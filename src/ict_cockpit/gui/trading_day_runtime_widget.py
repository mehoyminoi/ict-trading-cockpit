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

from ict_cockpit.analysis.trading_day_session import TradingDaySession, TradingDayStatus, TransitionOutcome
from ict_cockpit.analysis.trading_session_run import TradingRun
from ict_cockpit.gui.live_watch_widget import LiveWatchWidget
from ict_cockpit.gui.post_market_review_widget import PostMarketReviewWidget
from ict_cockpit.gui.qt_context_widget import QTContextWidget
from ict_cockpit.gui.tda_station_runner_widget import TDAStationRunnerWidget
from ict_cockpit.gui.tda_watch_point_widget import TDAWatchPointWidget
from ict_cockpit.process_blueprint import ModeDefinition, ProcessBlueprint
from ict_cockpit.trade_plan import LiveWatchPolicyDefinition, PlaybookDefinition


class TradingDayRuntimeWidget(QWidget):
    """Runtime shell for deliberate movement through process modes."""

    session_changed = Signal(TradingDaySession)
    models_in_play_changed = Signal(object)
    qt_context_changed = Signal(object)
    playbook_selected = Signal(str)  # compatibility
    live_observation_submitted = Signal(str)
    live_thesis_state_submitted = Signal(str, str)
    live_entry_condition_changed = Signal(str, bool)
    live_watch_point_state_changed = Signal(str, str)
    live_candidate_entry_condition_changed = Signal(str, str, bool)
    live_candidate_watch_point_state_changed = Signal(str, str, str)
    post_market_interpretation_submitted = Signal(str)
    post_market_review_submitted = Signal(str, str, bool)
    post_market_study_review_submitted = Signal(str, str)
    post_market_observed_qt_submitted = Signal(object, str)

    def __init__(
        self,
        blueprint: ProcessBlueprint,
        *,
        embedded_session_run: bool = False,
        live_watch_policy: LiveWatchPolicyDefinition | None = None,
        playbooks: tuple[PlaybookDefinition, ...] = (),
    ) -> None:
        super().__init__()
        self.blueprint = blueprint
        self.live_watch_policy = live_watch_policy or LiveWatchPolicyDefinition()
        self.playbooks = tuple(playbooks)
        self.embedded_session_run = embedded_session_run
        self.modes = list(blueprint.modes)
        if not self.modes:
            raise ValueError("blueprint must contain trading-day modes")

        self.session = self._new_session()
        self.trading_run: TradingRun | None = None

        title = "Trading Run Process" if embedded_session_run else "Trading Day Session"
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 17px; font-weight: 600;")
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)

        self.mode_rail = QHBoxLayout()
        self.mode_rail.setContentsMargins(0, 0, 0, 0)
        self.mode_rail.setSpacing(5)
        self.mode_labels: dict[str, QLabel] = {}
        for mode in self.modes:
            label = QLabel()
            label.setFrameShape(QFrame.Shape.StyledPanel)
            label.setContentsMargins(6, 4, 6, 4)
            self.mode_labels[mode.id] = label
            self.mode_rail.addWidget(label, 1)

        self.mode_stack = QStackedWidget()
        self.mode_pages: dict[str, QWidget] = {}

        self.tda_station_runner_widget = TDAStationRunnerWidget(blueprint)
        self.qt_context_widget = QTContextWidget()
        self.qt_context_widget.context_changed.connect(self.qt_context_changed.emit)
        self.tda_watch_point_widget = TDAWatchPointWidget(self.playbooks)
        self.tda_watch_point_widget.add_requested.connect(self._add_tda_watch_point)
        self.tda_watch_point_widget.remove_requested.connect(self._remove_tda_watch_point)
        self.tda_watch_point_widget.models_in_play_changed.connect(self.models_in_play_changed.emit)
        self.tda_watch_point_widget.playbook_selected.connect(self.playbook_selected.emit)
        self.tda_station_runner_widget.session_changed.connect(lambda _session: self._refresh_tda_watch_point_editor())
        self.tda_station_runner_widget.view_tabs.currentChanged.connect(lambda _index: self._refresh_tda_watch_point_editor())

        self.live_watch_widget = LiveWatchWidget(self.live_watch_policy)
        self.live_watch_widget.observation_submitted.connect(self.live_observation_submitted.emit)
        self.live_watch_widget.thesis_state_submitted.connect(self.live_thesis_state_submitted.emit)
        self.live_watch_widget.entry_condition_changed.connect(self.live_entry_condition_changed.emit)
        self.live_watch_widget.watch_point_state_changed.connect(self.live_watch_point_state_changed.emit)
        self.live_watch_widget.candidate_entry_condition_changed.connect(self.live_candidate_entry_condition_changed.emit)
        self.live_watch_widget.candidate_watch_point_state_changed.connect(self.live_candidate_watch_point_state_changed.emit)

        self.post_market_review_widget = PostMarketReviewWidget(blueprint)
        self.post_market_review_widget.interpretation_changed.connect(self.post_market_interpretation_submitted.emit)
        self.post_market_review_widget.review_changed.connect(self.post_market_review_submitted.emit)
        self.post_market_review_widget.study_review_changed.connect(
            self.post_market_study_review_submitted.emit
        )
        self.post_market_review_widget.observed_qt_changed.connect(
            self.post_market_observed_qt_submitted.emit
        )

        for mode in self.modes:
            if mode.id == "tda":
                page = self.tda_station_runner_widget
            elif mode.id == "live-watch":
                page = self.live_watch_widget
            elif mode.id == "post-market":
                page = self.post_market_review_widget
            else:
                page = self._build_placeholder_mode_page(mode)
            self.mode_pages[mode.id] = page
            self.mode_stack.addWidget(page)

        self.transition_frame = QFrame()
        self.transition_frame.setFrameShape(QFrame.Shape.StyledPanel)
        transition_layout = QVBoxLayout(self.transition_frame)
        transition_layout.setContentsMargins(8, 5, 8, 5)
        transition_layout.setSpacing(4)
        transition_heading = QLabel("Process Actions")
        transition_heading.setStyleSheet("font-weight: 600;")
        transition_layout.addWidget(transition_heading)
        self.transition_note_input = QLineEdit()
        self.transition_note_input.setPlaceholderText("Decision note / reason (optional)")
        transition_layout.addWidget(self.transition_note_input)
        self.transition_buttons_layout = QHBoxLayout()
        self.transition_buttons_layout.setContentsMargins(0, 0, 0, 0)
        transition_layout.addLayout(self.transition_buttons_layout)
        self.transition_buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(5)
        layout.addWidget(self.title_label)
        layout.addWidget(self.summary_label)
        layout.addLayout(self.mode_rail)
        # Premarket Thesis QT/model/watch-point decisions are station-critical work.
        # Keep them above the Focus viewport so they cannot be hidden below the
        # scroll boundary on compact displays.
        layout.addWidget(self.qt_context_widget)
        layout.addWidget(self.tda_watch_point_widget)
        layout.addWidget(self.mode_stack, 1)
        layout.addWidget(self.transition_frame)

        if self.embedded_session_run:
            self.title_label.hide()
            self.summary_label.hide()
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
            item.station_id
            for item in self.tda_station_runner_widget.session.observations
            if not item.completed
        ]

    def _touch(self) -> None:
        self.session.updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
        self.session_changed.emit(self.session)

    def _touch_tda_session(self) -> None:
        runner = self.tda_station_runner_widget
        runner.session.updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
        runner.session_changed.emit(runner.session)

    def _add_tda_watch_point(self, if_condition: str, then_action: str) -> None:
        self.tda_station_runner_widget.session.add_watch_point(if_condition, then_action)
        self._touch_tda_session()
        self._refresh_tda_watch_point_editor()

    def _remove_tda_watch_point(self, watch_point_id: str) -> None:
        if self.tda_station_runner_widget.session.remove_watch_point(watch_point_id):
            self._touch_tda_session()
            self._refresh_tda_watch_point_editor()

    def _refresh_tda_watch_point_editor(self) -> None:
        runner = self.tda_station_runner_widget
        visible = (
            self.session.current_mode_id == "tda"
            and runner.current_station_id == "tda-thesis"
            and runner.view_tabs.currentWidget() is runner.focus_page
        )
        self.qt_context_widget.setVisible(visible)
        self.tda_watch_point_widget.setVisible(visible)
        if visible:
            selected_ids = []
            qt_context = {}
            market_time_context = {}
            if self.trading_run is not None:
                selected_ids = [
                    item.source_id
                    for item in self.trading_run.setup_candidates
                    if item.source_type == "Playbook"
                ]
                qt_context = self.trading_run.qt_context
                market_time_context = self.trading_run.market_time_context
            self.qt_context_widget.load_context(
                qt_context,
                market_time_context,
            )
            self.tda_watch_point_widget.load_context(selected_ids, runner.session.watch_points)

    def apply_transition(self, transition_id: str, *, reason: str = "", override_incomplete: bool = False) -> bool:
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
            self.session.return_to_analysis(transition.target_mode_id, reason=reason)
        elif transition.outcome == "stand_down":
            self.session.stand_down(transition.target_mode_id, reason=reason)
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
            message = QMessageBox(self)
            message.setIcon(QMessageBox.Icon.Warning)
            message.setWindowTitle("TDA is incomplete")
            message.setText(f"{len(self.incomplete_tda_station_ids)} TDA station(s) are still incomplete.")
            message.setInformativeText(
                "Return to the missing work, or intentionally file the TDA incomplete and continue to Live Watch."
            )
            return_button = message.addButton("Return to TDA", QMessageBox.ButtonRole.RejectRole)
            override_button = message.addButton("File Incomplete Anyway", QMessageBox.ButtonRole.AcceptRole)
            message.exec()
            if message.clickedButton() is not override_button:
                if message.clickedButton() is return_button:
                    self._focus_first_incomplete_tda_station()
                return
            self.apply_transition(transition_id, reason=reason, override_incomplete=True)
            return
        self.apply_transition(transition_id, reason=reason)

    def _focus_first_incomplete_tda_station(self) -> None:
        if self.incomplete_tda_station_ids:
            self.tda_station_runner_widget.open_station_from_deck(self.incomplete_tda_station_ids[0])

    def go_next_mode(self) -> None:
        for transition in self.current_mode.transitions:
            if transition.outcome == "advance":
                self.apply_transition(
                    transition.id,
                    override_incomplete=(self.session.current_mode_id == "tda"),
                )
                return

    def go_previous_mode(self) -> None:
        if self.session.current_mode_id == "live-watch":
            transition = self.current_mode.transition_by_id("live-return-analysis")
            if transition is not None:
                self.apply_transition(transition.id)

    def load_session(self, session: TradingDaySession) -> None:
        expected_ids = [mode.id for mode in self.modes]
        if session.blueprint_revision == self.blueprint.revision and session.mode_ids == expected_ids:
            self.session = session
            self._update_view()

    def load_trading_run(self, trading_run: TradingRun) -> None:
        self.trading_run = trading_run
        self.qt_context_widget.load_context(
            trading_run.qt_context,
            trading_run.market_time_context,
        )
        self.live_watch_widget.load_run_context(
            trading_run,
            self.tda_station_runner_widget.session,
            self.blueprint,
        )
        self.post_market_review_widget.load_state(
            trading_run,
            self.tda_station_runner_widget.session,
        )
        self._refresh_tda_watch_point_editor()

    def start_new(self) -> None:
        self.tda_station_runner_widget.start_new()
        self.qt_context_widget.clear_context()
        self.live_watch_widget.clear_state()
        self.post_market_review_widget.clear_state()
        self.trading_run = None
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
        note = QLabel("Runtime shell only — this mode is visible so the full trading-day loop can be tested before its stations become executable.")
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
            label = QLabel("✓ Trading Run process complete" if self.embedded_session_run else "✓ Trading day complete")
            self.transition_buttons_layout.addWidget(label)
            self.transition_buttons_layout.addStretch()
            self.transition_note_input.setEnabled(False)
            if not self.embedded_session_run:
                start_new_button = QPushButton("Start New Trading Day")
                start_new_button.clicked.connect(self.start_new)
                self.transition_buttons["start-new-day"] = start_new_button
                self.transition_buttons_layout.addWidget(start_new_button)
            return

        self.transition_note_input.setEnabled(True)
        for transition in self.current_mode.transitions:
            button_name = "Conclude Trading Run" if self.embedded_session_run and transition.id == "complete-day" else transition.name
            button = QPushButton(button_name)
            button.setToolTip(transition.description)
            button.clicked.connect(lambda _checked=False, transition_id=transition.id: self.request_transition(transition_id))
            self.transition_buttons[transition.id] = button
            self.transition_buttons_layout.addWidget(button)
        self.transition_buttons_layout.addStretch()

    def _update_view(self) -> None:
        current_index = self.session.current_mode_index
        current_mode = self.current_mode
        self.mode_stack.setCurrentWidget(self.mode_pages[current_mode.id])
        self._refresh_tda_watch_point_editor()

        if current_mode.id == "live-watch" and self.trading_run is not None:
            self.live_watch_widget.load_run_context(
                self.trading_run,
                self.tda_station_runner_widget.session,
                self.blueprint,
            )
        elif current_mode.id == "post-market" and self.trading_run is not None:
            self.post_market_review_widget.load_state(
                self.trading_run,
                self.tda_station_runner_widget.session,
            )

        if self.session.status is TradingDayStatus.COMPLETE:
            subject = "Trading Run process" if self.embedded_session_run else "Trading day"
            summary = f"{subject} complete · Outcome: {self.session.day_outcome or 'Complete'} · {len(self.session.transitions)} recorded transition(s)"
        else:
            summary = (
                f"Current mode: {current_mode.name} · "
                f"{len(self.session.completed_mode_ids)}/{len(self.modes)} modes concluded · "
                f"{len(self.session.transitions)} recorded transition(s)"
            )
        self.summary_label.setText(summary)

        for index, mode in enumerate(self.modes):
            if mode.id == self.session.current_mode_id and self.session.status is TradingDayStatus.ACTIVE:
                state = "▶"
            elif mode.id in self.session.completed_mode_ids:
                state = "✓"
            elif index < current_index:
                state = "↶"
            else:
                state = "○"
            self.mode_labels[mode.id].setText(f"{state} {mode.name}")
        self._rebuild_transition_buttons()