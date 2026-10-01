# AGENTS.md

## Project
"Ask My Docs": a production-style RAG service that answers questions about the
Langfuse and Ragas documentation. It combines hybrid retrieval (BM25 + dense),
cross-encoder reranking, enforced citations, full tracing (latency, tokens, cost),
and a CI-gated evaluation pipeline.

Read `docs/SPEC.md`, `docs/ARCHITECTURE.md` and `docs/PLAN.md` before coding.
Work on ONE milestone from `docs/PLAN.md` at a time, and stop when its
acceptance checks pass. Tick the checkbox in PLAN.md when done.

## Stack (do not swap without asking)
- Python 3.12, `uv` for dependencies, FastAPI, Pydantic v2
- Vector store: Qdrant (Docker). BM25: `bm25s`. Fusion: our own RRF implementation
- Embeddings: `BAAI/bge-small-en-v1.5` (local). Reranker: `BAAI/bge-reranker-base` (local)
- LLM + judge: any OpenAI-compatible endpoint, configured only via env vars
- Orchestration: LangChain components only where they help; no unnecessary abstraction
- Tracing: Langfuse (cloud free tier by default). Evaluation: Ragas + custom checks
- CI: GitHub Actions

## Commands
- `make setup`   install deps (uv sync)
- `make up`      start Qdrant
- `make ingest`  load, chunk, embed, index the corpus
- `make run`     start the API on :8000
- `make test`    unit tests (no network, no LLM calls)
- `make lint`    ruff + mypy
- `make eval-fast`  deterministic eval (no LLM judge calls)
- `make eval-full`  deterministic + Ragas LLM-judged metrics

## Hard rules
1. Every answer MUST contain citations that map to retrieved chunks. If the
   context does not support an answer, return the refusal response, never guess.
2. NEVER edit `data/eval/golden.jsonl` or `config/thresholds.yaml` to make CI pass.
   If a threshold seems wrong, explain why in your reply and ask.
3. No secrets in code or git. Use `.env` (see `.env.example`).
4. Unit tests must not call external APIs. Mock the LLM and the embedder.
5. Every model name, price, k value, chunk size lives in config, not in code.
6. Write the test (or eval check) first, then the implementation.
7. Keep functions small, fully type-hinted, with docstrings on public functions.
8. Do not add dependencies without stating why in the PR/summary.

## Definition of Done (per milestone)
- `make lint` and `make test` pass
- Acceptance checks of the milestone in PLAN.md pass
- Relevant docs updated (ARCHITECTURE.md if design changed)
- Short summary of what changed and what is left
