"""Student code is executed only by E2B. Demo values are authored fixtures."""
import hashlib
import json
import os
import uuid
from storage import ROOT


class ExecutionUnavailable(Exception):
    pass


def code_hash(code):
    return hashlib.sha256(code.encode('utf-8')).hexdigest()


def same_value(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(same_value(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same_value(a[k], b[k]) for k in a)
    return a == b


def harness(exercise, code):
    # This string is sent to the managed sandbox, never executed on the host.
    prefix = f'SOURCE = {code!r}\nTESTS = {[{"id": t["id"], "args": t["args"]} for t in exercise["tests"]]!r}\nFUNCTION = {exercise["function"]!r}\n'
    return prefix + '''import json, contextlib, io
class LimitedOutput(io.StringIO):
    def write(self, text):
        if self.tell() + len(text) > 8192:
            raise RuntimeError("Student output limit exceeded")
        return super().write(text)
rows = []
scope = {}
with contextlib.redirect_stdout(LimitedOutput()), contextlib.redirect_stderr(LimitedOutput()):
    try:
        exec(compile(SOURCE, '<submission>', 'exec'), scope)
    except SyntaxError as error:
        rows = [{'id': t['id'], 'actual': None, 'status': 'syntax_error', 'error': type(error).__name__} for t in TESTS]
    except BaseException as error:
        rows = [{'id': t['id'], 'actual': None, 'status': 'runtime_error', 'error': type(error).__name__} for t in TESTS]
    else:
        for t in TESTS:
            try:
                value = scope[FUNCTION](*t['args'])
            except BaseException as error:
                rows.append({'id': t['id'], 'actual': None, 'status': 'runtime_error', 'error': type(error).__name__})
                continue
            try:
                encoded = json.dumps(value, allow_nan=False)
                if len(encoded) > 8192:
                    raise ValueError('Result too large')
                rows.append({'id': t['id'], 'actual': json.loads(encoded), 'status': 'returned'})
            except (TypeError, ValueError):
                rows.append({'id': t['id'], 'actual': None, 'status': 'serialization_error'})
print(json.dumps(rows))
'''


def live_rows(exercise, code):
    if not os.getenv('E2B_API_KEY'):
        raise ExecutionUnavailable('E2B_API_KEY is missing. No code was executed.')
    from e2b_code_interpreter import Sandbox
    sandbox = None
    try:
        sandbox = Sandbox.create(api_key=os.environ['E2B_API_KEY'], timeout=60)
        result = sandbox.run_code(harness(exercise, code), timeout=10, request_timeout=20)
        if result.error:
            if 'Timeout' in result.error.name:
                return [{'id': t['id'], 'actual': None, 'status': 'timeout'} for t in exercise['tests']]
            raise ExecutionUnavailable('Sandbox harness failed; tests are incomplete.')
        output = ''.join(result.logs.stdout)
        if len(output) > 65536:
            raise ExecutionUnavailable('Sandbox response exceeded the output limit.')
        return json.loads(output)
    except ExecutionUnavailable:
        raise
    except Exception as exc:
        raise ExecutionUnavailable('Execution service unavailable or invalid response; no test verdict.') from exc
    finally:
        if sandbox is not None:
            try:
                sandbox.kill()
            except Exception:
                pass  # Sandbox lifetime is also capped at 60 seconds.


def run_tests(exercise, code, mode='demo'):
    digest = code_hash(code)
    if mode == 'demo':
        fixtures = json.loads((ROOT / 'data/demo_fixtures.json').read_text(encoding='utf-8'))
        fixture = next((f for f in fixtures['fixtures'] if f['exercise_id'] == exercise['id'] and f['code_hash'] == digest), None)
        if fixture is None:
            raise ExecutionUnavailable('Edited code requires live execution. No matching demo fixture.')
        rows = fixture['rows']
    elif mode == 'live':
        rows = live_rows(exercise, code)
    else:
        raise ValueError('Unknown execution mode')
    tests = exercise['tests']
    if not isinstance(rows, list) or len(rows) != len(tests):
        raise ExecutionUnavailable('Incomplete execution response')
    checked = []
    for test, row in zip(tests, rows):
        if row.get('id') != test['id'] or row.get('status') not in {'returned', 'syntax_error', 'runtime_error', 'timeout', 'serialization_error', 'serialization_or_type_error'} or 'actual' not in row:
            raise ExecutionUnavailable('Invalid execution evidence')
        status = row['status']
        if status == 'returned':
            status = 'pass' if same_value(row['actual'], test['expected']) else 'wrong_output'
        checked.append({**test, 'actual': row['actual'], 'status': status,
                        **({'error': str(row['error'])[:100]} if 'error' in row else {})})
    return {'submission_id': str(uuid.uuid4()), 'exercise_id': exercise['id'],
            'code_hash': digest, 'mode': mode, 'rows': checked}


def is_current(result, exercise, code, mode):
    return bool(result and result['exercise_id'] == exercise['id'] and
                result['code_hash'] == code_hash(code) and result['mode'] == mode)
