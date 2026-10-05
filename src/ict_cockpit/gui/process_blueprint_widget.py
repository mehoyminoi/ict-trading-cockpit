from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.process_blueprint import ProcessBlueprint


class ProcessBlueprintWidget(QWidget):
    """Read-only alpha view of the process/deck/station hierarchy."""

    STATION_ID_ROLE = Qt.ItemDataRole.UserRole

    def __init__(self, blueprint: ProcessBlueprint) -> None:
        super().__init__()
        self.blueprint = blueprint
        self.selected_station_id = ""

        self.title_label = QLabel(
            f"{blueprint.name} — {blueprint.revision}"
        )
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")

        self.subtitle_label = QLabel(
            "TradingView decks and cockpit stations are intended to advance as one process. "
            "This first view is read-only while the hierarchy is validated in real use."
        )
        self.subtitle_label.setWordWrap(True)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.currentItemChanged.connect(self._selection_changed)

        self.mode_label = QLabel("Select a station")
        self.mode_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.deck_label = QLabel()
        self.deck_label.setWordWrap(True)
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.tradingview_label = QLabel()
        self.tradingview_label.setWordWrap(True)
        self.reference_label = QLabel()
        self.reference_label.setWordWrap(True)

        detail_group = QGroupBox("Current Station")
        detail_layout = QVBoxLayout(detail_group)
        detail_layout.addWidget(self.mode_label)
        detail_layout.addWidget(self.deck_label)
        detail_layout.addSpacing(8)
        detail_layout.addWidget(self.question_label)
        detail_layout.addSpacing(8)
        detail_layout.addWidget(self.tradingview_label)
        detail_layout.addSpacing(8)
        detail_layout.addWidget(self.reference_label)
        detail_layout.addStretch()

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.tree, 2)
        content_layout.addWidget(detail_group, 3)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addLayout(content_layout)

        self._populate_tree()

    def _populate_tree(self) -> None:
        first_station_item = None

        for mode in self.blueprint.modes:
            mode_item = QTreeWidgetItem([mode.name])
            mode_item.setToolTip(0, mode.purpose)
            self.tree.addTopLevelItem(mode_item)

            for deck in mode.decks:
                deck_item = QTreeWidgetItem([deck.name])
                deck_item.setToolTip(
                    0,
                    f"TradingView layout: {deck.tradingview_layout}"
                    if deck.tradingview_layout
                    else "",
                )
                mode_item.addChild(deck_item)

                for station in deck.stations:
                    station_item = QTreeWidgetItem([station.name])
                    station_item.setData(
                        0,
                        self.STATION_ID_ROLE,
                        station.id,
                    )
                    deck_item.addChild(station_item)
                    if first_station_item is None:
                        first_station_item = station_item

            mode_item.setExpanded(True)
            for index in range(mode_item.childCount()):
                mode_item.child(index).setExpanded(True)

        if first_station_item is not None:
            self.tree.setCurrentItem(first_station_item)

    def _selection_changed(
        self,
        current: QTreeWidgetItem | None,
        previous: QTreeWidgetItem | None,
    ) -> None:
        del previous
        if current is None:
            return

        station_id = current.data(0, self.STATION_ID_ROLE)
        if not station_id:
            return

        found = self.blueprint.station_by_id(station_id)
        if found is None:
            return

        mode, deck, station = found
        self.selected_station_id = station.id

        self.mode_label.setText(f"{mode.name} · {station.name}")
        self.deck_label.setText(
            f"Deck: {deck.name}\nTradingView layout: "
            f"{deck.tradingview_layout or 'Not assigned yet'}"
        )
        self.question_label.setText(
            f"Question\n{station.question}"
        )
        self.tradingview_label.setText(
            "TradingView role\n"
            f"{station.tradingview_role or 'Not defined yet'}"
        )
        self.reference_label.setText(
            "Reference / intent\n"
            f"{station.reference or 'No additional reference yet.'}"
        )
