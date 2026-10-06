from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.gui.process_blueprint_widget import ProcessBlueprintWidget
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget
from ict_cockpit.trade_plan import TradePlanDefinition, TradePlanSectionDefinition


class TradePlanWidget(QWidget):
    """Alpha shell for the trading system and its executable process."""

    def __init__(self, trade_plan: TradePlanDefinition) -> None:
        super().__init__()
        self.trade_plan = trade_plan

        self.title_label = QLabel(f"{trade_plan.name} — {trade_plan.revision}")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")

        self.subtitle_label = QLabel(
            "Define the plan, execute the plan, observe the execution, learn from it, revise the plan."
        )
        self.subtitle_label.setWordWrap(True)

        self.operating_model_label = QLabel(
            "Foundation + Rules / Safety define the system. Playbooks define valid methods. "
            "Process operates the trading day. Review / Development improves the system and "
            "may be entered directly for Film Night, Lab, backtesting, or revision work."
        )
        self.operating_model_label.setWordWrap(True)
        self.operating_model_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.operating_model_label.setContentsMargins(10, 8, 10, 8)

        self.section_list = QListWidget()
        self.section_list.setMaximumWidth(220)

        self.stack = QStackedWidget()
        self.process_blueprint_widget = ProcessBlueprintWidget(
            trade_plan.process_blueprint
        )
        self.trading_day_shell_widget = TradingDayShellWidget(
            trade_plan.process_blueprint
        )

        self.trading_day_runtime_widget = self.trading_day_shell_widget.runtime
        self.tda_station_runner_widget = (
            self.trading_day_runtime_widget.tda_station_runner_widget
        )

        self.process_tabs = QTabWidget()
        self.process_tabs.addTab(self.process_blueprint_widget, "Process Map")
        self.process_tabs.addTab(self.trading_day_shell_widget, "Run Trading Day")
        self.process_tabs.currentChanged.connect(self._process_tab_changed)

        self._section_ids: list[str] = []
        for section in trade_plan.sections:
            self._section_ids.append(section.id)
            self.section_list.addItem(QListWidgetItem(section.name))
            if section.id == "process":
                page = self.process_tabs
            else:
                page = self._build_section_page(section)
            self.stack.addWidget(page)

        self.section_list.currentRowChanged.connect(self._section_changed)
        self.section_list.setCurrentRow(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(6)
        body.addWidget(self.section_list)
        body.addWidget(self.stack, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(5)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.operating_model_label)
        layout.addLayout(body)

    def _section_changed(self, row: int) -> None:
        self.stack.setCurrentIndex(row)
        process_active = self.selected_section_id == "process"

        # These labels explain the Trade Plan while browsing it, but become
        # redundant operating chrome once the user enters the executable
        # Process. Collapse them to give the runtime the 1080p vertical budget.
        self.title_label.setVisible(not process_active)
        self.subtitle_label.setVisible(not process_active)
        self.operating_model_label.setVisible(not process_active)

    def _process_tab_changed(self, _index: int) -> None:
        if self.process_tabs.currentWidget() is self.trading_day_shell_widget:
            self.trading_day_shell_widget.ensure_primary_trading_run_started()

    def focus_runtime(self) -> None:
        """Orient the UI directly to the persisted trading-day runtime."""
        try:
            process_row = self._section_ids.index("process")
        except ValueError:
            return
        self.section_list.setCurrentRow(process_row)
        self.process_tabs.setCurrentWidget(self.trading_day_shell_widget)

    def _build_section_page(self, section: TradePlanSectionDefinition) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        heading = QLabel(section.name)
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(heading)

        purpose = QLabel(section.purpose)
        purpose.setWordWrap(True)
        layout.addWidget(purpose)
        layout.addSpacing(12)

        topics_heading = QLabel("Current scope")
        topics_heading.setStyleSheet("font-weight: 600;")
        layout.addWidget(topics_heading)

        for topic in section.topics:
            label = QLabel(f"• {topic}")
            label.setWordWrap(True)
            layout.addWidget(label)

        layout.addStretch()
        return page

    @property
    def selected_section_id(self) -> str:
        row = self.section_list.currentRow()
        if 0 <= row < len(self._section_ids):
            return self._section_ids[row]
        return ""

    @property
    def feedback_record_id(self) -> str:
        if self.selected_section_id == "process":
            if self.process_tabs.currentWidget() is self.trading_day_shell_widget:
                return self.trading_day_shell_widget.feedback_record_id
            station_id = self.process_blueprint_widget.selected_station_id
            if station_id:
                return station_id
        return self.selected_section_id
