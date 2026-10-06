from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
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
from ict_cockpit.trade_plan import PlaybookDefinition


class TDAWatchPointWidget(QWidget):
    """TDA surface for Playbook selection plus day-specific IF/THEN points."""

    add_requested = Signal(str, str)
    remove_requested = Signal(str)
    playbook_selected = Signal(str)

    def __init__(self, playbooks: tuple[PlaybookDefinition, ...] = ()) -> None:
        super().__init__()
        self.playbooks = tuple(playbooks)
        self._loading_playbook = False

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(8, 6, 8, 6)
        frame_layout.setSpacing(4)

        heading = QLabel("Playbook & Live Watch Points")
        heading.setStyleSheet("font-weight: 600;")
        guidance = QLabel(
            "Choose the Trade Plan Playbook for this run. Its standard watch points are inherited; add only day-specific IF/THEN conditions below."
        )
        guidance.setWordWrap(True)
        frame_layout.addWidget(heading)
        frame_layout.addWidget(guidance)

        playbook_row = QHBoxLayout()
        playbook_row.addWidget(QLabel("Playbook"))
        self.playbook_combo = QComboBox()
        self.playbook_combo.addItem("No Playbook selected", "")
        for playbook in self.playbooks:
            label = f"{playbook.name} · {playbook.revision}"
            if not playbook.available:
                label += " · Locked"
            self.playbook_combo.addItem(label, playbook.id)
        self.playbook_combo.currentIndexChanged.connect(self._playbook_changed)
        playbook_row.addWidget(self.playbook_combo, 1)
        frame_layout.addLayout(playbook_row)

        inherited_heading = QLabel("Inherited from Playbook")
        inherited_heading.setStyleSheet("font-weight: 600;")
        frame_layout.addWidget(inherited_heading)
        self.inherited_list = QListWidget()
        self.inherited_list.setMaximumHeight(95)
        frame_layout.addWidget(self.inherited_list)

        day_heading = QLabel("Day-Specific Additions")
        day_heading.setStyleSheet("font-weight: 600;")
        frame_layout.addWidget(day_heading)

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
        self.remove_button = QPushButton("Remove Selected Day Point")
        self.remove_button.clicked.connect(self._remove_selected)
        footer.addWidget(self.remove_button)
        frame_layout.addLayout(footer)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.frame)

        self.load_context("", [])

    def playbook_by_id(self, playbook_id: str) -> PlaybookDefinition | None:
        for playbook in self.playbooks:
            if playbook.id == playbook_id:
                return playbook
        return None

    def load_context(
        self,
        selected_playbook_id: str,
        watch_points: list[TDAWatchPoint],
    ) -> None:
        self._loading_playbook = True
        try:
            index = self.playbook_combo.findData(selected_playbook_id)
            self.playbook_combo.setCurrentIndex(index if index >= 0 else 0)
        finally:
            self._loading_playbook = False

        self.inherited_list.clear()
        playbook = self.playbook_by_id(selected_playbook_id)
        if playbook is None:
            self.inherited_list.addItem("No Playbook watch points inherited.")
        elif not playbook.watch_point_templates:
            self.inherited_list.addItem(
                "This Playbook revision does not define standard watch points."
            )
        else:
            for template in playbook.watch_point_templates:
                self.inherited_list.addItem(
                    f"IF {template.if_condition}  →  THEN {template.then_action}"
                )

        self.watch_point_list.clear()
        for watch_point in watch_points:
            self.watch_point_list.addItem(
                f"IF {watch_point.if_condition}  →  THEN {watch_point.then_action}"
            )
            item = self.watch_point_list.item(self.watch_point_list.count() - 1)
            item.setData(256, watch_point.id)
        if not watch_points:
            self.watch_point_list.addItem("No day-specific watch points added.")
        self.remove_button.setEnabled(bool(watch_points))

    def load_watch_points(self, watch_points: list[TDAWatchPoint]) -> None:
        """Backward-compatible helper for older tests/callers."""
        selected = str(self.playbook_combo.currentData() or "")
        self.load_context(selected, watch_points)

    def _playbook_changed(self) -> None:
        if self._loading_playbook:
            return
        playbook_id = str(self.playbook_combo.currentData() or "")
        playbook = self.playbook_by_id(playbook_id)
        if playbook is not None and not playbook.available:
            self._loading_playbook = True
            self.playbook_combo.setCurrentIndex(0)
            self._loading_playbook = False
            return
        self.playbook_selected.emit(playbook_id)

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
