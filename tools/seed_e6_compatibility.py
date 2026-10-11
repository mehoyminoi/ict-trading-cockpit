"""Internal offscreen seed worker; imports only archived accepted E6 source."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import sys


def main():
    directory, source, commit = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    sys.path.insert(0, str(source))
    import ict_cockpit.gui.main_window as window_module
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from ict_cockpit.analysis.trading_session_run import RunEnvironment, RunPurpose
    from ict_cockpit.context_rules import (
        ContextRuleDefinition, ContextConditionDefinition, ContextConditionKind, ContextEffect,
    )
    from ict_cockpit.database.connection import create_connection
    from ict_cockpit.database.schema import initialize_schema
    from ict_cockpit.database.tda_repository import TDARepository
    from ict_cockpit.database.study_find_repository import StudyFindRepository

    if not Path(window_module.__file__).resolve().is_relative_to(source.resolve()):
        raise RuntimeError("Seed must use archived E6 source exclusively")
    app = QApplication([])
    conn = create_connection(directory / "demo.db")
    initialize_schema(conn)
    window = window_module.MainWindow(TDARepository(conn), StudyFindRepository(conn))
    try:
        widget = window.trade_plan_widget.context_import_widget
        rows = [
            {"title": "E6 compatibility release", "country": "USD",
             "date": "2026-10-06T08:30:00-04:00", "impact": "High", "forecast": "2%", "previous": "1%"},
            {"title": "E6 compatibility bank holiday", "country": "AUD",
             "date": "2026-10-04T16:00:00-04:00", "impact": "Holiday", "forecast": "", "previous": ""},
        ]
        original_path = directory / "original.json"
        original_path.write_text(json.dumps(rows), encoding="utf-8")
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        capture = widget.preview_path(original_path, week_start="2026-10-04", imported_at=stamp)
        widget.save_pending_capture()
        widget.use_selected_capture()
        shell = window.trade_plan_widget.trading_day_shell_widget
        shell.run_environment = RunEnvironment.REPLAY
        shell.run_purpose = RunPurpose.REHEARSAL
        shell.run_market_timestamp = datetime.fromisoformat("2026-10-06T10:15:00-04:00")
        assert shell.start_trading_run()
        shell._sync_models_in_play(["silver-bullet"])
        assert shell.runtime.apply_transition("finish-tda", reason="Synthetic compatibility fixture: deliberate incomplete TDA", override_incomplete=True)
        run = shell.active_trading_run
        original_snapshot = json.loads(json.dumps(run.market_context_snapshot))
        revised_path = directory / "revised.json"
        revised_path.write_text(json.dumps([{**row, "previous": "revised"} for row in rows]), encoding="utf-8")
        revised = widget.preview_path(revised_path, week_start="2026-10-04", imported_at=stamp)
        widget.save_pending_capture()
        widget.use_selected_capture()
        assert run.market_context_snapshot == original_snapshot
        assert run.context_rule_snapshot == []
        # Serialize genuine E6 rules separately: Alpha 0.7's run remains rule-free.
        # E7 checks additive-field defaults against these old-writer payloads.
        legacy_rules = [ContextRuleDefinition(
            "e6-legacy-clock", "Synthetic E6 clock only",
            (ContextConditionDefinition(ContextConditionKind.MARKET_CLOCK, after_time="11:00"),),
            ("Replay",), ContextEffect.WARNING, ContextEffect.WARNING, "Compatibility only; unpublished",
        ).to_dict()]
        evidence = dict(
            source_commit=commit, schema=conn.execute("PRAGMA user_version").fetchone()[0],
            trade_plan_revision=run.trade_plan_revision, run_id=run.id,
            capture_id=capture.id, revised_capture_id=revised.id,
            market_context_snapshot=original_snapshot, market_time_context=run.market_time_context,
            context_rule_snapshot=run.context_rule_snapshot, legacy_rules=legacy_rules,
        )
        with sqlite3.connect(directory / "e6-original.db") as backup:
            conn.backup(backup)
        (directory / "e6-origin.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    finally:
        for timer in window.findChildren(QTimer):
            timer.stop()
        window.close()
        conn.close()
        window.deleteLater()
        app.processEvents()
        app.quit()


if __name__ == "__main__":
    main()
