from PySide6.QtWidgets import QApplication

from ict_cockpit.gui.tda_workflow import TDAWorkflowWidget

from PySide6.QtCore import QDate

from ict_cockpit.analysis.tda import Bias, TDAStatus

def test_tda_workflow_can_be_constructed() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    workflow = TDAWorkflowWidget()

    assert workflow is not None
def test_build_tda_record_from_workflow() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    workflow = TDAWorkflowWidget()

    workflow.context_step.instrument_input.setText("mnq")
    workflow.context_step.analysis_date_input.setDate(QDate(2026, 10, 3))

    workflow.bias_step.weekly_buttons[0].setChecked(True)
    workflow.bias_step.daily_buttons[1].setChecked(True)

    workflow.draw_thesis_step.primary_draw_input.setText("Previous Week High")
    workflow.draw_thesis_step.secondary_draw_input.setText("Previous Day High")
    workflow.draw_thesis_step.narrative_input.setPlainText(
        "Expecting expansion toward higher liquidity."
    )

    tda = workflow.build_tda_record()

    assert tda.instrument == "MNQ"
    assert tda.analysis_date.isoformat() == "2026-10-03"
    assert tda.weekly_bias == Bias.BULLISH
    assert tda.daily_bias == Bias.BEARISH
    assert tda.primary_draw == "Previous Week High"
    assert tda.secondary_draw == "Previous Day High"
    assert tda.narrative == "Expecting expansion toward higher liquidity."

def test_workflow_builds_complete_tda_when_required_fields_present() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    workflow = TDAWorkflowWidget()

    workflow.context_step.instrument_input.setText("MNQ")

    workflow.bias_step.weekly_buttons[0].setChecked(True)
    workflow.bias_step.daily_buttons[0].setChecked(True)

    workflow.draw_thesis_step.primary_draw_input.setText(
        "Previous Week High"
    )

    tda = workflow.build_tda_record()

    assert tda.missing_required_fields() == []

def test_attempt_completion_returns_to_bias_when_bias_missing() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    workflow = TDAWorkflowWidget()

    workflow.context_step.instrument_input.setText("MNQ")
    workflow.draw_thesis_step.primary_draw_input.setText(
        "Previous Week High"
    )

    workflow.current_step = 2
    workflow._update_view()

    workflow.attempt_completion()

    assert workflow.current_step == 1

def test_file_incomplete_emits_incomplete_tda() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    workflow = TDAWorkflowWidget()

    workflow.context_step.instrument_input.setText("MNQ")

    emitted_records = []
    workflow.tda_ready.connect(emitted_records.append)

    workflow.file_incomplete()

    assert len(emitted_records) == 1
    assert emitted_records[0].status == TDAStatus.INCOMPLETE_OVERRIDE

def test_reset_workflow_clears_previous_tda() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    workflow = TDAWorkflowWidget()

    workflow.context_step.instrument_input.setText("MNQ")
    workflow.bias_step.weekly_buttons[0].setChecked(True)
    workflow.draw_thesis_step.primary_draw_input.setText(
        "Previous Week High"
    )

    workflow.reset_workflow()

    assert workflow.context_step.instrument_input.text() == ""
    assert workflow.bias_step.weekly_group.checkedButton() is None
    assert workflow.draw_thesis_step.primary_draw_input.text() == ""
    assert workflow.current_step == 0

def test_workflow_reuses_same_tda_id_during_draft() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    workflow = TDAWorkflowWidget()

    workflow.context_step.instrument_input.setText("MNQ")

    first = workflow.build_tda_record()

    workflow.context_step.instrument_input.setText("NQ")

    second = workflow.build_tda_record()

    assert first.id == second.id

def test_reset_workflow_creates_new_tda_id() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    workflow = TDAWorkflowWidget()

    original_id = workflow.current_tda_id

    workflow.reset_workflow()

    assert workflow.current_tda_id != original_id