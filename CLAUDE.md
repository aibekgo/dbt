# CLAUDE.md — Guide for building a new course on this template

This repo is a template for interactive CLI-based data engineering courses.
The engine (CLI, state, quiz) is generic. You provide content and a verifier.

---

## Step 0 — Brainstorm curriculum and verify mechanisms before writing any code

Before touching any files, have a design conversation with Claude. This prevents
writing exercises that are hard to verify, or building a verifier before knowing
what it needs to check.

### Curriculum brainstorm

Ask Claude to help answer these questions:

**Scope**
- What is the tool? What problem does it solve?
- What does a learner need to be able to DO after finishing this course?
  (Concrete outcomes, not "understand X")
- What is explicitly out of scope?

**Stages**
- What are the natural learning stages? (e.g. install → first DAG → scheduling → sensors → best practices)
- What must be learned before what? Draw the dependency order.
- How many exercises per stage? (aim for 3-6 — enough to build muscle memory, not so many it drags)

**Exercise design**
- For each stage: what is the ONE thing the learner must do to prove they understand it?
- Is the exercise self-contained enough to verify programmatically?
- What is the simplest possible scaffold that forces the learner to implement the key concept?

Produce a draft `curriculum.yaml` outline (stages + item ids + titles only, no files yet)
and get agreement on it before writing any content.

---

### Verify mechanism brainstorm

For each exercise, decide which verifier pattern to use (see "Verifier patterns" section below).
Ask Claude to help answer:

**Pattern selection**
- Can correctness be checked with a unit test alone, or does it require a running service?
- If a service is needed: what API endpoint or query proves the exercise is done?
- Is there a risk of false positives? (e.g. a leftover artifact from a previous attempt
  making a fresh run look correct)

**Failure messages**
- When the exercise fails, what message tells the learner exactly what went wrong?
- Can the verifier surface logs or output from the service to help debug?

**Edge cases**
- What if the service is not running when the learner presses `v`?
- What if a previous exercise left state that interferes with this one?

Produce a table like this and agree on it before implementing anything:

| exercise id | verifier pattern | what it checks | key API / assertion |
|-------------|-----------------|----------------|---------------------|
| first_dag   | remote service  | DAG exists in Airflow and has no import errors | `GET /api/v1/dags/first_dag` → `is_paused: false` |
| run_dag     | remote service  | DAG run completed successfully | `GET /api/v1/dag_runs` → `state: success` |
| write_csv   | artifact check  | output file exists and is non-empty | `Path("output/result.csv").stat().st_size > 0` |

Only start Step 1 (copying the template) once both the curriculum outline and the
verify mechanism table are agreed on.

---

## Quick start — building a new course from scratch

Follow this order exactly. Don't skip ahead — get each step working before moving on.

### Step 1 — Copy the template
```bash
cp -r learn-de-template learn-<tool>
cd learn-<tool>
git init && git add . && git commit -m "init from learn-de-template"
pip install -e .
```

### Step 2 — Rename the CLI

In `pyproject.toml`:
```toml
name = "airflow-learn"
...
airflow-learn = "cli.main:app"
```

In `cli/main.py`:
```python
COURSE_NAME = os.environ.get("COURSE_NAME", "airflow-learn")
COURSE_EMOJI = os.environ.get("COURSE_EMOJI", "🌬️")
```

### Step 3 — Set up Docker

1. In `Dockerfile` — uncomment your tool's pip install line
2. In `docker-compose.yml` — fill in the `tool-service` block for your tool
3. Start everything:
```bash
docker compose up -d
docker compose ps   # confirm learn-local and tool-service are running
```

### Step 4 — Implement your verifier

```bash
cp verifier/example_api_verifier.py verifier/<tool>_verifier.py
```

Edit the new file to call your tool's API. Then register it in `cli/main.py`:
```python
from verifier.<tool>_verifier import MyVerifier

VERIFIER_REGISTRY = {
    "local": LocalVerifier,
    "<tool>": MyVerifier,
}
```

