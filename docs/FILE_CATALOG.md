# 파일 기능 명세

프로젝트의 모든 코드, 문서, 데이터 파일이 어떤 역할을 맡고 있는지 정리했습니다.  
`labled_data/`처럼 대량의 동형 파일은 패턴 단위로 묶어 설명합니다.

## 루트 · 환경 구성
- `.git/`: Git 버전 이력 및 훅 저장소.
- `.gitignore`: 가상환경·비밀키·캐시 파일 등을 커밋 대상에서 제외.
- `.env.example`: 필수 환경 변수 샘플. OpenAI/DB/Redis 기본값 안내.
- `.env`: 실제 개발용 민감 정보 (.env.example 기반). **Git에 포함하지 않음**.
- `.vscode/settings.json`: VS Code에서 Git 대용량 경고를 숨기는 최소 설정.
- `.venv/`: 로컬 Python 가상환경. 의존성 고립용.
- `.pytest_cache/`: pytest 실행 결과 캐시 디렉토리.
- `.DS_Store`: macOS Finder 메타데이터 (코드와 무관).
- `pyproject.toml`: Poetry 기반 패키지 메타데이터, 의존성, Black/Ruff/Pytest 설정.
- `requirements.txt`: 운영·테스트 서버에서 pip로 설치할 패키지 고정본.
- `pytest.ini`: pytest 기본 옵션(경로, 네이밍, asyncio 모드 등) 선언.
- `docker-compose.yml`: PostgreSQL(pgvector) + Redis 컨테이너 오케스트레이션 템플릿.
  - PostgreSQL: 5432 포트, tourism_db, pgvector 확장
  - Redis: 6379 포트, 캐시용
- `README.md`: FastAPI RAG 백엔드 소개·실행 절차·주요 모듈 요약.

## FastAPI 백엔드 (`backend/`)
- `backend/__init__.py`: 백엔드 모듈을 패키지로 인식시키는 초기화 파일.
- `backend/main.py`: FastAPI 앱 엔트리포인트. lifespan에서 Retriever, UnifiedChatHandler를 lazy-load하고 `/health`, `/rag/query`, `/chat` 라우트를 정의하며 공통 미들웨어·예외 처리 포함.
- `backend/retriever.py`: HuggingFace `multilingual-e5-small` 임베딩 + pgvector 직접 SQL 검색기. 메타데이터 필터링, query expansion, connection pool 관리, Document 변환 책임.
- `backend/query_expansion.py`: Query Expansion 설정 로더와 변형 생성 헬퍼. 구두점 제거·접미어·최대 변형 수를 JSON 설정으로 관리.
- `backend/cache.py`: Redis 캐시 초기화 및 JSON 직렬화 헬퍼. 검색/Query Expansion 결과 TTL 캐싱에 사용.
- `backend/rag_chain.py`: LangChain `RetrievalQA` 체인 생성 및 결과 후처리 로직. 일본어 프롬프트 템플릿 포함.
- `backend/llm_base.py`: OpenAI ChatCompletion(동기·비동기) 래퍼. 타임아웃(30초)·에러 로그·API 키 로딩 처리. generate_structured() 메서드로 Structured Outputs 지원 (gpt-4o-mini 기본).
- `backend/schemas.py`: Pydantic 기반 도메인 Enum과 요청/응답 스키마 정의.
  - RAGQueryRequest/Response: RAG 검색 요청/응답
  - ChatRequest: 통합 채팅 요청 (text 단일 필드)
  - ItineraryDay/Data/StructuredResponse: 여행 일정 Structured Outputs 스키마
  - HealthCheckResponse, ErrorResponse: 헬스체크 및 에러 응답
- `backend/unified_chat.py`: 통합 채팅 핸들러. Function Calling으로 사용자 의도 자동 파악.
  - _handle_general_chat(): 일반 대화 처리
  - _handle_search_places(): RAG 검색 (Retriever 연동, Document → dict 변환)
  - _handle_create_itinerary(): 여행 일정 생성 (Structured Outputs 사용)
  - handle_chat(): 메인 처리 로직 (Function Calling 자동 감지 및 실행)
- `backend/function_tools.py`: Function Calling 도구 정의.
  - search_places: 장소 검색 함수 스키마
  - create_itinerary: 여행 일정 생성 함수 스키마
  - ALL_TOOLS: OpenAI Function Calling에 전달할 도구 목록
