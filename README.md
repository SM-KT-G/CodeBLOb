## 설명
- 백엔드와 프론트 레포지토리에 올리기 전 거쳐가는 레포지토리입니다.
- 하루에 1인당 최소 10커밋씩 올려야합니다.
- 중요한 api 키는 올리지 않도록 주의해주시기 바랍니다.

## Scripts
- `scripts/ocr`: 예제용 파이썬 OCR 스크립트와 관련 자료가 정리되어 있습니다.
- `scripts/random_tools`: 파이썬 `random` 모듈 예제와 데모 스크립트를 확인할 수 있습니다.



# FastAPI RAG Backend# FastAPI RAG Backend# FastAPI RAG Backend



RAG 기반 관광정보 검색 시스템



## 기능RAG (Retrieval-Augmented Generation) 기반 관광정보 검색 시스템RAG (Retrieval-Augmented Generation) 기반 관광정보 검색 시스템입니다.



- PostgreSQL + pgvector 벡터 검색

- OpenAI GPT-4 답변 생성

- HuggingFace multilingual-e5-large 임베딩## 주요 기능## 주요 기능

- Connection Pool DB 연결

- 51개 테스트



## 기술 스택- PostgreSQL + pgvector 벡터 검색- PostgreSQL + pgvector 기반 벡터 검색



- FastAPI, PostgreSQL, OpenAI, HuggingFace, Python 3.10- OpenAI GPT-4 답변 생성- OpenAI GPT-4를 활용한 답변 생성



## 실행- HuggingFace multilingual-e5-large 임베딩- HuggingFace multilingual-e5-large 임베딩 모델



```bash- Connection Pool DB 연결 관리- Connection Pool을 통한 효율적인 DB 연결 관리

pip install -r requirements.txt

cp .env.example .env- 51개 테스트 (100% 통과)- 51개 테스트 (100% 통과)

docker-compose up -d

uvicorn backend.main:app --reload

```

## 기술 스택## 기술 스택



- FastAPI 0.109.0- **Backend**: FastAPI 0.109.0

- PostgreSQL 15 + pgvector 0.5.1- **Database**: PostgreSQL 15 + pgvector 0.5.1

- OpenAI GPT-4 Turbo- **LLM**: OpenAI GPT-4 Turbo

- HuggingFace multilingual-e5-large- **Embeddings**: HuggingFace multilingual-e5-large

- Python 3.10- **Testing**: pytest 7.4.4

- **Language**: Python 3.10

## 로컬 실행

## 로컬 실행

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

## 주요 모듈

- `backend/main.py`: FastAPI 엔트리포인트
- `backend/retriever.py`: 벡터 검색 엔진 (Connection Pool, Query Expansion)
- `backend/rag_chain.py`: RAG 처리 파이프라인
- `backend/llm_base.py`: OpenAI API 래퍼
- `backend/schemas.py`: Pydantic 스키마
- `backend/db/connect.py`: DB 연결 관리
- `tests/`: 51개 테스트 스위트