Test the verifier in isolation before wiring it to an exercise:
```python
# quick smoke test
from verifier.<tool>_verifier import MyVerifier
result = MyVerifier().verify("exercises/hello_pipeline.py")
print(result)
```

### Step 5 — Delete the example content

Remove the placeholder files that shipped with the template:
```bash
rm exercises/hello_pipeline.py
rm originals/hello_pipeline.py
rm tests/test_hello_pipeline.py
rm hints/hello_pipeline.md
rm lessons/hello_pipeline.html
rm quiz/hello_pipeline.yaml
```

Clear `curriculum.yaml` down to the empty skeleton (keep the comments as reference).

### Step 6 — Write and verify your first exercise end-to-end

Create one complete item: lesson → exercise → test → hint → quiz.
Add it to `curriculum.yaml`. Generate the HTML lesson, then walk through the full flow:
```bash
python3 build_lessons.py   # converts lessons/*.md → .html (commit the .html, not the .md)
<tool>-learn               # start interactive session
# press l → lesson opens in browser
# press v → verifier runs, should fail on the scaffold
# implement the solution in exercises/<name>.py
# press v again → should pass
# press n → quiz triggers, then moves to next item
```

Only add more exercises once this first item works completely end-to-end.

### Step 7 — Scale up content

Repeat Step 6 for each new exercise. Group exercises into stages in `curriculum.yaml`.
Add a `conftest.py` if your tests need shared fixtures (see the conftest section below).
Extend `reset()` in `cli/main.py` to clean up any artifacts your exercises generate.

---

**Critical order: Docker working → verifier returning real results → first exercise
passing end-to-end → then scale up. Never write 10 exercises before verifying the first.**

---

---

## How the engine works (read this first)

```
curriculum.yaml          ← single source of truth: all stages, lessons, exercises
cli/main.py              ← interactive session loop (l/v/h/n/x/q commands)
cli/curriculum.py        ← loads curriculum.yaml into CurriculumItem objects
cli/state.py             ← persists progress to progress.txt
verifier/base.py         ← BaseVerifier interface (syntax_ok + list[TestResult])
verifier/local.py        ← default: syntax check + pytest via docker exec
quiz/loader.py           ← loads quiz/{item_id}.yaml
quiz/runner.py           ← interactive quiz prompts, triggered at end of each stage
```

The learner runs a single command (e.g. `airflow-learn`) and gets an interactive
session. Keys: `l` open lesson, `v` verify, `h` hint, `n` next, `x` reset file, `q` quit.
Exercises are gated — the learner cannot advance past an exercise until it passes.

---

## Checklist to create a new course from this template

### 1. Rename the CLI

In [pyproject.toml](pyproject.toml):
- Change `name` to your course name (e.g. `airflow-learn`)
- Change the `[project.scripts]` entry point (e.g. `airflow-learn = "cli.main:app"`)
- Add course-specific Python dependencies

In [cli/main.py](cli/main.py):
- Set `COURSE_NAME` default (or set env var `COURSE_NAME=airflow-learn`)
- Set `COURSE_EMOJI` default (or set env var `COURSE_EMOJI=🌬️`)

### 2. Implement your verifier (if not using plain pytest)

If your course needs to verify against a running service (Airflow, dbt, a database):

1. Copy [verifier/example_api_verifier.py](verifier/example_api_verifier.py) to e.g. `verifier/airflow_verifier.py`
2. Implement the `verify(exercise_path) -> VerifyResult` method
3. Register it in [cli/main.py](cli/main.py):

```python
from verifier.airflow_verifier import AirflowVerifier

VERIFIER_REGISTRY = {
    "local":   LocalVerifier,     # keep this — used by the example exercise
    "airflow": AirflowVerifier,   # matches `verifier: airflow` in curriculum.yaml
}
```

The `verifier:` field in `curriculum.yaml` must exactly match a key in `VERIFIER_REGISTRY`.
If a key is not found, the engine falls back to `LocalVerifier` — so a typo silently runs
pytest instead of your custom verifier. Double-check the key spelling.

