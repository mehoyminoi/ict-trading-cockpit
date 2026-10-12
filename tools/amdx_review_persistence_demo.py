"""Verify atomic Review pairing and reopen in a disposable application DB."""
from datetime import timedelta
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from amdx_review_demo import worked_examples
from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import TradingRun
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository


def main():
    example = worked_examples()
    e1, e2, observation = example.interpretations.claims
    with TemporaryDirectory(prefix="ict-amdx-review-") as directory:
        database = Path(directory) / "temporary.db"
        connection = open_application_database(database)
        try:
            day = TradingDay(futures_day_label="2026-10-08")
            process = TradingDaySession(blueprint_revision="fixture-only", mode_ids=["tda"], current_mode_id="tda")
            TradingDayRepository(connection).save(day)
            TradingDaySessionRepository(connection).save(process)
            runs = TradingSessionRunRepository(connection)
            run = TradingRun(day.id, "Synthetic Review persistence", process.id,
                             id=e1.run_id, trade_plan_revision="fixture-only")
            runs.save(run)
            head = None
            for claim in (e1, e2):
                action = claim.action_anchor or next(a for a in claim.anchors if a.quarter_id == claim.action_quarter_id)
                args = dict(claim_id=claim.id, run_id=run.id, branch_id=claim.branch_id,
                            channel=claim.channel, cycle=claim.cycle, quarter_id=claim.action_quarter_id,
                            anchor=action, recorded_at=claim.recorded_at,
                            market_reference=claim.market_reference, expected_head_id=head)
                if claim == e1:
                    runs.amdx.accept(**args)
                else:
                    runs.amdx.revise_working(**args)
                head = claim.id
            args = dict(comparison_id="P1", expected_claim_id=e1.id, expected_comparison_head_id=None,
                        claim_id=observation.id, run_id=run.id, branch_id=observation.branch_id,
                        cycle=observation.cycle, quarter_id=observation.action_quarter_id,
                        anchor=observation.anchors[0], recorded_at=observation.recorded_at,
                        market_reference=observation.market_reference, expected_observed_head_id=None)
            original = runs.amdx.review.record_observation(**args)
            alternate = runs.amdx.review.record_comparison(
                run_id=run.id, comparison_id="P2", expected_claim_id=e2.id, observed_claim_id=observation.id,
                expected_head_id=original.id, recorded_at=observation.recorded_at + timedelta(minutes=1),
                market_reference=observation.market_reference)
            assert runs.amdx.review.record_observation(**args) == original
            expected = runs.amdx.review.get_history(run.id)
            runs.save(run)
        finally:
            connection.close()
        connection = open_application_database(database)
        try:
            restored = TradingSessionRunRepository(connection).amdx.review
            assert restored.get_history(run.id) == expected
            assert restored.get_comparison("P2") == alternate
            assert expected.summarize("P1").order_relation == "Different order"
            assert expected.summarize("P2").order_relation == "Same order"
            assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
            print(f"Disposable AMDX Review persistence · schema v{CURRENT_SCHEMA_VERSION} · synthetic Replay references.")
            print("Observation + original pairing commit together; alternate pairing preserves the same observation.")
            print("Original exact retry after later edits, ordinary run save and database reopen: PASS.")
            print("P1: Different order. P2: Same order; X subtype remains unresolved.")
            print("No baseline default, Watch display, real data, classifier, published policy or orders.")
        finally:
            connection.close()


if __name__ == "__main__":
    main()
