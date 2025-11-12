# RAG 파이프라인 아키텍처 문서

## 프로젝트 개요
**K-Culture Navi** - 일본인 관광객을 위한 한국 관광 AI 챗봇  
RAG (Retrieval Augmented Generation) 기반 질의응답 시스템

---

## 1. 데이터 전처리

### 1.1 청킹 전략
- **방식**: Document-level Chunking (문서 단위)
- **청킹 없음**: JSON 파일 1개 = 벡터 1개
- **오버랩**: 없음

**선택 이유:**
- 평균 텍스트 길이: 120-150자 (이미 짧음)
- 관광 정보 특성상 맥락 유지 필요
- 문장/단락 분할 시 정보 손실 위험

### 1.2 텍스트 구성

```python
# 임베딩 텍스트 = 제목 + 도메인 + 본문
def extract_embedding_text(data: Dict) -> str:
    parts = []
    
    # 1. 제목 (일본어)
    if title:
        parts.append(f"タイトル: {title}")
        # 예: "タイトル: 지코바치킨 문경모전점"
    
    # 2. 도메인 (일본어 카테고리)
    if domain:
        parts.append(f"分野: {domain}")
        # 예: "分野: 음식점"
    
    # 3. 본문 (일본어 설명)
    if text:
        parts.append(text)
        # 평균 120-150자
    
    return "\n\n".join(parts)
```

### 1.3 메타데이터 구조

```json
{
  "source_url": "블로거 비밀이야의 전국해장음식열전",
  "source": "도서"
}
```

**최적화:**
- 원본 12개 필드 → 2개 필드로 축소
- 저장 공간: 500 bytes → 100 bytes (80% 절감)
- 총 절감량: 144MB (377,265개 문서)

**유지 필드:**
- `source_url`: 챗봇 응답에 출처 표시 용도
- `source`: 정보 신뢰도 판단 용도

**제거 필드:**
- collectedDate, publishedDate
- writer, ISBN_ISNN
- version, source_language, translator

---

## 2. 임베딩 모델

### 2.1 모델 정보

| 항목 | 값 |
|------|-----|
| **모델명** | `intfloat/multilingual-e5-large` |
| **제공** | HuggingFace (sentence-transformers) |
| **벡터 차원** | 1024 |
| **언어** | Multilingual (일본어 최적화) |
| **라이센스** | MIT |
| **비용** | $0 (로컬 실행) |

### 2.2 모델 선정 비교

| 항목 | OpenAI text-embedding-3-small | multilingual-e5-large | 선택 |
|------|------------------------------|----------------------|------|
| 차원 | 1536 | 1024 | ✅ |
| 비용 | $1,131 (377K 문서) | $0 | ✅ |
| 속도 | API 호출 (느림) | GPU 로컬 (빠름) | ✅ |
| 일본어 성능 | 일반 | **특화** | ✅ |
| 관광 도메인 | 일반 | **우수** | ✅ |

**선정 이유:**
1. 100% 비용 절감 ($1,131 → $0)
2. Apple M4 GPU 활용으로 처리 속도 10배 향상
3. 일본어 및 관광 도메인 특화 성능
4. API 제한 없음 (로컬 처리)

### 2.3 임베딩 생성 코드

```python
from sentence_transformers import SentenceTransformer

# 모델 초기화 (GPU 활용)
model = SentenceTransformer(
    "intfloat/multilingual-e5-large",
    device='mps'  # Apple M4 GPU
)

# 임베딩 생성
text = extract_embedding_text(data)
embedding = model.encode(text)  # shape: (1024,)
```

---

## 3. 벡터 데이터베이스

### 3.1 저장 포맷

```sql
-- PostgreSQL + pgvector
CREATE TABLE tourism_data (
    id SERIAL PRIMARY KEY,
    document_id TEXT UNIQUE NOT NULL,     -- 예: "J_FOOD_000001"
    domain domain_type NOT NULL,          -- ENUM('food', 'stay', 'nat', 'his', 'shop', 'lei')
    title TEXT,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL,              -- {"source_url": "...", "source": "..."}
    embedding vector(1024),               -- pgvector 타입
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3.2 도메인 타입

```sql
CREATE TYPE domain_type AS ENUM (
    'food',   -- 음식점 (113,321개)
    'stay',   -- 숙박 (67,472개)
    'nat',    -- 자연/관광 (36,809개)
    'his',    -- 역사/문화 (115,944개)
    'shop',   -- 쇼핑 (29,151개)
    'lei'     -- 레저 (14,568개)
);
```

---

## 4. 인덱싱 방식

### 4.1 벡터 인덱스 (IVFFlat)

```sql
-- IVFFlat 인덱스 생성
CREATE INDEX idx_tourism_embedding 
    ON tourism_data 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

