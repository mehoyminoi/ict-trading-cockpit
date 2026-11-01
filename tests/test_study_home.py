import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.competency import CompetencyDevelopmentDirection
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


def close(window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    QApplication.processEvents()


@pytest.fixture
def cockpit(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    connection = open_application_database(tmp_path / "study.db")
    window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    yield window, connection
    close(window)
    connection.close()


def test_idle_opens_study_and_staging_does_not_write_or_launch(cockpit):
    window, connection = cockpit
    home = window.study_home_widget
    assert window.tabs.currentWidget() is home
    assert "No recorded Study direction" in home.basis_label.text()
    assert not home.study_button.isEnabled()
    before = connection.total_changes
    home.competency_combo.setCurrentIndex(1)
    home.study_button.click()
    plan = window.trade_plan_widget
    assert window.tabs.currentWidget() is plan
    assert plan.competency_evidence_review_widget.work_tabs.currentWidget() is plan.competency_evidence_review_widget.practice_page
    assert plan.process_run_launcher_widget.environment_combo.currentText() == "Historical Backtest"
    assert plan.trading_day_shell_widget.active_trading_run is None
    assert connection.total_changes == before


def test_active_restart_restores_runtime_and_study_cannot_launch_over_it(cockpit):
    window, connection = cockpit
    shell = window.trade_plan_widget.trading_day_shell_widget
    assert shell.start_trading_run()
    run_id = shell.active_trading_run.id
    restored = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    try:
        assert restored.tabs.currentWidget() is restored.trade_plan_widget
        restored.tabs.setCurrentWidget(restored.study_home_widget)
        home = restored.study_home_widget
        home.competency_combo.setCurrentIndex(1)
        assert not home.study_button.isEnabled()
        restored._stage_home_study(home.competency_combo.currentData())
        home.resume_button.click()
        assert restored.tabs.currentWidget() is restored.trade_plan_widget
        assert restored.trade_plan_widget.trading_day_shell_widget.active_trading_run.id == run_id
    finally:
        close(restored)


def test_recorded_direction_is_revision_scoped_and_capture_draft_survives(cockpit):
    window, connection = cockpit
    plan = window.trade_plan
    competency = plan.competencies[0]
    repo = window.competency_development_direction_repository
    repo.save(CompetencyDevelopmentDirection(
        trade_plan_id=plan.id, trade_plan_revision="old revision",
        competency_id=competency.id, direction="Study", note="Old direction",
    ))
    window._refresh_study_home()
    assert "No recorded Study direction" in window.study_home_widget.basis_label.text()
    repo.save(CompetencyDevelopmentDirection(
        trade_plan_id=plan.id, trade_plan_revision=plan.revision,
        competency_id=competency.id, direction="Study", note="Inspect displacement",
    ))
    window.study_find_widget.pattern_input.setText("Retained question")
    window._refresh_study_home()
    assert "Inspect displacement" in window.study_home_widget.basis_label.text()
    assert window.study_home_widget.competency_combo.currentData() == competency.id
    assert "Resume" in window.study_home_widget.capture_button.text()
    window.study_home_widget.capture_button.click()
    assert window.tabs.currentWidget() is window.study_find_widget
    assert window.study_find_widget.pattern_input.text() == "Retained question"


def test_latest_direction_uses_timestamp_offsets_and_manual_selection_is_retained(cockpit):
    window, _connection = cockpit
    plan = window.trade_plan
    first, second = plan.competencies[:2]
    repo = window.competency_development_direction_repository
    for competency, stamp in ((first, "2026-10-17T12:00:00+00:00"),
                              (second, "2026-10-17T08:00:00-06:00")):
        repo.save(CompetencyDevelopmentDirection(
            trade_plan_id=plan.id, trade_plan_revision=plan.revision,
            competency_id=competency.id, direction="Study", updated_at=stamp,
        ))
    window._refresh_study_home()
    home = window.study_home_widget
    assert home.competency_combo.currentData() == second.id
    home.competency_combo.setCurrentIndex(home.competency_combo.findData(first.id))
    window.tabs.setCurrentWidget(window.study_find_widget)
    window.tabs.setCurrentWidget(home)
    assert home.competency_combo.currentData() == first.id


def test_demo_restart_keeps_idle_study_and_rejects_unrelated_directory(tmp_path):
    from tools.study_startup_demo import open_demo
    trial = tmp_path / "trial"
    for _ in range(2):
        connection, window = open_demo(trial)
        try:
            assert window.tabs.currentWidget() is window.study_home_widget
        finally:
            close(window)
            connection.close()
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    (unrelated / "keep.txt").write_text("keep")
    with pytest.raises(ValueError, match="empty directory"):
        open_demo(unrelated)
    assert (unrelated / "keep.txt").read_text() == "keep"
