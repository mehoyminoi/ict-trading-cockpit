import importlib.util
from pathlib import Path
import subprocess

import pytest
from PySide6.QtCore import QTimer

from ict_cockpit.analysis.context_policy import evaluate_context_rules
from ict_cockpit.context_rules import ContextRuleDefinition
from ict_cockpit.database.context_capture_repository import ContextCaptureRepository
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("e6_compatibility_demo", ROOT / "tools/e6_compatibility_demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def close(conn, window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    conn.close()


def test_actual_e6_writer_restores_in_e7_normal_window_without_reseeding(tmp_path):
    probe = subprocess.run(["git", "cat-file", "-e", f"{demo.E6_COMMIT}:src"], cwd=ROOT, capture_output=True)
    if probe.returncode:
        pytest.skip("Historical E6 commit unavailable in this checkout")
    directory = tmp_path / "sandbox with spaces"
    evidence = demo.prepare_sandbox(directory)
    original_bytes = (directory / "e6-original.db").read_bytes()
    manifest_bytes = (directory / "e6-origin.json").read_bytes()
    assert evidence["schema"] == 37
    assert evidence["trade_plan_revision"] == "Alpha 0.7"
    legacy = evidence["legacy_rules"][0]
    assert "playbook_ids" not in legacy and "not_matched_effect" not in legacy
    assert "event_weekdays" not in legacy["conditions"][0]
    rule = ContextRuleDefinition.from_dict(legacy)
    assert rule.playbook_ids == () and rule.not_matched_effect is None
    result = evaluate_context_rules([rule], environment="Replay",
        market_time_context=evidence["market_time_context"],
        market_context_snapshot=evidence["market_context_snapshot"])[0]
    assert result.state.value == "Not Matched" and result.effect is None
    for attempt in range(2):
        assert demo.prepare_sandbox(directory) == evidence
        conn, window = demo.open_window(directory, evidence)
        try:
            plan = window.trade_plan_widget
            shell = plan.trading_day_shell_widget
            run = shell.active_trading_run
            assert shell.runtime.session.current_mode_id == ("live-watch" if attempt == 0 else "post-market")
            assert run.id == evidence["run_id"]
            assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION == 38
            assert TradingSessionRunRepository(conn).amdx.get_history(run.id).claims == ()
            assert TradingSessionRunRepository(conn).amdx.get_evaluations(run.id) == ()
            assert run.context_rule_snapshot == []
            assert run.market_context_snapshot == evidence["market_context_snapshot"]
            assert shell.market_context_event_provider is None
            assert plan.context_import_widget.captures.count() == 3
            assert plan.context_import_widget.captures.currentText() == "Not Configured"
            captures = ContextCaptureRepository(conn)
            old = captures.get_by_id(evidence["capture_id"])
            revised = captures.get_by_id(evidence["revised_capture_id"])
            assert '"previous": "1%"' in old.raw_payload
            assert '"previous": "revised"' in revised.raw_payload
            # Deliberately selecting the second capture configures only future runs.
            widget = plan.context_import_widget
            widget.captures.setCurrentIndex(widget.captures.findData(revised.id))
            widget.use_selected_capture()
            assert shell.market_context_event_provider is not None
            assert run.market_context_snapshot == evidence["market_context_snapshot"]
            assert all(result.effect is None for result in run.context_rule_results())
            candidate = next(c for c in run.setup_candidates if c.source_type == "Playbook")
            assert run.candidate_authorization(candidate.id).status.value == "Blocked"
            if attempt == 0:
                assert shell.runtime.apply_transition("live-return-analysis", reason="Compatibility workflow check")
                assert shell.runtime.apply_transition("finish-tda", override_incomplete=True)
                assert shell.runtime.apply_transition("live-finish")
        finally:
            close(conn, window)
    assert (directory / "e6-original.db").read_bytes() == original_bytes
    assert (directory / "e6-origin.json").read_bytes() == manifest_bytes


def test_seed_refuses_to_replace_existing_files(tmp_path):
    existing = tmp_path / "demo.db"
    existing.write_bytes(b"operator data")
    with pytest.raises(ValueError, match="empty directory"):
        demo.prepare_sandbox(tmp_path)
    assert existing.read_bytes() == b"operator data"
