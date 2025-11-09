# FastAPI 기반 RAG + LLM 백엔드 서빙 명세서

## 🎯 목적

한국 관광 가이드 챗봇 프로젝트에서 Node.js(게이트웨이)와 연동되는 FastAPI 백엔드의 **안정적 RAG + LLM 서빙 환경** 구축.

본 문서는 **바이브 코딩(Vibe Coding)** 과정 중 오류를 최소화하고, 일관된 실행 환경을 유지하기 위한 제약 조건을 포함한다.

---

## 🧱 1. 시스템 개요

```
(Node.js)
   ↓ /rag/query
(FastAPI)
   ├── retriever.py → pgvector 검색
   ├── llm_base.py → GPT API / Local LLM
   ├── rag_chain.py → LangChain QA 체인
   └── main.py → API 라우터
```

---

## 📂 2. 디렉토리 구조

```
backend/
├── main.py              # FastAPI 진입점
├── retriever.py         # 벡터 검색 모듈
├── llm_base.py          # LLM 추상화 계층
├── rag_chain.py         # LangChain RAG 체인
├── schemas.py           # Pydantic 스키마 정의
├── db/
│   ├── connect.py       # PostgreSQL 연결
│   └── init_vector.sql  # pgvector 초기화
├── utils/
│   └── logger.py        # 로깅 유틸리티
└── tests/
    ├── test_rag.py      # RAG 테스트
    └── test_api.py      # FastAPI 통합 테스트
```

---

## 🧠 3. 주요 제약 조건

### 3.1 코드 실행 제약

1. **FastAPI 서버는 단일 스레드로 실행 금지.** → `uvicorn main:app --workers 2` 이상 필요.
2. **DB 커넥션 풀 최소 5개 유지.** → psycopg2 connection pool 사용.
3. **LangChain 버전 고정:** `langchain==0.2.x` (버전 차이로 인한 Chain API 변경 방지)
4. **OpenAI SDK 고정:** `openai>=1.12.0,<2.0.0`
5. **임베딩 모델:** 반드시 `text-embedding-3-small` 사용 (vector dimension=1536)
6. **LLM 모델:** `gpt-4-turbo` 또는 동일 context length (128k) 모델만 허용.
7. **LLM 요청 시간 제한:** 15초 초과 시 `asyncio.TimeoutError` 발생 시 재시도.
8. **에러 핸들링 통합:** 모든 예외는 `utils/logger.py` 내 `log_exception()`으로 처리.

### 3.2 데이터 제약

1. **v1.1 Parent-Child 아키텍처 사용** (2025-11-07부터)
   - tourism_parent: 문서 요약 (377,263개)
   - tourism_child: QA 청크 (2,202,565개)
2. Parent 컬럼 `summary_embedding`은 vector(384)
3. Child 컬럼 `qa_embedding`은 vector(384)
4. `metadata` 필드는 JSON Schema 검증 필요 (9+개 필드)
   - 필수: domain, title, source_url
   - 선택: area, place_name, start_date, end_date, images, parent_id
5. `domain` 필드는 ENUM(`['food','stay','nat','his','shop','lei']`)
6. 텍스트 인코딩은 UTF-8 고정.
7. JSON 입력 시 `None` 또는 빈 문자열은 삽입 불가.

### 3.3 응답 구조 제약

```json
{
  "answer": string,   // 비어있을 수 없음
  "sources": string[], // 최소 1개 이상의 출처 필요
  "latency": float    // 소수점 이하 2자리, 초 단위
}
```

### 3.4 API 호출 제약

| 항목       | 조건                   |
| -------- | -------------------- |
| 요청 본문 크기 | 10KB 이하              |
| 응답 시간    | 최대 3초 이내 (LLM 포함)    |
| 동시 요청    | 20개 이하 유지            |
| HTTP 상태  | 200 / 400 / 500 외 금지 |

---

## 🔍 4. 주요 모듈

### retriever.py (v1.1)

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
import psycopg2
from langchain.schema import Document

