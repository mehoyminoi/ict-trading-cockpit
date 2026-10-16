"""Temporary chart-edge projection of the existing Study Find draft owner."""

from dataclasses import dataclass
from datetime import date

from PySide6.QtCore import QEvent, QPoint, QSettings, QSignalBlocker, Qt, QTimer, Signal
from PySide6.QtGui import QHideEvent, QKeyEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.gui.amdx_decision_dock import DISPLAY_PROFILES


@dataclass(frozen=True)
class StudyFindCaptureBasis:
    run_id: str
    run_label: str
    observation_date: date
    instrument: str
    session: str
    market_time: str
    amdx_target: str
    amdx_profile: str


class ContextualStudyFindDock(QFrame):
    """Small synchronized projection; the full StudyFindWidget remains owner."""

    dismissed = Signal()

    def __init__(self, source, *, settings: QSettings | None = None):
        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.source = source
        self.settings = settings
        self.return_anchor: QWidget | None = None
        self.basis: StudyFindCaptureBasis | None = None
        self._dismissing = False
        self._syncing = False
        self._pushing = False
        self.setObjectName("contextualStudyFindDock")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(420)
        self.setMaximumWidth(560)

        heading = QHBoxLayout()
        title = QLabel("Capture Study Find")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.dismiss)
        heading.addWidget(title, 1)
        heading.addWidget(self.close_button)

        self.persisted_basis_label = QLabel()
        self.persisted_basis_label.setWordWrap(True)
        self.persisted_basis_label.setStyleSheet("font-weight: 600;")
        self.context_only_label = QLabel()
        self.context_only_label.setWordWrap(True)
        self.context_only_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.context_only_label.setContentsMargins(8, 5, 8, 5)
        self.draft_label = QLabel()
        self.draft_label.setWordWrap(True)

        self.pattern_input = QLineEdit()
        self.pattern_input.setPlaceholderText("Pattern / working label")
        self.observation_input = QTextEdit()
        self.observation_input.setPlaceholderText("What happened in price?")
        self.observation_input.setMaximumHeight(120)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional lesson or note")
        self.notes_input.setMaximumHeight(80)

        attachment_row = QHBoxLayout()
        self.attachment_label = QLabel("No chart images attached")
        self.paste_chart_button = QPushButton("Paste chart")
        self.paste_chart_button.setToolTip("Paste an image from the clipboard (Ctrl+V)")
        self.paste_chart_button.clicked.connect(self.paste_chart)
        attachment_row.addWidget(self.attachment_label, 1)
        attachment_row.addWidget(self.paste_chart_button)

        action_row = QHBoxLayout()
        self.save_button = QPushButton("Save && return to Watch")
        self.save_button.clicked.connect(self.save_and_return)
        action_row.addStretch()
        action_row.addWidget(self.save_button)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        layout.addLayout(heading)
        layout.addWidget(self.persisted_basis_label)
        layout.addWidget(self.context_only_label)
        layout.addWidget(self.draft_label)
        layout.addWidget(QLabel("Pattern"))
        layout.addWidget(self.pattern_input)
        layout.addWidget(QLabel("Observation"))
        layout.addWidget(self.observation_input)
        layout.addWidget(QLabel("Lesson / notes"))
        layout.addWidget(self.notes_input)
        layout.addLayout(attachment_row)
        layout.addLayout(action_row)
        layout.addWidget(self.status_label)

        self.pattern_input.textChanged.connect(self._push_to_source)
        self.observation_input.textChanged.connect(self._push_to_source)
        self.notes_input.textChanged.connect(self._push_to_source)
        self.source.draft_changed.connect(self._source_draft_changed)
        self.source.submission_failed.connect(self._submission_failed)

        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    @property
    def display_profile(self) -> str:
        saved = (
            self.settings.value("workspace-displays/chart-relationship", "tv-left")
            if self.settings is not None
            else "tv-left"
        )
        return saved if saved in DISPLAY_PROFILES else "tv-left"

    def open_for(self, anchor: QWidget, basis: StudyFindCaptureBasis) -> None:
        self.return_anchor = anchor
        self.basis = basis
        if not self.source.save_button.isEnabled():
            self.source.reset_form()
        had_content = self.source.build_draft().has_content()
        seeded = self.source.apply_context_defaults(
            observation_date=basis.observation_date,
            instrument=basis.instrument,
            session=basis.session,
        )
        self._sync_from_source()
        self.persisted_basis_label.setText(
            f"Saved Study Find fields · {basis.observation_date.isoformat()} · "
            f"{basis.instrument} · {basis.session}"
        )
        self.context_only_label.setText(
            f"Current Watch context only · {basis.run_label} · {basis.market_time} ET · "
            f"{basis.amdx_target} · quartet {basis.amdx_profile}\n"
            "Exact run, time and AMDX basis are not stored by the current Study Find schema."
        )
        if had_content and not seeded:
            self.draft_label.setText(
                f"Resumed existing draft · {self.source.current_study_find_id[:8]} · "
                "current Watch defaults were not substituted"
            )
        else:
            self.draft_label.setText(
                f"New contextual draft · {self.source.current_study_find_id[:8]}"
            )
        self.status_label.clear()
        self.adjustSize()
        self._position_for(anchor)
        self.show()
        self.observation_input.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _position_for(self, anchor: QWidget) -> None:
        host = anchor.window()
        if self.display_profile == "tv-below":
            width = min(self.maximumWidth(), max(self.minimumWidth(), host.width() - 24))
            self.resize(width, self.sizeHint().height())
            point = host.mapToGlobal(
                QPoint(
                    max(0, (host.width() - width) // 2),
                    max(0, host.height() - self.height() - 8),
                )
            )
        else:
            point = host.mapToGlobal(
                QPoint(8, max(8, anchor.mapTo(host, QPoint(0, anchor.height())).y()))
            )
        self.move(point)

    def _source_draft_changed(self, _draft) -> None:
        if not self._pushing:
            self._sync_from_source()

    def _sync_from_source(self) -> None:
        self._syncing = True
        try:
            self.pattern_input.setText(self.source.pattern_input.text())
            self.observation_input.setPlainText(
                self.source.observation_input.toPlainText()
            )
            self.notes_input.setPlainText(self.source.notes_input.toPlainText())
            count = len(self.source.image_paths)
            self.attachment_label.setText(
                "No chart images attached"
                if count == 0
                else f"{count} managed chart image{'s' if count != 1 else ''} attached"
            )
        finally:
            self._syncing = False

    def _push_to_source(self) -> None:
        if self._syncing:
            return
        self._pushing = True
        try:
            with QSignalBlocker(self.source.pattern_input):
                self.source.pattern_input.setText(self.pattern_input.text())
            with QSignalBlocker(self.source.observation_input):
                self.source.observation_input.setPlainText(
                    self.observation_input.toPlainText()
                )
            with QSignalBlocker(self.source.notes_input):
                self.source.notes_input.setPlainText(self.notes_input.toPlainText())
            self.source.emit_draft_changed()
        finally:
            self._pushing = False

    def paste_chart(self) -> bool:
        if not self.source.paste_chart_from_clipboard():
            self.status_label.setText("Clipboard does not contain a chart image.")
            return False
        self._sync_from_source()
        self.status_label.setText("Chart image attached to this Study Find draft.")
        return True

    def save_and_return(self) -> bool:
        self._push_to_source()
        self.status_label.setText("Saving Study Find…")
        if not self.source.submit():
            return False
        return True

    def _submission_failed(self, message: str) -> None:
        labels = {
            "instrument cannot be empty": "Instrument is required.",
            "session cannot be empty": "Session is required.",
            "pattern_name cannot be empty": "Pattern is required before saving.",
            "observation cannot be empty": "Observation is required before saving.",
        }
        self.status_label.setText(labels.get(message, message))

    def notify_saved(self, study_find_id: str) -> None:
        if study_find_id != self.source.current_study_find_id:
            return
        self.status_label.setText("Study Find saved.")
        self.dismiss()

    def dismiss(self) -> None:
        self._dismissing = True
        self.hide()
        self._dismissing = False
        self._restore_anchor()

    def _restore_anchor(self) -> None:
        anchor = self.return_anchor
        self.return_anchor = None
        if anchor is not None and anchor.isEnabled() and anchor.isVisible():
            QTimer.singleShot(0, lambda: self._focus_anchor(anchor))
        self.dismissed.emit()

    @staticmethod
    def _focus_anchor(anchor: QWidget) -> None:
        try:
            if anchor.isEnabled() and anchor.isVisible():
                anchor.window().activateWindow()
                anchor.setFocus(Qt.FocusReason.OtherFocusReason)
        except RuntimeError:
            return

    def hideEvent(self, event: QHideEvent) -> None:
        super().hideEvent(event)
        if not self._dismissing and self.return_anchor is not None:
            self._restore_anchor()

    def eventFilter(self, watched, event) -> bool:
        if (
            isinstance(watched, QWidget)
            and (watched is self or self.isAncestorOf(watched))
            and event.type() == QEvent.Type.KeyPress
            and event.matches(QKeySequence.StandardKey.Paste)
            and QApplication.clipboard().mimeData().hasImage()
        ):
            self.paste_chart()
            return True
        return super().eventFilter(watched, event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.dismiss()
            event.accept()
            return
        super().keyPressEvent(event)
