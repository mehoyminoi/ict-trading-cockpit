from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QWidget,
)


class DrawThesisStep(QWidget):
    next_requested = Signal()
    back_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.primary_draw_input = QLineEdit()
        self.primary_draw_input.setPlaceholderText("Previous Day High")

        self.secondary_draw_input = QLineEdit()
        self.secondary_draw_input.setPlaceholderText("Optional")

        self.narrative_input = QTextEdit()
        self.narrative_input.setPlaceholderText(
            "Briefly describe the expected path of price..."
        )

        # Makes Tab leave the text box instead of inserting a tab character.
        self.narrative_input.setTabChangesFocus(True)

        self.primary_draw_input.installEventFilter(self)
        self.narrative_input.installEventFilter(self)

        layout = QFormLayout()
        layout.addRow("Primary Draw", self.primary_draw_input)
        layout.addRow("Secondary Draw", self.secondary_draw_input)
        layout.addRow("Thesis", self.narrative_input)

        self.setLayout(layout)

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            if (
                watched is self.narrative_input
                and event.key() == Qt.Key.Key_Tab
            ):
                self.next_requested.emit()
                return True

            if (
                watched is self.primary_draw_input
                and event.key() == Qt.Key.Key_Backtab
            ):
                self.back_requested.emit()
                return True

        return super().eventFilter(watched, event)

    def primary_draw(self) -> str:
        return self.primary_draw_input.text().strip()

    def secondary_draw(self) -> str:
        return self.secondary_draw_input.text().strip()

    def narrative(self) -> str:
        return self.narrative_input.toPlainText().strip()