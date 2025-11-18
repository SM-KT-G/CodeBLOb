# /chat API 명세서

> **Node.js 개발자를 위한 통합 채팅 API 가이드**  
> 작성일: 2025-11-18  
> 버전: v1.0

---

## 개요

`POST /chat`는 **하나의 엔드포인트로 모든 대화를 처리**하는 통합 채팅 API입니다.  
사용자의 의도를 자동으로 파악하여 일반 대화, 장소 검색, 여행 일정 생성 중 하나로 응답합니다.

### 핵심 특징
- ✅ **Function Calling**: OpenAI Function Calling으로 사용자 의도 자동 판단
- ✅ **채팅 기록**: 대화 내용을 MariaDB에 영구 저장
- ✅ **컨텍스트 관리**: 이전 대화를 기억하고 후속 질문에 활용
- ✅ **Structured Outputs**: 100% 유효한 JSON 응답 보장

---

## 엔드포인트

```
POST /chat
```

**Base URL**: `http://localhost:8000` (개발 환경)

---

## 요청 (Request)

### Headers
```http
Content-Type: application/json
```

### Request Body

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| `text` | `string` | ✅ | 사용자 메시지 (최소 1자) | `"서울 맛집 추천해줘"` |
| `session_id` | `string` | ✅ | 세션 ID (사용자 식별용) | `"user123"` |

### 요청 예시
```json
{
  "text": "서울 맛집 추천해줘",
  "session_id": "user123"
}
```

### 유효성 검증
- `text`: 빈 문자열 불가, 공백만 있는 경우 자동 제거
- `session_id`: 필수 값, 빈 문자열 불가

---

## 응답 (Response)

응답은 **사용자 의도에 따라 3가지 타입**으로 구분됩니다.

### 응답 타입 구분

| `response_type` | 설명 | 사용 사례 |
|----------------|------|-----------|
| `"chat"` | 일반 대화 | "안녕하세요", "고마워요", "설명해줘" |
| `"search"` | RAG 장소 검색 | "서울 맛집 추천", "경복궁 정보 알려줘" |
| `"itinerary"` | 여행 일정 생성 | "서울 1박 2일 일정 짜줘", "2일 여행 계획" |

---

## 응답 스키마

### 1. 일반 대화 응답 (`response_type: "chat"`)

사용자가 단순 인사, 감사, 설명 요청 등을 할 때 반환됩니다.

#### Response Fields
```typescript
{
  response_type: "chat",
  message: string  // LLM이 생성한 대화 응답
}
```

#### 예시
```json
{
  "response_type": "chat",
  "message": "안녕하세요! 한국 여행에 대해 무엇이든 물어보세요. 맛집, 관광지, 숙소, 쇼핑 등 도와드리겠습니다."
}
```

---

### 2. 장소 검색 응답 (`response_type: "search"`)

사용자가 장소 정보를 요청할 때 RAG 시스템이 검색한 결과를 반환합니다.

#### Response Fields
```typescript
{
  response_type: "search",
  message: string,        // 검색 결과 요약 메시지
  places: Array<{         // 검색된 장소 리스트
    place_name: string,   // 장소명
    domain: string,       // 도메인 (FOOD, HIS, NAT, STAY, SHOP, LEI)
    area: string,         // 지역
    description: string,  // 장소 설명
    source_id?: string    // 출처 ID (옵션)
  }>,
  latency_ms?: number     // 응답 시간 (밀리초, 옵션)
}
```

#### 예시
```json
{
  "response_type": "search",
  "message": "서울의 추천 맛집을 찾았습니다. 명동과 강남 지역의 유명한 식당들입니다.",
  "places": [
    {
      "place_name": "명동 교자",
      "domain": "FOOD",
      "area": "서울",
      "description": "칼국수와 만두로 유명한 맛집. 1966년부터 운영 중.",
      "source_id": "J_FOOD_000123"
    },
    {
      "place_name": "광장시장",
      "domain": "FOOD",
      "area": "서울",
      "description": "빈대떡, 마약김밥 등 한국 전통 먹거리를 즐길 수 있는 시장.",
      "source_id": "J_FOOD_000456"
    }
  ],
  "latency_ms": 1234
}
```

