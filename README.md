# FastAPI RAG Backend

한국 관광 정보를 일본어로 제공하는 Retrieval-Augmented Generation 백엔드입니다. FastAPI와 PostgreSQL(pgvector)을 기반으로 parent-child 청크 구조와 Query Expansion을 활용해 빠르고 정확한 응답을 제공합니다.

---

## 주요 기능

### 1. 통합 채팅 시스템 ✨ NEW (2025-11-17)
- **POST /chat**: 하나의 엔드포인트로 일반 대화 + 장소 검색 처리
- **Function Calling**: 사용자 의도 자동 파악 (일반 대화 / RAG 검색)
- **Structured Outputs**: 100% JSON 보장 (gpt-4o-mini) — 일정 생성은 `/recommend/itinerary`에서만 지원
- **채팅 기록**: MariaDB에 세션별 대화 영구 저장
- **컨텍스트 관리**: 이전 대화를 기억하고 후속 질문에 활용

### 2. RAG v1.1 Parent-Child 아키텍처
- **LangChain 기반 RAG 체인**: Retriever → LLM 체인으로 답변·출처·지연시간을 반환
- **Parent/Child QA 스키마**: tourism_parent/child 테이블에 풍부한 메타데이터를 저장해 domain/area 필터링 지원
- **Query Expansion**: JSON 설정 파일로 구두점 제거·접미어·사용자 변형을 관리하고, 변형별 성공/실패 지표를 로깅
- **캐시 없이 단순화**: Redis 의존성을 제거해 운영 구성을 단순화했습니다.

### 3. 여행 일정 추천
- **Query Expansion + LLM**: 지역/도메인/테마에 맞는 맞춤형 여행 일정을 자동 생성
- **Structured Outputs**: 100% 유효한 JSON 일정 반환

### 4. 운영 및 모니터링
- **헬스 체크**: `/health` 엔드포인트에서 API/DB/LLM 상태를 보고하고 degraded 상태 감지
- **테스트 스위트**: FastAPI TestClient 기반 통합 테스트 15/15 통과 (2분 18초)

---

## 기술 스택

| 영역 | 사용 기술 |
| --- | --- |
| Backend | FastAPI 0.115.5, Python 3.10+ |
| Database | PostgreSQL 17 + pgvector, MariaDB 10.11 |
| LLM & 임베딩 | OpenAI gpt-4o-mini (Function Calling + Structured Outputs), intfloat/multilingual-e5-small (384d) |
| 테스트/품질 | pytest + pytest-asyncio, httpx, black, ruff |

---

## 디렉터리 개요

```
backend/
  main.py               # FastAPI 엔트리포인트
  retriever.py          # PGVector 쿼리 + Query Expansion + 캐시
  query_expansion.py    # 설정 로드 + 변형 생성 헬퍼
  rag_chain.py          # LangChain RetrievalQA 체인
  llm_base.py           # OpenAI LLM 래퍼 (Structured Outputs 포함)
  itinerary.py          # 여행 일정 추천 플래너 (Query Expansion + LLM)
  unified_chat.py       # 통합 채팅 핸들러 (Function Calling)
  function_tools.py     # Function Calling 도구 정의
  schemas.py            # Pydantic 모델
  db/                   # ConnectionPool 및 스키마 스크립트
    init_vector_v1.1.sql       # PostgreSQL 벡터 DB 스키마
  utils/logger.py       # JSON 로깅 헬퍼
config/
  query_expansion.json  # Query Expansion 기본 설정
docs/                   # 파일/계획/상태 문서
scripts/                # 임베딩 및 운영 스크립트
tests/                  # FastAPI/Query Expansion/RAG 테스트
```

---

## 사전 준비

- Python 3.10+
- PostgreSQL 17 + pgvector (Docker Compose로 실행 가능)
- MariaDB 10.11+ (채팅 기록 저장용)

---

## 설치 및 실행

