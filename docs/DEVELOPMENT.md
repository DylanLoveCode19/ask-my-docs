# Development

M0 provides the installable package, validated configuration, an empty FastAPI
application, offline smoke tests, and PR lint/test automation. Modules for later
milestones contain only placeholders; ingestion, retrieval, generation, and
evaluation are not implemented yet.

## Setup and checks

Prerequisites: Python 3.12, uv, and GNU Make on PATH. Run from the repository root:

```sh
make setup
make lint
make test
```

`make setup` uses `uv sync --locked`; commit `uv.lock` together with dependency
changes. These checks need no `.env`, API keys, downloaded models, Docker, or
external services. Initial dependency installation requires package-index access.
Tests isolate configuration in a temporary directory and never call an LLM.

On Windows, run the same commands with GNU Make installed. If Make is unavailable,
the equivalent PowerShell commands are:

```powershell
uv sync --locked
uv run ruff check .
uv run mypy src
uv run pytest -q
```

`make run` starts the scaffold on port 8000 with Swagger at `/docs`. `/ask`,
`/ingest`, and `/health` are not implemented in M0. `make up` requires Docker
Compose and starts Qdrant with a persistent named volume. `make ingest`,
`make eval-fast`, and `make eval-full` are reserved for later milestones.

## Configuration

`askdocs.config.Settings` validates settings when instantiated. Priority is
explicit constructor arguments, environment variables, `.env`, then
`config/app.yaml`. Nested environment overrides use `__`, for example
`RETRIEVAL__TOP_K`. Run from the repository root so relative config paths resolve.
Copy `.env.example` to `.env` when configuring providers; M0 needs no credentials.

Local model names, token budgets, retrieval counts, and default token prices live
in `config/app.yaml`. LLM and judge provider URLs, credentials, and model names
are configured through environment variables or `.env`. Price environment
variables override YAML defaults; set actual provider prices before evaluating
costs. Secret fields are redacted in settings representations.

`config/thresholds.yaml` is human-owned and reserved for evaluation milestones;
M0 does not alter or load it. The golden dataset is also unchanged.

## Dependencies and CI

- FastAPI and Uvicorn provide the ASGI application and local server.
- Pydantic v2 and pydantic-settings with YAML support validate config and load
  `.env`, environment variables, and YAML.
- Hatchling builds the `src/askdocs` package for editable installs and wheels.
- pytest, Ruff, and mypy provide offline tests, linting, and strict type checking.

Retrieval, model, tracing, and evaluation dependencies will be added when their
milestones use them. CI runs the same three Make targets on Python 3.12 for pull
requests, pushes to `main`, and manual workflow runs. It uses the official
[setup-uv action](https://docs.astral.sh/uv/guides/integration/github/).
