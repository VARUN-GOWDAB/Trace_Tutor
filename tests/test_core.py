import csv
import json
import os
import pytest
from storage import load_exercises, append_log
from runner import run_tests, is_current, ExecutionUnavailable, harness
from hints import parse_hint, validate_claims, get_hint


@pytest.fixture
def example():
    e = load_exercises()[0]
    return e, run_tests(e, e['starter'])


@pytest.mark.parametrize('index', range(5))
def test_fixtures(index):
    e = load_exercises()[index]
    assert any(r['status'] != 'pass' for r in run_tests(e, e['starter'])['rows'])
    assert all(r['status'] == 'pass' for r in run_tests(e, e['reference'])['rows'])
    with pytest.raises(ExecutionUnavailable):
        run_tests(e, e['starter'] + '\n# changed')
    compile(harness(e, e['starter']), '<sandbox harness>', 'exec')


@pytest.mark.parametrize('value', [True, '30', 30.0, 31])
def test_wrong_value_type(example, value):
    e, r = example
    with pytest.raises(ValueError):
        validate_claims({'claims': [{'test_id': 'sum_01', 'field': 'actual', 'value': value}]}, r, r['submission_id'])


def test_claims(example):
    e, r = example
    obj = parse_hint(json.dumps({'hint': 'Check the boundary', 'claims': [{'test_id': 'sum_01', 'field': 'actual', 'value': 30}]}))
    assert validate_claims(obj, r, r['submission_id']) == 'claims_match'
    with pytest.raises(ValueError):
        validate_claims(obj, r, 'stale')
    obj['claims'][0]['test_id'] = 'unknown'
    with pytest.raises(ValueError):
        validate_claims(obj, r, r['submission_id'])
    assert validate_claims({'claims': []}, r, r['submission_id']) == 'no_claims_checked'


@pytest.mark.parametrize('raw', ['not json', '{}', '{"hint": "x", "claims": [1]}', '{"hint":"wrong", "claims":[{"test_id":"sum_01","field":"actual","value":99}]}'])
def test_retry_fallback(example, raw):
    e, r = example
    r['mode'] = 'live'
    calls = []
    def fake(payload):
        calls.append(payload)
        return raw
    event = get_hint(e, e['starter'], r, 1, 'live', call=fake)
    assert len(calls) == 2
    assert event['fallback'] and event['retry']


def test_empty_and_repair(example):
    e, r = example
    r['mode'] = 'live'
    responses = iter(['{}', '{"hint":"Check the loop", "claims":[]}'])
    event = get_hint(e, e['starter'], r, 1, 'live', call=lambda p: next(responses))
    assert event['retry'] and not event['fallback']
    assert event['validation'] == 'no_claims_checked'


def test_service_and_stale(example, monkeypatch):
    e, r = example
    monkeypatch.delenv('E2B_API_KEY', raising=False)
    with pytest.raises(ExecutionUnavailable):
        run_tests(e, e['starter'], 'live')
    assert not is_current(r, e, 'edited', 'demo')
    with pytest.raises(ValueError):
        get_hint(e, 'edited', r, 1, 'demo')
    r['mode'] = 'live'
    def unavailable(p):
        raise RuntimeError('secret must not be logged')
    event = get_hint(e, e['starter'], r, 1, 'live', call=unavailable)
    assert event['fallback'] and not event['retry']
    assert 'secret' not in event['failure_reason']


def test_csv(example, tmp_path):
    e, r = example
    path = tmp_path / 'events.csv'
    event = get_hint(e, e['starter'], r, 1, 'demo')
    append_log(event, path)
    append_log(event, path)
    with path.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2 and rows[0]['submission_id'] == r['submission_id']


def test_invalid_service_response(example, monkeypatch):
    import runner
    e, r = example
    for rows in ([], [{'id': 'unrelated', 'actual': 60, 'status': 'returned'}] * 4):
        monkeypatch.setattr(runner, 'live_rows', lambda *args: rows)
        with pytest.raises(ExecutionUnavailable):
            run_tests(e, e['starter'], 'live')


def test_sandbox_adapter_cleanup(example, monkeypatch):
    import e2b_code_interpreter
    from types import SimpleNamespace
    e, r = example
    calls = []
    class FakeSandbox:
        @classmethod
        def create(cls, **kwargs):
            calls.append('create')
            return cls()
        def run_code(self, code, **kwargs):
            assert kwargs['timeout'] == 10
            assert e['reference'] not in code
            return SimpleNamespace(error=None, logs=SimpleNamespace(stdout=[json.dumps([
                {'id': row['id'], 'actual': row['actual'], 'status': 'returned'} for row in r['rows']])]))
        def kill(self):
            calls.append('kill')
    monkeypatch.setenv('E2B_API_KEY', 'mock-key')
    monkeypatch.setattr(e2b_code_interpreter, 'Sandbox', FakeSandbox)
    assert run_tests(e, e['starter'], 'live')['rows'] == r['rows']
    assert calls == ['create', 'kill']


@pytest.mark.skipif(os.getenv('TRACETUTOR_LIVE_TESTS') != '1' or not os.getenv('E2B_API_KEY'), reason='Explicit live opt-in and E2B credentials required')
@pytest.mark.parametrize('index', range(5))
def test_live_reference_and_bug(index):
    e = load_exercises()[index]
    assert all(r['status'] == 'pass' for r in run_tests(e, e['reference'], 'live')['rows'])
    live = run_tests(e, e['starter'], 'live')
    demo = run_tests(e, e['starter'], 'demo')
    assert live['rows'] == demo['rows']