**VerifyResult contract:**
- `syntax_ok: bool` — set False only for syntax/parse errors, not logic failures
- `tests: list[TestResult]` — one entry per check, each with `name`, `passed`, `message`
- `extra: str | None` — optional extra text shown after test results (e.g. logs)
- The exercise passes only when `syntax_ok=True` AND all `TestResult.passed=True`

---

## Verifier architecture — read this before implementing

**The single most important rule: one verifier class per type, not one per exercise.**

A common mistake is creating a separate verifier for each exercise
(`FirstDagVerifier`, `RunDagVerifier`, `WriteCsvVerifier`...). This is wrong.
You should have one `AirflowVerifier` (or one per pattern type) that handles
all exercises of that type.

**How it works in practice:**

The verifier receives `exercise_path` — the path to the exercise file the
learner edited. It uses that path to look up what checks to run by reading
`curriculum.yaml`. The checks are defined *in the curriculum*, not hardcoded
in the verifier class.

```
curriculum.yaml                    verifier class
───────────────                    ──────────────
exercise: run_dag                  class AirflowVerifier:
  verifier: airflow       ──────►    def verify(self, exercise_path):
  airflow_checks:                       checks = _find_checks(exercise_path)
    app_name: my_dag                    # reads curriculum.yaml to get ^
    rules:                              # then runs each rule generically
      - type: dag_success
      - type: task_count
        value: 3
```

This means:
- Adding a new exercise = add a new block in `curriculum.yaml` with its checks
- The verifier class never changes when you add exercises
- All domain-specific check logic lives in small `_check_*` helper functions

**The pattern used in `learn_spark` (concrete reference):**

`ClusterVerifier` is one class that handles every cluster-mode exercise.
It reads `cluster_checks` from `curriculum.yaml`:
```yaml
- id: tune_partitions
  type: exercise
  verifier: cluster
  cluster_checks:
    app_name: tune_partitions
    rules:
      - type: spark_conf
        key: spark.sql.shuffle.partitions
        value: "10"
      - type: agg_plan
        value: HashAggregate
```
Then dispatches to `_check_spark_config()`, `_check_agg_plan()`, etc. based on
rule `type`. Each `_check_*` function is reusable across all exercises.

`FileVerifier` does the same with `file_checks`:
```yaml
  verifier: file
  file_checks:
    - path: tpch_data/lineitem
      min_bytes: 100000000
```

**Template for a new verifier:**

```python
class MyToolVerifier(BaseVerifier):
    def verify(self, exercise_path: str) -> VerifyResult:
        # 1. Check service is reachable — fail fast with a clear message
        # 2. Look up checks from curriculum.yaml for this exercise_path
        # 3. Run each check as a separate TestResult
        # 4. Return VerifyResult with all results

        checks = _find_checks(exercise_path)   # reads curriculum.yaml
        if checks is None:
            return VerifyResult(exercise_path=exercise_path, syntax_ok=True,
                syntax_error="No checks defined for this exercise in curriculum.yaml")

        tests = []
        for rule in checks.get("rules", []):
            if rule["type"] == "dag_success":
                tests.extend(_check_dag_success(...))
            elif rule["type"] == "task_count":
                tests.extend(_check_task_count(..., expected=rule["value"]))
            # add more rule types as needed

        return VerifyResult(exercise_path=exercise_path, syntax_ok=True, tests=tests)
```

Add the corresponding check fields to each exercise in `curriculum.yaml`:
```yaml
- id: my_exercise
  type: exercise
  verifier: mytool
  mytool_checks:
    rules:
      - type: dag_success
      - type: task_count
        value: 3
```

---

## Verifier patterns

There are three archetypes. Pick the one that fits each exercise. A course can
use multiple verifier types — just register each in `VERIFIER_REGISTRY`.

### Pattern 1 — Unit test (local pytest)

