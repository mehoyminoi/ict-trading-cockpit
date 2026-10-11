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
from ict_cockpit.analysis.market_context_event import (
    MarketContextEvent as Event, MarketContextEventCategory as Category,
    MarketContextEventStatus as Status, MarketContextImpact as Impact,
    MarketContextSnapshot as Snapshot, MarketContextSnapshotStatus as Availability,
)
from ict_cockpit.analysis.market_time import build_market_time_context, MARKET_TIMEZONE
from ict_cockpit.analysis.market_context_view import build_market_context_view
from ict_cockpit.analysis.trading_session_run import AuthorizationStatus, SetupCandidate, RunEnvironment
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema, CURRENT_SCHEMA_VERSION
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget
from ict_cockpit.gui.market_context_widget import MarketContextWidget


def market(at="2026-10-09T11:01:00-04:00"):
    return build_market_time_context(datetime.fromisoformat(at), source="Historical Reference").to_dict()


def snapshot(events=(), status=Availability.AVAILABLE, *, start="2026-10-08T18:00:00-04:00", end="2026-10-09T17:59:59.999999-04:00"):
    coverage = (ContextCoverage(start, end, True, ("*",), ("*",), ("*",), ("*",), "Complete synthetic test fixture")
                if start and end else ContextCoverage())
    return Snapshot(status, "Fixture", start, end, "2026-10-09T11:01:00-04:00", "Historical Reference", "2026-10-10T10:00:00-04:00", events, coverage=coverage).to_dict()


def event(**kwargs):
    return Event(**{**dict(id="fixture", provider="Fixture", source_event_id="source", category=Category.ECONOMIC,
                 normalized_event_type="NFP", title="Unrelated title", scheduled_at="2026-10-09T08:30:00-04:00",
                 impact=Impact.HIGH, status=Status.SCHEDULED, affected_markets=("USD",), timing_precision="Exact"), **kwargs})


def rule(*conditions, effect=Effect.BLOCK_NEW_ENTRY, unknown=Effect.WARNING, environments=("Live",)):
    return Rule("fixture-policy", "Fixture policy", conditions, environments, effect, unknown, "Fixture only; not a published trading rule.")


def evaluate(r, *, m=None, s=None, environment="Live"):
    return evaluate_context_rules([r], environment=environment, market_time_context=market() if m is None else m,
                                  market_context_snapshot=snapshot() if s is None else s)[0]


@pytest.mark.parametrize("at,expected", [
    ("2026-10-09T10:59:59-04:00", Match.NOT_MATCHED),
    ("2026-10-09T11:00:00-04:00", Match.NOT_MATCHED),
    ("2026-10-09T15:00:01+00:00", Match.MATCHED),
    ("2026-10-08T15:00:00-04:00", Match.NOT_MATCHED),
    ("2026-11-06T16:00:01+00:00", Match.MATCHED),
])
def test_clock_uses_explicit_ny_time_strict_cutoff_and_dst(at, expected):
    result = evaluate(rule(Condition(Kind.MARKET_CLOCK, weekdays=(4,), after_time="11:00")), m=market(at))
    assert result.state is expected
    assert result.blocks_new_entry == (expected is Match.MATCHED)


@pytest.mark.parametrize("environment", ["Replay", "Historical Backtest", "Forward Test"])
def test_environment_exclusion_precedes_missing_data(environment):
    result = evaluate(rule(Condition(Kind.MARKET_CLOCK, weekdays=(4,))), m={}, s={}, environment=environment)
    assert result.state is Match.NOT_APPLICABLE and result.effect is None


def test_missing_time_never_uses_wall_clock_and_false_conjunct_resolves_unknown():
    clock = Condition(Kind.MARKET_CLOCK, weekdays=(0,))
    event_term = Condition(Kind.EVENT_PRESENT, event_types=("NFP",))
    assert evaluate(rule(clock), m={}).state is Match.UNKNOWN
    assert evaluate(rule(clock, event_term), s={}).state is Match.NOT_MATCHED


