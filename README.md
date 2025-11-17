# FastAPI RAG Backend

한국 관광 정보를 일본어로 제공하는 Retrieval-Augmented Generation 백엔드입니다. FastAPI와 PostgreSQL(pgvector)을 기반으로 parent-child 청크 구조, Query Expansion, Redis 캐시를 활용해 빠르고 정확한 응답을 제공합니다.

---

## 주요 기능

- **LangChain 기반 RAG 체인**: Retriever → LLM 체인으로 답변·출처·지연시간을 반환.
- **Parent/Child QA 스키마**: tourism_parent/child 테이블에 풍부한 메타데이터를 저장해 domain/area 필터링 지원.
- **Query Expansion**: JSON 설정 파일로 구두점 제거·접미어·사용자 변형을 관리하고, 변형별 성공/실패 지표를 로깅.
- **여행 일정 추천**: Query Expansion + LLM 기반으로 지역/도메인/테마에 맞는 맞춤형 여행 일정을 자동 생성.
- **통합 채팅 시스템**: Function Calling으로 일반 대화, RAG 검색, 여행 일정 생성을 하나의 엔드포인트로 통합.
- **Structured Outputs**: 100% JSON 보장으로 파싱 오류 제거.
- **대화 기록 관리**: MariaDB에 채팅 기록을 영구 저장하고 컨텍스트 관리.
- **Redis 캐시**: 동일 쿼리/Query Expansion 결과를 TTL 기반으로 캐싱해 응답 속도 향상 (옵션).
- **헬스 체크**: `/health` 엔드포인트에서 API/DB/LLM/Redis 상태를 보고하고 degraded 상태 감지.
- **테스트 스위트**: FastAPI TestClient 기반 통합 테스트와 Query Expansion/RAG 후처리 단위 테스트 포함.

---

## 기술 스택

| 영역 | 사용 기술 |
| --- | --- |
| Backend | FastAPI 0.109.x, Python 3.11 |
| Database | PostgreSQL 15 + pgvector, MariaDB 10.11 |
| LLM & 임베딩 | OpenAI GPT-4 Turbo, HuggingFace `intfloat/multilingual-e5-small` |
| 캐시 | Redis 5.x (옵션) |
| 테스트/품질 | pytest, httpx, black, ruff |

---

## 디렉터리 개요

```
backend/
  cache.py              # Redis 캐시 유틸
  main.py               # FastAPI 엔트리포인트
  retriever.py          # PGVector 쿼리 + Query Expansion + 캐시
  query_expansion.py    # 설정 로드 + 변형 생성 헬퍼
  rag_chain.py          # LangChain RetrievalQA 체인
  llm_base.py           # OpenAI LLM 래퍼 (Structured Outputs 포함)
  itinerary.py          # 여행 일정 추천 플래너 (Query Expansion + LLM)
  unified_chat.py       # 통합 채팅 핸들러 (Function Calling)
  chat_history.py       # MariaDB 채팅 기록 관리
  function_tools.py     # Function Calling 도구 정의
  schemas.py            # Pydantic 모델
  db/                   # ConnectionPool 및 스키마 스크립트
    init_vector_v1.1.sql       # PostgreSQL 벡터 DB 스키마
    init_chat_history.sql      # MariaDB 채팅 기록 스키마
  utils/logger.py       # JSON 로깅 헬퍼
config/
  query_expansion.json  # Query Expansion 기본 설정
docs/                   # 파일/계획/상태 문서
scripts/                # 임베딩 및 운영 스크립트
tests/                  # FastAPI/Query Expansion/RAG 테스트
```

---

## 사전 준비

- Python 3.11
- PostgreSQL 15 + pgvector (Docker Compose로 실행 가능)
- MariaDB 10.11+ (채팅 기록 저장용)
- Redis (선택 사항 · 캐시 사용 시)

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

# 4) DB/Redis (Docker) 실행
docker-compose up -d

