from datetime import datetime
import json
import sqlite3

import pytest
from PySide6.QtCore import QDate, QSettings, QTime, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ict_cockpit.analysis.amdx import Profile, Role, XSubtype
from ict_cockpit.analysis.amdx_catalog import Catalog
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.amdx_catalog_widget import AMDXCatalogWidget, historical_reference
from ict_cockpit.gui.main_window import MainWindow


REFERENCE = datetime(1998, 5, 12, 9, 15, tzinfo=MARKET_TIMEZONE)
NOW = datetime(2026, 10, 13, 10, tzinfo=MARKET_TIMEZONE)


@pytest.fixture
def pane(tmp_path):
    path = tmp_path / "lab.db"
    connection = open_application_database(path)
    repo = AMDXRepository(connection).catalog
    widget = AMDXCatalogWidget(repo, reference=REFERENCE, clock=lambda: NOW)
    widget.resize(1344, 756)
    widget.show()
    widget.create_catalog("Synthetic MNQ study", definition_ref="candidate:r1")
    QApplication.processEvents()
    yield widget, repo, connection, path
    widget.close()
    widget.deleteLater()
    connection.close()


def commands(connection):
    return connection.execute("SELECT COUNT(*) FROM amdx_catalog_command").fetchone()[0]


def test_full_stack_and_adjacent_real_click_record_without_run_or_save(pane):
    widget, repo, connection, _ = pane
    assert widget.table.rowCount() == 7
    assert widget.target.cycle.layer == "session" and widget.target.quarter_id.endswith("Q3")
    assert not widget.phase_buttons[Role.A].isEnabled()
    QTest.mouseClick(widget.phase_buttons[Role.M], Qt.MouseButton.LeftButton)
    saved = repo.history(widget.catalog.id).claims[-1]
    assert saved.inference.candidates == (Profile.XAMD,)
    assert saved.market_reference == REFERENCE and saved.recorded_at == NOW
    assert "entered" in widget.table.item(6, 3).text()
    assert "implied" in widget.table.item(6, 1).text()
    assert widget.table.item(6, 5).text() == "XAMD"
    assert "Recorded" in widget.status_label.text()
    assert not connection.execute("SELECT * FROM trading_session_run").fetchall()


@pytest.mark.parametrize("row", range(7))
def test_each_visible_layer_has_actual_quarter_entry(pane, row):
    widget, repo, _, _ = pane
    cell = widget.table.visualItemRect(widget.table.item(row, 3)).center()
    QTest.mouseClick(widget.table.viewport(), Qt.MouseButton.LeftButton, pos=cell)
    selected = widget.target
    QTest.mouseClick(widget.phase_buttons[Role.D], Qt.MouseButton.LeftButton)
    claim = repo.history(widget.catalog.id).claims[-1]
    assert claim.cycle == selected.cycle and claim.action_quarter_id == selected.quarter_id
    assert claim.inference.candidates == (Profile.AMDX,)


@pytest.mark.parametrize("subtype", list(XSubtype))
def test_direct_one_click_subtype_and_structural_limits(pane, subtype):
    widget, repo, _, _ = pane
    widget.select_cell(2, 1)
    assert widget.phase_buttons[Role.A].isEnabled()
    assert not widget.phase_buttons[Role.M].isEnabled()
    QTest.mouseClick(widget.subtype_buttons[subtype], Qt.MouseButton.LeftButton)
    assert repo.history(widget.catalog.id).claims[-1].inference.roles[0].subtype is subtype


def test_keyboard_selection_and_session_navigation_record_nothing(pane):
    widget, _, connection, _ = pane
    widget.table.setFocus()
    QTest.keyClick(widget.table, Qt.Key.Key_Left)
    assert widget.target.quarter_id.endswith("Q2")
    for name in ("Asia", "London", "NYAM", "NYPM"):
        QTest.mouseClick(widget.session_buttons[name], Qt.MouseButton.LeftButton)
        assert name in widget.table.item(6, 0).text()
    widget.previous_button.click()
    widget.channel_selector.setCurrentText("Expected")
    widget.reload_button.click()
    assert commands(connection) == 0


def test_expected_observed_and_two_catalogs_never_borrow_heads(pane):
    widget, repo, _, _ = pane
    first_id = widget.catalog.id
    widget.choose(Role.M)
    first = repo.history(first_id).claims[-1]
    widget.channel_selector.setCurrentText("Expected")
    assert widget.target.expected_head_id is None
    widget.choose(Role.D)
    other = widget.create_catalog("Method 2")
    assert widget.target.expected_head_id is None
    widget.choose(Role.M)
    widget.catalog_selector.setCurrentIndex(widget.catalog_selector.findData(first_id))
    assert widget.target.expected_head_id != first.id
    widget.channel_selector.setCurrentText("Observed")
    assert widget.target.expected_head_id == first.id
    assert len(repo.history(first_id).claims) == 2 and len(repo.history(other.id).claims) == 1


