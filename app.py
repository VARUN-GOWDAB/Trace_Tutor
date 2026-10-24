"""One page classroom prototype. Services are called only from button handlers."""
import os
import streamlit as st
from dotenv import load_dotenv
from storage import ROOT, load_exercises, append_log
from runner import run_tests, is_current, ExecutionUnavailable
from hints import get_hint

load_dotenv(ROOT / '.env')
st.set_page_config(page_title='TraceTutor', page_icon='📘')
st.title('TraceTutor')
st.write('Practice debugging Python with tests and three gradual hints. An SDG 4 educational prototype.')
exercises = load_exercises()
mode = st.selectbox('Execution mode', ['demo', 'live'], index=1 if os.getenv('TRACETUTOR_MODE') == 'live' else 0)
st.info('DEMO: prerecorded authored outputs and reviewed hints. Edited code needs live execution.' if mode == 'demo' else 'LIVE: Run Tests uses E2B; hints use OpenAI and may incur charges.')
selected = st.selectbox('Exercise', range(len(exercises)), format_func=lambda i: exercises[i]['title'])
exercise = exercises[selected]


def reset():
    st.session_state.editor = exercise['starter']
    st.session_state.result = None
    st.session_state.history = []
    st.session_state.stale = False


def invalidate():
    st.session_state.history = []
    st.session_state.stale = True


if st.session_state.get('context') != (selected, mode):
    st.session_state.context = (selected, mode)
    reset()
st.subheader(exercise['title'])
st.write(exercise['description'])
st.text_area('Your single-function submission', key='editor', height=250, on_change=invalidate)
code = st.session_state.editor
st.button('Reset Exercise', on_click=reset)
if st.button('Run Tests', type='primary'):
    st.session_state.history = []
    st.session_state.result = None
    try:
        with st.spinner('Running tests…'):
            st.session_state.result = run_tests(exercise, code, mode)
        st.session_state.stale = False
    except ExecutionUnavailable as exc:
        st.error(str(exc))
result = st.session_state.result
fresh = not st.session_state.stale and is_current(result, exercise, code, mode)
if result:
    if not fresh:
        st.warning('Results are stale. Run tests again before requesting hints.')
    st.caption(f"{result['mode'].upper()} · submission {result['submission_id']}")
    st.table([{'Input (args)': str(r['args']), 'Expected': repr(r['expected']),
               'Actual': repr(r['actual']) if r['status'] in ('pass', 'wrong_output') else 'No returned value',
               'Status': r['status'], 'Exception': r.get('error', '')} for r in result['rows']])
passed = bool(fresh and result['rows'] and all(r['status'] == 'pass' for r in result['rows']))
if passed:
    st.success('All tests passed!' + (' (Demo fixture)' if mode == 'demo' else ''))
    st.write(exercise['explanation'])
    with st.expander('Reviewed reference solution'):
        st.code(exercise['reference'], language='python')
history = st.session_state.history
if st.button('Get Hint' if not history else 'Next Hint', disabled=not fresh or passed or len(history) >= 3):
    with st.spinner('Preparing hint…'):
        event = get_hint(exercise, code, result, len(history)+1, mode)
    history.append(event)
    try:
        append_log(event)
    except OSError:
        st.warning('Hint shown, but CSV logging failed. Check results folder permissions.')
for i, event in enumerate(history, 1):
    st.markdown(f'**Hint {i}**')
    st.write(event['hint'])
    st.caption(f"{event['validation']} · {event['claim_count']} declared claims · {event['elapsed_ms']} ms")
    if event['failure_reason'] and event['fallback']:
        st.warning(f"{event['failure_reason']}. Showing a reviewed fallback hint.")
    elif event['retry']:
        st.caption('An initial response was rejected; the retry is displayed.')
st.caption('Matching declared claims does not verify the prose. No learning improvement has been established.')
