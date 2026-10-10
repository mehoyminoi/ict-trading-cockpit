"""E5 disposable policy acceptance fixtures; no database, feed, or orders."""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ict_cockpit.context_rules import (
    ContextConditionDefinition as Condition, ContextConditionKind as Kind,
    ContextRuleDefinition as Rule, ContextEffect as Effect, ContextEventWindow as Window,
)
from ict_cockpit.analysis.market_context_event import InMemoryMarketContextEventProvider, MarketContextEventCategory as Category
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE, build_market_time_context
from ict_cockpit.analysis.trading_session_run import RunEnvironment, SetupCandidate, default_purpose_for_environment
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget
from context_surface_demo import fixture_events, UnavailableProvider


class FrozenContextShell(TradingDayShellWidget):
    def _current_market_time_context(self):
        if self.active_trading_run is not None:
            return dict(self.active_trading_run.market_time_context)
        return super()._current_market_time_context()


class ContextPolicyDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("E5 policy acceptance — disposable fixtures")
        self.resize(1100, 850)
        self.outer = QVBoxLayout(self)
        note = QLabel("Fixture rules only — not Alpha 0.7 policy. No database, real calendar, or orders. All manual gates and one fixture criterion start clear.")
        note.setWordWrap(True); self.outer.addWidget(note)
        bar = QHBoxLayout()
        self.scenario = QComboBox(); self.scenario.addItems([
            "Clock before cutoff", "Clock exactly cutoff", "Clock after cutoff", "Clock warning",
            "Event matched", "Event empty", "Event unavailable", "Unknown blocks", "Week coverage unknown", "Legacy rules",
        ])
        self.environment = QComboBox(); self.environment.addItems([x.value for x in RunEnvironment])
        self.mode = QComboBox(); self.mode.addItems(["TDA", "Watch", "Review"])
        for label, combo in (("Scenario", self.scenario), ("Environment", self.environment), ("Mode", self.mode)):
            bar.addWidget(QLabel(label)); bar.addWidget(combo)
        self.outer.addLayout(bar)
        self.shell = None
        for combo in (self.scenario, self.environment, self.mode): combo.currentTextChanged.connect(self.rebuild)
        self.rebuild()

    def rebuild(self, _text=""):
        if self.shell:
            self.shell.market_time_timer.stop(); self.outer.removeWidget(self.shell)
            self.shell.hide(); self.shell.deleteLater()
        scenario = self.scenario.currentText()
        is_clock = scenario.startswith("Clock")
        condition = (Condition(Kind.MARKET_CLOCK, weekdays=(4,), after_time="11:00") if is_clock else
                     Condition(Kind.EVENT_PRESENT, category=Category.ECONOMIC,
                               event_types=("FIXTURE",), event_window=Window.CALENDAR_WEEK if scenario.startswith("Week") else Window.FUTURES_DAY))
        rule = Rule("fixture-only", "Fixture context policy", (condition,), ("Live",),
                    Effect.WARNING if scenario == "Clock warning" else Effect.BLOCK_NEW_ENTRY,
                    Effect.BLOCK_NEW_ENTRY if scenario == "Unknown blocks" else Effect.WARNING,
                    "Explicit demo settings only; these are not published trading rules.")
        plan = build_default_trade_plan()
        provider = (UnavailableProvider() if scenario in {"Event unavailable", "Unknown blocks"} else
                    InMemoryMarketContextEventProvider("E5 fixture", fixture_events() if scenario == "Event matched" else ()))
        env = RunEnvironment(self.environment.currentText())
        self.shell = FrozenContextShell(plan.process_blueprint, authorization_gates=plan.authorization_gates,
                                          context_rules=() if scenario == "Legacy rules" else (rule,),
                                          trade_plan_revision="E5 fixture (unpublished)", run_environment=RunEnvironment.REPLAY,
                                          market_context_event_provider=provider)
        hour, minute = (10, 59) if scenario == "Clock before cutoff" else (11, 0) if scenario == "Clock exactly cutoff" else (11, 1)
        stamp = datetime(2026, 10, 9 if is_clock else 6, hour, minute, tzinfo=MARKET_TIMEZONE)
        self.shell.run_market_timestamp = stamp
        self.shell.start_trading_run(); self.shell.market_time_timer.stop()
        run = self.shell.active_trading_run
        # Freeze all environments at the selected fixture time; no live clock in this demo.
        run.environment = env
        run.purpose = default_purpose_for_environment(env)
        run.market_time_context = build_market_time_context(stamp, source="E5 fixture frozen time").to_dict()
        run.setup_candidates = [SetupCandidate("Fixture setup", source_type="Technician", definition_snapshot={
            "entry_criteria": [{"id": "fixture", "name": "Fixture criterion"}], "required_entry_count": 1,
        }, entry_condition_states={"fixture": True})]
        for gate in run.authorization_policy_snapshot:
            if gate["scope"] == "Run": run.set_authorization_gate(gate["id"], "Clear")
            else: run.set_candidate_authorization_gate(run.setup_candidates[0].id, gate["id"], "Clear")
        self.shell.runtime.load_trading_run(run)
        for _ in range(self.mode.currentIndex()): self.shell.runtime.go_next_mode()
        self.outer.addWidget(self.shell, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv); window = ContextPolicyDemo(); window.show(); raise SystemExit(app.exec())
