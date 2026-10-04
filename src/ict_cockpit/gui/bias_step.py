from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFormLayout,
    QHBoxLayout,
    QRadioButton,
    QWidget,
)

from ict_cockpit.analysis.tda import Bias


class BiasStep(QWidget):
    next_requested = Signal()
    back_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.weekly_group = QButtonGroup(self)
        self.daily_group = QButtonGroup(self)

        self.weekly_buttons = self._create_bias_buttons(self.weekly_group)
        self.daily_buttons = self._create_bias_buttons(self.daily_group)

        weekly_layout = self._create_button_layout(self.weekly_buttons)
        daily_layout = self._create_button_layout(self.daily_buttons)

        self.weekly_buttons[0].installEventFilter(self)
        self.daily_buttons[-1].installEventFilter(self)

        layout = QFormLayout()
        layout.addRow("Weekly Bias", weekly_layout)
        layout.addRow("Daily Bias", daily_layout)

        self.setLayout(layout)

    def _create_bias_buttons(
        self,
        group: QButtonGroup,
    ) -> list[QRadioButton]:
        buttons = []

        for bias in Bias:
            button = QRadioButton(bias.value)
            group.addButton(button)
            buttons.append(button)

        return buttons

    def _create_button_layout(
        self,
        buttons: list[QRadioButton],
    ) -> QHBoxLayout:
        layout = QHBoxLayout()

        for button in buttons:
            layout.addWidget(button)

        layout.addStretch()

        return layout

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            if (
                watched is self.daily_buttons[-1]
                and event.key() == Qt.Key.Key_Tab
            ):
                self.next_requested.emit()
                return True

            if (
                watched is self.weekly_buttons[0]
                and event.key() == Qt.Key.Key_Backtab
            ):
                self.back_requested.emit()
                return True

        return super().eventFilter(watched, event)

    def weekly_bias(self) -> Bias | None:
        checked = self.weekly_group.checkedButton()

        if checked is None:
            return None

        return Bias(checked.text())

    def daily_bias(self) -> Bias | None:
        checked = self.daily_group.checkedButton()

        if checked is None:
            return None

        return Bias(checked.text())