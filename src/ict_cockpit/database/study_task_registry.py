"""Explicit resumable task identities; historical receipts remain unchanged."""
import json


class StudyTaskRegistry:
    def __init__(self, connection):
        self.connection = connection

    def register(self, task_id, plan_id, revision, question):
        existing = self.connection.execute('SELECT plan_id,plan_revision,question FROM study_task_registry WHERE task_id=?', (task_id,)).fetchone()
        values = (plan_id, revision, question.strip())
        if existing and tuple(existing) != values:
            raise ValueError('Investigation identity already has different wording or revision; start a new investigation for a different question.')
        with self.connection:
            self.connection.execute('INSERT OR IGNORE INTO study_task_registry VALUES (?,?,?,?)', (task_id, *values))

    def choices(self, plan_id, revision):
        variants = {}
        def add(task, rev, question):
            if task and rev == revision and question.strip():
                variants.setdefault(task, set()).add(question.strip())
        for task, rev, question in self.connection.execute('SELECT task_id,plan_revision,question FROM study_investigation_capture WHERE plan_id=?', (plan_id,)):
            add(task, rev, question)
        for table in ('study_review', 'study_finding', 'study_criterion_evaluation'):
            for (payload,) in self.connection.execute('SELECT payload_json FROM ' + table):
                item = json.loads(payload)
                if table == 'study_finding':
                    item = item.get('investigation') or {}
                if item.get('plan_id') != plan_id:
                    continue
                rev = item.get('plan_revision')
                if table == 'study_criterion_evaluation':
                    definitions = item.get('evaluation', {}).get('definitions', [])
                    rev = definitions[0].get('plan_revision') if definitions else None
                add(item.get('task_id'), rev, item.get('question', ''))
        registered = {}
        for task, question in self.connection.execute('SELECT task_id,question FROM study_task_registry WHERE plan_id=? AND plan_revision=?', (plan_id, revision)):
            registered[task] = question
            variants.setdefault(task, set())
        # Registered wording is explicit; conflicting legacy variants require a choice.
        return [(task, registered[task] if task in registered else q, task not in registered)
                for task in sorted(variants)
                for q in ([registered[task]] if task in registered else sorted(variants[task]))]

    def context(self, capture_id):
        row = self.connection.execute('SELECT payload_json FROM study_capture_context WHERE capture_id=?', (capture_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def remember_context(self, capture_id, context):
        with self.connection:
            self.connection.execute('INSERT INTO study_capture_context VALUES (?,?) ON CONFLICT(capture_id) DO UPDATE SET payload_json=excluded.payload_json', (capture_id, json.dumps(context)))
