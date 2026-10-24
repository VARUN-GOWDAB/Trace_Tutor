"""Explicit opt-in only. At most 5 sandbox runs and 60 model requests."""
import argparse
import json
import os
from dotenv import load_dotenv
from storage import ROOT, load_exercises
from runner import run_tests, ExecutionUnavailable
from hints import get_hint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Authorize the bounded paid pilot')
    args = parser.parse_args()
    if not args.live:
        parser.error('Use --live to explicitly invoke the paid pilot (up to 60 model calls and 5 sandbox runs).')
    load_dotenv(ROOT / '.env')
    if not all(os.getenv(k) for k in ('OPENAI_API_KEY', 'E2B_API_KEY')):
        parser.error('Both provider keys are required. Fixtures never count as live findings.')
    directory = ROOT / 'results'
    directory.mkdir(exist_ok=True)
    # Exclusive create prevents accidentally mixing repeated pilot runs.
    with (directory / 'pilot.jsonl').open('x', encoding='utf-8') as f:
        for exercise in load_exercises():
            try:
                result = run_tests(exercise, exercise['starter'], 'live')
            except ExecutionUnavailable as exc:
                f.write(json.dumps({'exercise_id': exercise['id'], 'operational_failure': str(exc)}) + '\n')
                continue
            for checked in (False, True):
                for level in (1, 2, 3):
                    event = get_hint(exercise, exercise['starter'], result, level, 'live', checked=checked)
                    event['setting'] = 'grounded_checked' if checked else 'grounded'
                    f.write(json.dumps(event) + '\n')
                    f.flush()
    print('Exported results/pilot.jsonl. Human review is required; no ratings were generated.')


if __name__ == '__main__':
    main()
