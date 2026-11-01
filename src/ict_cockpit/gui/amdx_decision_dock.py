"""Temporary chart-edge Trade Plan reference and shared AMDX decision surface."""

from PySide6.QtCore import QPoint, QSettings, Qt, QTimer, Signal
from PySide6.QtGui import QHideEvent, QKeyEvent
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.amdx import Role, XSubtype
from ict_cockpit.gui.amdx_context_widget import AMDXDecisionProjection, role_text


DISPLAY_PROFILES = ("tv-left", "tv-below")


class AMDXDecisionDock(QFrame):
    """One temporary projection of the existing AMDX command."""

    dismissed = Signal()
    display_profile_changed = Signal(str)

    def __init__(self, source, *, trade_plan_revision="", settings: QSettings | None = None):
        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.source = source
        self.trade_plan_revision = trade_plan_revision.strip() or "Unknown revision"
        self.settings = settings
        self.return_anchor: QWidget | None = None
        self._dismissing = False
        self.projection: AMDXDecisionProjection | None = None
        saved = settings.value("workspace-displays/chart-relationship", "tv-left") if settings else "tv-left"
        self.display_profile = saved if saved in DISPLAY_PROFILES else "tv-left"
        self.setObjectName("amdxDecisionDock")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(360)
        self.setMaximumWidth(520)

        heading_row = QHBoxLayout()
        self.heading_label = QLabel("Trade Plan Reference")
        self.heading_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.dismiss)
        heading_row.addWidget(self.heading_label, 1)
        heading_row.addWidget(self.close_button)

        self.provenance_label = QLabel(f"Trade Plan · {self.trade_plan_revision}")
        self.reference_label = QLabel(
            f"No published AMDX definition is configured for Trade Plan {self.trade_plan_revision}."
        )
        self.reference_label.setWordWrap(True)
        self.reference_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.reference_label.setContentsMargins(8, 6, 8, 6)
        self.target_label = QLabel("No active AMDX target")
        self.target_label.setWordWrap(True)
        self.target_label.setStyleSheet("font-weight: 600;")
        self.current_label = QLabel()
        self.current_label.setWordWrap(True)

        actions = QGridLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        self.role_buttons = {}
        for column, role in enumerate((Role.A, Role.M, Role.D)):
            button = QPushButton(role.value)
            button.clicked.connect(lambda _checked=False, item=role: self._choose(item))
            self.role_buttons[role] = button
            actions.addWidget(button, 0, column)
        self.x_buttons = {}
        for column, (label, subtype) in enumerate((
            ("X(?)", None),
            ("X(C)", XSubtype.CONTINUATION),
            ("X(R)", XSubtype.REVERSAL),
        )):
            button = QPushButton(label)
            button.clicked.connect(lambda _checked=False, item=subtype: self._choose(Role.X, item))
            self.x_buttons[subtype] = button
            actions.addWidget(button, 1, column)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        layout.addLayout(heading_row)
        layout.addWidget(self.provenance_label)
        layout.addWidget(self.reference_label)
        layout.addWidget(self.target_label)
        layout.addWidget(self.current_label)
        layout.addLayout(actions)
        layout.addWidget(self.status_label)

        self.source.decision_projection_changed.connect(self.refresh_projection)
        self.refresh_projection(self.source.decision_projection())

    def set_display_profile(self, profile: str):
        if profile not in DISPLAY_PROFILES:
            raise ValueError(f"unknown workspace display profile: {profile}")
        self.display_profile = profile
        if self.settings is not None:
            self.settings.setValue("workspace-displays/chart-relationship", profile)
            self.settings.sync()
        self.display_profile_changed.emit(profile)
        if self.isVisible() and self.return_anchor is not None:
            self._position_for(self.return_anchor)

    def open_for(self, anchor: QWidget):
        self.return_anchor = anchor
        self.refresh_projection(self.source.decision_projection())
        self.adjustSize()
        self._position_for(anchor)
        self.show()
        first = next(
            (button for button in tuple(self.role_buttons.values()) + tuple(self.x_buttons.values())
             if button.isVisible() and button.isEnabled()),
            self.close_button,
        )
        first.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _position_for(self, anchor: QWidget):
        host = anchor.window()
        if self.display_profile == "tv-below":
            width = min(self.maximumWidth(), max(self.minimumWidth(), host.width() - 24))
            self.resize(width, self.sizeHint().height())
            point = host.mapToGlobal(QPoint(
                max(0, (host.width() - width) // 2),
                max(0, host.height() - self.height() - 8),
            ))
        else:
            point = host.mapToGlobal(QPoint(8, max(8, anchor.mapTo(host, QPoint(0, anchor.height())).y())))
        self.move(point)

    def dismiss(self):
        self._dismissing = True
        self.hide()
        self._dismissing = False
        self._restore_anchor()

    def _restore_anchor(self):
        anchor = self.return_anchor
        self.return_anchor = None
        if anchor is not None and anchor.isEnabled() and anchor.isVisible():
            QTimer.singleShot(
                0,
                lambda: AMDXDecisionDock._focus_anchor(anchor),
            )
        self.dismissed.emit()

    @staticmethod
    def _focus_anchor(anchor):
        try:
            if anchor.isEnabled() and anchor.isVisible():
                anchor.window().activateWindow()
                anchor.setFocus(Qt.FocusReason.OtherFocusReason)
        except RuntimeError:
            # The host may have closed while the deferred popup return ran.
            return

    def hideEvent(self, event: QHideEvent):
        super().hideEvent(event)
        if not self._dismissing and self.return_anchor is not None:
            self._restore_anchor()

    def refresh_projection(self, projection):
        self.projection = projection
        self.target_label.setText(projection.target_label)
        current = (
            role_text(projection.current_role, projection.current_subtype)
            if projection.current_role
            else "Unresolved"
        )
        self.current_label.setText(
            f"Current · {current} · {projection.current_origin} · quartet {projection.profile}"
        )
        for role, button in self.role_buttons.items():
            legal = role in projection.legal_roles
            button.setVisible(legal)
            button.setEnabled(projection.available and legal)
        for subtype, button in self.x_buttons.items():
            legal = Role.X in projection.legal_roles and (
                subtype is None or subtype in projection.legal_x_subtypes
            )
            button.setVisible(legal)
            button.setEnabled(projection.available and legal)
        self.status_label.setText(projection.unavailable_reason)

    def _choose(self, role, subtype=None):
        projection = self.projection
        if projection is None:
            return
        if self.source.choose_decision(projection.token, role, subtype):
            self.refresh_projection(self.source.decision_projection())
            self.dismiss()
        else:
            self.refresh_projection(self.source.decision_projection())
            self.status_label.setText(self.source.status_label.text())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.dismiss()
            event.accept()
            return
        super().keyPressEvent(event)