- `backend/itinerary.py`: ItineraryPlanner 클래스. 여행 일정 생성 로직 (현재는 UnifiedChatHandler에서 직접 LLMClient 사용).

### 데이터베이스 패키지 (`backend/db/`)
- `backend/db/__init__.py`: DB 하위 패키지 초기화.
- `backend/db/connect.py`: psycopg ConnectionPool 래퍼 `DatabaseConnection`. 재시도·스키마 검사·SQL 스크립트 실행·싱글톤 인스턴스 제공.
- `backend/db/init_vector.sql`: v1.0 단일 `tourism_data` 스키마 정의 SQL (deprecated).
- `backend/db/init_vector_v1.1.sql`: v1.1 Parent/Child 테이블, 확장 메타데이터, 인덱스 및 pgvector 설정 SQL.
  - tourism_parent: 문서 요약 테이블 (parent_id, summary, embedding_summary, metadata)
  - tourism_child: QA 청크 테이블 (child_id, parent_id FK, question, answer, embedding_qa, metadata)
  - IVFFlat 인덱스 (lists=1500, 코사인 거리)
- (제거됨) `backend/db/init_chat_history.sql`: MariaDB chat_history 테이블 스키마는 Node 관리로 대체

### 유틸리티 (`backend/utils/`)
- `backend/utils/__init__.py`: 유틸 패키지 초기화.
- `backend/utils/logger.py`: JSON 형식 로거 설정(`setup_logger`)과 구조화된 예외 로깅 헬퍼(`log_exception`).

## 문서 (`docs/`)
- `docs/README.md`: 문서 허브. 각 계획/아키텍처 문서 링크와 버전 히스토리 제공.
- `docs/CURRENT_STATUS.md`: 최신 구현 현황, 다음 작업 계획, 성능 지표, 데이터 현황 요약. 통합 채팅 시스템 테스트 결과 (15/15 통과) 반영.
- `docs/PROJECT_PLAN.md`: 전체 프로젝트 목표, 마일스톤, 체크리스트 상세 버전.
- `docs/IMPLEMENTATION_TRACKER.md`: 날짜별 구현 사항, 의사결정 로그, To-Do. 
  - Step 8: 통합 채팅 시스템 구현 완료 체크리스트
  - Step 9: 문서화 정리 진행 상황
  - 2025-11-17 진행 내역: TDD Red-Green-Refactor 사이클, 테스트 결과, API 문서화
- `docs/RAG_PIPELINE_ARCHITECTURE.md`: 시스템 구성도, 데이터 플로우, 개선안.
- `docs/EMBEDDING_PLAN.md`: 임베딩 모델 비교, 파이프라인, 배치 전략, 체크포인트 정책.
- `docs/API_INTEGRATION_FOR_NODE.md`: Node.js 팀을 위한 API 연동 가이드.
  - **POST /chat**: 통합 채팅 엔드포인트 (일반 대화 + RAG 검색 + 여행 일정)
  - **POST /rag/query**: RAG 검색 전용 엔드포인트
  - response_type별 응답 스키마 (chat, search, itinerary, error)
  - curl 및 Node.js fetch 예제
  - 비교표 (/chat vs /rag/query)
- `docs/openapi_rag.yaml`: OpenAPI 3.0 명세. `/rag/query` 요청/응답 스키마와 예시.
- `docs/FILE_CATALOG.md`: 본 문서. 파일별 책임·역할 관리.
- `docs/ITINERARY_RECOMMENDATION.md`: 여행 일정 추천 API 사양. 입력/응답 스키마, 처리 플로우, TODO 정리.
- `docs/REDIS_CACHE_GUIDE.md`: Redis 캐시 동작 방식, 환경 변수, 모니터링 지표, 장애 대응 가이드.
- `docs/readme!!!!.md`: TDD 원칙 및 제약사항. Kent Beck의 Red-Green-Refactor 사이클, Tidy First 원칙.

