from PySide6.QtWidgets import QApplication, QTabWidget

from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def build_window(tmp_path):
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )
    return window, connection


def test_review_development_exposes_focused_work_areas(tmp_path) -> None:
    window, connection = build_window(tmp_path)
    widget = window.trade_plan_widget.competency_evidence_review_widget
    assert widget is not None

    assert isinstance(widget.work_tabs, QTabWidget)
    assert [
        widget.work_tabs.tabText(index)
        for index in range(widget.work_tabs.count())
    ] == [
        "Evidence",
        "Interpretation",
        "Progression",
        "Practice & Launch",
    ]
    assert widget.summary_label.objectName() == "review.overview.summary"
    assert widget.evidence_page.objectName() == "review.evidence"
    assert widget.interpretation_page.objectName() == "review.interpretation"
    assert widget.progression_page.objectName() == "review.progression"
    assert widget.practice_page.objectName() == "review.practice_launcher"
    connection.close()


def test_only_one_detailed_work_area_is_active_at_a_time(tmp_path) -> None:
    window, connection = build_window(tmp_path)
    widget = window.trade_plan_widget.competency_evidence_review_widget
    assert widget is not None

    assert widget.select_work_area("Interpretation") is True
    assert widget.work_tabs.currentWidget() is widget.interpretation_page

    assert widget.select_work_area("Progression") is True
    assert widget.work_tabs.currentWidget() is widget.progression_page

    assert widget.select_work_area("Practice & Launch") is True
    assert widget.work_tabs.currentWidget() is widget.practice_page

    assert widget.select_work_area("missing") is False
    connection.close()


def test_process_launcher_is_embedded_in_practice_area(tmp_path) -> None:
    window, connection = build_window(tmp_path)
    trade_plan_widget = window.trade_plan_widget
    widget = trade_plan_widget.competency_evidence_review_widget
    assert widget is not None

    launcher = trade_plan_widget.process_run_launcher_widget
    assert launcher.parentWidget() is widget.practice_page
    assert launcher.objectName() == (
        "review.practice_launcher.process_run_launcher"
    )
    connection.close()


def test_existing_review_editors_keep_stable_ui_anchors(tmp_path) -> None:
    window, connection = build_window(tmp_path)
    widget = window.trade_plan_widget.competency_evidence_review_widget
    assert widget is not None

    assert widget.cross_run_frame.objectName() == (
        "review.cross_run_observation"
    )
    assert widget.development_frame.objectName() == (
        "review.development_direction"
    )
    assert widget.evidence_maturity_frame.objectName() == (
        "review.evidence_maturity"
    )
    assert widget.evidence_list.objectName() == "review.evidence.list"
    assert widget.detail_label.objectName() == "review.evidence.detail"
    connection.close()


def test_friction_slice_has_no_schema_change(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    version = connection.execute("PRAGMA user_version").fetchone()[0]

    assert version == CURRENT_SCHEMA_VERSION == 33
    connection.close()
