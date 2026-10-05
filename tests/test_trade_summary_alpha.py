from datetime import datetime

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.trade_record import TradeRecord, TradeRecordDraft
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.database.trade_record_repository import TradeRecordRepository
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.gui.trade_summary_widget import TradeSummaryWidget


def get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_creates_trade_tables(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    names = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }

    assert "trade_record" in names
    assert "trade_record_image" in names
    assert "trade_record_draft" in names
    connection.close()


def test_trade_repository_round_trips_record_and_images(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = TradeRecordRepository(connection)

    trade = TradeRecord(
        id="trade-123",
        instrument="mnq",
        trade_source="TradingView Replay",
        account_context="October replay",
        trade_number=2,
        model="NYAM FVG",
        direction="Long",
        entry_tf="5m",
        entry_time=datetime(2026, 10, 5, 9, 45),
        close_time=datetime(2026, 10, 5, 10, 31),
        entry_price=20589.0,
        close_price=20774.25,
        stop_price=20521.0,
        tick_size=0.25,
        session="NYAM D",
        summary="Clean replay example.",
    )

    repository.save(trade)
    repository.add_image(trade.id, "/tmp/chart-1.png")
    repository.add_image(trade.id, "/tmp/chart-2.png")

    loaded = repository.get_by_id(trade.id)
    assert loaded is not None
    assert loaded.instrument == "MNQ"
    assert loaded.trade_source == "TradingView Replay"
    assert loaded.account_context == "October replay"
    assert loaded.model == "NYAM FVG"
    assert repository.get_images(trade.id) == [
        "/tmp/chart-1.png",
        "/tmp/chart-2.png",
    ]
    connection.close()


def test_trade_repository_round_trips_draft(tmp_path) -> None:
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    repository = TradeRecordRepository(connection)

    draft = TradeRecordDraft(
        id="draft-123",
        instrument="MNQ",
        trade_source="TradingView Paper",
        account_context="Paper test",
        model="Silver Bullet",
        entry_time=datetime(2026, 10, 5, 10, 5),
        entry_price=21000.25,
        image_paths=["/tmp/chart-1.png"],
    )

    repository.save_draft(draft)
    loaded = repository.get_latest_draft()

    assert loaded is not None
    assert loaded.id == draft.id
    assert loaded.trade_source == "TradingView Paper"
    assert loaded.entry_price == 21000.25
    assert loaded.image_paths == ["/tmp/chart-1.png"]

    repository.delete_draft(draft.id)
    assert repository.get_latest_draft() is None
    connection.close()


def test_trade_summary_widget_generates_expected_summary() -> None:
    get_app()
    widget = TradeSummaryWidget()

    widget.instrument_input.setText("MNQ")
    widget.trade_source_input.setCurrentText("TradingView Replay")
    widget.account_context_input.setText("Replay Week 2")
    widget.model_input.setText("NYAM FVG")
    widget.direction_input.setCurrentText("Long")
    widget.entry_tf_input.setText("5m")
    widget.entry_price_input.setText("20589")
    widget.close_price_input.setText("20774.25")
    widget.stop_price_input.setText("20521")
    widget.summary_input.setPlainText("Waited for manipulation.")

    rendered = widget.generate_summary()

    assert "Asset: MNQ" in rendered
    assert "Source: TradingView Replay" in rendered
    assert "Account: Replay Week 2" in rendered
    assert "Model: NYAM FVG" in rendered
    assert "Trade Results: 185.25 handles/ 741 ticks" in rendered


def test_trade_summary_clipboard_image_is_managed(monkeypatch, tmp_path) -> None:
    app = get_app()
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    widget = TradeSummaryWidget()

    image = QImage(12, 12, QImage.Format.Format_RGB32)
    image.fill(0)
    app.clipboard().setImage(image)

    assert widget.paste_chart_from_clipboard()
    assert len(widget.image_paths) == 1
    assert widget.image_paths[0].endswith("chart-1.png")
    assert widget.image_list.currentRow() == 0


def test_main_window_restores_and_saves_trade_draft(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)

    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection)
    trade_repository = TradeRecordRepository(connection)

    draft = TradeRecordDraft(
        id="trade-draft",
        instrument="MNQ",
        trade_source="TradingView Replay",
        account_context="Replay session",
        model="NYAM FVG",
        entry_price=20589.0,
    )
    trade_repository.save_draft(draft)

    window = MainWindow(
        tda_repository,
        study_find_repository,
        trade_record_repository=trade_repository,
    )

    widget = window.trade_summary_widget
    assert widget.current_trade_id == "trade-draft"
    assert widget.instrument_input.text() == "MNQ"
    assert widget.account_context_input.text() == "Replay session"

    widget.close_price_input.setText("20774.25")
    widget.stop_price_input.setText("20521")
    trade = widget.build_trade_record()
    window.save_trade_record(trade)

    assert trade_repository.get_by_id(trade.id) is not None
    assert trade_repository.get_latest_draft() is None
    connection.close()


def test_feedback_context_tracks_trade_summary(tmp_path) -> None:
    get_app()
    connection = create_connection(tmp_path / "test.db")
    initialize_schema(connection)
    window = MainWindow(
        TDARepository(connection),
        StudyFindRepository(connection),
    )

    window.tabs.setCurrentWidget(window.trade_summary_widget)
    context, record_id = window.current_feedback_context()

    assert context == "Trade Summary"
    assert record_id == window.trade_summary_widget.current_trade_id
    connection.close()
