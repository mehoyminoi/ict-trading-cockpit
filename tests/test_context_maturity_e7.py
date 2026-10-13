from copy import deepcopy
from dataclasses import replace
from datetime import datetime
import json

import pytest

from ict_cockpit.context_rules import (
    ContextConditionDefinition as Condition, ContextConditionKind as Kind,
    ContextEffect as Effect, ContextEventWindow as Window, ContextRuleDefinition as Rule,
)
from ict_cockpit.analysis.context_policy import ContextMatch as Match, evaluate_context_rules
from ict_cockpit.analysis.context_source import ContextCoverage
from ict_cockpit.analysis.forex_factory_import import import_forex_factory_json
from ict_cockpit.analysis.market_context_event import (
    MarketContextEvent as Event, MarketContextEventCategory as Category,
    MarketContextSnapshot as Snapshot, MarketContextSnapshotStatus as Availability,
)
from ict_cockpit.analysis.market_time import build_market_time_context
from ict_cockpit.analysis.trading_session_run import (
    AuthorizationStatus, RunEnvironment, SetupCandidate, TradingSessionRun,
)
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION, initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.market_context_widget import MarketContextWidget
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


MONDAY_START = "2026-10-05T00:00:00-04:00"
MONDAY_END = "2026-10-05T23:59:59.999999-04:00"
TARGET = "fixture-friday"


def market(stamp="2026-10-09T10:15:00-04:00"):
    return build_market_time_context(datetime.fromisoformat(stamp), source="Historical Reference").to_dict()


def rule(**changes):
    base = Rule(
        "fixture-absence", "Fixture no Monday high-impact events",
        (Condition(Kind.EVENT_ABSENT, event_window=Window.CALENDAR_WEEK,
                   event_weekdays=(0,), category=Category.ECONOMIC, impacts=("High",)),),
        ("Replay",), Effect.INFORMATIONAL, Effect.WARNING,
        "Unpublished fixture: Monday of the reference calendar week, not an adopted trading rule.",
        playbook_ids=(TARGET,), not_matched_effect=Effect.BLOCK_NEW_ENTRY,
    )
    return replace(base, **changes)


def snapshot(events=(), *, start=MONDAY_START, end=MONDAY_END, complete=True, status=Availability.AVAILABLE):
    coverage = ContextCoverage(start, end, complete, ("*",), ("*",), ("*",), ("*",), "Explicit synthetic source guarantee")
    return Snapshot(status, "Fixture", "2026-10-08T18:00:00-04:00", "2026-10-09T17:59:59.999999-04:00",
                    "2026-10-09T10:15:00-04:00", "Historical Reference", "2026-10-10T12:00:00+00:00",
                    events, coverage=coverage).to_dict()


def event(**changes):
    return Event(**{**dict(id="monday", provider="Fixture", source_event_id="monday-native",
                          category=Category.ECONOMIC, normalized_event_type="FIXTURE",
                          title="Native fixture", scheduled_at="2026-10-05T08:30:00-04:00",
                          impact="High", status="Scheduled", timing_precision="Exact"), **changes})


def evaluate(r=None, *, s=None, m=None, playbook=TARGET, environment="Replay"):
    return evaluate_context_rules([r or rule()], environment=environment, playbook_id=playbook,
                                  market_time_context=m or market(), market_context_snapshot=s if s is not None else snapshot())[0]


def candidate(name, source_id, *, source_type="Playbook"):
    return SetupCandidate(name, source_type=source_type, source_id=source_id,
                          source_revision="fixture-v0", definition_snapshot={
                              "id": source_id, "revision": "fixture-v0",
                              "entry_criteria": [{"id": "fixture", "name": "Fixture criterion"}],
                              "required_entry_count": 1,
                          }, entry_condition_states={"fixture": True})


def configure(run):
    run.market_time_context = market()
    run.market_context_snapshot = snapshot((event(),))
    run.context_rule_snapshot = [rule().to_dict()]
    run.setup_candidates = [candidate("Target", TARGET), candidate("Other model", "fixture-other"),
                            candidate("Custom setup", TARGET, source_type="Custom")]
    for gate in run.authorization_policy_snapshot:
        if gate["scope"] == "Run":
            run.set_authorization_gate(gate["id"], "Clear")
        else:
            for item in run.setup_candidates:
                run.set_candidate_authorization_gate(item.id, gate["id"], "Clear")
    return run