**When to use:** the exercise is a pure Python function or script that can be
tested in isolation, with no running service needed.

**How it works:** `LocalVerifier` does a syntax check then runs pytest inside
the `learn-local` Docker container via `docker exec`. The test file imports
directly from `exercises/<name>.py`.

**learn_spark reference:** `verifier/local.py` — used for Stage 0 exercises
(DataFrame API, schema manipulation) that run against a local SparkSession
created in `conftest.py`.

**Use this for:** dbt macro logic, Python transform functions, Airflow operator
unit tests (mocked), any pure-logic exercise.

---

### Pattern 2 — Remote service validation

**When to use:** the exercise requires the learner to interact with a running
service (trigger a DAG, run a dbt model, submit a job), and correctness can
only be confirmed by querying that service's API or database.

**How it works:** implement a custom verifier that calls the service's REST API
or SDK, checks the expected resource/result exists, and returns `TestResult`
entries for each check. The service must be running (via docker-compose) when
the learner presses `v`.

**learn_spark reference:** `verifier/cluster.py` — queries the Spark History
Server REST API (`localhost:18080/api/v1/applications`) to confirm a job ran
successfully and inspect its physical plan (join types, shuffle counts, caching).

**Use this for:** confirming an Airflow DAG ran and succeeded, checking a dbt
model produced the right row count in Postgres, validating a Kafka topic has
messages, asserting a pipeline wrote output to an S3-compatible store.

**Template starting point:** `verifier/example_api_verifier.py`.

---

### Pattern 3 — Artifact / file check

**When to use:** the exercise asks the learner to generate a file or dataset,
and verification is just confirming the file exists and meets a size/format
threshold (not full content validation).

**How it works:** implement a verifier that checks `Path(path).exists()` and
`Path(path).stat().st_size >= min_bytes`. No Docker exec or service call needed
— runs directly on the host.

**learn_spark reference:** `verifier/file.py` — used for the TPC-H data
generation exercise, which checks that the expected `.parquet` files are present
and non-empty before allowing the learner to advance.

**Use this for:** confirming a dbt seed file was generated, checking that an
export CSV was written, asserting that a pipeline output directory is non-empty.

### 3. Set up Docker

The repo ships with a working [Dockerfile](Dockerfile) and [docker-compose.yml](docker-compose.yml).
You need to make two changes:

**Dockerfile** — add your course's Python dependencies:
```dockerfile
RUN pip install --no-cache-dir pytest pyyaml rich typer \
    && pip install apache-airflow   # ← your tool here
```

**docker-compose.yml** — uncomment and fill in the `tool-service` block:
```yaml
services:
  learn-local:          # ← do not rename; LocalVerifier execs into this
    build: .
    container_name: learn-local
    volumes:
      - .:/workspace    # entire repo mounted so tests can import exercises/
    environment:
      COURSE_ROOT: /workspace
      PYTHONPATH: /workspace
    depends_on:
      - tool-service    # ← add if exercises call the tool's API

  tool-service:         # ← replace with your tool (Airflow, Postgres, etc.)
    image: apache/airflow:2.9.2
    container_name: airflow
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
    command: standalone
```

Key rules:
- The `learn-local` container **must** mount `.:/workspace` — this is how pytest
  inside the container sees the learner's edited exercise files on the host.
- Always set `COURSE_ROOT=/workspace` and `PYTHONPATH=/workspace` in `learn-local`.
- If your verifier calls the tool's API (e.g. Airflow REST API at `localhost:8080`),
  reach it via the service name (`http://tool-service:8080`) from inside the container,
  or via `localhost:8080` from the host CLI. Use the host-side URL in your verifier
  since the verifier runs on the host, not inside a container.
- To start everything: `docker compose up -d`
- To restart after changing exercise files: no restart needed — the volume mount
  means the container always sees the latest file state.

### 4. Add your curriculum content

For every topic, you need these files (replace `<name>` with a snake_case id):

