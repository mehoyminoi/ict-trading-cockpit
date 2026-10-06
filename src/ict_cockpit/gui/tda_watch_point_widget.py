from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.tda_station_session import TDAWatchPoint
from ict_cockpit.trade_plan import PlaybookDefinition


class TDAWatchPointWidget(QWidget):
    """TDA surface for Models in Play plus day-specific IF/THEN points."""

    add_requested = Signal(str, str)
    remove_requested = Signal(str)
    models_in_play_changed = Signal(object)
    # Compatibility signal for older tests/callers. It emits the sole selected
    # playbook id, or an empty string when the selection is not singular.
    playbook_selected = Signal(str)

    def __init__(self, playbooks: tuple[PlaybookDefinition, ...] = ()) -> None:
        super().__init__()
        self.playbooks = tuple(playbooks)
        self._loading_models = False

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(8, 6, 8, 6)
        frame_layout.setSpacing(4)

        heading = QLabel("Models in Play & Live Watch Points")
        heading.setStyleSheet("font-weight: 600;")
        guidance = QLabel(
            "Mark any reference models that may be in play today. This is not a commitment to trade one named model. Their standard conditions are carried forward alongside technician/day-specific observations."
        )
        guidance.setWordWrap(True)
        frame_layout.addWidget(heading)
        frame_layout.addWidget(guidance)

        self.models_list = QListWidget()
        self.models_list.setMaximumHeight(95)
        for playbook in self.playbooks:
            label = f"{playbook.name} · {playbook.revision}"
            if not playbook.available:
                label += " · Locked"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, playbook.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            if not playbook.available:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.models_list.addItem(item)
        self.models_list.itemChanged.connect(self._models_changed)
        frame_layout.addWidget(self.models_list)

        inherited_heading = QLabel("Inherited Standard Watch Points")
        inherited_heading.setStyleSheet("font-weight: 600;")
        frame_layout.addWidget(inherited_heading)
        self.inherited_list = QListWidget()
        self.inherited_list.setMaximumHeight(125)
        frame_layout.addWidget(self.inherited_list)

        day_heading = QLabel("Technician / Day-Specific Additions")
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

        self.load_context([], [])

    def playbook_by_id(self, playbook_id: str) -> PlaybookDefinition | None:
        return next((item for item in self.playbooks if item.id == playbook_id), None)

    def selected_playbook_ids(self) -> list[str]:
        selected: list[str] = []
        for index in range(self.models_list.count()):
            item = self.models_list.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(str(item.data(Qt.ItemDataRole.UserRole) or ""))
        return [item for item in selected if item]

    def load_context(
        self,
        selected_playbook_ids: list[str] | tuple[str, ...] | str,
        watch_points: list[TDAWatchPoint],
    ) -> None:
        if isinstance(selected_playbook_ids, str):
            selected = {selected_playbook_ids} if selected_playbook_ids else set()
        else:
            selected = {str(item) for item in selected_playbook_ids}

        self._loading_models = True
        try:
            for index in range(self.models_list.count()):
                item = self.models_list.item(index)
                playbook_id = str(item.data(Qt.ItemDataRole.UserRole) or "")
                item.setCheckState(
                    Qt.CheckState.Checked if playbook_id in selected else Qt.CheckState.Unchecked
                )
        finally:
            self._loading_models = False

        self.inherited_list.clear()
        inherited_count = 0
        for playbook_id in selected:
            playbook = self.playbook_by_id(playbook_id)
            if playbook is None:
                continue
            for template in playbook.watch_point_templates:
                inherited_count += 1
                self.inherited_list.addItem(
                    f"{playbook.name} · IF {template.if_condition} → THEN {template.then_action}"
                )
        if inherited_count == 0:
            self.inherited_list.addItem("No standard Playbook watch points currently in play.")

        self.watch_point_list.clear()
        for watch_point in watch_points:
            self.watch_point_list.addItem(
                f"IF {watch_point.if_condition} → THEN {watch_point.then_action}"
            )
            item = self.watch_point_list.item(self.watch_point_list.count() - 1)
            item.setData(Qt.ItemDataRole.UserRole, watch_point.id)
        if not watch_points:
            self.watch_point_list.addItem("No day-specific watch points added.")
        self.remove_button.setEnabled(bool(watch_points))

    def load_watch_points(self, watch_points: list[TDAWatchPoint]) -> None:
        self.load_context(self.selected_playbook_ids(), watch_points)

    def _models_changed(self, _item: QListWidgetItem) -> None:
        if self._loading_models:
            return
        selected = self.selected_playbook_ids()
        self.models_in_play_changed.emit(selected)
        self.playbook_selected.emit(selected[0] if len(selected) == 1 else "")
        self.load_context(selected, [])

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
        watch_point_id = item.data(Qt.ItemDataRole.UserRole)
        if watch_point_id:
            self.remove_requested.emit(str(watch_point_id))
