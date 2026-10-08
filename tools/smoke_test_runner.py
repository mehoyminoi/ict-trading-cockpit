from __future__ import annotations

import argparse
from pathlib import Path
import sys

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.dev.smoke_test_document import (
    STATUSES,
    SmokeTestDocument,
)


class SmokeTestRunnerWindow(QMainWindow):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path
        self.document = SmokeTestDocument.load(path)
        if not self.document.items:
            raise ValueError(
                f"No status-bearing smoke-test items found in {path}"
            )
        self.current_index = 0

        self.setWindowTitle("ICT Cockpit Smoke Test Runner")
        self.resize(900, 620)

        central = QWidget()
        layout = QVBoxLayout(central)

        file_row = QHBoxLayout()
        self.file_label = QLabel()
        self.file_label.setWordWrap(True)
        file_row.addWidget(self.file_label, 1)
        open_button = QPushButton("Open…")
        open_button.clicked.connect(self.open_file)
        file_row.addWidget(open_button)
        layout.addLayout(file_row)

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        self.position_label = QLabel()
        self.position_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(self.position_label)

        self.section_label = QLabel()
        self.section_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(self.section_label)

        self.item_label = QLabel()
        self.item_label.setWordWrap(True)
        self.item_label.setMinimumHeight(72)
        layout.addWidget(self.item_label)

        status_row = QHBoxLayout()
        self.status_buttons: dict[str, QPushButton] = {}
        for status in STATUSES:
            button = QPushButton(status)
            button.setCheckable(True)
            button.clicked.connect(
                lambda checked=False, value=status: self.set_status(value)
            )
            self.status_buttons[status] = button
            status_row.addWidget(button)
        layout.addLayout(status_row)

        layout.addWidget(QLabel("Comments / evidence"))
        self.comment_edit = QPlainTextEdit()
        self.comment_edit.setPlaceholderText(
            "Optional. One note per line. Existing notes are preserved."
        )
        layout.addWidget(self.comment_edit, 1)

        navigation = QHBoxLayout()
        self.previous_button = QPushButton("← Previous")
        self.previous_button.clicked.connect(self.previous_item)
        navigation.addWidget(self.previous_button)

        self.next_unresolved_button = QPushButton("Next unresolved")
        self.next_unresolved_button.clicked.connect(self.next_unresolved)
        navigation.addWidget(self.next_unresolved_button)

        self.next_button = QPushButton("Next →")
        self.next_button.clicked.connect(self.next_item)
        navigation.addWidget(self.next_button)
        navigation.addStretch()

        save_button = QPushButton("Save Markdown")
        save_button.clicked.connect(self.save_document)
        navigation.addWidget(save_button)
        layout.addLayout(navigation)

        self.setCentralWidget(central)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_document)
        self.addAction(save_action)

        self.load_item()

    def commit_current_edits(self) -> None:
        item = self.document.items[self.current_index]
        selected = next(
            (
                status
                for status, button in self.status_buttons.items()
                if button.isChecked()
            ),
            item.status,
        )
        comments = [
            line.strip()
            for line in self.comment_edit.toPlainText().splitlines()
            if line.strip()
        ]
        self.document.update_item(
            self.current_index,
            status=selected,
            comments=comments,
        )

    def load_item(self) -> None:
        item = self.document.items[self.current_index]
        self.file_label.setText(f"File · {self.path}")
        self.position_label.setText(
            f"Validation {self.current_index + 1} of "
            f"{len(self.document.items)}"
        )
        self.section_label.setText(item.section or "Unsectioned")
        self.item_label.setText(item.text)

        for status, button in self.status_buttons.items():
            button.blockSignals(True)
            button.setChecked(status == item.status)
            button.blockSignals(False)

        self.comment_edit.setPlainText("\n".join(item.comments))
        self.previous_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(
            self.current_index < len(self.document.items) - 1
        )
        self.refresh_summary()

    def refresh_summary(self) -> None:
        counts = self.document.summary()
        result = "ACCEPTED" if self.document.accepted else "INCOMPLETE"
        self.summary_label.setText(
            " · ".join(
                [
                    f"PASS {counts['PASS']}",
                    f"FAIL {counts['FAIL']}",
                    f"QUESTION {counts['QUESTION']}",
                    f"NOT TESTED {counts['NOT TESTED']}",
                    f"Result: {result}",
                ]
            )
        )

    def set_status(self, status: str) -> None:
        for value, button in self.status_buttons.items():
            button.blockSignals(True)
            button.setChecked(value == status)
            button.blockSignals(False)
        self.commit_current_edits()
        self.refresh_summary()

    def previous_item(self) -> None:
        self.commit_current_edits()
        if self.current_index > 0:
            self.current_index -= 1
        self.load_item()

    def next_item(self) -> None:
        self.commit_current_edits()
        if self.current_index < len(self.document.items) - 1:
            self.current_index += 1
        self.load_item()

    def next_unresolved(self) -> None:
        self.commit_current_edits()
        count = len(self.document.items)
        for offset in range(1, count + 1):
            candidate = (self.current_index + offset) % count
            if self.document.items[candidate].status != "PASS":
                self.current_index = candidate
                self.load_item()
                return
        QMessageBox.information(
            self,
            "Smoke Test",
            "No unresolved validation items remain.",
        )

    def save_document(self) -> None:
        self.commit_current_edits()
        self.document.save(self.path)
        self.refresh_summary()
        result = "ACCEPTED" if self.document.accepted else "INCOMPLETE"
        self.statusBar().showMessage(
            f"Saved {self.path} · {result}",
            3500,
        )

    def open_file(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Open smoke test Markdown",
            str(self.path.parent),
            "Markdown files (*.md);;All files (*)",
        )
        if not selected:
            return
        candidate = Path(selected)
        document = SmokeTestDocument.load(candidate)
        if not document.items:
            QMessageBox.warning(
                self,
                "Smoke Test",
                "The selected file contains no supported validation items.",
            )
            return
        self.path = candidate
        self.document = document
        self.current_index = 0
        self.load_item()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run/edit the ICT Cockpit manual smoke-test checklist."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="docs/SMOKE_TEST.md",
        help="Markdown checklist path (default: docs/SMOKE_TEST.md)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    if not path.exists():
        print(f"Smoke-test file not found: {path}", file=sys.stderr)
        return 2

    app = QApplication.instance() or QApplication(sys.argv)
    try:
        window = SmokeTestRunnerWindow(path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
