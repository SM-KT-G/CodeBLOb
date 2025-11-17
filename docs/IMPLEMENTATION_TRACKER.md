# FastAPI RAG 백엔드 구현 체크리스트

> 바이브 코딩 진행 상황을 명확히 공유하기 위한 전용 체크 문서입니다.  
> 항목 완료 시 `- [x]`로 표시하고, 필요 시 날짜/메모 추가하세요.

## Step 0. 킥오프 & 환경 세팅
- [x] `.venv` 생성 및 Python 3.10.19 확인 (명령과 결과 기록)
- [x] 패키지 매니저 확정 및 `pyproject.toml`/`requirements.txt` 초안 작성
- [x] `.env.example` 작성 (필수 환경 변수 명시)
- [x] IDE 설정, 린터/포맷터 구성 완료 (black, ruff 설치 완료)

## Step 1. 프로젝트 스켈레톤 구성
- [x] `backend/` 디렉토리 및 기본 구조 생성
- [x] 핵심 모듈 파일( `main.py`, `schemas.py`, `retriever.py`, `llm_base.py`, `rag_chain.py` ) 생성
- [x] FastAPI 기본 앱 구동 및 `/health` 라우트 구현
- [x] `.env` 누락 검증 로직 추가

## Step 2. 데이터베이스 & 벡터 인프라
- [x] `db/connect.py`에 커넥션 풀 + 재시도 로직 구현
- [x] `init_vector.sql` 작성 및 ENUM/domain 포함 스키마 정의 (2025-11-05)
- [x] Docker Compose로 PostgreSQL + Redis 설정 완료 (2025-11-05)
- [x] 로컬 PostgreSQL 충돌 해결 및 Docker DB 연결 테스트 성공 (2025-11-05)
- [x] pgvector 확장 설치 및 스키마 초기화 확인 (2025-11-05)
- [x] DB 예외 처리에 `log_exception()` 연동 (2025-11-05)
- [x] **벡터 차원 변경: 1536 → 1024** (HuggingFace 모델 사용, 2025-11-06)

## Step 2.5. 임베딩 데이터 준비 (EMBEDDING_PLAN.md 참조)
- [x] `scripts/` 디렉토리 생성 (2025-11-06)
- [x] `scripts/embedding_utils.py` 작성 (JSON 로드, 도메인 매핑, 텍스트 추출) (2025-11-06)
- [x] **임베딩 모델 결정: OpenAI → HuggingFace `intfloat/multilingual-e5-large`** (2025-11-06)
  - 이유: 37만 개 파일에 대해 완전 무료, 일본어 성능 우수, 관광 도메인 강함
  - 비용: OpenAI $1.13 → HuggingFace $0 (100% 절감)
- [x] `requirements.txt`에 `sentence-transformers` 추가 및 설치 (2025-11-06)
- [x] `scripts/embed_initial_data.py` 작성 (HuggingFace 모델 사용) (2025-11-06)
  - 배치 처리 (batch_size=32)
  - 진행 상황 로깅
  - 중복 방지 (document_id 체크)
  - 드라이런 모드 지원
- [x] **v1.0 임베딩 66% 완료 후 아키텍처 결함 발견** (2025-11-07)
  - 문제: Document-level chunking, 메타데이터 부족, 리랭킹 없음
  - 결정: v1.0 중단하고 v1.1 Parent-Child 아키텍처로 재설계

## Step 2.6. v1.1 Parent-Child 아키텍처 구현 (2025-11-07)
- [x] **새 스키마 설계 및 배포** (`init_vector_v1.1.sql`)
  - tourism_parent: 문서 요약 테이블 (parent_id PK)
  - tourism_child: QA 청크 테이블 (child_id PK, parent_id FK)
  - 메타데이터 확장: 2개 → 9+개 필드 (area, place_name, dates, etc.)
- [x] **임베딩 모델 변경**: multilingual-e5-large (1024d) → multilingual-e5-small (384d)
  - 이유: 속도 향상, 메모리 효율, 일본어 성능 유지
- [x] `scripts/embedding_utils_v1.1.py` 작성 (QA 청크 생성 로직)
  - 문서당 평균 5-7개 QA 생성
  - 메타데이터 풍부화 (9+개 필드 추출)
- [x] `scripts/embed_initial_data_v1.1.py` 작성 (Parent-Child 배치 처리)
  - M4 GPU (MPS) 가속 지원
  - 체크포인트 기반 재시작 지원
  - 실시간 진행률 모니터링
- [x] **v1.1 임베딩 완료** (2025-11-07, 2시간 54분)
  - Parents: 377,263개 (100%)
  - Children: 2,202,565개 (평균 5.8개/문서)
  - 속도: 35.97 files/sec
  - IVFFlat 인덱스 생성 완료 (lists=1500)