---

### 3. 여행 일정 응답 (`response_type: "itinerary"`)

사용자가 여행 일정 생성을 요청할 때 Structured Outputs로 생성된 일정을 반환합니다.

#### Response Fields
```typescript
{
  response_type: "itinerary",
  message: string,          // 친절한 인사 메시지
  itinerary: {              // 일정 데이터
    title: string,          // 일정 제목
    summary: string,        // 일정 요약
    days: Array<{           // 일차별 일정
      day: number,          // Day 번호 (1부터 시작)
      segments: Array<{     // 세부 일정
        time: string,       // 시간대 ("오전", "오후", "저녁" 등)
        place_name: string, // 장소명
        description: string // 활동 설명
      }>
    }>,
    highlights: string[]    // 주요 하이라이트
  }
}
```

#### 예시
```json
{
  "response_type": "itinerary",
  "message": "서울 2일 여행 일정을 만들어드렸습니다! 맛집과 관광지를 균형있게 구성했어요.",
  "itinerary": {
    "title": "서울 2일 맛집 & 문화 여행",
    "summary": "명동, 강남, 경복궁을 중심으로 한 맛집과 역사 탐방",
    "days": [
      {
        "day": 1,
        "segments": [
          {
            "time": "오전",
            "place_name": "경복궁",
            "description": "조선시대 정궁 방문. 수문장 교대식 관람 추천."
          },
          {
            "time": "점심",
            "place_name": "광장시장",
            "description": "빈대떡과 마약김밥으로 점심. 한국 전통 시장 체험."
          },
          {
            "time": "오후",
            "place_name": "북촌 한옥마을",
            "description": "전통 한옥 거리 산책. 인증샷 명소."
          },
          {
            "time": "저녁",
            "place_name": "명동",
            "description": "명동 교자에서 저녁. 명동 거리 쇼핑."
          }
        ]
      },
      {
        "day": 2,
        "segments": [
          {
            "time": "오전",
            "place_name": "강남역",
            "description": "카페 거리에서 브런치. K-POP 관련 매장 방문."
          },
          {
            "time": "오후",
            "place_name": "코엑스 몰",
            "description": "별마당 도서관 방문. 쇼핑 및 휴식."
          },
          {
            "time": "저녁",
            "place_name": "강남 맛집",
            "description": "삼겹살 또는 한정식으로 마무리."
          }
        ]
      }
    ],
    "highlights": [
      "경복궁 수문장 교대식",
      "광장시장 빈대떡",
      "북촌 한옥마을 산책",
      "명동 쇼핑",
      "코엑스 별마당 도서관"
    ]
  }
}
```

---

## 에러 응답

### 400 Bad Request
요청 데이터가 유효하지 않을 때 반환됩니다.

```json
{
  "detail": "text는 비어있을 수 없습니다."
}
```

**발생 원인**:
- `text` 필드가 빈 문자열이거나 공백만 있는 경우
- `session_id` 필드가 누락된 경우

### 500 Internal Server Error
서버 내부 오류가 발생했을 때 반환됩니다.

```json
{
  "detail": "채팅 처리 중 오류 발생"
}
```

**발생 원인**:
- LLM API 호출 실패
- 데이터베이스 연결 오류
- 예상치 못한 서버 오류

---

## 사용 예시

### Node.js (fetch API)

