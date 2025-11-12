# API Integration Guide for Node.js Team

This document explains how to call the FastAPI RAG backend `/rag/query` endpoint, the available parameters, and examples (curl & Node.js fetch). It also describes the new query expansion and parent context options.

## Endpoint

- URL: `POST http://<HOST>:8000/rag/query`
- Content-Type: `application/json`
- Auth/Env: None enforced by this doc; backend uses `OPENAI_API_KEY` and `DATABASE_URL` in server env.

## Request schema (`RAGQueryRequest`)

- question (string, required): User question (Japanese). min_length=2, max_length=500.
- top_k (int, optional): Number of documents to retrieve (default 5, 1-10).
- domain (string enum, optional): One of `food`, `stay`, `nat`, `his`, `shop`, `lei`.
- area (string, optional): Region filter (e.g., `서울`, `부산`).
- expansion (bool, optional): If true, backend uses Query Expansion to run multiple query variants and merge results. Default: false.
- expansion_variations (array[string], optional): Custom query variants to include in expansion.
- parent_context (bool, optional): If true (default), returned documents include parent summary in `metadata.parent_summary` and in `page_content`.

Example request body:

```json
{
  "question": "温泉旅館のおすすめはありますか",
  "top_k": 3,
  "domain": "stay",
  "area": "부산",
  "expansion": true,
  "expansion_variations": ["温泉 おすすめ", "温泉 露天風呂"],
  "parent_context": true
}
```

## Response schema (`RAGQueryResponse`)

- answer (string): Short answer or aggregated context (first document preview if RAG chain not enabled).
- sources (array[string]): List of `document_id` values for the returned documents.
- latency (float): Response time in seconds.
- metadata (object, optional): Additional info (e.g., retrieved docs metadata when enabled).

Example response (simplified):

```json
{
  "answer": "親ドキュメント要約:\n...",
  "sources": ["J_STAY_000123", "J_STAY_000456"],
  "latency": 0.78,
  "metadata": {
    "retrieved_count": 2
  }
}
```

Note: Currently the backend returns the top document `page_content` as a short `answer` until the RAG chain (LLM answer synthesis) is implemented. Sources and parent_summary are provided to allow the Node.js side to show citations or build its own UI.

## Curl example

```bash
curl -X POST "http://localhost:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "温泉",
    "top_k": 5,
    "domain": "stay",
    "area": "부산",
    "expansion": true
  }'
```

## Node.js (fetch) example

```js
const fetch = require('node-fetch');

async function queryRag() {
  const res = await fetch('http://localhost:8000/rag/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: '温泉旅館のおすすめはありますか',
      top_k: 3,
      domain: 'stay',
      area: '부산',
      expansion: true
    })
  });

  const data = await res.json();
  console.log(data);
}

queryRag();
```

## Notes & Best Practices for Node Team

- Use `expansion=true` for broader recall when users use short queries (e.g., single-word queries).
- `parent_context=true` includes document summary; use it to display contextual snippets or citations.
- Expect `answer` to be a snippet until the RAG LLM chain is fully integrated; use `sources` and `metadata` for display.
- Keep payload size small (question <= 500 chars). The backend enforces request limits.
- Rate-limit client requests to avoid overloading the server; recommended concurrency <= 20.

## Troubleshooting

- If you receive a 500 error, check server logs for `log_exception` details (backend logs).
- If `sources` is empty, confirm that the backend `DATABASE_URL` is configured and the Postgres/pgvector service is healthy.

---

If you want, I can also add an OpenAPI-ready example or a small Node.js wrapper module (2-3 lines) to make calls easier for the frontend team. Would you like that? 

## Node helper (optional)

We added a tiny Node helper at `scripts/node_rag_client.js` that wraps the fetch call and can be used as a CLI or imported into your frontend/backend code. Example:

```js
const { queryRag } = require('../scripts/node_rag_client');

async function example(){
  const res = await queryRag({ question: '温泉', top_k: 3, domain: 'stay', expansion: true });
  console.log(res);
}

example();
```
