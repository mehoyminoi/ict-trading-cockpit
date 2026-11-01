"""Immutable technician findings; association is explicit, never inferred evidence."""
from datetime import datetime
import json

from ict_cockpit.database.study_question_repository import StudyQuestionRepository


class StudyFindingRepository:
    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def validate(item):
        if not isinstance(item.get('finding'), str) or not item['finding'].strip():
            raise ValueError('Enter a finding before keeping it')
        # The source envelope has the same provenance requirements as retained questions.
        StudyQuestionRepository.validate({**item, 'question': item.get('finding')})
        if item.get('kind') not in ('Finding', 'Partial answer'):
            raise ValueError('Choose Finding or Partial answer')
        navigation = item['source'].get('navigation_context')
        if navigation is not None and (not isinstance(navigation, dict) or any(
                not isinstance(navigation.get(k), str)
                for k in ('question', 'market_reference', 'interpretation'))):
            raise ValueError('Invalid capture-open navigation snapshot')
        association = item.get('investigation')
        if item['kind'] == 'Partial answer' and association is None:
            raise ValueError('A partial answer requires an explicit investigation association')
        if association is not None:
            keys = ('task_id', 'plan_id', 'plan_revision', 'question', 'instrument',
                    'market_reference', 'interpretation')
            if not isinstance(association, dict) or any(
                    not isinstance(association.get(k), str) or not association[k].strip() for k in keys):
                raise ValueError('Investigation destination is incomplete')
            if association['plan_id'] != item['plan_id']:
                raise ValueError('Investigation belongs to another Trade Plan')
            stamp = datetime.fromisoformat(association['market_reference'])
            if stamp.tzinfo is None or stamp.utcoffset() is None:
                raise ValueError('Historical reference requires a timezone')
            if association['interpretation'] not in ('Expected', 'Observed'):
                raise ValueError('Invalid investigation interpretation')

    def get(self, identity):
        row = self.connection.execute(
            'SELECT plan_id,task_id,payload_json FROM study_finding WHERE id=?', (identity,)).fetchone()
        if row is None:
            return None
        item = json.loads(row[2])
        self.validate(item)
        task = (item.get('investigation') or {}).get('task_id')
        if (item['id'], item['plan_id'], task) != (identity, row[0], row[1]):
            raise ValueError('Study finding identity mismatch')
        return item

    def list_for_plan(self, plan_id):
        return tuple(self.get(row[0]) for row in self.connection.execute(
            'SELECT id FROM study_finding WHERE plan_id=? ORDER BY rowid DESC', (plan_id,)).fetchall())

    def list_for_task(self, plan_id, task_id):
        return tuple(self.get(row[0]) for row in self.connection.execute(
            'SELECT id FROM study_finding WHERE plan_id=? AND task_id=? ORDER BY rowid DESC',
            (plan_id, task_id)).fetchall())

    def save(self, item):
        self.validate(item)
        encoded = json.dumps(item, sort_keys=True, allow_nan=False)
        if self.connection.in_transaction:
            raise RuntimeError('Finish the pending transaction before saving a finding')
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            old = self.get(item['id'])
            if old is not None:
                if old != item:
                    raise ValueError('Saved findings cannot be overwritten')
                return old
            task = (item.get('investigation') or {}).get('task_id')
            self.connection.execute('INSERT INTO study_finding VALUES (?,?,?,?)',
                                    (item['id'], item['plan_id'], task, encoded))
        return self.get(item['id'])


def describe_finding(item):
    source = item['source']
    target = item.get('investigation')
    context = (f"Associated investigation: {target['question']}\n"
               f"Reference: {target['market_reference']} · {target['interpretation']}"
               if target else 'Standalone finding · no investigation association.')
    navigation = source.get('navigation_context')
    navigation_text = (f"Capture-open navigation (not a saved capture link): {navigation['question']}\n"
                       f"{navigation['market_reference']} · {navigation['interpretation']}\n"
                       if navigation else '')
    return (f"{item['kind']}: {item['finding']}\n\n{context}\n\n"
            f"Original selected wording: {item['original_text'] or '(none)'}\n"
            f"Plan revision: {item['plan_revision']} · recorded {item['recorded_at']}\n"
            f"Source capture {source['capture_id']} · {source['state']}\n"
            f"{navigation_text}"
            f"{source['date']} · {source['instrument']} · {source['session']}\n\n"
            f"Pattern: {source['pattern']}\nObservation: {source['observation']}\n\nNotes: {source['notes']}\n\n"
            'Chart references:\n' + ('\n'.join(source['images']) or '(none)') +
            '\n\nTechnician interpretation, not a verified answer or competency assessment. '
            'The frozen source snapshot survives later capture edits or draft discard; chart paths reference existing files.')
