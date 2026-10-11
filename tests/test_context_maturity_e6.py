from dataclasses import replace
from datetime import datetime
from hashlib import sha256
import json
import sqlite3

import pytest

from ict_cockpit.analysis.context_policy import evaluate_context_rules, ContextMatch
from ict_cockpit.analysis.context_source import ContextCoverage
from ict_cockpit.analysis.forex_factory_import import import_forex_factory_json, ImportedCaptureProvider
from ict_cockpit.analysis.market_context_event import (
    MarketContextSnapshot, MarketContextSnapshotStatus, MarketContextTimingPrecision,
    MarketContextQueryResult, capture_market_context_snapshot,
)
from ict_cockpit.analysis.market_context_view import build_market_context_view
from ict_cockpit.analysis.market_time import build_market_time_context, MARKET_TIMEZONE
from ict_cockpit.analysis.trading_session_run import RunEnvironment, RunPurpose
from ict_cockpit.context_rules import ContextRuleDefinition, ContextConditionDefinition, ContextConditionKind, ContextEffect
from ict_cockpit.context_rules import ContextEventWindow
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.context_capture_repository import ContextCaptureRepository
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.context_import_widget import ContextImportWidget
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


ROW = {"title": "Fixture release", "country": "USD", "date": "2026-10-06T08:30:00-04:00",
       "impact": "High", "forecast": "2%", "previous": "1%"}
IMPORT_TIME = "2026-10-10T12:00:00+00:00"


def capture(rows=None, week="2026-10-04"):
    return import_forex_factory_json(json.dumps([ROW] if rows is None else rows).encode(),
        week_start=week, imported_at=IMPORT_TIME, source_reference="fixture://export.json")


def snapshot(item, stamp="2026-10-06T10:15:00-04:00"):
    market = build_market_time_context(datetime.fromisoformat(stamp), source="Historical Reference").to_dict()
    return market, capture_market_context_snapshot(provider=ImportedCaptureProvider(item),
        market_time_context=market, market_timezone=MARKET_TIMEZONE, captured_at=IMPORT_TIME)


def event_rule():
    return ContextRuleDefinition("fixture", "Fixture only", (ContextConditionDefinition(
        ContextConditionKind.EVENT_PRESENT, impacts=("High",)),), ("Replay",),
        ContextEffect.BLOCK_NEW_ENTRY, ContextEffect.WARNING, "Synthetic acceptance rule")


def test_import_preserves_native_rows_identity_provenance_and_uncertainty():
    raw = json.dumps([ROW, {**ROW, "title": "Fixture bank holiday", "impact": "Holiday"}, ROW]).encode()
    item = import_forex_factory_json(raw, week_start="2026-10-04", imported_at=IMPORT_TIME,
                                    source_reference="fixture://export.json")
    assert len(item.events) == 3 and len({e.id for e in item.events}) == 3
    assert item.provenance.content_sha256 == sha256(raw).hexdigest()
    assert item.raw_payload == raw.decode()
    assert item.provenance.adapter_revision and item.provenance.mapping_revision
    for e in item.events:
        assert e.source_event_id == "" and e.normalized_event_type == "" and e.affected_markets == ()
        assert e.status.value == "Unknown" and e.timing_precision is MarketContextTimingPrecision.UNKNOWN
        assert "Capture-local" in e.identity_basis
    assert json.loads(item.events[0].native_record) == ROW
    assert item.events[1].category.value == "Holiday"
    assert "as-of" in item.provenance.knowledge_basis
    assert item.id != capture().id  # imports are separate acquisition acts


@pytest.mark.parametrize("rows", [[], {}, [ROW, {**ROW, "date": "2026-10-13T12:00:00Z"}],
    [{**ROW, "date": "2026-10-06T08:30:00"}], [{**ROW, "date": "bad"}],
    [{"title": "partial"}], [{**ROW, "forecast": None}], [ROW, "bad"]])
def test_bad_or_wrong_week_records_reject_the_entire_capture(rows):
    with pytest.raises(ValueError): capture(rows)


