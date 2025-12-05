# 프로젝트 문서 목록# 프로젝트 문서 목록



> FastAPI RAG 백엔드 + 통합 채팅 시스템 문서 허브## 📚 문서 구조



---### 1. 프로젝트 계획

- **[프로젝트_계획서.md](./프로젝트_계획서.md)**: 초기 프로젝트 개요 및 목표

## 📚 문서 구조- **[PROJECT_PLAN.md](./PROJECT_PLAN.md)**: 상세 프로젝트 계획서 (영문)

- **[IMPLEMENTATION_TRACKER.md](./IMPLEMENTATION_TRACKER.md)**: 구현 진행 상황 추적

### 1. 프로젝트 현황

- **[CURRENT_STATUS.md](./CURRENT_STATUS.md)**: 최신 구현 현황 및 다음 작업 계획### 2. 기술 문서

- **[IMPLEMENTATION_TRACKER.md](./IMPLEMENTATION_TRACKER.md)**: 상세 구현 체크리스트- **[RAG_PIPELINE_ARCHITECTURE.md](./RAG_PIPELINE_ARCHITECTURE.md)**: RAG 파이프라인 아키텍처 설계 (v1.1)

- **[PROJECT_PLAN.md](./PROJECT_PLAN.md)**: 전체 프로젝트 계획 및 로드맵- **[EMBEDDING_PLAN.md](./EMBEDDING_PLAN.md)**: 임베딩 전략 및 계획

- **[ITINERARY_RECOMMENDATION.md](./ITINERARY_RECOMMENDATION.md)**: 여행 추천 API 사양 (입력/응답 스키마, 흐름)

### 2. 기술 문서- **[REDIS_CACHE_GUIDE.md](./REDIS_CACHE_GUIDE.md)**: Redis TTL, 키 구조, 장애 대응, 모니터링 지표 정리

- **[RAG_PIPELINE_ARCHITECTURE.md](./RAG_PIPELINE_ARCHITECTURE.md)**: RAG 파이프라인 아키텍처

- **[EMBEDDING_PLAN.md](./EMBEDDING_PLAN.md)**: 임베딩 전략 및 계획---

- **[FILE_CATALOG.md](./FILE_CATALOG.md)**: 파일별 책임 및 역할 정리

## 🔄 버전 히스토리

### 3. API 및 통합

- **[API_INTEGRATION_FOR_NODE.md](./API_INTEGRATION_FOR_NODE.md)**: Node.js 연동 가이드### v1.1 (2025-11-07~12) - Parent-Child Architecture ✅ COMPLETE

- **[ITINERARY_RECOMMENDATION.md](./ITINERARY_RECOMMENDATION.md)**: 여행 추천 API 사양- **주요 변경사항**:

- **[REDIS_CACHE_GUIDE.md](./REDIS_CACHE_GUIDE.md)**: Redis 캐시 운영 가이드  - Document-level → Parent-Child QA chunking

- **[openapi_rag.yaml](./openapi_rag.yaml)**: OpenAPI 3.0 명세  - 메타데이터 확장 (2개 → 9+개 필드)

  - multilingual-e5-large (1024d) → multilingual-e5-small (384d)

---  - 직접 SQL 쿼리 방식 (PGVector <=> 연산자)

  - Metadata Filtering 구현 (area, domain)

## 🔄 버전 히스토리  - Query Expansion + Parent Context 옵션 + Redis 캐시 도입

- **완료 상태**:

### v1.2 (2025-11-17) - 통합 채팅 시스템 ✅ COMPLETE  - ✅ 377,263개 Parents 임베딩 완료

**주요 기능**:  - ✅ 2,202,565개 Children 임베딩 완료

- Structured Outputs (100% JSON 보장)  - ✅ Retriever 구현 및 테스트 (90%+ 유사도)

- 세션/저장: Node에서 관리 (백엔드는 응답만 반환)

- UnifiedChatHandler (Function Calling)- **다음 단계**:

- POST /chat 통합 엔드포인트  - Query Expansion latency 분석 및 cutoff 전략

  - Redis 캐시 운영 가이드 및 장애 대응 시나리오 문서화

**완료 상태**:

- ✅ Structured Outputs 스키마 및 generate_structured() 메서드### v1.0 (2025-11-05~06) - Initial Implementation (Deprecated)

- ✅ MariaDB 채팅 기록 관리자- 기본 RAG 파이프라인 구축

- ✅ Function Calling 통합 핸들러 (일반 대화/RAG 검색/여행 일정)- Document-level 임베딩 (66% 완료 후 중단)

- ✅ 통합 채팅 엔드포인트- 단순 벡터 유사도 검색

- ✅ 4개 테스트 파일 작성- 아키텍처 결함으로 v1.1로 재설계

- ✅ Git 15개 커밋 분리 (1 변경 1 커밋)

---

### v1.1 (2025-11-07~12) - Parent-Child Architecture ✅ COMPLETE

