from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.tda_station_session import TDAWatchPoint


class TDAWatchPointWidget(QWidget):
    """Compact authoring surface for explicit TDA IF/THEN watch points."""

    add_requested = Signal(str, str)
    remove_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(8, 6, 8, 6)
        frame_layout.setSpacing(4)

        heading = QLabel("Live Watch Points")
        heading.setStyleSheet("font-weight: 600;")
        guidance = QLabel(
            "Define only the conditions worth carrying into Live Watch: IF this occurs, THEN what should I watch for or do?"
        )
        guidance.setWordWrap(True)
        frame_layout.addWidget(heading)
        frame_layout.addWidget(guidance)

        author_row = QHBoxLayout()
        author_row.setContentsMargins(0, 0, 0, 0)
        self.if_input = QLineEdit()
        self.if_input.setPlaceholderText("IF market condition...")
        self.then_input = QLineEdit()
        self.then_input.setPlaceholderText("THEN watch / action...")
        self.add_button = QPushButton("Add Watch Point")
        self.add_button.clicked.connect(self._add)
        self.then_input.returnPressed.connect(self._add)
        author_row.addWidget(self.if_input, 1)
        author_row.addWidget(self.then_input, 1)
        author_row.addWidget(self.add_button)
        frame_layout.addLayout(author_row)

        self.watch_point_list = QListWidget()
        self.watch_point_list.setMaximumHeight(105)
        frame_layout.addWidget(self.watch_point_list)

        footer = QHBoxLayout()
        footer.addStretch()
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._remove_selected)
        footer.addWidget(self.remove_button)
        frame_layout.addLayout(footer)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.frame)

    def load_watch_points(self, watch_points: list[TDAWatchPoint]) -> None:
        self.watch_point_list.clear()
        for watch_point in watch_points:
            self.watch_point_list.addItem(
                f"IF {watch_point.if_condition}  →  THEN {watch_point.then_action}"
            )
            item = self.watch_point_list.item(self.watch_point_list.count() - 1)
            item.setData(256, watch_point.id)
        self.remove_button.setEnabled(bool(watch_points))

    def _add(self) -> None:
        if_condition = self.if_input.text().strip()
        then_action = self.then_input.text().strip()
        if not if_condition or not then_action:
            return
        self.add_requested.emit(if_condition, then_action)
        self.if_input.clear()
        self.then_input.clear()

    def _remove_selected(self) -> None:
        item = self.watch_point_list.currentItem()
        if item is None:
            return
        watch_point_id = item.data(256)
        if watch_point_id:
            self.remove_requested.emit(str(watch_point_id))