def test_bad_encoding_json_and_week_declaration():
    for raw in (b"<weeklyevents/>", b"\xff", b"[broken"):
        with pytest.raises(ValueError):
            import_forex_factory_json(raw, week_start="2026-10-04", imported_at=IMPORT_TIME, source_reference="fixture")
    with pytest.raises(ValueError): capture(week="2026-10-05")


def test_missing_week_unavailable_and_matching_week_cannot_prove_absence_or_exact_time():
    item = capture()
    market, snap = snapshot(item)
    assert snap.status is MarketContextSnapshotStatus.AVAILABLE
    assert not snap.coverage.complete
    assert snap.source_provenance == item.provenance
    result = evaluate_context_rules([event_rule()], environment="Replay", market_time_context=market,
                                    market_context_snapshot=snap.to_dict())[0]
    assert result.state is ContextMatch.UNKNOWN and result.effect is ContextEffect.WARNING
    _, missing = snapshot(item, "2026-10-13T10:15:00-04:00")
    assert missing.status is MarketContextSnapshotStatus.UNAVAILABLE and not missing.events
    assert missing.source_provenance == item.provenance
    # Native clock uncertainty cannot silently discard a row at a futures-day boundary.
    _, day = snapshot(capture([{**ROW, "date": "2026-10-05T18:00:00-04:00"}, ROW]))
    assert len(day.events) == 2


def test_unknown_status_and_precision_never_appear_as_upcoming_exact_time():
    shell = TradingDayShellWidget(build_default_trade_plan().process_blueprint,
        run_environment=RunEnvironment.REPLAY, market_context_event_provider=ImportedCaptureProvider(capture()))
    shell.run_market_timestamp = datetime.fromisoformat("2026-10-06T07:00:00-04:00")
    assert shell.start_trading_run()
    run = shell.active_trading_run
    view = build_market_context_view(run, mode_id="live-watch")
    assert "Next recorded time" not in view.events
    assert "uncertain" in view.events.lower()
    assert "Schedule fact:" not in view.events
    for text in ("forex-factory-json-v0", "SHA-256", "Capture-local", "Native record", "completeness", "as-of"):
        assert text.lower() in view.detail.lower()
    assert run.context_rule_snapshot == []
    shell.close()


def test_legacy_query_success_and_legacy_snapshot_are_not_completeness_claims():
    class OldProvider:
        provider_name = "Old fixture"
        def events_between(self, start, end): return ()
    market = build_market_time_context(datetime.fromisoformat("2026-10-06T10:15:00-04:00"), source="Historical Reference").to_dict()
    snap = capture_market_context_snapshot(provider=OldProvider(), market_time_context=market,
        market_timezone=MARKET_TIMEZONE, captured_at=IMPORT_TIME)
    for payload in (snap.to_dict(), {k: v for k, v in snap.to_dict().items() if k not in {"coverage", "source_provenance"}}):
        result = evaluate_context_rules([event_rule()], environment="Replay", market_time_context=market,
                                       market_context_snapshot=payload)[0]
        assert result.state is ContextMatch.UNKNOWN


def test_coverage_requires_both_window_and_selector_scope():
    condition = event_rule().conditions[0]
    start, end = datetime.fromisoformat("2026-10-06T00:00:00Z"), datetime.fromisoformat("2026-10-07T00:00:00Z")
    complete = ContextCoverage(start.isoformat(), end.isoformat(), True, ("*",), ("*",), ("High",), ("*",), "Synthetic source guarantee")
    assert complete.covers(condition, start, end)
    assert not replace(complete, impacts=("Low",)).covers(condition, start, end)
    assert not replace(complete, event_types=()).covers(condition, start, end)
    assert not replace(complete, end=start.isoformat()).covers(condition, start, end)
    assert not replace(complete, complete=False).covers(condition, start, end)
    with pytest.raises(ValueError): ContextCoverage(complete="yes")
    with pytest.raises(ValueError): ContextCoverage(start="2026-10-06T00:00", end=end.isoformat())


