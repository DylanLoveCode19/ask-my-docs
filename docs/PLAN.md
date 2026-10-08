# PLAN

Rules: one milestone per session. Write tests/eval checks first. Tick the box when
all acceptance checks pass. Do not start the next milestone without being asked.

## M0 Scaffold
- [x] `pyproject.toml` (uv), package skeleton per ARCHITECTURE.md, `Makefile`, ruff + mypy config
- [x] `docker-compose.yml` with Qdrant, `.env.example`, `config/app.yaml`, `config/thresholds.yaml`
- [x] GitHub Actions workflow: lint + unit tests on PR
- Acceptance: `make setup && make lint && make test` pass on a clean clone; CI is green

**M0 acceptance complete (2026-10-01).** `make setup`, `make lint`, `make test`,
and `docker compose config --quiet` passed locally and on an actual clean Git
clone with a new Python 3.12 virtualenv. Ruff passed, mypy passed for 27 source
files, and all 9 offline tests passed.

Branch: `verify/m0-pr-ci`; [PR #1](https://github.com/DylanLoveCode19/ask-my-docs/pull/1)
targets `main`. The [PR CI run](https://github.com/DylanLoveCode19/ask-my-docs/actions/runs/36874000510)
passed all steps, including Docker Compose validation, at verification commit
`3d06db115779ee170b509ed2c3b6f895bcef09f3`. See `docs/DEVELOPMENT.md` for setup
and dependency rationale. M0 has no remaining acceptance blockers. M1 remains
pending and requires a separate request.

## M1 Ingestion
- [ ] Download/sync script for pinned Langfuse + Ragas docs; writes `data/corpus/SOURCES.md`
- [ ] Heading-aware chunker with stable chunk ids
- [ ] Indexer: dense vectors into Qdrant, BM25 index saved to disk
- Acceptance: unit tests for chunker (sizes, overlap, stable ids); `make ingest` reports file/chunk counts

## M2 Hybrid retrieval
- [ ] BM25 retriever, dense retriever, RRF fusion with tests (known rankings -> known fused order)
- [ ] `eval-fast` v0: hit@k and MRR on golden set for bm25-only, dense-only, hybrid
- Acceptance: hybrid >= max(bm25, dense) on hit@5, or explain why not

## M3 Rerank
- [ ] Cross-encoder reranker behind an interface (fake in tests)
- [ ] Add rerank stage to `eval-fast`; report before/after table
- Acceptance: results table in `docs/RESULTS.md` (bm25, dense, hybrid, hybrid+rerank), including per-stage latency

## M4 Generation + citation enforcement
- [ ] Prompt that outputs JSON `{answer, citations[]}` using only provided chunk ids
- [ ] Citation validator + one corrective retry + refusal path + confidence gate
- [ ] `POST /ask` and `GET /health`
- Acceptance: tests with a fake LLM cover valid, invalid id, fake quote, and no-context cases; citation validity = 1.00 on golden set; refusal accuracy reported

## M5 Observability
- [ ] Langfuse tracing with spans per stage, token usage, cost, trace_id in response
- [ ] Per-request latency and cost logged; p50/p95 computed in eval run
- Acceptance: one `/ask` call shows a full trace in Langfuse; screenshot saved to `docs/img/`

## M6 Eval + CI gate
- [ ] `run_eval.py`: deterministic metrics + latency + cost; writes `reports/eval_<sha>.json`
- [ ] Ragas runner (faithfulness, answer relevancy, context precision) with disk cache and a max-samples cap
- [ ] CI: PR runs `eval-fast`; nightly or label `full-eval` runs `eval-full`
- [ ] Commit `reports/baseline.json`; CI fails on threshold breach and prints deltas
- Acceptance: a deliberately broken change (e.g. k=1) makes CI fail; revert makes it pass

## M7 Polish
- [ ] README: architecture diagram, quickstart, results table, trace screenshot, cost notes
- [ ] Optional minimal demo page
- Acceptance: a stranger can run `make up ingest run` and get a cited answer in under 10 minutes