@pytest.mark.parametrize("status", [Availability.NOT_CONFIGURED, Availability.UNAVAILABLE])
def test_unavailable_context_uses_explicit_unknown_effect(status):
    result = evaluate(rule(Condition(Kind.EVENT_PRESENT, event_types=("NFP",)), unknown=Effect.BLOCK_NEW_ENTRY), s=snapshot(status=status))
    assert result.state is Match.UNKNOWN and result.blocks_new_entry


@pytest.mark.parametrize("status,expected", [
    (Status.SCHEDULED, Match.MATCHED), (Status.RELEASED, Match.MATCHED),
    (Status.CANCELLED, Match.NOT_MATCHED), (Status.POSTPONED, Match.NOT_MATCHED),
    (Status.TENTATIVE, Match.UNKNOWN), (Status.UNKNOWN, Match.UNKNOWN),
])
def test_daywide_event_rule_uses_status_not_upcoming_presentation(status, expected):
    result = evaluate(rule(Condition(Kind.EVENT_PRESENT, event_types=("NFP",))), s=snapshot((event(status=status),)))
    assert result.state is expected


def test_impact_and_type_and_market_are_explicit_not_inferred_from_provider_text():
    r = rule(Condition(Kind.EVENT_PRESENT, category=Category.ECONOMIC, event_types=("NFP",), impacts=(Impact.HIGH,), affected_markets=("USD",)))
    assert evaluate(r, s=snapshot((event(),))).state is Match.MATCHED
    assert evaluate(r, s=snapshot((event(normalized_event_type="", title="NFP red folder", impact=Impact.UNKNOWN, provider_native_impact="red"),))).state is Match.UNKNOWN
    assert evaluate(r, s=snapshot((event(normalized_event_type="CPI", title="NFP"),))).state is Match.NOT_MATCHED
    assert evaluate(r, s=snapshot((event(affected_markets=("EUR",)),))).state is Match.NOT_MATCHED
    assert evaluate(r, s=snapshot((event(affected_markets=()),))).state is Match.UNKNOWN


def test_negative_week_condition_requires_full_week_coverage_but_positive_can_be_known():
    r = rule(Condition(Kind.MARKET_CLOCK, weekdays=(2, 3, 4)), Condition(Kind.EVENT_PRESENT, event_window=Window.CALENDAR_WEEK, event_types=("NFP",)))
    assert evaluate(r).state is Match.UNKNOWN
    assert evaluate(r, s=snapshot((event(),))).state is Match.MATCHED
    assert evaluate(r, s=snapshot(start="2026-10-05T00:00:00-04:00", end="2026-10-11T23:59:59.999999-04:00")).state is Match.NOT_MATCHED


def test_empty_success_missing_bounds_and_outside_day_are_distinct():
    r = rule(Condition(Kind.EVENT_PRESENT, category=Category.EARLY_CLOSE))
    assert evaluate(r).state is Match.NOT_MATCHED
    assert evaluate(r, s=snapshot(start="", end="")).state is Match.UNKNOWN
    assert evaluate(r, m=market("2026-10-10T12:00:00-04:00")).state is Match.UNKNOWN
    contradictory = market(); contradictory["futures_trading_day"] = "2026-10-08"
    assert evaluate(r, m=contradictory).state is Match.UNKNOWN
    assert evaluate(r, s=snapshot((event(category=Category.EARLY_CLOSE),))).state is Match.MATCHED


@pytest.mark.parametrize("effect,blocks", [(Effect.INFORMATIONAL, False), (Effect.WARNING, False), (Effect.BLOCK_NEW_ENTRY, True), (Effect.STAND_DOWN_DAY, True)])
def test_effects_are_declarative_and_distinct(effect, blocks):
    result = evaluate(rule(Condition(Kind.MARKET_CLOCK, weekdays=(4,)), effect=effect))
    assert result.effect is effect and result.blocks_new_entry is blocks


