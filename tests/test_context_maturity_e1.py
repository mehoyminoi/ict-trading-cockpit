from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.quarter_theory import (
    QTComparisonState,
    compare_qt_context,
)
from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import TradingRun
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import (
    TradingDaySessionRepository,
)
from ict_cockpit.database.trading_session_run_repository import (
    TradingSessionRunRepository,
)
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_expected_observed_qt_comparison_is_descriptive() -> None:
    rows = {
        row["level_id"]: row
        for row in compare_qt_context(
            {
                "month": "A",
                "week": "M",
                "day": "D",
                "session": "N/A",
                "macro_90m": "X(R)",
            },
            {
                "month": "A",
                "week": "D",
                "day": "N/A",
                "session": "M",
                "macro_90m": "N/A",
            },
        )
    }

    assert rows["month"]["state"] == QTComparisonState.MATCHED.value
    assert rows["week"]["state"] == QTComparisonState.CHANGED.value
    assert rows["day"]["state"] == QTComparisonState.OBSERVED_UNKNOWN.value
    assert rows["session"]["state"] == QTComparisonState.EXPECTED_UNKNOWN.value
    assert rows["macro_90m"]["state"] == QTComparisonState.OBSERVED_UNKNOWN.value
    assert rows["quarter"]["state"] == QTComparisonState.NOT_COMPARABLE.value


def test_schema_v34_adds_observed_qt_review_columns(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    version = connection.execute("PRAGMA user_version").fetchone()[0]
    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(trading_session_run)"
        ).fetchall()
    }

    assert version == CURRENT_SCHEMA_VERSION == 34
    assert "review_observed_qt_context_json" in columns
    assert "review_qt_context_note" in columns
    connection.close()


def test_observed_qt_review_does_not_rewrite_tda_expectation() -> None:
    run = TradingRun("day-1", "Trading Run 1", "process-1")
    run.set_qt_context(
        {
            "week": "A",
            "day": "M",
            "session": "D",
        }
    )
    expected_before = dict(run.qt_context)

    run.set_review_observed_qt_context(
        {
            "week": "M",
            "day": "D",
            "session": "X(R)",
        },
        "Session resolved differently after the open.",
    )

    assert run.qt_context == expected_before
    assert run.review_observed_qt_context["week"] == "M"
    assert run.review_observed_qt_context["day"] == "D"
    assert run.review_observed_qt_context["session"] == "X(R)"
    assert run.review_qt_context_note == (
        "Session resolved differently after the open."
    )


def test_observed_qt_review_round_trips_through_repository(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = TradingSessionRunRepository(connection)
    day_repository = TradingDayRepository(connection)
    process_repository = TradingDaySessionRepository(connection)

    day = TradingDay(futures_day_label="2026-10-10")
    process = TradingDaySession(
        blueprint_revision="Alpha 0.2",
        mode_ids=["tda", "live-watch", "post-market"],
        current_mode_id="post-market",
    )
    process_repository.save(process)
    day_repository.save(day)

    run = TradingRun(day.id, "Trading Run 1", process.id)
    run.set_qt_context({"week": "A", "day": "M", "session": "D"})
    run.set_review_observed_qt_context(
        {"week": "A", "day": "D", "session": "D"},
        "Day phase changed; weekly and session interpretations held.",
    )
    repository.save(run)

    restored = repository.get_by_id(run.id)

    assert restored is not None
    assert restored.qt_context["day"] == "M"
    assert restored.review_observed_qt_context["day"] == "D"
    assert restored.review_observed_qt_context["week"] == "A"
    assert restored.review_qt_context_note == (
        "Day phase changed; weekly and session interpretations held."
    )
    connection.close()


def test_post_market_qt_review_updates_observed_state_only() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    assert shell.start_trading_run() is True
    run = shell.active_trading_run
    assert run is not None

    run.set_qt_context(
        {
            "week": "A",
            "day": "M",
            "session": "D",
        }
    )
    shell.runtime.load_trading_run(run)
    expected_before = dict(run.qt_context)

    review = shell.runtime.post_market_review_widget
    review.observed_qt_combos["week"].setCurrentText("A")
    review.observed_qt_combos["day"].setCurrentText("D")
    review.observed_qt_combos["session"].setCurrentText("D")
    review.qt_review_note_input.setText("Day shifted from M to D.")
    review.qt_review_note_input.editingFinished.emit()

    assert run.qt_context == expected_before
    assert run.review_observed_qt_context["week"] == "A"
    assert run.review_observed_qt_context["day"] == "D"
    assert run.review_observed_qt_context["session"] == "D"
    assert run.review_qt_context_note == "Day shifted from M to D."

    comparison = [
        review.qt_comparison_list.item(index).text()
        for index in range(review.qt_comparison_list.count())
    ]
    assert any("Week · A → A · Matched" in item for item in comparison)
    assert any("Day · M → D · Changed" in item for item in comparison)


def test_restored_review_rehydrates_observed_qt_context() -> None:
    get_app()
    blueprint = build_default_process_blueprint()
    shell = TradingDayShellWidget(blueprint)
    assert shell.start_trading_run() is True
    run = shell.active_trading_run
    assert run is not None

    run.set_qt_context({"week": "A", "day": "M", "session": "D"})
    run.set_review_observed_qt_context(
        {"week": "M", "day": "M", "session": "D"},
        "Weekly interpretation changed.",
    )
    shell.runtime.load_trading_run(run)

    review = shell.runtime.post_market_review_widget
    assert review.observed_qt_combos["week"].currentText() == "M"
    assert review.observed_qt_combos["day"].currentText() == "M"
    assert review.qt_review_note_input.text() == "Weekly interpretation changed."

    comparison = [
        review.qt_comparison_list.item(index).text()
        for index in range(review.qt_comparison_list.count())
    ]
    assert any("Week · A → M · Changed" in item for item in comparison)
    assert any("Day · M → M · Matched" in item for item in comparison)


def test_qt_review_input_does_not_create_run_evidence_automatically() -> None:
    get_app()
    shell = TradingDayShellWidget(build_default_process_blueprint())
    assert shell.start_trading_run() is True
    run = shell.active_trading_run
    assert run is not None
    assert run.evidence == []

    shell.runtime.load_trading_run(run)
    review = shell.runtime.post_market_review_widget
    review.observed_qt_combos["day"].setCurrentText("M")

    assert run.evidence == []
