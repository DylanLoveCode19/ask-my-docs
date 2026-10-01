# ARCHITECTURE

## Request flow
```
question
  -> embed query (bge-small, local)
  -> [parallel] BM25 top-N (bm25s)  +  dense top-N (Qdrant)
  -> RRF fusion (own implementation, k=60) -> top-M candidates
  -> cross-encoder rerank (bge-reranker-base, local) -> top-K
  -> confidence gate (rerank score threshold) -> refuse if too low
  -> generate (OpenAI-compatible LLM, JSON output with citations)
  -> validate citations (ids exist, quotes are substrings) -> retry once -> refuse
  -> response + Langfuse trace
```

## Layout
```
src/askdocs/
  config.py        # pydantic-settings; loads .env + config/*.yaml
  ingest/          # loaders.py, chunking.py, indexer.py
  retrieval/       # bm25.py, dense.py, fusion.py (RRF), rerank.py, pipeline.py
  generation/      # prompts.py, llm.py, citations.py
  obs/             # tracing.py (Langfuse wrapper), cost.py (token -> USD from config)
  api/             # main.py (FastAPI), schemas.py
  evals/           # run_eval.py, metrics.py, ragas_runner.py, report.py
config/            # app.yaml (models, k values, chunk size, prices), thresholds.yaml
data/corpus/       # pinned docs + SOURCES.md
data/eval/         # golden.jsonl (human-owned, do not edit via agent)
tests/             # unit tests with fakes for LLM and embedder
reports/           # eval outputs (gitignored except baseline.json)
```

## Key design decisions
- **M0 configuration:** `Settings` validates `config/app.yaml`, with `.env` and
  environment overrides (nested keys use `__`). Run from the repository root.
  Credentials may be empty for offline checks; service clients and threshold
  loading are deferred to the milestones that use them. See `DEVELOPMENT.md`.
- **Chunking:** split markdown by headings first, then by token budget with overlap.
  Each chunk keeps `doc`, `heading_path`, `chunk_id` (stable hash of doc + offset).
- **Why RRF:** needs no score normalisation between BM25 and cosine. ~20 lines, unit-tested.
- **Local models = near-zero marginal cost.** Only the generator and the Ragas judge call an API.
- **Provider-agnostic LLM:** one `LLMClient` protocol; base URL, key and model come from env.
- **Cost accounting:** price per 1M input/output tokens in `config/app.yaml`;
  `obs/cost.py` computes USD per request from reported usage.
- **Tracing:** wrapper around Langfuse so tests can swap in a no-op tracer.
- **Eval cost control:** `eval-fast` never calls an LLM. `eval-full` caches LLM and judge
  outputs on disk keyed by (question, config hash).
- **Baseline file:** `reports/baseline.json` is committed after M6; CI compares
  against thresholds and also reports delta vs baseline.