| File | Purpose |
|------|---------|
| `lessons/<name>.html` | Lesson content opened in browser when learner presses `l` |
| `exercises/<name>.py` | The file the learner edits |
| `originals/<name>.py` | Scaffold copy — restored when learner presses `x` or runs `reset` |
| `tests/test_<name>.py` | Pytest file run by LocalVerifier (skip if using API verifier) |
| `hints/<name>.md` | Progressive hints shown when learner presses `h` |
| `quiz/<name>.yaml` | Quiz questions shown at end of stage (optional) |

Then add an entry to [curriculum.yaml](curriculum.yaml). See the existing example.

---

## File conventions

### exercises/<name>.py and originals/<name>.py

- Start with a comment block explaining what the learner must do
- Use `raise NotImplementedError` as the placeholder — never leave functions empty
- Do not import modules the learner hasn't learned yet
- Keep scaffold functions named exactly as the tests expect

```python
# Exercise: <Title>
#
# <Clear description of what to implement>
# Do not rename the functions.

def my_function(arg):
    # TODO: implement this
    raise NotImplementedError
```

### lessons/<name>.html

**The `.html` file is the committed artifact. The `.md` source is gitignored.**

Authoring workflow:
1. Write the lesson in `lessons/<name>.md` (gitignored — local scratchpad only)
2. Run `python3 build_lessons.py` to generate the `.html`
3. Commit the `.html` — this is what the CLI opens when the learner presses `l`

Never edit `.html` files directly. Always edit the `.md` and regenerate.
`build_lessons.py` is also gitignored — it's a dev tool, not part of the committed course.

Lesson structure:
1. Concept explanation (what + why)
2. Minimal code example (fenced code block)
3. One or two common pitfalls

Keep it under ~300 lines. Learners read this inside a browser tab.

### hints/<name>.md

Progressive hints — each more specific than the last. Format:

```markdown
## Hint 1

<High-level nudge — approach, not code>

## Hint 2

<More specific — what to look at>

## Hint 3

<Near-complete code snippet if needed>
```

Aim for 2-4 hints. The first hint should never give away the answer.

### tests/test_<name>.py

**When to use unit tests vs a service verifier**

Use `verifier: local` (pytest) when the exercise is a Python function or script
that can be tested without a running service. Use a service verifier when the
learner must interact with a real tool (trigger a DAG, run a model, etc.).

If in doubt: can you import the exercise file and call its functions directly?
If yes → unit test. If the exercise's side effects only appear in a running
service → service verifier.

**How tests work in this repo (from `learn_spark`)**

Tests import the exercise module at the top level — not inside test functions.
Module-level code in the exercise runs on import. This means the learner's
assignments (`df = ...`, `result = ...`) execute when pytest collects the test,
and each test just asserts on the resulting variables.

```python
# tests/test_my_exercise.py
import exercises.my_exercise as ex   # ← runs the exercise's module-level code

def test_result_is_not_none():
    print(f"OUTPUT: result={ex.result!r}", flush=True)   # shown in CLI on failure
    assert ex.result is not None, "`result` is still None — assign your answer to it."

def test_result_correct():
    print(f"OUTPUT: result={ex.result!r}  expected=42", flush=True)
    assert ex.result == 42, f"Expected 42, got {ex.result!r}"
```

And the matching exercise scaffold:
```python
# exercises/my_exercise.py
# TASK: compute the answer and assign it to `result`

result = None   # TODO: replace None with your answer
```

**Key rules for writing tests:**

- Always `import exercises.<name> as ex` at module level — never inside a test function
- First test should always check `is not None` with a clear message pointing to
  the variable name — this is what the learner sees when they haven't started yet
- Use `print(f"OUTPUT: ...", flush=True)` to surface values in the CLI output
  after verification — helps the learner debug without reading raw pytest output
- Name tests in progression: existence → type → value → edge case
- Keep tests independent — each must pass or fail on its own
- Assert messages should tell the learner exactly what to do, not just what went wrong:
  `"Expected 42, got 7"` is worse than `"Expected 42, got 7 — did you filter before counting?"`

