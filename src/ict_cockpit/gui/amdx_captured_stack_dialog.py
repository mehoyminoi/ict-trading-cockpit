"""Read-only full-stack inspection of a retained run capture."""
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from ict_cockpit.database.amdx_master_repository import read_master_archive
from ict_cockpit.gui.amdx_catalog_widget import AMDXCatalogWidget


class _CapturedSource:
    def __init__(self, capture, amdx):
        self.capture, self.amdx, self.connection = capture, amdx, amdx.connection
        self.owner = read_master_archive(capture.packet["master"])[1]

    def list_catalogs(self):
        return (self.owner,)

    def get(self, id):
        if id != self.owner.id:
            raise ValueError("Captured owner differs")
        return self.owner

    def load_stack(self, *args, **kwargs):
        return self.capture.projection

    def revise(self, *args, **kwargs):
        raise ValueError("Captured context is read-only")


class _CapturedPane(AMDXCatalogWidget):
    def refresh(self):
        super().refresh()
        self.status_label.setText("Retained run context · inspection is read-only")
        self.rule_label.setText("This is the captured working stack. Current calendar corrections do not change it.")

    def _restore(self):
        self._restore_catalog_id = self.repository.owner.id

    def _save_navigation(self):
        pass

    def choose(self, *args, **kwargs):
        return


class AMDXCapturedStackDialog(QDialog):
    def __init__(self, capture, amdx, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AMDX · captured working context")
        self.resize(1344, 756)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Captured at {capture.reason.lower()} · reference {capture.projection.reference.isoformat()} · read-only"))
        self.pane = _CapturedPane(_CapturedSource(capture, amdx), reference=capture.projection.reference)
        self.pane.heading.setText("AMDX · retained run context")
        self.pane.channel_selector.setCurrentText("Expected")
        self.pane.set_active(False)
        for control in (self.pane.catalog_selector, self.pane.new_button, self.pane.details_button):
            control.hide()
        for control in (self.pane.date_input, self.pane.time_input, self.pane.fold_selector,
                        self.pane.channel_selector, self.pane.previous_button, self.pane.next_button,
                        *self.pane.session_buttons.values()):
            control.setEnabled(False)
        layout.addWidget(self.pane)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.reject)
        layout.addWidget(close)
