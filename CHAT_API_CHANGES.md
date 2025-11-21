# Chat API 업데이트 (2025-11-21)

## 변경 사항

### 1. /chat은 대화/검색 전용으로 축소
- `response_type`과 일정(Itinerary) 응답을 제거했습니다.
- 요청 스키마: `{ "text": "..." }` 그대로 유지, `session_id` 미지원.
- 응답 예시:
```json
{
  "chat_completion_id": "chatcmpl-...",
  "message": "1件の場所が見つかりました。",
  "places": [
    {
      "name": "명동 교자",
      "description": "...",
      "area": "서울",
      "document_id": "DOC1"
    }
  ]
}
```

### 2. 일정 추천은 `/recommend` (또는 `/recommend/itinerary`)에서만 제공
- 요청 스키마: `ItineraryRecommendationRequest`
- 응답 스키마: `ItineraryRecommendationResponse`
- 예시:
```json
{
  "itineraries": [
    {
      "title": "서울 2일 추천 #1",
      "summary": "샘플",
      "days": [ { "day": 1, "segments": [] } ],
      "highlights": []
    }
  ],
  "metadata": { "generated_count": 1, "region": "서울" }
}
```

### 3. 클라이언트 변경 지침 (Node/웹)
- `/chat` 호출 시 `text`만 전송, `response_type` 분기 제거, `places` 존재 여부로 검색 응답 판단.
- 일정 페이지에서는 `/recommend` 호출로 일정 데이터를 받음(`/chat` 사용하지 않음).

### 4. 영향 범위
- 서버: `backend/unified_chat.py`(itinerary 경로 제거), `backend/function_tools.py`(itinerary tool 제거)
- API 문서: `README.md`, `docs/FILE_CATALOG.md`
- 클라이언트: `scripts/node_rag_client.js` (`response_type`, `session_id` 제거)
// 채팅 기록이 필요한 경우 (예: 대화 이어가기)
const sessionId = localStorage.getItem('sessionId') || generateUUID();
const response = await chatAPI({ 
  text: "질문", 
  session_id: sessionId 
});
```

### 3. latency_ms 제거
```diff
- console.log(`응답 시간: ${response.latency_ms}ms`);
+ // latency_ms는 더 이상 사용 불가
```

---

## 참고

- Commit Hash: (추후 추가)
- 작성일: 2025-01-19
- 요청자: Node 담당자