```javascript
async function sendChatMessage(text, sessionId) {
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API 요청 실패');
    }

    const data = await response.json();
    
    // response_type에 따라 분기 처리
    switch (data.response_type) {
      case 'chat':
        console.log('일반 대화:', data.message);
        break;
      
      case 'search':
        console.log('장소 검색:', data.message);
        console.log('검색된 장소:', data.places);
        break;
      
      case 'itinerary':
        console.log('여행 일정:', data.message);
        console.log('일정:', data.itinerary);
        break;
      
      default:
        console.log('알 수 없는 응답:', data);
    }
    
    return data;
  } catch (error) {
    console.error('채팅 전송 실패:', error);
    throw error;
  }
}

// 사용 예시
sendChatMessage('서울 맛집 추천해줘', 'user123');
sendChatMessage('안녕하세요', 'user123');
sendChatMessage('서울 2일 여행 일정 짜줘', 'user123');
```

### Node.js (axios)

```javascript
const axios = require('axios');

async function sendChatMessage(text, sessionId) {
  try {
    const response = await axios.post('http://localhost:8000/chat', {
      text: text,
      session_id: sessionId
    });

    const data = response.data;
    
    // response_type에 따라 분기 처리
    if (data.response_type === 'chat') {
      console.log('일반 대화:', data.message);
    } else if (data.response_type === 'search') {
      console.log('장소 검색:', data.message);
      data.places.forEach(place => {
        console.log(`- ${place.place_name} (${place.area}): ${place.description}`);
      });
    } else if (data.response_type === 'itinerary') {
      console.log('여행 일정:', data.message);
      console.log('제목:', data.itinerary.title);
      data.itinerary.days.forEach(day => {
        console.log(`Day ${day.day}:`);
        day.segments.forEach(seg => {
          console.log(`  ${seg.time} - ${seg.place_name}: ${seg.description}`);
        });
      });
    }
    
    return data;
  } catch (error) {
    if (error.response) {
      // 서버가 응답했지만 에러 상태 코드
      console.error('API 에러:', error.response.data.detail);
    } else if (error.request) {
      // 요청은 보냈지만 응답 없음
      console.error('서버 응답 없음');
    } else {
      // 요청 설정 중 에러
      console.error('요청 설정 오류:', error.message);
    }
    throw error;
  }
}
```

### cURL 예시

```bash
# 일반 대화
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "안녕하세요",
    "session_id": "user123"
  }'

# 장소 검색
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "서울 맛집 추천해줘",
    "session_id": "user123"
  }'

# 여행 일정
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "서울 2일 여행 일정 짜줘",
    "session_id": "user123"
  }'
```

---

## TypeScript 타입 정의

프론트엔드에서 사용할 수 있는 TypeScript 인터페이스입니다.

```typescript
// 요청
interface ChatRequest {
  text: string;
  session_id: string;
}

// 공통 응답 타입
type ChatResponse = 
  | ChatOnlyResponse 
  | SearchResponse 
  | ItineraryResponse;

// 일반 대화 응답
interface ChatOnlyResponse {
  response_type: 'chat';
  message: string;
}

// 장소 검색 응답
interface SearchResponse {
  response_type: 'search';
  message: string;
  places: Place[];
  latency_ms?: number;
}

interface Place {
  place_name: string;
  domain: 'FOOD' | 'HIS' | 'NAT' | 'STAY' | 'SHOP' | 'LEI';
  area: string;
  description: string;
  source_id?: string;
}

// 여행 일정 응답
interface ItineraryResponse {
  response_type: 'itinerary';
  message: string;
  itinerary: Itinerary;
}

interface Itinerary {
  title: string;
  summary: string;
  days: ItineraryDay[];
  highlights: string[];
}

interface ItineraryDay {
  day: number;
  segments: ItinerarySegment[];
}

interface ItinerarySegment {
  time: string;
  place_name: string;
  description: string;
}

// 에러 응답
interface ErrorResponse {
  detail: string;
}
```

---

## 채팅 기록 관리

### 세션 ID 관리
- `session_id`는 사용자별로 고유해야 합니다
- 권장 형식: `user_{userId}` 또는 UUID
- 같은 `session_id`를 사용하면 이전 대화를 기억합니다

