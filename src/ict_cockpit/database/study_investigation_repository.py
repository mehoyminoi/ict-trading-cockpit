"""Explicit immutable links to draft or saved capture IDs, independent of runs."""
from datetime import datetime, timezone


class StudyInvestigationRepository:
    def __init__(self, connection):
        self.connection = connection

    def get(self, capture_id):
        cursor = self.connection.execute(
            "SELECT * FROM study_investigation_capture WHERE capture_id=?", (capture_id,))
        row = cursor.fetchone()
        return dict(zip((item[0] for item in cursor.description), row)) if row else None

    def link(self, capture_id, *, task_id, plan_id, plan_revision, question,
             instrument, market_reference, interpretation):
        values = (capture_id, task_id, plan_id, plan_revision, question.strip(),
                  instrument.strip(), market_reference, interpretation)
        if not all(values):
            raise ValueError("A question, plan and complete historical reference are required")
        reference = datetime.fromisoformat(market_reference)
        if reference.tzinfo is None or reference.utcoffset() is None:
            raise ValueError("Historical reference requires a timezone")
        if interpretation not in ('Expected', 'Observed'):
            raise ValueError("Choose Expected or Observed")
        with self.connection:
            existing = self.get(capture_id)
            if existing:
                if tuple(existing[k] for k in ('capture_id','task_id','plan_id','plan_revision',
                    'question','instrument','market_reference','interpretation')) == values:
                    return existing
                raise ValueError("This capture is already linked; its recorded investigation cannot be reassigned")
            if not self.connection.execute(
                "SELECT id FROM study_find WHERE id=? UNION ALL SELECT id FROM study_find_draft WHERE id=?",
                (capture_id, capture_id)).fetchone():
                raise ValueError("Enter and retain capture content before linking")
            self.connection.execute(
                "INSERT INTO study_investigation_capture VALUES (?,?,?,?,?,?,?,?,?)",
                (*values, datetime.now(timezone.utc).isoformat()))
        return self.get(capture_id)


def describe_association(record):
    if record is None:
        return "No saved investigation association."
    return (f"Linked investigation: {record['question']}\n"
            f"{record['instrument']} · {record['market_reference']} · {record['interpretation']}\n"
            f"Plan {record['plan_revision']} · recorded {record['recorded_at']}\n"
            "Preserved at linking; not a competency assessment or proof of prospective knowledge.")
