from datetime import date

from PySide6.QtCore import QDate, QEvent, Qt, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QFormLayout,
    QLineEdit,
    QWidget,
)


class ContextStep(QWidget):
    next_requested = Signal()
    back_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.instrument_input = QLineEdit()
        self.instrument_input.setPlaceholderText("MNQ")

        self.analysis_date_input = QDateEdit()
        self.analysis_date_input.setCalendarPopup(True)
        self.analysis_date_input.setDate(QDate.currentDate())

        self.instrument_input.installEventFilter(self)
        self.analysis_date_input.installEventFilter(self)

        layout = QFormLayout()
        layout.addRow("Instrument", self.instrument_input)
        layout.addRow("Analysis Date", self.analysis_date_input)

        self.setLayout(layout)

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            if (
                watched is self.analysis_date_input
                and event.key() == Qt.Key.Key_Tab
            ):
                self.next_requested.emit()
                return True

            if (
                watched is self.instrument_input
                and event.key() == Qt.Key.Key_Backtab
            ):
                self.back_requested.emit()
                return True

        return super().eventFilter(watched, event)

    def instrument(self) -> str:
        return self.instrument_input.text().strip().upper()

    def analysis_date(self) -> date:
        selected_date = self.analysis_date_input.date()

        return date(
            selected_date.year(),
            selected_date.month(),
            selected_date.day(),
        )