### 채팅 기록 저장
- 모든 대화는 자동으로 MariaDB에 저장됩니다
- 저장 내용:
  - 사용자 메시지 (`text`)
  - 응답 타입 (`response_type`)
  - 전체 응답 데이터 (JSON)
  - 타임스탬프

### 컨텍스트 관리
- 최근 5개 대화를 자동으로 LLM에 전달합니다
- 후속 질문 가능: 
  ```
  사용자: "서울 맛집 추천해줘"
  AI: [장소 검색 결과]
  사용자: "거기 중에 가장 유명한 곳은?"  <- 이전 대화 기억
  ```

---

## 응답 시간 (Latency)

| 응답 타입 | 평균 응답 시간 | 설명 |
|-----------|----------------|------|
| `chat` | 1~3초 | LLM 호출만 필요 |
| `search` | 2~5초 | RAG 검색 + LLM 호출 |
| `itinerary` | 5~10초 | Query Expansion + RAG + Structured Outputs |

**최대 타임아웃**: 30초

---

## 주의사항 및 제한사항

### 1. 요청 크기
- `text` 최대 길이: 제한 없음 (단, 너무 긴 텍스트는 LLM 토큰 제한에 걸릴 수 있음)
- 권장 최대 길이: 500자

### 2. Rate Limiting
- 현재 Rate Limiting 없음
- 프로덕션 환경에서는 추가 필요

### 3. 동시 요청
- 같은 `session_id`로 동시 요청 시 경쟁 조건 발생 가능
- 순차적으로 요청하는 것을 권장

### 4. 캐싱
- 동일한 질문에 대한 캐싱 없음 (매번 새로운 응답 생성)
- Redis 캐시는 RAG 검색에만 적용됨

### 5. 언어 지원
- 현재 **한국어**만 지원
- 일본어 데이터베이스를 사용하므로 일부 응답이 일본어로 나올 수 있음

---

## FAQ

### Q1. `session_id`는 어떻게 생성하나요?
**A**: 사용자별로 고유한 ID를 사용하세요. 예:
```javascript
const sessionId = `user_${userId}`;
// 또는
const sessionId = `${userId}_${Date.now()}`;
```

### Q2. 이전 대화를 초기화하려면?
**A**: 새로운 `session_id`를 사용하면 됩니다.

### Q3. 응답 타입을 미리 지정할 수 있나요?
**A**: 아니요. Function Calling이 자동으로 판단합니다. 특정 타입만 필요한 경우:
- 장소 검색: `POST /rag/query` 사용
- 여행 일정: `POST /recommend/itinerary` 사용

### Q4. 에러 처리는 어떻게 하나요?
**A**: HTTP 상태 코드를 확인하세요:
```javascript
if (!response.ok) {
  const error = await response.json();
  console.error('API 에러:', error.detail);
  // 사용자에게 에러 메시지 표시
}
```

### Q5. 응답 시간이 너무 오래 걸려요
**A**: 
- `itinerary` 타입은 5~10초 소요 (정상)
- 30초 이상 걸리면 타임아웃 에러 발생
- 네트워크 상태 확인 필요

### Q6. 장소 검색 결과가 없을 때는?
**A**: `places` 배열이 빈 배열 `[]`로 반환됩니다:
```json
{
  "response_type": "search",
  "message": "죄송합니다. 해당하는 장소를 찾지 못했습니다.",
  "places": []
}
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| v1.0 | 2025-11-18 | 초기 문서 작성 |

---

## 문의

기술적 문제나 궁금한 점이 있으면 백엔드 팀에 문의하세요.

**관련 문서**:
- [API_INTEGRATION_FOR_NODE.md](./API_INTEGRATION_FOR_NODE.md) - Node.js 통합 가이드
- [README.md](../README.md) - 전체 프로젝트 문서
- [IMPLEMENTATION_TRACKER.md](./IMPLEMENTATION_TRACKER.md) - 구현 진행 상황
