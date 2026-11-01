"""Small shared editor behaviors; no domain validation or persistence ownership."""
from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QPainter, QPen, QPalette
from PySide6.QtWidgets import QWidget


def handle_ctrl_y(editor, event):
    if (event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Y
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
            and not editor.isReadOnly()):
        editor.redo()
        return True
    return False


class FieldAttention(QWidget):
    """Non-interactive outline; paint overlay avoids changing the field's layout."""
    def __init__(self, field):
        super().__init__(field)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)
        field.installEventFilter(self)
        self.hide()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(watched.rect())
        return super().eventFilter(watched, event)

    def show_cue(self):
        self.setGeometry(self.parentWidget().rect())
        self.show()
        self.raise_()
        self.update()
        self.timer.start(1800)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(self.palette().color(QPalette.ColorRole.Highlight), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect().adjusted(2, 2, -2, -2))


def focus_invalid_field(field):
    field.setFocus(Qt.FocusReason.OtherFocusReason)
    cue = getattr(field, '_validation_attention', None)
    if cue is None:
        cue = field._validation_attention = FieldAttention(field)
    cue.show_cue()