def test_absence_uses_explicit_complete_monday_scope_and_retains_counterexample_ids():
    empty = evaluate()
    assert empty.state is Match.MATCHED and empty.effect is Effect.INFORMATIONAL
    assert "2026-10-05T00:00:00-04:00" in empty.reasons[0]
    present = evaluate(s=snapshot((event(),)))
    assert present.state is Match.NOT_MATCHED and present.blocks_new_entry
    assert present.event_ids == ("monday",)
    assert evaluate(s=snapshot((event(scheduled_at="2026-10-06T08:30:00-04:00"),))).state is Match.MATCHED


@pytest.mark.parametrize("changes", [
    {"timing_precision": "Unknown"}, {"status": "Tentative"}, {"status": "Unknown"},
    {"impact": "Unknown"},
])
def test_absence_never_inverts_uncertain_source_facts_into_a_positive(changes):
    result = evaluate(s=snapshot((event(**changes),)))
    assert result.state is Match.UNKNOWN and result.effect is Effect.WARNING
    assert not result.blocks_new_entry
    assert result.event_ids == ("monday",)


@pytest.mark.parametrize("status", [Availability.UNAVAILABLE, Availability.NOT_CONFIGURED])
def test_missing_sources_keep_absence_unknown_with_configured_effect(status):
    result = evaluate(rule(unknown_effect=Effect.BLOCK_NEW_ENTRY), s=snapshot(status=status))
    assert result.state is Match.UNKNOWN and result.blocks_new_entry


def test_absence_needs_every_selected_day_and_full_selector_scope():
    assert evaluate(s=snapshot(complete=False)).state is Match.UNKNOWN
    payload = snapshot()
    payload["coverage"]["impacts"] = ["Low"]
    assert evaluate(s=payload).state is Match.UNKNOWN
    r = rule(conditions=(replace(rule().conditions[0], event_weekdays=(0, 2)),))
    assert evaluate(r).state is Match.UNKNOWN
    assert evaluate(r, s=snapshot(end="2026-10-07T23:59:59.999999-04:00")).state is Match.MATCHED


@pytest.mark.parametrize("offset,start,end", [
    (-1, "2026-09-28T00:00:00-04:00", "2026-09-28T23:59:59.999999-04:00"),
    (1, "2026-10-12T00:00:00-04:00", "2026-10-12T23:59:59.999999-04:00"),
])
def test_calendar_week_relationship_is_explicit_not_inferred_from_model_name(offset, start, end):
    r = rule(conditions=(replace(rule().conditions[0], calendar_week_offset=offset),))
    assert evaluate(r).state is Match.UNKNOWN
    result = evaluate(r, s=snapshot(start=start, end=end))
    assert result.state is Match.MATCHED and start in result.reasons[0]


@pytest.mark.parametrize("stamp,start,end", [
    ("2026-03-06T10:15:00-05:00", "2026-03-08T05:00:00Z", "2026-03-09T03:59:59.999999Z"),
    ("2026-10-30T10:15:00-04:00", "2026-11-01T04:00:00Z", "2026-11-02T04:59:59.999999Z"),
])
def test_selected_calendar_day_uses_ny_civil_boundaries_across_dst(stamp, start, end):
    r = rule(conditions=(replace(rule().conditions[0], event_weekdays=(6,)),))
    assert evaluate(r, m=market(stamp), s=snapshot(start=start, end=end)).state is Match.MATCHED
    shortened_end = end.replace("59:59.999999", "59:59.999998")
    assert evaluate(r, m=market(stamp), s=snapshot(start=start, end=shortened_end)).state is Match.UNKNOWN


def test_real_import_keeps_absence_unknown_even_when_native_row_is_on_another_day():
    raw = json.dumps([{"title": "Native event", "country": "USD", "date": "2026-10-06T08:30:00-04:00",
                       "impact": "High", "forecast": "", "previous": ""}]).encode()
    imported = import_forex_factory_json(raw, week_start="2026-10-04",
                                        imported_at="2026-10-10T12:00:00Z", source_reference="fixture.json")
    result = evaluate(s=snapshot(imported.events, complete=False))
    assert result.state is Match.UNKNOWN
    assert result.event_ids == (imported.events[0].id,)


@pytest.mark.parametrize("playbook", [None, "fixture-other"])
def test_scoped_rule_is_not_applicable_before_missing_data_is_evaluated(playbook):
    result = evaluate(s={}, playbook=playbook)
    assert result.state is Match.NOT_APPLICABLE and result.effect is None


