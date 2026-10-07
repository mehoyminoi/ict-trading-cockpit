from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.environment_progression import (
    EnvironmentEligibilityStatus,
    evaluate_environment_eligibility,
)
from ict_cockpit.analysis.trading_session_run import (
    RunEnvironment,
    RunPurpose,
    default_purpose_for_environment,
)
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_environment_defaults_form_training_ladder() -> None:
    assert default_purpose_for_environment(
        RunEnvironment.HISTORICAL_BACKTEST
    ) is RunPurpose.STUDY
    assert default_purpose_for_environment(
        RunEnvironment.REPLAY
    ) is RunPurpose.REHEARSAL
    assert default_purpose_for_environment(
        RunEnvironment.FORWARD_TEST
    ) is RunPurpose.VALIDATION
    assert default_purpose_for_environment(
        RunEnvironment.LIVE
    ) is RunPurpose.EXECUTION


def test_foundation_study_environment_is_available_without_progression_policy() -> None:
    result = evaluate_environment_eligibility(
        RunEnvironment.HISTORICAL_BACKTEST
    )

    assert result.status is EnvironmentEligibilityStatus.AVAILABLE
    assert result.can_launch is True
    assert result.recommended_environment is None


def test_higher_rungs_are_explicitly_unknown_until_trade_plan_configures_them() -> None:
    replay = evaluate_environment_eligibility(RunEnvironment.REPLAY)
    forward = evaluate_environment_eligibility(
        RunEnvironment.FORWARD_TEST
    )
    live = evaluate_environment_eligibility(RunEnvironment.LIVE)

    assert replay.status is EnvironmentEligibilityStatus.NOT_CONFIGURED
    assert replay.recommended_environment is RunEnvironment.HISTORICAL_BACKTEST
    assert forward.status is EnvironmentEligibilityStatus.NOT_CONFIGURED
    assert forward.recommended_environment is RunEnvironment.REPLAY
    assert live.status is EnvironmentEligibilityStatus.NOT_CONFIGURED
    assert live.recommended_environment is RunEnvironment.FORWARD_TEST

    assert replay.can_launch is True
    assert forward.can_launch is True
    assert live.can_launch is True


def test_launcher_surfaces_environment_purpose_and_unconfigured_progression_state() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(RunEnvironment.LIVE.value)

    assert launcher.purpose_label.text() == "Default purpose · Execution"
    assert "NOT CONFIGURED" in launcher.eligibility_label.text()
    assert "Forward Test" in launcher.eligibility_label.text()

    launcher.environment_combo.setCurrentText(
        RunEnvironment.HISTORICAL_BACKTEST.value
    )

    assert launcher.purpose_label.text() == "Default purpose · Study"
    assert "AVAILABLE" in launcher.eligibility_label.text()
    assert launcher.study_heading.text() == "Study Intent"


def test_replay_run_persists_rehearsal_purpose_even_without_study_intent() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(RunEnvironment.REPLAY.value)
    assert launcher.begin_process_run() is True

    run = widget.trading_day_shell_widget.active_trading_run
    assert run is not None
    assert run.environment is RunEnvironment.REPLAY
    assert run.purpose is RunPurpose.REHEARSAL
    assert run.study_context is None
