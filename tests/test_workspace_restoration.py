from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.gui.main_window import MainWindow
from test_study_home import close


def open_window(path):
    connection = open_application_database(path)
    window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    return connection, window


def test_main_geometry_and_review_split_restore_without_run_or_database_writes(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path/'xdg'))
    path = tmp_path/'trial.db'
    connection, window = open_window(path)
    window.tabs.setCurrentWidget(window.study_find_review_widget)
    window.resize(700,600)
    window.move(35,45)
    window.show()
    QTest.qWait(30)
    splitter = window.study_find_review_widget.splitter
    splitter.setSizes([210,490])
    QTest.qWait(30)
    size = window.size()
    position = window.pos()
    sizes = splitter.sizes()
    ratio = sizes[0]/sum(sizes)
    changes = connection.total_changes
    close(window)
    assert connection.total_changes == changes
    connection.close()
    connection, restored = open_window(path)
    try:
        assert restored.tabs.currentWidget() is restored.study_home_widget
        restored.tabs.setCurrentWidget(restored.study_find_review_widget)
        restored.show()
        QTest.qWait(30)
        assert restored.size() == size
        assert (restored.pos()-position).manhattanLength() <= 4
        sizes = restored.study_find_review_widget.splitter.sizes()
        assert abs(sizes[0]/sum(sizes)-ratio) < .02
        assert restored.trade_plan_widget.trading_day_shell_widget.active_trading_run is None
    finally:
        close(restored)
        connection.close()


def test_bad_layout_settings_fall_back_without_changing_active_run(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path/'xdg'))
    connection, window = open_window(tmp_path/'trial.db')
    shell = window.trade_plan_widget.trading_day_shell_widget
    assert shell.start_trading_run()
    run_id = shell.active_trading_run.id
    close(window)
    window.workspace_settings.setValue('workspace-window/geometry-v1','invalid geometry')
    window.workspace_settings.setValue('study-review/splitter-v1','invalid split')
    window.workspace_settings.sync()
    restored = MainWindow(TDARepository(connection),StudyFindRepository(connection))
    try:
        assert restored.tabs.currentWidget() is restored.trade_plan_widget
        assert restored.trade_plan_widget.trading_day_shell_widget.active_trading_run.id == run_id
        assert restored.size().width() == 1120
    finally:
        close(restored)
        connection.close()


def test_offscreen_saved_position_is_recovered_to_available_screen(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME',str(tmp_path/'xdg'))
    connection, window = open_window(tmp_path/'trial.db')
    window.resize(600,500)
    window.show()
    QTest.qWait(20)
    window.move(20000,20000)
    close(window)
    restored = MainWindow(TDARepository(connection),StudyFindRepository(connection))
    try:
        restored.show()
        QTest.qWait(20)
        assert restored.screen().availableGeometry().intersects(restored.frameGeometry())
    finally:
        close(restored)
        connection.close()