**When your exercise needs a shared service fixture (e.g. a DB connection):**

Add a `conftest.py` at the repo root and use a session-scoped fixture:
```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def airflow_client():
    from airflow_client import Client
    return Client(host="localhost", port=8080)
```

Tests then declare it as a parameter — pytest injects it automatically:
```python
def test_dag_exists(airflow_client):
    dags = airflow_client.get_dags()
    assert any(d.dag_id == "my_dag" for d in dags)
```

Note: if the exercise uses module-level imports that require the service
(e.g. `from airflow import DAG`), the service must be running before pytest
collects the test file. Make sure the learner knows to start Docker first.

### quiz/<name>.yaml

```yaml
topic: <snake_case_topic_name>
questions:
  - id: <topic>_01
    difficulty: easy | medium | hard
    type: multiple_choice
    prompt: "Question text?"
    options:
      a: "Option A"
      b: "Option B"
      c: "Option C"
      d: "Option D"
    answer: b              # must match an options key exactly
    explanation: |
      Why the answer is correct. 2-4 sentences. Reference the lesson concept.
    related_item: <curriculum item id>   # used to show "review this lesson" on wrong answers
```

Rules:
- `related_item` must match an `id` in `curriculum.yaml`
- `answer` must be a single key from `options` (a/b/c/d)
- Aim for 2-5 questions per topic
- Questions test understanding, not memorization of syntax

---

## curriculum.yaml schema

```yaml
stages:
  - id: stage_0_foundations      # snake_case, unique
    title: "Stage 0 — Title"     # shown in CLI header
    items:
      - id: my_lesson            # snake_case, unique across entire curriculum
        type: lesson
        file: lessons/my_lesson.html
        quiz: quiz/my_lesson.yaml          # optional

      - id: my_exercise
        type: exercise
        lesson:   lessons/my_lesson.html   # opened on 'l'
        exercise: exercises/my_exercise.py # file learner edits
        original: originals/my_exercise.py # scaffold restored on 'x'
        test:     tests/test_my_exercise.py
        hints:    hints/my_exercise.md
        verifier: local                    # key in VERIFIER_REGISTRY
        quiz:     quiz/my_exercise.yaml    # optional
```

Required fields for exercise: `id`, `type`, `exercise`, `original`, `test`, `verifier`.
All paths are relative to the repo root.

---

## Environment variables reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `COURSE_ROOT` | repo root | Absolute path to repo — set to `/workspace` in Docker |
| `COURSE_NAME` | `de-learn` | CLI name shown in panels and help text |
| `COURSE_EMOJI` | `📚` | Emoji used in CLI panels |
| `LEARN_CONTAINER` | `learn-local` | Docker container name for `docker exec` in LocalVerifier |
| `STATE_DIR` | auto | Override progress.txt directory |

---

## Extending the reset command

The template's `reset` command in [cli/main.py](cli/main.py) only resets progress and
restores exercise files. Real courses generate artifacts that also need cleaning.

Extend `reset()` for your course by adding cleanup steps after the base reset:

```python
@app.command()
def reset() -> None:
    # base reset (keep these two)
    save_state({"current": CURRICULUM[0].id, "done": [], "verified": []})
    for item in CURRICULUM:
        if item.type == "exercise" and item.original:
            reset_exercise(item)

    # course-specific cleanup — examples:
    # shutil.rmtree(ROOT / "dags/__pycache__", ignore_errors=True)
    # shutil.rmtree(ROOT / "target", ignore_errors=True)          # dbt artifacts
    # subprocess.run(["docker", "compose", "down", "-v"], cwd=ROOT, check=True)
    # subprocess.run(["docker", "compose", "up", "-d"],  cwd=ROOT, check=True)

    console.print("[green]✅ Reset complete.[/]")
```

Always restart the tool's Docker service in `reset` if exercise state leaks into the
service (e.g. Airflow DAG run history, database tables). Otherwise old state from a
previous attempt will interfere with fresh runs.

