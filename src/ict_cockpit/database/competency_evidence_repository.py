import json
import sqlite3

from ict_cockpit.analysis.competency import CompetencyEvidence
from ict_cockpit.analysis.trading_session_run import StudyOutcome


class CompetencyEvidenceRepository:
    """Persistence boundary for evidence separate from competency state."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def replace_from_study_review(
        self,
        *,
        trade_plan_id: str,
        trading_run,
    ) -> list[CompetencyEvidence]:
        """Mirror the run's current reviewed Study outcome into competency evidence.

        v0 deliberately creates evidence only when the run has a reviewed Study
        context and one or more focused competencies. Re-reviewing the same run
        replaces that run's evidence rather than accumulating duplicate rows.
        """
        run_id = str(trading_run.id).strip()
        with self.connection:
            self.connection.execute(
                "DELETE FROM competency_evidence WHERE trading_run_id = ?",
                (run_id,),
            )

            study = trading_run.study_context
            if (
                study is None
                or study.outcome is StudyOutcome.NOT_REVIEWED
                or not study.competency_focus
            ):
                return []

            records = [
                CompetencyEvidence(
                    trade_plan_id=trade_plan_id,
                    trade_plan_revision=trading_run.trade_plan_revision,
                    competency_id=str(item.get("id", "")),
                    competency_name=str(item.get("name", item.get("id", ""))),
                    competency_category=str(item.get("category", "")),
                    trading_run_id=run_id,
                    run_environment=trading_run.environment.value,
                    run_purpose=trading_run.purpose.value,
                    study_outcome=study.outcome.value,
                    note=study.outcome_note,
                    study_question=study.question,
                    study_hypothesis=study.hypothesis,
                    study_scope=study.scope,
                    market_time_context=trading_run.market_time_context,
                    qt_context=trading_run.qt_context,
                    recorded_at=study.completed_at,
                    id=f"{run_id}:{str(item.get('id', '')).strip()}",
                )
                for item in study.competency_focus
                if str(item.get("id", "")).strip()
            ]

            for evidence in records:
                self.connection.execute(
                    """
                    INSERT INTO competency_evidence (
                        id,
                        trade_plan_id,
                        trade_plan_revision,
                        competency_id,
                        competency_name,
                        competency_category,
                        trading_run_id,
                        run_environment,
                        run_purpose,
                        study_outcome,
                        note,
                        study_question,
                        study_hypothesis,
                        study_scope,
                        market_time_context_json,
                        qt_context_json,
                        source,
                        recorded_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        evidence.id,
                        evidence.trade_plan_id,
                        evidence.trade_plan_revision,
                        evidence.competency_id,
                        evidence.competency_name,
                        evidence.competency_category,
                        evidence.trading_run_id,
                        evidence.run_environment,
                        evidence.run_purpose,
                        evidence.study_outcome,
                        evidence.note,
                        evidence.study_question,
                        evidence.study_hypothesis,
                        evidence.study_scope,
                        json.dumps(evidence.market_time_context),
                        json.dumps(evidence.qt_context),
                        evidence.source,
                        evidence.recorded_at,
                    ),
                )

        return records

    def list_for_competency(
        self,
        trade_plan_id: str,
        competency_id: str,
    ) -> list[CompetencyEvidence]:
        rows = self.connection.execute(
            """
            SELECT id, trade_plan_id, trade_plan_revision, competency_id,
                   competency_name, competency_category, trading_run_id,
                   run_environment, run_purpose, study_outcome, note,
                   study_question, study_hypothesis, study_scope,
                   market_time_context_json, qt_context_json, source, recorded_at
            FROM competency_evidence
            WHERE trade_plan_id = ? AND competency_id = ?
            ORDER BY recorded_at, id
            """,
            (trade_plan_id, competency_id),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    def list_for_run(self, trading_run_id: str) -> list[CompetencyEvidence]:
        rows = self.connection.execute(
            """
            SELECT id, trade_plan_id, trade_plan_revision, competency_id,
                   competency_name, competency_category, trading_run_id,
                   run_environment, run_purpose, study_outcome, note,
                   study_question, study_hypothesis, study_scope,
                   market_time_context_json, qt_context_json, source, recorded_at
            FROM competency_evidence
            WHERE trading_run_id = ?
            ORDER BY competency_id
            """,
            (trading_run_id,),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row) -> CompetencyEvidence:
        return CompetencyEvidence(
            id=row[0],
            trade_plan_id=row[1],
            trade_plan_revision=row[2],
            competency_id=row[3],
            competency_name=row[4],
            competency_category=row[5],
            trading_run_id=row[6],
            run_environment=row[7],
            run_purpose=row[8],
            study_outcome=row[9],
            note=row[10],
            study_question=row[11],
            study_hypothesis=row[12],
            study_scope=row[13],
            market_time_context=json.loads(row[14] or "{}"),
            qt_context=json.loads(row[15] or "{}"),
            source=row[16],
            recorded_at=row[17],
        )
