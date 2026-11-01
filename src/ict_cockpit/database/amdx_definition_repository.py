"""Independent candidate revisions in the existing immutable definition registry.

Saving a candidate is not publication, evaluation, calendar adoption or run creation.
Input scope IDs remain explicit; this layer does not invent reusable scope bindings.
"""
import json

from ict_cockpit.analysis.amdx import payload, require_id
from ict_cockpit.analysis.amdx_rules import Condition, Definition
from ict_cockpit.database.amdx_repository import _json


class AMDXDefinitionRepository:
    def __init__(self, amdx):
        self.amdx = amdx
        self.connection = amdx.connection

    @staticmethod
    def _decode(encoded):
        item = json.loads(encoded)
        return Definition(**{**item, "conditions": tuple(Condition(**c) for c in item["conditions"])})

    def get(self, *, plan_revision, rule_id, revision, publication):
        key = (plan_revision, rule_id, revision, publication)
        row = self.connection.execute("""
            SELECT payload_json FROM amdx_definition_revision
            WHERE plan_revision=? AND rule_id=? AND rule_revision=? AND publication=?
        """, key).fetchone()
        if row is None:
            return None
        definition = self._decode(row[0])
        if (definition.plan_revision, definition.id, definition.revision, definition.publication) != key:
            raise ValueError("Definition payload disagrees with its stored identity")
        return definition

    def list_revisions(self, *, plan_revision, rule_id=None, publication=None):
        require_id(plan_revision)
        if publication not in (None, "Candidate", "Published"):
            raise ValueError("Unknown definition publication status")
        rows = self.connection.execute("""
            SELECT rule_id, rule_revision, publication FROM amdx_definition_revision
            WHERE plan_revision=? AND (? IS NULL OR rule_id=?)
                AND (? IS NULL OR publication=?)
            ORDER BY rule_id, rule_revision, publication
        """, (plan_revision, rule_id, rule_id, publication, publication)).fetchall()
        # Explicit deterministic identity order; never infer a latest/adopted revision.
        return tuple(self.get(plan_revision=plan_revision, rule_id=r[0], revision=r[1], publication=r[2])
                     for r in rows)

    def save_candidate(self, definition):
        definition = self._decode(_json(payload(definition)))
        if definition.publication != "Candidate":
            raise ValueError("Candidate authoring cannot publish a definition")
        with self.amdx._transaction():
            self._store_locked(definition)
        return definition

    def _store_locked(self, definition):
        """Internal registry write shared with the existing evaluation transaction."""
        key = (definition.plan_revision, definition.id, definition.revision, definition.publication)
        encoded = _json(payload(definition))
        existing = self.get(plan_revision=key[0], rule_id=key[1], revision=key[2], publication=key[3])
        if existing is not None:
            if _json(payload(existing)) != encoded:
                raise ValueError("A recorded definition revision has different content; use a new revision")
            return
        self.connection.execute("""
            INSERT INTO amdx_definition_revision
                (plan_revision, rule_id, rule_revision, publication, payload_json)
            VALUES (?, ?, ?, ?, ?)
        """, key + (encoded,))
