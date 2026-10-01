# SPEC

## Goal
Answer questions about the Langfuse and Ragas documentation with grounded,
cited answers, and prove quality and cost with automated evaluation.

## Non-goals
- No chat UI beyond a minimal demo page (optional, last milestone)
- No multi-tenant auth, no streaming, no conversation memory
- No fine-tuning

## Corpus
- Markdown/MDX docs from the Langfuse docs repo and the Ragas docs folder
- Pinned to a specific git commit per repo (record SHAs in `data/corpus/SOURCES.md`)
- Target: 50-200 files. Keep corpus files out of git if large; keep the ingestion script reproducible

## API
`POST /ask`
Request: `{"question": "string", "top_k": 5}`
Response:
```json
{
  "answer": "string",
  "citations": [
    {"doc": "path/or/url", "chunk_id": "string", "quote": "short supporting span"}
  ],
  "refused": false,
  "trace_id": "string",
  "latency_ms": 0,
  "usage": {"prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}
}
```
`POST /ingest` (re)builds the indexes from `data/corpus/`.
`GET /health`.

## Citation enforcement
- The model must cite using chunk ids from the provided context only.
- A post-generation validator checks: every citation id exists in the retrieved
  set, and each `quote` is a (near-)verbatim substring of its chunk.
- If validation fails: retry once with a corrective prompt, otherwise return a refusal.
- If retrieval confidence is below a configured threshold: return `refused: true`
  with a message that the docs do not cover the question.

## Quality and performance targets (initial, calibrate after first baseline)
Stored in `config/thresholds.yaml`.

| Metric | Target | Needs LLM judge? |
|---|---|---|
| Retrieval hit@5 (gold doc in top 5) | >= 0.80 | no |
| MRR | >= 0.60 | no |
| Citation validity rate | = 1.00 | no |
| Refusal accuracy on unanswerable questions | >= 0.80 | no |
| Faithfulness (Ragas) | >= 0.85 | yes |
| Answer relevancy (Ragas) | >= 0.80 | yes |
| Context precision (Ragas) | >= 0.70 | yes |
| Latency p50 / p95 | < 3s / < 8s | no |
| Cost per request | < $0.005 | no |

## Observability
Each request produces one Langfuse trace with spans: `retrieve_bm25`,
`retrieve_dense`, `fuse`, `rerank`, `generate`, `validate_citations`.
Record latency per span, token usage, computed cost, and eval scores attached
to traces for eval runs.

## CI gating
- Every PR: lint, unit tests, `make eval-fast` (zero LLM cost). Fails if any
  deterministic metric, p95 latency or cost/request regresses past thresholds.
- Nightly or PR label `full-eval`: `make eval-full` with Ragas on the golden set.
  Results cached by (question, config hash) to avoid paying twice.
- Eval run writes `reports/eval_<sha>.json` and a markdown summary as a PR comment/artifact.
