from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout

from ict_cockpit.analysis.market_context_view import build_market_context_view
from ict_cockpit.analysis.trading_session_run import TradingRun


class MarketContextWidget(QFrame):
    """Compact, read-only context with bounded, scrollable provenance detail."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("process.market_context")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._view_key: tuple[str, str] | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(3)
        header = QHBoxLayout()
        self.heading_label = QLabel("Market context")
        self.heading_label.setStyleSheet("font-weight: 600;")
        self.heading_label.setToolTip(
            "Stored context facts and explicit Trade Plan rule results. Entry also requires setup criteria and all authorization gates."
        )
        header.addWidget(self.heading_label)
        header.addStretch()
        self.details_button = QPushButton("Show context details")
        self.details_button.setObjectName("process.market_context.details_toggle")
        self.details_button.setCheckable(True)
        self.details_button.toggled.connect(self._show_details)
        header.addWidget(self.details_button)
        layout.addLayout(header)
        self.availability_label = QLabel()
        self.temporal_label = QLabel()
        self.events_label = QLabel()
        for name, label in (
            ("availability", self.availability_label),
            ("temporal", self.temporal_label),
            ("events", self.events_label),
        ):
            label.setObjectName(f"process.market_context.{name}")
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setWordWrap(True)
            layout.addWidget(label)
        self.detail_text = QPlainTextEdit()
        self.detail_text.setObjectName("process.market_context.detail")
        self.detail_text.setReadOnly(True)
        self.detail_text.setFixedHeight(180)
        layout.addWidget(self.detail_text)
        self._show_details(False)
        self.hide()

    def _show_details(self, expanded: bool) -> None:
        self.detail_text.setVisible(expanded)
        self.details_button.setText("Hide context details" if expanded else "Show context details")

    def load_run_context(
        self,
        run: TradingRun | None,
        *,
        mode_id: str,
        market_time_context: dict | None = None,
    ) -> None:
        key = (run.id, mode_id) if run is not None else None
        if key != self._view_key:
            self.details_button.setChecked(False)
            self._view_key = key
        self.setVisible(run is not None)
        if run is None:
            self.detail_text.clear()
            return
        mode_name = {"tda": "TDA", "live-watch": "Watch", "post-market": "Review"}.get(mode_id, mode_id)
        self.heading_label.setText(f"Market context · {mode_name}")
        view = build_market_context_view(run, mode_id=mode_id, market_time_context=market_time_context)
        self.availability_label.setText(view.availability)
        self.temporal_label.setText(view.temporal)
        self.events_label.setText(view.events)
        # Passive timer refreshes must not reset the operator's scroll/selection.
        if self.detail_text.toPlainText() != view.detail:
            scrollbar = self.detail_text.verticalScrollBar()
            previous = scrollbar.value()
            self.detail_text.setPlainText(view.detail)
            scrollbar.setValue(previous)
