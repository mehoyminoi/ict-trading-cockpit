"""Retained 16:9 trial of the native AMDX Lab widget; separate synthetic catalog."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.gui.amdx_catalog_widget import AMDXCatalogWidget


def open_demo(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / "catalog-lab-fixture.json"
    existing = manifest.exists()
    if not existing and any(directory.iterdir()):
        raise ValueError("Use an empty catalog trial directory; existing files will not be replaced")
    metadata = json.loads(manifest.read_text()) if existing else None
    if existing and (metadata.get("kind") != "AMDX catalog Lab trial v1" or not (directory / "demo.db").exists()):
        raise ValueError("This is not a complete retained catalog Lab trial")
    connection = open_application_database(directory / "demo.db")
    try:
        repo = AMDXRepository(connection).catalog
        pane = AMDXCatalogWidget(repo, reference="1998-05-12T09:15:00-04:00")
        if not existing:
            catalog = pane.create_catalog("MNQ historical trial", definition_ref="Synthetic trial; no adopted rules")
            metadata = dict(kind="AMDX catalog Lab trial v1", catalog_id=catalog.id)
            manifest.write_text(json.dumps(metadata, indent=2))
        else:
            repo.get(metadata["catalog_id"])
        window = QMainWindow()
        window.setWindowTitle("AMDX Lab trial · separate synthetic catalog")
        window.setCentralWidget(pane)
        window.resize(1344, 756)
        notice = QLabel(f"Retained trial · {directory / 'demo.db'} · close and reopen with the same command")
        window.statusBar().addPermanentWidget(notice)
        window.reference_menu_bar = window.menuBar()
        menu = window.reference_menu_bar.addMenu("Study references")
        window.reference_menu = menu
        window.reference_menu_action = menu.menuAction()
        window.reference_actions = []
        for label, reference, row in (
            ("Initial 1998 example · NYAM 90m Q3", "1998-05-12T09:15:00-04:00", 6),
            ("Older 1985 example · Yearly Q3", "1985-08-12T09:15:00-04:00", 2),
        ):
            action = QAction(label, window)
            def navigate(_checked=False, ref=reference, selected=row):
                pane.channel_selector.setCurrentText("Observed")
                pane.set_reference(ref)
                pane.select_cell(selected, 3)
            action.triggered.connect(navigate)
            menu.addAction(action)
            window.reference_actions.append(action)
        window.catalog_lab_widget = pane
        return connection, window
    except Exception:
        if "pane" in locals():
            pane.close()
            pane.deleteLater()
        connection.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(tempfile.gettempdir()) / "ict-amdx-catalog-lab-v1")
    args = parser.parse_args()
    app = QApplication.instance() or QApplication(sys.argv)
    connection, window = open_demo(args.data_dir)
    window.show()
    print(f"Catalog Lab trial database: {args.data_dir / 'demo.db'}", flush=True)
    try:
        return app.exec()
    finally:
        window.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