```bash
# 1) 의존성 설치
pip install -r requirements.txt

# 2) 환경 변수 파일 작성
cp .env.example .env
# .env에서 OPENAI_API_KEY, DATABASE_URL 등 수정

# 3) (옵션) Query Expansion 설정 변경
# config/query_expansion.json 수정 또는 QUERY_EXPANSION_CONFIG_PATH 지정

# 4) DB (Docker) 실행
docker-compose up -d

# 5) FastAPI 서버 실행
uvicorn backend.main:app --reload
```

---

## 환경 변수

| 키 | 설명 |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI ChatCompletion/Embedding 키 |
| `OPENAI_MODEL` | LLM 모델명 (기본: `gpt-4o-mini`) |
| `DATABASE_URL` | PostgreSQL 접속 URL |
| `MARIADB_HOST` | MariaDB 호스트 (기본: localhost) |
| `MARIADB_PORT` | MariaDB 포트 (기본: 3306) |
| `MARIADB_USER` | MariaDB 사용자 (기본: training_user) |
| `MARIADB_PASSWORD` | MariaDB 비밀번호 |
| `MARIADB_DATABASE` | MariaDB 데이터베이스명 (기본: training_db) |
| `MARIADB_PORT` | MariaDB 포트 (기본: 3306) |
| `MARIADB_USER` | MariaDB 사용자명 |
| `MARIADB_PASSWORD` | MariaDB 비밀번호 |
| `MARIADB_DATABASE` | MariaDB 데이터베이스 이름 |
| `LOG_LEVEL` | 로깅 레벨 (INFO/DEBUG 등) |
| `QUERY_EXPANSION_CONFIG_PATH` | Query Expansion JSON 파일 경로(선택) |

---

## Query Expansion 설정

- 기본 설정: `config/query_expansion.json`
- 항목
  - `punctuation_chars`: 제거할 구두점 목록
  - `suffixes`: 접미어/추천 키워드 리스트
  - `max_variations`: 최대 변형 개수
- 환경 변수 `QUERY_EXPANSION_CONFIG_PATH`로 외부 파일을 지정할 수 있습니다.

---

## 주요 모듈 설명

### Backend 모듈

#### `backend/main.py`
- FastAPI 애플리케이션 엔트리포인트
- 환경변수 검증 및 로깅 설정
- 라우터: `/rag/query`, `/recommend/itinerary`, `/health`
- lifespan 관리로 Retriever/캐시 초기화 및 정리

#### `backend/llm_base.py`
- OpenAI API 래퍼 (동기/비동기 클라이언트)
- GPT-4 Turbo 모델 호출 인터페이스
- **Structured Outputs 지원**: `generate_structured()` 메서드로 100% JSON 보장
- 에러 핸들링 및 로깅

#### `backend/unified_chat.py`
- **통합 채팅 핸들러**: Function Calling으로 사용자 의도 자동 파악 (일반 대화/검색 전용)
- `_handle_general_chat()`: 일반 대화 처리
- `_handle_search_places()`: RAG 검색 (Retriever 연동)
- 단일 세션·무저장 모드 (Node가 저장/세션 관리)

#### `backend/function_tools.py`
- **Function Calling 도구 정의**
- `SEARCH_PLACES_TOOL`: 장소 검색 함수 (유일한 도구)
- OpenAI Function Calling 스키마

#### `backend/retriever.py`
- PGVector 기반 벡터 검색
- HuggingFace `intfloat/multilingual-e5-small` 임베딩
- Query Expansion 통합
- 연결 풀 관리

#### `backend/query_expansion.py`
- JSON 설정 파일 로드 (`config/query_expansion.json`)
- 쿼리 변형 생성 (구두점 제거, 접미어 추가)
- 변형별 성공/실패 메트릭 추적

#### `backend/rag_chain.py`
- LangChain RetrievalQA 체인 구현
- Retriever → LLM 파이프라인
- Parent context 처리
- 응답 후처리 (출처 추출, 지연시간 계산)

#### `backend/itinerary.py`
- 여행 일정 추천 플래너
- Query Expansion으로 도메인별 후보 수집
- LLM 기반 일정 생성 (GPT-4 Turbo)
- Fallback: Rule-based 일정 생성

