"""Small manual editor; market clock ownership remains in the shell command."""
from copy import deepcopy
from uuid import uuid4

from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout
from ict_cockpit.analysis.replay_reference import aware_instant, resolve_new_york


class ReplayReferenceDialog(QDialog):
    def __init__(self, shell):
        super().__init__(shell)
        self.setWindowTitle("Set Replay reference")
        self.shell = shell
        self.expected_run = deepcopy(shell.active_trading_run)
        self.operation_id = str(uuid4())
        current = aware_instant(self.expected_run.market_time_context["captured_at"])
        layout = QVBoxLayout(self)
        notice = QLabel("Manual operator-selected reference · not synchronized with TradingView.\n"
                        "Forward only within the original Trading Day (18:00 New York boundary).")
        notice.setWordWrap(True)
        layout.addWidget(notice)
        layout.addWidget(QLabel(f"Current: {current.isoformat()} · America/New_York"))
        self.time_input = QLineEdit(current.strftime("%Y-%m-%d %H:%M:%S"))
        self.time_input.setAccessibleName("New York Replay reference")
        layout.addWidget(self.time_input)
        self.occurrence = QComboBox()
        self.occurrence.addItem("Repeated hour: choose only if requested", None)
        self.occurrence.addItem("First occurrence (earlier instant)", 0)
        self.occurrence.addItem("Second occurrence (later instant)", 1)
        layout.addWidget(self.occurrence)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def apply(self):
        try:
            requested = resolve_new_york(self.time_input.text(), self.occurrence.currentData())
            self.shell.set_replay_reference(requested, expected_run=self.expected_run,
                                            operation_id=self.operation_id)
        except (ValueError, TypeError, KeyError, RuntimeError) as error:
            self.status.setText(f"Reference unchanged · {error}")
            self.time_input.setFocus()
            return
        self.accept()
