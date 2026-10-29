"""Investigation synthesis snapshots, independent of run-based competency evidence."""
from dataclasses import asdict
from datetime import datetime
import json

from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.database.study_investigation_repository import StudyInvestigationRepository
from ict_cockpit.database.study_finding_repository import StudyFindingRepository
from ict_cockpit.database.study_criterion_repository import StudyCriterionRepository
from ict_cockpit.database.amdx_repository import AMDXRepository


class StudyReviewRepository:
    def __init__(self, connection):
        self.connection = connection

    def source(self, kind, identity, plan_id, task_id):
        if kind == 'capture':
            links = StudyInvestigationRepository(self.connection)
            link = links.get(identity)
            finds = StudyFindRepository(self.connection)
            find = finds.get_by_id(identity)
            if not link or not find:
                raise ValueError('Save the linked capture before using it as review support')
            scope = (link['plan_id'], link['task_id'])
            payload = dict(association=link, capture=asdict(find), images=finds.get_images(identity))
        elif kind == 'finding':
            item = StudyFindingRepository(self.connection).get(identity)
            link = (item or {}).get('investigation')
            if not link:
                raise ValueError('Finding is unavailable or not associated with this investigation')
            scope = (item['plan_id'], link['task_id'])
            payload = item
        elif kind == 'result':
            record = StudyCriterionRepository(AMDXRepository(self.connection)).get(identity)
            if not record:
                raise ValueError('Criterion result unavailable')
            scope = (record.plan_id, record.task_id)
            payload = record.to_payload()
        else:
            raise ValueError('Unsupported review source')
        if scope != (plan_id, task_id):
            raise ValueError('Supporting material belongs to another investigation')
        return json.loads(json.dumps(dict(kind=kind, id=identity, snapshot=payload), default=str))

    @staticmethod
    def validate(item):
        if item.get('version') != 1:
            raise ValueError('Unsupported review version')
        for key in ('id', 'plan_id', 'plan_revision', 'task_id', 'recorded_at'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f'{key} is required')
        for key in ('question', 'understanding', 'uncertainty', 'next_step'):
            if not isinstance(item.get(key), str):
                raise ValueError(f'{key} must be text')
        if not any(item[k].strip() for k in ('understanding', 'uncertainty', 'next_step')):
            raise ValueError('Keep at least one thought; no conclusion is required')
        stamp = datetime.fromisoformat(item['recorded_at'])
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError('Recording time requires a timezone')
        if not isinstance(item.get('sources'), list):
            raise ValueError('Supporting references must be a list')
        seen = set()
        for source in item['sources']:
            if not isinstance(source, dict) or source.get('kind') not in ('capture', 'finding', 'result') or not isinstance(source.get('id'), str) or not source['id'] or not isinstance(source.get('snapshot'), dict):
                raise ValueError('Invalid supporting snapshot')
            key = (source['kind'], source['id'])
            if key in seen:
                raise ValueError('Duplicate supporting reference')
            seen.add(key)

    def get(self, identity):
        row = self.connection.execute('SELECT plan_id,task_id,payload_json FROM study_review WHERE id=?', (identity,)).fetchone()
        if row is None:
            return None
        item = json.loads(row[2])
        self.validate(item)
        if (item['id'], item['plan_id'], item['task_id']) != (identity, row[0], row[1]):
            raise ValueError('Review identity mismatch')
        return item

    def list_for_plan(self, plan_id):
        return tuple(self.get(row[0]) for row in self.connection.execute(
            'SELECT id FROM study_review WHERE plan_id=? ORDER BY rowid DESC', (plan_id,)).fetchall())

    def list_for_task(self, plan_id, task_id):
        return tuple(self.get(row[0]) for row in self.connection.execute(
            'SELECT id FROM study_review WHERE plan_id=? AND task_id=? ORDER BY rowid DESC', (plan_id, task_id)).fetchall())

    def save(self, item):
        self.validate(item)
        if self.connection.in_transaction:
            raise RuntimeError('Finish the pending transaction before saving a review')
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            old = self.get(item['id'])
            if old is not None:
                if old != item:
                    raise ValueError('Saved reviews cannot be overwritten; keep a later checkpoint')
                return old
            for source in item['sources']:
                if source != self.source(source['kind'], source['id'], item['plan_id'], item['task_id']):
                    raise ValueError('Supporting material changed; inspect and select it again')
            self.connection.execute('INSERT INTO study_review VALUES (?,?,?,?)',
                (item['id'], item['plan_id'], item['task_id'], json.dumps(item, sort_keys=True, allow_nan=False)))
        return self.get(item['id'])


def describe_review(item):
    lines = [f"Question as reviewed: {item['question'] or '(not entered)'}",
             f"Plan {item['plan_revision']} · recorded {item['recorded_at']}"]
    for key, label in [('understanding', 'Current understanding'), ('uncertainty', 'Uncertainty / counterexamples'), ('next_step', 'Next study step')]:
        if item[key].strip():
            lines.extend(['', label + ':', item[key]])
    lines += ['', 'Explicit supporting material:']
    if not item['sources']:
        lines.append('(none selected)')
    for source in item['sources']:
        lines.append(f"{source['kind']} · {source['id']}")
        snapshot = source['snapshot']
        if source['kind'] == 'finding':
            from ict_cockpit.database.study_finding_repository import describe_finding
            lines.append(describe_finding(snapshot))
        elif source['kind'] == 'capture':
            from ict_cockpit.database.study_investigation_repository import describe_association
            capture = snapshot['capture']
            lines.extend([describe_association(snapshot['association']),
                f"{capture['observation_date']} · {capture['instrument']} · {capture['session']}",
                f"Pattern: {capture['pattern_name']}", f"Observation: {capture['observation']}",
                f"Notes: {capture['notes']}", f"Available move: {capture['available_move_handles']}",
                "Chart references: " + (', '.join(snapshot['images']) or '(none)')])
        else:
            from ict_cockpit.database.study_criterion_repository import StudyCriterionRecord
            record = StudyCriterionRecord.from_payload(snapshot)
            lines.extend([record.question, f"{record.instrument} · {record.evaluation.market_reference.isoformat()}"])
            for definition, result in zip(record.evaluation.definitions, record.evaluation.results):
                lines.extend([f"Criterion {definition.id} · revision {definition.revision} · plan {definition.plan_revision}",
                              f"Result: {result.state}", f"Definition: {definition.description}" if hasattr(definition, 'description') else f"Role: {definition.role}"])
        lines.append('')
    lines.extend(['', 'Retained review basis. Chart paths reference files, not embedded images. No competency assessment or investigation completion.'])
    return '\n'.join(lines)
