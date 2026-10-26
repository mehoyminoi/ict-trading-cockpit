"""Independent immutable Study evaluations; never manufacture a trading run."""
from dataclasses import dataclass
from datetime import datetime
import json

from ict_cockpit.analysis.amdx import aware, require_id, timestamp
from ict_cockpit.analysis.amdx_rules import Evaluation
from ict_cockpit.database.amdx_repository import _json


@dataclass(frozen=True)
class StudyCriterionRecord:
    task_id: str
    plan_id: str
    question: str
    instrument: str
    recorded_at: datetime
    evaluation: Evaluation

    def __post_init__(self):
        for value in (self.task_id, self.plan_id, self.question, self.instrument):
            require_id(value)
        aware(self.recorded_at)
        if self.evaluation.run_id is not None:
            raise ValueError('Independent Study evaluation cannot own a Trading Run')
        if len(self.evaluation.definitions) != 1:
            raise ValueError('Choose exactly one retained criterion for this Study task')

    def to_payload(self):
        return dict(version=1, task_id=self.task_id, plan_id=self.plan_id, question=self.question,
                    instrument=self.instrument, recorded_at=self.recorded_at.isoformat(),
                    evaluation=self.evaluation.to_payload())

    @classmethod
    def from_payload(cls, item):
        if item.get('version') != 1:
            raise ValueError('Unsupported Study evaluation version')
        return cls(item['task_id'], item['plan_id'], item['question'], item['instrument'],
                   timestamp(item['recorded_at']), Evaluation.from_payload(item['evaluation']))


class StudyCriterionRepository:
    def __init__(self, amdx):
        self.amdx, self.connection = amdx, amdx.connection

    def get(self, identity):
        row = self.connection.execute('SELECT task_id,payload_json FROM study_criterion_evaluation WHERE id=?', (identity,)).fetchone()
        if row is None:
            return None
        record = StudyCriterionRecord.from_payload(json.loads(row[1]))
        if record.task_id != row[0] or record.evaluation.id != identity:
            raise ValueError('Stored Study identity disagrees with its retained basis')
        d = record.evaluation.definitions[0]
        if self.amdx.definitions.get(plan_revision=d.plan_revision, rule_id=d.id,
                revision=d.revision, publication=d.publication) != d:
            raise ValueError('Study result disagrees with its retained definition')
        return record

    def list_for_task(self, task_id):
        return tuple(self.get(row[0]) for row in self.connection.execute(
            'SELECT id FROM study_criterion_evaluation WHERE task_id=? ORDER BY rowid', (task_id,)).fetchall())

    def save(self, record):
        record = StudyCriterionRecord.from_payload(record.to_payload())
        with self.amdx._transaction():
            old = self.get(record.evaluation.id)
            if old is not None:
                if old != record:
                    raise ValueError('A saved Study result cannot be overwritten')
                return old
            d = record.evaluation.definitions[0]
            if self.amdx.definitions.get(plan_revision=d.plan_revision, rule_id=d.id,
                    revision=d.revision, publication=d.publication) != d:
                raise ValueError('Save the criterion revision before evaluating it')
            self.connection.execute('INSERT INTO study_criterion_evaluation VALUES (?,?,?)',
                (record.evaluation.id, record.task_id, _json(record.to_payload())))
        return record
