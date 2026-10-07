from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.quarter_theory import (
    QTPhase,
    QuarterTheoryContext,
    normalize_qt_context,
    qt_context_summary,
)
from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import TradingRun
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def build_shell() -> TradingDayShellWidget:
    plan = build_default_trade_plan()
    return TradingDayShellWidget(
        plan.process_blueprint,
        playbooks=plan.playbooks,
        authorization_gates=plan.authorization_gates,
        trade_plan_revision=plan.revision,
    )


def test_qt_context_normalizes_all_nested_levels() -> None:
    context = normalize_qt_context(
        {
            "day": "M",
            "session": "D",
            "macro_90m": "X(R)",
        }
    )

    assert context["cycle_16y"] == "N/A"
    assert context["day"] == "M"
    assert context["session"] == "D"
    assert context["macro_90m"] == "X(R)"


def test_qt_context_rejects_unknown_phase_to_na_during_normalization() -> None:
    context = normalize_qt_context({"week": "Something Else"})

    assert context["week"] == QTPhase.NOT_APPLICABLE.value


def test_qt_context_object_supports_explicit_amdx_phases() -> None:
    context = QuarterTheoryContext()
    context.set_phase("month", QTPhase.ACCUMULATION)
    context.set_phase("week", QTPhase.MANIPULATION)
    context.set_phase("day", QTPhase.DISTRIBUTION)
    context.set_phase("session", QTPhase.X_REVERSAL)

    assert context.to_dict()["month"] == "A"
    assert context.to_dict()["week"] == "M"
    assert context.to_dict()["day"] == "D"
    assert context.to_dict()["session"] == "X(R)"
    assert qt_context_summary(context.to_dict()) == (
        "Month A · Week M · Day D · Session X(R)"
    )


def test_trading_run_qt_mutator_updates_and_normalizes_context() -> None:
    run = TradingRun(
        trading_day_id="day-1",
        session_name="Trading Run 1",
        process_session_id="process-1",
    )

    run.set_qt_context(
        {
            "day": "M",
            "session": "D",
            "macro_90m": "X(R)",
        }
    )

    assert run.qt_context["day"] == "M"
    assert run.qt_context["session"] == "D"
    assert run.qt_context["macro_90m"] == "X(R)"
    assert run.qt_context["week"] == "N/A"


def test_qt_context_round_trips_with_trading_run(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    plan = build_default_trade_plan()
    day = TradingDay(futures_day_label="2026-10-07")
    process = TradingDaySession(
        blueprint_revision=plan.process_blueprint.revision,
        mode_ids=[mode.id for mode in plan.process_blueprint.modes],
        current_mode_id="tda",
    )
    run = TradingRun(
        trading_day_id=day.id,
        session_name="Trading Run 1",
        process_session_id=process.id,
        trade_plan_revision=plan.revision,
        qt_context={
            "quarter": "X(C)",
            "month": "A",
            "week": "M",
            "day": "D",
            "session": "X(R)",
            "macro_90m": "Distortion",
        },
    )

    TradingDaySessionRepository(connection).save(process)
    day.activate_trading_run(run)
    TradingDayRepository(connection).save(day)
    repository = TradingSessionRunRepository(connection)
    repository.save(run)

    restored = repository.get_by_id(run.id)
    assert restored is not None
    assert restored.qt_context["quarter"] == "X(C)"
    assert restored.qt_context["month"] == "A"
    assert restored.qt_context["week"] == "M"
    assert restored.qt_context["day"] == "D"
    assert restored.qt_context["session"] == "X(R)"
    assert restored.qt_context["macro_90m"] == "Distortion"

    connection.close()


def test_tda_qt_editor_updates_run_and_carries_into_watch() -> None:
    get_app()
    shell = build_shell()
    assert shell.start_trading_run() is True
    run = shell.active_trading_run
    assert run is not None

    runner = shell.runtime.tda_station_runner_widget
    runner.select_station("tda-thesis")
    editor = shell.runtime.qt_context_widget
    assert editor.isHidden() is False

    editor.phase_combos["day"].setCurrentText("M")
    editor.phase_combos["session"].setCurrentText("D")
    editor.phase_combos["macro_90m"].setCurrentText("X(R)")

    assert run.qt_context["day"] == "M"
    assert run.qt_context["session"] == "D"
    assert run.qt_context["macro_90m"] == "X(R)"

    assert shell.runtime.apply_transition(
        "finish-tda",
        override_incomplete=True,
    ) is True

    watch = shell.runtime.live_watch_widget
    assert "Day M" in watch.qt_summary_label.text()
    assert "Session D" in watch.qt_summary_label.text()
    assert "90m Macro X(R)" in watch.qt_summary_label.text()


def test_post_market_review_surfaces_qt_context() -> None:
    get_app()
    shell = build_shell()
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

    review = shell.runtime.post_market_review_widget
    review.load_state(
        run,
        shell.runtime.tda_station_runner_widget.session,
    )

    items = [
        review.tda_snapshot_list.item(index).text()
        for index in range(review.tda_snapshot_list.count())
    ]
    assert any(
        "QT / AMDX Stack" in item
        and "Week A" in item
        and "Day M" in item
        and "Session D" in item
        for item in items
    )
