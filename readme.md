# FastAPI RAG Backend



RAG 기반 관광정보 검색 시스템



기능RAG (Retrieval-Augmented Generation) 기반 관광정보 검색 시스템



- PostgreSQL + pgvector 벡터 검색

- OpenAI GPT-4 답변 생성

- HuggingFace multilingual-e5-large 임베딩

- Connection Pool DB 연결

- 51개 테스트



# 기술 스택- PostgreSQL + pgvector 벡터 검색



- FastAPI, PostgreSQL, OpenAI, HuggingFace, Python 3.10- OpenAI GPT-4 답변 생성



# 실행- HuggingFace multilingual-e5-large 임베딩



```bash- Connection Pool DB 연결 관리

pip install -r requirements.txt

cp .env.example .env- 51개 테스트 (100% 통과)- 51개 테스트 (100% 통과)

docker-compose up -d

uvicorn backend.main:app --reload

```

# 기술 스택



- FastAPI 0.109.0- **Backend**: FastAPI 0.109.0

- PostgreSQL 15 + pgvector 0.5.1- **Database**: PostgreSQL 15 + pgvector 0.5.1

- OpenAI GPT-4 Turbo- **LLM**: OpenAI GPT-4 Turbo

- HuggingFace multilingual-e5-large- **Embeddings**: HuggingFace multilingual-e5-large

- Python 3.10- **Testing**: pytest 7.4.4

- **Language**: Python 3.10

# 로컬 실행

```bash

pip install -r requirements.txt```bash

cp .env.example .env# 1. 의존성 설치

docker-compose up -dpip install -r requirements.txt

uvicorn backend.main:app --reload

```# 2. 환경변수 설정

cp .env.example .env

## 주요 모듈# .env 파일에서 API 키 수정



- `backend/main.py`: FastAPI 엔트리포인트# 3. DB 실행

- `backend/retriever.py`: 벡터 검색 엔진docker-compose up -d

- `backend/rag_chain.py`: RAG 처리 파이프라인

- `backend/llm_base.py`: OpenAI API 래퍼# 4. FastAPI 서버 실행

- `backend/schemas.py`: Pydantic 스키마uvicorn backend.main:app --reload

- `backend/db/connect.py`: DB 연결 관리

# 5. 테스트 실행
pytest tests/ -v
```

# 주요 모듈

- `backend/main.py`: FastAPI 엔트리포인트
- `backend/retriever.py`: 벡터 검색 엔진 (Connection Pool, Query Expansion)
- `backend/rag_chain.py`: RAG 처리 파이프라인
- `backend/llm_base.py`: OpenAI API 래퍼
- `backend/schemas.py`: Pydantic 스키마
- `backend/db/connect.py`: DB 연결 관리
- `tests/`: 51개 테스트 스위트