## 데이터 소스 (`labled_data/`)
- `labled_data/TL_FOOD/J_FOOD_*.json`: 음식점/맛집 데이터. 일본어 설명 + 메타데이터. 임베딩 입력으로 사용.
- `labled_data/TL_HIS/J_HIS_*.json`: 역사·문화 관광지 원본 JSON.
- `labled_data/TL_NAT/J_NAT_*.json`: 자연 관광지/국립공원 데이터.
- `labled_data/TL_SHOP/J_SHOP_*.json`: 쇼핑·상업 지역 데이터.
- `labled_data/TL_LEI/J_LEI_*.json`: 레저·체험 항목 데이터.
- `labled_data/TL_STAY/J_STAY_*.json`: 숙박 시설/온천/호텔 데이터.
- 각 JSON은 1 레코드=1 객체 구조이며, `scripts/embed_*.py`가 제목/본문/도메인을 읽어 DB parent-child 테이블에 적재한다.

## 임베딩 · 운영 스크립트 (`scripts/`)
- `scripts/embedding_utils.py`: v1.0 데이터 정규화 및 텍스트 전처리 헬퍼 (deprecated).
- `scripts/embed_initial_data.py`: OpenAI 임베딩 모델을 사용해 초기 데이터셋을 vector DB에 적재 (deprecated).
- `scripts/embedding_utils_v1.1.py`: parent/child 청크 생성, 요약, 질문/답변 페어링 로직. 
  - 문서 요약 생성 (summary)
  - QA 청크 생성 (평균 5.8개/문서)
  - 메타데이터 9+개 필드 추출
- `scripts/embed_initial_data_v1.1.py`: HuggingFace e5-small 기반 배치 임베딩 파이프라인. 
  - 체크포인트 기반 재시작 지원
  - M4 GPU (MPS) 가속 지원
  - 실시간 진행률 로깅
  - 377,263 parents + 2,202,565 children 임베딩 완료 (2시간 54분)
- `scripts/embedding_checkpoint_v1.1.json`: v1.1 임베딩 진행률/중단 지점 기록.
- `scripts/monitor_embedding.sh`: 임베딩 로그 tail + 진행률 모니터링 스크립트.
- `scripts/watch_progress.sh`: 배치 수행 중 시스템 상태를 주기적으로 출력.
- `scripts/node_rag_client.js`: Node 환경에서 API 호출을 검증하는 샘플 클라이언트.
  - chat() 함수: POST /chat 호출 (통합 채팅)
  - queryRag() 함수: POST /rag/query 호출 (RAG 검색)
  - CLI 모드 지원: `node scripts/node_rag_client.js chat "질문"`

## 구성 파일 (`config/`)
- `config/query_expansion.json`: Query Expansion 접미어, 구두점, 최대 변형 수를 정의하는 기본 설정(환경 변수 `QUERY_EXPANSION_CONFIG_PATH`로 교체 가능).

## 수동 진단 스크립트 (루트)
- `test_db_connection.py`: `DatabaseConnection`으로 pgvector 확장/스키마/행 수를 확인하는 콘솔 유틸.
- `test_retriever_v1.1.py`: 실제 DB와 연결해 일본어 쿼리 3건을 수행, chunk/metadata를 출력.
- `test_step1_filtering.py`: domain/area 필터 시나리오를 단계별로 실행하며 메타데이터 검증.

## 자동 테스트 (`tests/`)
- `tests/conftest.py`: pytest 설정. python-dotenv로 .env 파일 자동 로드.
- `tests/test_api.py`: FastAPI 건강검진·RAG 엔드포인트 존재 여부를 검증하는 틀(실제 client 주석 처리됨).
- `tests/test_api_integration.py`: `TestClient`로 `/rag/query`를 호출하여 필터/expansion/validation/지연시간을 통합 검증.
- `tests/test_connection_pool.py`: `Retriever`의 psycopg connection pool 동작, 컨텍스트 매니저, 수동 close 시나리오를 검증.
- `tests/test_embedding_injection.py`: Mock embeddings 주입을 통해 `Retriever` 의존성 역전 및 expansion 시나리오를 테스트.
- `tests/test_parent_context.py`: 검색 결과가 parent summary 메타데이터를 포함하는지 확인(실 DB 필요).
- `tests/test_query_expansion.py`: expansion on/off 결과 차이와 문서 유니크 수 증가 여부 확인.
- `tests/test_rag.py`: `process_rag_response()` 후처리를 실제 코드로 검증(중복 출처 제거, Unknown 처리, retrieved_count 확인).
- `tests/test_query_expansion_config.py`: Query Expansion JSON 설정이 suffix/punctuation/max_variations를 올바르게 반영하는지 단위 테스트.
- `tests/test_retriever_unit.py`: `_embed_query`, `_build_sql_and_params`, `_rows_to_documents` 등 내부 헬퍼 함수의 세부 검증.
- `tests/test_similarity_calculation.py`: distance/similarity 필드 정합성, 정렬 순서, expansion 시 일관성 검증.
- `tests/test_itinerary_structured.py`: Structured Outputs 테스트. **3/3 PASSED ✅**
  - test_generate_structured_returns_pydantic_model: Pydantic 모델 반환 검증
  - test_structured_response_always_valid_json: 2번 반복 실행 (100% JSON 보장)
  - test_structured_output_has_greeting_message: 인사 메시지 포함 검증