**파라미터 설명:**
- `ivfflat`: Inverted File Flat 알고리즘
- `vector_cosine_ops`: 코사인 유사도 연산자
- `lists = 100`: 클러스터 수 (데이터 크기에 따라 조정)

### 4.2 IVFFlat vs HNSW

| 항목 | IVFFlat | HNSW |
|------|---------|------|
| 검색 속도 | 빠름 | **매우 빠름** |
| 메모리 사용량 | **낮음** | 높음 |
| 인덱스 구축 속도 | **빠름** | 느림 |
| 정확도 | 높음 | 매우 높음 |
| 377K 문서 적합성 | ✅ | △ |

**IVFFlat 선택 이유:**
- PostgreSQL pgvector의 안정적인 기본 옵션
- 377,265개 문서 규모에 적합
- 검색 속도와 정확도의 균형
- 메모리 효율적

### 4.3 보조 인덱스

```sql
-- 메타데이터 검색 (GIN 인덱스)
CREATE INDEX idx_tourism_metadata 
    ON tourism_data 
    USING gin (metadata);

-- 도메인 필터링 (B-tree 인덱스)
CREATE INDEX idx_tourism_domain 
    ON tourism_data (domain);

-- 문서 ID 조회
CREATE UNIQUE INDEX idx_tourism_doc_id
    ON tourism_data (document_id);
```

---

## 5. 검색 전략

### 5.1 벡터 유사도 검색

```python
def search(query: str, top_k: int = 4, domain: str = None):
    """
    코사인 유사도 기반 벡터 검색
    
    Args:
        query: 검색 쿼리 (일본어)
        top_k: 반환할 문서 개수 (기본 4개)
        domain: 도메인 필터 (선택)
    
    Returns:
        상위 K개 문서 리스트
    """
    # 1. 쿼리 벡터화
    query_vector = model.encode(query)  # shape: (1024,)
    
    # 2. 도메인 필터 (선택)
    filter_dict = {"domain": domain} if domain else None
    
    # 3. 벡터 검색 (IVFFlat 인덱스 활용)
    documents = vector_store.similarity_search(
        query=query,
        k=top_k,
        filter=filter_dict
    )
    
    return documents
```

### 5.2 검색 파라미터

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| **top_k** | 4 | GPT-4 컨텍스트 윈도우 최적화 |
| **유사도 임계값** | 없음 | 상위 4개 무조건 반환 |
| **검색 알고리즘** | 코사인 유사도 | `vector_cosine_ops` |

### 5.3 도메인 필터링

```python
# 6개 도메인별 검색
DOMAINS = ['food', 'stay', 'nat', 'his', 'shop', 'lei']

# 예시 1: 음식점만 검색
GET /rag/query?question=ラーメン&domain=food

# 예시 2: 전체 도메인 검색
GET /rag/query?question=観光地
```

### 5.4 재랭킹 전략 (향후 계획)

**현재: 재랭킹 없음**

**향후 개선 계획:**
1. **Cross-Encoder 재랭킹**
   - 검색된 4개 문서를 더 정교하게 재정렬
   - 모델: `cross-encoder/ms-marco-MiniLM-L-12-v2`

2. **Hybrid Search**
   - 벡터 검색 + 키워드 검색 결합
   - BM25 + Semantic Search

3. **MMR (Maximal Marginal Relevance)**
   - 다양성 확보 (유사한 문서 제거)
   - 중복 정보 최소화

---

## 6. 파이프라인 처리 순서

### 6.1 전체 플로우

