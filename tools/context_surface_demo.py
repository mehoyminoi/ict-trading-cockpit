"""Disposable E4 UI fixtures. No database, feed, or execution connection."""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ict_cockpit.analysis.market_context_event import (
    InMemoryMarketContextEventProvider,
    MarketContextEvent,
    MarketContextEventCategory as Category,
    MarketContextEventStatus,
    MarketContextImpact,
)
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_session_run import RunEnvironment
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.gui.trading_day_shell_widget import TradingDayShellWidget


def fixture_events():
    result = []
    for title, time, category in (
        ("Fixture CPI", "08:30", Category.ECONOMIC),
        ("Fixture FOMC", "14:00", Category.ECONOMIC),
        ("Fixture early close", "16:00", Category.EARLY_CLOSE),
    ):
        result.append(MarketContextEvent(
            id=title, provider="E4 fixture calendar", source_event_id=title,
            category=category, normalized_event_type="FIXTURE", title=title,
            scheduled_at=f"2026-10-06T{time}:00-04:00", source_timezone="America/New_York",
            impact=MarketContextImpact.HIGH if category is Category.ECONOMIC else MarketContextImpact.UNKNOWN,
            status=MarketContextEventStatus.SCHEDULED,
            provider_native_impact="fixture-high" if category is Category.ECONOMIC else "",
            affected_markets=("Fixture market",), provenance_reference=f"fixture://{title}",
            captured_at="2026-10-10T12:00:00-04:00",
        ))
    return tuple(result)


class UnavailableProvider:
    provider_name = "Unavailable fixture"

    def events_between(self, start, end):
        raise RuntimeError("Deliberate fixture outage")


class ContextSurfaceDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("E4 context acceptance — disposable fixtures")
        self.resize(1100, 800)
        self.demo_layout = QVBoxLayout(self)
        note = QLabel("Fixture data only · no database or provider connection · each scenario starts a disposable Replay run.")
        note.setWordWrap(True)
        self.demo_layout.addWidget(note)
        controls = QHBoxLayout()
        self.scenario_combo = QComboBox()
        self.scenario_combo.addItems(["Available", "Available empty", "Not Configured", "Unavailable", "Legacy"])
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["TDA", "Watch", "Review"])
        controls.addWidget(QLabel("Scenario"))
        controls.addWidget(self.scenario_combo)
        controls.addWidget(QLabel("Mode"))
        controls.addWidget(self.mode_combo)
        controls.addStretch()
        self.demo_layout.addLayout(controls)
        self.shell = None
        self.scenario_combo.currentTextChanged.connect(self._rebuild)
        self.mode_combo.currentTextChanged.connect(self._rebuild)
        self._rebuild()

    def _rebuild(self, _text=""):
        if self.shell is not None:
            self.shell.market_time_timer.stop()
            self.demo_layout.removeWidget(self.shell)
            self.shell.hide()
            self.shell.deleteLater()
        scenario = self.scenario_combo.currentText()
        provider = None
        if scenario.startswith("Available"):
            provider = InMemoryMarketContextEventProvider(
                "E4 fixture calendar", fixture_events() if scenario == "Available" else ()
            )
        elif scenario == "Unavailable":
            provider = UnavailableProvider()
        plan = build_default_trade_plan()
        self.shell = TradingDayShellWidget(
            plan.process_blueprint, live_watch_policy=plan.live_watch_policy,
            playbooks=plan.playbooks, authorization_gates=plan.authorization_gates,
            trade_plan_revision=plan.revision, run_environment=RunEnvironment.REPLAY,
            market_context_event_provider=provider,
        )
        self.shell.run_market_timestamp = datetime(2026, 10, 6, 10, 15, tzinfo=MARKET_TIMEZONE)
        self.shell.start_trading_run()
        run = self.shell.active_trading_run
        if scenario == "Legacy":
            run.set_market_context_snapshot(None)
        run.set_qt_context({"day": "M", "session": "D"})
        self.shell.runtime.load_trading_run(run)
        for _ in range(self.mode_combo.currentIndex()):
            # Fixture navigation only; production transition controls remain unchanged.
            self.shell.runtime.go_next_mode()
        self.demo_layout.addWidget(self.shell, 1)


def main():
    app = QApplication(sys.argv)
    window = ContextSurfaceDemo()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