- `tests/test_chat_integration.py`: 통합 채팅 API 테스트. **4/4 PASSED ✅** (response_type 제거 버전)
  - test_chat_endpoint_general_conversation: POST /chat 일반 대화
  - test_chat_endpoint_search_places: POST /chat RAG 검색
  - test_chat_endpoint_create_itinerary: POST /chat 여행 일정
  - test_chat_endpoint_invalid_request: 잘못된 요청 검증
- `tests/test_response_fixtures.py`: 테스트용 응답 fixture 정의.

## 기타 메타 파일
- `labled_data/` 외부의 `test_db_connection.py`, `test_retriever_v1.1.py`, `test_step1_filtering.py`는 위 수동 진단 섹션을 참고.
- `README.md`·`docs/`·`openapi_rag.yaml`은 API 사용자용 문서 세트.
- 인프라/개발 편의를 위한 숨김 파일(`.DS_Store`, `.pytest_cache/`, `.venv/`, `.vscode/`)은 코드 실행에는 영향이 없으며 필요 시 안전하게 삭제 가능.

---

## 핵심 기능별 파일 매핑

### 1. RAG v1.1 Parent-Child 검색
- **스키마**: `backend/db/init_vector_v1.1.sql`
- **임베딩**: `scripts/embed_initial_data_v1.1.py`, `scripts/embedding_utils_v1.1.py`
- **검색 엔진**: `backend/retriever.py`
- **Query Expansion**: `backend/query_expansion.py`, `config/query_expansion.json`
- **캐시**: `backend/cache.py`
- **테스트**: `tests/test_retriever_unit.py`, `tests/test_parent_context.py`, `tests/test_query_expansion.py`

### 2. 통합 채팅 시스템 (Function Calling)
- **통합 핸들러**: `backend/unified_chat.py`
- **Function 정의**: `backend/function_tools.py`
- **Structured Outputs**: `backend/llm_base.py` (generate_structured)
- **스키마**: `backend/schemas.py` (ChatRequest, ItineraryStructuredResponse)
- **API**: `backend/main.py` (POST /chat)
- **세션/저장**: Node에서 관리 (백엔드는 응답만 반환)
- **테스트**: `tests/test_itinerary_structured.py`, `tests/test_chat_integration.py`

### 3. RAG 검색 전용 (고급 제어)
- **API**: `backend/main.py` (POST /rag/query)
- **체인**: `backend/rag_chain.py`
- **스키마**: `backend/schemas.py` (RAGQueryRequest/Response)
- **테스트**: `tests/test_api_integration.py`, `tests/test_rag.py`

### 4. 프론트엔드 연동
- **API 문서**: `docs/API_INTEGRATION_FOR_NODE.md`
- **OpenAPI 스펙**: `docs/openapi_rag.yaml`
- **Node.js 클라이언트**: `scripts/node_rag_client.js`

---

## 테스트 현황 (2025-11-17)

**총 15/15 테스트 통과** (2분 18초)

| 테스트 파일 | 통과 | 설명 |
|------------|------|------|
| test_itinerary_structured.py | 3/3 ✅ | Structured Outputs |
| test_chat_integration.py | 4/4 ✅ | POST /chat API |

---

필요 시 새 파일 추가 시 본 문서를 함께 업데이트해 파일 책임을 지속적으로 추적하세요.

**최종 업데이트**: 2025-11-17  
**상태**: 통합 채팅 시스템 구현 완료 ✅
