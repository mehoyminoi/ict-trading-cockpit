from dataclasses import replace
from datetime import timedelta
import copy

import pytest

from ict_cockpit.analysis.amdx import intraday_cycles, payload
from ict_cockpit.analysis.amdx_rules import (
    QuartetScope, Condition, Evaluation, evaluate, EVALUATION_REVISION,
    SCOPED_EVALUATION_REVISION,
)
from ict_cockpit.database.bootstrap import open_application_database
from ict_cockpit.database.amdx_repository import AMDXRepository
from test_amdx_repository import assessment, saved_run, REFERENCE


class SyntheticRun:
    id = 'synthetic'


def basis():
    original = assessment(SyntheticRun())
    definition = original.definitions[0]
    return original, replace(definition, conditions=(replace(definition.conditions[0], scope_id=QuartetScope(2)),))


def test_same_definition_binds_two_dates_and_retains_both_bases(tmp_path):
    c = open_application_database(tmp_path / 'scopes.db')
    run = saved_run(c)
    repo = AMDXRepository(c)
    original, definition = basis()
    repo.definitions.save_candidate(definition)
    results = []
    for offset in (0, 1):
        reference = REFERENCE + timedelta(days=offset)
        cycle = intraday_cycles(reference)[0]
        fact = replace(original.facts[0], id=f'fact-{offset}', scope_id=cycle.quarters[1].id,
                       available_at=reference)
        result = evaluate(evaluation_id=f'ev-{offset}', run_id=run.id, cycle=cycle,
                          market_reference=reference, definitions=(definition,), facts=(fact,))
        assert result.revision == SCOPED_EVALUATION_REVISION
        assert result.results[0].state == 'Matched'
        assert cycle.quarters[1].id in result.results[0].reasons[0]
        assert result.definitions == (definition,)
        results.append(repo.save_evaluation(result, recorded_at=reference))
    assert results[0].evaluation.cycle != results[1].evaluation.cycle
    for result in results:
        assert repo.get_evaluation(result.evaluation.id) == result
    c.close()


def test_old_fixed_scope_never_rebinds_and_serialization_stays_v1():
    old, relative = basis()
    assert old.revision == EVALUATION_REVISION
    assert isinstance(old.to_payload()['evaluation']['definitions'][0]['conditions'][0]['scope_id'], str)
    assert Evaluation.from_payload(old.to_payload()) == old
    later = intraday_cycles(REFERENCE + timedelta(days=1))[0]
    fact = replace(old.facts[0], scope_id=later.quarters[1].id)
    result = evaluate(evaluation_id='fixed', run_id='synthetic', cycle=later,
                      market_reference=REFERENCE + timedelta(days=1), definitions=old.definitions, facts=(fact,))
    assert result.results[0].state == 'Unknown'
    assert result.definitions == old.definitions


def test_wrong_scope_future_and_missing_inputs_stay_unknown():
    old, definition = basis()
    wrong = replace(old.facts[0], scope_id=old.cycle.quarters[0].id)
    future = replace(old.facts[0], available_at=REFERENCE + timedelta(minutes=1))
    for facts in ((), (wrong,), (future,)):
        result = evaluate(evaluation_id='unknown', run_id='synthetic', cycle=old.cycle,
                          market_reference=REFERENCE, definitions=(definition,), facts=facts)
        assert result.results[0].state == 'Unknown'
    other_layer = replace(definition, layer='session')
    result = evaluate(evaluation_id='other', run_id='synthetic', cycle=old.cycle,
                      market_reference=REFERENCE, definitions=(other_layer,), facts=old.facts)
    assert result.results[0].state == 'Not Applicable'


def test_tampered_binding_or_evaluator_revision_is_rejected():
    old, definition = basis()
    result = evaluate(evaluation_id='scoped', run_id='synthetic', cycle=old.cycle,
                      market_reference=REFERENCE, definitions=(definition,), facts=old.facts)
    assert Evaluation.from_payload(result.to_payload()) == result
    altered = copy.deepcopy(result.to_payload())
    altered['evaluation']['definitions'][0]['conditions'][0]['scope_id']['position'] = 1
    with pytest.raises(ValueError, match='disagrees'):
        Evaluation.from_payload(altered)
    altered = copy.deepcopy(result.to_payload())
    altered['evaluation']['revision'] = EVALUATION_REVISION
    with pytest.raises(ValueError, match='disagrees'):
        Evaluation.from_payload(altered)


@pytest.mark.parametrize('scope', [
    {'kind': 'selected-quartet-quarter-v1', 'position': 0},
    {'kind': 'selected-quartet-quarter-v1', 'position': True},
    {'kind': 'future-v99', 'position': 2},
    {'position': 2},
])
def test_unknown_or_malformed_scope_is_rejected(scope):
    with pytest.raises(ValueError):
        Condition(scope, 'feature', 'eq', True)
