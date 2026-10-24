"""Authored teaching data and single-process classroom CSV logging."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ['submission_id', 'exercise_id', 'code_hash', 'hint_level', 'mode',
          'model', 'prompt_version', 'hint', 'claim_count', 'validation',
          'retry', 'fallback', 'elapsed_ms', 'failure_reason']


def load_exercises():
    exercises = json.loads((ROOT / 'data/exercises.json').read_text(encoding='utf-8'))
    if len(exercises) != 5 or len({e['id'] for e in exercises}) != 5:
        raise ValueError('Expected five unique authored exercises')
    for e in exercises:
        if not 3 <= len(e['tests']) <= 5 or len(e['hints']) != 3:
            raise ValueError('Invalid teaching material')
        if len({t['id'] for t in e['tests']}) != len(e['tests']):
            raise ValueError('Duplicate test IDs')
    return exercises


def append_log(event, path=None):
    path = Path(path) if path else ROOT / 'results/events.csv'
    path.parent.mkdir(parents=True, exist_ok=True)
    header = not path.exists() or path.stat().st_size == 0
    with path.open('a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if header:
            writer.writeheader()
        writer.writerow({key: event.get(key, '') for key in FIELDS})