---

## conftest.py — shared pytest fixtures

If your test files need a shared fixture (e.g. a database connection, a tool client),
add a `conftest.py` at the repo root. pytest auto-loads it before any test file.

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def my_client():
    # set up once per test session
    client = MyToolClient(host="localhost", port=8080)
    yield client
    client.close()
```

Tests in `tests/` can then use `my_client` as a parameter without importing it.
The template does not ship a `conftest.py` because the required fixture is course-specific.

---

## README.md

Every course repo needs a `README.md` at the root. It is the first thing a learner
reads — it must get them from zero to running the CLI in under 5 minutes.

**Required sections (in this order):**

1. **One-liner** — what the course is and what style it follows
   e.g. `An interactive, rustlings-style CLI for learning Apache Airflow.`

2. **Prerequisites** — exactly what needs to be installed before anything works
   (Docker, uv or pip, Python version, recommended editor)

3. **Setup** — numbered steps, copy-pasteable commands:
   - Clone + open in editor
   - Create local venv using `uv` for editor autocomplete:
     ```bash
     uv venv
     source .venv/bin/activate
     uv pip install -e .
     ```
     Explain that this is for editor import resolution only — all execution
     happens inside Docker. Do not suggest `pip` or `conda` as alternatives.
   - Point editor to the local interpreter (`Cmd+Shift+P` → "Python: Select Interpreter" → `.venv`)
   - `docker compose up -d`
   - List the containers and their roles in a table

4. **Running** — the single command to launch the CLI

5. **Interactive session** — the key-commands table (copy from the template below)

6. **CLI commands** — non-interactive commands (`list`, `reset`, `quiz`)

7. **How exercises work** — 3-4 sentences explaining lessons vs exercises,
   the edit-verify loop, and where progress is saved

**Key-commands table (generic — reuse this in every course):**

```markdown
## Interactive session

**Lessons:**

| Key | Action |
|-----|--------|
| `l` | Open the lesson in browser |
| `n` | Advance to next item |
| `q` | Quit |

**Exercises:**

| Key | Action |
|-----|--------|
| `l` | Open the associated lesson in browser |
| `v` | Verify your solution (output shown inline) |
| `h` | Show hints |
| `n` | Advance (must pass verification first) |
| `x` | Reset exercise file to original scaffold |
| `q` | Quit |
```

**Reference:** see `../learn_spark/README.md` for a complete worked example.

---

## What NOT to change

- `cli/curriculum.py` — only change if you need new curriculum.yaml fields
- `cli/state.py` — state format is stable; only change if you add new state keys
- `verifier/base.py` — the interface contract; never modify
- `quiz/loader.py` and `quiz/runner.py` — fully generic, leave as-is

---

## Example: adding a new stage

1. Create the content files:
   - `lessons/my_topic.html`
   - `exercises/my_topic.py` and `originals/my_topic.py` (identical scaffold)
   - `tests/test_my_topic.py`
   - `hints/my_topic.md`
   - `quiz/my_topic.yaml` (optional)

2. Add the stage to `curriculum.yaml`:
```yaml
  - id: stage_1_my_topic
    title: "Stage 1 — My Topic"
    items:
      - id: my_topic_intro
        type: lesson
        file: lessons/my_topic.html

      - id: my_topic
        type: exercise
        lesson:   lessons/my_topic.html
        exercise: exercises/my_topic.py
        original: originals/my_topic.py
        test:     tests/test_my_topic.py
        hints:    hints/my_topic.md
        verifier: local
        quiz:     quiz/my_topic.yaml
```

3. Run `de-learn list` to confirm the item appears and `de-learn` to test the flow.

---

## Reference: learn_spark

This template was extracted from [learn_spark](../learn_spark).
When in doubt about how something should work, look at how it is done there.
The Spark-specific verifiers are in `verifier/cluster.py` (queries Spark History Server)
and show a good example of a real API-based verifier.