**주요 변경**:## 📊 프로젝트 현황

- Document-level → Parent-Child QA chunking

- 메타데이터 확장 (2개 → 9+개 필드)**데이터**: 377,265개 일본어 관광 문서 (6개 도메인)

- multilingual-e5-large (1024d) → multilingual-e5-small (384d)- 음식점 (FOOD): 113,383개

- Metadata Filtering, Query Expansion, Parent Context, Redis 캐시- 역사 (HIS): 116,387개  

- 레저 (LEI): 15,373개

**완료 상태**:- 자연 (NAT): 37,408개

- ✅ 377,263개 Parents 임베딩- 쇼핑 (SHOP): 29,005개

- ✅ 2,202,565개 Children 임베딩- 숙박 (STAY): 67,709개

- ✅ Retriever 구현 (90%+ 유사도)

- ✅ 모든 품질 개선 단계**임베딩 현황**: 

- ✅ v1.1 100% 완료 (2025-11-07)

### v1.0 (2025-11-05~06) - Initial (Deprecated)- Parents: 377,263개 (문서 요약)

- 기본 RAG 파이프라인- Children: 2,202,565개 (QA 청크, 평균 5.8개/문서)

- v1.1로 재설계- 처리 시간: 2시간 54분

- 속도: 35.97 files/sec

---

**검색 성능**:

## 📊 현재 시스템 구조- 평균 유사도: 90%+ (0.90~0.92)

- Metadata Filtering: 복합 조건 검색 시 0.91 달성

```- M4 GPU (MPS) 가속 사용

FastAPI Backend

├─ POST /chat (통합 채팅)---

│  ├─ UnifiedChatHandler

│  ├─ Function Calling 자동 감지## 🛠️ 기술 스택

│- **Backend**: FastAPI + Python 3.10

├─ POST /rag/query (RAG 검색)- **Database**: PostgreSQL + pgvector

│  ├─ Query Expansion- **LLM**: OpenAI GPT-4

│  ├─ Metadata Filtering- **Embedding**: intfloat/multilingual-e5-small (384d)

│  ├─ Parent Context- **Hardware**: M4 GPU (MPS acceleration)

│  └─ Redis 캐시- **Cache**: Redis

│- **Deployment**: Docker Compose

├─ PostgreSQL + pgvector

│  ├─ tourism_parent (377,263)## 📈 품질 개선 현황

│  └─ tourism_child (2,202,565)

│### ✅ Step 1: Metadata Filtering (완료)

└─ MariaDB- 지역/도메인별 타겟팅 검색


```- 검색 정확도 향상 (최고 유사도 0.91)



---### ✅ Step 2: Query Expansion (완료)

- JSON 설정 기반 변형 생성(접미어, 구두점, 사용자 변형)

## 📈 데이터 현황- 변형별 성공/실패/latency/cached 지표 로깅 및 `/rag/query` metadata로 노출

- Redis TTL 캐시로 반복 쿼리 응답 속도 향상

**총 377,265개 일본어 관광 문서**

### ✅ Step 3: Parent Context (완료)

| 도메인 | 문서 수 | 비율 |- `parent_context` 플래그로 parent summary 포함 여부 제어

|--------|---------|------|- fallback 경로에서도 요약 제거 처리

| 음식점 (food) | 113,383 | 30.1% |

| 역사 (his) | 116,387 | 30.8% |### 🔄 Step 4: 캐시/운영 가시성 (진행 중)

| 숙박 (stay) | 67,709 | 17.9% |- Redis TTL 전략 운영 가이드 및 fallback 시나리오 문서화

| 자연 (nat) | 37,408 | 9.9% |- Query Expansion/검색 지표를 모니터링 대시보드에 노출

| 쇼핑 (shop) | 29,005 | 7.7% |

| 레저 (lei) | 15,373 | 4.1% |---



**임베딩**: v1.1 100% 완료## 📖 참고 링크

- Parents: 377,263개

- Children: 2,202,565개 (평균 5.8개/문서)프로젝트 루트의 [README.md](../README.md)를 참조하세요.

- 처리 시간: 2시간 54분

---

## 🛠️ 기술 스택

- **Backend**: FastAPI + Python 3.10
- **Database**: PostgreSQL + pgvector, MariaDB
- **LLM**: OpenAI GPT-4
- **Embedding**: intfloat/multilingual-e5-small (384d)
- **Cache**: Redis
- **Hardware**: M4 GPU (MPS)

---

## 🎯 주요 기능

### RAG 검색
- Parent-Child 아키텍처
- Metadata Filtering (domain, area)
- Query Expansion (변형 생성, 캐시)
- Parent Context 옵션
- 평균 유사도: 90%+

### 통합 채팅
- Function Calling 자동 의도 파악
- 일반 대화 + RAG 검색 + 여행 일정
- Structured Outputs (100% JSON)
- MariaDB 영구 저장

---

**최종 업데이트**: 2025-11-17  
**문서 버전**: 1.2
