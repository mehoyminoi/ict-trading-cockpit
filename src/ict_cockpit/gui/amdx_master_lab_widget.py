"""Normal Lab workspace over the maintained instrument calendar."""
from datetime import datetime
import sqlite3
from uuid import uuid4

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QPushButton

from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.database.amdx_master_repository import MasterAdoptionRequired, MasterTarget
from ict_cockpit.analysis.amdx import payload
from ict_cockpit.database.amdx_repository import StaleAMDXUpdate
from ict_cockpit.gui.amdx_catalog_widget import AMDXCatalogWidget


class _MasterEntries:
    def __init__(self, pane, repository):
        self.pane, self.repository = pane, repository

    def __getattr__(self, name):
        return getattr(self.repository, name)

    def revise(self, target, **arguments):
        if self.pane.run_scope is not None:
            run_id, reference = self.pane.run_scope
            if target.channel != "Expected" or target.market_reference.isoformat() != reference:
                raise ValueError("Run inspection scope changed; return to the study calendar")
            prepared = self.repository.amdx.run_calendar.prepare_capture(run_id, reference=target.market_reference)
            if payload(prepared.snapshot.projection) != payload(self.pane.projection):
                raise StaleAMDXUpdate("Inspected stack changed; reload before choosing")
            args = dict(arguments)
            args["operation_id"] = args.pop("command_id")
            result = self.repository.amdx.run_calendar.revise(prepared, MasterTarget(self.pane.binding, target),
                capture_id=str(uuid4()), **args)
            return result.calendar_result
        request = self.repository._revision_request(target, **arguments)
        with self.repository.amdx._transaction():
            self.pane.master_repository.validate_target(MasterTarget(self.pane.binding, target))
            return self.repository._revise_locked(target, request)


class AMDXMasterLabWidget(AMDXCatalogWidget):
    def __init__(self, master_repository, *, instrument="MNQ", **kwargs):
        self.master_repository = master_repository
        self.instrument = instrument
        self.binding = None
        self.run_scope = None
        self.adoption_required = False
        self.adopt_button = QPushButton("Use existing AMDX data…")
        self.study_button = QPushButton("Study calendar")
        super().__init__(_MasterEntries(self, master_repository.catalog), **kwargs)
        self.heading.setText(f"AMDX Lab · {instrument} maintained calendar")
        self.catalog_selector.hide()
        self.new_button.hide()
        self.layout().itemAt(0).layout().insertWidget(2, self.adopt_button)
        self.layout().itemAt(0).layout().insertWidget(2, self.study_button)
        self.study_button.clicked.connect(self.leave_run_scope)
        self.study_button.hide()
        self.adopt_button.clicked.connect(self._adopt_dialog)
        self.adopt_button.setVisible(self.adoption_required)

    def inspect_run(self, run_id):
        self.run_scope = (run_id, self.reference().isoformat())
        self.study_button.show()
        self.heading.setText(f"AMDX Lab · {self.instrument} · working context for run")

    def leave_run_scope(self):
        self.run_scope = None
        self.study_button.hide()
        self.heading.setText(f"AMDX Lab · {self.instrument} maintained calendar")
        self.capture_selector.setCurrentIndex(0)
        self.channel_selector.setCurrentText("Observed")
        self.refresh()

    def _navigation_changed(self, *args):
        if self.run_scope is not None:
            try:
                changed = self.reference().isoformat() != self.run_scope[1] or self.channel_selector.currentText() != "Expected"
            except ValueError:
                changed = True
            if changed:
                self.run_scope = None
                self.study_button.hide()
                self.heading.setText(f"AMDX Lab · {self.instrument} maintained calendar")
                self.capture_selector.setCurrentIndex(0)
        super()._navigation_changed(*args)

    def _restore(self):
        super()._restore()
        # The canonical binding, not a prior collection preference, owns this view.
        self._restore_catalog_id = None

    def create_catalog(self, *args, **kwargs):
        raise ValueError("The normal Lab uses its maintained instrument calendar")

    def adopt_existing(self, catalog_id):
        self.master_repository.adopt(self.instrument, catalog_id, binding_id=str(uuid4()),
            recorded_at=datetime.now().astimezone(), source_ref="Technician selected maintained Lab calendar")
        self.adoption_required = False
        self._warning = ""
        self.refresh()

    def _adopt_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Choose maintained {self.instrument} AMDX data")
        layout = QFormLayout(dialog)
        explanation = QLabel("Choose the existing data to maintain across Lab, TDA and Watch. Other collections stay saved separately.")
        explanation.setWordWrap(True)
        layout.addRow(explanation)
        selector = QComboBox()
        selector.addItem("Choose existing data…", None)
        for owner in self.repository.list_catalogs(instrument=self.instrument):
            selector.addItem(owner.title, owner.id)
        layout.addRow("Existing data", selector)
        error = QLabel()
        error.setWordWrap(True)
        layout.addRow(error)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addRow(buttons)
        buttons.rejected.connect(dialog.reject)
        def accept():
            try:
                if selector.currentData() is None:
                    raise ValueError("Choose the maintained data deliberately")
                self.adopt_existing(selector.currentData())
            except (ValueError, sqlite3.Error, RuntimeError) as exc:
                error.setText(str(exc))
                return
            dialog.accept()
        buttons.accepted.connect(accept)
        dialog.exec()

    def refresh(self):
        self._invalidate_gesture()
        try:
            exists = self.repository.connection.execute("SELECT 1 FROM amdx_master_binding WHERE instrument=?", (self.instrument,)).fetchone()
            binding = (self.master_repository.resolve(self.instrument) if exists else
                       self.master_repository.ensure(self.instrument, recorded_at=datetime.now().astimezone()))
            self.binding = binding
            with self.repository.amdx.review._snapshot():
                self.catalog = self.repository.get(binding.catalog_id)
                self.catalogs = (self.catalog,)
                with QSignalBlocker(self.catalog_selector):
                    self.catalog_selector.clear()
                    self.catalog_selector.addItem(self.catalog.title, self.catalog.id)
                self._restore_catalog_id = None
                reference = self.reference()
                local = reference.astimezone(MARKET_TIMEZONE)
                self.fold_selector.setVisible(local.replace(fold=0).utcoffset() != local.replace(fold=1).utcoffset())
                self.reference_label.setText(f"{self.instrument} · {reference.isoformat()} · • marks position at reference")
                self.projection = self.master_repository.load_stack(self.instrument, reference=reference,
                    channel=self.channel_selector.currentText()).projection
            self.adoption_required = False
            self.adopt_button.hide()
            self._read_error = False
            self._load_draft()
            self._render_stack()
            self._save_navigation()
            self.status_label.setText(self._warning or "One maintained calendar · choose a quarter and enter immediately.")
        except (ValueError, TypeError, sqlite3.Error, RuntimeError) as exc:
            self.adoption_required = isinstance(exc, MasterAdoptionRequired)
            self.adopt_button.setVisible(self.adoption_required)
            self.catalog = self.projection = self.target = None
            self._read_error = True
            self._render_stack()
            self.status_label.setText("Choose the maintained existing data once using ‘Use existing AMDX data…’." if self.adoption_required
                else f"Calendar unavailable — entry disabled. {exc}. Use Reload after correcting the source.")
