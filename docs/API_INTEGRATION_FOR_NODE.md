# API Integration Guide for Node.js Team

This document explains how to call the FastAPI RAG backend `/rag/query` endpoint, the available parameters, and examples (curl & Node.js fetch). It also describes the query expansion, parent context, and Redis 캐시 옵션.

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
- parent_context (bool, optional): If true (default), returned documents include parent summary in `metadata.parent_summary` and in `page_content`. False면 child chunk만 반환.

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

- answer (string): LLM 생성 답변(체인 오류 시 fallback으로 상위 문서 snippet을 반환).
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
    "retrieved_count": 2,
    "expansion_metrics": {
      "variants": ["温泉旅館のおすすめはありますか", "温泉旅館のおすすめはありますか おすすめ"],
      "success_count": 2,
      "failure_count": 0,
      "retrieved": 2,
      "duration_ms": 120.5,
      "cache_hit": false
    }
  }
}
```

### Metadata 필드 안내

- `retrieved_count`: 최종 반환된 문서 수.
- `expansion_metrics`: `expansion=true`일 때만 포함. 변형 리스트, 성공/실패 횟수, 캐시 적중 여부(`cache_hit`), 실행 시간(`duration_ms`) 등을 포함해 노출합니다.
- `fallback`: RAG 체인 오류 시 `true`.

Note: 기본적으로 LangChain RAG 체인이 answer를 생성하며, fallback 시에만 상위 문서 snippet이 사용됩니다.

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

- Use `expansion=true` for broader recall when users use short queries (e.g., single-word queries). 응답의 `metadata.expansion_metrics`를 확인해 변형 수·캐시 여부를 모니터링하세요.
- `parent_context=true` includes document summary; use it to display contextual snippets or citations. False일 때는 요약이 제거됩니다.
- Keep payload size small (question <= 500 chars). The backend enforces request limits.
- Rate-limit client requests to avoid overloading the server; recommended concurrency <= 20.
- Redis 캐시가 활성화되면 동일 쿼리는 TTL(기본 300초) 동안 빠르게 응답하며, 캐시 미사용 시 `metadata.expansion_metrics.cache_hit=false`로 확인할 수 있습니다.

## Troubleshooting

- If you receive a 500 error, check server logs for `log_exception` details (backend logs) and `/health` 응답에서 `db` / `llm` / `cache` 상태를 확인하세요.
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
