.PHONY: setup up ingest run test lint eval-fast eval-full

setup:
	uv sync --locked

up:
	docker compose up -d qdrant

ingest:
	uv run python -m askdocs.ingest

run:
	uv run uvicorn askdocs.api.main:app --port 8000 --reload

test:
	uv run pytest -q

lint:
	uv run ruff check .
	uv run mypy src

eval-fast:
	uv run python -m askdocs.evals.run_eval --mode fast

eval-full:
	uv run python -m askdocs.evals.run_eval --mode full