- [x] DB 검증: 레코드 수, 벡터 차원(384), 도메인 분포 확인 완료
- [x] **Retriever v1.1 구현** (`backend/retriever.py`)
  - 직접 SQL 쿼리 (PGVector <=> 연산자)
  - Parent-Child JOIN으로 메타데이터 결합
  - 유사도 점수 계산 및 정렬
- [x] **검색 테스트 성공** (`test_retriever_v1.1.py`)
  - 일본어 쿼리: ラーメン店, 温泉旅館, 歴史的観光地
  - 평균 유사도: 90%+ (0.90~0.92)
  - 메타데이터 정확도: 100%

## Step 2.7. RAG 품질 개선 (2025-11-07)
- [x] **Step 1: Metadata Filtering 구현**
  - `retriever.search()`에 area 파라미터 추가
  - SQL LIKE 필터링 (area, place_name, title)
  - 테스트 완료: 도메인/지역/복합 필터링 정상 작동
  - 최고 유사도: 0.91 (부산 온천 검색)
- [ ] **Step 2: Query Expansion 구현** (예정)
  - 쿼리 다양화로 재현율 향상
  - 다중 쿼리 결과 병합 및 중복 제거
- [ ] **Step 3: Parent Context 추가** (예정)
  - Parent summary를 Child 결과에 포함
  - 답변 품질 및 맥락 이해도 향상

## Step 3. RAG 구성 요소
- [x] `retriever.py`에서 PGVector + 임베딩 초기화, 입력 검증
- [x] **임베딩 모델 변경: OpenAIEmbeddings → HuggingFaceEmbeddings** (2025-11-06)
  - 모델: `intfloat/multilingual-e5-large` (1024 차원)
  - 일본어 관광 데이터에 최적화
- [x] **v1.1 Retriever 재구현** (2025-11-07)
  - 모델: `intfloat/multilingual-e5-small` (384 차원)
  - 직접 SQL 쿼리 방식 (PGVector <=> 연산자)
  - Parent-Child JOIN으로 풍부한 메타데이터 제공
  - M4 GPU (MPS) 가속 지원
- [x] `llm_base.py` 타임아웃(15초) + 재시도 로직 구현
- [x] `rag_chain.py` PromptTemplate & RetrievalQA 구성
- [x] LangChain/OpenAI 버전 고정 및 의존성 파일 업데이트

## Step 4. API 계약
- [ ] `schemas.py` 요청/응답 모델 작성 (응답 포맷 준수)
- [ ] `/rag/query` 라우터 구현 및 의존성 주입 패턴 적용
- [ ] latency 계산, 소수 둘째 자리 포맷 처리
- [ ] HTTP 200/400/500 에러 핸들러 통합

## Step 5. 로깅·모니터링·캐시
- [ ] `utils/logger.py` 구조화 로깅 & `log_exception` 구현
- [ ] 주요 플로우에 로깅 삽입
- [ ] Redis 캐시 훅(옵션) 인터페이스 초안
- [ ] 메트릭/모니터링 플랜 정리

## Step 6. 테스트 & 품질
- [ ] `tests/test_rag.py` Dummy 기반 단위 테스트
- [ ] `tests/test_api.py` FastAPI TestClient 통합 테스트
- [ ] pytest 설정(`--maxfail=1 --disable-warnings`) 검증
- [ ] 린트/포맷 파이프라인 구성(예: pre-commit)

## Step 7. 배포 준비
- [ ] Dockerfile(Python 3.10, uvicorn 멀티 워커) 작성
- [ ] 헬스체크(`/health`) 및 재시작 정책 문서화
- [ ] CI 파이프라인에 pytest + lint 조건 추가
- [ ] 시크릿/환경 변수 관리 전략 정리

## Step 8. 추천 여행 경로 기능 사전 준비
- [ ] Node/프론트 팀과 API 스펙 협의 (입력/응답 포맷)
- [ ] FastAPI placeholder 라우터/서비스 인터페이스 작성
- [ ] Mock 응답 및 관련 테스트 케이스 추가
- [ ] 데이터 소스 & 알고리즘 후보 조사

---

