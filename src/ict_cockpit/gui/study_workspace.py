"""Presentation-only Study container and routing for existing workspace pages."""
from PySide6.QtCore import Signal, Qt, QSignalBlocker
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QStackedWidget, QTabWidget, QScrollArea, QFrame


class StudyWorkspace(QWidget):
    page_changed = Signal()

    def __init__(self, investigation, pages):
        super().__init__()
        self.before_change = lambda old, new: True
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
        self.selector.currentIndexChanged.connect(self._select)
        self.stack.currentChanged.connect(self._changed)

    def _select(self, index):
        old = self.stack.currentIndex()
        if index != old and not self.before_change(self.pages[old], self.pages[index]):
            with QSignalBlocker(self.selector):
                self.selector.setCurrentIndex(old)
            return
        self.stack.setCurrentIndex(index)

    def _changed(self, index):
        self.selector.setCurrentIndex(index)
        self.page_changed.emit()

    def currentWidget(self):
        return self.pages[self.stack.currentIndex()]

    def setCurrentWidget(self, widget):
        self._select(self.pages.index(widget))


class WorkspaceTabs(QTabWidget):
    """Legacy workspace routes address logical pages, even inside Study.

    currentWidget/setCurrentWidget intentionally expose logical page identity to
    existing run/capture guards and demo callers. current_surface exposes the
    physical global tab. Consumers use navigation_changed, emitted only after a
    permitted transition. Rejected native tab selections are restored before
    application observers run. Inner navigation is notified only while Study is
    visible. No domain command is performed here.
    """
    navigation_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.study = None
        self.before_change = lambda old, new: True
        self._accepted_surface = None
        self.currentChanged.connect(self._surface_changed)

    def _surface_changed(self, index):
        target = self.current_surface()
        old = self._accepted_surface
        if old is not None and old is not target and not self.before_change(old, target):
            with QSignalBlocker(self):
                super().setCurrentIndex(self.indexOf(old))
            return
        self._accepted_surface = target
        self.navigation_changed.emit(index)

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
            self.navigation_changed.emit(self.currentIndex())

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
