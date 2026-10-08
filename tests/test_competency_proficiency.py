from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.competency import (
    CompetencyAssessment,
    CompetencyState,
)
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.database.competency_assessment_repository import (
    CompetencyAssessmentRepository,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trade_plan_widget import TradePlanWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_default_trade_plan_publishes_plan_owned_competency_catalog() -> None:
    plan = build_default_trade_plan()

    assert plan.revision == "Alpha 0.7"
    assert [item.id for item in plan.competencies] == [
        "htf-liquidity-recognition",
        "draw-on-liquidity",
        "displacement-fvg-recognition",
        "premium-discount-context",
        "time-session-awareness",
    ]

    htf = plan.competency_by_id("htf-liquidity-recognition")
    assert htf is not None
    assert htf.category == "Market Structure"
    assert "higher-timeframe wicks" in htf.description


def test_competency_assessment_round_trips_separately_from_plan_definition(
    tmp_path,
) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = CompetencyAssessmentRepository(connection)
    plan = build_default_trade_plan()

    assessment = CompetencyAssessment(
        trade_plan_id=plan.id,
        trade_plan_revision=plan.revision,
        competency_id="htf-liquidity-recognition",
        state=CompetencyState.UNDER_STUDY,
        note="Repeatedly missed nested liquidity inside HTF wicks.",
        source="Manual",
    )
    repository.save(assessment)

    restored = repository.get(
        plan.id,
        "htf-liquidity-recognition",
    )

    assert restored is not None
    assert restored.state is CompetencyState.UNDER_STUDY
    assert "HTF wicks" in restored.note
    assert restored.source == "Manual"
    assert repository.list_for_plan(plan.id) == [restored]

    newer = CompetencyAssessment(
        trade_plan_id=plan.id,
        trade_plan_revision="Alpha 0.8",
        competency_id="htf-liquidity-recognition",
        state=CompetencyState.REHEARSAL_NEEDED,
        note="Component study passed; integration now needs rehearsal.",
        source="Manual",
    )
    repository.save(newer)
    carried = repository.get(
        plan.id,
        "htf-liquidity-recognition",
    )
    assert carried is not None
    assert carried.trade_plan_revision == "Alpha 0.8"
    assert carried.state is CompetencyState.REHEARSAL_NEEDED
    assert len(repository.list_for_plan(plan.id)) == 1

    connection.close()


def test_competency_state_is_workflow_state_not_numeric_score() -> None:
    assert [state.value for state in CompetencyState] == [
        "Not Assessed",
        "Under Study",
        "Rehearsal Needed",
        "Validation Needed",
        "Proficient",
    ]


def test_historical_backtest_can_target_plan_competency_and_carry_to_review() -> None:
    get_app()
    plan = build_default_trade_plan()
    widget = TradePlanWidget(plan)
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(
        RunEnvironment.HISTORICAL_BACKTEST.value
    )
    launcher.study_question_input.setText(
        "Can I identify meaningful liquidity inside HTF wicks?"
    )
    launcher.study_scope_input.setText("Daily / 4H context · NYAM examples")
    launcher.competency_checkboxes[
        "htf-liquidity-recognition"
    ].setChecked(True)

    assert launcher.begin_process_run() is True

    shell = widget.trading_day_shell_widget
    run = shell.active_trading_run
    assert run is not None
    assert run.study_context is not None
    assert run.study_context.competency_focus == [
        {
            "id": "htf-liquidity-recognition",
            "name": "HTF liquidity recognition",
            "category": "Market Structure",
        }
    ]

    review = shell.runtime.post_market_review_widget
    review.load_state(
        run,
        shell.runtime.tda_station_runner_widget.session,
    )

    assert "HTF liquidity recognition" in (
        review.study_competency_label.text()
    )


def test_study_competency_focus_snapshot_survives_context_round_trip() -> None:
    get_app()
    plan = build_default_trade_plan()
    widget = TradePlanWidget(plan)
    launcher = widget.process_run_launcher_widget

    launcher.environment_combo.setCurrentText(
        RunEnvironment.HISTORICAL_BACKTEST.value
    )
    launcher.study_question_input.setText("Study time awareness")
    launcher.competency_checkboxes["time-session-awareness"].setChecked(True)
    assert launcher.begin_process_run() is True

    run = widget.trading_day_shell_widget.active_trading_run
    assert run is not None
    assert run.study_context is not None

    payload = run.study_context.to_dict()
    restored = type(run.study_context).from_dict(payload)

    assert restored is not None
    assert restored.competency_focus == [
        {
            "id": "time-session-awareness",
            "name": "Time / session awareness",
            "category": "Time",
        }
    ]
