# API Response Fixtures

Node.js로 전달되는 실제 API 응답 형식을 저장한 폴더입니다.

## 파일 목록

### 1. `rag_query_response.json`
**엔드포인트**: `POST /rag/query`

RAG 쿼리 응답 예시입니다.

**필드 설명**:
- `answer` (string): LLM이 생성한 일본어 답변
- `sources` (array): 참조한 문서 ID 목록
- `latency` (number): 응답 생성 시간 (초)
- `metadata` (object): 추가 정보
  - `model`: 사용된 LLM 모델
  - `top_k`: 검색된 문서 개수
  - `expansion`: 쿼리 확장 사용 여부
  - `parent_context`: Parent context 포함 여부
  - `retrieved_count`: 실제 검색된 문서 수

**Node.js 사용 예시**:
```javascript
const response = await fetch('http://localhost:8000/rag/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "明洞について教えてください",
    top_k: 5,
    expansion: false
  })
});
const data = await response.json();
// data 구조는 rag_query_response.json과 동일
```

---

### 2. `itinerary_response.json`
**엔드포인트**: `POST /recommend/itinerary`

여행 일정 추천 응답 예시입니다.

**필드 설명**:
- `itineraries` (array): 추천 일정 목록
  - `title` (string): 일정 제목
  - `summary` (string): 일정 요약
  - `days` (array): 일차별 계획
    - `day` (number): 일차 (1부터 시작)
    - `segments` (array): 방문 장소 목록
      - `time` (string): 시간대 ("午前", "午後" 등)
      - `place_name` (string): 장소명
      - `description` (string): 장소 설명
      - `document_id` (string): 참조 문서 ID
      - `source_url` (string|null): 원본 URL
      - `area` (string): 지역
      - `notes` (string|null): 추가 메모
  - `highlights` (array): 주요 장소 목록
  - `estimated_budget` (string): 예상 예산 수준
  - `metadata` (object): 추가 정보
- `metadata` (object): 응답 메타데이터
  - `generated_count`: 생성된 일정 개수
  - `duration_days`: 여행 일수
  - `region`: 여행 지역
  - `domains`: 관심 도메인 목록
  - `themes`: 테마 목록
  - `generator`: 생성 방식 ("llm" 또는 "rule")

**Node.js 사용 예시**:
```javascript
const response = await fetch('http://localhost:8000/recommend/itinerary', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    region: "ソウル",
    domains: ["shop", "his"],
    duration_days: 2,
    themes: ["インスタ映え"],
    transport_mode: "public",
    budget_level: "standard"
  })
});
const data = await response.json();
// data 구조는 itinerary_response.json과 동일
```

---

### 3. `health_response.json`
**엔드포인트**: `GET /health`

헬스 체크 응답 예시입니다.

**필드 설명**:
- `status` (string): 전체 상태 ("healthy" 또는 "degraded")
- `timestamp` (string): 체크 시간 (ISO 8601)
- `version` (string): API 버전
- `checks` (object): 각 컴포넌트 상태
  - `api`: API 서버 상태 ("ok")
  - `db`: 데이터베이스 상태 ("ok", "error", "missing")
  - `llm`: LLM 상태 ("ok", "error", "missing")
  - `cache`: 캐시 상태 ("ok", "error", "missing")

**Node.js 사용 예시**:
```javascript
const response = await fetch('http://localhost:8000/health');
const data = await response.json();
// data 구조는 health_response.json과 동일

if (data.status === 'healthy') {
  console.log('All systems operational');
} else {
  console.warn('Some systems degraded:', data.checks);
}
```

---

## Fixtures 업데이트 방법

테스트를 실행하면 자동으로 최신 응답 형식으로 업데이트됩니다:

```bash
python -m pytest tests/test_response_fixtures.py -v
```

---

## TypeScript 타입 정의

Node.js/TypeScript에서 사용할 수 있는 타입 정의:

```typescript
// RAG Query
interface RAGQueryResponse {
  answer: string;
  sources: string[];
  latency: number;
  metadata: {
    model: string;
    top_k: number;
    expansion: boolean;
    parent_context: boolean;
    fallback?: boolean;
    retrieved_count: number;
  };
}

// Itinerary
interface ItinerarySegment {
  time: string | null;
  place_name: string;
  description: string;
  document_id: string | null;
  source_url: string | null;
  area: string | null;
  notes: string | null;
}

interface DayPlan {
  day: number;
  segments: ItinerarySegment[];
}

interface ItineraryPlan {
  title: string;
  summary: string;
  days: DayPlan[];
  highlights: string[];
  estimated_budget: string | null;
  metadata: Record<string, any>;
}

interface ItineraryResponse {
  itineraries: ItineraryPlan[];
  metadata: {
    generated_count: number;
    duration_days: number;
    region: string;
    domains: string[];
    themes: string[];
    generator: 'llm' | 'rule';
    latency?: number;
  };
}

// Health Check
interface HealthResponse {
  status: 'healthy' | 'degraded';
  timestamp: string;
  version: string;
  checks: {
    api: string;
    db: string;
    llm: string;
    cache: string;
  };
}
```