# 5) FastAPI 서버 실행
uvicorn backend.main:app --reload
```

---

## 환경 변수

| 키 | 설명 |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI ChatCompletion/Embedding 키 |
| `OPENAI_MODEL` | LLM 모델명(기본: `gpt-4-turbo`) |
| `DATABASE_URL` | PostgreSQL 접속 URL |
| `MARIADB_HOST` | MariaDB 호스트 (기본: localhost) |
| `MARIADB_PORT` | MariaDB 포트 (기본: 3306) |
| `MARIADB_USER` | MariaDB 사용자명 |
| `MARIADB_PASSWORD` | MariaDB 비밀번호 |
| `MARIADB_DATABASE` | MariaDB 데이터베이스 이름 |
| `REDIS_URL` | Redis 접속 URL (없으면 캐시 비활성화) |
| `REDIS_TTL` | 캐시 TTL(초, 기본 300) |
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
- **통합 채팅 핸들러**: Function Calling으로 사용자 의도 자동 파악
- `_handle_general_chat()`: 일반 대화 처리
- `_handle_search_places()`: RAG 검색 (Retriever 연동)
- `_handle_create_itinerary()`: 여행 일정 생성 (Structured Outputs 사용)
- 대화 기록 관리 및 컨텍스트 포함

#### `backend/chat_history.py`
- **ChatHistoryManager**: MariaDB 채팅 기록 관리
- `save_message()`: 대화 저장 (JSON → LONGTEXT)
- `get_history()`: 세션 전체 기록 조회
- `get_recent_context()`: 최근 N개 컨텍스트 (LLM 프롬프트용)
- `delete_session()`: 세션 삭제

#### `backend/function_tools.py`
- **Function Calling 도구 정의**
- `SEARCH_PLACES_TOOL`: 장소 검색 함수
- `CREATE_ITINERARY_TOOL`: 여행 일정 생성 함수
- OpenAI Function Calling 스키마

#### `backend/retriever.py`
- PGVector 기반 벡터 검색
- HuggingFace `intfloat/multilingual-e5-small` 임베딩
- Query Expansion 통합
- Redis 캐시 연동
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
- **ChatRequest**: 통합 채팅 요청 (text, session_id)
- **ItineraryStructuredResponse**: Structured Outputs용 스키마 (message + itinerary)
- HealthCheckResponse
- 데이터 검증 및 직렬화

#### `backend/cache.py`
- Redis 캐시 유틸리티
- TTL 기반 캐싱
- 환경변수로 활성화/비활성화

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

#### `tests/test_chat_history.py`
- ChatHistoryManager 단위 테스트
- MariaDB 저장/조회 검증

#### `tests/test_itinerary_structured.py`
- Structured Outputs 테스트
- JSON 스키마 보장 검증

#### `tests/test_unified_chat.py`
- UnifiedChatHandler 통합 테스트
- Function Calling 의도 파악 검증

---

## 테스트

```bash
# 빠른 테스트 (Query Expansion + RAG 후처리 + FastAPI)
python -m pytest tests/test_query_expansion_config.py tests/test_rag.py tests/test_api.py

# 전체 테스트
python -m pytest
```

테스트는 실제 DB/Redis 없이 Mock을 사용해 동작하도록 구성되어 있습니다.

---

## API 엔드포인트

### 통합 채팅 (신규)
- **POST /chat**
  - 요청 body: `ChatRequest` (text, session_id)
  - 응답: 사용자 의도에 따라 다름
    - **일반 대화**: `{"response_type": "chat", "message": "..."}`
    - **장소 검색**: `{"response_type": "search", "message": "...", "places": [...]}`
    - **여행 일정**: `{"response_type": "itinerary", "message": "...", "itinerary": {...}}`
  - Function Calling으로 의도 자동 파악
  - 대화 기록 자동 저장 (MariaDB)
  - 이전 컨텍스트 포함

### RAG 쿼리
- **POST /rag/query**
  - 요청 body: `RAGQueryRequest` (query, top_k, domain, area, expansion 등)
  - 응답: `RAGQueryResponse` (answer, sources, latency_ms, metadata)
  - Query Expansion 활성화 시 확장된 쿼리로 검색 수행

### 여행 일정 추천
- **POST /recommend/itinerary**
  - 요청 body: `ItineraryRecommendationRequest` (region, domains, duration_days, themes, budget_level 등)
  - 응답: `ItineraryRecommendationResponse` (itineraries 배열, metadata)
  - Query Expansion + LLM으로 맞춤형 여행 일정 생성

### 헬스 체크
- **GET /health**
  - 응답: `HealthCheckResponse` (status, checks, timestamp)
  - API, DB, LLM, Redis 상태 점검

---

## 헬스 체크

- `GET /health`
- `checks` 항목에 `api`, `db`, `llm`, `cache`를 포함하며, 미구성 또는 오류 시 `missing`/`error`로 표기합니다.
- `status`는 `healthy` 또는 `degraded`로 구분됩니다.

---

## troubleshooting

- **캐시 미사용**: `REDIS_URL`을 비워두면 자동으로 캐시가 비활성화됩니다.
- **Query Expansion 튜닝**: 접미어·구두점·최대 변형 수를 JSON에서 조정하거나, 사용자 요청에 `expansion_variations`를 전달해 실험할 수 있습니다.
- **Parent Context 비활성화**: `/rag/query` 요청에서 `parent_context=false`로 설정하면 parent summary 없이 child chunk만 반환됩니다.

더 자세한 정보는 `docs/FILE_CATALOG.md`, `docs/PROJECT_PLAN.md`를 참고하세요.
