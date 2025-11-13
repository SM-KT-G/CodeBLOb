# FastAPI RAG Backend

한국 관광 정보를 일본어로 제공하는 Retrieval-Augmented Generation 백엔드입니다. FastAPI와 PostgreSQL(pgvector)을 기반으로 parent-child 청크 구조, Query Expansion, Redis 캐시를 활용해 빠르고 정확한 응답을 제공합니다.

---

## 주요 기능

- **LangChain 기반 RAG 체인**: Retriever → LLM 체인으로 답변·출처·지연시간을 반환.
- **Parent/Child QA 스키마**: tourism_parent/child 테이블에 풍부한 메타데이터를 저장해 domain/area 필터링 지원.
- **Query Expansion**: JSON 설정 파일로 구두점 제거·접미어·사용자 변형을 관리하고, 변형별 성공/실패 지표를 로깅.
- **Redis 캐시**: 동일 쿼리/Query Expansion 결과를 TTL 기반으로 캐싱해 응답 속도 향상 (옵션).
- **헬스 체크**: `/health` 엔드포인트에서 API/DB/LLM/Redis 상태를 보고하고 degraded 상태 감지.
- **테스트 스위트**: FastAPI TestClient 기반 통합 테스트와 Query Expansion/RAG 후처리 단위 테스트 포함.

---

## 기술 스택

| 영역 | 사용 기술 |
| --- | --- |
| Backend | FastAPI 0.109.x, Python 3.11 |
| Database | PostgreSQL 15 + pgvector |
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
  llm_base.py           # OpenAI LLM 래퍼
  schemas.py            # Pydantic 모델
  db/                   # ConnectionPool 및 스키마 스크립트
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

## 테스트

```bash
# 빠른 테스트 (Query Expansion + RAG 후처리 + FastAPI)
python -m pytest tests/test_query_expansion_config.py tests/test_rag.py tests/test_api.py

# 전체 테스트
python -m pytest
```

테스트는 실제 DB/Redis 없이 Mock을 사용해 동작하도록 구성되어 있습니다.

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
