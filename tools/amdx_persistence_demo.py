"""Exercise durable AMDX actions in a disposable temporary application database."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from amdx_foundation_demo import worked_examples
from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import TradingRun
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository


def main():
    history, evaluation, _ = worked_examples()
    with TemporaryDirectory(prefix="ict-amdx-persistence-") as directory:
        database = Path(directory) / "temporary.db"
        connection = open_application_database(database)
        try:
            day = TradingDay(futures_day_label="2026-10-08")
            process = TradingDaySession(blueprint_revision="fixture-only", mode_ids=["tda"], current_mode_id="tda")
            TradingDayRepository(connection).save(day)
            TradingDaySessionRepository(connection).save(process)
            runs = TradingSessionRunRepository(connection)
            run = TradingRun(day.id, "Synthetic persistence", process.id,
                             id=evaluation.run_id, trade_plan_revision="fixture-plan")
            runs.save(run)
            head = None
            for claim in history.claims:
                accepted = runs.amdx.accept(
                    claim_id=claim.id, run_id=claim.run_id, branch_id=claim.branch_id, channel=claim.channel,
                    cycle=claim.cycle, quarter_id=claim.action_quarter_id,
                    anchor=next(a for a in claim.anchors if a.quarter_id == claim.action_quarter_id),
                    recorded_at=claim.recorded_at, market_reference=claim.market_reference, expected_head_id=head,
                )
                head = accepted.id
            runs.amdx.save_evaluation(evaluation, recorded_at=history.claims[-1].recorded_at, basis_claim_id=head)
            runs.save(run)  # An ordinary save cannot truncate the child history.
        finally:
            connection.close()
        connection = open_application_database(database)
        try:
            restored = TradingSessionRunRepository(connection).amdx
            assert restored.get_history(evaluation.run_id) == history
            assert restored.get_evaluation(evaluation.id).evaluation == evaluation
            assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
            print(f"Disposable AMDX persistence · schema v{CURRENT_SCHEMA_VERSION} · fixture definitions only.")
            print("Accepted Q3=M → XAMD, then Q3=D → AMDX; both revisions survive database reopen.")
            print("Original criteria, opposing evidence, priority policy and explicit claim basis survive reopen.")
            print("Ordinary run save preserves AMDX history. Foreign-key consistency: PASS.")
            print("Temporary database only; no real data, source feed, published plan or orders.")
        finally:
            connection.close()


if __name__ == "__main__":
    main()
