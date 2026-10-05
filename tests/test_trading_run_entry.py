from PySide6.QtWidgets import QApplication

from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_entering_run_trading_day_starts_primary_trading_run() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    shell = widget.trading_day_shell_widget

    assert shell.trading_runs == []
    assert shell.active_trading_run is None

    widget.process_tabs.setCurrentWidget(shell)

    assert len(shell.trading_runs) == 1
    assert shell.active_trading_run is shell.trading_runs[0]
    assert shell.active_trading_run.run_label == "Trading Run 1"
    assert shell.start_run_button.isVisible() is False


def test_second_run_is_presented_as_secondary_action_after_primary_concludes() -> None:
    get_app()
    widget = TradePlanWidget(build_default_trade_plan())
    shell = widget.trading_day_shell_widget
    widget.process_tabs.setCurrentWidget(shell)

    shell.runtime.apply_transition("tda-stand-down")
    shell.runtime.apply_transition("complete-day")

    assert shell.active_trading_run is None
    assert len(shell.trading_runs) == 1
    assert shell.start_run_button.text() == "Start Another Trading Run"
    assert shell.start_run_button.isEnabled() is True
