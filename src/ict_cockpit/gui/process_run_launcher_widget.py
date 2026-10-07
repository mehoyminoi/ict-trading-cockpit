from datetime import datetime

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.environment_progression import (
    evaluate_environment_eligibility,
)
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, current_new_york_time
from ict_cockpit.analysis.trading_session_run import (
    RunEnvironment,
    default_purpose_for_environment,
)
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

        self.purpose_label = QLabel()
        self.purpose_label.setWordWrap(True)
        frame_layout.addWidget(self.purpose_label)

        self.eligibility_label = QLabel()
        self.eligibility_label.setWordWrap(True)
        self.eligibility_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.eligibility_label.setContentsMargins(8, 6, 8, 6)
        frame_layout.addWidget(self.eligibility_label)

        market_time_row = QHBoxLayout()
        self.market_time_label = QLabel("Replay market time · New York")
        self.market_time_edit = QDateTimeEdit()
        self.market_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.market_time_edit.setCalendarPopup(True)
        now_ny = current_new_york_time()
        self.market_time_edit.setDateTime(
            QDateTime.fromString(
                now_ny.strftime("%Y-%m-%d %H:%M"),
                "yyyy-MM-dd HH:mm",
            )
        )
        market_time_row.addWidget(self.market_time_label)
        market_time_row.addWidget(self.market_time_edit, 1)
        frame_layout.addLayout(market_time_row)
        self.environment_combo.currentTextChanged.connect(
            lambda _text: self._sync_environment_ui()
        )

        self.study_frame = QFrame()
        self.study_frame.setFrameShape(QFrame.Shape.StyledPanel)
        study_layout = QVBoxLayout(self.study_frame)
        study_layout.setContentsMargins(8, 6, 8, 6)
        study_layout.setSpacing(4)

        self.study_heading = QLabel("Run Intent")
        self.study_heading.setStyleSheet("font-weight: 600;")
        study_layout.addWidget(self.study_heading)

        self.study_question_input = QLineEdit()
        self.study_question_input.setPlaceholderText(
            "Focus / question — what are you trying to learn, rehearse, or validate?"
        )
        study_layout.addWidget(self.study_question_input)

        self.study_hypothesis_input = QLineEdit()
        self.study_hypothesis_input.setPlaceholderText(
            "Hypothesis (optional) — what do you expect to find?"
        )
        study_layout.addWidget(self.study_hypothesis_input)

        self.study_scope_input = QLineEdit()
        self.study_scope_input.setPlaceholderText(
            "Scope (optional) — setup, session, dates, conditions, or practice focus"
        )
        study_layout.addWidget(self.study_scope_input)

        study_note = QLabel(
            "Historical Backtest requires a focused study question. "
            "Replay and Forward Test may carry optional intent without becoming Lab work."
        )
        study_note.setWordWrap(True)
        study_layout.addWidget(study_note)
        frame_layout.addWidget(self.study_frame)

        plan_row = QHBoxLayout()
        plan_row.addWidget(QLabel("Trade Plan"))
        self.trade_plan_label = QLabel(self.trade_plan_revision or "Not identified")
        self.trade_plan_label.setStyleSheet("font-weight: 600;")
        plan_row.addWidget(self.trade_plan_label, 1)
        frame_layout.addLayout(plan_row)

        available_playbooks = [item for item in trading_day_shell.playbooks if item.available]
        models_row = QHBoxLayout()
        models_row.addWidget(QLabel("Reference models"))
        self.models_label = QLabel(
            f"{len(available_playbooks)} available from Trade Plan · selected during TDA"
        )
        self.models_label.setWordWrap(True)
        models_row.addWidget(self.models_label, 1)
        frame_layout.addLayout(models_row)

        model_guidance = QLabel(
            "Reference models are not auto-selected for Replay or Backtest runs. "
            "During Premarket Thesis, use Models in Play to mark whichever models the analysis says may apply. "
            "Selecting none is valid and leaves the technician/day-specific path available."
        )
        model_guidance.setWordWrap(True)
        model_guidance.setFrameShape(QFrame.Shape.StyledPanel)
        model_guidance.setContentsMargins(8, 6, 8, 6)
        frame_layout.addWidget(model_guidance)

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
        self._sync_environment_ui()

    def _sync_environment_ui(self) -> None:
        environment = self.selected_environment
        historical = environment in {
            RunEnvironment.REPLAY,
            RunEnvironment.HISTORICAL_BACKTEST,
        }
        self.market_time_label.setVisible(historical)
        self.market_time_edit.setVisible(historical)

        intent_visible = environment is not RunEnvironment.LIVE
        self.study_frame.setVisible(intent_visible)
        self.study_heading.setText(
            "Study Intent"
            if environment is RunEnvironment.HISTORICAL_BACKTEST
            else "Run Intent"
        )

        purpose = default_purpose_for_environment(environment)
        self.purpose_label.setText(
            f"Default purpose · {purpose.value}"
        )

        eligibility = evaluate_environment_eligibility(environment)
        detail = (
            f"Progression eligibility · {eligibility.status.value.upper()} · "
            f"{eligibility.detail}"
        )
        if eligibility.recommended_environment is not None:
            detail += (
                f" Recommended lower rung: "
                f"{eligibility.recommended_environment.value}."
            )
        self.eligibility_label.setText(detail)

    def _selected_historical_market_time(self) -> datetime:
        value = self.market_time_edit.dateTime()
        date_value = value.date()
        time_value = value.time()
        return datetime(
            date_value.year(),
            date_value.month(),
            date_value.day(),
            time_value.hour(),
            time_value.minute(),
            tzinfo=MARKET_TIMEZONE,
        )

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
        shell.run_purpose = default_purpose_for_environment(environment)

        question = self.study_question_input.text().strip()
        if (
            environment is RunEnvironment.HISTORICAL_BACKTEST
            and not question
        ):
            self.status_label.setText(
                "Add a focused study question before starting Historical Backtest."
            )
            return False

        if environment in {
            RunEnvironment.REPLAY,
            RunEnvironment.HISTORICAL_BACKTEST,
        }:
            shell.run_market_timestamp = self._selected_historical_market_time()
        else:
            shell.run_market_timestamp = None

        if environment is not RunEnvironment.LIVE and question:
            shell.run_study_context = {
                "question": question,
                "hypothesis": self.study_hypothesis_input.text().strip(),
                "scope": self.study_scope_input.text().strip(),
            }
        else:
            shell.run_study_context = {}
        shell.start_new_trading_day()

        run = shell.active_trading_run
        if run is None:
            self.status_label.setText("The Process Run could not be started.")
            return False

        available_count = len([item for item in shell.playbooks if item.available])
        self.status_label.setText(
            f"Started {environment.value} · {run.purpose.value} · {run.run_label} · Trade Plan "
            f"{run.trade_plan_revision or self.trade_plan_revision}. "
            f"{available_count} reference model(s) are available; none are auto-selected. "
            f"Market time source: {run.market_time_context.get('source', 'Not configured')}. "
            + (
                f"Study: {run.study_context.question}. "
                if run.study_context is not None
                else ""
            )
            + "Choose Models in Play during Premarket Thesis if the TDA says they apply."
        )
        if self.on_launched is not None:
            self.on_launched()
        return True
