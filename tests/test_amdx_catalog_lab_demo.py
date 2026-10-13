from pathlib import Path
import sys

import pytest

from ict_cockpit.analysis.amdx import Role, XSubtype

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from amdx_catalog_lab_demo import open_demo


def test_retained_trial_can_reopen_anytime_and_presets_do_not_overwrite_entry(tmp_path):
    directory = tmp_path / "trial"
    connection, window = open_demo(directory)
    pane = window.catalog_lab_widget
    catalog_id = pane.catalog.id
    pane.choose(Role.M)
    pane.select_cell(6, 1)
    pane.choose(Role.X, XSubtype.REVERSAL)
    menu = window.menuBar().actions()[0].menu()
    menu.actions()[1].trigger()
    assert pane.reference().year == 1985 and pane.target.cycle.layer == "year"
    pane.choose(Role.D)
    assert len(pane.repository.history(catalog_id).claims) == 3
    window.close()
    window.deleteLater()
    connection.close()
    connection, window = open_demo(directory)
    try:
        pane = window.catalog_lab_widget
        assert pane.catalog.id == catalog_id
        assert pane.reference().year == 1985 and pane.target.cycle.layer == "year"
        assert pane.table.item(2, 5).text() == "AMDX"
        window.menuBar().actions()[0].menu().actions()[0].trigger()
        assert pane.table.item(6, 5).text() == "XAMD"
        assert "X(R)" in pane.table.item(6, 1).text()
        assert len(pane.repository.history(catalog_id).claims) == 3
        assert not connection.execute("SELECT * FROM trading_session_run").fetchall()
    finally:
        window.close()
        window.deleteLater()
        connection.close()


def test_trial_refuses_unrelated_files_without_overwriting_them(tmp_path):
    file = tmp_path / "notes.txt"
    file.write_text("keep")
    with pytest.raises(ValueError, match="empty"):
        open_demo(tmp_path)
    assert file.read_text() == "keep"
