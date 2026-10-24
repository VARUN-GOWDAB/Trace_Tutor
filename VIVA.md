# Viva guide

**Purpose:** Beginner Python debugging using tests and three gradual hints, aligned
with SDG 4. We use an existing LLM; we do not train one or claim research novelty.

**Architecture:** app.py manages widgets/state; storage.py loads JSON and appends
CSV; runner.py calls E2B or matches demo fixtures; hints.py validates model JSON and
declared execution claims. evaluate.py is a separately invoked pilot exporter.
Walk through the README Mermaid diagram.

**Environment:** .venv isolates Python packages. .env configures credentials and
model/mode. Neither belongs in Git; each teammate creates their own environment.

**Execution:** The exec text in runner.py belongs to a managed sandbox harness,
never host execution. A timeout alone would not isolate the host. Demo uses exact
hashes and rejects unknown edits. Expected values and credentials stay on the host.

**Evidence:** Positional args invoke functions consistently. Each run has a UUID
and SHA-256 code hash. Type-aware comparison distinguishes booleans and integers.
An editor change makes results stale; exercise switching resets the starter.
Outputs are evidence, not variable traces.

**Hints:** Level one nudges a concept, level two relates a failure, level three
explains the language behavior. The model receives no reference solution. We
check JSON/schema, allowed actual/expected fields, known tests, submission identity
and value/type agreement. One retry, then a reviewed fallback. Service failures
are not invented student results.

**Validator limits:** It cannot verify all prose or undeclared claims. Empty claims
are unchecked. Human reviewers assess correctness, solution disclosure and usefulness.

**Logging:** CSV records IDs, hash, hint and validation/latency metadata, not keys
or raw source. It suits one classroom process, not concurrent deployment.

**Evaluation:** Thirty initial hints across grounded and grounded+checked settings,
with bounded retries. Review initial and displayed hints separately. Injected wrong
claims test software; they are not observed model errors. No ratings are fabricated.
The curated pilot cannot prove learning improvement or generalize broadly.

**Rehearsal:** Run the sum starter in demo, show 30 versus 60, request hints, edit
and show stale results, explain why unknown code requires live service, reset and
switch exercise. Paste a local authored reference for a passing fixture and clearly
explain that this is offline demonstration data. Discuss missing live verification.
