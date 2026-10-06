from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


class ProcessRunLauncherWidget(QWidget):
    """Small doorway into the shared TDA -> Watch -> Review runtime.

    The launcher chooses provenance only. It does not create a Lab-specific
    process definition; Replay, Historical Backtest, Forward Test, and Live all
    execute the same runtime owned by the active Trade Plan.
    """

    def __init__(
        self,
        trading_day_shell: TradingDayShellWidget,
        *,
        trade_plan_revision: str,
        on_launched=None,
    ) -> None:
        super().__init__()
        self.trading_day_shell = trading_day_shell
        self.trade_plan_revision = trade_plan_revision.strip()
        self.on_launched = on_launched

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(10, 8, 10, 8)
        frame_layout.setSpacing(6)

        heading = QLabel("New Process Run")
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        frame_layout.addWidget(heading)

        description = QLabel(
            "Use the same Trade Plan and operating process in Live, Replay, Historical Backtest, or Forward Test. "
            "Only the run environment changes; TDA, Watch, authorization, and Review remain the same."
        )
        description.setWordWrap(True)
        frame_layout.addWidget(description)

        environment_row = QHBoxLayout()
        environment_row.addWidget(QLabel("Environment"))
        self.environment_combo = QComboBox()
        for environment in (
            RunEnvironment.REPLAY,
            RunEnvironment.HISTORICAL_BACKTEST,
            RunEnvironment.FORWARD_TEST,
            RunEnvironment.LIVE,
        ):
            self.environment_combo.addItem(environment.value, environment.value)
        environment_row.addWidget(self.environment_combo, 1)
        frame_layout.addLayout(environment_row)

        plan_row = QHBoxLayout()
        plan_row.addWidget(QLabel("Trade Plan"))
        self.trade_plan_label = QLabel(self.trade_plan_revision or "Not identified")
        self.trade_plan_label.setStyleSheet("font-weight: 600;")
        plan_row.addWidget(self.trade_plan_label, 1)
        frame_layout.addLayout(plan_row)

        self.begin_button = QPushButton("Begin Process Run")
        self.begin_button.clicked.connect(self.begin_process_run)
        frame_layout.addWidget(self.begin_button)

        self.status_label = QLabel(
            "No separate Lab workflow is created; this opens the normal Process runtime with study provenance attached."
        )
        self.status_label.setWordWrap(True)
        frame_layout.addWidget(self.status_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(frame)

    @property
    def selected_environment(self) -> RunEnvironment:
        return RunEnvironment(self.environment_combo.currentData())

    def begin_process_run(self) -> bool:
        shell = self.trading_day_shell
        if shell.active_trading_run is not None:
            self.status_label.setText(
                "An active Process Run already exists. Conclude it before starting another environment."
            )
            return False

        environment = self.selected_environment
        shell.run_environment = environment
        shell.start_new_trading_day()

        run = shell.active_trading_run
        if run is None:
            self.status_label.setText("The Process Run could not be started.")
            return False

        self.status_label.setText(
            f"Started {environment.value} · {run.run_label} · Trade Plan {run.trade_plan_revision or self.trade_plan_revision}."
        )
        if self.on_launched is not None:
            self.on_launched()
        return True
