# FastAPI RAG 백엔드 구현 계획 _(2025-11-08 최신화)_

프로젝트 문서·코드 전반을 재검토해 실제 구현 상태와 앞으로의 작업을 다시 정리했습니다.  
본 계획은 Node.js 게이트웨이와 연동되는 한국 관광 가이드 RAG 백엔드를 안정적으로 제공하기 위한 기준 문서입니다.

---

## 1. 프로젝트 개요
- **목표**: 일본어 사용자 대상 관광 Q&A API(`/rag/query`)를 FastAPI로 제공하고, Node 게이트웨이·프론트엔드에서 안정적으로 소비할 수 있도록 문서/테스트/운영 체계를 갖춘다.
- **범위**: 데이터 임베딩 파이프라인, Retriever, FastAPI 엔드포인트, LLM/RAG 체인, 품질 모니터링 및 향후 추천 경로 API 준비.
- **운영 제약**: 응답 SLA 3초, 동시 요청 20rps, 요청 본문 10KB 이하, 민감 키(.env) 관리, PostgreSQL + pgvector + Redis(옵션).

---

## 2. 현재 구현 현황 (코드 기준)
| 영역 | 상태 | 관련 파일 | 비고 |
|------|------|-----------|------|
| 데이터/임베딩 | ✅ v1.1 Parent-Child 완료 | `scripts/embed_initial_data_v1.1.py`, `labled_data/*`, `backend/db/init_vector_v1.1.sql` | Parents 377k / Children 2.2M, e5-small(384d) |
| 검색기 | ✅ 직접 SQL + metadata filtering | `backend/retriever.py` | Query expansion 프로토타입 존재, parent_context 플래그 미연동 |
| FastAPI API | ✅ `/health`, `/rag/query` 라우트 | `backend/main.py` | `/rag/query`는 Retriever top document preview를 그대로 반환 (LLM 미사용) |
| RAG 체인/LLM | ⚠️ 코드만 존재, 미연결 | `backend/rag_chain.py`, `backend/llm_base.py` | import 경로 오류(`utils.logger`), FastAPI에 주입 안 됨 |
| 테스트 | ⚠️ 수동 스크립트/설계안 위주 | `tests/*`, `test_*.py` | 통합 테스트 다수 미구현, Mock 기반 단위 테스트 필요 |
| 문서 | ⚠️ 일부 구 버전 설정(1536d, OpenAI Embedding) | `docs/*.md`, `readme.md` | API/상태 문서는 최신, 계획 문서/README는 구 정보 포함 |

---

## 3. 코드 vs 문서 갭 요약
1. **임베딩/모델 정보 불일치**: Plan/README가 OpenAI `text-embedding-3-small`, 1536d 벡터를 언급하나 실제 코드는 HuggingFace `intfloat/multilingual-e5-small` 384d 사용.
2. **LLM/RAG 통합 미완**: `rag_chain.py`·`llm_base.py`가 FastAPI에 연결되지 않아 답변 생성이 Retriever preview에 머물러 있음.
3. **`parent_context` 옵션 미반영**: 스키마에는 필드가 있으나 `/rag/query`는 항상 parent summary를 포함한 page_content를 답변에 그대로 노출.
4. **테스트 스위트 미구현**: `tests/test_api.py`, `tests/test_rag.py` 등은 placeholder이며 CI에 활용 불가. 실 DB 의존 테스트만 존재.
5. **헬스체크 TODO 미해결**: `/health`가 DB/LLM 상태를 점검하지 않으며 TODO 주석 그대로 남아 있음.
6. **로깅/문서 링크 불일치**: `rag_chain.py`, `llm_base.py`가 `utils.logger`를 import하여 패키지 경로 오류 가능. Node 통합 문서는 최신이지만 README/PLAN 문서는 중복 및 구 정보 유지.

---

## 4. 우선순위 로드맵
### 4.1 이번 주 (Short Term)
1. **RAG 체인 연결 (완료)**
   - `backend/rag_chain.py` import 경로 정리 및 Retriever 어댑터 추가.
   - `backend/main.py`에서 Retriever → RAG 체인을 구성하고, `parent_context`/`expansion` 옵션과 연동.
   - 응답 `metadata`에 모델명, retrieved_count 등을 포함.
2. **Parent Context 옵션 정합성 (완료)**
   - `RAGQueryRequest.parent_context`에 따라 parent summary 포함/제외 처리.
   - Node 가이드 업데이트는 후속 작업으로 추적.
3. **테스트 자동화 1차 (완료)**
   - `tests/test_api.py`에 FastAPI TestClient 기반 happy path/validation 테스트 작성.
   - `tests/test_rag.py`를 실제 `process_rag_response()` 호출로 교체해 중복 출처 제거 로직 검증.
4. **헬스체크/모니터링 (완료)**
   - `/health`에서 DB ping 및 OpenAI/Redis 상태를 검증하고 degraded 상태를 표기.
   - Query Expansion 변형·성공/실패 지표를 로그에 포함.

