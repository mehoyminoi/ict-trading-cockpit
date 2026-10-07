from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import (
    RunEnvironment,
    RunPurpose,
    StudyOutcome,
    StudyRunContext,
    TradingRun,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import (
    TradingDaySessionRepository,
)
from ict_cockpit.database.trading_session_run_repository import (
    TradingSessionRunRepository,
)
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_historical_backtest_requires_explicit_study_question() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(
        RunEnvironment.HISTORICAL_BACKTEST.value
    )

    assert launcher.begin_process_run() is False
    assert "study question" in launcher.status_label.text().lower()
    assert widget.trading_day_shell_widget.active_trading_run is None


def test_replay_can_launch_without_study_question() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(RunEnvironment.REPLAY.value)

    assert launcher.begin_process_run() is True
    run = widget.trading_day_shell_widget.active_trading_run
    assert run is not None
    assert run.study_context is None


def test_replay_launcher_attaches_sparse_study_intent_to_run() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(RunEnvironment.REPLAY.value)
    launcher.study_question_input.setText(
        "Can I recognize the NYAM setup in real-time replay?"
    )
    launcher.study_hypothesis_input.setText(
        "I will recognize displacement before chasing the retracement."
    )
    launcher.study_scope_input.setText(
        "NYAM · Silver Bullet · deliberate recognition practice"
    )

    assert launcher.begin_process_run() is True

    run = widget.trading_day_shell_widget.active_trading_run
    assert run is not None
    assert run.study_context is not None
    assert run.purpose is RunPurpose.REHEARSAL
    assert run.study_context.question == (
        "Can I recognize the NYAM setup in real-time replay?"
    )
    assert run.study_context.hypothesis == (
        "I will recognize displacement before chasing the retracement."
    )
    assert run.study_context.scope == (
        "NYAM · Silver Bullet · deliberate recognition practice"
    )
    assert run.study_context.outcome is StudyOutcome.NOT_REVIEWED
    assert run.study_context.completed_at == ""


def test_live_run_does_not_require_or_create_study_context() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(RunEnvironment.LIVE.value)

    assert launcher.begin_process_run() is True
    run = widget.trading_day_shell_widget.active_trading_run
    assert run is not None
    assert run.study_context is None


def test_study_context_round_trips_with_trading_run(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    plan = build_default_trade_plan()
    day = TradingDay(futures_day_label="2026-10-07")
    process = TradingDaySession(
        blueprint_revision=plan.process_blueprint.revision,
        mode_ids=[mode.id for mode in plan.process_blueprint.modes],
        current_mode_id="tda",
    )
    study = StudyRunContext(
        question="Does the setup become obvious before the entry?",
        hypothesis="The displacement leg should be recognizable in real time.",
        scope="Replay · NYAM only",
    )
    study.record_outcome(
        StudyOutcome.REFINED,
        "I recognized displacement, but not the liquidity context soon enough.",
    )
    run = TradingRun(
        trading_day_id=day.id,
        session_name="Trading Run 1",
        process_session_id=process.id,
        environment=RunEnvironment.REPLAY,
        trade_plan_revision=plan.revision,
        study_context=study,
    )

    TradingDaySessionRepository(connection).save(process)
    day.activate_trading_run(run)
    TradingDayRepository(connection).save(day)
    repository = TradingSessionRunRepository(connection)
    repository.save(run)

    restored = repository.get_by_id(run.id)

    assert restored is not None
    assert restored.study_context is not None
    assert restored.purpose is RunPurpose.REHEARSAL
    assert restored.study_context.question == study.question
    assert restored.study_context.hypothesis == study.hypothesis
    assert restored.study_context.scope == study.scope
    assert restored.study_context.outcome is StudyOutcome.REFINED
    assert restored.study_context.outcome_note.startswith(
        "I recognized displacement"
    )
    assert restored.study_context.completed_at

    connection.close()


def test_study_review_is_visible_and_updates_active_run() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(RunEnvironment.REPLAY.value)
    launcher.study_question_input.setText(
        "Can I identify the setup without hindsight?"
    )
    assert launcher.begin_process_run() is True

    shell = widget.trading_day_shell_widget
    run = shell.active_trading_run
    assert run is not None
    assert run.study_context is not None

    review = shell.runtime.post_market_review_widget
    review.load_state(
        run,
        shell.runtime.tda_station_runner_widget.session,
    )

    assert review.study_review_frame.isHidden() is False
    assert "Can I identify the setup without hindsight?" in (
        review.study_question_label.text()
    )

    review.study_outcome_combo.setCurrentText(
        StudyOutcome.INCONCLUSIVE.value
    )
    review.study_outcome_note_input.setText(
        "Need another replay sample with a cleaner session."
    )
    review.study_outcome_note_input.editingFinished.emit()

    assert run.study_context.outcome is StudyOutcome.INCONCLUSIVE
    assert run.study_context.outcome_note == (
        "Need another replay sample with a cleaner session."
    )
    assert run.study_context.completed_at