#### `backend/schemas.py`
- Pydantic 모델 정의
- RAGQueryRequest/Response
- ItineraryRecommendationRequest/Response
- **ChatRequest**: 통합 채팅 요청 (text)
- **ItineraryStructuredResponse**: Structured Outputs용 스키마 (message + itinerary)
- HealthCheckResponse
- 데이터 검증 및 직렬화

#### `backend/db/connect.py`
- PostgreSQL 연결 풀 관리
- pgvector 확장 지원
- 컨텍스트 매니저 제공

#### `backend/db/init_vector_v1.1.sql`
- tourism_parent/child 테이블 스키마
- pgvector 인덱스 설정
- 메타데이터 컬럼 (domain, area, place_name 등)

#### `backend/utils/logger.py`
- 구조화된 JSON 로깅
- 로그 레벨 설정
- 예외 로깅 헬퍼

### Scripts

#### `scripts/embed_initial_data_v1.1.py`
- 초기 데이터 임베딩 스크립트
- JSON 파일을 읽어 벡터화 후 DB 삽입
- 체크포인트 관리 (중단 후 재개 가능)

#### `scripts/embedding_utils_v1.1.py`
- 임베딩 유틸리티 함수
- HuggingFace 모델 로딩
- 배치 처리

### Tests

#### `tests/test_api.py`
- FastAPI 엔드포인트 통합 테스트
- `/rag/query`, `/health` 테스트

#### `tests/test_itinerary_api.py`
- 여행 일정 추천 API 테스트
- Mock을 사용한 격리 테스트

#### `tests/test_query_expansion.py`
- Query Expansion 로직 단위 테스트
- 변형 생성 검증

#### `tests/test_chat_integration.py`
- 통합 채팅 API 테스트
- Mock을 사용한 Function Calling 테스트
- 일반 대화, 장소 검색, 여행 일정 생성 시나리오

#### `tests/test_itinerary_structured.py`
- Structured Outputs 테스트
- JSON 스키마 보장 검증

---

## 테스트

```bash
# 빠른 테스트 (Query Expansion + RAG 후처리 + FastAPI)
python -m pytest tests/test_query_expansion_config.py tests/test_rag.py tests/test_api.py

# 전체 테스트 (15개 테스트 파일, 2분 18초)
python -m pytest

# 테스트 결과 (2025-11-17)
# ✅ 15/15 통과
# - test_api.py: 5 passed (RAG API)
# - test_chat_integration.py: 1 passed (통합 채팅 API)
# - test_itinerary_api.py: 1 passed (여행 일정 API)
# - test_itinerary_structured.py: 1 passed (Structured Outputs)
# - test_query_expansion.py: 1 passed (Query Expansion)
# - test_query_expansion_config.py: 1 passed (JSON 설정)
# - test_rag.py: 1 passed (RAG 체인)
# - test_unified_chat.py: 3 passed (UnifiedChatHandler)
```

테스트는 실제 DB/Redis 없이 Mock을 사용해 동작하도록 구성되어 있습니다.  
**CI/CD 파이프라인**: GitHub Actions에서 pytest 자동 실행 예정.

---

## API 엔드포인트

### 1. 통합 채팅 ✨ NEW (2025-11-17)
**POST /chat**
- **요청**: `ChatRequest` (text)
- **응답**: 일반 대화 또는 장소 검색 응답 (response_type 없이 message/places 반환)
- **기능**:
  - Function Calling으로 의도 자동 파악
  - (채팅 기록 저장 필요 시 별도 서비스에서 관리)
  - 이전 대화 컨텍스트 활용
- **예시**:
  ```bash
  # 일반 대화
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"text": "안녕하세요"}'
  
  # 장소 검색
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"text": "서울 맛집 추천해줘"}'
  ```

### 2. RAG 검색 (기존)
**POST /rag/query**
- **요청**: `RAGQueryRequest` (query, top_k, domain, area, expansion 등)
- **응답**: `RAGQueryResponse` (answer, sources, latency_ms, metadata)
- **기능**:
  - Query Expansion으로 쿼리 확장
  - PGVector 벡터 검색
  - LangChain RAG 체인
