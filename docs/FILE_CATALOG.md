# 파일 기능 명세

프로젝트의 모든 코드, 문서, 데이터 파일이 어떤 역할을 맡고 있는지 정리했습니다.  
`labled_data/`처럼 대량의 동형 파일은 패턴 단위로 묶어 설명합니다.

## 루트 · 환경 구성
- `.git/`: Git 버전 이력 및 훅 저장소.
- `.gitignore`: 가상환경·비밀키·캐시 파일 등을 커밋 대상에서 제외.
- `.env.example`: 필수 환경 변수 샘플. OpenAI/DB/Redis/성능 제한 등 기본값 안내.
- `.env.local`: 실제 개발용 민감 정보(.env.example를 기반으로 커스터마이징). Git에 포함되지만 값은 공유 금지.
- `.vscode/settings.json`: VS Code에서 Git 대용량 경고를 숨기는 최소 설정.
- `.venv/`: 로컬 Python 가상환경. 의존성 고립용.
- `.pytest_cache/`: pytest 실행 결과 캐시 디렉토리.
- `.DS_Store`: macOS Finder 메타데이터 (코드와 무관).
- `pyproject.toml`: Poetry 기반 패키지 메타데이터, 의존성, Black/Ruff/Pytest 설정.
- `requirements.txt`: 운영·테스트 서버에서 pip로 설치할 패키지 고정본.
- `pytest.ini`: pytest 기본 옵션(경로, 네이밍, asyncio 모드 등) 선언.
- `docker-compose.yml`: PostgreSQL(pgvector)·Redis 컨테이너 오케스트레이션 템플릿.
- `readme.md`: FastAPI RAG 백엔드 소개·실행 절차·주요 모듈 요약(현재 중복 문구 존재).

## FastAPI 백엔드 (`backend/`)
- `backend/__init__.py`: 백엔드 모듈을 패키지로 인식시키는 초기화 파일.
- `backend/main.py`: FastAPI 앱 엔트리포인트. lifespan에서 Retriever와 UnifiedChatHandler를 lazy-load하고 `/health`, `/rag/query`, `/chat` 라우트를 정의하며 공통 미들웨어·예외 처리 포함.
- `backend/retriever.py`: HuggingFace `multilingual-e5-small` 임베딩 + pgvector 직접 SQL 검색기. 메타데이터 필터링, query expansion, connection pool 관리, Document 변환 책임.
- `backend/query_expansion.py`: Query Expansion 설정 로더와 변형 생성 헬퍼. 구두점 제거·접미어·최대 변형 수를 JSON 설정으로 관리.
- `backend/cache.py`: Redis 캐시 초기화 및 JSON 직렬화 헬퍼. 검색/Query Expansion 결과 TTL 캐싱에 사용.
- `backend/rag_chain.py`: LangChain `RetrievalQA` 체인 생성 및 결과 후처리 로직. 일본어 프롬프트 템플릿 포함.
- `backend/llm_base.py`: OpenAI ChatCompletion(동기·비동기) 래퍼. 타임아웃·에러 로그·API 키 로딩 처리. generate_structured() 메서드로 Structured Outputs 지원.
- `backend/schemas.py`: Pydantic 기반 도메인 Enum과 RAGQueryRequest/Response, HealthCheckResponse, ErrorResponse 정의 및 검증기 포함. ItineraryDay, ItineraryData, ItineraryStructuredResponse, ChatRequest 스키마 추가.
- `backend/chat_history.py`: MariaDB 채팅 기록 관리자. JSON을 LONGTEXT로 저장/조회. save_message(), get_history(), get_recent_context(), delete_session() 메서드 제공.
- `backend/unified_chat.py`: 통합 채팅 핸들러. Function Calling으로 사용자 의도 자동 파악. _handle_general_chat(), _handle_search_places(), _handle_create_itinerary() 메서드.
- `backend/function_tools.py`: Function Calling 도구 정의. get_itinerary_recommendation 함수 및 OpenAI Function Calling 스키마.

### 데이터베이스 패키지 (`backend/db/`)
- `backend/db/__init__.py`: DB 하위 패키지 초기화.
- `backend/db/connect.py`: psycopg ConnectionPool 래퍼 `DatabaseConnection`. 재시도·스키마 검사·SQL 스크립트 실행·싱글톤 인스턴스 제공.
- `backend/db/init_vector.sql`: v1.0 단일 `tourism_data` 스키마 정의 SQL.
- `backend/db/init_vector_v1.1.sql`: v1.1 Parent/Child 테이블, 확장 메타데이터, 인덱스 및 pgvector 설정 SQL.
- `backend/db/init_chat_history.sql`: MariaDB chat_history 테이블 스키마. session_id, turn, role, content, metadata, created_at 컬럼 및 복합 인덱스.

### 유틸리티 (`backend/utils/`)
- `backend/utils/__init__.py`: 유틸 패키지 초기화.
- `backend/utils/logger.py`: JSON 형식 로거 설정(`setup_logger`)과 구조화된 예외 로깅 헬퍼(`log_exception`).