def test_clock_is_not_precision_and_source_week_facts_are_not_request_bounds():
    item = capture()
    legacy = item.events[0].to_dict(); legacy.pop("timing_precision")
    assert type(item.events[0]).from_dict(legacy).timing_precision is MarketContextTimingPrecision.UNKNOWN
    market, snap = snapshot(item)
    # A future provider can supply factual week data around a day request.
    known = replace(item.events[0], scheduled_at="2026-10-09T08:30:00-04:00", status="Scheduled", timing_precision="Exact")
    r = event_rule()
    r = replace(r, conditions=(replace(r.conditions[0], event_window=ContextEventWindow.CALENDAR_WEEK),))
    result = evaluate_context_rules([r], environment="Replay", market_time_context=market,
        market_context_snapshot=replace(snap, events=(known,)).to_dict())[0]
    assert result.state is ContextMatch.MATCHED


def test_bom_payload_digest_and_duplicate_fields():
    raw = b"\xef\xbb\xbf" + json.dumps([ROW]).encode()
    item = import_forex_factory_json(raw, week_start="2026-10-04", imported_at=IMPORT_TIME, source_reference="fixture")
    assert sha256(item.raw_payload.encode("utf-8")).hexdigest() == item.provenance.content_sha256
    duplicate = json.dumps([ROW]).replace('"title": "Fixture release"', '"title": "Fixture release", "title": "Changed"')
    with pytest.raises(ValueError):
        import_forex_factory_json(duplicate.encode(), week_start="2026-10-04", imported_at=IMPORT_TIME, source_reference="fixture")


def test_invalid_source_result_is_unavailable_and_string_scope_is_rejected():
    class InvalidProvider:
        provider_name = "Invalid fixture"
        def query_context(self, start, end):
            return MarketContextQueryResult(events=({"title": "Missing required fields"},))
    market = snapshot(capture())[0]
    result = capture_market_context_snapshot(provider=InvalidProvider(), market_time_context=market,
        market_timezone=MARKET_TIMEZONE, captured_at=IMPORT_TIME)
    assert result.status is MarketContextSnapshotStatus.UNAVAILABLE
    assert not result.coverage.complete
    with pytest.raises(ValueError): ContextCoverage(affected_markets="USD")


def test_normal_main_window_exposes_import_and_restores_with_no_implicit_source(tmp_path):
    from PySide6.QtCore import QTimer
    from ict_cockpit.database.tda_repository import TDARepository
    from ict_cockpit.database.study_find_repository import StudyFindRepository
    from ict_cockpit.gui.main_window import MainWindow
    path = tmp_path / "normal.db"
    conn = create_connection(path); initialize_schema(conn)
    window = MainWindow(TDARepository(conn), StudyFindRepository(conn))
    plan = window.trade_plan_widget
    widget = plan.context_import_widget
    assert plan.process_tabs.tabText(plan.process_tabs.indexOf(widget)) == "Calendar captures"
    source = tmp_path / "source.json"; source.write_text(json.dumps([ROW]))
    widget.preview_path(source, week_start="2026-10-04", imported_at=IMPORT_TIME)
    widget.save_pending_capture(); widget.use_selected_capture()
    shell = plan.trading_day_shell_widget
    shell.run_environment = RunEnvironment.REPLAY
    shell.run_purpose = RunPurpose.REHEARSAL
    shell.run_market_timestamp = datetime.fromisoformat("2026-10-06T10:15:00-04:00")
    assert shell.start_trading_run()
    original = shell.active_trading_run.market_context_snapshot
    for timer in window.findChildren(QTimer): timer.stop()
    window.close(); conn.close()
    conn = create_connection(path); initialize_schema(conn)
    reopened = MainWindow(TDARepository(conn), StudyFindRepository(conn))
    shell = reopened.trade_plan_widget.trading_day_shell_widget
    assert shell.active_trading_run.market_context_snapshot == original
    assert shell.market_context_event_provider is None
    assert reopened.trade_plan_widget.context_import_widget.captures.count() == 2
    for timer in reopened.findChildren(QTimer): timer.stop()
    reopened.close(); conn.close()


