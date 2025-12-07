# Company Matcher

A small Python package that matches noisy, user-entered company names against
an Elasticsearch-backed index. This repo contains a lightweight matching
pipeline with several complementary signals (Elasticsearch score dominance,
string similarity, and phonetic similarity) combined into a single
confidence score and an accept/reject decision.

This README is a developer-oriented quickstart and reference.

---

## Quick summary
- Language: Python 3.10+ (pyproject.toml declares ^3.10)
- Key libs: RapidFuzz (string similarity), Metaphone (phonetic), Faker (test/demo), requests (ES HTTP)
- Layout: source under `src/company_match`, tests under `tests/`

---

## Local setup (recommended)
Create a virtual environment, install pinned deps, and perform an editable
install so imports behave like an installed package.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Notes:
- `setup.cfg` in the repo provides minimal metadata so `pip install -e .` works.
- Alternatively you can use Poetry (the repo has `pyproject.toml` poetry metadata):
  - `poetry install` then `poetry shell`.

---

## Run the demo / CLI
After an editable install (or with `PYTHONPATH=src`) you can run the included
demo which generates names, "dirties" them and attempts to match each:

```bash
# if package is installed editable
python -m company_match.pipeline

# or without installing (temporary)
PYTHONPATH=src python -m company_match.pipeline
```

The demo prints lines like: `canonical_name => dirty_input => {match result dict}`.

---

## Running tests and coverage
Run unit tests with pytest (a `tests/conftest.py` is present to set `src/` on
sys.path so tests run without setting `PYTHONPATH` manually):

```bash
pytest -q
```

Generate a coverage HTML report:

```bash
pytest --cov=company_match --cov-report=term-missing --cov-report=html
# open report on macOS
open htmlcov/index.html
```

Current test status (local run): 6 tests passed, coverage ~74% (some areas remain
untested: demo `__main__`, certain matching branches, and some generator branches).

---

## Troubleshooting
- ModuleNotFoundError: No module named 'company_match'
  - This happens if `src/` is not on Python's import path. Fixes:
    - Use the editable install: `pip install -e .`
    - Or run with `PYTHONPATH=src` (temporary):
      ```bash
      PYTHONPATH=src pytest
      PYTHONPATH=src python -m company_match.pipeline
      ```
    - In PyCharm: Right-click `src` -> Mark Directory As -> Sources Root.
    - The repo includes `tests/conftest.py` which inserts `src/` at test time.

- Elasticsearch / ES_URL:
  - `src/company_match/pipeline/es_client.py` issues HTTP requests to `config.ES_URL`.
  - Unit tests should mock `search_es` or `requests.post` so CI does not need a running ES instance.

- Logging side effects:
  - `elk_log` appends JSONL to `logs/company_matching_elk.jsonl`. Tests should
    monkeypatch `elk_log` or use a temporary log path to avoid polluting the repo during tests.

- Python 3.14 DeprecationWarning:
  - `logging_utils.py` currently uses `datetime.utcnow().isoformat()` which
    emits a deprecation warning on Python 3.14+. Prefer timezone-aware UTC:
    `datetime.now(timezone.utc).isoformat()`.

---

## What is missing / fragile
- Packaging metadata: `pyproject.toml` contains Poetry metadata but no
  `build-system` block. I added a minimal `setup.cfg` so `pip install -e .`
  works; for long-term maintainability consider adding a `pyproject.build-system`
  or committing to Poetry tooling.
- ES dependency: there are no integration tests or Docker setup for a local ES
  index. Either provide a test fixture that spins up a test ES or ensure
  `search_es` is always mocked in unit tests.
- Logging: `elk_log` writes to disk by default. Consider making the path
  configurable or allowing the logger to be a no-op in tests.
- Tests: Add more unit tests for `matching.match()` decision branches. Currently
  tests are minimal / smoke-level for `matching` and `scoring`.

---

## Suggested next dev tasks (prioritized)
1. Add unit tests for `matching.match()` that mock `search_es` and assert
   the `reason` and `status` under different signal combinations.
2. Replace `datetime.utcnow()` with timezone-aware UTC to silence warnings.
3. Make `elk_log` configurable (env var or parameter) so tests can disable or
   redirect logging output.
4. Add a CI pipeline that installs deps, runs tests, and publishes coverage.

---

## CI example (GitHub Actions)
Create `.github/workflows/ci.yml` with a job that installs dependencies,
performs an editable install, runs tests and generates coverage. Example:

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ['3.11']
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python }}
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Install package
        run: pip install -e .
      - name: Run tests
        run: pytest --cov=company_match --cov-report=term-missing --cov-report=xml --cov-report=html
      - name: Upload coverage HTML
        uses: actions/upload-artifact@v4
        with:
          name: coverage-html
          path: htmlcov
```

Notes for CI:
- Ensure unit tests do not call a real ES instance (mock `search_es`).
- Optionally upload `htmlcov` as an artifact or publish coverage to a service.

---

## Contributing / Development tips
- Use `tests/conftest.py` to make pytest discover the package source.
- Use monkeypatching to control randomness in `generator.dirty_name` tests.
- Keep `es_client.search_es` mocked for unit tests to avoid network calls.
- Run the demo locally to manually inspect matching behavior.

---

If you want, I can now:
- add the GitHub Actions workflow file, and/or
- create unit tests for `matching.match()` that mock `search_es` and improve coverage, and/or
- fix the `datetime.utcnow()` deprecation by updating `logging_utils.py`.

Tell me which of those you'd like me to do next and I'll implement and test it.