def test_definition_validation_and_published_plan_compatibility():
    r = rule(Condition(Kind.EVENT_PRESENT, event_types=("NFP",)))
    assert Rule.from_dict(json.loads(json.dumps(r.to_dict()))) == r
    assert build_default_trade_plan().revision == "Alpha 0.7"
    assert build_default_trade_plan().context_rule_snapshot() == []
    with pytest.raises(ValueError): replace(build_default_trade_plan(), context_rules=(r, r))
    with pytest.raises(ValueError): replace(r, environments=())
    with pytest.raises(ValueError): replace(r, conditions=())
    with pytest.raises(ValueError): Condition(Kind.MARKET_CLOCK, after_time="11:00:00")
    with pytest.raises(ValueError): Condition(Kind.EVENT_PRESENT, impacts=(Impact.UNKNOWN,))
    with pytest.raises(ValueError): Condition(Kind.MARKET_CLOCK, weekdays=(7,))
    with pytest.raises(ValueError): Condition(Kind.EVENT_PRESENT, weekdays=(0,), event_types=("NFP",))


def configured_shell():
    plan = build_default_trade_plan()
    r = rule(Condition(Kind.MARKET_CLOCK, weekdays=(4,), after_time="11:00"))
    shell = TradingDayShellWidget(plan.process_blueprint, context_rules=(r,),
                                 authorization_gates=plan.authorization_gates, trade_plan_revision="E5 fixture",
                                 run_environment=RunEnvironment.LIVE)
    # Live start derives wall time by design; freeze the run explicitly for this test.
    assert shell.start_trading_run()
    run = shell.active_trading_run
    run.market_time_context = market()
    run.setup_candidates = [SetupCandidate(name="Fixture candidate", source_type="Technician", definition_snapshot={
        "entry_criteria": [{"id": "one", "name": "One"}], "required_entry_count": 1,
    }, entry_condition_states={"one": True})]
    for gate in run.authorization_policy_snapshot:
        if gate["scope"] == "Run": run.set_authorization_gate(gate["id"], "Clear")
        else: run.set_candidate_authorization_gate(run.setup_candidates[0].id, gate["id"], "Clear")
    return shell, run


def test_context_block_cannot_be_bypassed_by_manual_clear_and_warning_never_grants_entry():
    shell, run = configured_shell()
    cid = run.setup_candidates[0].id
    before = deepcopy(run.__dict__)
    result = run.candidate_authorization(cid)
    assert result.status is AuthorizationStatus.BLOCKED and "Context rule" in result.blockers[0]
    assert run.__dict__ == before
    r = Rule.from_dict(run.context_rule_snapshot[0])
    run.context_rule_snapshot = [replace(r, effect=Effect.WARNING).to_dict()]
    assert run.candidate_authorization(cid).status is AuthorizationStatus.AUTHORIZED
    run.set_authorization_gate("trading-day-permitted", "Pending")
    assert run.candidate_authorization(cid).status is AuthorizationStatus.BLOCKED
    shell.close()


def test_rule_snapshot_roundtrip_survives_new_plan_and_explains_review_without_mutation(tmp_path):
    shell, run = configured_shell()
    conn = create_connection(tmp_path / "e5.db"); initialize_schema(conn)
    TradingDayRepository(conn).save(shell.trading_day)
    TradingDaySessionRepository(conn).save(shell.runtime.session)
    repo = TradingSessionRunRepository(conn); repo.save(run)
    shell.context_rules = ()  # current plan has changed; historical run must not change.
    restored = repo.get_by_id(run.id)
    assert restored.context_rule_snapshot == run.context_rule_snapshot
    assert restored.candidate_authorization(restored.setup_candidates[0].id).status is AuthorizationStatus.BLOCKED
    before = deepcopy(restored.__dict__)
    card = MarketContextWidget(); card.load_run_context(restored, mode_id="post-market")
    assert "Matched / Block New Entry" in card.events_label.text()
    assert "E5 fixture" in card.detail_text.toPlainText()
    assert "Fixture only" in card.detail_text.toPlainText()
    assert restored.__dict__ == before
    assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION == 37
    conn.close(); shell.close(); card.close()


def test_v35_migration_keeps_legacy_rules_empty():
    import sqlite3
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE trading_session_run (id TEXT PRIMARY KEY)")
    conn.execute("INSERT INTO trading_session_run VALUES ('legacy')")
    conn.execute("PRAGMA user_version = 35")
    initialize_schema(conn)
    assert conn.execute("SELECT context_rule_snapshot_json FROM trading_session_run").fetchone()[0] == "[]"
    initialize_schema(conn)  # migration is repeatable
    conn.close()
