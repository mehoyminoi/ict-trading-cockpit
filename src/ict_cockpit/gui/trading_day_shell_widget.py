from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
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
    TradingRun,
    TradingRunStatus,
)
from ict_cockpit.gui.trading_day_runtime_widget import TradingDayRuntimeWidget
from ict_cockpit.process_blueprint import ProcessBlueprint


class TradingDayShellWidget(QWidget):
    """Own one or more Trading Runs under a Trading Day."""

    trading_day_changed = Signal(object)
    session_run_changed = Signal(object)  # Backward-compatible signal name.

    def __init__(self, blueprint: ProcessBlueprint) -> None:
        super().__init__()
        self.blueprint = blueprint
        self.trading_day = TradingDay()
        self.trading_runs: list[TradingRun] = []
        self.active_trading_run: TradingRun | None = None

        # Backward-compatible aliases while callers migrate to Trading Run terms.
        self.session_runs = self.trading_runs
        self.active_session_run = self.active_trading_run

        self.title_label = QLabel("Trading Day")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)

        self.run_history = QListWidget()
        self.run_history.setMaximumHeight(120)
        self.session_history = self.run_history

        self.start_run_button = QPushButton("Start Trading Run")
        self.start_run_button.clicked.connect(self.start_trading_run)
        self.start_session_button = self.start_run_button

        self.complete_day_button = QPushButton("Complete Trading Day")
        self.complete_day_button.clicked.connect(self.complete_trading_day)

        self.start_new_day_button = QPushButton("Start New Trading Day")
        self.start_new_day_button.clicked.connect(self.start_new_trading_day)

        controls = QHBoxLayout()
        controls.addWidget(self.start_run_button)
        controls.addStretch()
        controls.addWidget(self.complete_day_button)
        controls.addWidget(self.start_new_day_button)

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
        layout.addWidget(QLabel("Trading Runs"))
        layout.addWidget(self.run_history)
        layout.addLayout(controls)
        layout.addWidget(self.runtime_frame, 1)

        self._update_view()

    @property
    def feedback_record_id(self) -> str:
        if self.active_trading_run is not None:
            return self.runtime.feedback_record_id
        return self.trading_day.id

    def _sync_legacy_aliases(self) -> None:
        self.session_runs = self.trading_runs
        self.active_session_run = self.active_trading_run

    def ensure_primary_trading_run_started(self) -> bool:
        """Start Trading Run 1 automatically when a fresh day enters Run Trading Day."""
        if self.trading_day.status is TradingDayLifecycleStatus.COMPLETE:
            return False
        if self.active_trading_run is not None:
            return False
        if self.trading_runs:
            return False
        return self.start_trading_run()

    def start_trading_run(self) -> bool:
        if self.trading_day.status is TradingDayLifecycleStatus.COMPLETE:
            return False
        if self.active_trading_run is not None:
            return False

        self.runtime.start_new()
        run_number = len(self.trading_runs) + 1
        run = TradingRun(
            trading_day_id=self.trading_day.id,
            session_name=f"Trading Run {run_number}",
            process_session_id=self.runtime.session.id,
            tda_station_session_id=self.runtime.tda_station_runner_widget.session.id,
        )
        self.trading_day.activate_session_run(run)
        self.trading_runs.append(run)
        self.active_trading_run = run
        self._sync_legacy_aliases()

        self.trading_day_changed.emit(self.trading_day)
        self.session_run_changed.emit(run)
        self._update_view()
        return True

    # Compatibility helper for older tests/callers. The supplied market-session
    # label is intentionally ignored: market sessions are context inside a run.
    def start_session_run(self, _session_name: str = "") -> bool:
        return self.start_trading_run()

    def _process_session_changed(self, process_session: TradingDaySession) -> None:
        if self.active_trading_run is None:
            return
        if process_session.id != self.active_trading_run.process_session_id:
            return
        if process_session.status is TradingDayStatus.COMPLETE:
            self._conclude_active_trading_run(process_session.day_outcome)

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
        if self.active_trading_run is not None:
            return False
        if self.trading_day.status is TradingDayLifecycleStatus.COMPLETE:
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
        self.runtime.start_new()
        self.trading_day_changed.emit(self.trading_day)
        self._update_view()

    def load_state(
        self,
        trading_day: TradingDay,
        session_runs: list[TradingRun],
        *,
        process_session: TradingDaySession | None = None,
        tda_session=None,
    ) -> None:
        self.trading_day = trading_day
        self.trading_runs = list(session_runs)
        self.active_trading_run = next(
            (
                run
                for run in self.trading_runs
                if run.id == trading_day.active_session_run_id
                and run.status is TradingRunStatus.ACTIVE
            ),
            None,
        )
        self._sync_legacy_aliases()

        if self.active_trading_run is not None:
            if process_session is not None:
                self.runtime.load_session(process_session)
            if tda_session is not None:
                self.runtime.tda_station_runner_widget.load_session(tda_session)

        self._update_view()

    def _refresh_history(self) -> None:
        self.run_history.clear()
        for run in self.trading_runs:
            if run.status is TradingRunStatus.ACTIVE:
                state = "▶ ACTIVE"
            else:
                state = "✓ CONCLUDED"
            outcome = f" · {run.outcome}" if run.outcome else ""
            self.run_history.addItem(f"{state} · {run.run_label}{outcome}")

    def _update_view(self) -> None:
        self._refresh_history()
        day_complete = self.trading_day.status is TradingDayLifecycleStatus.COMPLETE

        if day_complete:
            self.summary_label.setText(
                f"Trading day complete · {len(self.trading_runs)} Trading Run(s) recorded"
            )
        elif self.active_trading_run is not None:
            self.summary_label.setText(
                f"Trading day active · {self.active_trading_run.run_label} active · "
                f"{len(self.trading_runs)} total run(s)"
            )
        else:
            self.summary_label.setText(
                f"Trading day active · No Trading Run active · "
                f"{len(self.trading_runs)} concluded run(s)"
            )

        self.runtime_frame.setVisible(self.active_trading_run is not None)
        can_start_another = (
            not day_complete
            and self.active_trading_run is None
            and bool(self.trading_runs)
        )
        self.start_run_button.setVisible(can_start_another)
        self.start_run_button.setEnabled(can_start_another)
        self.start_run_button.setText("Start Another Trading Run")

        self.complete_day_button.setEnabled(
            not day_complete and self.active_trading_run is None
        )
        self.start_new_day_button.setVisible(day_complete)
        self.start_new_day_button.setEnabled(day_complete)

        if day_complete:
            self.complete_day_button.setText("Trading Day Complete")
        else:
            self.complete_day_button.setText("Complete Trading Day")
