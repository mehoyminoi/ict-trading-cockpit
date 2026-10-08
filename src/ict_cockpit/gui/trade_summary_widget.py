from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QDateTime, QEvent, Qt, Signal
from PySide6.QtGui import QAction, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateTimeEdit,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.trade_record import (
    TRADE_SOURCES,
    TradeRecord,
    TradeRecordDraft,
)
from ict_cockpit.database.summary_template_repository import (
    SummaryTemplateRepository,
)
from ict_cockpit.media.trade_media import (
    get_trade_image_destination,
    store_trade_image,
)
from ict_cockpit.summary.renderer import SummaryRenderer
from ict_cockpit.summary.template_definition import SummaryTemplateKind
from ict_cockpit.summary.templates import TRADE_SUMMARY_V1
from ict_cockpit.summary.trade_summary_context import TradeSummaryContext
from ict_cockpit.summary.trade_summary_data import TradeSummaryData


class TradeSummaryWidget(QWidget):
    trade_ready = Signal(TradeRecord)
    draft_changed = Signal(object)

    def __init__(
        self,
        summary_template_repository: SummaryTemplateRepository | None = None,
    ) -> None:
        super().__init__()

        self.summary_template_repository = summary_template_repository
        self.current_trade_id = str(uuid4())
        self.image_paths: list[str] = []
        self.next_image_number = 1
        self._loading_draft = False
        self._is_saved = False

        self.paste_chart_action = QAction("Paste Chart", self)
        self.paste_chart_action.triggered.connect(self.paste_chart_from_clipboard)
        self.addAction(self.paste_chart_action)

        self.instrument_input = QLineEdit()
        self.instrument_input.setPlaceholderText("MNQ")

        self.trade_source_input = QComboBox()
        self.trade_source_input.addItems(TRADE_SOURCES)

        self.account_context_input = QLineEdit()
        self.account_context_input.setPlaceholderText(
            "Replay session, sim account, prop account..."
        )

        self.trade_number_input = QSpinBox()
        self.trade_number_input.setRange(1, 999)
        self.trade_number_input.setValue(1)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("NYAM FVG")

        self.direction_input = QComboBox()
        self.direction_input.addItems(["Long", "Short"])

        self.entry_tf_input = QLineEdit()
        self.entry_tf_input.setPlaceholderText("5m")

        self.entry_time_input = QDateTimeEdit()
        self.entry_time_input.setCalendarPopup(True)
        self.entry_time_input.setDisplayFormat("yyyy-MM-dd hh:mm AP")
        self.entry_time_input.setDateTime(QDateTime.currentDateTime())

        self.close_time_input = QDateTimeEdit()
        self.close_time_input.setCalendarPopup(True)
        self.close_time_input.setDisplayFormat("yyyy-MM-dd hh:mm AP")
        self.close_time_input.setDateTime(QDateTime.currentDateTime())

        self.entry_price_input = QLineEdit()
        self.entry_price_input.setPlaceholderText("20589.00")
        self.close_price_input = QLineEdit()
        self.close_price_input.setPlaceholderText("20774.25")
        self.stop_price_input = QLineEdit()
        self.stop_price_input.setPlaceholderText("20521.00")

        self.tick_size_input = QDoubleSpinBox()
        self.tick_size_input.setDecimals(4)
        self.tick_size_input.setRange(0.0001, 1000.0)
        self.tick_size_input.setValue(0.25)

        self.cycle_16y_input = QLineEdit()
        self.quadrennial_input = QLineEdit()
        self.quarter_input = QLineEdit()
        self.month_input = QLineEdit()
        self.week_input = QLineEdit()
        self.day_input = QLineEdit()
        self.session_input = QLineEdit()
        self.macro_90m_input = QLineEdit()

        self.summary_input = QTextEdit()
        self.summary_input.setPlaceholderText(
            "Trade narrative, execution notes, process observations, lessons..."
        )

        self.image_list = QListWidget()
        self.image_list.setMinimumHeight(80)
        self.image_list.currentRowChanged.connect(self.update_image_preview)

        self.image_preview = QLabel("No chart image selected")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumHeight(150)
        self.image_preview.setMaximumHeight(240)

        self.attach_image_button = QPushButton("Add Chart Image")
        self.attach_image_button.clicked.connect(self.choose_chart_image)
        self.remove_image_button = QPushButton("Remove Selected")
        self.remove_image_button.clicked.connect(self.remove_selected_image)
        self.copy_image_button = QPushButton("Copy Selected Image")
        self.copy_image_button.setEnabled(False)
        self.copy_image_button.clicked.connect(self.copy_selected_image)

        self.summary_template_label = QLabel()
        self.summary_template_label.setWordWrap(True)

        self.summary_preview = QPlainTextEdit()
        self.summary_preview.setReadOnly(True)
        self.summary_preview.setPlaceholderText(
            "Generated Trade Summary will appear here."
        )

        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        self.validation_label.hide()

        self.generate_summary_button = QPushButton("Generate Summary")
        self.generate_summary_button.clicked.connect(self.generate_summary)
        self.copy_summary_button = QPushButton("Copy Summary")
        self.copy_summary_button.clicked.connect(self.copy_summary)
        self.save_button = QPushButton("Save Trade Summary")
        self.save_button.clicked.connect(self.submit)
        self.new_trade_button = QPushButton("Start New Trade Summary")
        self.new_trade_button.hide()
        self.new_trade_button.clicked.connect(self.reset_form)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(self._build_trade_context_group())
        container_layout.addWidget(self._build_execution_group())
        container_layout.addWidget(self._build_amdx_group())
        container_layout.addWidget(self._build_notes_group())
        container_layout.addWidget(self._build_charts_group())
        container_layout.addWidget(self.validation_label)
        container_layout.addWidget(self.summary_template_label)
        container_layout.addWidget(self.generate_summary_button)
        container_layout.addWidget(self.summary_preview)
        container_layout.addWidget(self.copy_summary_button)
        container_layout.addWidget(self.save_button)
        container_layout.addWidget(self.new_trade_button)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        self._connect_draft_signals()
        self.refresh_summary_template_label()

        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def _build_trade_context_group(self) -> QGroupBox:
        group = QGroupBox("Trade Context")
        form = QFormLayout(group)
        form.addRow("Instrument", self.instrument_input)
        form.addRow("Trade Source", self.trade_source_input)
        form.addRow("Account Context", self.account_context_input)
        form.addRow("Trade #", self.trade_number_input)
        form.addRow("Model", self.model_input)
        form.addRow("Direction", self.direction_input)
        form.addRow("Entry TF", self.entry_tf_input)
        return group

    def _build_execution_group(self) -> QGroupBox:
        group = QGroupBox("Execution")
        form = QFormLayout(group)
        form.addRow("Entry Time", self.entry_time_input)
        form.addRow("Entry Price", self.entry_price_input)
        form.addRow("Close Time", self.close_time_input)
        form.addRow("Close Price", self.close_price_input)
        form.addRow("Stop Price", self.stop_price_input)
        form.addRow("Tick Size", self.tick_size_input)
        return group

    def _build_amdx_group(self) -> QGroupBox:
        group = QGroupBox("AMDX / XAMD Stack")
        form = QFormLayout(group)
        form.addRow("16Y Cycle", self.cycle_16y_input)
        form.addRow("Quadrennial", self.quadrennial_input)
        form.addRow("Quarter", self.quarter_input)
        form.addRow("Month", self.month_input)
        form.addRow("Week", self.week_input)
        form.addRow("Day", self.day_input)
        form.addRow("Session", self.session_input)
        form.addRow("90m Macro Cycle", self.macro_90m_input)
        return group

    def _build_notes_group(self) -> QGroupBox:
        group = QGroupBox("Summary / Journal")
        layout = QVBoxLayout(group)
        layout.addWidget(self.summary_input)
        return group

    def _build_charts_group(self) -> QGroupBox:
        group = QGroupBox("Chart Attachments")
        layout = QVBoxLayout(group)
        layout.addWidget(self.image_list)
        layout.addWidget(self.image_preview)
        layout.addWidget(self.copy_image_button)
        layout.addWidget(self.attach_image_button)
        layout.addWidget(self.remove_image_button)
        return group

    def _connect_draft_signals(self) -> None:
        for widget in (
            self.instrument_input,
            self.account_context_input,
            self.model_input,
            self.entry_tf_input,
            self.entry_price_input,
            self.close_price_input,
            self.stop_price_input,
            self.cycle_16y_input,
            self.quadrennial_input,
            self.quarter_input,
            self.month_input,
            self.week_input,
            self.day_input,
            self.session_input,
            self.macro_90m_input,
        ):
            widget.textChanged.connect(self.emit_draft_changed)

        self.summary_input.textChanged.connect(self.emit_draft_changed)
        self.trade_source_input.currentTextChanged.connect(self.emit_draft_changed)
        self.direction_input.currentTextChanged.connect(self.emit_draft_changed)
        self.trade_number_input.valueChanged.connect(self.emit_draft_changed)
        self.tick_size_input.valueChanged.connect(self.emit_draft_changed)
        self.entry_time_input.dateTimeChanged.connect(self.emit_draft_changed)
        self.close_time_input.dateTimeChanged.connect(self.emit_draft_changed)

    def eventFilter(self, watched, event) -> bool:
        if (
            isinstance(watched, QWidget)
            and (watched is self or self.isAncestorOf(watched))
            and event.type() == QEvent.Type.KeyPress
            and event.matches(QKeySequence.StandardKey.Paste)
            and QApplication.clipboard().mimeData().hasImage()
            and self.paste_chart_action.isEnabled()
        ):
            self.paste_chart_action.trigger()
            return True
        return super().eventFilter(watched, event)

    @staticmethod
    def _optional_float(text: str) -> float | None:
        value = text.strip().replace(",", "")
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _to_datetime(value: QDateTime) -> datetime:
        return value.toPython()

    def build_draft(self) -> TradeRecordDraft:
        return TradeRecordDraft(
            id=self.current_trade_id,
            instrument=self.instrument_input.text(),
            trade_source=self.trade_source_input.currentText(),
            account_context=self.account_context_input.text(),
            trade_number=self.trade_number_input.value(),
            model=self.model_input.text(),
            direction=self.direction_input.currentText(),
            entry_tf=self.entry_tf_input.text(),
            entry_time=self._to_datetime(self.entry_time_input.dateTime()),
            close_time=self._to_datetime(self.close_time_input.dateTime()),
            entry_price=self._optional_float(self.entry_price_input.text()),
            close_price=self._optional_float(self.close_price_input.text()),
            stop_price=self._optional_float(self.stop_price_input.text()),
            tick_size=self.tick_size_input.value(),
            cycle_16y=self.cycle_16y_input.text(),
            quadrennial=self.quadrennial_input.text(),
            quarter=self.quarter_input.text(),
            month=self.month_input.text(),
            week=self.week_input.text(),
            day=self.day_input.text(),
            session=self.session_input.text(),
            macro_90m=self.macro_90m_input.text(),
            summary=self.summary_input.toPlainText(),
            image_paths=list(self.image_paths),
        )

    def build_trade_record(self) -> TradeRecord:
        draft = self.build_draft()
        missing = []
        if not draft.instrument.strip():
            missing.append("Instrument")
        if draft.entry_price is None:
            missing.append("Entry Price")
        if draft.close_price is None:
            missing.append("Close Price")
        if draft.stop_price is None:
            missing.append("Stop Price")
        if missing:
            raise ValueError("Missing required items: " + ", ".join(missing))

        return TradeRecord(
            id=draft.id,
            instrument=draft.instrument,
            trade_source=draft.trade_source,
            account_context=draft.account_context,
            trade_number=draft.trade_number,
            model=draft.model,
            direction=draft.direction,
            entry_tf=draft.entry_tf,
            entry_time=draft.entry_time,
            close_time=draft.close_time,
            entry_price=draft.entry_price,
            close_price=draft.close_price,
            stop_price=draft.stop_price,
            tick_size=draft.tick_size,
            cycle_16y=draft.cycle_16y,
            quadrennial=draft.quadrennial,
            quarter=draft.quarter,
            month=draft.month,
            week=draft.week,
            day=draft.day,
            session=draft.session,
            macro_90m=draft.macro_90m,
            summary=draft.summary,
        )

    def _build_summary_context(self) -> TradeSummaryContext:
        trade = self.build_trade_record()
        data = TradeSummaryData(
            instrument=trade.instrument,
            entry_time=trade.entry_time,
            close_time=trade.close_time,
            entry_price=trade.entry_price,
            close_price=trade.close_price,
            stop_price=trade.stop_price,
            direction=trade.direction,
            tick_size=trade.tick_size,
        )
        return TradeSummaryContext(
            trade=data,
            trade_number=trade.trade_number,
            model=trade.model,
            entry_tf=trade.entry_tf,
            trade_source=trade.trade_source,
            account_context=trade.account_context,
            cycle_16y=trade.cycle_16y,
            quadrennial=trade.quadrennial,
            quarter=trade.quarter,
            month=trade.month,
            week=trade.week,
            day=trade.day,
            session=trade.session,
            macro_90m=trade.macro_90m,
            summary=trade.summary,
            image_paths=self.image_paths,
        )

    def _active_summary_template_body(self) -> str:
        if self.summary_template_repository is None:
            return TRADE_SUMMARY_V1
        template = self.summary_template_repository.get_active(
            SummaryTemplateKind.TRADE_SUMMARY
        )
        return template.body if template is not None else TRADE_SUMMARY_V1

    def refresh_summary_template_label(self) -> None:
        if self.summary_template_repository is None:
            self.summary_template_label.setText(
                "Template · Trade Summary Default · r1"
            )
            return
        template = self.summary_template_repository.get_active(
            SummaryTemplateKind.TRADE_SUMMARY
        )
        if template is None:
            self.summary_template_label.setText(
                "Template · Trade Summary Default · r1"
            )
        else:
            self.summary_template_label.setText(
                f"Template · {template.label}"
            )

    def generate_summary(self) -> str:
        try:
            rendered = SummaryRenderer().render(
                self._active_summary_template_body(),
                self._build_summary_context().to_template_values(),
            )
        except ValueError as exc:
            self.validation_label.setText(str(exc))
            self.validation_label.show()
            return ""

        self.validation_label.hide()
        self.summary_preview.setPlainText(rendered)
        return rendered

    def copy_summary(self) -> None:
        rendered = self.generate_summary()
        if rendered:
            QApplication.clipboard().setText(rendered)

    def submit(self) -> None:
        try:
            trade = self.build_trade_record()
            self._build_summary_context().to_template_values()
        except ValueError as exc:
            self.validation_label.setText(str(exc))
            self.validation_label.show()
            return
        self.validation_label.hide()
        self.trade_ready.emit(trade)

    def choose_chart_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Attach Chart Image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)",
        )
        if not file_path:
            return
        stored = store_trade_image(
            self.current_trade_id,
            Path(file_path),
            self.next_image_number,
        )
        self._add_managed_image(stored)

    def paste_chart_from_clipboard(self) -> bool:
        image = QApplication.clipboard().image()
        if image.isNull():
            return False
        destination = get_trade_image_destination(
            self.current_trade_id,
            self.next_image_number,
            ".png",
        )
        if not image.save(str(destination), "PNG"):
            return False
        self._add_managed_image(destination)
        return True

    def _add_managed_image(self, path: Path) -> None:
        self.image_paths.append(str(path))
        self.image_list.addItem(path.name)
        self.next_image_number += 1
        self.image_list.setCurrentRow(self.image_list.count() - 1)
        self.emit_draft_changed()

    def remove_selected_image(self) -> None:
        row = self.image_list.currentRow()
        if row < 0:
            return
        self.image_list.takeItem(row)
        self.image_paths.pop(row)
        if self.image_paths:
            self.image_list.setCurrentRow(min(row, len(self.image_paths) - 1))
        else:
            self.update_image_preview(-1)
        self.emit_draft_changed()

    def update_image_preview(self, row: int) -> None:
        if row < 0 or row >= len(self.image_paths):
            self.image_preview.clear()
            self.image_preview.setText("No chart image selected")
            self.copy_image_button.setEnabled(False)
            return

        pixmap = QPixmap(self.image_paths[row])
        if pixmap.isNull():
            self.image_preview.clear()
            self.image_preview.setText("Unable to load chart image")
            self.copy_image_button.setEnabled(False)
            return

        self.image_preview.setPixmap(
            pixmap.scaled(
                520,
                220,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.copy_image_button.setEnabled(True)

    def copy_selected_image(self) -> None:
        row = self.image_list.currentRow()
        if row < 0 or row >= len(self.image_paths):
            return
        pixmap = QPixmap(self.image_paths[row])
        if not pixmap.isNull():
            QApplication.clipboard().setPixmap(pixmap)

    def emit_draft_changed(self) -> None:
        if not self._loading_draft and not self._is_saved:
            self.draft_changed.emit(self.build_draft())

    def load_draft(self, draft: TradeRecordDraft) -> None:
        self._loading_draft = True
        self._is_saved = False
        try:
            self.current_trade_id = draft.id
            self.instrument_input.setText(draft.instrument)
            self.trade_source_input.setCurrentText(draft.trade_source)
            self.account_context_input.setText(draft.account_context)
            self.trade_number_input.setValue(draft.trade_number)
            self.model_input.setText(draft.model)
            self.direction_input.setCurrentText(draft.direction)
            self.entry_tf_input.setText(draft.entry_tf)
            if draft.entry_time:
                self.entry_time_input.setDateTime(QDateTime(draft.entry_time))
            if draft.close_time:
                self.close_time_input.setDateTime(QDateTime(draft.close_time))
            self.entry_price_input.setText(
                "" if draft.entry_price is None else str(draft.entry_price)
            )
            self.close_price_input.setText(
                "" if draft.close_price is None else str(draft.close_price)
            )
            self.stop_price_input.setText(
                "" if draft.stop_price is None else str(draft.stop_price)
            )
            self.tick_size_input.setValue(draft.tick_size)
            self.cycle_16y_input.setText(draft.cycle_16y)
            self.quadrennial_input.setText(draft.quadrennial)
            self.quarter_input.setText(draft.quarter)
            self.month_input.setText(draft.month)
            self.week_input.setText(draft.week)
            self.day_input.setText(draft.day)
            self.session_input.setText(draft.session)
            self.macro_90m_input.setText(draft.macro_90m)
            self.summary_input.setPlainText(draft.summary)

            self.image_paths = list(draft.image_paths)
            self.image_list.clear()
            self.image_list.addItems(
                [Path(path).name for path in self.image_paths]
            )
            self.next_image_number = self._next_image_number()
            if self.image_paths:
                self.image_list.setCurrentRow(0)
            else:
                self.update_image_preview(-1)
        finally:
            self._loading_draft = False

    def _next_image_number(self) -> int:
        highest = 0
        for path in self.image_paths:
            stem = Path(path).stem
            if stem.startswith("chart-"):
                try:
                    highest = max(highest, int(stem.split("-", 1)[1]))
                except ValueError:
                    pass
        return highest + 1

    def mark_saved(self) -> None:
        self._is_saved = True
        self.save_button.setText("Saved")
        self.save_button.setEnabled(False)
        self.attach_image_button.setEnabled(False)
        self.remove_image_button.setEnabled(False)
        self.paste_chart_action.setEnabled(False)
        self.new_trade_button.show()

    def reset_form(self) -> None:
        self._loading_draft = True
        self._is_saved = False
        try:
            self.current_trade_id = str(uuid4())
            self.instrument_input.clear()
            self.trade_source_input.setCurrentIndex(0)
            self.account_context_input.clear()
            self.trade_number_input.setValue(1)
            self.model_input.clear()
            self.direction_input.setCurrentIndex(0)
            self.entry_tf_input.clear()
            now = QDateTime.currentDateTime()
            self.entry_time_input.setDateTime(now)
            self.close_time_input.setDateTime(now)
            self.entry_price_input.clear()
            self.close_price_input.clear()
            self.stop_price_input.clear()
            self.tick_size_input.setValue(0.25)
            for widget in (
                self.cycle_16y_input,
                self.quadrennial_input,
                self.quarter_input,
                self.month_input,
                self.week_input,
                self.day_input,
                self.session_input,
                self.macro_90m_input,
            ):
                widget.clear()
            self.summary_input.clear()
            self.image_paths.clear()
            self.image_list.clear()
            self.update_image_preview(-1)
            self.next_image_number = 1
            self.summary_preview.clear()
            self.validation_label.hide()
            self.save_button.setText("Save Trade Summary")
            self.save_button.setEnabled(True)
            self.attach_image_button.setEnabled(True)
            self.remove_image_button.setEnabled(True)
            self.paste_chart_action.setEnabled(True)
            self.new_trade_button.hide()
        finally:
            self._loading_draft = False

        self.instrument_input.setFocus()
        self.emit_draft_changed()