```
┌─────────────────────────────────────────┐
│ Phase 1: 데이터 수집 및 전처리             │
└─────────────────────────────────────────┘
         ↓
[1] JSON 파일 로드 (377,265개)
         ↓
[2] 데이터 검증
    - 필수 필드 존재 확인
    - 텍스트 길이 체크
    - 도메인 매핑 확인
         ↓
[3] 텍스트 추출
    extract_embedding_text()
    - 제목 + 도메인 + 본문 결합
         ↓
[4] 메타데이터 추출
    extract_metadata()
    - source_url, source 추출
    - 80% 크기 절감

┌─────────────────────────────────────────┐
│ Phase 2: 임베딩 생성                      │
└─────────────────────────────────────────┘
         ↓
[5] 중복 체크
    - document_id로 DB 조회
    - 이미 존재하면 SKIP
         ↓
[6] 임베딩 생성
    model.encode(text)
    - HuggingFace multilingual-e5-large
    - Apple M4 GPU 가속
    - 배치 크기: 1000개
         ↓
[7] 1024차원 벡터 반환

┌─────────────────────────────────────────┐
│ Phase 3: 벡터 DB 저장                     │
└─────────────────────────────────────────┘
         ↓
[8] PostgreSQL INSERT
    INSERT INTO tourism_data (...)
         ↓
[9] IVFFlat 인덱스 자동 업데이트
    - lists = 100 클러스터링
         ↓
[10] 배치 완료
     - 1000개마다 1초 휴식

┌─────────────────────────────────────────┐
│ Phase 4: 검색 및 응답 생성 (런타임)        │
└─────────────────────────────────────────┘
         ↓
[11] 사용자 질문 수신 (일본어)
     POST /rag/query
         ↓
[12] 질문 벡터화
     multilingual-e5-large.encode(query)
         ↓
[13] 벡터 검색
     SELECT * FROM tourism_data
     ORDER BY embedding <=> query_vector
     LIMIT 4
         ↓
[14] 도메인 필터 적용 (선택)
     WHERE domain = 'food'
         ↓
[15] 상위 4개 문서 추출
         ↓
[16] LLM 컨텍스트 구성
     context = "\n\n".join([doc.content])
         ↓
[17] GPT-4 Turbo 답변 생성
     - 일본어 프롬프트
     - temperature = 0.7
         ↓
[18] 출처 정보 추가
     sources = [doc.metadata.source_url]
         ↓
[19] JSON 응답 반환
     {
       "answer": "...",
       "sources": ["...", "..."]
     }
```

### 6.2 성능 최적화 (선택적)

```
[20] Redis 캐싱
     - 동일 질문 재검색 방지
     - TTL: 1시간

[21] Connection Pool
     - PostgreSQL: 5~20 연결 유지

[22] 비동기 처리
     - FastAPI async/await
```

---

## 7. LLM 통합

### 7.1 프롬프트 템플릿

```python
PROMPT_TEMPLATE = """あなたは日本人観光客のための韓国観光ガイドチャットボットです。
以下のコンテキストを基に、質問に日本語で答えてください。
回答には必ず出典(ソース)を明記してください。

コンテキスト:
{context}

質問: {question}

回答（日本語）:"""
```

### 7.2 LLM 설정

```python
# GPT-4 Turbo
llm = ChatOpenAI(
    model="gpt-4-turbo",
    temperature=0.7,
    request_timeout=15
)
```

### 7.3 RAG 체인 구성

```python
from langchain.chains import RetrievalQA

chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",           # 단순 연결
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)
```

---

## 8. 성능 지표

### 8.1 임베딩 성능

| 항목 | 값 |
|------|-----|
| 처리 속도 | ~0.1초/문서 |
| 배치 크기 | 1000개 |
| GPU | Apple M4 (MPS) |
| 총 문서 수 | 377,265개 |
| 총 소요 시간 | ~19시간 |

### 8.2 검색 성능 (예상)

| 항목 | 목표 값 |
|------|---------|
| 벡터 검색 시간 | ~100ms |
| LLM 생성 시간 | ~2-3초 |
| **총 응답 시간** | **< 3초** |

### 8.3 저장 효율

| 항목 | 값 |
|------|-----|
| 메타데이터 (원본) | 500 bytes/문서 |
| 메타데이터 (최적화) | 100 bytes/문서 |
| **절감률** | **80%** |
| **총 절감량** | **144MB** |

---

## 9. 데이터 품질 보장

### 9.1 데이터 검증

```python
# 1. JSON 스키마 검증
required_fields = ["data_info", "text"]

# 2. 텍스트 길이 체크
MIN_LENGTH = 10
MAX_LENGTH = 10000

if not (MIN_LENGTH <= len(text) <= MAX_LENGTH):
    skip_document()

# 3. 도메인 매핑 검증
if domain not in VALID_DOMAINS:
    domain = map_from_folder_name(folder)

# 4. 중복 방지
if document_id_exists_in_db(document_id):
    skip_document()
```

### 9.2 평가 지표 (향후 구현)

