from PySide6.QtWidgets import QApplication

from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.summary_template_repository import (
    SummaryTemplateRepository,
)
from ict_cockpit.gui.study_find_widget import StudyFindWidget
from ict_cockpit.gui.trade_summary_widget import TradeSummaryWidget
from ict_cockpit.gui.summary_template_workbench_widget import (
    SummaryTemplateWorkbenchWidget,
)
from ict_cockpit.summary.renderer import SummaryRenderer
from ict_cockpit.summary.template_definition import SummaryTemplateKind
from ict_cockpit.summary.templates import STUDY_FIND_FIELDS


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def build_repository(tmp_path) -> tuple:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = SummaryTemplateRepository(connection)
    repository.ensure_defaults()
    return connection, repository


def test_schema_v27_adds_versioned_summary_template_storage(tmp_path) -> None:
    connection, _repository = build_repository(tmp_path)

    version = connection.execute("PRAGMA user_version").fetchone()[0]
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }

    assert version == CURRENT_SCHEMA_VERSION == 28
    assert "summary_template" in tables
    assert "summary_template_active" in tables
    connection.close()


def test_default_summary_templates_are_seeded_and_active(tmp_path) -> None:
    connection, repository = build_repository(tmp_path)

    trade = repository.get_active(SummaryTemplateKind.TRADE_SUMMARY)
    study = repository.get_active(SummaryTemplateKind.STUDY_FIND)

    assert trade is not None
    assert trade.template_id == "trade-summary-default"
    assert trade.revision == 1
    assert study is not None
    assert study.template_id == "study-find-default"
    assert study.revision == 1
    connection.close()


def test_publish_revision_keeps_history_and_moves_active_pointer(tmp_path) -> None:
    connection, repository = build_repository(tmp_path)
    original = repository.get_active(SummaryTemplateKind.STUDY_FIND)
    assert original is not None

    published = repository.publish_revision(
        original,
        name="Study Find Compact",
        body="Study {asset}: {observation}\n",
    )

    assert published.revision == 2
    assert repository.get(original.template_id, 1) == original
    assert repository.get_active(SummaryTemplateKind.STUDY_FIND) == published
    assert [item.revision for item in repository.list_revisions(original.template_id)] == [
        2,
        1,
    ]
    connection.close()


def test_renderer_rejects_unknown_configurable_template_field() -> None:
    renderer = SummaryRenderer()

    try:
        renderer.validate(
            "Asset: {asset}\nUnknown: {does_not_exist}\n",
            STUDY_FIND_FIELDS,
        )
    except ValueError as exc:
        assert "does_not_exist" in str(exc)
    else:
        raise AssertionError("expected unknown template field to fail validation")


def test_workbench_publishes_revision_used_by_study_find(tmp_path) -> None:
    get_app()
    connection, repository = build_repository(tmp_path)
    workbench = SummaryTemplateWorkbenchWidget(repository)

    workbench.kind_combo.setCurrentText(SummaryTemplateKind.STUDY_FIND.value)
    workbench.name_input.setText("Study Find Compact")
    workbench.body_input.setPlainText(
        "CUSTOM {asset} | {pattern} | {observation}"
    )
    workbench.publish_revision()

    active = repository.get_active(SummaryTemplateKind.STUDY_FIND)
    assert active is not None
    assert active.revision == 2
    assert active.name == "Study Find Compact"

    widget = StudyFindWidget(repository)
    widget.instrument_input.setText("MNQ")
    widget.session_input.setText("NYAM")
    widget.pattern_input.setText("London low raid")
    widget.observation_input.setPlainText("Bullish displacement followed.")

    rendered = widget.generate_summary()

    assert rendered.startswith("CUSTOM MNQ | London low raid")
    assert "Template: Study Find Compact · r2" in rendered
    assert "r2" in widget.summary_template_label.text()
    connection.close()


def test_trade_summary_output_includes_active_template_provenance(tmp_path) -> None:
    get_app()
    connection, repository = build_repository(tmp_path)
    original = repository.get_active(SummaryTemplateKind.TRADE_SUMMARY)
    assert original is not None
    repository.publish_revision(
        original,
        name="Trade Summary Compact",
        body="TRADE {asset} | {direction} | {result_handles}\n",
    )

    widget = TradeSummaryWidget(repository)
    widget.instrument_input.setText("MNQ")
    widget.direction_input.setCurrentText("Long")
    widget.entry_price_input.setText("20000")
    widget.close_price_input.setText("20010")
    widget.stop_price_input.setText("19995")

    rendered = widget.generate_summary()

    assert rendered.startswith("TRADE MNQ | Long | 10.00")
    assert "Template: Trade Summary Compact · r2" in rendered
    assert "r2" in widget.summary_template_label.text()
    connection.close()