### 진행 메모
- 2025-11-05: Step 0~3 기본 구현 완료
  - Python 3.10.19 가상환경 설정 완료
  - 모든 필수 패키지 설치 완료 (FastAPI, LangChain, OpenAI, psycopg, pgvector 등)
  - 프로젝트 스켈레톤 구성 완료 (backend/, db/, utils/, tests/ 디렉토리)
  - 핵심 모듈 파일 생성 완료:
    - main.py: FastAPI 앱, /health, /rag/query 엔드포인트
    - schemas.py: Pydantic 모델 (요청/응답 검증)
    - retriever.py: PGVector 기반 문서 검색
    - llm_base.py: OpenAI LLM 클라이언트 (타임아웃, 재시도)
    - rag_chain.py: LangChain RetrievalQA 구성
    - db/connect.py: PostgreSQL 커넥션 풀 관리
    - db/init_vector.sql: pgvector 스키마 초기화
    - utils/logger.py: 구조화 로깅 및 예외 처리
  - FastAPI 서버 로컬 실행 테스트 성공 (http://127.0.0.1:8000)
  - /health 엔드포인트 정상 작동 확인
  - /rag/query Mock 응답 정상 작동 확인
  - Docker Compose로 PostgreSQL + Redis 컨테이너 설정 완료
  - DB 연결 테스트 성공 (로컬 PostgreSQL 충돌 해결)

- 2025-11-06: v1.0 임베딩 시작 및 모델 변경
  - **중요 결정: OpenAI → HuggingFace 로컬 모델로 전환**
    - 이유: 377,265개 파일 처리 시 비용 절감 ($1.13 → $0)
    - 모델: `intfloat/multilingual-e5-large` (일본어 최적화, 1024d)
  - DB 스키마 수정: vector(1536) → vector(1024)
  - Docker 컨테이너 재생성으로 스키마 적용
  - `scripts/embedding_utils.py` 작성 (JSON 처리, 도메인 매핑)
  - `scripts/embed_initial_data.py` 작성 (HuggingFace 배치 처리)
  - `sentence-transformers` 패키지 설치 완료
  - `retriever.py` 임베딩 모델 변경 (OpenAI → HuggingFace)
  - v1.0 임베딩 진행: 220,202/377,265 (66% 완료)

- 2025-11-07 오전: v1.0 → v1.1 아키텍처 전환
  - **아키텍처 결함 발견**:
    - Document-level chunking: 짧은 쿼리에 대응 불가
    - 메타데이터 부족: 2개 필드만 (domain, source_url)
    - 리랭킹 없음: 단순 벡터 유사도만 사용
  - **결정: v1.0 임베딩 중단, v1.1 Parent-Child 아키텍처로 재구축**
  - `init_vector_v1.1.sql` 작성 (Parent-Child 스키마)
  - `embedding_utils_v1.1.py` 작성 (QA 청크 생성 로직)
  - `embed_initial_data_v1.1.py` 작성 (Parent-Child 배치 처리)
  - **모델 변경**: multilingual-e5-large (1024d) → multilingual-e5-small (384d)
    - 이유: 속도 향상, 메모리 효율, 일본어 성능 유지

- 2025-11-07 오후: v1.1 임베딩 완료 및 Retriever 구현
  - **v1.1 임베딩 100% 완료** (2시간 54분)
    - Parents: 377,263개 (문서 요약)
    - Children: 2,202,565개 (QA 청크)
    - 평균: 문서당 5.8개 QA
    - 속도: 35.97 files/sec
    - M4 GPU (MPS) 가속 사용
  - IVFFlat 인덱스 생성 완료 (lists=1500)
  - `retriever.py` v1.1 재구현:
    - 직접 SQL 쿼리 (PGVector <=> 연산자)
    - Parent-Child JOIN으로 메타데이터 풍부화
    - 9+개 필드 제공 (domain, title, area, place_name, dates, etc.)
  - **검색 테스트 성공** (`test_retriever_v1.1.py`)
    - 일본어 쿼리 3개 테스트 (ラーメン店, 温泉旅館, 歴史的観光地)
    - 평균 유사도: 90%+ (0.90~0.92)
    - 메타데이터 정확도: 100%

- 2025-11-07 저녁: RAG 품질 개선 (Step 1)
  - **Metadata Filtering 구현 및 테스트 완료**
    - `retriever.search()`에 area 파라미터 추가
    - SQL WHERE 절에 LIKE 필터링 (area, place_name, title)
    - 테스트 4개 케이스 모두 통과:
      1. 도메인 필터링: food 도메인만 검색 ✅
      2. 지역 필터링: 서울 지역 결과만 ✅
      3. 복합 필터링: 부산 숙박시설만 (유사도 0.91) ✅
      4. 기본 검색: 모든 도메인 검색 ✅
    - 품질 개선 확인: 타겟팅 정확도 향상, 복합 필터 시 최고 유사도 달성

- 2025-XX-XX: **통합 채팅 시스템 구현 (TDD 원칙)**
  - **Structured Outputs 구현**:
    - `backend/schemas.py`: ItineraryDay, ItineraryData, ItineraryStructuredResponse, ChatRequest 추가
    - `backend/llm_base.py`: generate_structured() 메서드 추가 (OpenAI beta.chat.completions.parse 사용)
    - 100% JSON 보장으로 파싱 오류 제거
  - **ChatHistoryManager 구현** (`backend/chat_history.py`):
    - MariaDB에 JSON을 LONGTEXT로 저장 (JSON_VALID CHECK 제약)
    - save_message(), get_history(), get_recent_context(), delete_session() 구현
    - 채팅 기록 영구 저장 및 컨텍스트 관리
  - **UnifiedChatHandler 구현** (`backend/unified_chat.py`):
    - Function Calling으로 사용자 의도 자동 파악
    - _handle_general_chat(): 일반 대화
    - _handle_search_places(): RAG 검색 (Retriever 연동)
    - _handle_create_itinerary(): 여행 일정 생성 (Structured Outputs 사용)
  - **통합 채팅 엔드포인트** (`backend/main.py`):
    - POST /chat 엔드포인트 추가
    - lifespan에서 UnifiedChatHandler 초기화 및 정리
    - 일반 대화, RAG 검색, 여행 일정을 하나의 엔드포인트로 통합
  - **의존성 추가**:
    - requirements.txt에 mariadb>=1.1.0,<2.0.0 추가
  - **테스트 작성** (TDD Red 단계):
    - tests/test_chat_history.py: MariaDB 저장/조회 테스트
    - tests/test_itinerary_structured.py: Structured Outputs 테스트
    - tests/test_unified_chat.py: Function Calling 통합 테스트
  
## Step 8. 통합 채팅 시스템 구현 (2025-11-17)
- [x] **Structured Outputs 구현**
  - `backend/schemas.py`: ItineraryDay, ItineraryData, ItineraryStructuredResponse, ChatRequest 스키마 추가
  - `backend/llm_base.py`: generate_structured() 메서드 추가 (OpenAI beta.chat.completions.parse 사용)
  - 100% JSON 보장으로 파싱 오류 완전 제거
- [x] **ChatHistoryManager 구현** (`backend/chat_history.py`)
  - MariaDB에 JSON을 LONGTEXT로 저장 (JSON_VALID CHECK 제약)
  - save_message(), get_history(), get_recent_context(), delete_session() 메서드 구현
  - 채팅 기록 영구 저장 및 컨텍스트 관리
- [x] **UnifiedChatHandler 구현** (`backend/unified_chat.py`)
  - Function Calling으로 사용자 의도 자동 파악
  - _handle_general_chat(): 일반 대화 처리
  - _handle_search_places(): RAG 검색 (Retriever 연동)
  - _handle_create_itinerary(): 여행 일정 생성 (Structured Outputs 사용)
- [x] **통합 채팅 엔드포인트** (`backend/main.py`)
  - POST /chat 엔드포인트 추가
  - lifespan에서 UnifiedChatHandler 초기화 및 정리
  - 일반 대화, RAG 검색, 여행 일정을 하나의 엔드포인트로 통합
  - Function Calling 자동 감지 및 실행
- [x] **MariaDB 설정**
  - docker-compose.yml에 MariaDB 10.11 컨테이너 추가
  - backend/db/init_chat_history.sql: chat_history 테이블 스키마 작성
  - 포트 3306 바인딩, 초기화 스크립트 마운트
- [x] **의존성 추가**
  - requirements.txt에 mariadb>=1.1.0,<2.0.0 추가
  - .env.example에 MariaDB 환경변수 추가
- [x] **테스트 코드 작성** (TDD Red 단계)
  - tests/test_chat_history.py: MariaDB 저장/조회 테스트
  - tests/test_itinerary_structured.py: Structured Outputs 테스트
  - tests/test_unified_chat.py: Function Calling 통합 테스트
  - tests/test_chat_integration.py: 통합 채팅 API 테스트
- [x] **Git 커밋 분리** (1 변경 1 커밋 원칙)
  - 15개 파일을 개별 커밋으로 분리 완료
  - feat, chore, test, docs 태그로 명확한 커밋 메시지

## Step 9. 문서화 정리 (2025-11-17)
- [x] **중복 문서 통합**
  - WORK_STATUS.md 삭제 (CURRENT_STATUS.md로 대체)
  - plan.md 삭제 (TDD 원칙은 본 문서에 포함)
  - 프로젝트_계획서.md 삭제 (PROJECT_PLAN.md로 통합)
  - PROJECT_STATUS.md 삭제 (CURRENT_STATUS.md로 대체)
- [x] **CURRENT_STATUS.md 생성**
  - 최신 구현 현황 요약
  - 다음 작업 계획
  - 성능 지표 및 데이터 현황
- [ ] **FILE_CATALOG.md 업데이트**
  - 통합 채팅 시스템 파일 추가
  - 구조 최신화
- [ ] **README.md 업데이트**
  - 통합 채팅 시스템 기능 설명 추가
  - 최신 API 엔드포인트 반영

---

### 다음 단계
- MariaDB 설정 및 chat_history 테이블 생성 확인
- 통합 채팅 시스템 테스트 실행 (4개 테스트 파일)
- 프론트엔드 연동 준비 (Node.js 가이드 업데이트)
