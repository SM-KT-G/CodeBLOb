# 파일 기능 명세

프로젝트에 포함된 주요 파일과 디렉토리의 역할을 아래와 같이 정리했습니다.  
데이터 원본(`labled_data/`)처럼 다량의 동형 파일은 패턴 단위로 설명합니다.

## 루트 디렉토리
- `.env.example`: 필수 환경 변수 샘플, API 키·DB URL 템플릿 제공.
- `.gitignore`: 가상환경, 캐시, 로그 등 불필요한 파일을 Git에서 제외.
- `README.md`: FastAPI RAG 백엔드 개요, 실행·테스트 방법 정리 (병합 과정에서 중복 문구 존재).
- `docker-compose.yml`: PostgreSQL(+pgvector) 및 Redis 컨테이너 구성.
- `pyproject.toml`: Poetry/빌드 메타데이터와 기본 의존성 정의.
- `requirements.txt`: FastAPI, LangChain, psycopg, sentence-transformers 등 런타임 패키지 고정.
- `pytest.ini`: pytest 전역 옵션 자리(현재 기본값 위주).
- `embedding_v1.1.log`: 임베딩 배치 실행 로그(모니터링 참고용).

## backend/
- `backend/__init__.py`: 패키지 초기화.
- `backend/main.py`: FastAPI 엔트리포인트, lifespan에서 Retriever 주입, `/health` 및 `/rag/query` 라우트.
- `backend/retriever.py`: PGVector 직접 쿼리 기반 검색기, metadata 필터링·Query Expansion 포함.
- `backend/rag_chain.py`: LangChain RetrievalQA 체인 생성/후처리 로직.
- `backend/llm_base.py`: OpenAI ChatCompletion 래퍼, 동기/비동기 인터페이스·타임아웃 관리.
- `backend/schemas.py`: Pydantic 요청/응답 모델 (DomainEnum, RAGQueryRequest/Response 등).
- `backend/db/connect.py`: psycopg ConnectionPool 생성, 재시도·스키마 체크·SQL 스크립트 실행.
- `backend/db/init_vector.sql`: v1.0 스키마 정의 (단일 tourism_data 테이블).
- `backend/db/init_vector_v1.1.sql`: Parent/Child 테이블, 확장 메타데이터, 인덱스 정의.
- `backend/utils/__init__.py`: 유틸 패키지 초기화.
- `backend/utils/logger.py`: JSON 포맷 구조화 로거와 `log_exception` 헬퍼.

## docs/
- `docs/README.md`: 문서 디렉토리 안내 및 주요 문서 링크.
- `docs/PROJECT_PLAN.md`: 초기 목표·모듈 계획·체크리스트.
- `docs/IMPLEMENTATION_TRACKER.md`: 날짜별 구현 현황과 결정 사항 로그.
- `docs/EMBEDDING_PLAN.md`: 임베딩 전략, 모델 선정, 처리 파이프라인.
- `docs/RAG_PIPELINE_ARCHITECTURE.md`: 전체 RAG 설계 및 향후 개선안.
- `docs/PROJECT_STATUS.md`: 최근 진행 상황·지표·남은 작업 현황.
- `docs/API_INTEGRATION_FOR_NODE.md`: Node 게이트웨이 연동 가이드, 요청/응답 스키마 예시.
- `docs/openapi_rag.yaml`: `/rag/query` 엔드포인트 스펙(OpenAPI 3.0).
- `docs/프로젝트_계획서.md`: 한글 요약본(encoding 이슈 포함).
- `docs/FILE_CATALOG.md`(본 문서): 파일 기능 명세.

## scripts/
- `scripts/embedding_utils.py`: v1.0 데이터 추출·정규화 헬퍼.
- `scripts/embed_initial_data.py`: OpenAI 기반 임베딩 배치 실행.
- `scripts/embedding_utils_v1.1.py`: Parent-Child QA 청크 생성 로직.
- `scripts/embed_initial_data_v1.1.py`: HuggingFace e5-small 임베딩 파이프라인 (체크포인트·MPS 지원).
- `scripts/embedding_checkpoint_v1.1.json`: v1.1 임베딩 진행상황 저장 파일.
- `scripts/monitor_embedding.sh`: 로그 tail 및 진행률 모니터링 쉘 스크립트.
- `scripts/watch_progress.sh`: 배치 수행 중 실시간 상태 확인 스크립트.
- `scripts/node_rag_client.js`: Node 환경에서 `/rag/query` 호출 예제/헬퍼.

## 데이터 (`labled_data/`)
- `labled_data/TL_FOOD/J_FOOD_*.json`: 음식점 도메인 원천 데이터(377k 중 food 영역), 일본어 설명 포함.
- `labled_data/TL_HIS/J_HIS_*.json`: 역사/문화 명소 데이터.
- `labled_data/TL_NAT/J_NAT_*.json`: 자연 관광지 데이터.
- `labled_data/TL_SHOP/J_SHOP_*.json`: 쇼핑/상업 구역 데이터.
- `labled_data/TL_LEI/J_LEI_*.json`: 레저·체험 데이터.
- `labled_data/TL_STAY/J_STAY_*.json`: 숙박 시설 데이터.
- 파일 구조는 JSON 1문서=1객체 형태이며, 임베딩 스크립트가 제목/본문/도메인을 추출해 DB 적재.

## 독립 실행 스크립트 (루트)
- `test_db_connection.py`: DatabaseConnection 클래스로 pgvector/스키마 점검 (수동 실행).
- `test_retriever_v1.1.py`: Retriever v1.1을 직접 호출해 일본어 쿼리 결과 출력.
- `test_step1_filtering.py`: Metadata 필터링 로직 콘솔 검증.

## tests/ 디렉토리 (참고)
> 사용자 요청에 따라 새로운 테스트 코드는 추가하지 않았습니다.
- `tests/test_api.py` 등: FastAPI 라우트 및 스키마 검증용 플레이스홀더.
- `tests/test_retriever_unit.py`, `tests/test_query_expansion.py` 등: Retriever·Query Expansion 단위 테스트 설계안.
- `tests/test_parent_context.py`: Parent summary 관여 여부를 확인하기 위한 예정 테스트.
- `tests/test_similarity_calculation.py`, `tests/test_embedding_injection.py` 등: 품질 회귀 방지 목적(현재 구현 대기).

## 기타
- `embedding_v1.1.log`: v1.1 임베딩 작업 로그.
- `openapi_rag.yaml`: API 명세(문서 섹션에 포함).
- `node_rag_client.js`: Node 샘플 클라이언트(스크립트 섹션에 포함).

필요 시 특정 파일에 대한 상세 설명을 이 문서에 추가하거나 업데이트해 일관성을 유지하세요.
