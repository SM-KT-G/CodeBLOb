# Chat API 응답 형식 수정 (2025-01-19)

## 변경 사항

### 1. `session_id` 필드 → Optional로 변경

**Before:**
```json
{
  "text": "서울 맛집 추천해줘",
  "session_id": "user123"  // 필수
}
```

**After:**
```json
{
  "text": "서울 맛집 추천해줘"
  // session_id는 선택 사항
}
```

**변경 이유:**
- Node 담당자 요청: "Chat Text응답형식에 session_id 빼주면"
- 프론트엔드에서 세션 관리가 필요 없는 경우 간소화

**동작:**
- `session_id` 제공 시: 채팅 기록 저장 및 컨텍스트 유지
- `session_id` 미제공 시: 일회성 대화로 처리 (기록 저장 안 됨)

---

### 2. `latency_ms` 필드 → 제거

**Before:**
```json
{
  "response_type": "search",
  "message": "서울의 추천 맛집을 찾았습니다.",
  "places": [...],
  "latency_ms": 1234  // 응답 시간
}
```

**After:**
```json
{
  "response_type": "search",
  "message": "서울의 추천 맛집을 찾았습니다.",
  "places": [...]
  // latency_ms 제거
}
```

**변경 이유:**
- Node 담당자 요청: "Rag응답에 응답속도 빼주면"
- 프론트엔드에서 응답 속도 표시가 필요 없음

---

## 수정된 파일

### 1. `backend/schemas.py`
```python
class ChatRequest(BaseModel):
    """통합 채팅 요청"""
    text: str = Field(..., min_length=1, description="사용자 메시지")
    session_id: Optional[str] = Field(default=None, description="세션 ID (선택적)")  # ← 변경
```

### 2. `backend/unified_chat.py`
```python
# session_id가 있을 때만 채팅 기록 저장
if self.chat_history and request.session_id:
    self.chat_history.save_message(...)

# session_id가 있을 때만 이전 대화 로드
if self.chat_history and request.session_id:
    context = self.chat_history.get_recent_context(...)
```

### 3. `docs/CHAT_API_SPEC.md`
- Request Body: `session_id` 필수 → 선택 사항
- Search Response: `latency_ms` 필드 제거
- TypeScript 인터페이스 업데이트

---

## 하위 호환성

### ✅ 기존 코드 호환 가능
```javascript
// 기존 방식 (session_id 포함) - 여전히 작동
fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "서울 맛집 추천",
    session_id: "user123"
  })
});
```

### ✅ 새로운 방식 (session_id 생략)
```javascript
// 새로운 방식 (session_id 생략) - 일회성 대화
fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "서울 맛집 추천"
  })
});
```

### ⚠️ latency_ms는 더 이상 반환되지 않음
```javascript
// Before: latency_ms 사용 중이었다면 제거 필요
response.latency_ms  // ← undefined

// After: 제거하거나 옵셔널 체이닝 사용
response.latency_ms ?? 0
```

---

## 테스트 결과

```bash
$ python test_chat_request.py
✅ session_id 있는 요청: OK
✅ session_id 없는 요청: OK
✅ 빈 text 거부: OK
✅ 모든 테스트 통과!
```

---

## 배포 체크리스트

- [x] `backend/schemas.py` 수정
- [x] `backend/unified_chat.py` 수정
- [x] `docs/CHAT_API_SPEC.md` 업데이트
- [x] 테스트 작성 및 실행
- [ ] Docker 이미지 재빌드
- [ ] 프론트엔드 팀 공유

---

## 프론트엔드 마이그레이션 가이드

### 1. session_id 제거 (권장)
```diff
// 간단한 일회성 대화
- const response = await chatAPI({ text: "질문", session_id: generateUUID() });
+ const response = await chatAPI({ text: "질문" });
```

### 2. session_id 유지 (채팅 기록 필요 시)
```javascript
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
