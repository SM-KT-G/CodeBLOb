# /chat 응답 포맷 (Node 저장용)

백엔드는 LLM/RAG 응답만 JSON으로 반환하고, 저장은 Node에서 수행합니다. `response_type`을 포함하지 않으며, OpenAI ChatCompletion ID를 `chat_completion_id`로 내려줍니다.

## 공통 규칙
- 모든 응답은 JSON 객체
- `chat_completion_id`: OpenAI ChatCompletion 응답 ID (예: `chatcmpl-abc123`)
- `message`: LLM이 생성한 텍스트(일반 대화, 검색 요약, 일정 인사)
- `places`/`itinerary`는 의도에 따라 선택적으로 포함

## 요청 예시
```json
{
  "text": "서울 맛집 추천해줘"
}
```

## 응답 예시

### 1) 일반 대화
```json
{
  "chat_completion_id": "chatcmpl-abc123",
  "message": "안녕하세요! 한국 여행에 대해 무엇이든 물어보세요."
}
```

### 2) 검색(RAG)
```json
{
  "chat_completion_id": "chatcmpl-xyz789",
  "message": "3件の場所が見つかりました。",
  "places": [
    {
      "name": "명동 교자",
      "description": "칼국수와 만두로 유명한 맛집...",
      "area": "서울 중구",
      "document_id": "DOC_001"
    },
    {
      "name": "광장시장",
      "description": "빈대떡, 마약김밥 등 전통 먹거리...",
      "area": "서울 종로구",
      "document_id": "DOC_002"
    }
  ]
}
```

### 3) 일정 생성
```json
{
  "chat_completion_id": "chatcmpl-itin456",
  "message": "서울 2일 여행 일정을 준비했어요!",
  "itinerary": {
    "title": "서울 2일 맛집 & 문화 여행",
    "summary": "명동·강남·경복궁 중심",
    "days": [
      {
        "day": 1,
        "segments": [
          { "time": "오전", "place_name": "경복궁", "description": "수문장 교대식 관람", "place_id": "DOC_101" },
          { "time": "점심", "place_name": "광장시장", "description": "빈대떡·마약김밥", "place_id": "DOC_102" }
        ]
      },
      {
        "day": 2,
        "segments": [
          { "time": "오전", "place_name": "남산타워", "description": "전망대 방문", "place_id": "DOC_201" }
        ]
      }
    ],
    "highlights": ["경복궁", "광장시장", "남산타워"]
  }
}
```

### 4) 에러
```json
{
  "chat_completion_id": "chatcmpl-err999",
  "message": "처리 중 오류가 발생했습니다: ..."
}
```

## 저장 가이드 (Node 측)
- 모든 응답을 LongText 컬럼 하나로 저장 가능 (`message` 중심). 
- `chat_completion_id`는 OpenAI 호출 상관관계/추적용으로 함께 저장 권장.
- `places`/`itinerary`는 필요 시 JSON 컬럼/LongText에 저장하거나 무시 가능합니다.
