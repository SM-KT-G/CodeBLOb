# API 통합 가이드 (Node/Postman)

최신 분리 정책:  
- `/chat` → 일반 대화/장소 검색 전용  
- `/recommend` (=/recommend/itinerary) → 여행 일정 추천 전용  
- `/rag/query` → 고급 RAG 검색

## 환경 변수
- `OPENAI_API_KEY`: 필수
- `DATABASE_URL`: 필수 (PostgreSQL + pgvector)

## 1) 통합 채팅 (대화/검색)
- 엔드포인트: `POST /chat`
- 요청 예시:
```jsonc
{ "text": "서울 맛집 추천해줘" }
```
- 응답 예시:
```jsonc
{
  "chat_completion_id": "chatcmpl-abc",
  "message": "1件の場所が見つかりました。",
  "places": [
    { "name": "명동 교자", "description": "...", "area": "서울", "document_id": "DOC1" }
  ]
}
```
- 비고: `response_type`/`session_id`/`itinerary` 필드는 더 이상 제공되지 않음.

## 2) 여행 일정 추천
- 엔드포인트: `POST /recommend` (alias `/recommend/itinerary`)
- 요청 예시:
```jsonc
{
  "region": "서울",
  "domains": ["food", "nat"],
  "duration_days": 2,
  "themes": ["グルメ"]
}
```
- 응답 예시:
```jsonc
{
  "itineraries": [
    {
      "title": "서울 2일 추천 #1",
      "summary": "샘플",
      "days": [{ "day": 1, "segments": [] }],
      "highlights": []
    }
  ],
  "metadata": { "generated_count": 1, "region": "서울" }
}
```

## 3) RAG 검색 (고급 제어)
- 엔드포인트: `POST /rag/query`
- 요청 예시:
```jsonc
{
  "question": "서울 역사 관광지",
  "top_k": 5,
  "domain": "his",
  "area": "서울",
  "expansion": true
}
```
- 응답 예시:
```jsonc
{
  "answer": "...",
  "sources": ["J_HIS_0001"],
  "latency": 1.23,
  "metadata": { "retrieved_count": 5 }
}
```

## Node 샘플 호출
`scripts/node_rag_client.js`에서 제공:
- `chat({ text })`
- `queryRag({ question, ... })`
- `recommendItinerary({ region, domains, duration_days, ... })`

CLI 사용:
```bash
node scripts/node_rag_client.js chat "こんにちは"
node scripts/node_rag_client.js rag "서울 맛집"
node scripts/node_rag_client.js recommend "서울"
```

## Postman 테스트 팁
- ngrok 등으로 8000 포트 터널링 후 `{ngrok_url}/health`로 상태 확인.
- 일정 추천 테스트 시 `region/domains/duration_days`는 필수.
- DB/LLM 키 미설정 시 500/422가 발생할 수 있으니 로컬 환경변수 확인 필요.