- **예시**:
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "서울 역사 관광지", "top_k": 5, "domain": "HIS", "area": "서울"}'
```

### 3. 여행 일정 추천
**POST /recommend/itinerary** (또는 **POST /recommend**)
- **요청**: `ItineraryRecommendationRequest` (region, domains, duration_days, themes, budget_level 등)
- **응답**: `ItineraryRecommendationResponse` (itineraries 배열, metadata)
- **기능**:
  - Query Expansion으로 도메인별 후보 수집
  - LLM 기반 일정 생성 (Structured Outputs)
- **예시**:
```bash
  curl -X POST http://localhost:8000/recommend \
    -H "Content-Type: application/json" \
    -d '{"region": "서울", "domains": ["FOOD", "NAT"], "duration_days": 2}'
```

### 4. 헬스 체크
**GET /health**
- **응답**: `HealthCheckResponse` (status, checks, timestamp)
- **검사 항목**:
  - `api`: FastAPI 서버 상태
  - `db`: PostgreSQL + MariaDB 연결
  - `llm`: OpenAI API 키 검증
  - `cache`: Redis 연결 (선택)
- **상태**: `healthy` 또는 `degraded`

---

## 성능 및 운영

### 성능 최적화
- **Redis 캐시**: 동일 쿼리 및 Query Expansion 결과를 TTL 기반으로 캐싱
- **연결 풀**: PostgreSQL/MariaDB 연결 재사용으로 latency 감소
- **Query Expansion**: 최대 변형 수 제한으로 과도한 검색 방지

### 모니터링
- **헬스 체크**: `/health` 엔드포인트로 주요 서비스 상태 점검
- **로깅**: JSON 구조화 로그로 쿼리/응답/에러 추적
- **메트릭**: Query Expansion 성공/실패 지표 로깅

### Troubleshooting
- **캐시 미사용**: `REDIS_URL`을 비워두면 자동으로 캐시가 비활성화됩니다.
- **Query Expansion 튜닝**: 접미어·구두점·최대 변형 수를 JSON에서 조정하거나, 사용자 요청에 `expansion_variations`를 전달해 실험할 수 있습니다.
- **Parent Context 비활성화**: `/rag/query` 요청에서 `parent_context=false`로 설정하면 parent summary 없이 child chunk만 반환됩니다.

---

## 다음 단계

### 우선순위 1: 성능 최적화
- [ ] Query Expansion latency 개선 (병렬 검색)
- [ ] Redis 캐시 TTL 튜닝
- [ ] LLM 타임아웃 최적화 (현재 30초)

### 우선순위 2: 운영 문서화
- [ ] 배포 가이드 (Docker, Kubernetes)
- [ ] 모니터링 설정 (Prometheus, Grafana)
- [ ] 로그 수집 (ELK Stack)

### 우선순위 3: 프론트엔드 연동
- [ ] Node.js 클라이언트 테스트 (`scripts/node_rag_client.js`)
- [ ] WebSocket 지원 (실시간 대화)
- [ ] 채팅 UI 연동

---

## 참고 문서

더 자세한 정보는 다음 문서를 참고하세요:

- **[FILE_CATALOG.md](docs/FILE_CATALOG.md)**: 전체 파일 구조 및 상세 설명
- **[PROJECT_PLAN.md](docs/PROJECT_PLAN.md)**: 프로젝트 계획 및 아키텍처
- **[IMPLEMENTATION_TRACKER.md](docs/IMPLEMENTATION_TRACKER.md)**: 구현 진행 상황 및 Git 이력
- **[API_INTEGRATION_FOR_NODE.md](docs/API_INTEGRATION_FOR_NODE.md)**: Node.js 연동 가이드
- **[RAG_PIPELINE_ARCHITECTURE.md](docs/RAG_PIPELINE_ARCHITECTURE.md)**: RAG 파이프라인 상세 설계