def test_preferences_restore_exact_reference_target_channel_and_metadata_draft(pane):
    widget, repo, connection, path = pane
    widget.set_reference("1985-06-10T10:30:00-04:00")
    widget.channel_selector.setCurrentText("Expected")
    widget.select_cell(2, 4)
    widget.evidence_input.setText("chart:1985")
    widget.definition_input.setText("candidate:r2")
    widget.availability_input.setText("1985-06-10T10:00:00-04:00")
    widget.choose(Role.X, XSubtype.CONTINUATION)
    original = widget.target
    other = open_application_database(path)
    restored = AMDXCatalogWidget(AMDXRepository(other).catalog, clock=lambda: NOW)
    try:
        assert restored.target == original
        assert restored.evidence_input.text() == "chart:1985"
        assert restored.definition_input.text() == "candidate:r2"
        assert restored.availability_input.text().startswith("1985-06-10")
        assert restored.table.item(2, 5).text() == "AMDX"
        assert commands(other) == 1
    finally:
        restored.close()
        restored.deleteLater()
        other.close()


@pytest.mark.parametrize("change", ["date", "quarter", "channel", "catalog", "metadata", "active"])
def test_pressed_gesture_cannot_cross_navigation_or_metadata(pane, change):
    widget, _, connection, _ = pane
    if change == "catalog":
        other = widget.create_catalog("Other")
        widget.catalog_selector.setCurrentIndex(0)
    button = widget.phase_buttons[Role.M]
    QTest.mousePress(button, Qt.MouseButton.LeftButton)
    if change == "date":widget.date_input.setDate(QDate(1998, 5, 13))
    elif change == "quarter":widget.select_cell(2, 3)
    elif change == "channel":widget.channel_selector.setCurrentText("Expected")
    elif change == "catalog":widget.catalog_selector.setCurrentIndex(widget.catalog_selector.findData(other.id))
    elif change == "metadata":widget.evidence_input.setText("different evidence")
    else:widget.set_active(False)
    QTest.mouseRelease(button, Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    assert commands(connection) == 0


def test_write_failure_disables_until_explicit_reload_without_replay(pane):
    widget, repo, connection, _ = pane
    widget.choose(Role.D)
    prior = repo.history(widget.catalog.id).claims[-1]
    connection.execute("CREATE TRIGGER fail_lab BEFORE INSERT ON amdx_catalog_command BEGIN SELECT RAISE(ABORT,'fault'); END")
    widget.choose(Role.M)
    assert "not recorded" in widget.status_label.text()
    assert not widget.phase_buttons[Role.M].isEnabled()
    assert repo.history(widget.catalog.id).claims == (prior,)
    connection.execute("DROP TRIGGER fail_lab")
    widget.reload_button.click()
    assert commands(connection) == 1
    widget.choose(Role.M)
    assert commands(connection) == 2


def test_stale_external_head_requires_reload(pane):
    widget, repo, connection, _ = pane
    repo.revise(widget.target, command_id="external", recorded_at=NOW, role=Role.D,
                anchor_id="external-anchor", source_ref="external")
    widget.choose(Role.M)
    assert "not recorded" in widget.status_label.text()
    assert commands(connection) == 1
    widget.reload_button.click()
    assert widget.table.item(6, 5).text() == "AMDX"
    widget.choose(Role.M)
    assert commands(connection) == 2


def test_post_commit_read_failure_reports_recorded_but_unavailable(pane, monkeypatch):
    widget, repo, connection, _ = pane
    original = repo.load_stack
    def fail(*args, **kwargs):raise sqlite3.OperationalError("read fault")
    monkeypatch.setattr(repo, "load_stack", fail)
    widget.choose(Role.M)
    assert commands(connection) == 1
    assert "recorded, but" in widget.status_label.text()
    assert not widget.phase_buttons[Role.M].isEnabled()
    monkeypatch.setattr(repo, "load_stack", original)
    widget.reload_button.click()
    assert widget.table.item(6, 5).text() == "XAMD"
    assert commands(connection) == 1


def test_capture_basis_repeated_no_op_and_invalid_availability(pane):
    widget, repo, connection, _ = pane
    widget.evidence_input.setText("chart:old")
    widget.choose(Role.M)
    widget.choose(Role.M)
    assert commands(connection) == 2 and len(repo.history(widget.catalog.id).claims) == 1
    assert "Unchanged" in widget.status_label.text()
    widget.availability_input.setText("bad")
    QTest.mouseClick(widget.phase_buttons[Role.D], Qt.MouseButton.LeftButton)
    assert commands(connection) == 2 and "not recorded" in widget.status_label.text()
    widget.availability_input.clear()
    widget.reload_button.click()
    widget.choose(Role.D)
    archive = repo.export_archive(widget.catalog.id)
    assert archive["commands"][-1]["request"]["capture"]["evidence_ref"] == "chart:old"


def test_unknown_applicability_and_clear_are_distinct(pane):
    widget, repo, _, _ = pane
    widget.unknown_action.trigger()
    assert repo.history(widget.catalog.id).claims[-1].action_anchor.role is Role.UNKNOWN
    widget.na_action.trigger()
    assert repo.history(widget.catalog.id).claims[-1].applicability
    widget.clear_na_action.trigger()
    assert not repo.history(widget.catalog.id).claims[-1].applicability


def test_dst_ambiguity_and_skipped_time_disable_inaccurate_entry(pane):
    widget, repo, connection, _ = pane
    widget.set_reference("2026-11-01T01:30:00-04:00")
    assert not widget.fold_selector.isHidden()
    widget.select_cell(2, 3)
    widget.choose(Role.M)
    first = repo.history(widget.catalog.id).claims[-1]
    widget.fold_selector.setCurrentIndex(1)
    assert widget.reference().isoformat().endswith("-05:00")
    widget.choose(Role.D)
    second = repo.history(widget.catalog.id).claims[-1]
    assert first.market_reference != second.market_reference
    widget.date_input.setDate(QDate(2026, 3, 8))
    widget.time_input.setTime(QTime(2, 30))
    assert widget.target is None and "did not occur" in widget.status_label.text()
    before = commands(connection)
    widget.choose(Role.M)
    assert commands(connection) == before


def test_absent_restored_catalog_requires_deliberate_selection(pane):
    widget, _, connection, path = pane
    settings = QSettings(str(path.with_name(path.name+".bad.ini")), QSettings.Format.IniFormat)
    settings.setValue("catalog-view-v1", json.dumps({"catalog_id":"missing"}))
    other = AMDXCatalogWidget(widget.repository, settings=settings, reference=REFERENCE)
    try:
        assert other.catalog is None and other.target is None
        other.choose(Role.M)
        assert commands(connection) == 0
        other.catalog_selector.setCurrentIndex(0)
        assert other.target is not None
    finally:
        other.close()
        other.deleteLater()


def test_forward_collection_declares_capture_and_preserves_separate_drafts(pane):
    widget, repo, _, _ = pane
    historical_id = widget.catalog.id
    widget.evidence_input.setText("historical-chart")
    forward = widget.create_catalog("Forward study", purpose="ForwardTest", definition_ref="candidate:f1")
    assert widget.capture_selector.currentIndex() == 1
    assert "Forward entry" in widget.definition_label.text()
    widget.evidence_input.setText("forward-evidence")
    widget.choose(Role.M)
    basis = repo.export_archive(forward.id)["commands"][-1]["request"]["capture"]
    assert basis["kind"] == "ForwardEntry" and basis["evidence_ref"] == "forward-evidence"
    assert basis["information_available_at"] is None
    widget.catalog_selector.setCurrentIndex(widget.catalog_selector.findData(historical_id))
    assert widget.evidence_input.text() == "historical-chart" and widget.capture_selector.currentIndex() == 0


def test_closed_reference_keeps_higher_entry_and_no_intraday_target(pane):
    widget, repo, connection, _ = pane
    widget.set_reference("2026-11-01T12:00:00-05:00")
    assert widget.target is None and widget.table.item(6, 5).text() == "Unavailable"
    assert not widget.session_buttons["Asia"].isEnabled()
    widget.select_cell(6, 3)
    assert commands(connection) == 0 and widget.target is None
    widget.select_cell(2, 3)
    widget.choose(Role.M)
    assert len(repo.history(widget.catalog.id).claims) == 1


def test_level_or_profile_inspection_selects_reference_quarter_without_recording(pane):
    widget, _, connection, _ = pane
    widget.select_cell(2, 0)
    assert widget.target.cycle.layer == "year" and widget.target.quarter_id.endswith("Q2")
    assert widget.table.currentColumn() == 2
    widget.set_reference("2026-10-01T10:00:00-04:00")
    widget.select_cell(3, 5)
    assert widget.target is None  # Unassigned month needs explicit quarter inspection.
    assert commands(connection) == 0


def test_main_window_lab_uses_same_storage_and_cancels_entry_on_tab_exit(pane):
    widget, repo, connection, _ = pane
    window = MainWindow(TDARepository(connection), StudyFindRepository(connection))
    try:
        lab = window.amdx_catalog_widget
        window.tabs.setCurrentWidget(lab)
        assert lab.active and lab.target == widget.target
        window.tabs.setCurrentWidget(window.study_find_widget)
        lab.choose(Role.M)
        assert commands(connection) == 0
        window.tabs.setCurrentWidget(lab)
        lab.clock = lambda: NOW
        lab.choose(Role.M)
        assert len(repo.history(widget.catalog.id).claims) == 1
        assert window.current_feedback_context() == ("AMDX Lab", widget.catalog.id)
    finally:
        window.close()
        window.deleteLater()
