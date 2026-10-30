"""Durable follow-up questions with frozen capture context, separate from assessments."""
from datetime import datetime
import json


class StudyQuestionRepository:
    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def validate(item):
        if item.get('version') not in (1, 2):
            raise ValueError('Unsupported Study question version')
        for key in ('id', 'plan_id', 'plan_revision', 'question', 'recorded_at'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f'{key} is required')
        stamp = datetime.fromisoformat(item['recorded_at'])
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError('Recording time requires a timezone')
        source = item.get('source')
        if item['version'] == 2:
            if not isinstance(source, dict) or source.get('kind') != 'review':
                raise ValueError('Review source snapshot is required')
            for key in ('review_id', 'task_id', 'plan_id', 'plan_revision', 'question', 'state', 'selected_field'):
                if not isinstance(source.get(key), str):
                    raise ValueError(f'Review source {key} must be retained')
            if not source['review_id'] or not source['task_id']:
                raise ValueError('Review identity is required')
            if source['plan_id'] != item['plan_id'] or source['plan_revision'] != item['plan_revision']:
                raise ValueError('Review source plan differs from question')
            if source['state'] not in ('Draft review snapshot', 'Saved review snapshot'):
                raise ValueError('Invalid review snapshot state')
            if source['selected_field'] not in ('', 'understanding', 'uncertainty', 'next_step'):
                raise ValueError('Invalid review field')
            if not isinstance(source.get('fields'), dict) or any(not isinstance(source['fields'].get(k), str) for k in ('understanding', 'uncertainty', 'next_step')):
                raise ValueError('Review wording must be retained')
            if not isinstance(source.get('sources'), list):
                raise ValueError('Review support snapshot must be retained')
            if not isinstance(item.get('original_text'), str):
                raise ValueError('Original selected text must be retained')
            return
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


def describe_review_question(item):
    source = item['source']
    lines = [f"Question: {item['question']}", f"Original selected text: {item['original_text'] or '(none)'}",
             f"Plan revision: {item['plan_revision']} · recorded {item['recorded_at']}",
             f"Source review {source['review_id']} · {source['state']}",
             f"Investigation: {source['question']} · {source['task_id']}",
             f"Selected review field: {source['selected_field'] or '(composer)'}"]
    lines.extend(f"{key}: {value}" for key, value in source['fields'].items())
    lines.extend(['Support snapshot:', json.dumps(source['sources'], indent=2),
                  'Retained at question capture. A draft review snapshot is not a saved checkpoint. '
                  'No market date, capture association or competency judgment is inferred.'])
    return '\n\n'.join(lines)