def test_candidate_scope_is_by_stored_source_identity_and_never_leaks_to_other_or_custom_setups():
    plan = build_default_trade_plan()
    run = configure(TradingSessionRun("day", "NYAM", "session", environment=RunEnvironment.REPLAY,
                                     authorization_policy_snapshot=plan.authorization_snapshot()))
    before = deepcopy(run.__dict__)
    assert run.context_rule_results()[0].state is Match.NOT_APPLICABLE
    assert run.candidate_authorization(run.setup_candidates[0].id).status is AuthorizationStatus.BLOCKED
    assert all(run.candidate_authorization(x.id).status is AuthorizationStatus.AUTHORIZED for x in run.setup_candidates[1:])
    assert run.__dict__ == before
    run.market_context_snapshot = snapshot()
    run.set_authorization_gate("trading-day-permitted", "Pending")
    assert run.candidate_authorization(run.setup_candidates[0].id).status is AuthorizationStatus.BLOCKED


def test_new_definition_roundtrip_and_legacy_defaults_preserve_existing_rule_semantics():
    r = rule()
    assert Rule.from_dict(json.loads(json.dumps(r.to_dict()))) == r
    legacy = r.to_dict()
    for name in ("playbook_ids", "not_matched_effect"):
        legacy.pop(name)
    term = legacy["conditions"][0]
    term["kind"] = Kind.EVENT_PRESENT.value
    term.pop("event_weekdays"); term.pop("calendar_week_offset")
    restored = Rule.from_dict(legacy)
    assert restored.playbook_ids == () and restored.not_matched_effect is None
    assert restored.conditions[0].event_weekdays == ()
    assert restored.conditions[0].calendar_week_offset == 0
    assert evaluate(restored, s=snapshot(start="2026-10-05T00:00:00-04:00", end="2026-10-11T23:59:59.999999-04:00")).effect is None


@pytest.mark.parametrize("changes", [
    {"event_weekdays": (7,)}, {"event_weekdays": (0, 0)}, {"calendar_week_offset": True},
    {"calendar_week_offset": 1.5}, {"event_window": Window.FUTURES_DAY},
])
def test_calendar_selector_validation_rejects_ambiguous_or_invalid_definitions(changes):
    with pytest.raises(ValueError):
        replace(rule().conditions[0], **changes)


@pytest.mark.parametrize("field", ["effect", "unknown_effect", "not_matched_effect"])
def test_day_stand_down_cannot_be_mislabeled_as_a_playbook_effect(field):
    with pytest.raises(ValueError, match="run-wide"):
        rule(**{field: Effect.STAND_DOWN_DAY})


def test_trade_plan_owns_scope_references_and_default_policy_is_unchanged():
    plan = build_default_trade_plan()
    with pytest.raises(ValueError, match="unknown playbooks"):
        replace(plan, context_rules=(rule(),))
    actual_id = plan.playbooks[0].id
    replace(plan, context_rules=(rule(playbook_ids=(actual_id,)),))
    assert plan.revision == "Alpha 0.7" and plan.context_rule_snapshot() == []


def test_restore_and_shared_surfaces_use_stored_scope_effects_and_candidate_revision(tmp_path):
    plan = build_default_trade_plan()
    shell = TradingDayShellWidget(plan.process_blueprint, authorization_gates=plan.authorization_gates,
                                  context_rules=(rule(),), trade_plan_revision="E7 fixture",
                                  run_environment=RunEnvironment.REPLAY)
    shell.run_market_timestamp = datetime.fromisoformat("2026-10-09T10:15:00-04:00")
    assert shell.start_trading_run()
    run = configure(shell.active_trading_run)
    conn = create_connection(tmp_path / "e7.db"); initialize_schema(conn)
    TradingDayRepository(conn).save(shell.trading_day)
    TradingDaySessionRepository(conn).save(shell.runtime.session)
    repo = TradingSessionRunRepository(conn); repo.save(run)
    shell.context_rules = ()
    conn.close()
    conn = create_connection(tmp_path / "e7.db")
    repo = TradingSessionRunRepository(conn)
    restored = repo.get_by_id(run.id)
    assert restored.context_rule_snapshot == run.context_rule_snapshot
    assert restored.market_context_snapshot == run.market_context_snapshot
    assert restored.candidate_authorization(restored.setup_candidates[0].id).status is AuthorizationStatus.BLOCKED
    before = deepcopy(restored.__dict__)
    card = MarketContextWidget()
    for mode in ("tda", "live-watch", "post-market"):
        card.load_run_context(restored, mode_id=mode)
        details = card.detail_text.toPlainText()
        assert "fixture-friday@fixture-v0" in details
        assert "Not Matched / Block New Entry" in details
        assert "2026-10-05T00:00:00-04:00" in details
        assert "Playbook scope: fixture-friday" in details
        assert "E7 fixture" in details
    assert restored.__dict__ == before
    assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION
    shell.market_time_timer.stop(); shell.close(); card.close(); conn.close()


