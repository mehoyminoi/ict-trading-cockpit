"""Read-only project orientation; never reads or writes study records."""
from importlib.resources import files
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QDialogButtonBox


class DevelopmentRoadmap(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Development roadmap')
        self.resize(760, 650)
        layout = QVBoxLayout(self)
        self.reader = QTextBrowser()
        self.reader.setAccessibleName('Development roadmap — read-only')
        self.reader.setOpenExternalLinks(False)
        self.reader.setMarkdown(files('ict_cockpit').joinpath('development_roadmap.md').read_text(encoding='utf-8'))
        layout.addWidget(self.reader)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