**계획:**
1. **Retrieval Accuracy**
   - 정답 문서가 상위 4개에 포함되는 비율
   - 목표: 90% 이상

2. **응답 품질**
   - 일본어 자연스러움 평가
   - 메트릭: BLEU, ROUGE

3. **속도 벤치마크**
   - p50, p95, p99 응답 시간 측정
   - 목표: p95 < 3초

---

## 10. 기술 스택 요약

### 10.1 전체 아키텍처

| 레이어 | 기술 | 역할 |
|--------|------|------|
| **프론트엔드** | Streamlit/React | 일본어 채팅 UI |
| **API** | FastAPI | RESTful API 서버 |
| **RAG 프레임워크** | LangChain | 파이프라인 구성 |
| **임베딩** | HuggingFace | multilingual-e5-large |
| **벡터 DB** | PostgreSQL + pgvector | 벡터 저장 및 검색 |
| **LLM** | OpenAI GPT-4 Turbo | 답변 생성 |
| **캐싱** | Redis | 중복 요청 방지 |
| **인프라** | Docker Compose | 컨테이너 오케스트레이션 |
| **GPU** | Apple M4 (MPS) | 임베딩 가속 |

### 10.2 핵심 파라미터

| 항목 | 값 |
|------|-----|
| 임베딩 차원 | 1024 |
| 청킹 방식 | Document-level (청킹 없음) |
| 인덱스 알고리즘 | IVFFlat (lists=100) |
| 검색 알고리즘 | 코사인 유사도 |
| Top-K | 4 |
| LLM Temperature | 0.7 |
| 배치 크기 | 1000 |

---

## 11. 파일 구조

```
Training/
├── backend/
│   ├── main.py                 # FastAPI 엔트리포인트
│   ├── retriever.py            # 벡터 검색 모듈
│   ├── llm_base.py            # LLM 클라이언트
│   ├── rag_chain.py           # RAG 체인 구성
│   ├── schemas.py             # API 스키마
│   └── db/
│       ├── connect.py         # DB 연결 풀
│       └── init_vector.sql    # 스키마 초기화
│
├── scripts/
│   ├── embedding_utils.py     # 임베딩 유틸리티
│   └── embed_initial_data.py  # 임베딩 실행 스크립트
│
├── labled_data/               # 원본 데이터
│   ├── TL_FOOD/              # 113,321개
│   ├── TL_HIS/               # 115,944개
│   ├── TL_LEI/               # 14,568개
│   ├── TL_NAT/               # 36,809개
│   ├── TL_SHOP/              # 29,151개
│   └── TL_STAY/              # 67,472개
│
├── docker-compose.yml         # PostgreSQL + Redis
├── requirements.txt           # Python 의존성
├── .env                       # 환경 변수
│
└── 문서/
    ├── PROJECT_PLAN.md
    ├── IMPLEMENTATION_TRACKER.md
    ├── EMBEDDING_PLAN.md
    └── RAG_PIPELINE_ARCHITECTURE.md  # 본 문서
```

---

## 12. 향후 개선 계획

### 12.1 단기 개선 (1-2주)

1. **재랭킹 추가**
   - Cross-Encoder 모델 통합
   - 검색 정확도 향상

2. **하이브리드 검색**
   - BM25 + Semantic Search
   - 키워드 검색 보완

3. **캐싱 최적화**
   - Redis 통합
   - 응답 속도 개선

### 12.2 중기 개선 (1-2개월)

1. **평가 시스템**
   - Retrieval Accuracy 측정
   - A/B 테스트 프레임워크

2. **다국어 확장**
   - 영어, 중국어 데이터 추가
   - 동일 아키텍처 재사용

3. **도메인 확장**
   - 교통 정보 연동
   - 실시간 이벤트 정보

### 12.3 장기 개선 (3-6개월)

1. **여행 경로 추천**
   - Graph RAG 도입
   - 지리 정보 활용

2. **멀티모달 검색**
   - 이미지 + 텍스트
   - CLIP 모델 통합

3. **파인튜닝**
   - 관광 도메인 특화 모델
   - 일본어 답변 품질 향상

---

## 참고 자료

- [LangChain Documentation](https://python.langchain.com/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [multilingual-e5-large](https://huggingface.co/intfloat/multilingual-e5-large)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**문서 버전**: 1.0  
**최종 수정일**: 2025년 11월 7일  
**작성자**: K-Culture Navi 개발팀