### 4.2 다음 주 (Mid Term)
1. **Query Expansion 하드닝**
   - 변형 규칙을 설정 파일/테이블로 외부화, 실패 변형 로깅, Top-K 병합 로직 개선. ✅ 설정 파일/로그 기반 1차 구현 완료, latency 분석 및 cutoff 전략은 후속.
   - 확장 사용 시 latency 영향 측정 및 cutoff 전략 도입.
2. **캐시/성능**
   - Redis TTL 전략 설계(동일 질문 캐시, area/domain 키 구성) 및 장애 시 fallback 절차 문서화. ✅ Redis 캐시 1차 도입(검색/Query Expansion 결과 캐싱), 운영 Runbook 반영 예정.
   - Connection pool 모니터링/metrics 수집.
3. **테스트 자동화 2차**
   - Mock Retriever/LLM을 이용해 DB 없이도 pytest가 통과하도록 리팩터링.
   - Query expansion/parent context를 커버하는 단위 테스트 추가.

### 4.3 장기
1. **추천 여행 경로 API**
   - 입력 스키마(지역/교통/테마) 확정, placeholder 라우트 추가.
   - Node 팀과 응답 포맷 합의, Mock 데이터 기반 E2E 준비.
2. **운영 문서화/배포 자동화**
   - Dockerfile + CI 파이프라인 정비, 배포 체크리스트 작성.
   - SLA/알림 정책, 장애 대응 Runbook 작성.

---

## 5. 구현 체크리스트 (업데이트)

### 5.1 완료된 항목
- [x] FastAPI 스켈레톤 + `/health`/`/rag/query` 라우트
- [x] PostgreSQL + pgvector 인프라, ConnectionPool, 재시도 로직
- [x] v1.1 Parent-Child 스키마/임베딩 + HuggingFace e5-small 적용
- [x] Metadata Filtering (domain/area) + Query Expansion 프로토타입
- [x] 수동 진단 스크립트 (`test_db_connection.py`, `test_retriever_v1.1.py`, `test_step1_filtering.py`)
- [x] 프로젝트 문서 허브(`docs/README.md`), API 스펙(`docs/openapi_rag.yaml`), 상태 리포트(`docs/PROJECT_STATUS.md`)

### 5.2 진행 예정
- [x] `rag_chain.py`/`llm_base.py` 실제 API 연동 및 예외 처리
- [x] `parent_context` 플래그 분기, child only 응답 모드 지원
- [x] `/health` DB/LLM 체크 및 지표 노출
- [ ] README/프로젝트 문서의 임베딩/모델 정보 최신화
- [x] FastAPI/TestClient + Mock 기반 테스트 스위트 정비
- [x] Query Expansion 설정/모니터링 체계 수립
- [x] Redis 캐시 전략 및 fallback 시나리오 1차 구현 (추가 문서화 필요)
- [ ] 추천 경로 API 사전 설계 및 스키마 초안

---

## 6. 테스트 & 품질 전략
1. **단위 테스트**
   - Retriever helper → Mock DB cursor 주입으로 `_build_sql_and_params`, `_rows_to_documents` 검증.
   - Query Expansion 변형 로직에 대한 pure function 테스트 작성.
2. **통합 테스트**
   - FastAPI TestClient로 `/rag/query` happy path, validation error, expansion=true, parent_context=false 경로 검증.
   - `/health`가 DB/LLM 상태 필드를 반환하는지 확인.
3. **회귀 방지**
   - Mock LLM(샘플 답변) + In-memory docs로 RAG 체인을 테스트하여 OpenAI 호출 없이 CI 통과.
   - `pytest.ini` 설정 유지(`--maxfail=1 --disable-warnings -v`).
4. **수동 검증**
   - `test_retriever_v1.1.py`, `test_step1_filtering.py`는 운영 점검 시 사용하되 CI에서 자동 실행하지 않는다.

---

## 7. 운영/배포 노트
- Docker Compose로 PostgreSQL + Redis 실행, 앱은 uvicorn 멀티 프로세스로 구동.
- `.env.local`에 OPENAI_API_KEY, DATABASE_URL, LOG_LEVEL 필수.
- SLA 모니터링: `X-Process-Time` 헤더 활용, 3초 초과 시 로그 경고.
- 장애 대비: DB 접속 실패 시 애플리케이션 기동 중단, LLM 오류 시 graceful 메시지 반환.
- 향후 배포 자동화를 위해 GitHub Actions에서 `pytest` + `ruff` + `black --check` 실행을 권장.

---

## 8. 협업 & 문서화 To-Do
1. Node.js 팀과 API 계약 재확인 (`parent_context`, `metadata` 구조 공유).
2. README 중복 문구 정리 및 최신 실행/테스트 절차 반영.
3. 운영 팀을 위한 Runbook(health 체크, 장애 대응) 초안 작성.
4. 추천 경로 기능 요구사항을 별도 문서로 분리하고 일정 합의.

---

문서 개선이나 새로운 파일이 생기면 `docs/FILE_CATALOG.md`와 본 계획을 동시에 업데이트하여 일관성을 유지하세요.
