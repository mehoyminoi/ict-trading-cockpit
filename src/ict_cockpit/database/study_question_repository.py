"""Durable follow-up questions with frozen capture context, separate from assessments."""
from datetime import datetime
import json


class StudyQuestionRepository:
    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def validate(item):
        if item.get('version') != 1:
            raise ValueError('Unsupported Study question version')
        for key in ('id', 'plan_id', 'plan_revision', 'question', 'recorded_at'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f'{key} is required')
        stamp = datetime.fromisoformat(item['recorded_at'])
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError('Recording time requires a timezone')
        source = item.get('source')
        if not isinstance(source, dict) or not source.get('capture_id'):
            raise ValueError('Capture source snapshot is required')
        for key in ('date', 'instrument', 'session', 'pattern', 'observation', 'notes', 'state'):
            if not isinstance(source.get(key), str):
                raise ValueError(f'Source {key} must be retained')
        if not isinstance(source.get('images'), list) or any(not isinstance(x, str) for x in source['images']):
            raise ValueError('Chart references must be a list of paths')
        association = source.get('association')
        if association is not None and (not isinstance(association, dict) or
                not all(isinstance(association.get(k), str) for k in ('question', 'market_reference'))):
            raise ValueError('Invalid source association snapshot')
        if not isinstance(item.get('original_text'), str):
            raise ValueError('Original selected text must be retained')

    def get(self, identity):
        row = self.connection.execute('SELECT plan_id,payload_json FROM study_question WHERE id=?', (identity,)).fetchone()
        if row is None:
            return None
        item = json.loads(row[1])
        self.validate(item)
        if item['id'] != identity or item['plan_id'] != row[0]:
            raise ValueError('Study question identity mismatch')
        return item

    def list_for_plan(self, plan_id):
        return tuple(self.get(row[0]) for row in self.connection.execute(
            'SELECT id FROM study_question WHERE plan_id=? ORDER BY rowid DESC', (plan_id,)).fetchall())

    def save(self, item):
        self.validate(item)
        encoded = json.dumps(item, sort_keys=True, allow_nan=False)
        if self.connection.in_transaction:
            raise RuntimeError('Finish the pending transaction before saving a question')
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            old = self.get(item['id'])
            if old is not None:
                if old != item:
                    raise ValueError('Saved questions cannot be overwritten')
                return old
            self.connection.execute('INSERT INTO study_question VALUES (?,?,?)',
                                    (item['id'], item['plan_id'], encoded))
        return self.get(item['id'])