## 문서 (`docs/`)
- `docs/README.md`: 문서 허브. 각 계획/아키텍처 문서 링크와 버전 히스토리 제공.
- `docs/CURRENT_STATUS.md`: 최신 구현 현황, 다음 작업 계획, 성능 지표, 데이터 현황 요약.
- `docs/PROJECT_PLAN.md`: 전체 프로젝트 목표, 마일스톤, 체크리스트 상세 버전.
- `docs/IMPLEMENTATION_TRACKER.md`: 날짜별 구현 사항, 의사결정 로그, To-Do. 통합 채팅 시스템 구현 내역 포함.
- `docs/RAG_PIPELINE_ARCHITECTURE.md`: 시스템 구성도, 데이터 플로우, 개선안.
- `docs/EMBEDDING_PLAN.md`: 임베딩 모델 비교, 파이프라인, 배치 전략, 체크포인트 정책.
- `docs/API_INTEGRATION_FOR_NODE.md`: Node.js 게이트웨이 팀을 위한 `/rag/query` 연동 가이드(curl·fetch 예시, expansion/parent_context 옵션 설명).
- `docs/openapi_rag.yaml`: OpenAPI 3.0 명세. `/rag/query` 요청/응답 스키마와 예시.
- `docs/FILE_CATALOG.md`: 본 문서. 파일별 책임·역할 관리.
- `docs/ITINERARY_RECOMMENDATION.md`: 여행 일정 추천 API 사양. 입력/응답 스키마, 처리 플로우, TODO 정리.
- `docs/REDIS_CACHE_GUIDE.md`: Redis 캐시 동작 방식, 환경 변수, 모니터링 지표, 장애 대응 가이드.

## 데이터 소스 (`labled_data/`)
- `labled_data/TL_FOOD/J_FOOD_*.json`: 음식점/맛집 데이터. 일본어 설명 + 메타데이터. 임베딩 입력으로 사용.
- `labled_data/TL_HIS/J_HIS_*.json`: 역사·문화 관광지 원본 JSON.
- `labled_data/TL_NAT/J_NAT_*.json`: 자연 관광지/국립공원 데이터.
- `labled_data/TL_SHOP/J_SHOP_*.json`: 쇼핑·상업 지역 데이터.
- `labled_data/TL_LEI/J_LEI_*.json`: 레저·체험 항목 데이터.
- `labled_data/TL_STAY/J_STAY_*.json`: 숙박 시설/온천/호텔 데이터.
- 각 JSON은 1 레코드=1 객체 구조이며, `scripts/embed_*.py`가 제목/본문/도메인을 읽어 DB parent-child 테이블에 적재한다.

## 임베딩 · 운영 스크립트 (`scripts/`)
- `scripts/embedding_utils.py`: v1.0 데이터 정규화 및 텍스트 전처리 헬퍼.
- `scripts/embed_initial_data.py`: OpenAI 임베딩 모델을 사용해 초기 데이터셋을 vector DB에 적재.
- `scripts/embedding_utils_v1.1.py`: parent/child 청크 생성, 요약, 질문/답변 페어링 로직.
- `scripts/embed_initial_data_v1.1.py`: HuggingFace e5-small 기반 배치 임베딩 파이프라인. 체크포인트·MPS 지원.
- `scripts/embedding_checkpoint_v1.1.json`: v1.1 임베딩 진행률/중단 지점 기록.
- `scripts/monitor_embedding.sh`: 임베딩 로그 tail + 진행률 모니터링 스크립트.
- `scripts/watch_progress.sh`: 배치 수행 중 시스템 상태를 주기적으로 출력.
- `scripts/node_rag_client.js`: Node 환경에서 `/rag/query` 호출을 검증하는 샘플 클라이언트.

## 구성 파일 (`config/`)
- `config/query_expansion.json`: Query Expansion 접미어, 구두점, 최대 변형 수를 정의하는 기본 설정(환경 변수 `QUERY_EXPANSION_CONFIG_PATH`로 교체 가능).

## 수동 진단 스크립트 (루트)
- `test_db_connection.py`: `DatabaseConnection`으로 pgvector 확장/스키마/행 수를 확인하는 콘솔 유틸.
- `test_retriever_v1.1.py`: 실제 DB와 연결해 일본어 쿼리 3건을 수행, chunk/metadata를 출력.
- `test_step1_filtering.py`: domain/area 필터 시나리오를 단계별로 실행하며 메타데이터 검증.

## 자동 테스트 (`tests/`)
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
- `tests/test_chat_history.py`: ChatHistoryManager의 MariaDB 저장/조회 테스트. 메시지 저장, 최근 컨텍스트 조회, 세션 삭제 검증.
- `tests/test_itinerary_structured.py`: Structured Outputs 테스트. ItineraryStructuredResponse 파싱 및 generate_structured() 메서드 검증.
- `tests/test_unified_chat.py`: UnifiedChatHandler 테스트. 일반 대화, Function Calling 플로우, 채팅 기록 통합 검증.
- `tests/test_chat_integration.py`: 통합 채팅 API 테스트. /chat 엔드포인트의 일반 대화 + Function Calling 전체 플로우 검증.

## 기타 메타 파일
- `labled_data/` 외부의 `test_db_connection.py`, `test_retriever_v1.1.py`, `test_step1_filtering.py`는 위 수동 진단 섹션을 참고.
- `README.md`·`docs/`·`openapi_rag.yaml`은 API 사용자용 문서 세트.
- 인프라/개발 편의를 위한 숨김 파일(`.DS_Store`, `.pytest_cache/`, `.venv/`, `.vscode/`)은 코드 실행에는 영향이 없으며 필요 시 안전하게 삭제 가능.

필요 시 새 파일 추가 시 본 문서를 함께 업데이트해 파일 책임을 지속적으로 추적하세요.
- ## 구성 파일 (`config/`)
- `config/query_expansion.json`: Query Expansion 접미어, 구두점, 최대 변형 수를 정의하는 기본 설정. 환경 변수 `QUERY_EXPANSION_CONFIG_PATH`로 교체 가능.
- 