def test_selection_change_invalidates_an_unsaved_preview(tmp_path):
    conn = create_connection(tmp_path / "preview.db"); initialize_schema(conn)
    repo = ContextCaptureRepository(conn); repo.save(capture())
    shell = TradingDayShellWidget(build_default_trade_plan().process_blueprint)
    widget = ContextImportWidget(repo, shell)
    widget.captures.setCurrentIndex(1)
    path = tmp_path / "preview.json"; path.write_text(json.dumps([ROW]))
    widget.preview_path(path, week_start="2026-10-04", imported_at=IMPORT_TIME)
    assert widget.pending_capture is not None and widget.save_button.isEnabled()
    widget.captures.setCurrentIndex(0)
    assert widget.pending_capture is None and not widget.save_button.isEnabled()
    assert not widget.preview.toPlainText()
    widget.save_pending_capture()
    assert len(repo.list_all()) == 1
    widget.close(); shell.close(); conn.close()


def test_capture_repository_restart_immutability_and_v36_migration(tmp_path):
    path = tmp_path / "e6.db"
    conn = create_connection(path); initialize_schema(conn)
    # Simulate the prior schema: new migration creates only source storage.
    conn.execute("DROP TABLE context_source_capture")
    conn.execute("PRAGMA user_version = 36"); conn.commit()
    initialize_schema(conn); initialize_schema(conn)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 37
    repo = ContextCaptureRepository(conn)
    original = capture(); repo.save(original); repo.save(original)
    with pytest.raises(ValueError): repo.save(replace(original, raw_payload="changed"))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE context_source_capture SET payload_json = '{}' WHERE id = ?", (original.id,))
    conn.close()
    conn = create_connection(path); initialize_schema(conn)
    assert ContextCaptureRepository(conn).get_by_id(original.id) == original
    conn.close()


def test_preview_save_selection_run_restore_and_new_import_do_not_rewrite_history(tmp_path):
    conn = create_connection(tmp_path / "loop.db"); initialize_schema(conn)
    repo = ContextCaptureRepository(conn)
    shell = TradingDayShellWidget(build_default_trade_plan().process_blueprint, run_environment=RunEnvironment.REPLAY)
    widget = ContextImportWidget(repo, shell)
    path = tmp_path / "fixture.json"; path.write_text(json.dumps([ROW]))
    first = widget.preview_path(path, week_start="2026-10-04", imported_at=IMPORT_TIME)
    assert not repo.list_all() and shell.market_context_event_provider is None
    widget.save_pending_capture()
    assert repo.get_by_id(first.id) == first and shell.market_context_event_provider is None
    widget.use_selected_capture()
    shell.run_market_timestamp = datetime.fromisoformat("2026-10-06T10:15:00-04:00")
    assert shell.start_trading_run()
    run = shell.active_trading_run
    before = json.dumps(run.market_context_snapshot, sort_keys=True)
    TradingDayRepository(conn).save(shell.trading_day)
    TradingDaySessionRepository(conn).save(shell.runtime.session)
    runs = TradingSessionRunRepository(conn); runs.save(run)
    path.write_text(json.dumps([{**ROW, "previous": "revised"}]))
    second = widget.preview_path(path, week_start="2026-10-04", imported_at=IMPORT_TIME)
    widget.save_pending_capture(); widget.use_selected_capture()
    assert second.id != first.id
    restored = runs.get_by_id(run.id)
    assert json.dumps(restored.market_context_snapshot, sort_keys=True) == before
    assert restored.market_context_snapshot["events"][0]["previous"] == "1%"
    # Reopen capture selection without turning the latest import into an implicit provider.
    other_shell = TradingDayShellWidget(build_default_trade_plan().process_blueprint)
    reopened = ContextImportWidget(repo, other_shell)
    assert reopened.captures.currentData() == "" and other_shell.market_context_event_provider is None
    assert reopened.captures.count() == 3
    conn.close(); widget.close(); shell.close(); reopened.close(); other_shell.close()


@pytest.mark.parametrize("stamp,week", [
    ("2026-11-01T06:30:00Z", "2026-11-01"),
    ("2026-03-08T07:30:00Z", "2026-03-08"),
])
def test_dst_offsets_preserved_without_assigning_exact_precision(stamp, week):
    item = capture([{**ROW, "date": stamp}], week=week)
    assert item.events[0].scheduled_at == stamp
    assert item.events[0].timing_precision is MarketContextTimingPrecision.UNKNOWN