class Retriever:
    def __init__(self, db_url: str):
        # multilingual-e5-small 사용 (384차원, M4 GPU 가속)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-small",
            model_kwargs={'device': 'mps'}  # M4 GPU
        )
        self.db_url = db_url

    def search(self, query: str, top_k: int = 5, 
               domain: str = None, area: str = None):
        """
        Parent-Child 구조에서 검색
        - PGVector <=> 연산자로 코사인 유사도 계산
        - Parent-Child JOIN으로 메타데이터 풍부화
        - domain/area 필터링 지원
        """
        if not query or len(query.strip()) < 2:
            raise ValueError("Query must be non-empty.")
        
        # 쿼리 임베딩
        query_vector = self.embeddings.embed_query(query)
        
        # SQL 쿼리 구성 (직접 쿼리 방식)
        sql = """
        SELECT 
            c.child_id, c.qa_text, c.parent_id,
            p.title, p.domain, p.area, p.place_name, 
            p.source_url, p.start_date, p.end_date,
            1 - (c.qa_embedding <=> %s::vector) as similarity
        FROM tourism_child c
        JOIN tourism_parent p ON c.parent_id = p.parent_id
        WHERE 1=1
        """
        params = [query_vector]
        
        if domain:
            sql += " AND p.domain = %s"
            params.append(domain)
        
        if area:
            sql += " AND (c.area LIKE %s OR c.place_name LIKE %s OR c.title LIKE %s)"
            area_pattern = f"%{area}%"
            params.extend([area_pattern, area_pattern, area_pattern])
        
        sql += " ORDER BY similarity DESC LIMIT %s"
        params.append(top_k)
        
        # DB 실행 및 결과 반환
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                results = cur.fetchall()
        
        # Document 객체 생성
        documents = []
        for row in results:
            doc = Document(
                page_content=row[1],  # qa_text
                metadata={
                    'child_id': row[0],
                    'parent_id': row[2],
                    'title': row[3],
                    'domain': row[4],
                    'area': row[5],
                    'place_name': row[6],
                    'source_url': row[7],
                    'start_date': row[8],
                    'end_date': row[9],
                    'similarity': float(row[10])
                }
            )
            documents.append(doc)
        
        return documents
```

### llm_base.py

```python
from openai import OpenAI
import os, asyncio

class LLMClient:
    def __init__(self, model_name="gpt-4-turbo"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model_name

    async def generate(self, messages):
        try:
            async with asyncio.timeout(15):
                completion = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=messages
                )
                return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"[오류] 응답 생성 실패: {str(e)}"
```

### rag_chain.py

```python
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

PROMPT = """
너는 일본인을 위한 한국 관광 안내 챗봇이다.
모든 답변은 일본어로 제공하고 출처를 명시하라.

질문: {question}
컨텍스트: {context}
"""

def create_chain(llm, retriever):
    prompt = PromptTemplate(template=PROMPT, input_variables=["question", "context"])
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )
    return chain
```

---

## 🧩 5. 운영 관련 제약

| 항목       | 내용                                         |
| -------- | ------------------------------------------ |
| 환경 변수 검증 | FastAPI 시작 시 `.env` 누락 시 종료                |
| 로깅 정책    | 모든 API 호출/LLM 결과/에러는 `utils/logger.py`에 기록 |
| DB 재연결   | 5회까지 재시도 후 실패 시 종료                         |
| 메모리 사용   | 512MB 초과 시 자동 리셋 권장                        |
| 임시 캐시    | Redis TTL 300초                             |

---

## 🧪 6. 테스트 제약

* `pytest --maxfail=1 --disable-warnings` 로 단일 실패 즉시 중단.
* 통합테스트는 실제 DB에 쓰기 금지 → Mock VectorStore 사용.
* 테스트는 LLM 호출 시 `DummyLLM`으로 대체 (비용 절약).

---

## 🧱 7. 배포 제약

* **Docker 컨테이너:** 반드시 Python 3.10 이미지 사용.
* **Health check:** `/health` 엔드포인트 3회 실패 시 자동 재시작.
* **CI/CD 조건:** 모든 pytest 성공 + lint 통과 시에만 배포.
* **API Key 보안:** `.env` 외 노출 금지, Node에 직접 포함 금지.

---

## ✅ 실행 예시

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

---

> 이 문서는 FastAPI 기반 RAG + LLM 백엔드의 안정성과 재현성을 보장하기 위한 공식 제약 명세서이다.
