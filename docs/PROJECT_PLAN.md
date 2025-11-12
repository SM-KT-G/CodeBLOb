# FastAPI RAG 백엔드 구현 계획

## 1. 프로젝트 개요
- 목적: Node.js 게이트웨이와 연동되는 한국 관광 가이드 챗봇 백엔드 구축.
- 범위: RAG 기반 답변 API, 시스템/데이터 제약 준수, 향후 추천 여행 경로 기능 확장 대비.
- 목표: 안정적·일관된 실행 환경, 테스트 가능한 구조, 배포 자동화를 포함한 운영 전략 수립.

## 2. 시스템 아키텍처 개요
```
프론트엔드 (웹/모바일)
   └─ Node.js Gateway (/rag/query, 추천 경로 API 예정)
        └─ FastAPI Backend
             ├─ main.py (엔트리포인트 & 라우터)
             ├─ rag_chain.py (LangChain QA)
             ├─ retriever.py (pgvector 검색)
             ├─ llm_base.py (OpenAI LLM 클라이언트)
             ├─ schemas.py (Pydantic 스키마)
             ├─ db/connect.py (PostgreSQL + Connection Pool)
             └─ utils/logger.py (로깅/예외 처리)
```
- 외부 의존성: PostgreSQL + pgvector, OpenAI API, Redis(캐시, 옵션).
- FastAPI는 멀티 워커(Uvicorn workers ≥ 2)로 구동.

## 3. 기본 디렉토리 구조
```
backend/
├── main.py               # FastAPI 앱 초기화 및 라우터 등록
├── retriever.py          # PGVector 기반 검색 모듈
├── llm_base.py           # OpenAI SDK 래퍼
├── rag_chain.py          # LangChain RetrievalQA 구성
├── schemas.py            # 요청/응답 Pydantic 모델
├── db/
│   ├── connect.py        # 커넥션 풀 & 재연결 로직
│   └── init_vector.sql   # pgvector 초기화 스크립트
├── utils/
│   └── logger.py         # 공통 로깅/예외 헬퍼
└── tests/
    ├── test_rag.py       # RAG 체인 단위 테스트
    └── test_api.py       # FastAPI 통합 테스트
```
- 추가 파일: `.env.example`, `pyproject.toml` 또는 `requirements.txt`, `Dockerfile`, `pytest.ini`.
- 문서화: `PROJECT_PLAN.md`(본 문서), README 유지, 추가 기술 문서는 `docs/` 디렉토리 고려.

## 4. 모듈별 구현 계획
### 4.1 main.py
- FastAPI 인스턴스 생성, `/rag/query`, `/health` 라우터 정의.
- 의존성 주입 패턴으로 LLMClient, Retriever, RAG 체인 관리.
- 애플리케이션 시작 시 `.env` 로드 및 필수 환경 변수 검증 후 미충족 시 종료.

### 4.2 schemas.py
- 요청 모델: 질문 문자열, 메타데이터 등 검증.
- 응답 모델: `answer`, `sources`, `latency` 필수 필드, 응답 시간 소수점 둘째 자리 포맷터 포함.

### 4.3 retriever.py
- `PGVector`와 `OpenAIEmbeddings(model="text-embedding-3-small")` 초기화.
- 입력 검증(최소 길이 등), 예외 시 `log_exception()` 호출 후 HTTP 400 변환.
- `top_k` 기본값 5, 요구 시 파라미터화.

### 4.4 llm_base.py
- `OpenAI` SDK (`>=1.12.0,<2.0.0`) 기반 클라이언트.
- `asyncio.timeout(15)` 및 재시도(backoff) 로직.
- 모델: `gpt-4-turbo` 또는 동등 128k context 모델로 제한.

### 4.5 rag_chain.py
- Prompt: 일본어 응답 + 출처 표시 강제.
- `RetrievalQA.from_chain_type()` 사용, chain_type_kwargs로 PromptTemplate 주입.
- 체인 실행 결과 후처리: sources 추출, latency 계산.

### 4.6 utils/logger.py
- 표준 로거 구성, 구조화 로그(JSON) 고려.
- `log_exception(e: Exception, context: dict)` 제공, 모든 예외 처리 지점에서 호출.

