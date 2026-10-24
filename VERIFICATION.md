# Verification record — 24 October 2026

## Checkout and environment

- Target origin: `https://github.com/VARUN-GOWDAB/Trace_Tutor.git`.
- Actual checkout: `C:\Users\chand\OneDrive\Desktop\Trace_Tutor\Trace_Tutor`.
- Initially clean `main`, containing README only. No applicable AGENTS.md found.
- Work branch: `feature/simple-tracetutor`. No push, merge or deployment performed.
- Environment: `C:\Users\chand\OneDrive\Desktop\Trace_Tutor\Trace_Tutor\.venv`.
- Python 3.12.14, using bundled Python as the environment creator because the
  WindowsApps `py` launcher could not be accessed. Direct installed dependencies:
  Streamlit 1.66.1, python-dotenv 1.2.4, OpenAI 2.54.0,
  e2b-code-interpreter 2.4.1 and pytest 9.1.1.

## Executed commands

Commands below ran from the target checkout unless otherwise stated:

```powershell
git remote -v
git branch --show-current
git status --short
git switch -c feature/simple-tracetutor
& 'C:\Users\chand\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' --version
& 'C:\Users\chand\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv .venv
.\.venv\Scripts\python.exe -m ensurepip --upgrade --default-pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pip check
git diff --check
.\.venv\Scripts\python.exe -m streamlit run app.py --server.headless true --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
Invoke-WebRequest -Uri http://127.0.0.1:8501/_stcore/health -TimeoutSec 10
```

Initial environment creation failed in ensurepip because the execution sandbox
denied temporary-wheel access. Rerunning the exact ensurepip command with normal
permissions succeeded. Initial pip installation failed with package-index DNS
errors; the same command with normal network access succeeded. No dependencies
were installed globally. Initial pytest temporary-file errors similarly required
normal temporary-directory access. The first UI test exposed a relative app-path
error; it was fixed to use an absolute project path. Its cold table import also
exceeded the initial three-second test timeout; the test now allows 30 seconds.
The sandboxed Streamlit/loopback check was inaccessible; the local launch and health
check succeeded with normal permissions. These are environment/setup outcomes,
not model or student-program findings.

## Final outcomes

- **20 passed, 5 skipped in 1.77 seconds.** The five skipped tests explicitly require
  live opt-in and E2B credentials. Each would execute both a starter and reference.
- Streamlit AppTest exercised run, hint history, rerun without duplicate logging,
  editor invalidation, disabled stale hints, exercise switching, reset and a
  successful reference fixture. No app exception remained.
- Unit tests cover exact demo matching, arbitrary-code rejection, claim value/type
  mismatches, unknown tests, stale IDs, empty claims, malformed JSON, bounded retry,
  repeated contradictions, fallback, outages, CSV, incomplete service responses,
  and mocked sandbox cleanup. Harness syntax was compiled without executing student
  code on the host.
- `pip check`: no broken requirements. `git diff --check`: no whitespace errors
  (Git may print its standard LF-to-CRLF notice on Windows).
- Local server started at `http://127.0.0.1:8501`; health endpoint returned
  **HTTP 200, `ok`**. A browser-open request was queued in Codex.
- Automated interaction checks are not a visual browser inspection. Human review
  of page appearance and a full manual rehearsal remain advisable.

## What was not verified

Neither `OPENAI_API_KEY` nor `E2B_API_KEY` was present (checked for presence only;
no secrets printed). No live model or sandbox request was made. SDK method
signatures were inspected locally and checked against official documentation;
this does not establish provider availability, billing or live behavior.

The ten fixture programs and their 20 test cases are authored offline material;
passing fixture checks does not mean the reference programs ran live. References
and expected values were manually reviewed. Live tests are provided for subsequent
verification. No paid pilot was invoked, no human ratings were fabricated and no
learning outcomes were measured. See README reliability limits and pilot procedure.

## Delivered files

Application: app.py, runner.py, hints.py, storage.py. Teaching data:
data/exercises.json and data/demo_fixtures.json. Verification: tests/test_core.py,
tests/test_ui.py. Optional explicit pilot: evaluate.py. Setup: requirements.txt,
.env.example, .gitignore. Handoff: README.md (including workflow diagram and team
schedule), VIVA.md and this record. Local credentials, environment and logs are
ignored and excluded from delivery.
