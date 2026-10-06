from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_runtime_keeps_process_actions_outside_scroll_viewport() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()

    assert shell.runtime.transition_frame.parent() is shell
    assert shell.runtime_scroll.horizontalScrollBarPolicy() == (
        Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert shell.runtime.transition_frame.isHidden() is False


def test_tda_navigation_is_anchored_outside_scrolling_content() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    runner = shell.runtime.tda_station_runner_widget

    assert runner.back_button.isHidden() is True
    assert runner.next_button.isHidden() is True
    assert shell.tda_nav_frame.isHidden() is False
    assert shell.tda_next_button.text() == runner.next_button.text()

    shell.tda_next_button.click()

    assert runner.current_station_index == 1
    assert shell.tda_back_button.isEnabled() is True


def test_resume_context_tracks_current_tda_station() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    shell.start_trading_run()
    runner = shell.runtime.tda_station_runner_widget

    assert "Trading Run 1" in shell.resume_context_label.text()
    assert "Premarket / TDA" in shell.resume_context_label.text()

    runner.go_next_station()

    assert "IPDA Premium / Discount" in shell.resume_context_label.text()


def test_main_window_restores_directly_to_active_runtime(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection)

    first = MainWindow(tda_repository, study_find_repository)
    first.tabs.setCurrentWidget(first.trade_plan_widget)
    first.trade_plan_widget.focus_runtime()
    first_runner = first.trade_plan_widget.tda_station_runner_widget
    first_runner.go_next_station()

    second = MainWindow(tda_repository, study_find_repository)

    assert second.tabs.currentWidget() is second.trade_plan_widget
    assert second.trade_plan_widget.selected_section_id == "process"
    assert second.trade_plan_widget.process_tabs.currentWidget() is (
        second.trade_plan_widget.trading_day_shell_widget
    )
    assert "Trading Run 1" in (
        second.trade_plan_widget.trading_day_shell_widget.resume_context_label.text()
    )
    assert "IPDA Premium / Discount" in (
        second.trade_plan_widget.trading_day_shell_widget.resume_context_label.text()
    )

    first.close()
    second.close()
    connection.close()
