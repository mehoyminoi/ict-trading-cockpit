from dataclasses import replace

import pytest

from ict_cockpit.analysis.amdx import Role
from ict_cockpit.database.amdx_repository import AMDXRepository
from ict_cockpit.database.bootstrap import open_application_database
from test_amdx_repository import assessment, saved_run, REFERENCE


def test_candidate_can_be_saved_without_run_and_reopened(tmp_path):
    path = tmp_path / "criteria.db"
    connection = open_application_database(path)
    # Fixture evaluation supplies a synthetic definition; no run is saved here.
    class Run:
        id = "not-a-saved-run"
    definition = assessment(Run()).definitions[0]
    repo = AMDXRepository(connection)
    repo.definitions.save_candidate(definition)
    changes = connection.total_changes
    repo.definitions.save_candidate(definition)
    assert connection.total_changes == changes
    for table in ("trading_session_run", "amdx_evaluation", "amdx_claim", "amdx_cycle_identity"):
        assert connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
    connection.close()
    connection = open_application_database(path)
    assert AMDXRepository(connection).definitions.list_revisions(plan_revision=definition.plan_revision) == (definition,)
    connection.close()


def test_revision_conflict_and_publication_rejected_without_writes(tmp_path):
    connection = open_application_database(tmp_path / "criteria.db")
    run = saved_run(connection)
    repo = AMDXRepository(connection)
    definition = assessment(run).definitions[0]
    repo.definitions.save_candidate(definition)
    with pytest.raises(ValueError, match="new revision"):
        repo.definitions.save_candidate(replace(definition, rationale="Different criterion"))
    with pytest.raises(ValueError, match="cannot publish"):
        repo.definitions.save_candidate(replace(definition, publication="Published"))
    assert repo.definitions.list_revisions(plan_revision=definition.plan_revision) == (definition,)
    connection.close()


def test_candidate_edits_preserve_evaluated_and_published_basis(tmp_path):
    connection = open_application_database(tmp_path / "criteria.db")
    run = saved_run(connection)
    repo = AMDXRepository(connection)
    original = assessment(run)
    repo.definitions.save_candidate(original.definitions[0])
    saved = repo.save_evaluation(original, recorded_at=REFERENCE)
    alternative = assessment(run, id="alternative", revision="v2", role=Role.X)
    repo.definitions.save_candidate(alternative.definitions[0])
    repo.save_evaluation(alternative, recorded_at=REFERENCE)
    assert repo.get_evaluation(original.id) == saved
    assert len(repo.definitions.list_revisions(plan_revision="synthetic-plan", rule_id="synthetic-rule")) == 2
    assert repo.definitions.list_revisions(plan_revision="other-plan") == ()
    assert repo.definitions.list_revisions(plan_revision="synthetic-plan", publication="Published") == ()
    assert original.profile() != alternative.profile()
    # Existing evaluation path may retain externally supplied published definitions;
    # candidate authoring must never alter them.
    from ict_cockpit.analysis.amdx_rules import evaluate
    published_rule = replace(original.definitions[0], publication="Published")
    published = evaluate(evaluation_id="published", run_id=run.id, cycle=original.cycle,
                         market_reference=REFERENCE, definitions=(published_rule,), facts=original.facts)
    stored = repo.save_evaluation(published, recorded_at=REFERENCE)
    repo.definitions.save_candidate(replace(published_rule, publication="Candidate", revision="v3"))
    assert repo.get_evaluation("published") == stored
    connection.close()


def test_candidate_save_does_not_commit_callers_transaction(tmp_path):
    connection = open_application_database(tmp_path / "criteria.db")
    run = saved_run(connection)
    repo = AMDXRepository(connection)
    connection.execute("BEGIN")
    with pytest.raises(RuntimeError, match="pending transaction"):
        repo.definitions.save_candidate(assessment(run).definitions[0])
    assert connection.in_transaction
    connection.rollback()
    assert repo.definitions.list_revisions(plan_revision="synthetic-plan") == ()
    connection.close()
