from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.quarter_theory import (
    QT_LEVELS,
    QTPhase,
    normalize_qt_context,
)


class QTContextWidget(QFrame):
    """Compact editor for the technician's nested QT / AMDX interpretation."""

    context_changed = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._loading = False
        self.phase_combos: dict[str, QComboBox] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        heading = QLabel("QT / AMDX Stack")
        heading.setStyleSheet("font-weight: 600;")
        help_label = QLabel(
            "Interpret the active nested quarters. Market-time quarter positions are factual; "
            "A/M/D/X labels remain technician / Trade Plan interpretation."
        )
        help_label.setWordWrap(True)
        self.market_time_label = QLabel("Market-time context: not loaded")
        self.market_time_label.setWordWrap(True)

        layout.addWidget(heading)
        layout.addWidget(help_label)
        layout.addWidget(self.market_time_label)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(3)

        values = [item.value for item in QTPhase]
        for index, (level_id, label) in enumerate(QT_LEVELS):
            row = index // 4
            column = (index % 4) * 2
            grid.addWidget(QLabel(label), row, column)
            combo = QComboBox()
            combo.addItems(values)
            combo.currentTextChanged.connect(
                lambda _text, level=level_id: self._emit_context_changed(level)
            )
            self.phase_combos[level_id] = combo
            grid.addWidget(combo, row, column + 1)

        layout.addLayout(grid)

    def _emit_context_changed(self, _level_id: str) -> None:
        if not self._loading:
            self.context_changed.emit(self.context())

    def context(self) -> dict[str, str]:
        return {
            level_id: combo.currentText()
            for level_id, combo in self.phase_combos.items()
        }

    def load_context(
        self,
        qt_context: dict | None,
        market_time_context: dict | None = None,
    ) -> None:
        context = normalize_qt_context(qt_context)
        self._loading = True
        try:
            for level_id, combo in self.phase_combos.items():
                combo.setCurrentText(context[level_id])
        finally:
            self._loading = False

        market = dict(market_time_context or {})
        daily_q = str(market.get("daily_quarter", "")).strip()
        session_q = str(market.get("session_quarter", "")).strip()
        session = str(market.get("session", "")).strip()
        pieces = []
        if daily_q:
            pieces.append(f"Daily {daily_q}")
        if session:
            pieces.append(session)
        if session_q:
            pieces.append(f"Session {session_q}")
        self.market_time_label.setText(
            "Market-time context: " + (" · ".join(pieces) if pieces else "not available")
        )

    def clear_context(self) -> None:
        self.load_context({})
