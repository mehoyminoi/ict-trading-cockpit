"""E7 acceptance sandbox: explicit fixture predicates and a separate database."""
import argparse
from datetime import datetime
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ict_cockpit.context_rules import (
    ContextConditionDefinition as Condition, ContextConditionKind as Kind,
    ContextRuleDefinition as Rule, ContextEffect as Effect, ContextEventWindow as Window,
)
from ict_cockpit.analysis.context_source import ContextCoverage
from ict_cockpit.analysis.market_context_event import MarketContextEvent, MarketContextSnapshot, MarketContextSnapshotStatus
from ict_cockpit.analysis.market_time import build_market_time_context
from ict_cockpit.analysis.trading_session_run import RunEnvironment, SetupCandidate, default_purpose_for_environment
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.tda_station_session_repository import TDAStationSessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository
from ict_cockpit.default_trade_plan import build_default_trade_plan
from ict_cockpit.trade_plan import EntryCriterionDefinition, PlaybookDefinition
from context_policy_demo import FrozenContextShell


class ContextPredicateDemo(QWidget):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.setWindowTitle("E7 acceptance — unpublished fixture models / separate database")
        self.resize(1120, 900)
        self.outer = QVBoxLayout(self)
        note = QLabel("Fixture only: Monday of the Friday reference's calendar week (offset 0). "
                      "Following Monday uses explicit offset 1. No adopted Friday Asian Range rule. "
                      "Manual gates and one synthetic criterion initially clear; no orders or real calendar.")
        note.setWordWrap(True); self.outer.addWidget(note)
        bar = QHBoxLayout()
        self.scenario = QComboBox()
        self.scenario.addItems(["Monday event present", "Complete Monday empty", "Incomplete coverage",
                                "Unknown timing", "Unknown blocks", "Following Monday unverified",
                                "Other playbook only", "Not Configured", "Legacy rules"])
        self.environment = QComboBox()
        self.environment.addItems(["Replay", "Live", "Forward Test", "Historical Backtest"])
        for label, combo in (("New fixture", self.scenario), ("Environment", self.environment)):
            bar.addWidget(QLabel(label)); bar.addWidget(combo)
        self.save_button = QPushButton("Save fixture")
        self.restore_button = QPushButton("Restore saved fixture")
        bar.addWidget(self.save_button); bar.addWidget(self.restore_button)
        self.outer.addLayout(bar)
        self.storage_label = QLabel("Scenario changes create a new fixture run. Save is explicit; restore uses stored rules and facts.")
        self.storage_label.setWordWrap(True); self.outer.addWidget(self.storage_label)
        self.shell = None
        self.scenario.currentTextChanged.connect(self.rebuild)
        self.environment.currentTextChanged.connect(self.rebuild)
        self.save_button.clicked.connect(self.save_fixture)
        self.restore_button.clicked.connect(self.restore_fixture)
        self.rebuild()

    def rebuild(self, _text=""):
        if self.shell:
            self.shell.market_time_timer.stop()
            self.outer.removeWidget(self.shell); self.shell.hide(); self.shell.deleteLater()
        scenario = self.scenario.currentText()
        plan = build_default_trade_plan()
        models = tuple(PlaybookDefinition(id=model_id, name=name, revision="fixture-v0",
                                         entry_criteria=(EntryCriterionDefinition("fixture", "Fixture criterion"),),
                                         required_entry_count=1)
                       for model_id, name in (("fixture-friday", "Fixture Friday model"), ("fixture-other", "Other fixture model")))
        condition = Condition(Kind.EVENT_ABSENT, event_window=Window.CALENDAR_WEEK, event_weekdays=(0,),
                              calendar_week_offset=1 if scenario == "Following Monday unverified" else 0,
                              category="Economic", impacts=("High",))
        rule = Rule("fixture-no-monday", "Fixture no Monday high-impact events", (condition,), ("Replay",),
                    Effect.INFORMATIONAL, Effect.BLOCK_NEW_ENTRY if scenario == "Unknown blocks" else Effect.WARNING,
                    "Explicit fixture week relation and effects only; not Alpha 0.7 trading policy.",
                    playbook_ids=("fixture-friday",), not_matched_effect=Effect.BLOCK_NEW_ENTRY)
        self.shell = FrozenContextShell(plan.process_blueprint, playbooks=models,
                                        authorization_gates=plan.authorization_gates,
                                        context_rules=() if scenario == "Legacy rules" else (rule,),
                                        trade_plan_revision="E7 fixture (unpublished)", run_environment=RunEnvironment.REPLAY)
        stamp = datetime.fromisoformat("2026-10-09T10:15:00-04:00")
        self.shell.run_market_timestamp = stamp
        self.shell.start_trading_run(); self.shell.market_time_timer.stop()
        run = self.shell.active_trading_run
        run.environment = RunEnvironment(self.environment.currentText())
        run.purpose = default_purpose_for_environment(run.environment)
        run.market_time_context = build_market_time_context(stamp, source="E7 frozen historical fixture").to_dict()
        records = ()
        if scenario in {"Monday event present", "Other playbook only", "Unknown timing"}:
            records = (MarketContextEvent(id="fixture-monday", provider="E7 synthetic source", source_event_id="fixture-native",
                                          category="Economic", normalized_event_type="FIXTURE", title="Fixture Monday release",
                                          scheduled_at="2026-10-05T08:30:00-04:00", impact="High", status="Scheduled",
                                          timing_precision="Unknown" if scenario == "Unknown timing" else "Exact"),)
        coverage = ContextCoverage("2026-10-05T00:00:00-04:00", "2026-10-05T23:59:59.999999-04:00",
                                   scenario not in {"Incomplete coverage", "Unknown blocks", "Not Configured"},
                                   ("*",), ("*",), ("*",), ("*",), "Complete Monday claimed only by synthetic fixtures")
        run.market_context_snapshot = MarketContextSnapshot(
            MarketContextSnapshotStatus.NOT_CONFIGURED if scenario == "Not Configured" else MarketContextSnapshotStatus.AVAILABLE,
            "E7 synthetic source", "2026-10-08T18:00:00-04:00", "2026-10-09T17:59:59.999999-04:00",
            stamp.isoformat(), "E7 frozen historical fixture", "2026-10-10T12:00:00+00:00",
            records, coverage=coverage,
        ).to_dict()
        run.setup_candidates = [SetupCandidate(model.name, source_type="Playbook", source_id=model.id,
                                               source_revision=model.revision, definition_snapshot=model.to_snapshot(),
                                               entry_condition_states={"fixture": True})
                                for model in models if scenario != "Other playbook only" or model.id == "fixture-other"]
        run.setup_candidates.append(SetupCandidate("Custom fixture", source_type="Custom", definition_snapshot={
            "entry_criteria": [{"id": "fixture", "name": "Fixture criterion"}], "required_entry_count": 1,
        }, entry_condition_states={"fixture": True}))
        for gate in run.authorization_policy_snapshot:
            if gate["scope"] == "Run":
                run.set_authorization_gate(gate["id"], "Clear")
            else:
                for candidate in run.setup_candidates:
                    run.set_candidate_authorization_gate(candidate.id, gate["id"], "Clear")
        self.shell.runtime.load_trading_run(run)
        self.outer.addWidget(self.shell, 1)
        self.storage_label.setText("New unsaved fixture. Use the normal TDA → Watch → Review controls; Save preserves the current state.")
        self.restore_button.setEnabled(TradingDayRepository(self.connection).get_latest() is not None)

    def save_fixture(self):
        run = self.shell.active_trading_run
        if run is None:
            self.storage_label.setText("No active fixture to save. Select a new scenario to start another fixture.")
            return
        TradingDayRepository(self.connection).save(self.shell.trading_day)
        TradingDaySessionRepository(self.connection).save(self.shell.runtime.session)
        TDAStationSessionRepository(self.connection).save(self.shell.runtime.tda_station_runner_widget.session)
        TradingSessionRunRepository(self.connection).save(run)
        self.restore_button.setEnabled(True)
        self.storage_label.setText(f"Saved fixture run {run.id}. Change scenario, then Restore to inspect its original rules and facts.")

    def restore_fixture(self):
        day = TradingDayRepository(self.connection).get_latest()
        if day is None:
            return
        repo = TradingSessionRunRepository(self.connection)
        run = repo.get_by_id(day.active_session_run_id)
        if run is None:
            return
        self.shell.context_rules = ()  # Current definitions never replace saved run rules.
        self.shell.load_state(day, repo.get_for_day(day.id),
                              process_session=TradingDaySessionRepository(self.connection).get_by_id(run.process_session_id),
                              tda_session=TDAStationSessionRepository(self.connection).get_by_id(run.tda_station_session_id))
        self.storage_label.setText(f"Restored saved fixture run {run.id}; scenario controls describe new fixtures, not this stored run.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, help="Reuse the same E7 acceptance database for restart checks")
    args = parser.parse_args()
    directory = args.data_dir or Path(tempfile.mkdtemp(prefix="ict-e7-"))
    directory.mkdir(parents=True, exist_ok=True)
    print(f"E7 sandbox: {directory.resolve()}", flush=True)
    print(f"Restart: python tools/context_predicate_demo.py --data-dir {directory.resolve()}", flush=True)
    app = QApplication(sys.argv[:1])
    conn = create_connection(directory / "demo.db"); initialize_schema(conn)
    window = ContextPredicateDemo(conn); window.show()
    result = app.exec()
    window.shell.market_time_timer.stop(); conn.close()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