### 4.7 db/connect.py
- psycopg 커넥션 풀 최소 5개 유지.
- 연결 실패 시 최대 5회 재시도, 실패 시 애플리케이션 종료.
- `init_vector.sql` 실행 여부 확인, 스키마 상태 검사.

### 4.8 tests/
- `pytest --maxfail=1 --disable-warnings` 설정.
- `test_rag.py`: Dummy LLM/Retriever로 RAG 응답 구조 검증.
- `test_api.py`: FastAPI TestClient, Mock VectorStore 사용하여 실제 DB 쓰기 금지.

## 5. 시스템 제약 및 정책
- LangChain 버전: `langchain==0.2.x`.
- OpenAI Embeddings: `text-embedding-3-small` (dim 1536).
- DB 스키마:
  - `embedding` 컬럼: `vector(1536)`.
  - `domain`: ENUM(`food`, `stay`, `nat`, `his`, `shop`, `lei`).
  - `metadata`: JSON Schema 검증, `null`/빈 문자열 허용 안 함.
- API 제약:
  - 요청 본문 10KB 이하.
  - 응답 시간 최대 3초(LLM 호출 포함).
  - 동시 요청 20 이하, 허용 상태 코드 200/400/500.
- 로깅: 모든 API/Troubleshooting 결과 `logger.py` 활용, 식별 가능한 trace id 고려.
- 캐시: Redis TTL 300초 (추후 구현 시).
- 메모리 512MB 초과 시 프로세스 재기동 권장.

## 6. Step-by-Step 구현 체크리스트
### Step 0. 킥오프 & 환경 세팅
- [ ] `.venv` 생성 및 활성화, Python 3.10 확인.
- [ ] 패키지 매니저(예: Poetry) 결정 후 `pyproject.toml`/`requirements.txt` 초안 작성.
- [ ] `.env.example` 작성, 필수 키(OPENAI_API_KEY, DATABASE_URL 등) 명시.
- [ ] VS Code/IDE 기본 설정 및 포맷터, 린터(ruff/black) 확정.

### Step 1. 프로젝트 스켈레톤 구성
- [ ] `backend/` 디렉토리와 필수 서브 디렉토리(`db`, `utils`, `tests`) 생성.
- [ ] `main.py`, `schemas.py`, `retriever.py`, `llm_base.py`, `rag_chain.py` 빈 파일 배치.
- [ ] FastAPI 앱 기본 구조 및 `/health` 라우트 추가.
- [ ] 애플리케이션 시작 시 `.env` 누락 검증 로직 작성.

### Step 2. 데이터베이스 & 벡터 인프라 준비
- [ ] `db/connect.py`에 psycopg 커넥션 풀과 재시도 로직 구현.
- [ ] `init_vector.sql` 작성: pgvector 확장, 테이블, ENUM(domain) 정의.
- [ ] 로컬/개발 환경 DB 연결 테스트, 스키마 유효성 검증.
- [ ] DB 관련 예외 처리에서 `log_exception()` 호출 확인.

### Step 2.5. 임베딩 데이터 준비 (상세 계획: EMBEDDING_PLAN.md)
- [ ] `scripts/` 디렉토리 생성 및 임베딩 유틸리티 작성.
- [ ] `scripts/embed_initial_data.py` 구현:
  - `labled_data/` JSON 파일 재귀 탐색
  - 텍스트 추출 (제목 + 도메인 + 본문)
  - OpenAI `text-embedding-3-small` 호출 (배치 처리)
  - `tourism_data` 테이블에 INSERT (중복 방지)
  - 진행 상황 로깅 및 에러 핸들링
- [ ] 개발 환경에서 초기 임베딩 실행 (약 500개 파일 예상).
- [ ] DB 검증: 레코드 수, 벡터 차원(1536), 도메인 분포 확인.
- [ ] Retriever로 간단한 검색 테스트 수행.
- [ ] **비용**: 약 $0.002 (OpenAI embedding API)

