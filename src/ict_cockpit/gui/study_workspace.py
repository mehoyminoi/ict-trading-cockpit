"""Presentation-only Study container and routing for existing workspace pages."""
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QStackedWidget, QTabWidget, QScrollArea, QFrame


class StudyWorkspace(QWidget):
    page_changed = Signal()

    def __init__(self, investigation, pages):
        super().__init__()
        self.pages = tuple(widget for _, widget in pages)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(investigation)
        row = QHBoxLayout()
        row.addWidget(QLabel('Study view'))
        self.selector = QComboBox()
        self.selector.setAccessibleName('Study workspace view')
        for label, _ in pages:
            self.selector.addItem(label)
        row.addWidget(self.selector)
        self.reference = QLabel()
        self.reference.setTextFormat(Qt.TextFormat.PlainText)
        self.reference.setWordWrap(True)
        row.addWidget(self.reference, 1)
        layout.addLayout(row)
        self.stack = QStackedWidget()
        self.scrolls = []
        for _, widget in pages:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setWidget(widget)
            self.scrolls.append(scroll)
            self.stack.addWidget(scroll)
        layout.addWidget(self.stack, 1)
        self.selector.currentIndexChanged.connect(self.stack.setCurrentIndex)
        self.stack.currentChanged.connect(self._changed)

    def _changed(self, index):
        self.selector.setCurrentIndex(index)
        self.page_changed.emit()

    def currentWidget(self):
        return self.pages[self.stack.currentIndex()]

    def setCurrentWidget(self, widget):
        self.stack.setCurrentIndex(self.pages.index(widget))


class WorkspaceTabs(QTabWidget):
    """Legacy workspace routes address logical pages, even inside Study.

    currentWidget/setCurrentWidget intentionally expose logical page identity to
    existing run/capture guards and demo callers. current_surface exposes the
    physical global tab. Inner navigation emits the existing change notification
    only while Study is the visible surface. No domain command is performed here.
    """
    def __init__(self):
        super().__init__()
        self.study = None

    def install_study(self, study):
        self.study = study
        for widget in study.pages:
            index = self.indexOf(widget)
            if index >= 0:
                self.removeTab(index)
        self.addTab(study, 'Study')
        study.page_changed.connect(self._study_changed)

    def _study_changed(self):
        if self.current_surface() is self.study:
            self.currentChanged.emit(self.currentIndex())

    def current_surface(self):
        return super().currentWidget()

    def currentWidget(self):
        surface = self.current_surface()
        return self.study.currentWidget() if self.study is not None and surface is self.study else surface

    def setCurrentWidget(self, widget):
        if self.study is not None and widget in self.study.pages:
            self.study.setCurrentWidget(widget)
            super().setCurrentWidget(self.study)
        else:
            super().setCurrentWidget(widget)
