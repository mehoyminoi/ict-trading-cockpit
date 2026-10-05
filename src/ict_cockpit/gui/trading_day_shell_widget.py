from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.trading_day import TradingDay, TradingDayLifecycleStatus
from ict_cockpit.analysis.trading_day_session import TradingDaySession, TradingDayStatus
from ict_cockpit.analysis.trading_session_run import (
    SESSION_NAMES,
    TradingSessionRun,
    TradingSessionRunStatus,
)
from ict_cockpit.gui.trading_day_runtime_widget import TradingDayRuntimeWidget
from ict_cockpit.process_blueprint import ProcessBlueprint


class TradingDayShellWidget(QWidget):
    """Own Session Runs under one Trading Day and host the active process runtime."""

    trading_day_changed = Signal(object)
    session_run_changed = Signal(object)

    def __init__(self, blueprint: ProcessBlueprint) -> None:
        super().__init__()
        self.blueprint = blueprint
        self.trading_day = TradingDay()
        self.session_runs: list[TradingSessionRun] = []
        self.active_session_run: TradingSessionRun | None = None

        self.title_label = QLabel("Trading Day")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)

        self.session_history = QListWidget()
        self.session_history.setMaximumHeight(120)

        self.session_selector = QComboBox()
        self.session_selector.addItems(SESSION_NAMES)
        self.start_session_button = QPushButton("Start Session Run")
        self.start_session_button.clicked.connect(self.start_selected_session)
        self.complete_day_button = QPushButton("Complete Trading Day")
        self.complete_day_button.clicked.connect(self.complete_trading_day)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Session"))
        controls.addWidget(self.session_selector)
        controls.addWidget(self.start_session_button)
        controls.addStretch()
        controls.addWidget(self.complete_day_button)

        self.runtime_frame = QFrame()
        self.runtime_frame.setFrameShape(QFrame.Shape.StyledPanel)
        runtime_layout = QVBoxLayout(self.runtime_frame)
        self.runtime = TradingDayRuntimeWidget(
            blueprint,
            embedded_session_run=True,
        )
        runtime_layout.addWidget(self.runtime)
        self.runtime.session_changed.connect(self._process_session_changed)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.summary_label)
        layout.addWidget(QLabel("Session Runs"))
        layout.addWidget(self.session_history)
        layout.addLayout(controls)
        layout.addWidget(self.runtime_frame, 1)

        self._update_view()

    @property
    def feedback_record_id(self) -> str:
        if self.active_session_run is not None:
            return self.runtime.feedback_record_id
        return self.trading_day.id

    def start_selected_session(self) -> None:
        self.start_session_run(self.session_selector.currentText())

    def start_session_run(self, session_name: str) -> bool:
        if self.trading_day.status is TradingDayLifecycleStatus.COMPLETE:
            return False
        if self.active_session_run is not None:
            return False

        self.runtime.start_new()
        run = TradingSessionRun(
            trading_day_id=self.trading_day.id,
            session_name=session_name,
            process_session_id=self.runtime.session.id,
            tda_station_session_id=self.runtime.tda_station_runner_widget.session.id,
        )
        self.trading_day.activate_session_run(run)
        self.session_runs.append(run)
        self.active_session_run = run

        self.trading_day_changed.emit(self.trading_day)
        self.session_run_changed.emit(run)
        self._update_view()
        return True

    def _process_session_changed(self, process_session: TradingDaySession) -> None:
        if self.active_session_run is None:
            return
        if process_session.id != self.active_session_run.process_session_id:
            return
        if process_session.status is TradingDayStatus.COMPLETE:
            self._conclude_active_session_run(process_session.day_outcome)

    def _conclude_active_session_run(self, outcome: str = "") -> None:
        run = self.active_session_run
        if run is None:
            return
        self.trading_day.conclude_session_run(run, outcome)
        self.active_session_run = None
        self.session_run_changed.emit(run)
        self.trading_day_changed.emit(self.trading_day)
        self._update_view()

    def complete_trading_day(self) -> bool:
        if self.active_session_run is not None:
            return False
        if self.trading_day.status is TradingDayLifecycleStatus.COMPLETE:
            return False
        self.trading_day.complete()
        self.trading_day_changed.emit(self.trading_day)
        self._update_view()
        return True

    def start_new_trading_day(self) -> None:
        if self.active_session_run is not None:
            return
        self.trading_day = TradingDay()
        self.session_runs = []
        self.active_session_run = None
        self.runtime.start_new()
        self.trading_day_changed.emit(self.trading_day)
        self._update_view()

    def load_state(
        self,
        trading_day: TradingDay,
        session_runs: list[TradingSessionRun],
        *,
        process_session: TradingDaySession | None = None,
        tda_session=None,
    ) -> None:
        self.trading_day = trading_day
        self.session_runs = list(session_runs)
        self.active_session_run = next(
            (
                run
                for run in self.session_runs
                if run.id == trading_day.active_session_run_id
                and run.status is TradingSessionRunStatus.ACTIVE
            ),
            None,
        )

        if self.active_session_run is not None:
            if process_session is not None:
                self.runtime.load_session(process_session)
            if tda_session is not None:
                self.runtime.tda_station_runner_widget.load_session(tda_session)

        self._update_view()

    def _refresh_history(self) -> None:
        self.session_history.clear()
        for run in self.session_runs:
            if run.status is TradingSessionRunStatus.ACTIVE:
                state = "▶ ACTIVE"
            else:
                state = "✓ CONCLUDED"
            outcome = f" · {run.outcome}" if run.outcome else ""
            self.session_history.addItem(f"{state} · {run.session_name}{outcome}")

    def _update_view(self) -> None:
        self._refresh_history()
        day_complete = self.trading_day.status is TradingDayLifecycleStatus.COMPLETE

        if day_complete:
            self.summary_label.setText(
                f"Trading day complete · {len(self.session_runs)} Session Run(s) recorded"
            )
        elif self.active_session_run is not None:
            self.summary_label.setText(
                f"Trading day active · {self.active_session_run.session_name} Session Run active · "
                f"{len(self.session_runs)} total run(s)"
            )
        else:
            self.summary_label.setText(
                f"Trading day active · No Session Run active · {len(self.session_runs)} concluded run(s)"
            )

        self.runtime_frame.setVisible(self.active_session_run is not None)
        self.session_selector.setEnabled(not day_complete and self.active_session_run is None)
        self.start_session_button.setEnabled(
            not day_complete and self.active_session_run is None
        )
        self.complete_day_button.setEnabled(
            not day_complete and self.active_session_run is None
        )

        if day_complete:
            self.complete_day_button.setText("Trading Day Complete")
        else:
            self.complete_day_button.setText("Complete Trading Day")