### Step 3. RAG 구성 요소 구현
- [ ] `retriever.py`에 `PGVector` 초기화 및 입력 검증 로직 작성.
- [ ] `llm_base.py`에 OpenAI 클라이언트, 15초 타임아웃 및 재시도 반영.
- [ ] `rag_chain.py`에서 PromptTemplate, RetrievalQA 체인 구성.
- [ ] LangChain/OpenAI 버전 고정 및 의존성 파일 업데이트.

### Step 4. API 계약 완성
- [ ] `schemas.py`에 요청/응답 모델 정의, 응답 포맷(답변/출처/지연시간) 보장.
- [ ] `/rag/query` 라우터 구현, 의존성 주입으로 RAG 체인 호출.
- [ ] 응답 latency 계산 및 소수 둘째 자리 포맷 처리.
- [ ] 에러 핸들러 등록, 상태 코드(200/400/500) 제한.

### Step 5. 로깅, 모니터링, 캐시 훅
- [ ] `utils/logger.py`에서 구조화 로깅 구성 및 `log_exception` 구현.
- [ ] 주요 경로에 로깅 삽입(요청 수신, LLM 호출, 예외).
- [ ] Redis 캐시 인터페이스 초안 설계(필요 시 env flag로 활성화).
- [ ] 시스템 메트릭 수집 방법 정리(추후 APM 연동 용도).

### Step 6. 테스트 & 품질 관리
- [ ] `tests/test_rag.py`에 DummyRetriever/LLM 활용한 단위 테스트 작성.
- [ ] `tests/test_api.py`에 FastAPI TestClient 기반 통합 테스트 작성.
- [ ] pytest 설정 파일 및 명령(`--maxfail=1 --disable-warnings`) 검증.
- [ ] 린트/포맷 파이프라인(pre-commit 또는 CI 스크립트) 구성.

### Step 7. 배포 준비
- [ ] Python 3.10 기반 Dockerfile 작성, uvicorn 멀티 워커 설정.
- [ ] CI 파이프라인에서 pytest + lint 통과 시에만 배포하도록 조건화.
- [ ] `/health` 헬스체크와 재시작 정책 문서화.
- [ ] 환경 변수 주입 전략 및 시크릿 관리 프로세스 확정.

### Step 8. 추천 여행 경로 기능(사전 준비)
- [ ] Node/프론트 팀과 API 스펙 논의, 입력/응답 포맷 확정.
- [ ] FastAPI 내 placeholder 라우터/서비스 인터페이스 초안 작성.
- [ ] 임시 Mock 응답과 테스트 케이스 작성(프론트 연동 용도).
- [ ] 데이터 소스 조사 및 알고리즘 선택지 정리.

## 7. 향후 과제: 추천 여행 경로 기능(구현 예정)
- **기능 개요**: 프론트 별도 페이지에서 사용자 입력 기반 당일 여행 경로 제안.
- **입력 항목**
  - 지역: 시 단위 선택.
  - 이동수단: 버스, 도보, 자전거, 택시, 지하철, 자차.
  - 원하는 주제: 음식, 문화 생활, 축제, 휴식, 액티비티.
- **요구 사항**
  - 챗봇 API와 별도 엔드포인트로 분리.
  - Node.js 게이트웨이/프론트와 협의 후 인터페이스 확정.
  - 추천 알고리즘(룰 기반 혹은 외부 데이터) 정의, 데이터 소스 확보 필요.
  - 응답에 경로, 예상 소요 시간, 추천 장소 출처 포함 검토.
- **초기 설계 제안**
  1. FastAPI 내부 서비스 레이어 초안 작성(입력 검증, 추천 Stub).
  2. Node.js와 데이터 포맷 합의 후 schemas에 반영.
  3. 실제 구현 전 Mock 응답 제공하여 프론트 개발 병행 지원.
  4. 장기적으로 RAG와 연계해 지역 컨텍스트 기반 추천 고도화.

## 8. 후속 작업 제안
- 1) 스켈레톤 코드 작성 및 의존성 설치.
- 2) DB/pgvector 환경 세팅 및 기본 테스트 통과.
- 3) 추천 경로 기능 관련 요구사항 명세 및 프론트/Node 팀 협업 일정 수립.

본 계획은 FastAPI 백엔드와 추가 기능 확장을 안정적으로 수행하기 위한 기준 문서로 유지/업데이트한다.