def test_acceptance_demo_renders_custom_candidate_and_restores_its_tda_watch_point(tmp_path, monkeypatch):
    from pathlib import Path
    from PySide6.QtWidgets import QLabel

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "tools"))
    from context_predicate_demo import ContextPredicateDemo

    conn = create_connection(tmp_path / "demo.db"); initialize_schema(conn)
    demo = ContextPredicateDemo(conn)

    def check_custom_fixture():
        run = demo.shell.active_trading_run
        watch = demo.shell.runtime.live_watch_widget
        assert "Custom fixture" in [label.text() for label in watch.findChildren(QLabel)]
        custom = next(item for item in run.setup_candidates if item.source_type == "Custom")
        assert custom.source_id == "day-specific"
        points = demo.shell.runtime.tda_station_runner_widget.session.watch_points
        assert len(points) == 1
        assert (custom.id, points[0].id) in watch.candidate_watch_point_combos
        assert run.candidate_authorization(custom.id).status is AuthorizationStatus.AUTHORIZED
        target = run.playbook_candidate("fixture-friday")
        assert run.candidate_authorization(target.id).status is AuthorizationStatus.BLOCKED
        return run.id, custom.id, points[0].id

    try:
        saved_identity = check_custom_fixture()
        demo.save_fixture()
        demo.scenario.setCurrentText("Complete Monday empty")
        demo.restore_fixture()
        assert check_custom_fixture() == saved_identity
    finally:
        demo.shell.market_time_timer.stop(); demo.close(); conn.close()

    conn = create_connection(tmp_path / "demo.db")
    demo = ContextPredicateDemo(conn)
    try:
        demo.restore_fixture()
        assert check_custom_fixture() == saved_identity
    finally:
        demo.shell.market_time_timer.stop(); demo.close(); conn.close()


def test_acceptance_restart_identifies_database_and_restores_saved_review(tmp_path, monkeypatch):
    from pathlib import Path
    import shlex
    from PySide6.QtWidgets import QApplication

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "tools"))
    from context_predicate_demo import ContextPredicateDemo

    saved_path = tmp_path / "saved sandbox" / "demo.db"
    conn = create_connection(saved_path); initialize_schema(conn)
    demo = ContextPredicateDemo(conn)
    try:
        assert str(saved_path) in demo.database_label.text()
        assert not demo.restore_button.isEnabled()
        assert "No saved fixture in this database" in demo.storage_label.text()
        demo.copy_restart_button.click()
        assert QApplication.clipboard().text() == demo.restart_command
        assert shlex.split(demo.restart_command)[-1] == str(saved_path.parent)
        runtime = demo.shell.runtime
        transition = next(item for item in runtime.current_mode.transitions if item.outcome == "advance")
        assert runtime.apply_transition(transition.id, reason="Synthetic fixture acceptance", override_incomplete=True)
        assert runtime.apply_transition("live-finish")
        assert runtime.session.current_mode_id == "post-market"
        run_id = demo.shell.active_trading_run.id
        demo.save_fixture()
        assert demo.restore_button.isEnabled()
    finally:
        demo.shell.market_time_timer.stop(); demo.close(); conn.close()

    conn = create_connection(tmp_path / "different sandbox" / "demo.db"); initialize_schema(conn)
    demo = ContextPredicateDemo(conn)
    try:
        assert not demo.restore_button.isEnabled()
        assert "No saved fixture in this database" in demo.storage_label.text()
        assert str(saved_path) not in demo.database_label.text()
    finally:
        demo.shell.market_time_timer.stop(); demo.close(); conn.close()

    conn = create_connection(saved_path)
    demo = ContextPredicateDemo(conn)
    try:
        assert demo.restore_button.isEnabled()
        demo.restore_fixture()
        assert demo.shell.active_trading_run.id == run_id
        assert demo.shell.runtime.session.current_mode_id == "post-market"
        assert demo.shell.active_trading_run.candidate_authorization(
            demo.shell.active_trading_run.playbook_candidate("fixture-friday").id
        ).status is AuthorizationStatus.BLOCKED
    finally:
        demo.shell.market_time_timer.stop(); demo.close(); conn.close()
