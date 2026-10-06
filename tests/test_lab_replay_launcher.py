from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_replay_launcher_enters_same_process_runtime() -> None:
    get_app()
    plan = build_default_trade_plan()
    widget = TradePlanWidget(plan)
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(RunEnvironment.REPLAY.value)
    assert launcher.begin_process_run() is True

    shell = widget.trading_day_shell_widget
    run = shell.active_trading_run
    assert run is not None
    assert run.environment is RunEnvironment.REPLAY
    assert run.trade_plan_revision == plan.revision
    assert [mode.id for mode in shell.runtime.modes] == [
        "tda",
        "live-watch",
        "post-market",
    ]
    assert shell.runtime.current_mode.id == "tda"
    assert widget.selected_section_id == "process"
    assert widget.process_tabs.currentWidget() is shell
    assert "Replay" in shell.resume_context_label.text()


def test_launcher_exposes_model_library_without_auto_selecting_models() -> None:
    get_app()
    plan = build_default_trade_plan()
    widget = TradePlanWidget(plan)
    launcher = widget.process_run_launcher_widget

    available_count = len([item for item in plan.playbooks if item.available])
    assert f"{available_count} available" in launcher.models_label.text()
    assert "selected during TDA" in launcher.models_label.text()

    launcher.environment_combo.setCurrentText(RunEnvironment.REPLAY.value)
    assert launcher.begin_process_run() is True

    run = widget.trading_day_shell_widget.active_trading_run
    assert run is not None
    assert [
        item for item in run.setup_candidates if item.source_type == "Playbook"
    ] == []
    assert "none are auto-selected" in launcher.status_label.text()
    assert "Premarket Thesis" in launcher.status_label.text()

    editor = widget.trading_day_runtime_widget.tda_watch_point_widget
    assert editor.models_list.count() == len(plan.playbooks)


def test_launcher_refuses_competing_active_process_run() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    shell = widget.trading_day_shell_widget
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(RunEnvironment.REPLAY.value)
    assert launcher.begin_process_run() is True
    first_run = shell.active_trading_run
    assert first_run is not None

    launcher.environment_combo.setCurrentText(RunEnvironment.HISTORICAL_BACKTEST.value)
    assert launcher.begin_process_run() is False

    assert shell.active_trading_run is first_run
    assert shell.active_trading_run.environment is RunEnvironment.REPLAY
    assert "active Process Run already exists" in launcher.status_label.text()


def test_live_environment_is_available_from_same_launcher() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(RunEnvironment.LIVE.value)
    assert launcher.begin_process_run() is True

    run = widget.trading_day_shell_widget.active_trading_run
    assert run is not None
    assert run.environment is RunEnvironment.LIVE
