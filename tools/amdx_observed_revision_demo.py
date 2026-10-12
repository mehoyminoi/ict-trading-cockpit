"""Disposable observed quartet correction; no comparison controls or app UI."""
from datetime import datetime, timedelta
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ict_cockpit.analysis.amdx import Anchor, Role, intraday_cycles
from ict_cockpit.analysis.market_time import MARKET_TIMEZONE
from ict_cockpit.analysis.trading_day import TradingDay
from ict_cockpit.analysis.trading_day_session import TradingDaySession
from ict_cockpit.analysis.trading_session_run import TradingRun
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.schema import CURRENT_SCHEMA_VERSION
from ict_cockpit.database.trading_day_repository import TradingDayRepository
from ict_cockpit.database.trading_day_session_repository import TradingDaySessionRepository
from ict_cockpit.database.trading_session_run_repository import TradingSessionRunRepository


def main():
    reference = datetime(2026, 10, 8, 9, 15, tzinfo=MARKET_TIMEZONE)
    cycle = intraday_cycles(reference)[0]
    with TemporaryDirectory(prefix="ict-amdx-observed-") as directory:
        database = Path(directory)/"temporary.db"
        connection = open_application_database(database)
        try:
            day=TradingDay(futures_day_label="2026-10-08")
            process=TradingDaySession(blueprint_revision="fixture-only",mode_ids=["tda"],current_mode_id="tda")
            TradingDayRepository(connection).save(day)
            TradingDaySessionRepository(connection).save(process)
            runs=TradingSessionRunRepository(connection)
            run=TradingRun(day.id,"Synthetic observed revision",process.id,trade_plan_revision="fixture-only")
            runs.save(run)
            repo=runs.amdx
            working=repo.revise_working(
                claim_id="working",run_id=run.id,branch_id="working",channel="Expected",cycle=cycle,
                quarter_id=cycle.quarters[2].id,anchor=Anchor("working-a",cycle.quarters[2].id,Role.D,"fixture"),
                recorded_at=reference,market_reference=reference,expected_head_id=None).claim
            def request(number,role,position,previous):
                return dict(claim_id=f"O{number}",comparison_id=f"P{number}",run_id=run.id,branch_id="working",
                            cycle=cycle,quarter_id=cycle.quarters[position-1].id,
                            anchor=Anchor(f"a{number}",cycle.quarters[position-1].id,role,"fixture") if role else None,
                            recorded_at=reference+timedelta(minutes=number),market_reference=cycle.quarters[-1].end,
                            expected_observed_head_id=previous.claim.id if previous else None,
                            expected_comparison_head_id=previous.comparison.id if previous else None)
            first=repo.review.revise_observed(**request(1,Role.A,1,None))
            second=repo.review.revise_observed(**request(2,Role.M,3,first))
            repeat_args=request(3,Role.M,3,second)
            repeated=repo.review.revise_observed(**repeat_args)
            assert not repeated.changed and repeated.claim == second.claim
            cleared=repo.review.revise_observed(**request(4,None,3,second))
            assert cleared.claim.inference.state == "Unresolved" and cleared.claim.anchors == ()
            assert repo.review.revise_observed(**repeat_args) == repeated
            expected=repo.review.get_history(run.id)
            assert all(p.expected_claim_id is None for p in expected.comparisons)
            assert repo.get_history(run.id).claims[0] == working
            runs.save(run)
        finally:
            connection.close()
        connection=open_application_database(database)
        try:
            restored=TradingSessionRunRepository(connection).amdx.review.get_history(run.id)
            assert restored == expected
            assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
            print(f"Disposable observed AMDX revision · schema v{CURRENT_SCHEMA_VERSION} · synthetic Replay references.")
            print("Observed Q1=A → AMDX; new Q3=M → XAMD; clear Q3 → Unresolved. Old A never returns.")
            print("Identical explicit entry adds no observation/pair; original retry after later clear: PASS.")
            print("Working AMDX unchanged; no expectation automatically selected; database reopen: PASS.")
            print("No app UI, Watch comparison, real data, classifier, published policy or orders.")
        finally:
            connection.close()


if __name__ == "__main__":
    main()
